import pytest
from unittest.mock import Mock, patch
from src.video_understanding.core.processing.video import VideoProcessor
from src.video_understanding.core.exceptions import (
    VideoProcessingError,
    VideoFormatError,
    ResourceExceededError,
    ConcurrencyLimitError,
    ValidationError
)

class TestVideoProcessor:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.processor = VideoProcessor()
        self.test_file = "tests/fixtures/sample_video.mp4"

    def test_process_frame(self, sample_frame):
        """Test processing of a single video frame."""
        frames = [sample_frame]
        result = self.processor.detect_text(frames)
        assert isinstance(result, list)
        assert len(result) == 1
        assert "text" in result[0]
        assert "confidence" in result[0]
        assert "position" in result[0]

    def test_valid_video_processing(self):
        """Test processing of a valid video file."""
        result = self.processor.process_video(self.test_file)
        assert "frames" in result
        assert "text_results" in result
        assert "audio_results" in result

    def test_invalid_video_format(self):
        """Test handling of invalid video format."""
        with pytest.raises(VideoFormatError):
            self.processor.validate_video("invalid.txt")

    def test_memory_limit_handling(self):
        """Test handling of memory limit exceeded scenario."""
        with patch('src.video_understanding.core.processing.video.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 3 * 1024 * 1024 * 1024  # 3GB, above limit
            with pytest.raises(ValidationError):
                self.processor.validate_video(self.test_file)

    def test_concurrent_processing_limit(self):
        """Test handling of concurrent processing limit."""
        mock_metrics = Mock()
        mock_metrics.get_active_count.return_value = 4  # Above limit
        processor = VideoProcessor(metrics_tracker=mock_metrics)
        with pytest.raises(ConcurrencyLimitError):
            processor.process_video(self.test_file)

    def test_processing_with_custom_settings(self):
        """Test video processing with custom settings."""
        custom_settings = {
            "frame_interval": 2,
            "min_confidence": 0.8,
            "enable_audio": True
        }
        result = self.processor.process_video(self.test_file, options=custom_settings)
        assert "frames" in result
        assert "text_results" in result
        assert "audio_results" in result
