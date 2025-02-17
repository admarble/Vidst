"""Twelve Labs model implementation for video analysis."""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

import backoff
import requests

from src.core.exceptions import ModelError

from .base import BaseModel


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""

    pass


class APITimeoutError(Exception):
    """Raised when API request times out."""

    pass


class TwelveLabsError(Exception):
    """Base exception for Twelve Labs API errors."""

    pass


class TwelveLabsModel(BaseModel):
    """Model for processing videos using Twelve Labs API"""

    API_BASE_URL = "https://api.twelvelabs.io/v1.2"
    DEFAULT_INDEX = "default_index"
    CHUNK_SIZE = 5 * 1024 * 1024  # 5MB chunks
    TASK_TIMEOUT = 300  # 5 minutes
    TASK_CHECK_INTERVAL = 5  # 5 seconds
    MAX_RETRIES = 3
    MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

    def __init__(self, api_key: str = None):
        """Initialize the model with API key."""
        if not api_key:
            raise ModelError("Missing API key")

        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an API request with error handling."""
        try:
            response = self.session.request(
                method, f"{self.API_BASE_URL}{endpoint}", **kwargs
            )

            if response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")

            response.raise_for_status()

            if response.status_code != 204:  # No content
                return response.json()
            return {}

        except requests.exceptions.Timeout:
            raise APITimeoutError("Request timed out")
        except requests.exceptions.RequestException as e:
            raise TwelveLabsError(f"API request failed: {str(e)}")

    def _ensure_index(self) -> None:
        """Ensure the default index exists."""
        try:
            # Check if index exists
            response = self._make_request("GET", "/indexes")
            indexes = response.get("data", [])

            index_exists = any(
                index.get("name") == self.DEFAULT_INDEX for index in indexes
            )

            if not index_exists:
                # Create index if it doesn't exist
                self._make_request(
                    "POST",
                    "/indexes",
                    json={"name": self.DEFAULT_INDEX, "engine": "marengo2.5"},
                )
        except TwelveLabsError as e:
            raise ModelError(f"Failed to ensure index exists: {str(e)}")

    def _track_task_status(
        self, task_id: str, callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Track task status with timeout."""
        start_time = time.time()

        while True:
            if time.time() - start_time > self.TASK_TIMEOUT:
                raise APITimeoutError("Task timed out")

            try:
                response = self._make_request("GET", f"/tasks/{task_id}")
                status = response.get("status", "unknown").lower()
                progress = response.get("progress", 0)
                message = response.get("message", "")

                if callback:
                    callback(
                        {"status": status, "progress": progress, "message": message}
                    )

                if status == "completed":
                    return response.get("result", {})
                elif status == "failed":
                    raise TwelveLabsError(f"Task failed: {message}")
                elif status == "error":
                    raise TwelveLabsError(f"Task error: {message}")

                time.sleep(self.TASK_CHECK_INTERVAL)

            except RateLimitError:
                raise
            except (TwelveLabsError, APITimeoutError):
                raise  # Re-raise task errors and timeouts directly
            except Exception as e:
                raise TwelveLabsError(f"Failed to track task status: {str(e)}")

    def validate(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data."""
        required_fields = ["video_path", "start_time", "end_time"]
        for field in required_fields:
            if field not in input_data:
                raise ModelError(f"Missing {field} in input data")

        video_path = Path(input_data["video_path"])
        if not video_path.exists():
            raise ModelError(f"Video file not found: {video_path}")

        if video_path.stat().st_size > self.MAX_FILE_SIZE:
            raise ModelError("Video file too large (max 2GB)")

        if video_path.suffix.lower() not in [".mp4", ".avi", ".mov"]:
            raise ModelError(f"Unsupported video format: {video_path.suffix}")

        return True

    @backoff.on_exception(backoff.expo, RateLimitError, max_tries=3)
    def process(
        self, input_data: Dict[str, Any], status_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Process video using Twelve Labs API with rate limit handling."""
        try:
            self.validate(input_data)

            # Ensure index exists
            self._ensure_index()

            # Upload video
            if status_callback:
                status_callback(
                    {
                        "status": "uploading",
                        "progress": 0,
                        "message": "Starting video upload",
                    }
                )

            # Create upload task
            upload_task = self._make_request(
                "POST",
                "/tasks/upload",
                json={
                    "index_name": self.DEFAULT_INDEX,
                    "language": "en",
                    "visual_tasks": [
                        "scene_detection",
                        "object_detection",
                        "action_detection",
                    ],
                    "text_tasks": ["transcription", "text_detection"],
                },
            )

            if "task_id" not in upload_task:
                raise TwelveLabsError("Invalid upload task response: missing task_id")

            # Upload video file in chunks
            video_path = Path(input_data["video_path"])
            with open(video_path, "rb") as f:
                headers = {"Content-Type": "application/octet-stream"}
                while chunk := f.read(self.CHUNK_SIZE):
                    self._make_request(
                        "PUT",
                        f"/tasks/{upload_task['task_id']}/upload",
                        data=chunk,
                        headers=headers,
                    )

            # Track upload status
            video_info = self._track_task_status(
                upload_task["task_id"], status_callback
            )

            # Start analysis
            analysis_task = self._make_request(
                "POST",
                "/tasks/index",
                json={
                    "video_id": video_info["video_id"],
                    "index_name": self.DEFAULT_INDEX,
                    "start_time": input_data["start_time"],
                    "end_time": input_data["end_time"],
                    "visual_tasks": [
                        "scene_detection",
                        "object_detection",
                        "action_detection",
                    ],
                    "text_tasks": ["transcription", "text_detection"],
                    "language": "en",
                },
            )

            # Track task status and get results
            result = self._track_task_status(analysis_task["task_id"], status_callback)

            # Process and normalize the results
            return {
                "description": result.get("scene_description", ""),
                "objects": [obj.get("name") for obj in result.get("objects", [])],
                "actions": [
                    action.get("description") for action in result.get("actions", [])
                ],
                "metadata": {
                    "duration": result.get("metadata", {}).get("duration", 0),
                    "fps": result.get("metadata", {}).get("fps", 0),
                    "resolution": result.get("metadata", {}).get("resolution", ""),
                    "video_id": video_info.get("video_id", ""),
                    "index_name": self.DEFAULT_INDEX,
                },
            }

        except APITimeoutError:
            raise ModelError("Task timed out")
        except RateLimitError as e:
            raise ModelError(f"Rate limit exceeded: {str(e)}")
        except TwelveLabsError as e:
            raise ModelError(f"Twelve Labs API error: {str(e)}")
        except Exception as e:
            raise ModelError(f"Failed to process video: {str(e)}")
