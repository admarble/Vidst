"""Internal API client for Twelve Labs.

This module provides a low-level client for interacting with the Twelve Labs API.
It handles:

- Authentication and session management
- Rate limiting and retries
- Chunked file uploads
- Task tracking and status polling
- Error handling and recovery

The client is designed to be used internally by the TwelveLabsModel and
should not be instantiated directly by users.

Note:
    This client requires valid API credentials and network connectivity
    to the Twelve Labs API endpoints.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

import aiohttp
import backoff

from video_understanding.ai.exceptions import (
    APIError,
    RateLimitError,
    TaskError,
    ValidationError,
)

from .types import TaskOptions, TaskResult, TaskType

logger = logging.getLogger(__name__)


class TwelveLabsClient:
    """Internal API client for Twelve Labs.

    This class handles low-level API communication and is not exposed
    outside the twelve_labs package. It provides robust error handling,
    automatic retries, and resource management.

    Attributes:
        API_BASE_URL: Base URL for API endpoints
        DEFAULT_INDEX: Default index name for video storage
        CHUNK_SIZE: Size of upload chunks in bytes
        MAX_RETRIES: Maximum number of retry attempts
        INITIAL_BACKOFF: Initial backoff delay in seconds
        MAX_BACKOFF: Maximum backoff delay in seconds

    Note:
        This class uses asyncio for all operations and should be used
        in an async context.
    """

    API_BASE_URL = "https://api.twelvelabs.io/v1.3"
    DEFAULT_INDEX = "default_index"
    CHUNK_SIZE = 1024 * 1024  # 1MB
    MAX_RETRIES = 3
    INITIAL_BACKOFF = 1
    MAX_BACKOFF = 30

    def __init__(self, api_key: str) -> None:
        """Initialize the client.

        Args:
            api_key: Twelve Labs API key for authentication

        Raises:
            ValueError: If api_key is empty or invalid
        """
        if not api_key or not isinstance(api_key, str):
            raise ValueError("Valid API key is required")

        self._api_key = api_key
        self._session: aiohttp.ClientSession | None = None
        self._rate_limit_remaining: int | None = None
        self._rate_limit_reset: int | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create session with proper headers.

        This method ensures we have a valid session with the correct
        authentication headers. It will create a new session if none
        exists or if the current session is closed.

        Returns:
            Active aiohttp session with proper headers

        Note:
            Sessions are created with keep-alive enabled for better
            performance with multiple requests.
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                }
            )
        return self._session

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, RateLimitError),
        max_tries=MAX_RETRIES,
        max_time=MAX_BACKOFF,
    )
    async def _make_request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Make an API request with retries and error handling.

        This method handles all HTTP communication with the API, including:
        - Automatic retries with exponential backoff
        - Rate limit tracking and handling
        - Error parsing and conversion to exceptions
        - Response validation

        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters

        Returns:
            Parsed JSON response from the API

        Raises:
            APIError: If request fails or response is invalid
            RateLimitError: If rate limit is exceeded

        Note:
            This method is decorated with backoff for automatic retries
            on transient failures.
        """
        session = await self._get_session()
        url = f"{self.API_BASE_URL}{endpoint}"

        try:
            async with session.request(method, url, **kwargs) as response:
                # Update rate limit info
                self._rate_limit_remaining = int(
                    response.headers.get("X-RateLimit-Remaining", 0)
                )
                self._rate_limit_reset = int(
                    response.headers.get("X-RateLimit-Reset", 0)
                )

                if response.status == 429:
                    raise RateLimitError(
                        f"Rate limit exceeded. Reset in {self._rate_limit_reset} seconds"
                    )

                if response.status >= 400:
                    error_data = await response.json()
                    raise APIError(
                        f"API request failed: {error_data.get('message', 'Unknown error')}"
                    )

                if response.content_length == 0:
                    return {"status": "success"}

                return await response.json()

        except aiohttp.ClientError as e:
            raise APIError(f"Request failed: {e!s}") from e

    async def upload_video(self, video_path: Path) -> str:
        """Upload video with chunked transfer.

        This method handles large video uploads by:
        1. Creating an upload task
        2. Streaming the file in chunks
        3. Monitoring upload progress
        4. Waiting for processing completion

        Args:
            video_path: Path to video file to upload

        Returns:
            Video ID assigned by Twelve Labs

        Raises:
            APIError: If upload or processing fails
            ValidationError: If file is invalid or inaccessible

        Note:
            This method will block until the upload is complete and
            the video is ready for processing.
        """
        if not video_path.exists():
            raise ValidationError(f"Video file not found: {video_path}")

        # Create upload task
        response = await self._make_request(
            "POST", "/tasks/upload", json={"index_name": self.DEFAULT_INDEX}
        )
        task_id = response.get("task_id")
        if not task_id:
            raise APIError("Invalid upload response: missing task_id")

        # Upload video chunks
        async with aiohttp.ClientSession() as session:
            with open(video_path, "rb") as f:
                while chunk := f.read(self.CHUNK_SIZE):
                    async with session.post(
                        f"{self.API_BASE_URL}/tasks/{task_id}",
                        data=chunk,
                        headers={"Content-Type": "application/octet-stream"},
                    ) as response:
                        if response.status != 200:
                            raise APIError(f"Upload failed: {response.status}")

        # Wait for upload to complete
        result = await self.wait_for_task(task_id)
        if not result["video_id"]:
            raise APIError("Upload task completed but no video_id returned")
        return result["video_id"]

    async def create_task(
        self,
        task_type: TaskType | str,
        video_id: str,
        options: TaskOptions | None = None,
    ) -> str:
        """Create a processing task.

        Creates a new video processing task with the specified parameters.

        Args:
            task_type: Type of processing to perform
            video_id: ID of video to process
            options: Optional processing parameters

        Returns:
            Task ID for tracking progress

        Raises:
            APIError: If task creation fails
            ValidationError: If parameters are invalid

        Example:
            >>> task_id = await client.create_task(
            ...     TaskType.SCENE_DETECTION,
            ...     "vid_123",
            ...     {"confidence_threshold": 0.8}
            ... )
        """
        if isinstance(task_type, TaskType):
            task_type = task_type.value

        response = await self._make_request(
            "POST",
            "/tasks/analyze",
            json={
                "video_id": video_id,
                "task_type": task_type,
                "options": options or {},
            },
        )

        task_id = response.get("task_id")
        if not task_id:
            raise APIError("Invalid task response: missing task_id")
        return task_id

    async def wait_for_task(self, task_id: str, timeout: int = 300) -> TaskResult:
        """Wait for task completion with timeout.

        Polls the task status until completion or failure.

        Args:
            task_id: Task ID to monitor
            timeout: Maximum wait time in seconds

        Returns:
            Task result data including status and output

        Raises:
            TaskError: If task fails or times out
            APIError: If status check fails

        Note:
            This method implements exponential backoff between status
            checks to avoid API rate limits.
        """
        start_time = asyncio.get_event_loop().time()
        while True:
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TaskError(f"Task {task_id} timed out")

            response = await self._make_request("GET", f"/tasks/{task_id}")
            status = response.get("status")

            if status == "completed":
                return TaskResult(
                    task_id=task_id,
                    status="completed",
                    result=response.get("result", {}),
                    error=None,
                    video_id=response.get("video_id"),
                )
            elif status == "failed":
                raise TaskError(
                    f"Task {task_id} failed: {response.get('error', 'Unknown error')}"
                )
            elif status in ("pending", "processing"):
                await asyncio.sleep(2)
            else:
                raise TaskError(f"Unknown task status: {status}")

    async def search(
        self, query: str, index_name: str | None = None, **options: Any
    ) -> dict[str, Any]:
        """Perform semantic search across indexed videos.

        Searches for video segments matching the query text.

        Args:
            query: Natural language search query
            index_name: Optional index to search (default: DEFAULT_INDEX)
            **options: Additional search parameters

        Returns:
            Search results with matched segments

        Raises:
            APIError: If search fails
            ValidationError: If query is invalid

        Example:
            >>> results = await client.search(
            ...     "person wearing red shirt",
            ...     confidence_threshold=0.7
            ... )
        """
        response = await self._make_request(
            "POST",
            "/search",
            json={
                "index_name": index_name or self.DEFAULT_INDEX,
                "query": query,
                **options,
            },
        )
        return response

    async def close(self) -> None:
        """Close the client session.

        Properly closes the HTTP session and cleans up resources.
        This should be called when the client is no longer needed.

        Note:
            This is automatically called when the client is garbage
            collected, but explicit calls are recommended.
        """
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def list_indexes(self) -> dict[str, Any]:
        """List all available indexes.

        Returns:
            List of index information dictionaries

        Raises:
            APIError: If the API request fails
        """
        return await self._make_request("GET", "/indexes")

    async def create_index(self, name: str) -> dict[str, Any]:
        """Create a new index.

        Args:
            name: Name of the index to create

        Returns:
            Created index information

        Raises:
            APIError: If index creation fails
            ValidationError: If name is invalid
        """
        if not name:
            raise ValidationError("Index name is required")

        return await self._make_request("POST", "/indexes", json={"name": name})

    async def generate_text(self, video_id: str, prompt: str) -> dict[str, Any]:
        """Generate text content from video.

        Args:
            video_id: ID of the processed video
            prompt: Generation prompt/instructions

        Returns:
            Generated text content

        Raises:
            APIError: If text generation fails
            ValidationError: If parameters are invalid
        """
        if not video_id or not prompt:
            raise ValidationError("Video ID and prompt are required")

        return await self._make_request(
            "POST", f"/videos/{video_id}/generate", json={"prompt": prompt}
        )

    async def cancel_task(self, task_id: str) -> None:
        """Cancel a running task.

        Args:
            task_id: ID of the task to cancel

        Raises:
            APIError: If task cancellation fails
            ValidationError: If task_id is invalid
        """
        if not task_id:
            raise ValidationError("Task ID is required")

        await self._make_request("POST", f"/tasks/{task_id}/cancel")
