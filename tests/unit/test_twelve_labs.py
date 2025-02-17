"""Unit tests for Twelve Labs model."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.ai.models.twelve_labs import (
    APITimeoutError,
    RateLimitError,
    TwelveLabsError,
    TwelveLabsModel,
)
from src.core.exceptions import ModelError


@pytest.fixture
def model():
    """Create a TwelveLabsModel instance."""
    return TwelveLabsModel(api_key="test_key")


@pytest.fixture
def test_video_file():
    """Create a temporary test video file."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        temp_file.write(b"dummy video content")
        temp_file.flush()
        yield Path(temp_file.name)
        temp_file.unlink()


def test_initialization():
    """Test model initialization."""
    # Test successful initialization
    model = TwelveLabsModel(api_key="test_key")
    assert model.api_key == "test_key"
    assert model.session.headers["Authorization"] == "Bearer test_key"

    # Test missing API key
    with pytest.raises(ModelError, match="Missing API key"):
        TwelveLabsModel()

    with pytest.raises(ModelError, match="Missing API key"):
        TwelveLabsModel(api_key=None)


def test_make_request_success(model):
    """Test successful API request."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}

    with patch.object(model.session, "request", return_value=mock_response):
        result = model._make_request("GET", "/test")
        assert result == {"data": "test"}


def test_make_request_rate_limit(model):
    """Test rate limit handling."""
    mock_response = MagicMock()
    mock_response.status_code = 429

    with patch.object(model.session, "request", return_value=mock_response):
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            model._make_request("GET", "/test")


def test_make_request_timeout(model):
    """Test timeout handling."""
    with patch.object(
        model.session, "request", side_effect=requests.exceptions.Timeout
    ):
        with pytest.raises(APITimeoutError, match="Request timed out"):
            model._make_request("GET", "/test")


def test_make_request_error(model):
    """Test general error handling."""
    with patch.object(
        model.session,
        "request",
        side_effect=requests.exceptions.RequestException("error"),
    ):
        with pytest.raises(TwelveLabsError, match="API request failed: error"):
            model._make_request("GET", "/test")


def test_ensure_index_exists(model):
    """Test index existence check and creation."""
    # Mock index exists
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": [{"name": model.DEFAULT_INDEX}]}

    with patch.object(model.session, "request", return_value=mock_response):
        model._ensure_index()  # Should not create new index

    # Mock index doesn't exist
    mock_response.json.return_value = {"data": []}
    mock_create = MagicMock()
    mock_create.status_code = 200

    with patch.object(
        model.session, "request", side_effect=[mock_response, mock_create]
    ):
        model._ensure_index()  # Should create new index


def test_track_task_status_success(model):
    """Test successful task status tracking."""
    mock_responses = [
        {"status": "processing", "progress": 50},
        {"status": "processing", "progress": 75},
        {"status": "completed", "result": {"data": "test"}},
    ]

    mock_request = MagicMock()
    mock_request.status_code = 200
    mock_request.json.side_effect = mock_responses

    with patch.object(model.session, "request", return_value=mock_request):
        result = model._track_task_status("test_task")
        assert result == {"data": "test"}


def test_track_task_status_failure(model):
    """Test task status failure handling."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "failed", "message": "Task failed"}

    with patch.object(model.session, "request", return_value=mock_response):
        with pytest.raises(TwelveLabsError, match="Task failed: Task failed"):
            model._track_task_status("test_task")


def test_track_task_status_timeout(model):
    """Test task status timeout."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "processing", "progress": 50}

    with patch.object(model.session, "request", return_value=mock_response):
        with pytest.raises(APITimeoutError, match="Task timed out"):
            model._track_task_status("test_task")


def test_validate_input(model, test_video_file):
    """Test input validation."""
    # Test valid input
    valid_input = {
        "video_path": str(test_video_file),
        "start_time": 0,
        "end_time": 10,
    }
    assert model.validate(valid_input) is True

    # Test missing fields
    invalid_input = {"video_path": str(test_video_file)}
    with pytest.raises(ModelError, match="Missing start_time in input data"):
        model.validate(invalid_input)

    # Test non-existent file
    invalid_input = {
        "video_path": "nonexistent.mp4",
        "start_time": 0,
        "end_time": 10,
    }
    with pytest.raises(ModelError, match="Video file not found"):
        model.validate(invalid_input)

    # Test file too large
    with patch("pathlib.Path.stat") as mock_stat:
        mock_stat.return_value.st_size = model.MAX_FILE_SIZE + 1
        with pytest.raises(ModelError, match="Video file too large"):
            model.validate(valid_input)

    # Test unsupported format
    invalid_input = {
        "video_path": str(test_video_file.with_suffix(".xyz")),
        "start_time": 0,
        "end_time": 10,
    }
    with pytest.raises(ModelError, match="Unsupported video format"):
        model.validate(invalid_input)


@patch("src.ai.models.twelve_labs.TwelveLabsModel._make_request")
@patch("src.ai.models.twelve_labs.TwelveLabsModel._track_task_status")
def test_process_success(mock_track_status, mock_request, model, test_video_file):
    """Test successful video processing."""
    input_data = {
        "video_path": str(test_video_file),
        "start_time": 0,
        "end_time": 10,
    }

    # Mock API responses
    mock_request.side_effect = [
        {"task_id": "upload_task"},  # Upload task creation
        {},  # Upload chunk
        {"video_id": "test_video"},  # Upload completion
        {"task_id": "analysis_task"},  # Analysis task creation
    ]

    mock_track_status.side_effect = [
        {"video_id": "test_video"},  # Upload task completion
        {  # Analysis task completion
            "scene_description": "Test scene",
            "objects": [{"name": "object1"}],
            "actions": [{"description": "action1"}],
            "metadata": {
                "duration": 10,
                "fps": 30,
                "resolution": "1920x1080",
            },
        },
    ]

    result = model.process(input_data)

    assert result["description"] == "Test scene"
    assert result["objects"] == ["object1"]
    assert result["actions"] == ["action1"]
    assert result["metadata"]["duration"] == 10
    assert result["metadata"]["fps"] == 30
    assert result["metadata"]["resolution"] == "1920x1080"


@patch("src.ai.models.twelve_labs.TwelveLabsModel._make_request")
def test_process_rate_limit_retry(mock_request, model, test_video_file):
    """Test rate limit retry mechanism."""
    input_data = {
        "video_path": str(test_video_file),
        "start_time": 0,
        "end_time": 10,
    }

    # First call raises rate limit, second succeeds
    mock_request.side_effect = [
        RateLimitError("Rate limit exceeded"),
        {"task_id": "test_task"},
    ]

    with patch("time.sleep"):  # Don't actually sleep in tests
        model.process(input_data)  # Should retry and succeed

    assert mock_request.call_count == 2


@patch("src.ai.models.twelve_labs.TwelveLabsModel._make_request")
def test_process_with_callback(mock_request, model, test_video_file):
    """Test processing with status callback."""
    input_data = {
        "video_path": str(test_video_file),
        "start_time": 0,
        "end_time": 10,
    }

    mock_callback = MagicMock()

    # Mock successful responses
    mock_request.side_effect = [
        {"task_id": "upload_task"},
        {},
        {"video_id": "test_video"},
        {"task_id": "analysis_task"},
        {"status": "completed", "result": {}},
    ]

    model.process(input_data, status_callback=mock_callback)

    # Verify callback was called with status updates
    assert mock_callback.call_count > 0
    for call in mock_callback.call_args_list:
        status = call[0][0]
        assert "status" in status
        assert "progress" in status
        assert "message" in status
