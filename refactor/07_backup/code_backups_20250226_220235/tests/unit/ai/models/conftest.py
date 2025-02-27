"""Shared fixtures for AI model tests."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def model():
    """Create a mock AI model for testing."""
    mock_model = MagicMock()

    def process_with_file_read(input_data):
        # Simulate reading the file
        with open(input_data["image_path"], "rb") as f:
            _ = f.read()
        return {
            "description": "Test description",
            "objects": ["object1", "object2"],
            "text": ["text1", "text2"],
            "actions": ["action1", "action2"],
        }

    mock_model.process.side_effect = process_with_file_read
    return mock_model


@pytest.fixture
def ai_test_image(tmp_path):
    """Create a test image file for AI model testing."""
    image_path = tmp_path / "test_image.jpg"
    image_path.write_bytes(b"test image data")
    return image_path


@pytest.fixture
def ai_test_video(tmp_path):
    """Create a test video file for AI model testing."""
    video_path = tmp_path / "test_video.mp4"
    video_path.write_bytes(b"test video content")
    return video_path
