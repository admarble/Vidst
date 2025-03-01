"""Unit tests for video processing pipeline."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from video_understanding.ai.models.base import BaseModel
from video_understanding.ai.models.twelve_labs import (
    APITimeoutError,
    TwelveLabsError,
)
from video_understanding.ai.models.twelve_labs import (
    TwelveLabsRateLimitError as RateLimitError,
)
from video_understanding.ai.pipeline import VideoPipeline
from video_understanding.core.config import ProcessingConfig
from video_understanding.core.exceptions import ProcessingError


@pytest.fixture
def mock_video_config():
    """Create a mock video configuration."""
    return ProcessingConfig()


@pytest.fixture
def mock_model():
    """Create a mock AI model."""
    model = Mock(spec=BaseModel)
    model.validate.return_value = True
    model.process.return_value = {
        "scene_description": "Test scene",
        "scenes": [{"start": 0, "end": 5}],
        "transcription": {"text": "Test transcript"},
        "text_segments": [{"text": "Test OCR", "timestamp": 1.0}],
    }
    return model


@pytest.fixture
def mock_video_capture():
    """Create a mock video capture."""
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.get.side_effect = [30.0, 300, 1920, 1080]  # fps, frames, width, height
    return mock_cap


@pytest.fixture
def pipeline(mock_video_config, mock_model):
    """Create a pipeline instance with mock model."""
    pipeline = VideoPipeline(mock_video_config)
    pipeline.add_model(mock_model)
    return pipeline


def test_pipeline_initialization(mock_video_config):
    """Test pipeline initialization."""
    pipeline = VideoPipeline(mock_video_config)
    assert pipeline.config == mock_video_config
    assert pipeline.models == []

    model = Mock(spec=BaseModel)
    pipeline = VideoPipeline(mock_video_config, [model])
    assert pipeline.models == [model]


def test_add_model(mock_video_config):
    """Test adding a model to the pipeline."""
    pipeline = VideoPipeline(mock_video_config)
    model = Mock(spec=BaseModel)
    pipeline.add_model(model)
    assert model in pipeline.models


@patch("cv2.VideoCapture")
def test_process_valid_video(mock_capture, pipeline, mock_video_capture, tmp_path):
    """Test processing a valid video file."""
    # Setup mock video file
    video_path = tmp_path / "test.mp4"
    video_path.write_bytes(b"test video content")

    # Setup mock video capture
    mock_capture.return_value = mock_video_capture

    # Process video with dictionary input
    result = pipeline.process({"video_path": str(video_path)})

    # Verify results
    assert result["status"] == "completed"
    assert result["metadata"]["duration"] == 10.0  # 300 frames / 30 fps
    assert result["metadata"]["frame_count"] == 300
    assert result["metadata"]["resolution"] == (1920, 1080)
    assert result["metadata"]["fps"] == 30.0
    assert result["scene_description"] == "Test scene"
    assert result["scenes"] == [{"start": 0, "end": 5}]
    assert result["transcription"] == {"text": "Test transcript"}
    assert result["text_segments"] == [{"text": "Test OCR", "timestamp": 1.0}]


def test_process_missing_video(pipeline):
    """Test processing with missing video file."""
    with pytest.raises(ProcessingError, match="Video file not found"):
        pipeline.process("nonexistent.mp4")


def test_process_empty_video(pipeline, tmp_path):
    """Test processing an empty video file."""
    video_path = tmp_path / "empty.mp4"
    video_path.write_bytes(b"")

    with pytest.raises(ProcessingError, match="Video file is empty"):
        pipeline.process(str(video_path))


@patch("cv2.VideoCapture")
def test_process_corrupted_video(mock_capture, pipeline, tmp_path):
    """Test processing a corrupted video file."""
    video_path = tmp_path / "corrupted.mp4"
    video_path.write_bytes(b"corrupted content")

    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = False
    mock_capture.return_value = mock_cap

    with pytest.raises(
        ProcessingError, match="Failed to open video file - file may be corrupted"
    ):
        pipeline.process(str(video_path))


@patch("cv2.VideoCapture")
def test_process_model_failure(mock_capture, pipeline, mock_video_capture, tmp_path):
    """Test handling of model processing failure."""
    video_path = tmp_path / "test.mp4"
    video_path.write_bytes(b"test content")

    # Setup mock video capture
    mock_capture.return_value = mock_video_capture

    # Make model validation fail
    pipeline.models[0].validate.return_value = True  # Let validation pass
    pipeline.models[0].process.side_effect = Exception("Model failed")

    with pytest.raises(ProcessingError, match="Model processing failed"):
        pipeline.process({"video_path": str(video_path)})


@patch("cv2.VideoCapture")
def test_detect_scenes(mock_capture, pipeline, mock_video_capture, tmp_path):
    """Test scene detection."""
    video_path = tmp_path / "test.mp4"
    video_path.write_bytes(b"test content")

    # Setup mock video capture
    mock_capture.return_value = mock_video_capture

    scenes = pipeline.detect_scenes(video_path)
    assert scenes == [{"start": 0, "end": 5}]
    # Verify the process method was called with correct input
    pipeline.models[0].process.assert_called_with(
        {"task": "scene_detection", "video_path": str(video_path)}
    )


@patch("cv2.VideoCapture")
def test_transcribe_audio(mock_capture, pipeline, mock_video_capture, tmp_path):
    """Test audio transcription."""
    video_path = tmp_path / "test.mp4"
    video_path.write_bytes(b"test content")

    # Setup mock video capture
    mock_capture.return_value = mock_video_capture

    transcription = pipeline.transcribe_audio(video_path)
    assert transcription == {"text": "Test transcript"}
    # Verify the process method was called with correct input
    pipeline.models[0].process.assert_called_with(
        {"task": "transcription", "video_path": str(video_path)}
    )


@patch("cv2.VideoCapture")
def test_extract_text(mock_capture, pipeline, mock_video_capture, tmp_path):
    """Test text extraction."""
    video_path = tmp_path / "test.mp4"
    video_path.write_bytes(b"test content")

    # Setup mock video capture
    mock_capture.return_value = mock_video_capture

    text_segments = pipeline.extract_text(video_path)
    assert text_segments == [{"text": "Test OCR", "timestamp": 1.0}]
    # Verify the process method was called with correct input
    pipeline.models[0].process.assert_called_with(
        {"task": "text_extraction", "video_path": str(video_path)}
    )


@patch("psutil.Process")
def test_get_memory_usage(mock_process):
    """Test memory usage statistics."""
    mock_process_instance = Mock()
    mock_memory_info = Mock()
    mock_memory_info.rss = 1024 * 1024 * 100  # 100 MB
    mock_memory_info.vms = 1024 * 1024 * 200  # 200 MB
    mock_process_instance.memory_info.return_value = mock_memory_info
    mock_process_instance.memory_percent.return_value = 5.0
    mock_process.return_value = mock_process_instance

    pipeline = VideoPipeline(ProcessingConfig())
    memory_stats = pipeline.get_memory_usage()

    assert memory_stats["rss"] == 100.0  # MB
    assert memory_stats["vms"] == 200.0  # MB
    assert memory_stats["percent"] == 5.0


@patch("cv2.VideoCapture")
def test_process_model_error(mock_capture, pipeline, mock_video_capture, tmp_path):
    """Test handling of model errors during processing."""
    # Setup mock video file
    video_path = tmp_path / "test.mp4"
    video_path.write_bytes(b"test video content")

    # Setup mock video capture
    mock_capture.return_value = mock_video_capture

    # Make model raise an error
    pipeline.models[0].process.side_effect = TwelveLabsError("Test model error")

    # Process video and verify error handling
    result = pipeline.process({"video_path": str(video_path)})
    assert result["status"] == "error"
    assert result["error"] == "Model error: Test model error"


@patch("cv2.VideoCapture")
def test_process_rate_limit_error(mock_capture, pipeline, mock_video_capture, tmp_path):
    """Test handling of rate limit errors during processing."""
    # Setup mock video file
    video_path = tmp_path / "test.mp4"
    video_path.write_bytes(b"test video content")

    # Setup mock video capture
    mock_capture.return_value = mock_video_capture

    # Make model raise a rate limit error
    pipeline.models[0].process.side_effect = RateLimitError("Rate limit exceeded")

    # Process video and verify error handling
    result = pipeline.process({"video_path": str(video_path)})
    assert result["status"] == "error"
    assert result["error"] == "Rate limit exceeded: Rate limit exceeded"


@patch("cv2.VideoCapture")
def test_process_timeout_error(mock_capture, pipeline, mock_video_capture, tmp_path):
    """Test handling of API timeout errors during processing."""
    # Setup mock video file
    video_path = tmp_path / "test.mp4"
    video_path.write_bytes(b"test video content")

    # Setup mock video capture
    mock_capture.return_value = mock_video_capture

    # Make model raise a timeout error
    pipeline.models[0].process.side_effect = APITimeoutError("API request timed out")

    # Process video and verify error handling
    result = pipeline.process({"video_path": str(video_path)})
    assert result["status"] == "error"
    assert result["error"] == "API timeout: API request timed out"
