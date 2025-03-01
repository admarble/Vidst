"""Unit tests for Twelve Labs API client.

This module contains unit tests for the TwelveLabsClient class. The tests use
pytest fixtures and mocks to simulate API interactions without making actual
HTTP requests.

Note on Lint Configuration:
    This module uses test-specific lint rules defined in ../.pylintrc:
    - Protected access is allowed for testing internal methods
    - Fixture redefinition is expected with pytest
    - Import order follows standard->third-party->local pattern

Example:
    To run these tests with pylint checking:
    ```bash
    pylint --rcfile=tests/ai/models/twelve_labs/.pylintrc tests/ai/models/twelve_labs/
    ```
"""

from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock

import pytest

from video_understanding.ai.models.twelve_labs.client import TwelveLabsClient
from video_understanding.ai.models.twelve_labs.exceptions import (
    TwelveLabsAPIError,
    TwelveLabsAuthError,
    TwelveLabsRateLimitError,
)
from video_understanding.ai.models.twelve_labs.types import (
    TaskOptions,
    TaskResult,
    TaskType,
    VideoMetadata,
)


@pytest.fixture
def mock_response() -> AsyncMock:
    """Create a mock aiohttp response."""
    response = AsyncMock()
    response.status = 200
    response.json.return_value = {
        "task_id": "task_123",
        "status": "pending",
        "video_id": "video_123",
    }
    return response


@pytest.fixture
def mock_session(mock_response: AsyncMock) -> AsyncMock:
    """Create a mock aiohttp ClientSession."""
    session = AsyncMock()
    session.post.return_value.__aenter__.return_value = mock_response
    session.get.return_value.__aenter__.return_value = mock_response
    return session


@pytest.fixture
def client(mock_session: AsyncMock) -> TwelveLabsClient:
    """Create a TwelveLabsClient instance with a mock session."""
    client = TwelveLabsClient("test_api_key")
    client._session = mock_session  # pylint: disable=protected-access
    return client


async def test_client_initialization() -> None:
    """Test client initialization."""
    client = TwelveLabsClient("test_api_key")
    assert client._api_key == "test_api_key"  # pylint: disable=protected-access
    assert client.API_BASE_URL == "https://api.twelvelabs.io/v1.3"


async def test_get_session(client: TwelveLabsClient) -> None:
    """Test session creation."""
    session = await client._get_session()  # pylint: disable=protected-access
    assert session is not None
    await client.close()


async def test_upload_video(client: TwelveLabsClient, mock_response: AsyncMock) -> None:
    """Test video upload."""
    mock_response.json.return_value = {
        "video_id": "test_123",
        "index_name": "default",
        "duration": 120.5,
        "format": "mp4",
    }

    result = await client.upload_video(Path("test.mp4"))
    assert isinstance(result, dict)
    metadata = cast(VideoMetadata, result)
    assert metadata["video_id"] == "test_123"


async def test_create_task(client: TwelveLabsClient, mock_response: AsyncMock) -> None:
    """Test task creation."""
    mock_response.json.return_value = {
        "task_id": "task_123",
        "status": "pending",
        "video_id": "video_123",
    }

    options = TaskOptions(confidence_threshold=0.8)
    result = await client.create_task(TaskType.SCENE_DETECTION, "video_123", options)
    assert isinstance(result, dict)
    task_result = cast(TaskResult, result)
    assert task_result["task_id"] == "task_123"


async def test_wait_for_task(
    client: TwelveLabsClient, mock_response: AsyncMock
) -> None:
    """Test getting task status."""
    mock_response.json.return_value = {
        "task_id": "task_123",
        "status": "completed",
        "result": {"scenes": []},
        "video_id": "video_123",
    }

    result = await client.wait_for_task("task_123")
    assert isinstance(result, dict)
    task_result = cast(TaskResult, result)
    assert task_result["status"] == "completed"


async def test_rate_limit_error(
    client: TwelveLabsClient, mock_response: AsyncMock
) -> None:
    """Test rate limit error handling."""
    mock_response.status = 429

    with pytest.raises(TwelveLabsRateLimitError):
        await client.create_task(
            TaskType.SCENE_DETECTION, "video_123", TaskOptions(confidence_threshold=0.8)
        )


async def test_auth_error(client: TwelveLabsClient, mock_response: AsyncMock) -> None:
    """Test authentication error handling."""
    mock_response.status = 401

    with pytest.raises(TwelveLabsAuthError):
        await client.create_task(
            TaskType.SCENE_DETECTION, "video_123", TaskOptions(confidence_threshold=0.8)
        )


async def test_api_error(client: TwelveLabsClient, mock_response: AsyncMock) -> None:
    """Test general API error handling."""
    mock_response.status = 500

    with pytest.raises(TwelveLabsAPIError):
        await client.create_task(
            TaskType.SCENE_DETECTION, "video_123", TaskOptions(confidence_threshold=0.8)
        )
