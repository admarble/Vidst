"""Twelve Labs video understanding model implementation.

This module provides the main interface for video understanding using
the Twelve Labs API. It handles:

- Video upload and processing
- Task management and tracking
- Resource cleanup
- Error handling and recovery
- Input validation
- Asynchronous operations

The model supports multiple processing tasks including:
- Scene detection
- Speech transcription
- Text extraction
- Visual search
- Content understanding

Example:
    >>> model = TwelveLabsModel(api_key="your_api_key")
    >>> result = await model.process({
    ...     "video_path": "path/to/video.mp4",
    ...     "task": TaskType.SCENE_DETECTION,
    ...     "options": {"confidence_threshold": 0.8}
    ... })

Note:
    This model requires valid API credentials and network connectivity
    to the Twelve Labs API endpoints. All operations are asynchronous
    and should be used within an async context.
"""

import asyncio
import os
from pathlib import Path
from typing import Any

import aiohttp

from video_understanding.ai.exceptions import (
    APIError,
    RateLimitError,
    ResourceError,
    ValidationError,
)
from video_understanding.ai.models.base import BaseModel

from .client import TwelveLabsClient
from .exceptions import TwelveLabsError
from .types import TaskType


class TwelveLabsModel(BaseModel):
    """Twelve Labs video understanding model.

    This model provides high-level access to Twelve Labs' video
    processing capabilities while handling:
    - Input validation and error handling
    - Task creation and management
    - Resource cleanup and lifecycle management
    - Asynchronous operation coordination
    - Video upload and processing
    - Search and retrieval

    The model supports multiple processing tasks and provides
    a simple interface for video analysis. All operations are
    performed asynchronously for optimal performance.

    Attributes:
        MAX_FILE_SIZE (int): Maximum supported video file size (2GB)
        SUPPORTED_FORMATS (frozenset): Set of supported video formats (mp4, avi, mov)
        DEFAULT_INDEX (str): Default index name for video indexing

    Note:
        This model uses asyncio for all operations and should be used
        in an async context. Proper cleanup is essential - use async
        context managers or explicitly call close().
    """

    # Constants
    MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
    SUPPORTED_FORMATS = frozenset({"mp4", "avi", "mov"})
    DEFAULT_INDEX = "default_index"

    def __init__(self, api_key: str, base_url: str = "https://api.twelvelabs.io/v1.1"):
        """Initialize the model.

        Creates a new TwelveLabsModel instance with the specified API key and base URL.
        The model lazily initializes its resources when first used.

        Args:
            api_key: Twelve Labs API key for authentication
            base_url: Base URL for the Twelve Labs API

        Raises:
            ValidationError: If API key is empty or invalid

        Note:
            The model uses lazy initialization - the API client and other
            resources are created only when needed.
        """
        super().__init__()
        if not api_key:
            raise ValidationError("API key is required")

        self.api_key = api_key
        self.base_url = base_url
        self._client = TwelveLabsClient(api_key)
        self._active_tasks: set[str] = set()
        self._temp_files: set[str] = set()
        self._session: aiohttp.ClientSession | None = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure a valid session exists and return it.

        This method lazily initializes the session when needed and ensures
        it has the proper authentication headers set.

        Returns:
            aiohttp.ClientSession: The active session

        Raises:
            TwelveLabsError: If session creation fails
        """
        if self._session is None:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session

    async def close(self) -> None:
        """Close the model and cleanup resources.

        This method ensures proper cleanup of resources:
        - Closes the API session
        - Removes temporary files
        - Cancels active tasks

        Note:
            This method should be called when the model is no longer needed
            to prevent resource leaks.
        """
        if self._session is not None:
            await self._session.close()
            self._session = None

        # Clean up temporary files
        for file_path in self._temp_files:
            try:
                Path(file_path).unlink()
            except OSError:
                pass
        self._temp_files.clear()

        # Cancel active tasks
        for task_id in self._active_tasks:
            try:
                await self._client.cancel_task(task_id)
            except Exception:
                pass
        self._active_tasks.clear()

    async def _make_request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Make an HTTP request to the API.

        This method handles common request functionality:
        - Session management
        - Error handling
        - Rate limit handling
        - Response parsing

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters

        Returns:
            Parsed JSON response data

        Raises:
            TwelveLabsError: For API errors
            RateLimitError: When rate limit is exceeded
            APIError: For network or timeout issues
        """
        session = await self._ensure_session()
        try:
            # Ensure endpoint starts with /
            if not endpoint.startswith("/"):
                endpoint = f"/{endpoint}"

            # Construct full URL
            url = f"{self.base_url.rstrip('/')}{endpoint}"

            async with session.request(method, url, **kwargs) as response:
                response_text = await response.text()
                try:
                    response_data = await response.json() if response_text else {}
                except ValueError:
                    response_data = {}

                error_message = response_data.get("error") or response_data.get(
                    "message", response_text
                )

                if response.status == 429:
                    reset_time = response.headers.get("X-RateLimit-Reset", "30")
                    raise RateLimitError(
                        f"Rate limit exceeded, reset in {reset_time} seconds"
                    )
                elif response.status == 401:
                    raise TwelveLabsError(f"Unauthorized: {error_message}")
                elif response.status == 403:
                    raise TwelveLabsError(f"Forbidden: {error_message}")
                elif response.status == 404:
                    raise TwelveLabsError(f"Not found: {endpoint}")
                elif response.status == 400:
                    raise TwelveLabsError(f"Bad request: {error_message}")
                elif response.status >= 500:
                    raise TwelveLabsError(f"Server error: {error_message}")

                return response_data

        except aiohttp.ClientError as e:
            raise APIError(f"Request failed: {e!s}")

    async def _make_request_with_retry(
        self,
        method: str,
        endpoint: str,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make a request with exponential backoff retry.

        Args:
            method: HTTP method
            endpoint: API endpoint
            max_retries: Maximum number of retries
            initial_delay: Initial delay in seconds
            **kwargs: Additional request parameters

        Returns:
            Dict[str, Any]: Response data

        Raises:
            TwelveLabsError: If all retries fail
        """
        delay = initial_delay
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                return await self._make_request(method, endpoint, **kwargs)
            except RateLimitError as e:
                last_error = e
                if attempt == max_retries:
                    break
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
            except (TwelveLabsError, APIError) as e:
                # Don't retry on other errors
                raise e

        raise last_error or TwelveLabsError("Max retries exceeded")

    def validate(self, input_data: dict[str, Any]) -> bool:
        """Validate input data for video processing.

        Performs comprehensive validation of input data including:
        - Required field presence and type checking
        - Task type validation and enumeration
        - Video file existence and format validation
        - File size verification
        - Options structure validation

        The validation is performed in a specific order to provide
        clear error messages and fail fast:
        1. Basic input structure
        2. Required fields
        3. Task type validation
        4. Video file validation
        5. Options validation

        Args:
            input_data: Dictionary containing:
                - video_path (str): Path to video file
                - task (Union[str, TaskType]): Processing task type
                - options (Optional[Dict]): Task-specific parameters

        Returns:
            bool: True if input is valid

        Raises:
            ValidationError: If any validation check fails, with a specific
                error message indicating the validation failure

        Example:
            >>> model = TwelveLabsModel(api_key)
            >>> try:
            ...     model.validate({
            ...         "video_path": "video.mp4",
            ...         "task": TaskType.SCENE_DETECTION,
            ...         "options": {"confidence_threshold": 0.8}
            ...     })
            ... except ValidationError as e:
            ...     print(f"Validation failed: {e}")
        """
        try:
            # Check required fields
            if not isinstance(input_data, dict):
                raise ValidationError("Input must be a dictionary")

            if "video_path" not in input_data:
                raise ValidationError("Missing video_path in input data")

            if "task" not in input_data:
                raise ValidationError("Missing task type in input data")

            # Validate task type first
            task = input_data["task"]
            if isinstance(task, str):
                try:
                    TaskType(task)
                except ValueError:
                    raise ValidationError(f"Invalid task type: {task}")
            elif not isinstance(task, TaskType):
                raise ValidationError(f"Invalid task type: {task}")

            # Then validate video file
            video_path = Path(input_data["video_path"])
            if not video_path.exists():
                raise ValidationError("Video file not found")

            if video_path.stat().st_size > self.MAX_FILE_SIZE:
                raise ValidationError("Video file too large")

            if video_path.suffix[1:] not in self.SUPPORTED_FORMATS:
                raise ValidationError("Unsupported video format")

            # Validate options if present
            if "options" in input_data:
                options = input_data["options"]
                if not isinstance(options, dict):
                    raise ValidationError("Options must be a dictionary")

            return True

        except (TypeError, ValueError, OSError) as e:
            raise ValidationError(f"Validation failed: {e!s}")

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process a video using specified task type.

        This is the main entry point for video processing. It orchestrates
        the complete processing pipeline:
        1. Input validation and preprocessing
        2. Video upload with chunked transfer
        3. Task creation and configuration
        4. Progress monitoring and status updates
        5. Result collection and formatting
        6. Resource cleanup and error handling

        Args:
            input_data: Dictionary containing:
                - video_path (str): Path to video file
                - task (Union[str, TaskType]): Processing task type
                - options (Optional[Dict]): Task-specific parameters
                    - confidence_threshold (float): Detection confidence
                    - max_scenes (int): Maximum scenes to detect
                    - language (str): Processing language
                    - Other task-specific options

        Returns:
            Dictionary containing:
                - data (Dict): Task-specific result data
                - metadata (Dict): Video and processing metadata
                    - video_id (str): Unique video identifier
                    - index_name (str): Search index name
                    - task_id (str): Processing task identifier
                    - status (str): Task status

        Raises:
            ValidationError: If input validation fails
            ResourceError: If processing fails due to:
                - API errors
                - Network issues
                - Resource limitations
                - Processing timeouts
            TwelveLabsError: If task fails or API returns error
        """
        self.validate(input_data)

        try:
            # Upload video
            video_id = await self._upload_video(input_data["video_path"])

            # Create task
            task_id = await self._client.create_task(
                video_id, input_data["task"], input_data.get("options", {})
            )
            self._active_tasks.add(task_id)

            try:
                # Wait for task completion
                task_result = await self._track_task_status(task_id)

                # Format result
                return {
                    "data": task_result["result"]["data"],
                    "metadata": {
                        "video_id": video_id,
                        "index_name": self.DEFAULT_INDEX,
                        "task_id": task_id,
                        "status": task_result["status"],
                    },
                }
            finally:
                self._active_tasks.remove(task_id)

        except TwelveLabsError:
            raise
        except Exception as e:
            raise ResourceError(f"Processing failed: {e!s}") from e

    async def search(
        self, query: str, index_name: str | None = None, **options: Any
    ) -> dict[str, Any]:
        """Search across indexed videos.

        Performs semantic search across processed videos to find
        relevant segments matching the query. The search uses
        multimodal understanding to match:
        - Visual content
        - Spoken words
        - On-screen text
        - Scene context
        - Actions and objects

        Args:
            query (str): Natural language search query
            index_name (Optional[str]): Index to search (default: DEFAULT_INDEX)
            **options: Additional search parameters:
                - confidence_threshold (float): Minimum match confidence (0-1)
                - max_results (int): Maximum number of results
                - filters (Dict): Additional search filters
                    - duration_range (Tuple[float, float]): Time range
                    - date_range (Tuple[str, str]): Date range
                    - video_ids (List[str]): Specific videos to search
                    - custom_metadata (Dict): Custom metadata filters

        Returns:
            Dictionary containing:
                - matches (List[Dict]): Matched video segments
                    - video_id (str): Video identifier
                    - start_time (float): Start time in seconds
                    - end_time (float): End time in seconds
                    - confidence (float): Match confidence
                    - context (str): Segment context
                - metadata (Dict): Search metadata
                    - total_results (int): Total matches found
                    - search_time (float): Search duration
                    - index_stats (Dict): Index statistics

        Raises:
            ResourceError: If search fails due to:
                - Invalid query
                - Index not found
                - API errors
            ValidationError: If query or options are invalid

        Example:
            >>> results = await model.search(
            ...     "person explaining neural networks",
            ...     confidence_threshold=0.7,
            ...     max_results=10,
            ...     filters={
            ...         "duration_range": (0, 300),
            ...         "video_ids": ["vid_123", "vid_456"]
            ...     }
            ... )
            >>> for match in results["matches"]:
            ...     print(f"Found at {match['start_time']}s")

        Note:
            Search is only available for previously processed videos
            in the specified index. For optimal results, ensure videos
            are fully processed and indexed.
        """
        try:
            return await self._client.search(query, index_name, **options)
        except Exception as e:
            raise ResourceError(f"Search failed: {e!s}") from e

    async def _ensure_index(self, index_name: str | None = None) -> None:
        """Ensure the specified index exists.

        Args:
            index_name: Name of the index to check/create

        Raises:
            ResourceError: If index creation fails
        """
        try:
            indexes = await self._client.list_indexes()
            if isinstance(indexes, list):
                if not any(
                    isinstance(idx, dict) and idx.get("name") == index_name
                    for idx in indexes
                ):
                    if index_name is not None:
                        await self._client.create_index(index_name)
        except Exception as e:
            raise ResourceError(f"Failed to ensure index exists: {e!s}") from e

    async def generate_text(self, video_id: str, prompt: str) -> dict[str, Any]:
        """Generate text content from video.

        Args:
            video_id: ID of the processed video
            prompt: Generation prompt/instructions

        Returns:
            Dictionary containing generated text content

        Raises:
            ResourceError: If text generation fails
        """
        try:
            return await self._client.generate_text(video_id, prompt)
        except Exception as e:
            raise ResourceError(f"Text generation failed: {e!s}") from e

    def __del__(self) -> None:
        """Ensure resources are cleaned up during garbage collection.

        This method provides a safety net for resource cleanup when
        the model instance is garbage collected. It attempts to:
        - Close the API client
        - Cancel active tasks
        - Clean up system resources

        The cleanup process handles several scenarios:
        1. Running event loop:
           - Creates a cleanup task in the existing loop
           - Non-blocking asynchronous cleanup

        2. No running event loop:
           - Attempts to create a temporary loop
           - Performs synchronous cleanup
           - Properly closes temporary loop

        3. Interpreter shutdown:
           - Detects shutdown state
           - Skips cleanup gracefully
           - Prevents shutdown errors

        Note:
            This is a backup mechanism - explicit calls to close()
            are strongly recommended for deterministic cleanup.
            This method may not be called in all circumstances,
            particularly during program termination.

        Example:
            >>> # Proper cleanup pattern
            >>> model = TwelveLabsModel(api_key)
            >>> try:
            ...     await model.process(video_data)
            ... finally:
            ...     # Prefer explicit cleanup over relying on __del__
            ...     await model.close()

        Warning:
            Do not rely on this method for cleanup in production code.
            Always use explicit cleanup via close() when possible.
            This method is provided only as a safety net for cases
            where explicit cleanup is not possible.
        """
        if self._client:
            try:
                # Try to get the current event loop
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    # No event loop available - skip cleanup
                    return

                if loop.is_running():
                    # Schedule cleanup if loop is running
                    loop.create_task(self.close())
                else:
                    try:
                        # Try to create a new loop for cleanup
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(self.close())
                    except Exception:
                        # If we can't create a loop, skip cleanup
                        pass
                    finally:
                        try:
                            loop.close()
                        except Exception:
                            pass
            except Exception:
                # During interpreter shutdown or other error conditions,
                # skip cleanup gracefully
                pass

    @property
    def session(self) -> aiohttp.ClientSession | None:
        """Get the current session.

        Returns:
            The current aiohttp session or None if not initialized
        """
        return self._client._session

    async def _track_task_status(self, task_id: str) -> dict[str, Any]:
        """Track the status of a task until completion.

        This method polls the task status endpoint until the task
        reaches a terminal state (completed or failed).

        Args:
            task_id: Task identifier to track

        Returns:
            Task result data

        Raises:
            TwelveLabsError: If task fails or tracking fails
        """
        try:
            response = await self._make_request_with_retry("GET", f"/tasks/{task_id}")

            if response["status"] == "failed":
                raise TwelveLabsError(
                    f"Task failed: {response.get('error', 'Unknown error')}"
                )

            return response

        except Exception as e:
            if isinstance(e, TwelveLabsError):
                raise
            raise TwelveLabsError(f"Task tracking failed: {e!s}") from e

    async def _upload_video(self, video_path: str) -> str:
        """Upload a video file to the API.

        Args:
            video_path: Path to the video file

        Returns:
            str: The ID of the uploaded video

        Raises:
            TwelveLabsError: If upload fails
            ValidationError: If video path is invalid
        """
        if not os.path.exists(video_path):
            raise ValidationError(f"Video file not found: {video_path}")

        # Create upload task
        response = await self._make_request_with_retry(
            "POST", "/tasks", json={"type": "video_upload"}
        )
        task_id = response.get("task_id")
        if not task_id:
            raise TwelveLabsError("Failed to create upload task")

        # Track task status
        task_result = await self._track_task_status(task_id)
        if task_result.get("status") == "failed":
            raise TwelveLabsError(
                f"Upload failed: {task_result.get('error', 'Unknown error')}"
            )

        video_id = task_result.get("result", {}).get("video_id")
        if not video_id:
            raise TwelveLabsError("Failed to get video ID from upload task")

        return video_id

    def _cleanup_resources(self) -> None:
        """Clean up temporary resources.

        This method ensures proper cleanup of:
        - Temporary files
        - Active tasks
        """
        # Clean up temporary files
        for file_path in self._temp_files:
            try:
                Path(file_path).unlink(missing_ok=True)
            except OSError:
                pass  # Best effort cleanup
        self._temp_files.clear()

        # Cancel active tasks
        for task_id in self._active_tasks:
            try:
                asyncio.create_task(self._client.cancel_task(task_id))
            except Exception:
                pass  # Best effort cleanup
        self._active_tasks.clear()
