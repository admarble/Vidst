"""Tests for TwelveLabs model validation."""

from unittest.mock import patch

import pytest

from video_understanding.ai.exceptions import ValidationError
from video_understanding.ai.models.twelve_labs import TwelveLabsModel


def test_validate_missing_fields(model):
    """Test validation with missing fields."""
    with pytest.raises(ValidationError, match="Input must be a dictionary"):
        model.validate(None)

    with pytest.raises(ValidationError, match="Missing video_path in input data"):
        model.validate({})

    with pytest.raises(ValidationError, match="Missing task type in input data"):
        model.validate({"video_path": "test.mp4"})

    with pytest.raises(ValidationError, match="Invalid task type: invalid_task"):
        model.validate({"video_path": "test.mp4", "task": "invalid_task"})


def test_validate_invalid_format(model, tmp_path):
    """Test validation with invalid video format."""
    video_path = tmp_path / "test.txt"
    video_path.write_bytes(b"test data")
    input_data = {"video_path": str(video_path), "task": "scene_detection"}
    with pytest.raises(ValidationError, match="Unsupported video format"):
        model.validate(input_data)


def test_validate_nonexistent_file(model):
    """Test validation with nonexistent file."""
    input_data = {"video_path": "nonexistent.mp4", "task": "scene_detection"}
    with pytest.raises(ValidationError, match="Video file not found"):
        model.validate(input_data)


def test_validate_file_too_large(model, test_video):
    """Test validation with file too large."""
    with patch("pathlib.Path.stat") as mock_stat:
        mock_stat.return_value.st_size = TwelveLabsModel.MAX_FILE_SIZE + 1
        input_data = {"video_path": str(test_video), "task": "scene_detection"}
        with pytest.raises(ValidationError, match="Video file too large"):
            model.validate(input_data)


def test_validate_success(model, test_video):
    """Test successful validation."""
    input_data = {"video_path": str(test_video), "task": "scene_detection"}
    assert model.validate(input_data) is True
