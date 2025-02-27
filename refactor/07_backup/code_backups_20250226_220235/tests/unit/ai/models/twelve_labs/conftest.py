"""Shared fixtures and utilities for Twelve Labs tests."""

from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
import requests

from video_understanding.ai.exceptions.twelve_labs import ValidationError
from video_understanding.ai.models.twelve_labs.client import TwelveLabsClient
from video_understanding.ai.models.twelve_labs.model import TwelveLabsModel
from video_understanding.ai.models.twelve_labs.types import TaskResult


def create_mock_response(status_code=200, json_data=None, headers=None):
    """Create a mock response object."""
    if json_data is None:
        json_data = {}

    # Ensure task responses have proper structure
    if "task_id" in json_data:
        if "status" not in json_data:
            json_data["status"] = "completed"
        if "result" not in json_data:
            json_data["result"] = {"video_id": "test_video_id"}

    # Ensure task status responses have proper structure
    if (
        "status" in json_data
        and json_data["status"] == "completed"
        and "result" not in json_data
    ):
        json_data["result"] = {"video_id": "test_video_id"}

    response = Mock(spec=requests.Response)
    response.status_code = status_code
    response.json = Mock(return_value=json_data)
    response.headers = headers or {}
    response.reason = "Not Found" if status_code == 404 else "OK"
    response.url = "https://api.twelvelabs.io/v1.3/test"

    def raise_for_status():
        if status_code >= 400:
            raise requests.exceptions.HTTPError(
                f"{status_code} Client Error: {response.reason} for url: {response.url}",
                response=response,
            )

    response.raise_for_status = Mock(side_effect=raise_for_status)
    return response


@pytest.fixture
def mock_client():
    """Create a mock TwelveLabsClient."""
    client = AsyncMock(spec=TwelveLabsClient)
    client.API_BASE_URL = "https://api.twelvelabs.io/v1.3"
    client.DEFAULT_INDEX = "default_index"
    client.CHUNK_SIZE = 1024 * 1024  # 1MB
    client.MAX_RETRIES = 3
    client.INITIAL_BACKOFF = 1
    client.MAX_BACKOFF = 30

    # Mock session management
    client._session = AsyncMock()
    client._get_session = AsyncMock(return_value=client._session)
    client._rate_limit_remaining = 50
    client._rate_limit_reset = 1500000000

    # Mock core API methods with validation
    async def mock_make_request(method, endpoint, **kwargs):
        if method == "GET" and endpoint == "/test":
            return {"status": "success"}
        if method == "POST" and endpoint == "/tasks/upload":
            if not kwargs.get("json", {}).get("index_name"):
                raise ValidationError("Missing index_name")
            return {"task_id": "test_task_id"}
        if method == "PUT" and "tasks/" in endpoint:
            if not kwargs.get("data"):
                raise ValidationError("Missing upload data")
            return {"status": "success"}
        return {"status": "success"}

    client._make_request = AsyncMock(side_effect=mock_make_request)

    async def mock_upload_video(video_path):
        if not isinstance(video_path, Path):
            raise ValidationError("Invalid video path type")
        if not video_path.exists():
            raise ValidationError(f"Video file not found: {video_path}")
        return "test_video_id"

    client.upload_video = AsyncMock(side_effect=mock_upload_video)

    async def mock_create_task(task_type, video_id, options=None):
        if not task_type:
            raise ValidationError("Missing task type")
        if not video_id:
            raise ValidationError("Missing video ID")
        return "test_task_id"

    client.create_task = AsyncMock(side_effect=mock_create_task)

    client.wait_for_task = AsyncMock(
        return_value=TaskResult(
            task_id="test_task_id",
            status="completed",
            result={"data": "test_result"},
            error=None,
            video_id="test_video_id",
        )
    )
    client.search = AsyncMock(return_value={"data": "test_search_result"})
    client.generate_text = AsyncMock(return_value={"data": "test_text"})
    client.get_rate_limit_info = AsyncMock(
        return_value={"remaining": 50, "reset": 1500000000}
    )
    client.close = AsyncMock()

    # Mock index management with validation
    async def mock_list_indexes():
        return [{"name": "default_index"}]

    async def mock_create_index():
        return {"name": "default_index"}

    async def mock_delete_index():
        return {"status": "success"}

    async def mock_get_index():
        return {"name": "default_index"}

    client.list_indexes = AsyncMock(side_effect=mock_list_indexes)
    client.create_index = AsyncMock(side_effect=mock_create_index)
    client.delete_index = AsyncMock(side_effect=mock_delete_index)
    client.get_index = AsyncMock(side_effect=mock_get_index)

    # Mock task management with validation
    async def mock_get_task_status(task_id):
        if not task_id:
            raise ValidationError("Missing task ID")
        return {"status": "completed"}

    async def mock_cancel_task(task_id):
        if not task_id:
            raise ValidationError("Missing task ID")
        return {"status": "cancelled"}

    async def mock_list_tasks():
        return [{"task_id": "test_task_id"}]

    client.get_task_status = AsyncMock(side_effect=mock_get_task_status)
    client.cancel_task = AsyncMock(side_effect=mock_cancel_task)
    client.list_tasks = AsyncMock(side_effect=mock_list_tasks)

    return client


@pytest.fixture
def mock_session():
    """Create a mock aiohttp ClientSession."""
    session = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def model(mock_client):
    """Create a TwelveLabsModel instance with a mock client."""
    model = TwelveLabsModel(api_key="test_key")
    model._client = mock_client
    return model


@pytest.fixture
def test_video(tmp_path):
    """Create a temporary video file for testing.

    This fixture creates a mock video file in a temporary directory.
    The file contains dummy content but has a valid video extension.

    Args:
        tmp_path: pytest fixture providing temporary directory path

    Returns:
        Path: Path object pointing to the created test video file.
    """
    video_file = tmp_path / "test_video.mp4"
    video_file.write_bytes(b"test video content")
    return video_file
