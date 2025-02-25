"""Unit tests for Video model."""

from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from video_understanding.models.video import Video, VideoFile, VideoProcessingStatus


@pytest.fixture
def sample_video() -> Video:
    """Create a sample video instance."""
    file_info = VideoFile(
        filename="test.mp4",
        file_size=1024,
        format="mp4",
    )
    return Video(
        file_info=file_info,
        id=uuid4(),
        upload_time=datetime.now(),
    )


def test_video_initialization() -> None:
    """Test basic video initialization."""
    file_info = VideoFile(filename="test.mp4", file_size=1024, format="mp4")
    video = Video(file_info=file_info)
    assert isinstance(video.id, UUID)
    assert isinstance(video.upload_time, datetime)
    assert video.processing.status == "pending"
    assert video.processing.processing_progress == 0.0
    assert video.processing.error_message == ""


def test_post_init_validation() -> None:
    """Test post initialization validation."""
    # Test UUID conversion
    str_uuid = UUID("550e8400-e29b-41d4-a716-446655440000")
    file_info = VideoFile(filename="test.mp4", file_size=1024, format="mp4")
    video = Video(file_info=file_info, id=str_uuid)
    assert isinstance(video.id, UUID)
    assert str(video.id) == "550e8400-e29b-41d4-a716-446655440000"

    # Test format normalization
    file_info = VideoFile(filename="test.mp4", file_size=1024, format="mp4")
    video = Video(file_info=file_info)
    assert video.file_info.format == "mp4"


def test_equality() -> None:
    """Test video equality comparison."""
    id1 = uuid4()
    id2 = uuid4()

    file_info1 = VideoFile(filename="test1.mp4", file_size=1024, format="mp4")
    file_info2 = VideoFile(filename="test2.mp4", file_size=2048, format="avi")
    file_info3 = VideoFile(filename="test3.mp4", file_size=1024, format="mp4")

    video1 = Video(file_info=file_info1, id=id1)
    video2 = Video(file_info=file_info2, id=id1)
    video3 = Video(file_info=file_info3, id=id2)

    # Same ID should be equal regardless of other attributes
    assert video1 == video2
    # Different IDs should not be equal
    assert video1 != video3
    # Comparison with non-Video object
    assert video1 != "not a video"


def test_file_path() -> None:
    """Test file path generation."""
    file_info = VideoFile(
        filename="test.mp4",
        file_size=1024,
        format="mp4",
    )
    video = Video(
        file_info=file_info,
        id=UUID("550e8400-e29b-41d4-a716-446655440000"),
    )
    assert video.file_path == ""  # file_path is empty by default in VideoFile


def test_status_properties() -> None:
    """Test status-related properties."""
    file_info = VideoFile(filename="test.mp4", file_size=1024, format="mp4")
    video = Video(file_info=file_info)

    # Test initial state
    assert not video.processing.is_complete
    assert not video.processing.has_error

    # Test complete state
    video.processing.status = "complete"
    assert video.processing.is_complete
    assert not video.processing.has_error

    # Test error state
    video.processing.status = "error"
    assert not video.processing.is_complete
    assert video.processing.has_error


def test_from_path(tmp_path: Path) -> None:
    """Test creating video from path."""
    # Create a temporary file
    file_path = tmp_path / "test.mp4"
    file_path.write_text("dummy content")

    video_id = uuid4()
    video = Video.from_path(file_path, video_id, status="processing")

    assert video.file_info.filename == "test.mp4"
    assert video.file_info.format == "MP4"
    assert video.file_info.file_size == len("dummy content")
    assert video.id == video_id
    assert video.processing.status == "processing"


def test_video_with_progress() -> None:
    """Test video with processing progress."""
    file_info = VideoFile(filename="test.mp4", file_size=1024, format="mp4")
    processing = VideoProcessingStatus(processing_progress=50.0)
    video = Video(file_info=file_info, processing=processing)
    assert video.processing.processing_progress == 50.0


def test_video_with_error() -> None:
    """Test video with error message."""
    file_info = VideoFile(filename="test.mp4", file_size=1024, format="mp4")
    processing = VideoProcessingStatus(
        status="error", error_message="Processing failed"
    )
    video = Video(file_info=file_info, processing=processing)
    assert video.processing.has_error
    assert video.processing.error_message == "Processing failed"


def test_file_path_property(sample_video: Video) -> None:
    """Test file path property."""
    expected_path = ""  # file_path is empty by default in VideoFile
    assert sample_video.file_path == expected_path


def test_status_transitions() -> None:
    """Test valid and invalid status transitions."""
    file_info = VideoFile(filename="test.mp4", file_size=1024, format="mp4")
    video = Video(file_info=file_info)

    # Test valid transitions
    valid_statuses = ["pending", "processing", "complete", "error"]
    for status in valid_statuses:
        video.processing.status = status
        assert video.processing.status == status

    # Test status with error message
    video.processing.status = "error"
    video.processing.error_message = "Processing failed"
    assert video.processing.status == "error"
    assert video.processing.error_message == "Processing failed"
