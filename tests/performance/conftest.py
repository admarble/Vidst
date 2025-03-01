"""Common fixtures for performance tests."""

import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from video_understanding.types.cv2 import (
    CAP_PROP_FPS,
    CAP_PROP_FRAME_COUNT,
    CAP_PROP_FRAME_HEIGHT,
    CAP_PROP_FRAME_WIDTH,
)
from tests.config.test_config import PerformanceConfig


@pytest.fixture(scope="session")
def performance_config() -> PerformanceConfig:
    """Provide test configuration."""
    return PerformanceConfig()


@pytest.fixture
def temp_test_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_cv2(mocker) -> MagicMock:
    """Mock cv2 for video processing."""
    mock_cv2 = mocker.patch("cv2.VideoCapture")
    mock_capture = mocker.MagicMock()

    # Set up mock video properties
    mock_capture.get.side_effect = lambda prop: {
        CAP_PROP_FPS: 30.0,
        CAP_PROP_FRAME_COUNT: 9000,  # 5 minutes at 30fps
        CAP_PROP_FRAME_WIDTH: 1920,
        CAP_PROP_FRAME_HEIGHT: 1080,
    }.get(prop, 0)

    mock_capture.isOpened.return_value = True
    mock_capture.read.return_value = (True, mocker.MagicMock())
    mock_cv2.return_value = mock_capture

    return mock_cv2


@pytest.fixture
def mock_twelve_labs(mocker) -> dict:
    """Mock Twelve Labs API responses."""
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [{"name": "default_index"}],
        "task_id": "test_task_id",
        "video_id": "test_video_id",
        "status": "completed",
        "scene_description": "Test scene",
        "objects": [{"name": "test_object"}],
        "actions": [{"description": "test_action"}],
        "metadata": {"duration": 300, "fps": 30, "resolution": "1920x1080"},
    }

    mocker.patch("requests.Session.request", return_value=mock_response)
    mocker.patch(
        "src.ai.models.twelve_labs.TwelveLabsModel._upload_video",
        return_value="test_video_id",
    )
    mocker.patch(
        "src.ai.models.twelve_labs.TwelveLabsModel._track_task_status",
        return_value={
            "status": "completed",
            "video_id": "test_video_id",
            "scene_description": "Test scene",
            "objects": [{"name": "test_object"}],
            "actions": [{"description": "test_action"}],
            "metadata": {"duration": 300, "fps": 30, "resolution": "1920x1080"},
        },
    )

    return {
        "response": mock_response,
        "video_id": "test_video_id",
        "task_id": "test_task_id",
    }


@pytest.fixture
def mock_process_metrics(mocker) -> None:
    """Mock process metrics collection."""
    mock_process = mocker.MagicMock()
    mock_process.memory_info.return_value = MagicMock(rss=100 * 1024 * 1024)  # 100MB
    mock_process.cpu_percent.return_value = 5.0

    mocker.patch("psutil.Process", return_value=mock_process)


@pytest.fixture
def create_test_video(temp_test_dir: Path):
    """Factory fixture for creating test video files."""

    def _create_video(size_mb: int, duration: int) -> Path:
        """Create a test video file.

        Args:
            size_mb: Size in megabytes
            duration: Duration in seconds

        Returns:
            Path to created video file
        """
        video_path = temp_test_dir / f"test_{size_mb}mb_{duration}s.mp4"

        # Create an empty file of the specified size
        with open(video_path, "wb") as f:
            f.seek(size_mb * 1024 * 1024 - 1)
            f.write(b"\0")

        return video_path

    return _create_video
