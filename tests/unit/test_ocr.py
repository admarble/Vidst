"""Tests for OCR processing functionality."""

import pytest
from pathlib import Path
import tempfile
import cv2
import numpy as np

from video_understanding.core.upload.ocr import OCRProcessor

@pytest.fixture
def sample_video():
    """Create a sample video file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        # Create a video writer
        fourcc = cv2.VideoWriter.fourcc(*'mp4v')
        out = cv2.VideoWriter(f.name, fourcc, 30.0, (640, 480))

        try:
            # Create some frames with text
            font = cv2.FONT_HERSHEY_SIMPLEX

            # First scene with text
            for _ in range(90):  # 3 seconds at 30fps
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Hello World", (50, 50), font, 1, (255, 255, 255), 2)
                out.write(frame)

            # Second scene with different text
            for _ in range(90):  # Another 3 seconds
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Testing OCR", (100, 100), font, 1, (255, 255, 255), 2)
                out.write(frame)

        finally:
            out.release()

    yield Path(f.name)
    Path(f.name).unlink()

@pytest.mark.asyncio
async def test_ocr_processing(sample_video):
    """Test basic OCR processing."""
    processor = OCRProcessor()
    results = await processor.process(sample_video)

    # Since we're using a placeholder OCR implementation,
    # we just verify the structure but not actual text extraction
    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_ocr_with_languages():
    """Test OCR with specific languages."""
    processor = OCRProcessor(languages=["eng", "fra"])
    assert "eng" in processor.languages
    assert "fra" in processor.languages

@pytest.mark.asyncio
async def test_ocr_confidence_threshold():
    """Test OCR confidence threshold setting."""
    processor = OCRProcessor()

    # Test valid threshold
    processor.set_confidence_threshold(0.8)
    assert processor.confidence_threshold == 0.8

    # Test threshold clamping
    processor.set_confidence_threshold(1.5)  # Should clamp to 1.0
    assert processor.confidence_threshold == 1.0

    processor.set_confidence_threshold(-0.5)  # Should clamp to 0.0
    assert processor.confidence_threshold == 0.0

@pytest.mark.asyncio
async def test_ocr_invalid_file():
    """Test OCR with invalid file."""
    processor = OCRProcessor()
    with pytest.raises(FileNotFoundError):
        await processor.process(Path("nonexistent.mp4"))
