"""Tests for the Video model."""

from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from src.models.video import Video


@pytest.fixture
def video_id():
    return UUID("12345678-1234-5678-1234-567812345678")


@pytest.fixture
def sample_video(video_id):
    return Video(
        id=video_id,
        filename="test.mp4",
        file_size=1024,
        format="mp4",
        upload_time=datetime(2024, 1, 1, 12, 0),
        status="pending",
    )


def test_video_initialization(video_id):
    """Test basic video initialization with minimal fields."""
    video = Video(id=video_id, filename="video.mp4", file_size=1024, format="mp4")

    assert str(video.id) == str(video_id)
    assert video.filename == "video.mp4"
    assert video.file_size == 1024
    assert video.format == "MP4"  # Should be uppercase
    assert not video.is_complete
    assert video.error_message is None


def test_video_initialization_with_all_fields(video_id):
    upload_time = datetime.now()
    video = Video(
        id=video_id,
        filename="test.mp4",
        file_size=1024,
        format="mp4",
        upload_time=upload_time,
        status="processing",
        processing_progress=50.0,
        error_message="test error",
    )

    assert video.id == video_id
    assert video.filename == "test.mp4"
    assert video.file_size == 1024
    assert video.format == "MP4"
    assert video.upload_time == upload_time
    assert video.status == "processing"
    assert video.processing_progress == 50.0
    assert video.error_message == "test error"


def test_post_init_format_normalization():
    # Test format normalization with different cases
    video1 = Video(filename="test.mp4", file_size=1024, format="mp4")
    assert video1.format == "MP4"

    video2 = Video(filename="test.MP4", file_size=1024, format="MP4")
    assert video2.format == "MP4"

    video3 = Video(filename="test.mP4", file_size=1024, format="mP4")
    assert video3.format == "MP4"


def test_post_init_id_conversion():
    # Test UUID string conversion
    uuid_str = "12345678-1234-5678-1234-567812345678"
    video = Video(id=uuid_str, filename="test.mp4", file_size=1024, format="mp4")
    assert isinstance(video.id, UUID)
    assert str(video.id) == uuid_str


def test_file_path_property(sample_video):
    expected_path = f"{sample_video.id}/test.mp4"
    assert sample_video.file_path == expected_path


def test_is_complete_property():
    # Test with different status values
    video1 = Video(filename="test.mp4", file_size=1024, format="mp4", status="complete")
    assert video1.is_complete is True

    video2 = Video(filename="test.mp4", file_size=1024, format="mp4", status="pending")
    assert video2.is_complete is False

    video3 = Video(
        filename="test.mp4", file_size=1024, format="mp4", status="processing"
    )
    assert video3.is_complete is False


def test_has_error_property():
    # Test with different status values
    video1 = Video(filename="test.mp4", file_size=1024, format="mp4", status="error")
    assert video1.has_error is True

    video2 = Video(filename="test.mp4", file_size=1024, format="mp4", status="pending")
    assert video2.has_error is False

    video3 = Video(filename="test.mp4", file_size=1024, format="mp4", status="complete")
    assert video3.has_error is False


def test_from_path_classmethod(tmp_path, video_id):
    # Create a test file
    video_path = tmp_path / "test.mp4"
    video_path.write_bytes(b"test content")

    # Create video instance from path
    video = Video.from_path(video_path, video_id)

    assert video.id == video_id
    assert video.filename == "test.mp4"
    assert video.format == "MP4"
    assert video.status == "pending"
    assert video.file_size == len(b"test content")


def test_from_path_with_custom_status(tmp_path, video_id):
    video_path = tmp_path / "test.mp4"
    video_path.write_bytes(b"test content")

    video = Video.from_path(video_path, video_id, status="processing")
    assert video.status == "processing"


def test_video_equality(video_id):
    """Test video equality based on ID."""
    # Two videos with same ID should be equal regardless of other fields
    video1 = Video(filename="test1.mp4", file_size=1024, format="mp4", id=video_id)
    video2 = Video(filename="test2.mp4", file_size=2048, format="mp4", id=video_id)

    # Videos are equal if they have the same ID
    assert video1 == video2

    # Different IDs make videos not equal
    video3 = Video(filename="test1.mp4", file_size=1024, format="mp4")
    assert video1 != video3


def test_video_representation(sample_video):
    # Test string representation
    video_str = str(sample_video)
    assert sample_video.filename in video_str
    assert str(sample_video.id) in video_str
    assert sample_video.status in video_str


def test_video_creation():
    """Test basic video creation with required fields."""
    video = Video(filename="test.mp4", file_size=1024, format="mp4")
    assert isinstance(video.id, UUID)
    assert video.filename == "test.mp4"
    assert video.file_size == 1024
    assert video.format == "MP4"  # Should be uppercase
    assert isinstance(video.upload_time, datetime)
    assert video.status == "pending"
    assert video.processing_progress is None
    assert video.error_message is None


def test_video_with_custom_id():
    """Test video creation with custom UUID."""
    custom_id = uuid4()
    video = Video(
        id=custom_id,
        filename="test.mp4",
        file_size=1024,
        format="mp4",
    )
    assert video.id == custom_id


def test_video_with_string_id():
    """Test video creation with string UUID."""
    id_str = "123e4567-e89b-12d3-a456-426614174000"
    video = Video(
        id=id_str,
        filename="test.mp4",
        file_size=1024,
        format="mp4",
    )
    assert isinstance(video.id, UUID)
    assert str(video.id) == id_str


def test_format_normalization():
    """Test that video format is normalized to uppercase."""
    video = Video(filename="test.mp4", file_size=1024, format="mp4")
    assert video.format == "MP4"

    video = Video(filename="test.AVI", file_size=1024, format="AVI")
    assert video.format == "AVI"


def test_file_path_property():
    """Test the file_path property."""
    video = Video(
        id="123e4567-e89b-12d3-a456-426614174000",
        filename="test.mp4",
        file_size=1024,
        format="mp4",
    )
    assert video.file_path == "123e4567-e89b-12d3-a456-426614174000/test.mp4"


def test_status_properties():
    """Test is_complete and has_error properties."""
    video = Video(filename="test.mp4", file_size=1024, format="mp4")
    assert not video.is_complete  # Default status is "pending"
    assert not video.has_error

    video.status = "complete"
    assert video.is_complete
    assert not video.has_error

    video.status = "error"
    assert not video.is_complete
    assert video.has_error


def test_video_progress_tracking():
    """Test processing progress tracking"""
    video = Video(filename="test.mp4", file_size=1024, format="MP4")

    # Test progress updates
    video.processing_progress = 50.0
    assert video.processing_progress == 50.0

    # Test completion
    video.processing_progress = 100.0
    video.status = "complete"
    assert video.is_complete
    assert video.processing_progress == 100.0


def test_video_error_handling():
    """Test error handling in Video model"""
    video = Video(filename="test.mp4", file_size=1024, format="MP4")

    # Set error state
    video.status = "error"
    video.error_message = "Test error message"

    assert video.has_error
    assert video.error_message == "Test error message"
    assert not video.is_complete
