"""Unit tests for the core processing module."""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

import cv2
import numpy as np
import pytest

from video_understanding.core.exceptions import ProcessingError, ValidationError
from video_understanding.core.processing import (
    SceneResults,
    VideoProcessor,
    VideoResults,
    detect_text,
    extract_frames,
    process_video,
    transcribe_audio,
)
from video_understanding.models.video import Video, VideoFile


@pytest.fixture
def video_processor():
    """Create a VideoProcessor instance for testing."""
    return VideoProcessor()


@pytest.fixture
def sample_video():
    """Create a sample Video object for testing."""
    video_id = uuid4()
    file_info = VideoFile(
        filename="test.mp4",
        file_path="/path/to/test.mp4",
        format="mp4",
        file_size=1024,
        duration=10.0,
        width=1920,
        height=1080,
        fps=30.0,
    )
    return Video(id=video_id, file_info=file_info, upload_time=datetime.now())


@pytest.fixture
def mock_cv2():
    """Mock cv2 functionality."""
    with patch("cv2.VideoCapture") as mock_capture:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.side_effect = [(True, np.zeros((100, 100, 3))), (False, None)]
        mock_cap.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 300,
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080,
        }.get(prop, 0)
        mock_capture.return_value = mock_cap
        yield mock_capture


class TestVideoProcessor:
    """Test cases for VideoProcessor class."""

    def test_init(self, video_processor):
        """Test VideoProcessor initialization."""
        assert isinstance(video_processor.processed_videos, dict)
        assert isinstance(video_processor.scene_cache, dict)
        assert len(video_processor.processed_videos) == 0
        assert len(video_processor.scene_cache) == 0

    def test_validate_video_data_valid(self, video_processor):
        """Test video data validation with valid data."""
        valid_data = {"video_id": "test_id", "file_path": "/path/to/video.mp4"}
        video_processor.validate_video_data(valid_data)  # Should not raise

    def test_validate_video_data_invalid_type(self, video_processor):
        """Test video data validation with invalid type."""
        with pytest.raises(ValidationError, match="Video data must be a dictionary"):
            video_processor.validate_video_data("not a dict")

    def test_validate_video_data_missing_id(self, video_processor):
        """Test video data validation with missing video_id."""
        invalid_data = {"file_path": "/path/to/video.mp4"}
        with pytest.raises(ValidationError, match="Missing required field: video_id"):
            video_processor.validate_video_data(invalid_data)

    def test_validate_video_data_missing_path(self, video_processor):
        """Test video data validation with missing file_path."""
        invalid_data = {"video_id": "test_id"}
        with pytest.raises(ValidationError, match="Missing required field: file_path"):
            video_processor.validate_video_data(invalid_data)

    def test_process_cached_result(self, video_processor):
        """Test retrieving cached processing results."""
        video_id = "test_id"
        cached_result = VideoResults(scenes=[], transcription={}, text=[], metadata={})
        video_processor.processed_videos[video_id] = cached_result

        result = video_processor.process(
            {"video_id": video_id, "file_path": "test.mp4"}
        )
        assert result == cached_result

    def test_process_new_video(self, video_processor):
        """Test processing a new video."""
        video_data = {"video_id": "new_test_id", "file_path": "/path/to/video.mp4"}
        result = video_processor.process(video_data)

        assert isinstance(result, dict)
        assert "scenes" in result
        assert "transcription" in result
        assert "text" in result
        assert "metadata" in result
        assert video_data["video_id"] in video_processor.processed_videos

    def test_process_validation_error(self, video_processor):
        """Test process with invalid data."""
        with pytest.raises(ValidationError):
            video_processor.process({})

    def test_validate_scene_data_valid(self, video_processor):
        """Test scene data validation with valid data."""
        valid_data = {"scene_id": "test_scene"}
        video_processor.validate_scene_data(valid_data)  # Should not raise

    def test_validate_scene_data_invalid_type(self, video_processor):
        """Test scene data validation with invalid type."""
        with pytest.raises(ValidationError, match="Scene data must be a dictionary"):
            video_processor.validate_scene_data("not a dict")

    def test_validate_scene_data_missing_id(self, video_processor):
        """Test scene data validation with missing scene_id."""
        with pytest.raises(ValidationError, match="Missing required field: scene_id"):
            video_processor.validate_scene_data({})

    def test_analyze_scene_cached_result(self, video_processor):
        """Test retrieving cached scene analysis results."""
        scene_id = "test_scene"
        cached_result = SceneResults(
            start_time=0.0, end_time=1.0, keyframes=[], text=[], objects=[]
        )
        video_processor.scene_cache[scene_id] = cached_result

        result = video_processor.analyze_scene({"scene_id": scene_id})
        assert result == cached_result

    def test_analyze_scene_new(self, video_processor):
        """Test analyzing a new scene."""
        scene_data = {"scene_id": "new_test_scene"}
        result = video_processor.analyze_scene(scene_data)

        assert isinstance(result, dict)
        assert "start_time" in result
        assert "end_time" in result
        assert "keyframes" in result
        assert "text" in result
        assert "objects" in result
        assert scene_data["scene_id"] in video_processor.scene_cache

    def test_analyze_scene_validation_error(self, video_processor):
        """Test analyze_scene with invalid data."""
        with pytest.raises(ValidationError):
            video_processor.analyze_scene({})

    def test_process_unexpected_error(self, video_processor):
        """Test handling of unexpected errors in process method."""
        with patch.object(
            video_processor,
            "validate_video_data",
            side_effect=Exception("Unexpected error"),
        ):
            with pytest.raises(
                ProcessingError, match="Unexpected error during video processing"
            ):
                video_processor.process({"video_id": "test", "file_path": "test.mp4"})

    def test_analyze_scene_unexpected_error(self, video_processor):
        """Test handling of unexpected errors in analyze_scene method."""
        with patch.object(
            video_processor,
            "validate_scene_data",
            side_effect=Exception("Unexpected error"),
        ):
            with pytest.raises(
                ProcessingError, match="Unexpected error during scene analysis"
            ):
                video_processor.analyze_scene({"scene_id": "test"})


