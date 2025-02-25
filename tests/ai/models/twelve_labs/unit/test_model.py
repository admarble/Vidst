# pylint: disable=redefined-outer-name,protected-access
"""Unit tests for TwelveLabsModel.

This module contains unit tests for the TwelveLabsModel class, which handles
video processing using the Twelve Labs API.

Tests cover:
1. Initialization
2. Session management
3. Response parsing
4. Request handling
5. Retry logic
6. Task tracking
7. Index management
8. Input validation
9. Video processing
10. Search functionality
11. Text generation
12. Resource cleanup
13. Video upload
14. End-to-end processing
15. Video analysis

Note on Lint Configuration:
    This module uses test-specific lint rules defined in ../.pylintrc:
    - Protected access is allowed for testing internal attributes
    - Fixture redefinition is expected with pytest
    - Import order follows standard->third-party->local pattern
    - No-member warnings are disabled for dynamic attributes

Example:
    To run these tests with pylint checking:
    ```bash
    pylint --rcfile=tests/ai/models/twelve_labs/.pylintrc tests/ai/models/twelve_labs/
    ```
"""

import os
from tempfile import NamedTemporaryFile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from video_understanding.ai.models.twelve_labs.exceptions import TwelveLabsError
from video_understanding.ai.models.twelve_labs.model import TwelveLabsModel
from video_understanding.core.exceptions import (
    APIError,
    ResourceError,
    ValidationError,
)

# Test data
API_KEY = "test_api_key"
VIDEO_PATH = "test_video.mp4"
VIDEO_ID = "test_video_id"
TASK_ID = "test_task_id"
UPLOAD_TASK_ID = "test_upload_task_id"


class RateLimitError(APIError):
    """Exception for rate limit errors."""


class APITimeoutError(APIError):
    """Exception for API timeout errors."""


@pytest.fixture
def test_video_file():
    """Create a temporary test video file."""
    with NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        f.write(b"test video content")
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def model_base():
    """Create a TwelveLabsModel instance without mocks."""
    return TwelveLabsModel(api_key=API_KEY)


@pytest.fixture
def mock_client():
    """Create a mock client with async methods."""
    mock = MagicMock()
    mock.upload_video = AsyncMock()
    mock.create_task = AsyncMock()
    mock.get_task_status = AsyncMock()
    mock.search = AsyncMock()
    return mock


@pytest.fixture
def model(mock_client):
    """Create a TwelveLabsModel instance with a mock client."""
    with patch(
        "src.video_understanding.ai.models.twelve_labs.model.TwelveLabsClient"
    ) as mock_client_class:
        mock_client_class.return_value = mock_client
        model = TwelveLabsModel(api_key=API_KEY)
        # Patch _make_request_with_retry and _track_task_status to avoid real API calls
        model._make_request_with_retry = AsyncMock()
        model._track_task_status = AsyncMock()
        yield model


@pytest.mark.asyncio
async def test_model_initialization():
    """Test model initialization."""
    model = TwelveLabsModel(api_key=API_KEY)
    assert model.api_key == API_KEY


@pytest.mark.asyncio
async def test_validate_config():
    """Test config validation."""
    # Valid config
    model = TwelveLabsModel(api_key=API_KEY)
    assert model.api_key == API_KEY

    # Invalid config
    with pytest.raises(ValidationError):
        TwelveLabsModel(api_key="")


@pytest.mark.asyncio
async def test_process_video(model, mock_client, test_video_file):
    """Test video processing."""
    # Mock _make_request_with_retry responses for video upload
    model._make_request_with_retry.side_effect = [
        # Upload task creation response
        {"task_id": UPLOAD_TASK_ID, "type": "video_upload", "status": "pending"}
    ]

    # Mock _track_task_status responses
    model._track_task_status.side_effect = [
        # Upload task status
        {
            "task_id": UPLOAD_TASK_ID,
            "status": "completed",
            "result": {
                "video_id": VIDEO_ID,
                "index_name": "default",
                "duration": 120.5,
                "format": "mp4",
            },
        },
        # Processing task status
        {
            "task_id": TASK_ID,
            "status": "completed",
            "result": {"data": {"scenes": [{"start": 0, "end": 10}]}},
            "video_id": VIDEO_ID,
        },
    ]

    # Mock create_task response
    mock_client.create_task.return_value = TASK_ID

    input_data = {
        "video_path": test_video_file,
        "task": "scene_detection",
        "options": {"confidence_threshold": 0.8},
    }
    result = await model.process(input_data)
    assert result["metadata"]["task_id"] == TASK_ID
    assert result["metadata"]["status"] == "completed"
    assert "scenes" in result["data"]


@pytest.mark.asyncio
async def test_process_video_error(model, mock_client, test_video_file):
    """Test video processing error handling."""
    # Mock _make_request_with_retry to raise TwelveLabsError
    model._make_request_with_retry.side_effect = ResourceError("Upload failed")

    with pytest.raises(ResourceError) as exc_info:
        input_data = {
            "video_path": test_video_file,
            "task": "scene_detection",
            "options": {"confidence_threshold": 0.8},
        }
        await model.process(input_data)

    assert str(exc_info.value) == "Processing failed: Upload failed"


@pytest.mark.asyncio
async def test_search_video(model, mock_client):
    """Test video search."""
    expected_result = {
        "matches": [
            {
                "video_id": VIDEO_ID,
                "confidence": 0.95,
                "start_time": 5.0,
                "end_time": 15.0,
                "metadata": {"scene_type": "dialogue"},
            }
        ],
        "metadata": {"total_results": 1, "search_time": 0.5},
    }
    mock_client.search.return_value = expected_result

    results = await model.search("query text")
    assert results == expected_result


@pytest.mark.asyncio
async def test_search_video_error(model, mock_client):
    """Test video search error handling."""
    mock_client.search.side_effect = TwelveLabsError("Search failed")

    with pytest.raises(ResourceError):
        await model.search("query text")


@pytest.mark.asyncio
async def test_validate_task_options(model_base, test_video_file):
    """Test task options validation."""
    # Valid options
    input_data = {
        "video_path": test_video_file,
        "task": "scene_detection",
        "options": {"confidence_threshold": 0.8, "max_scenes": 100, "language": "en"},
    }
    assert model_base.validate(input_data) is True

    # Invalid options - non-existent video file
    input_data["video_path"] = "/path/to/nonexistent/video.mp4"
    with pytest.raises(ValidationError):
        model_base.validate(input_data)

    # Invalid options - missing required field
    del input_data["task"]
    with pytest.raises(ValidationError):
        model_base.validate(input_data)

    # Invalid options - invalid task type
    input_data = {
        "video_path": test_video_file,
        "task": "invalid_task",
        "options": {"confidence_threshold": 0.8},
    }
    with pytest.raises(ValidationError):
        model_base.validate(input_data)
