"""Unit tests for video processing pipeline."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest

from src.ai.models.base import BaseModel
from src.ai.pipeline import VideoPipeline
from src.core.config import VideoConfig
from src.core.exceptions import ProcessingError


class MockModel(BaseModel):
    """Mock model for testing."""

    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.validate_called = False
        self.process_called = False

    def validate(self, input_data):
        self.validate_called = True
        if self.should_fail:
            raise ValueError("Validation failed")
        return True

    def process(self, input_data):
        self.process_called = True
        if self.should_fail:
            raise ValueError("Processing failed")
        return {"test_key": "test_value"}


@pytest.fixture
def config():
    """Create test configuration."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield VideoConfig(
            upload_directory=Path(temp_dir),
            supported_formats=["MP4", "AVI", "MOV"],
            max_file_size=1024 * 1024 * 1024,  # 1GB
        )


@pytest.fixture
def pipeline(config):
    """Create pipeline instance."""
    return VideoPipeline(config)


@pytest.fixture
def test_video_file():
    """Create a test video file."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        # Create a small test video
        width, height = 64, 64
        fps = 30.0
        writer = cv2.VideoWriter(
            temp_file.name,
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height),
        )

        # Write some frames
        for _ in range(30):  # 1 second of video
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            writer.write(frame)

        writer.release()
        path = Path(temp_file.name)
        yield path
        path.unlink(missing_ok=True)  # Use Path.unlink() and handle missing file case


def test_initialization(config):
    """Test pipeline initialization."""
    # Test with no models
    pipeline = VideoPipeline(config)
    assert len(pipeline.models) == 0

    # Test with models
    models = [MockModel(), MockModel()]
    pipeline = VideoPipeline(config, models)
    assert len(pipeline.models) == 2
    assert all(isinstance(model, BaseModel) for model in pipeline.models)


def test_add_model(pipeline):
    """Test adding models to pipeline."""
    model = MockModel()
    pipeline.add_model(model)
    assert len(pipeline.models) == 1
    assert pipeline.models[0] is model


def test_process_basic_validation(pipeline, test_video_file):
    """Test basic input validation."""
    # Test with string path
    result = pipeline.process(str(test_video_file))
    assert result["status"] == "completed"
    assert "metadata" in result

    # Test with Path object
    result = pipeline.process(test_video_file)
    assert result["status"] == "completed"
    assert "metadata" in result

    # Test with dictionary input
    result = pipeline.process({"video_path": str(test_video_file)})
    assert result["status"] == "completed"
    assert "metadata" in result


def test_process_validation_errors(pipeline):
    """Test input validation errors."""
    # Test missing video path
    with pytest.raises(ProcessingError, match="Missing required video_path"):
        pipeline.process({})

    # Test non-existent file
    with pytest.raises(ProcessingError, match="Video file not found"):
        pipeline.process("nonexistent.mp4")

    # Test empty file
    with tempfile.NamedTemporaryFile(suffix=".mp4") as temp_file:
        with pytest.raises(ProcessingError, match="Video file is empty"):
            pipeline.process(temp_file.name)


def test_process_corrupted_video(pipeline):
    """Test handling of corrupted video files."""
    with tempfile.NamedTemporaryFile(suffix=".mp4") as temp_file:
        temp_file.write(b"not a video file")
        temp_file.flush()
        with pytest.raises(ProcessingError, match="Failed to open video file"):
            pipeline.process(temp_file.name)


def test_process_with_models(pipeline, test_video_file):
    """Test processing with multiple models."""
    # Add two mock models
    models = [MockModel(), MockModel()]
    for model in models:
        pipeline.add_model(model)

    # Process video
    result = pipeline.process(test_video_file)

    # Verify all models were called
    for model in models:
        assert model.validate_called
        assert model.process_called

    # Verify results were combined
    assert result["status"] == "completed"
    assert result["test_key"] == "test_value"


def test_process_model_failure(pipeline, test_video_file):
    """Test handling of model failures."""
    # Add failing model
    pipeline.add_model(MockModel(should_fail=True))

    # Test validation failure
    with pytest.raises(ProcessingError, match="Model processing failed"):
        pipeline.process(test_video_file)


def test_scene_detection(pipeline, test_video_file):
    """Test scene detection functionality."""
    # Mock model that returns scene data
    mock_model = MockModel()
    mock_model.process = MagicMock(
        return_value={
            "scenes": [
                {"start": 0, "end": 1, "description": "Scene 1"},
                {"start": 1, "end": 2, "description": "Scene 2"},
            ]
        }
    )
    pipeline.add_model(mock_model)

    scenes = pipeline.detect_scenes(test_video_file)
    assert len(scenes) == 2
    assert scenes[0]["description"] == "Scene 1"
    assert scenes[1]["description"] == "Scene 2"


def test_audio_transcription(pipeline, test_video_file):
    """Test audio transcription functionality."""
    # Mock model that returns transcription data
    mock_model = MockModel()
    mock_model.process = MagicMock(
        return_value={
            "transcription": {
                "text": "Test transcription",
                "segments": [{"start": 0, "end": 1, "text": "Test"}],
            }
        }
    )
    pipeline.add_model(mock_model)

    transcription = pipeline.transcribe_audio(test_video_file)
    assert transcription["text"] == "Test transcription"
    assert len(transcription["segments"]) == 1


def test_text_extraction(pipeline, test_video_file):
    """Test text extraction functionality."""
    # Mock model that returns text extraction data
    mock_model = MockModel()
    mock_model.process = MagicMock(
        return_value={
            "text_segments": [
                {"text": "Text 1", "confidence": 0.9, "timestamp": 1.0},
                {"text": "Text 2", "confidence": 0.8, "timestamp": 2.0},
            ]
        }
    )
    pipeline.add_model(mock_model)

    text_segments = pipeline.extract_text(test_video_file)
    assert len(text_segments) == 2
    assert text_segments[0]["text"] == "Text 1"
    assert text_segments[1]["text"] == "Text 2"


def test_memory_usage(pipeline):
    """Test memory usage monitoring."""
    usage = pipeline.get_memory_usage()
    assert "rss" in usage
    assert "vms" in usage
    assert "percent" in usage
    assert isinstance(usage["rss"], float)
    assert isinstance(usage["vms"], float)
    assert isinstance(usage["percent"], float)


def test_process_edge_cases(pipeline, test_video_file):
    """Test processing edge cases."""
    # Test very short video
    with patch("cv2.VideoCapture") as mock_cap:
        mock_cap.return_value.get.side_effect = [
            30.0,  # fps
            1,  # frame_count
            640,  # width
            480,  # height
        ]
        mock_cap.return_value.isOpened.return_value = True
        result = pipeline.process(test_video_file)
        assert result["scene_description"] == "Video too short for analysis"

    # Test video with no frames
    with patch("cv2.VideoCapture") as mock_cap:
        mock_cap.return_value.get.side_effect = [
            30.0,  # fps
            0,  # frame_count
            640,  # width
            480,  # height
        ]
        mock_cap.return_value.isOpened.return_value = True
        result = pipeline.process(test_video_file)
        assert result["scene_description"] == "No visual content detected"

    # Test normal video without content analysis
    with patch("cv2.VideoCapture") as mock_cap:
        mock_cap.return_value.get.side_effect = [
            30.0,  # fps
            300,  # frame_count (10 seconds)
            640,  # width
            480,  # height
        ]
        mock_cap.return_value.isOpened.return_value = True
        result = pipeline.process(test_video_file)
        assert result["scene_description"] == "No content analysis available"


def test_concurrent_processing(pipeline, test_video_file):
    """Test concurrent video processing."""
    import threading

    def process_video():
        result = pipeline.process(test_video_file)
        assert result["status"] == "completed"

    # Create multiple threads to process the same video
    threads = [threading.Thread(target=process_video) for _ in range(3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def test_process_with_custom_tasks(pipeline, test_video_file):
    """Test processing with custom task configurations."""
    # Test with specific task
    result = pipeline.process(
        {
            "video_path": str(test_video_file),
            "task": "scene_detection",
        }
    )
    assert result["status"] == "completed"

    # Test with multiple tasks
    result = pipeline.process(
        {
            "video_path": str(test_video_file),
            "tasks": ["scene_detection", "transcription"],
        }
    )
    assert result["status"] == "completed"
