"""Unit tests for the AI pipeline."""

from pathlib import Path
from unittest.mock import Mock, patch

import cv2
import numpy as np
import pytest

from src.ai.models.base import BaseModel
from src.ai.pipeline import VideoPipeline
from src.core.config import VideoConfig
from src.core.exceptions import ProcessingError


class MockModel(BaseModel):
    def process(self, data):
        return {"mock_result": "success"}

    def validate(self, data):
        return True


@pytest.fixture
def config():
    return VideoConfig()


@pytest.fixture
def pipeline(config):
    return VideoPipeline(config=config)


@pytest.fixture
def mock_video_file(tmp_path):
    """Create a mock video file for testing."""
    video_path = tmp_path / "test.mp4"
    # Create a small valid video file
    writer = cv2.VideoWriter(
        str(video_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        30,  # fps
        (640, 480),  # resolution
    )
    # Write a few frames
    for _ in range(30):  # 1 second of video
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        writer.write(frame)
    writer.release()
    return video_path


def test_pipeline_initialization(config):
    """Test pipeline initialization."""
    pipeline = VideoPipeline(config)
    assert pipeline.config == config
    assert pipeline.models == []

    models = [MockModel(), MockModel()]
    pipeline = VideoPipeline(config, models)
    assert pipeline.models == models


def test_add_model(pipeline):
    """Test adding a model to the pipeline."""
    model = MockModel()
    assert len(pipeline.models) == 0
    pipeline.add_model(model)
    assert len(pipeline.models) == 1
    assert pipeline.models[0] == model


def test_process_string_input(pipeline, mock_video_file):
    """Test processing with string input."""
    result = pipeline.process(str(mock_video_file))
    assert result["status"] == "completed"
    assert "metadata" in result
    assert "scene_description" in result


def test_process_path_input(pipeline, mock_video_file):
    """Test processing with Path input."""
    result = pipeline.process(Path(mock_video_file))
    assert result["status"] == "completed"
    assert "metadata" in result


def test_process_dict_input(pipeline, mock_video_file):
    """Test processing with dictionary input."""
    result = pipeline.process({"video_path": str(mock_video_file)})
    assert result["status"] == "completed"
    assert "metadata" in result


def test_process_missing_video_path(pipeline):
    """Test processing without video path."""
    with pytest.raises(ProcessingError, match="Missing required video_path"):
        pipeline.process({})


def test_process_nonexistent_video(pipeline):
    """Test processing non-existent video."""
    with pytest.raises(ProcessingError, match="Video file not found"):
        pipeline.process({"video_path": "nonexistent.mp4"})


def test_process_empty_video(pipeline, tmp_path):
    """Test processing empty video file."""
    empty_file = tmp_path / "empty.mp4"
    empty_file.touch()
    with pytest.raises(ProcessingError, match="Video file is empty"):
        pipeline.process({"video_path": str(empty_file)})


def test_process_corrupted_video(pipeline, tmp_path):
    """Test processing corrupted video file."""
    corrupted_file = tmp_path / "corrupted.mp4"
    corrupted_file.write_bytes(b"not a video file")
    with pytest.raises(ProcessingError, match="Failed to open video file"):
        pipeline.process({"video_path": str(corrupted_file)})


def test_process_with_models(pipeline, mock_video_file):
    """Test processing with multiple models."""
    model1 = Mock(spec=BaseModel)
    model1.validate.return_value = True
    model1.process.return_value = {"stage1": "complete"}

    model2 = Mock(spec=BaseModel)
    model2.validate.return_value = True
    model2.process.return_value = {"stage2": "complete"}

    pipeline.add_model(model1)
    pipeline.add_model(model2)

    result = pipeline.process({"video_path": str(mock_video_file)})

    assert result["status"] == "completed"
    assert result["stage1"] == "complete"
    assert result["stage2"] == "complete"
    model1.process.assert_called_once()
    model2.process.assert_called_once()


def test_process_model_failure(pipeline, mock_video_file):
    """Test processing with model failure."""
    model = Mock(spec=BaseModel)
    model.validate.return_value = True
    model.process.side_effect = Exception("Model failed")
    pipeline.add_model(model)

    with pytest.raises(ProcessingError, match="Model processing failed"):
        pipeline.process({"video_path": str(mock_video_file)})


def test_detect_scenes(pipeline, mock_video_file):
    """Test scene detection."""
    scenes = pipeline.detect_scenes(Path(mock_video_file))
    assert isinstance(scenes, list)


def test_transcribe_audio(pipeline, mock_video_file):
    """Test audio transcription."""
    transcription = pipeline.transcribe_audio(Path(mock_video_file))
    assert isinstance(transcription, dict)


def test_extract_text(pipeline, mock_video_file):
    """Test text extraction."""
    text_segments = pipeline.extract_text(Path(mock_video_file))
    assert isinstance(text_segments, list)


@patch("psutil.Process")
def test_get_memory_usage(mock_process, pipeline):
    """Test memory usage monitoring."""
    process = Mock()
    memory_info = Mock()
    memory_info.rss = 1024 * 1024 * 100  # 100MB
    memory_info.vms = 1024 * 1024 * 200  # 200MB
    process.memory_info.return_value = memory_info
    process.memory_percent.return_value = 5.0
    mock_process.return_value = process

    usage = pipeline.get_memory_usage()

    assert "rss" in usage
    assert "vms" in usage
    assert "percent" in usage
    assert usage["rss"] == 100.0  # MB
    assert usage["vms"] == 200.0  # MB
    assert usage["percent"] == 5.0
