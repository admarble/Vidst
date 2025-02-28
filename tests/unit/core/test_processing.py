"""Unit tests for the core processing module."""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

import cv2
import numpy as np
import pytest
import os
import tempfile
import json

from video_understanding.core.exceptions import ProcessingError, ValidationError
from video_understanding.core.processing import (
    SceneResults,
    VideoProcessor,
    VideoResults,
    detect_text,
    extract_frames,
    process_video,
    transcribe_audio,
    VideoProcessingError,
    VideoFormatError,
    ProcessingJob,
    JobStatus,
    ProcessingContext,
    ProcessingResult,
    JobManager,
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


class TestProcessingJob:
    """Test suite for ProcessingJob class."""

    def test_init(self):
        """Test initialization of ProcessingJob."""
        job = ProcessingJob(
            job_id="test-job-123",
            video_path="/path/to/video.mp4",
            user_id="user123",
            options={"extract_audio": True},
        )

        assert job.job_id == "test-job-123"
        assert job.video_path == "/path/to/video.mp4"
        assert job.user_id == "user123"
        assert job.options == {"extract_audio": True}
        assert job.status == JobStatus.PENDING
        assert job.created_at is not None
        assert job.updated_at is not None
        assert job.result is None
        assert job.error is None

    def test_update_status(self):
        """Test updating job status."""
        job = ProcessingJob(job_id="test-job-123", video_path="/path/to/video.mp4")

        job.update_status(JobStatus.PROCESSING)
        assert job.status == JobStatus.PROCESSING

        job.update_status(JobStatus.COMPLETED)
        assert job.status == JobStatus.COMPLETED

        # Test that updated_at is changed
        previous_updated_at = job.updated_at

        # Force a small delay
        import time

        time.sleep(0.001)

        job.update_status(JobStatus.FAILED)
        assert job.status == JobStatus.FAILED
        assert job.updated_at > previous_updated_at

    def test_set_result(self):
        """Test setting job result."""
        job = ProcessingJob(job_id="test-job-123", video_path="/path/to/video.mp4")
        result = ProcessingResult(
            scene_timestamps=[(0, 10), (10, 20)],
            extracted_frames=["frame1.jpg", "frame2.jpg"],
            transcription="Test transcription",
            metadata={"duration": 30},
        )

        job.set_result(result)

        assert job.result == result
        assert job.status == JobStatus.COMPLETED

    def test_set_error(self):
        """Test setting job error."""
        job = ProcessingJob(job_id="test-job-123", video_path="/path/to/video.mp4")
        error = VideoProcessingError("Test error")

        job.set_error(error)

        assert job.error == "Test error"
        assert job.status == JobStatus.FAILED

    def test_to_dict_and_from_dict(self):
        """Test conversion to and from dictionary."""
        original_job = ProcessingJob(
            job_id="test-job-123",
            video_path="/path/to/video.mp4",
            user_id="user123",
            options={"extract_audio": True},
        )

        # Add a result
        result = ProcessingResult(
            scene_timestamps=[(0, 10), (10, 20)],
            extracted_frames=["frame1.jpg", "frame2.jpg"],
            transcription="Test transcription",
            metadata={"duration": 30},
        )
        original_job.set_result(result)

        # Convert to dict
        job_dict = original_job.to_dict()

        # Create new job from dict
        new_job = ProcessingJob.from_dict(job_dict)

        # Check that the jobs are equivalent
        assert new_job.job_id == original_job.job_id
        assert new_job.video_path == original_job.video_path
        assert new_job.user_id == original_job.user_id
        assert new_job.options == original_job.options
        assert new_job.status == original_job.status
        assert new_job.created_at == original_job.created_at
        assert new_job.updated_at == original_job.updated_at

        # Check result
        assert new_job.result.scene_timestamps == original_job.result.scene_timestamps
        assert new_job.result.extracted_frames == original_job.result.extracted_frames
        assert new_job.result.transcription == original_job.result.transcription
        assert new_job.result.metadata == original_job.result.metadata

    def test_from_dict_with_error(self):
        """Test from_dict with error state."""
        job_dict = {
            "job_id": "test-job-123",
            "video_path": "/path/to/video.mp4",
            "user_id": "user123",
            "options": {"extract_audio": True},
            "status": "FAILED",
            "created_at": "2023-01-01T12:00:00.000000",
            "updated_at": "2023-01-01T12:05:00.000000",
            "result": None,
            "error": "Video processing failed: Invalid format",
        }

        job = ProcessingJob.from_dict(job_dict)

        assert job.job_id == "test-job-123"
        assert job.status == JobStatus.FAILED
        assert job.error == "Video processing failed: Invalid format"
        assert job.result is None


class TestProcessingResult:
    """Test suite for ProcessingResult class."""

    def test_init(self):
        """Test initialization of ProcessingResult."""
        result = ProcessingResult(
            scene_timestamps=[(0, 10), (10, 20)],
            extracted_frames=["frame1.jpg", "frame2.jpg"],
            transcription="Test transcription",
            metadata={"duration": 30},
        )

        assert result.scene_timestamps == [(0, 10), (10, 20)]
        assert result.extracted_frames == ["frame1.jpg", "frame2.jpg"]
        assert result.transcription == "Test transcription"
        assert result.metadata == {"duration": 30}

    def test_to_dict_and_from_dict(self):
        """Test conversion to and from dictionary."""
        original_result = ProcessingResult(
            scene_timestamps=[(0, 10), (10, 20)],
            extracted_frames=["frame1.jpg", "frame2.jpg"],
            transcription="Test transcription",
            metadata={"duration": 30},
        )

        # Convert to dict
        result_dict = original_result.to_dict()

        # Create new result from dict
        new_result = ProcessingResult.from_dict(result_dict)

        # Check that the results are equivalent
        assert new_result.scene_timestamps == original_result.scene_timestamps
        assert new_result.extracted_frames == original_result.extracted_frames
        assert new_result.transcription == original_result.transcription
        assert new_result.metadata == original_result.metadata


class TestProcessingContext:
    """Test suite for ProcessingContext class."""

    def test_init(self):
        """Test initialization of ProcessingContext."""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProcessingContext(
                job_id="test-job-123",
                video_path="/path/to/video.mp4",
                temp_dir=temp_dir,
                output_dir="/path/to/output",
            )

            assert context.job_id == "test-job-123"
            assert context.video_path == "/path/to/video.mp4"
            assert context.temp_dir == temp_dir
            assert context.output_dir == "/path/to/output"
            assert context.artifacts == {}
            assert context.metadata == {}

    def test_add_artifact(self):
        """Test adding an artifact to the context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProcessingContext(
                job_id="test-job-123",
                video_path="/path/to/video.mp4",
                temp_dir=temp_dir,
            )

            context.add_artifact(
                "frames", ["/path/to/frame1.jpg", "/path/to/frame2.jpg"]
            )

            assert "frames" in context.artifacts
            assert context.artifacts["frames"] == [
                "/path/to/frame1.jpg",
                "/path/to/frame2.jpg",
            ]

    def test_add_metadata(self):
        """Test adding metadata to the context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProcessingContext(
                job_id="test-job-123",
                video_path="/path/to/video.mp4",
                temp_dir=temp_dir,
            )

            context.add_metadata("duration", 30)
            context.add_metadata("format", "mp4")

            assert context.metadata == {"duration": 30, "format": "mp4"}

    def test_get_temp_file_path(self):
        """Test getting a temporary file path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProcessingContext(
                job_id="test-job-123",
                video_path="/path/to/video.mp4",
                temp_dir=temp_dir,
            )

            path = context.get_temp_file_path("audio.wav")

            assert os.path.dirname(path) == temp_dir
            assert os.path.basename(path) == "audio.wav"

    def test_get_output_file_path(self):
        """Test getting an output file path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProcessingContext(
                job_id="test-job-123",
                video_path="/path/to/video.mp4",
                temp_dir=temp_dir,
                output_dir="/path/to/output",
            )

            path = context.get_output_file_path("transcription.json")

            assert os.path.dirname(path) == "/path/to/output"
            assert os.path.basename(path) == "transcription.json"

    def test_create_dirs(self):
        """Test creating directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, "output")

            context = ProcessingContext(
                job_id="test-job-123",
                video_path="/path/to/video.mp4",
                temp_dir=os.path.join(temp_dir, "temp"),
                output_dir=output_dir,
            )

            context.create_dirs()

            assert os.path.exists(context.temp_dir)
            assert os.path.exists(context.output_dir)

    def test_cleanup(self):
        """Test cleaning up temporary files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProcessingContext(
                job_id="test-job-123",
                video_path="/path/to/video.mp4",
                temp_dir=temp_dir,
            )

            # Create a test file
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")

            assert os.path.exists(test_file)

            # Clean up
            with patch("shutil.rmtree") as mock_rmtree:
                context.cleanup()
                mock_rmtree.assert_called_once_with(temp_dir, ignore_errors=True)


class TestVideoProcessor:
    """Test suite for VideoProcessor class."""

    def setup_method(self):
        """Set up test environment."""
        self.processor = VideoProcessor()
        self.test_video_path = "/path/to/test.mp4"

    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_validate_video_exists(self, mock_getsize, mock_exists):
        """Test validation for video existence."""
        # Video exists
        mock_exists.return_value = True
        mock_getsize.return_value = 1024 * 1024  # 1MB

        self.processor.validate_video(self.test_video_path)

        # Video doesn't exist
        mock_exists.return_value = False

        with pytest.raises(VideoProcessingError, match="Video file does not exist"):
            self.processor.validate_video(self.test_video_path)

    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_validate_video_size(self, mock_getsize, mock_exists):
        """Test validation for video size."""
        mock_exists.return_value = True

        # Valid size
        mock_getsize.return_value = 1024 * 1024  # 1MB

        self.processor.validate_video(self.test_video_path)

        # Too large
        mock_getsize.return_value = (
            3000 * 1024 * 1024
        )  # 3000MB (exceeds default 2000MB)

        with pytest.raises(
            VideoProcessingError, match="Video file exceeds maximum size"
        ):
            self.processor.validate_video(self.test_video_path)

    @patch("os.path.exists")
    @patch("os.path.getsize")
    @patch("video_understanding.core.processing.get_video_metadata")
    def test_validate_video_format(self, mock_get_metadata, mock_getsize, mock_exists):
        """Test validation for video format."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024 * 1024  # 1MB

        # Valid format
        mock_get_metadata.return_value = {"format": "mp4", "duration": 60}

        self.processor.validate_video(self.test_video_path)

        # Invalid format
        mock_get_metadata.return_value = {"format": "xyz", "duration": 60}

        with pytest.raises(VideoFormatError, match="Unsupported video format"):
            self.processor.validate_video(self.test_video_path)

    @patch("os.path.exists")
    @patch("os.path.getsize")
    @patch("video_understanding.core.processing.get_video_metadata")
    def test_validate_video_duration(
        self, mock_get_metadata, mock_getsize, mock_exists
    ):
        """Test validation for video duration."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024 * 1024  # 1MB

        # Valid duration
        mock_get_metadata.return_value = {"format": "mp4", "duration": 60}

        self.processor.validate_video(self.test_video_path)

        # Too long
        mock_get_metadata.return_value = {"format": "mp4", "duration": 7200}  # 2 hours

        with pytest.raises(
            VideoProcessingError, match="Video duration exceeds maximum"
        ):
            self.processor.validate_video(self.test_video_path)

    @patch("video_understanding.core.processing.uuid.uuid4")
    def test_create_job_id(self, mock_uuid4):
        """Test creation of job ID."""
        mock_uuid4.return_value = "test-uuid"

        job_id = self.processor._create_job_id()

        assert job_id == "test-uuid"

    @patch("video_understanding.core.processing.VideoProcessor.validate_video")
    @patch("video_understanding.core.processing.VideoProcessor._create_job_id")
    @patch("video_understanding.core.processing.tempfile.mkdtemp")
    def test_create_processing_context(
        self, mock_mkdtemp, mock_create_job_id, mock_validate
    ):
        """Test creation of processing context."""
        mock_create_job_id.return_value = "test-job-123"
        mock_mkdtemp.return_value = "/tmp/test_dir"

        context = self.processor._create_processing_context(self.test_video_path)

        assert context.job_id == "test-job-123"
        assert context.video_path == self.test_video_path
        assert context.temp_dir == "/tmp/test_dir"
        assert context.output_dir == self.processor.config.processed_dir

    @patch("video_understanding.core.processing.detect_scenes")
    def test_extract_scenes(self, mock_detect_scenes):
        """Test scene extraction."""
        mock_detect_scenes.return_value = [(0, 10), (10, 20)]

        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProcessingContext(
                job_id="test-job-123",
                video_path=self.test_video_path,
                temp_dir=temp_dir,
            )

            self.processor._extract_scenes(context)

            assert "scene_timestamps" in context.artifacts
            assert context.artifacts["scene_timestamps"] == [(0, 10), (10, 20)]

    @patch("video_understanding.core.processing.extract_audio")
    def test_extract_audio(self, mock_extract_audio):
        """Test audio extraction."""
        mock_extract_audio.return_value = "/tmp/test_dir/audio.wav"

        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProcessingContext(
                job_id="test-job-123",
                video_path=self.test_video_path,
                temp_dir=temp_dir,
            )

            self.processor._extract_audio(context)

            assert "audio_path" in context.artifacts
            assert context.artifacts["audio_path"] == "/tmp/test_dir/audio.wav"

    @patch("video_understanding.core.processing.transcribe_audio")
    def test_transcribe_audio(self, mock_transcribe):
        """Test audio transcription."""
        mock_transcribe.return_value = {
            "text": "This is a test transcription.",
            "segments": [{"start": 0, "end": 5, "text": "This is a test"}],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProcessingContext(
                job_id="test-job-123",
                video_path=self.test_video_path,
                temp_dir=temp_dir,
            )

            # Add audio path artifact
            context.add_artifact("audio_path", "/tmp/test_dir/audio.wav")

            self.processor._transcribe_audio(context)

            assert "transcription" in context.artifacts
            assert (
                context.artifacts["transcription"]["text"]
                == "This is a test transcription."
            )
            assert len(context.artifacts["transcription"]["segments"]) == 1

    @patch("video_understanding.core.processing.extract_frames")
    def test_extract_frames(self, mock_extract_frames):
        """Test frame extraction."""
        mock_extract_frames.return_value = [
            "/tmp/test_dir/frame1.jpg",
            "/tmp/test_dir/frame2.jpg",
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProcessingContext(
                job_id="test-job-123",
                video_path=self.test_video_path,
                temp_dir=temp_dir,
            )

            self.processor._extract_frames(context)

            assert "extracted_frames" in context.artifacts
            assert len(context.artifacts["extracted_frames"]) == 2

    @patch("video_understanding.core.processing.extract_text_from_frames")
    def test_extract_text_from_frames(self, mock_extract_text):
        """Test text extraction from frames."""
        mock_extract_text.return_value = {
            "/tmp/test_dir/frame1.jpg": "Text from frame 1",
            "/tmp/test_dir/frame2.jpg": "Text from frame 2",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProcessingContext(
                job_id="test-job-123",
                video_path=self.test_video_path,
                temp_dir=temp_dir,
            )

            # Add extracted frames artifact
            context.add_artifact(
                "extracted_frames",
                ["/tmp/test_dir/frame1.jpg", "/tmp/test_dir/frame2.jpg"],
            )

            self.processor._extract_text_from_frames(context)

            assert "extracted_text" in context.artifacts
            assert len(context.artifacts["extracted_text"]) == 2
            assert (
                context.artifacts["extracted_text"]["/tmp/test_dir/frame1.jpg"]
                == "Text from frame 1"
            )

    def test_create_processing_result(self):
        """Test creation of processing result."""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = ProcessingContext(
                job_id="test-job-123",
                video_path=self.test_video_path,
                temp_dir=temp_dir,
            )

            # Add artifacts
            context.add_artifact("scene_timestamps", [(0, 10), (10, 20)])
            context.add_artifact(
                "extracted_frames",
                ["/tmp/test_dir/frame1.jpg", "/tmp/test_dir/frame2.jpg"],
            )
            context.add_artifact(
                "transcription",
                {
                    "text": "This is a test transcription.",
                    "segments": [{"start": 0, "end": 5, "text": "This is a test"}],
                },
            )

            # Add metadata
            context.add_metadata("duration", 30)
            context.add_metadata("format", "mp4")

            result = self.processor._create_processing_result(context)

            assert result.scene_timestamps == [(0, 10), (10, 20)]
            assert result.extracted_frames == [
                "/tmp/test_dir/frame1.jpg",
                "/tmp/test_dir/frame2.jpg",
            ]
            assert result.transcription == {
                "text": "This is a test transcription.",
                "segments": [{"start": 0, "end": 5, "text": "This is a test"}],
            }
            assert result.metadata == {"duration": 30, "format": "mp4"}

    @patch("video_understanding.core.processing.VideoProcessor._create_job_id")
    @patch("video_understanding.core.processing.VideoProcessor.validate_video")
    @patch(
        "video_understanding.core.processing.VideoProcessor._create_processing_context"
    )
    @patch("video_understanding.core.processing.VideoProcessor._extract_scenes")
    @patch("video_understanding.core.processing.VideoProcessor._extract_audio")
    @patch("video_understanding.core.processing.VideoProcessor._transcribe_audio")
    @patch("video_understanding.core.processing.VideoProcessor._extract_frames")
    @patch(
        "video_understanding.core.processing.VideoProcessor._extract_text_from_frames"
    )
    @patch(
        "video_understanding.core.processing.VideoProcessor._create_processing_result"
    )
    def test_process_video_success(
        self,
        mock_create_result,
        mock_extract_text,
        mock_extract_frames,
        mock_transcribe,
        mock_extract_audio,
        mock_extract_scenes,
        mock_create_context,
        mock_validate,
        mock_create_job_id,
    ):
        """Test successful video processing."""
        # Set up mocks
        mock_create_job_id.return_value = "test-job-123"
        mock_validate.return_value = None

        context = ProcessingContext(
            job_id="test-job-123",
            video_path=self.test_video_path,
            temp_dir="/tmp/test_dir",
        )
        mock_create_context.return_value = context

        result = ProcessingResult(
            scene_timestamps=[(0, 10), (10, 20)],
            extracted_frames=["/tmp/test_dir/frame1.jpg", "/tmp/test_dir/frame2.jpg"],
            transcription="Test transcription",
            metadata={"duration": 30},
        )
        mock_create_result.return_value = result

        # Call the method
        job = self.processor.process_video(self.test_video_path)

        # Verify the job was created correctly
        assert job.job_id == "test-job-123"
        assert job.video_path == self.test_video_path
        assert job.status == JobStatus.COMPLETED
        assert job.result == result

        # Verify that all the processing steps were called
        mock_validate.assert_called_once_with(self.test_video_path)
        mock_create_context.assert_called_once_with(self.test_video_path)
        mock_extract_scenes.assert_called_once_with(context)
        mock_extract_audio.assert_called_once_with(context)
        mock_transcribe.assert_called_once_with(context)
        mock_extract_frames.assert_called_once_with(context)
        mock_extract_text.assert_called_once_with(context)
        mock_create_result.assert_called_once_with(context)

    @patch("video_understanding.core.processing.VideoProcessor._create_job_id")
    @patch("video_understanding.core.processing.VideoProcessor.validate_video")
    @patch(
        "video_understanding.core.processing.VideoProcessor._create_processing_context"
    )
    def test_process_video_error(
        self, mock_create_context, mock_validate, mock_create_job_id
    ):
        """Test video processing with error."""
        # Set up mocks
        mock_create_job_id.return_value = "test-job-123"
        mock_validate.side_effect = VideoFormatError("Unsupported video format: xyz")

        # Call the method
        job = self.processor.process_video(self.test_video_path)

        # Verify the job was created with error
        assert job.job_id == "test-job-123"
        assert job.video_path == self.test_video_path
        assert job.status == JobStatus.FAILED
        assert job.error == "Unsupported video format: xyz"
        assert job.result is None


class TestJobManager:
    """Test suite for JobManager class."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.job_store_path = os.path.join(self.temp_dir.name, "jobs.json")
        self.manager = JobManager(job_store_path=self.job_store_path)

    def teardown_method(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_add_job(self):
        """Test adding a job to the manager."""
        job = ProcessingJob(
            job_id="test-job-123", video_path="/path/to/video.mp4", user_id="user123"
        )

        self.manager.add_job(job)

        assert len(self.manager.jobs) == 1
        assert self.manager.jobs[0].job_id == "test-job-123"

    def test_get_job(self):
        """Test getting a job by ID."""
        job1 = ProcessingJob(job_id="test-job-123", video_path="/path/to/video1.mp4")

        job2 = ProcessingJob(job_id="test-job-456", video_path="/path/to/video2.mp4")

        self.manager.add_job(job1)
        self.manager.add_job(job2)

        # Get existing job
        retrieved_job = self.manager.get_job("test-job-123")
        assert retrieved_job.job_id == "test-job-123"
        assert retrieved_job.video_path == "/path/to/video1.mp4"

        # Get non-existent job
        assert self.manager.get_job("non-existent") is None

    def test_get_jobs_by_status(self):
        """Test getting jobs by status."""
        job1 = ProcessingJob(job_id="test-job-123", video_path="/path/to/video1.mp4")
        job1.update_status(JobStatus.PROCESSING)

        job2 = ProcessingJob(job_id="test-job-456", video_path="/path/to/video2.mp4")
        job2.update_status(JobStatus.COMPLETED)

        job3 = ProcessingJob(job_id="test-job-789", video_path="/path/to/video3.mp4")
        job3.update_status(JobStatus.FAILED)

        self.manager.add_job(job1)
        self.manager.add_job(job2)
        self.manager.add_job(job3)

        processing_jobs = self.manager.get_jobs_by_status(JobStatus.PROCESSING)
        completed_jobs = self.manager.get_jobs_by_status(JobStatus.COMPLETED)
        failed_jobs = self.manager.get_jobs_by_status(JobStatus.FAILED)

        assert len(processing_jobs) == 1
        assert processing_jobs[0].job_id == "test-job-123"

        assert len(completed_jobs) == 1
        assert completed_jobs[0].job_id == "test-job-456"

        assert len(failed_jobs) == 1
        assert failed_jobs[0].job_id == "test-job-789"

    def test_get_jobs_by_user(self):
        """Test getting jobs by user ID."""
        job1 = ProcessingJob(
            job_id="test-job-123", video_path="/path/to/video1.mp4", user_id="user123"
        )

        job2 = ProcessingJob(
            job_id="test-job-456", video_path="/path/to/video2.mp4", user_id="user456"
        )

        job3 = ProcessingJob(
            job_id="test-job-789", video_path="/path/to/video3.mp4", user_id="user123"
        )

        self.manager.add_job(job1)
        self.manager.add_job(job2)
        self.manager.add_job(job3)

        user123_jobs = self.manager.get_jobs_by_user("user123")
        user456_jobs = self.manager.get_jobs_by_user("user456")

        assert len(user123_jobs) == 2
        assert user123_jobs[0].job_id == "test-job-123"
        assert user123_jobs[1].job_id == "test-job-789"

        assert len(user456_jobs) == 1
        assert user456_jobs[0].job_id == "test-job-456"

    @patch("json.dump")
    def test_save_jobs(self, mock_dump):
        """Test saving jobs to file."""
        job1 = ProcessingJob(job_id="test-job-123", video_path="/path/to/video1.mp4")

        job2 = ProcessingJob(job_id="test-job-456", video_path="/path/to/video2.mp4")

        self.manager.add_job(job1)
        self.manager.add_job(job2)

        self.manager.save_jobs()

        # Verify json.dump was called with the correct arguments
        mock_dump.assert_called_once()
        args, kwargs = mock_dump.call_args
        job_list = args[0]

        assert len(job_list) == 2
        assert job_list[0]["job_id"] == "test-job-123"
        assert job_list[1]["job_id"] == "test-job-456"

    @patch("json.load")
    @patch("os.path.exists")
    def test_load_jobs(self, mock_exists, mock_load):
        """Test loading jobs from file."""
        # Set up mocks
        mock_exists.return_value = True
        mock_load.return_value = [
            {
                "job_id": "test-job-123",
                "video_path": "/path/to/video1.mp4",
                "user_id": "user123",
                "options": {},
                "status": "COMPLETED",
                "created_at": "2023-01-01T12:00:00.000000",
                "updated_at": "2023-01-01T12:05:00.000000",
                "result": {
                    "scene_timestamps": [[0, 10], [10, 20]],
                    "extracted_frames": ["frame1.jpg", "frame2.jpg"],
                    "transcription": "Test transcription",
                    "metadata": {"duration": 30},
                },
                "error": None,
            },
            {
                "job_id": "test-job-456",
                "video_path": "/path/to/video2.mp4",
                "user_id": "user456",
                "options": {},
                "status": "FAILED",
                "created_at": "2023-01-01T13:00:00.000000",
                "updated_at": "2023-01-01T13:05:00.000000",
                "result": None,
                "error": "Test error",
            },
        ]

        # Call the method
        self.manager.load_jobs()

        # Verify the jobs were loaded correctly
        assert len(self.manager.jobs) == 2

        job1 = self.manager.get_job("test-job-123")
        assert job1.job_id == "test-job-123"
        assert job1.user_id == "user123"
        assert job1.status == JobStatus.COMPLETED
        assert job1.result.scene_timestamps == [(0, 10), (10, 20)]

        job2 = self.manager.get_job("test-job-456")
        assert job2.job_id == "test-job-456"
        assert job2.user_id == "user456"
        assert job2.status == JobStatus.FAILED
        assert job2.error == "Test error"

    @patch("os.path.exists")
    def test_load_jobs_file_not_exists(self, mock_exists):
        """Test loading jobs when file doesn't exist."""
        # Set up mock
        mock_exists.return_value = False

        # Call the method
        self.manager.load_jobs()

        # Verify no jobs were loaded
        assert len(self.manager.jobs) == 0

    def test_update_job(self):
        """Test updating a job."""
        job = ProcessingJob(job_id="test-job-123", video_path="/path/to/video.mp4")

        self.manager.add_job(job)

        # Verify initial state
        assert self.manager.get_job("test-job-123").status == JobStatus.PENDING

        # Update job
        job.update_status(JobStatus.COMPLETED)
        self.manager.update_job(job)

        # Verify updated state
        assert self.manager.get_job("test-job-123").status == JobStatus.COMPLETED

    def test_remove_job(self):
        """Test removing a job."""
        job1 = ProcessingJob(job_id="test-job-123", video_path="/path/to/video1.mp4")

        job2 = ProcessingJob(job_id="test-job-456", video_path="/path/to/video2.mp4")

        self.manager.add_job(job1)
        self.manager.add_job(job2)

        # Verify initial state
        assert len(self.manager.jobs) == 2

        # Remove job
        self.manager.remove_job("test-job-123")

        # Verify updated state
        assert len(self.manager.jobs) == 1
        assert self.manager.get_job("test-job-123") is None
        assert self.manager.get_job("test-job-456") is not None

    def test_clear_jobs(self):
        """Test clearing all jobs."""
        job1 = ProcessingJob(job_id="test-job-123", video_path="/path/to/video1.mp4")

        job2 = ProcessingJob(job_id="test-job-456", video_path="/path/to/video2.mp4")

        self.manager.add_job(job1)
        self.manager.add_job(job2)

        # Verify initial state
        assert len(self.manager.jobs) == 2

        # Clear jobs
        self.manager.clear_jobs()

        # Verify updated state
        assert len(self.manager.jobs) == 0
