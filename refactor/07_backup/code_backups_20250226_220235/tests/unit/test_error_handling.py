"""Unit tests for error handling and edge cases."""

import tempfile
from pathlib import Path
from typing import Dict
from uuid import uuid4

import cv2
import numpy as np
import pytest
from pytest import MonkeyPatch

from video_understanding.core.exceptions import (
    ConfigurationError,
    FileValidationError,
    ProcessingError,
)
from video_understanding.core.upload.config import ProcessorConfig
from video_understanding.core.upload.processor import VideoProcessor
from video_understanding.core.upload.scene import SceneDetector
from video_understanding.core.upload.detection import ObjectDetector
from video_understanding.core.upload.ocr import OCRProcessor
from video_understanding.models.video import Video, VideoFile, VideoProcessingInfo

@pytest.fixture
def mock_env_vars(monkeypatch: MonkeyPatch) -> Dict[str, str]:
    """Mock environment variables for testing."""
    env_vars = {
        "OPENAI_API_KEY": "test_openai_key",
        "TWELVE_LABS_API_KEY": "test_twelve_labs_key",
        "GOOGLE_API_KEY": "test_google_key",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars

def test_file_validation_errors() -> None:
    """Test various file validation error scenarios."""
    processor = VideoProcessor(ProcessorConfig())

    # Test non-existent file
    with pytest.raises(FileValidationError, match="File not found"):
        file_info = VideoFile(
            filename="nonexistent.mp4",
            file_path=Path("nonexistent.mp4"),
            format="mp4",
            file_size=0
        )
        video = Video(
            id=uuid4(),
            file_info=file_info,
            processing=VideoProcessingInfo()
        )
        processor.process(video)

    # Test empty file
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tf:
        file_info = VideoFile(
            filename=Path(tf.name).name,
            file_path=Path(tf.name),
            format="mp4",
            file_size=0
        )
        video = Video(
            id=uuid4(),
            file_info=file_info,
            processing=VideoProcessingInfo()
        )
        with pytest.raises(FileValidationError, match="File is empty"):
            processor.process(video)

    # Test invalid extension
    with tempfile.NamedTemporaryFile(suffix=".invalid") as tf:
        file_info = VideoFile(
            filename=Path(tf.name).name,
            file_path=Path(tf.name),
            format="invalid",
            file_size=0
        )
        video = Video(
            id=uuid4(),
            file_info=file_info,
            processing=VideoProcessingInfo()
        )
        with pytest.raises(FileValidationError, match="Unsupported format"):
            processor.process(video)

def test_processing_errors() -> None:
    """Test video processing error scenarios."""
    processor = VideoProcessor(ProcessorConfig())

    # Test corrupted video
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tf:
        tf.write(b"corrupted data")
        tf.flush()
        file_info = VideoFile(
            filename=Path(tf.name).name,
            file_path=Path(tf.name),
            format="mp4",
            file_size=len(b"corrupted data")
        )
        video = Video(
            id=uuid4(),
            file_info=file_info,
            processing=VideoProcessingInfo()
        )
        with pytest.raises(ProcessingError):
            processor.process(video)

def test_configuration_errors() -> None:
    """Test configuration error scenarios."""
    # Test invalid config values
    config = ProcessorConfig()
    config.max_video_size = -1
    with pytest.raises(ConfigurationError):
        VideoProcessor(config)

    # Test empty supported formats
    config = ProcessorConfig()
    config.supported_formats = []
    with pytest.raises(ConfigurationError):
        VideoProcessor(config)

    # Test invalid scene length
    config = ProcessorConfig()
    config.min_scene_length = 0
    with pytest.raises(ConfigurationError):
        VideoProcessor(config)

    # Test invalid max scenes
    config = ProcessorConfig()
    config.max_scenes = -1
    with pytest.raises(ConfigurationError):
        VideoProcessor(config)

def test_edge_cases() -> None:
    """Test various edge cases."""
    processor = VideoProcessor(ProcessorConfig())

    # Create a test video with a single black frame
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tf:
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        fourcc = cv2.VideoWriter.fourcc(*'mp4v')
        out = cv2.VideoWriter(tf.name, fourcc, 30.0, (640, 480))
        out.write(frame)
        out.release()

        # Test extremely short video
        file_info = VideoFile(
            filename=Path(tf.name).name,
            file_path=Path(tf.name),
            format="mp4",
            file_size=Path(tf.name).stat().st_size
        )
        video = Video(
            id=uuid4(),
            file_info=file_info,
            processing=VideoProcessingInfo()
        )
        result = processor.process(video)
        assert result is not None

@pytest.mark.asyncio
async def test_scene_detector_errors() -> None:
    """Test scene detector error handling."""
    detector = SceneDetector()

    # Test invalid video path
    with pytest.raises(FileValidationError):
        await detector.detect(Path("nonexistent.mp4"))

@pytest.mark.asyncio
async def test_object_detector_errors() -> None:
    """Test object detector error handling."""
    detector = ObjectDetector()

    # Test invalid input
    with pytest.raises(ProcessingError):
        detector.detect_objects(None)  # type: ignore

    # Test invalid frame shape
    with pytest.raises(ProcessingError):
        detector.detect_objects(np.zeros((10, 10), dtype=np.uint8))  # Wrong number of channels

@pytest.mark.asyncio
async def test_ocr_processor_errors() -> None:
    """Test OCR processor error handling."""
    processor = OCRProcessor()

    # Test invalid file path
    with pytest.raises(FileValidationError):
        await processor.process(Path("nonexistent.mp4"))

    # Test invalid confidence threshold
    with pytest.raises(ValueError):
        processor.set_confidence_threshold(1.5)  # Should be between 0 and 1
