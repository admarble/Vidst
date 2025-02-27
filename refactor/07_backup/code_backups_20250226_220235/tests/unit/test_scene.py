"""Tests for scene detection functionality."""

import pytest
from pathlib import Path
import tempfile
import cv2
import numpy as np

from video_understanding.core.upload.scene import SceneDetector

@pytest.fixture
def sample_video():
    """Create a sample video file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        # Create a video writer
        fourcc = cv2.VideoWriter.fourcc(*'mp4v')
        out = cv2.VideoWriter(f.name, fourcc, 30.0, (640, 480))

        try:
            # Create some frames
            for _ in range(90):  # 3 seconds at 30fps
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                # Add some content to make scene detection possible
                cv2.rectangle(frame, (100, 100), (200, 200), (0, 255, 0), -1)
                out.write(frame)

            # Create a scene change
            for _ in range(90):  # Another 3 seconds
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                # Different content
                cv2.circle(frame, (320, 240), 100, (0, 0, 255), -1)
                out.write(frame)

        finally:
            out.release()

    yield Path(f.name)
    Path(f.name).unlink()

@pytest.mark.asyncio
async def test_scene_detection(sample_video):
    """Test basic scene detection."""
    detector = SceneDetector()
    scenes = await detector.detect(sample_video)

    assert len(scenes) > 0
    for scene in scenes:
        assert "start_frame" in scene
        assert "end_frame" in scene
        assert "start_time" in scene
        assert "end_time" in scene
        assert "duration" in scene
        assert scene["duration"] > 0

@pytest.mark.asyncio
async def test_scene_detection_config():
    """Test scene detector configuration."""
    detector = SceneDetector()

    # Test min scene duration
    detector.set_min_scene_duration(5.0)
    assert detector.min_scene_duration == 5.0

    # Test max scenes
    detector.set_max_scenes(100)
    assert detector.max_scenes == 100

    # Test threshold
    detector.set_threshold(50.0)
    assert detector.threshold == 50.0

@pytest.mark.asyncio
async def test_scene_detection_invalid_file():
    """Test scene detection with invalid file."""
    detector = SceneDetector()
    scenes = await detector.detect(Path("nonexistent.mp4"))
    assert len(scenes) == 0

@pytest.mark.asyncio
async def test_frame_difference():
    """Test frame difference calculation."""
    detector = SceneDetector()

    # Create two different frames
    frame1 = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(frame1, (100, 100), (200, 200), (0, 255, 0), -1)

    frame2 = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.circle(frame2, (320, 240), 100, (0, 0, 255), -1)

    diff = detector._calculate_frame_diff(frame1, frame2)
    assert diff > 0
