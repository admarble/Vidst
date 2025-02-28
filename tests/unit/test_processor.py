import os
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch
from src.video_understanding.core.processing.video import VideoProcessor
from src.video_understanding.core.exceptions import (
    VideoProcessingError,
    VideoFormatError,
    ResourceExceededError,
    ConcurrencyLimitError,
    ValidationError,
)


class TestVideoProcessor:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.processor = VideoProcessor()

        # Create the test file directory structure if it doesn't exist
        test_file_dir = Path("tests/fixtures/video_samples/valid")
        test_file_dir.mkdir(parents=True, exist_ok=True)

        # Create a sample video file for testing if it doesn't exist
        self.test_file = test_file_dir / "sample_video.mp4"
        if not self.test_file.exists():
            # Create a minimal valid MP4 file for testing
            with open(self.test_file, "wb") as f:
                # Write minimal MP4 header (not a real MP4, just enough for testing)
                f.write(b"\x00\x00\x00\x20\x66\x74\x79\x70\x6d\x70\x34\x32")
                f.write(b"\x00\x00\x00\x00\x6d\x70\x34\x32\x69\x73\x6f\x6d")
                f.write(b"\x00\x00\x00\x08\x6d\x6f\x6f\x76")

        # Create invalid directory if it doesn't exist
        invalid_dir = Path("tests/fixtures/video_samples/invalid")
        invalid_dir.mkdir(parents=True, exist_ok=True)

        # Create an invalid test file
        invalid_file = invalid_dir / "test.txt"
        if not invalid_file.exists():
            with open(invalid_file, "w") as f:
                f.write("This is not a video file.")

    def teardown_method(self):
        """Clean up after tests if needed."""
        pass

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
        assert isinstance(result, dict)
        assert "frames" in result
        assert "text_results" in result
        assert "audio_results" in result

    def test_invalid_video_format(self):
        """Test handling of invalid video format."""
        with pytest.raises(VideoFormatError):
            self.processor.validate_video(
                "tests/fixtures/video_samples/invalid/test.txt"
            )

    def test_memory_limit_handling(self):
        """Test handling of memory limits."""
        with patch("psutil.virtual_memory") as mock_memory:
            mock_memory.return_value.available = 100  # Very low memory
            with pytest.raises(ResourceExceededError):
                self.processor.check_resources()

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
            "enable_audio": True,
        }
        result = self.processor.process_video(self.test_file, options=custom_settings)
        assert isinstance(result, dict)
