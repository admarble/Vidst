"""Unit tests for Twelve Labs model implementation."""

import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

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
def mock_session():
    """Create a mock session."""
    with patch("requests.Session") as mock:
        session = MagicMock()
        mock.return_value = session
        yield session


@pytest.fixture
def model(mock_session):
    """Create a model instance with mocked session."""
    return TwelveLabsModel("test_api_key")


@pytest.fixture
def mock_video_file(tmp_path):
    """Create a temporary video file."""
    video_path = tmp_path / "test.mp4"
    video_path.write_bytes(b"test video content")
    return str(video_path)


@pytest.fixture
def valid_input_data(mock_video_file):
    """Create valid input data."""
    return {"video_path": mock_video_file, "start_time": 0, "end_time": 10}


def test_model_initialization():
    """Test model initialization."""
    model = TwelveLabsModel("test_api_key")
    assert isinstance(model, TwelveLabsModel)
    assert model.api_key == "test_api_key"


def test_model_initialization_no_key():
    """Test model initialization without API key."""
    with pytest.raises(ModelError, match="Missing API key"):
        TwelveLabsModel()


def test_ensure_index_exists(model, mock_session):
    """Test handling when index already exists."""
    mock_session.request.return_value = MagicMock(
        status_code=200, json=lambda: {"data": [{"name": "default_index"}]}
    )

    model._ensure_index()

    # Verify only one call to check index
    assert mock_session.request.call_count == 1
    assert mock_session.request.call_args[0] == ("GET", f"{model.API_BASE_URL}/indexes")


def test_ensure_index_creation(model, mock_session):
    """Test index creation when it doesn't exist."""
    responses = [
        # Initial check returns no indexes
        MagicMock(status_code=200, json=lambda: {"data": []}),
        # Index creation success
        MagicMock(status_code=200),
    ]
    mock_session.request.side_effect = responses

    model._ensure_index()

    # Verify both check and creation calls
    assert mock_session.request.call_count == 2
    calls = mock_session.request.call_args_list
    assert calls[0][0] == ("GET", f"{model.API_BASE_URL}/indexes")
    assert calls[1][0] == ("POST", f"{model.API_BASE_URL}/indexes")
    assert calls[1][1]["json"] == {"name": "default_index", "engine": "marengo2.5"}


def test_ensure_index_error(model, mock_session):
    """Test error handling during index creation."""
    mock_session.request.side_effect = requests.exceptions.RequestException("API Error")

    with pytest.raises(
        ModelError, match="Failed to ensure index exists: API request failed: API Error"
    ):
        model._ensure_index()


def test_process_success(model, valid_input_data, mock_session):
    """Test successful video processing."""
    responses = [
        # Initial index check
        MagicMock(status_code=200, json=lambda: {"data": [{"name": "default_index"}]}),
        # Upload task creation
        MagicMock(status_code=200, json=lambda: {"task_id": "upload_task_id"}),
        # Upload chunk success
        MagicMock(status_code=204),
        # Upload status updates
        MagicMock(
            status_code=200,
            json=lambda: {
                "status": "completed",
                "progress": 100,
                "message": "Upload complete",
                "result": {"video_id": "test_video_id"},
            },
        ),
        # Analysis task creation
        MagicMock(status_code=200, json=lambda: {"task_id": "analysis_task_id"}),
        # Analysis status updates
        MagicMock(
            status_code=200,
            json=lambda: {
                "status": "completed",
                "progress": 100,
                "message": "Done",
                "result": {
                    "scene_description": "Test scene",
                    "objects": [{"name": "object1"}, {"name": "object2"}],
                    "actions": [{"description": "action1"}, {"description": "action2"}],
                    "metadata": {"duration": 10, "fps": 30, "resolution": "1920x1080"},
                },
            },
        ),
    ]

    mock_session.request.side_effect = responses

    # Mock callback
    callback_data = []

    def status_callback(data):
        callback_data.append(data)

    result = model.process(valid_input_data, status_callback=status_callback)

    assert isinstance(result, dict)
    assert result["description"] == "Test scene"
    assert result["objects"] == ["object1", "object2"]
    assert result["actions"] == ["action1", "action2"]
    assert result["metadata"] == {
        "duration": 10,
        "fps": 30,
        "resolution": "1920x1080",
        "video_id": "test_video_id",
        "index_name": "default_index",
    }


