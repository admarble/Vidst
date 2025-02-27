"""Unit tests for Scene Detection."""

# Standard library imports
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

# Third-party imports
import pytest

# Local imports
from video_understanding.core.scene import SceneDetector
from video_understanding.models.scene import Scene
from video_understanding.models.video import Video, VideoFile


@pytest.fixture
def sample_video() -> Video:
    """Create a sample video instance for testing."""
    file_info = VideoFile(filename="test.mp4", file_size=1024, format="mp4")
    return Video(file_info=file_info, id=uuid4(), upload_time=datetime.now())


@pytest.fixture
def scene_detector() -> SceneDetector:
    """Create a scene detector instance."""
    return SceneDetector()


@pytest.fixture
def mock_video_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary video file for testing."""
    video_path = tmp_path / "test_video.mp4"
    # Create a dummy video file with some content
    video_path.write_bytes(b"test video content")
    yield video_path
    # Cleanup
    if video_path.exists():
        video_path.unlink()


def test_scene_detector_initialization(scene_detector: SceneDetector) -> None:
    """Test basic scene detector initialization."""
    assert scene_detector is not None
    assert hasattr(scene_detector, "detect_scenes")
    assert callable(scene_detector.detect_scenes)


def test_scene_detection_empty_video(
    scene_detector: SceneDetector, sample_video: Video
) -> None:
    """Test scene detection with empty video."""
    with pytest.raises(ValueError, match="Video file not found or empty"):
        scene_detector.detect_scenes(sample_video)


def test_scene_detection_with_valid_video(
    scene_detector: SceneDetector, mock_video_file: Path
) -> None:
    """Test basic scene detection functionality with a valid video."""
    # Create a video instance with the mock file
    video_id = uuid4()
    file_info = VideoFile(
        filename=mock_video_file.name,
        file_size=mock_video_file.stat().st_size,
        format="mp4",
        file_path=str(mock_video_file),
    )
    video = Video(file_info=file_info, id=video_id, upload_time=datetime.now())

    # Mock the actual scene detection since we don't want to process real video
    with patch.object(scene_detector, "_process_video") as mock_process:
        mock_process.return_value = [
            Scene(
                video_id=video_id,
                start_time=0.0,
                end_time=5.0,
                confidence_score=0.95,
                metadata={"description": "Test scene 1"},
            ),
            Scene(
                video_id=video_id,
                start_time=5.0,
                end_time=10.0,
                confidence_score=0.92,
                metadata={"description": "Test scene 2"},
            ),
        ]

        scenes = scene_detector.detect_scenes(video)

        assert isinstance(scenes, list)
        assert len(scenes) == 2
        assert all(isinstance(scene, Scene) for scene in scenes)
        assert scenes[0].start_time == 0.0
        assert scenes[0].end_time == 5.0
        assert scenes[0].confidence_score == 0.95
        assert scenes[1].start_time == 5.0
        assert scenes[1].end_time == 10.0
        assert scenes[1].confidence_score == 0.92


def test_scene_detection_error_handling(
    scene_detector: SceneDetector, mock_video_file: Path
) -> None:
    """Test error handling during scene detection."""
    video_id = uuid4()
    file_info = VideoFile(
        filename=mock_video_file.name,
        file_size=mock_video_file.stat().st_size,
        format="mp4",
        file_path=str(mock_video_file),
    )
    video = Video(file_info=file_info, id=video_id, upload_time=datetime.now())

    # Test processing error
    with patch.object(
        scene_detector, "_process_video", side_effect=RuntimeError("Processing failed")
    ):
        with pytest.raises(RuntimeError, match="Processing failed"):
            scene_detector.detect_scenes(video)

    # Test invalid video format
    invalid_video = Video(
        file_info=VideoFile(filename="test.xyz", file_size=1024, format="xyz"),
        id=uuid4(),
    )
    with pytest.raises(ValueError, match="Unsupported video format"):
        scene_detector.detect_scenes(invalid_video)
