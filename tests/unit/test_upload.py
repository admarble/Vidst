"""Tests for video upload functionality."""

import pytest
from pathlib import Path
import tempfile
import cv2
import numpy as np

from video_understanding.core.upload import VideoUploader, UploadConfig
from video_understanding.core.exceptions import VideoUnderstandingError

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
async def test_video_upload_processing(sample_video):
    """Test basic video upload processing."""
    uploader = VideoUploader()
    results = await uploader.process_upload(sample_video)

    assert results is not None
    assert "metadata" in results
    assert "scenes" in results
    assert len(results["scenes"]) > 0

@pytest.mark.asyncio
async def test_upload_invalid_file():
    """Test handling of invalid file."""
    uploader = VideoUploader()
    with pytest.raises(VideoUnderstandingError):
        await uploader.process_upload(Path("nonexistent.mp4"))

@pytest.mark.asyncio
async def test_batch_processing(sample_video):
    """Test batch video processing."""
    uploader = VideoUploader()
    results = await uploader.process_batch([sample_video, sample_video])

    assert len(results) == 2
    for result in results:
        assert isinstance(result, dict)
        assert "metadata" in result
        assert "scenes" in result

@pytest.mark.asyncio
async def test_custom_config():
    """Test uploader with custom configuration."""
    config = UploadConfig(
        max_file_size_mb=100,
        allowed_extensions=[".mp4"],
        detection_enabled=True,
        ocr_enabled=False
    )
    uploader = VideoUploader(config)

    assert uploader.config.max_file_size_mb == 100
    assert uploader.config.allowed_extensions == [".mp4"]
    assert uploader.config.detection_enabled is True
    assert uploader.config.ocr_enabled is False