def test_process_video(sample_video, tmp_path):
    """Test process_video function."""
    result = process_video(sample_video, tmp_path)
    assert isinstance(result, dict)
    assert "scenes" in result
    assert "transcription" in result
    assert "text" in result
    assert "metadata" in result


def test_process_video_error(sample_video):
    """Test process_video with invalid video."""
    sample_video.file_info.file_path = "nonexistent.mp4"
    with pytest.raises(ProcessingError):
        process_video(sample_video)


def test_process_video_unexpected_error(sample_video):
    """Test handling of unexpected errors in process_video function."""
    with patch(
        "src.core.processing.VideoProcessor.process",
        side_effect=Exception("Unexpected error"),
    ):
        with pytest.raises(ProcessingError, match="Failed to process video"):
            process_video(sample_video)


def test_extract_frames(sample_video, tmp_path, mock_cv2):
    """Test frame extraction from video."""
    frame_paths = extract_frames(sample_video, tmp_path)
    assert isinstance(frame_paths, list)
    assert len(frame_paths) > 0
    assert all(isinstance(p, Path) for p in frame_paths)


def test_extract_frames_invalid_video(sample_video, tmp_path):
    """Test frame extraction with invalid video."""
    sample_video.file_info.file_path = "nonexistent.mp4"
    with pytest.raises(ProcessingError):
        extract_frames(sample_video, tmp_path)


def test_extract_frames_empty_video(sample_video, tmp_path, mock_cv2):
    """Test frame extraction with empty video."""
    mock_cv2.VideoCapture.return_value.read.return_value = (False, None)
    frame_paths = extract_frames(sample_video, tmp_path)
    assert isinstance(frame_paths, list)
    assert len(frame_paths) == 0


@patch("cv2.imread")
def test_detect_text(mock_imread):
    """Test text detection in frame."""
    # Mock frame data
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    mock_imread.return_value = frame

    # Test text detection
    detections = detect_text(frame)
    assert isinstance(detections, list)
    for detection in detections:
        assert isinstance(detection, dict)
        assert "text" in detection
        assert "confidence" in detection
        assert "bbox" in detection


@patch("cv2.imread")
def test_detect_text_error(mock_imread):
    """Test error handling in text detection."""
    # Mock frame data
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    mock_imread.side_effect = Exception("OCR error")

    with pytest.raises(ProcessingError, match="Failed to detect text"):
        detect_text(frame)


@patch("cv2.imread")
def test_detect_text_empty_frame(mock_imread):
    """Test text detection with empty frame."""
    # Mock empty frame
    frame = np.zeros((0, 0, 3), dtype=np.uint8)
    mock_imread.return_value = frame

    detections = detect_text(frame)
    assert isinstance(detections, list)
    assert len(detections) == 0


def test_transcribe_audio(sample_video):
    """Test audio transcription."""
    result = transcribe_audio(sample_video)
    assert isinstance(result, dict)
    assert "text" in result
    assert "segments" in result
    assert "speakers" in result


def test_transcribe_audio_error(sample_video):
    """Test error handling in audio transcription."""
    with patch(
        "src.core.processing.transcribe_audio",
        side_effect=Exception("Transcription error"),
    ):
        with pytest.raises(ProcessingError, match="Failed to transcribe audio"):
            transcribe_audio(sample_video)
