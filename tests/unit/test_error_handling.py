"""Unit tests for error handling and edge cases."""

import os
import tempfile
from pathlib import Path

import cv2
import numpy as np
import pytest

from src.ai.pipeline import VideoPipeline
from src.core.config import VideoConfig
from src.core.exceptions import (
    ConfigurationError,
    FileValidationError,
    ModelError,
    ProcessingError,
    StorageError,
)
from src.storage.vector import VectorStorage
from src.video.upload import VideoUploader


def test_file_validation_errors():
    """Test various file validation error scenarios."""
    config = VideoConfig()
    uploader = VideoUploader(config)

    # Test non-existent file
    with pytest.raises(FileValidationError, match="File does not exist"):
        uploader.validate_file("nonexistent.mp4")

    # Test empty file
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tf:
        with pytest.raises(FileValidationError, match="File is empty"):
            uploader.validate_file(tf.name)

    # Test invalid extension
    with tempfile.NamedTemporaryFile(suffix=".invalid") as tf:
        with pytest.raises(FileValidationError, match="Unsupported format"):
            uploader.validate_file(tf.name)


def test_processing_errors(mock_env_vars):
    """Test video processing error scenarios."""
    config = VideoConfig()
    pipeline = VideoPipeline(config)

    # Test corrupted video
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tf:
        tf.write(b"corrupted data")
        tf.flush()
        with pytest.raises(ProcessingError):
            pipeline.process({"video_path": tf.name, "start_time": 0, "end_time": 10})


def test_model_errors(mock_env_vars):
    """Test AI model error scenarios."""
    from src.ai.models.gpt4v import GPT4VisionModel

    model = GPT4VisionModel(api_key=mock_env_vars["OPENAI_API_KEY"])

    # Test invalid input
    with pytest.raises(ModelError):
        model.validate({})

    # Test invalid file path
    with pytest.raises(ModelError):
        model.validate({"image_path": "nonexistent.jpg"})


def test_storage_errors():
    """Test storage-related error scenarios."""
    storage = VectorStorage()

    # Test invalid input
    with pytest.raises(StorageError):
        storage.store(key="test", vector=None)

    # Test invalid search query
    with pytest.raises(StorageError):
        storage.search(query_vector=None)


def test_configuration_errors():
    """Test configuration error scenarios."""
    # Test invalid config values
    config = VideoConfig()
    config.MAX_FILE_SIZE = -1
    with pytest.raises(ConfigurationError):
        config.validate()


def test_edge_cases(mock_env_vars):
    """Test various edge cases."""
    config = VideoConfig()
    pipeline = VideoPipeline(config)

    # Test extremely short video
    with create_test_video(duration=0.1) as video_path:
        result = pipeline.process(
            {"video_path": video_path, "start_time": 0, "end_time": 0.1}
        )
        assert isinstance(result, dict)
        assert "scene_description" in result

    # Test video with no audio
    with create_silent_video() as video_path:
        result = pipeline.process(
            {"video_path": video_path, "start_time": 0, "end_time": 1}
        )
        assert isinstance(result, dict)
        assert "scene_description" in result

    # Test video with no visual content
    with create_black_video() as video_path:
        result = pipeline.process(
            {"video_path": video_path, "start_time": 0, "end_time": 1}
        )
        assert isinstance(result, dict)
        assert "scene_description" in result


def test_concurrent_access():
    """Test concurrent access scenarios."""
    import queue
    import threading

    config = VideoConfig()
    pipeline = VideoPipeline(config)
    errors = queue.Queue()

    # Create a test video that all threads will use
    with create_test_video(duration=1.0) as test_video_path:

        def process_video():
            try:
                pipeline.process(
                    {"video_path": test_video_path, "start_time": 0, "end_time": 1}
                )
            except Exception as e:
                errors.put(e)

        # Start multiple threads
        threads = []
        for _ in range(5):
            t = threading.Thread(target=process_video)
            t.start()
            threads.append(t)

        # Wait for completion
        for t in threads:
            t.join()

        # Check for errors
        assert errors.empty(), f"Concurrent processing errors: {list(errors.queue)}"


def test_resource_cleanup():
    """Test resource cleanup in error scenarios."""
    config = VideoConfig()
    pipeline = VideoPipeline(config)

    initial_resources = get_resource_usage()

    try:
        pipeline.process(
            {"video_path": "nonexistent.mp4", "start_time": 0, "end_time": 10}
        )
    except Exception:
        pass

    final_resources = get_resource_usage()
    assert_resources_cleaned_up(initial_resources, final_resources)


# Helper functions for tests
class VideoContextManager:
    """Context manager for test video files."""

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        return str(self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            Path(self.path).unlink()
        except Exception:
            pass


def create_test_video(duration):
    """Create a test video file with specified duration."""
    path = Path(tempfile.mktemp(suffix=".mp4"))

    # Create a test video using ffmpeg
    fps = 30
    size = "640x480"

    # Generate a test pattern video
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output file if it exists
        "-f",
        "lavfi",  # Use lavfi input
        "-i",
        f"testsrc=duration={duration}:size={size}:rate={fps}",  # Test input pattern
        "-c:v",
        "libx264",  # Use H.264 codec
        "-pix_fmt",
        "yuv420p",  # Pixel format for compatibility
        "-movflags",
        "+faststart",  # Enable fast start for web playback
        str(path),
    ]

    try:
        import subprocess

        subprocess.run(cmd, check=True, capture_output=True)

        # Verify the file was created
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError("Failed to create test video file")

        return VideoContextManager(path)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create video: {e.stderr.decode()}")


def create_silent_video():
    """Create a video without audio."""
    path = Path(tempfile.mktemp(suffix=".mp4"))

    # Create a silent video using ffmpeg
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "testsrc=duration=1:size=640x480:rate=30",
        "-an",  # No audio
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(path),
    ]

    try:
        import subprocess

        subprocess.run(cmd, check=True, capture_output=True)
        return VideoContextManager(path)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create video: {e.stderr.decode()}")


def create_black_video():
    """Create a video with no visual content."""
    path = Path(tempfile.mktemp(suffix=".mp4"))

    # Create a black video using ffmpeg
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=black:s=640x480:d=1:r=30",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(path),
    ]

    try:
        import subprocess

        subprocess.run(cmd, check=True, capture_output=True)
        return VideoContextManager(path)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create video: {e.stderr.decode()}")


def get_resource_usage():
    """Get current resource usage."""
    import psutil

    process = psutil.Process()
    return {
        "memory": process.memory_info().rss,
        "threads": process.num_threads(),
        "files": process.open_files(),
    }


def assert_resources_cleaned_up(initial, final):
    """Assert resources were properly cleaned up."""
    # Allow for small variations in memory usage
    memory_threshold = 1024 * 1024  # 1MB
    assert abs(final["memory"] - initial["memory"]) < memory_threshold
    assert final["threads"] <= initial["threads"]
    assert len(final["files"]) <= len(initial["files"])
