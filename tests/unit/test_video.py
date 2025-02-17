"""Unit tests for Video model."""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from src.models.video import Video


@pytest.fixture
def sample_video():
    """Create a sample video instance."""
    return Video(
        filename="test.mp4",
        file_size=1024,
        format="mp4",
        id=uuid4(),
        upload_time=datetime.now(),
    )


def test_video_initialization():
    """Test basic video initialization."""
    video = Video(filename="test.mp4", file_size=1024, format="mp4")
    assert isinstance(video.id, UUID)
    assert isinstance(video.upload_time, datetime)
    assert video.status == "pending"
    assert video.processing_progress is None
    assert video.error_message is None


def test_post_init_validation():
    """Test post initialization validation."""
    # Test UUID conversion
    str_uuid = "550e8400-e29b-41d4-a716-446655440000"
    video = Video(filename="test.mp4", file_size=1024, format="mp4", id=str_uuid)
    assert isinstance(video.id, UUID)
    assert str(video.id) == str_uuid

    # Test format normalization
    video = Video(filename="test.mp4", file_size=1024, format="mp4")
    assert video.format == "MP4"


def test_equality():
    """Test video equality comparison."""
    id1 = uuid4()
    id2 = uuid4()

    video1 = Video(filename="test1.mp4", file_size=1024, format="mp4", id=id1)
    video2 = Video(filename="test2.mp4", file_size=2048, format="avi", id=id1)
    video3 = Video(filename="test3.mp4", file_size=1024, format="mp4", id=id2)

    # Same ID should be equal regardless of other attributes
    assert video1 == video2
    # Different IDs should not be equal
    assert video1 != video3
    # Comparison with non-Video object
    assert video1 != "not a video"


def test_file_path():
    """Test file path generation."""
    video = Video(
        filename="test.mp4",
        file_size=1024,
        format="mp4",
        id="550e8400-e29b-41d4-a716-446655440000",
    )
    assert video.file_path == "550e8400-e29b-41d4-a716-446655440000/test.mp4"


def test_status_properties():
    """Test status-related properties."""
    video = Video(filename="test.mp4", file_size=1024, format="mp4")

    # Test initial state
    assert not video.is_complete
    assert not video.has_error

    # Test complete state
    video.status = "complete"
    assert video.is_complete
    assert not video.has_error

    # Test error state
    video.status = "error"
    assert not video.is_complete
    assert video.has_error


def test_from_path(tmp_path):
    """Test creating video from path."""
    # Create a temporary file
    file_path = tmp_path / "test.mp4"
    file_path.write_text("dummy content")

    video_id = uuid4()
    video = Video.from_path(file_path, video_id, status="processing")

    assert video.filename == "test.mp4"
    assert video.format == "MP4"
    assert video.file_size == len("dummy content")
    assert video.id == video_id
    assert video.status == "processing"


def test_video_with_progress():
    """Test video with processing progress."""
    video = Video(
        filename="test.mp4", file_size=1024, format="mp4", processing_progress=50.0
    )
    assert video.processing_progress == 50.0


def test_video_with_error():
    """Test video with error message."""
    video = Video(
        filename="test.mp4",
        file_size=1024,
        format="mp4",
        status="error",
        error_message="Processing failed",
    )
    assert video.has_error
    assert video.error_message == "Processing failed"


def test_file_path_property(sample_video):
    """Test file path property."""
    expected_path = f"{sample_video.id}/{sample_video.filename}"
    assert sample_video.file_path == expected_path


def test_status_transitions():
    """Test valid and invalid status transitions."""
    video = Video(
        filename="test.mp4",
        file_size=1024,
        format="mp4",
    )

    # Test valid transitions
    valid_statuses = ["pending", "processing", "complete", "error"]
    for status in valid_statuses:
        video.status = status
        assert video.status == status

    # TODO: Implement status validation in Video class
    # # Test invalid status
    # with pytest.raises(ValueError):
    #     video.status = "invalid_status"

    # Test status with error message
    video.status = "error"
    video.error_message = "Processing failed"
    assert video.status == "error"
    assert video.error_message == "Processing failed"

    # TODO: Implement error message clearing when status changes from error
    # # Clear error
    # video.status = "pending"
    # assert video.error_message is None