def test_process_task_failure(model, valid_input_data, mock_session):
    """Test handling of task failure."""
    responses = [
        # Initial index check
        MagicMock(status_code=200, json=lambda: {"data": [{"name": "default_index"}]}),
        # Upload task creation
        MagicMock(status_code=200, json=lambda: {"task_id": "upload_task_id"}),
        # Upload chunk success
        MagicMock(status_code=204),
        # Failed status
        MagicMock(
            status_code=200,
            json=lambda: {"status": "failed", "message": "Processing failed"},
        ),
    ]

    mock_session.request.side_effect = responses

    with pytest.raises(
        ModelError, match="Twelve Labs API error: Task failed: Processing failed"
    ):
        model.process(valid_input_data)


def test_process_task_error(model, valid_input_data, mock_session):
    """Test handling of task error status."""
    responses = [
        # Initial index check
        MagicMock(status_code=200, json=lambda: {"data": [{"name": "default_index"}]}),
        # Upload task creation
        MagicMock(status_code=200, json=lambda: {"task_id": "upload_task_id"}),
        # Upload chunk success
        MagicMock(status_code=204),
        # Error status
        MagicMock(
            status_code=200,
            json=lambda: {"status": "error", "message": "Internal error occurred"},
        ),
    ]

    mock_session.request.side_effect = responses

    with pytest.raises(
        ModelError, match="Twelve Labs API error: Task error: Internal error occurred"
    ):
        model.process(valid_input_data)


def test_process_task_timeout(model, valid_input_data, mock_session):
    """Test handling of task timeout."""
    responses = [
        # Initial index check
        MagicMock(status_code=200, json=lambda: {"data": [{"name": "default_index"}]}),
        # Upload task creation
        MagicMock(status_code=200, json=lambda: {"task_id": "upload_task_id"}),
        # Upload chunk success
        MagicMock(status_code=204),
        # Timeout
        requests.exceptions.Timeout("Request timed out"),
    ]

    mock_session.request.side_effect = responses

    with pytest.raises(ModelError, match="Task timed out"):
        model.process(valid_input_data)


def test_process_rate_limit(model, valid_input_data, mock_session):
    """Test handling of rate limit errors."""
    mock_session.request.side_effect = [
        # Initial index check
        MagicMock(status_code=200, json=lambda: {"data": [{"name": "default_index"}]}),
        # Rate limit response
        MagicMock(status_code=429),
    ]

    with pytest.raises(ModelError, match="Rate limit exceeded: Rate limit exceeded"):
        model.process(valid_input_data)


def test_process_api_error(model, valid_input_data, mock_session):
    """Test handling of API errors."""
    mock_session.request.side_effect = [
        # Initial index check
        MagicMock(status_code=200, json=lambda: {"data": [{"name": "default_index"}]}),
        # API error
        requests.exceptions.RequestException("API Error"),
    ]

    with pytest.raises(
        ModelError, match="Twelve Labs API error: API request failed: API Error"
    ):
        model.process(valid_input_data)


def test_validate_missing_fields(model):
    """Test validation of missing required fields."""
    with pytest.raises(ModelError, match="Missing video_path in input data"):
        model.validate({})


def test_validate_file_not_found(model, tmp_path):
    """Test validation of non-existent video file."""
    video_path = tmp_path / "nonexistent.mp4"
    with pytest.raises(ModelError, match=f"Video file not found: {video_path}"):
        model.validate({"video_path": str(video_path), "start_time": 0, "end_time": 10})


def test_validate_unsupported_format(model, tmp_path):
    """Test validation of unsupported video format."""
    video_path = tmp_path / "test.xyz"
    video_path.write_bytes(b"test")
    with pytest.raises(ModelError, match=f"Unsupported video format: .xyz"):
        model.validate({"video_path": str(video_path), "start_time": 0, "end_time": 10})


def test_validate_file_too_large(model, tmp_path):
    """Test validation of large video file."""
    video_path = tmp_path / "test.mp4"
    with patch.object(Path, "stat") as mock_stat:
        mock_stat.return_value.st_size = 3 * 1024 * 1024 * 1024  # 3GB
        with pytest.raises(ModelError, match="Video file too large \(max 2GB\)"):
            model.validate(
                {"video_path": str(video_path), "start_time": 0, "end_time": 10}
            )
