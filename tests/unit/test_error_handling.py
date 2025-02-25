"""Unit tests for error handling and edge cases."""

import queue
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import pytest
from pytest import MonkeyPatch

from video_understanding.ai.pipeline import ProcessingConfig, VideoPipeline
from video_understanding.core.config import VideoConfig
from video_understanding.core.exceptions import (
    ConfigurationError,
    FileValidationError,
    ModelError,
    ProcessingError,
    StorageError,
)
from video_understanding.storage.vector import VectorStorage
from video_understanding.video.upload import VideoUploader


@pytest.fixture
def mock_env_vars(monkeypatch: MonkeyPatch) -> dict[str, str]:
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


def test_processing_errors(mock_env_vars: dict[str, str]) -> None:
    """Test video processing error scenarios."""
    config = ProcessingConfig()
    pipeline = VideoPipeline(config)

    # Test corrupted video
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tf:
        tf.write(b"corrupted data")
        tf.flush()
        with pytest.raises(ProcessingError):
            pipeline.process({"video_path": tf.name, "start_time": 0, "end_time": 10})


def test_model_errors(mock_env_vars: dict[str, str]) -> None:
    """Test AI model error scenarios."""
    from video_understanding.ai.models.gpt4v import GPT4VisionModel

    model = GPT4VisionModel(api_key=mock_env_vars["OPENAI_API_KEY"])

    # Test invalid input
    with pytest.raises(ModelError):
        model.validate({})

    # Test invalid file path
    with pytest.raises(ModelError):
        model.validate({"image_path": "nonexistent.jpg"})


def test_storage_errors() -> None:
    """Test storage-related error scenarios."""
    storage = VectorStorage(
        dimension=768,
        index_path=Path("test_index.faiss"),
        metadata_path=Path("test_metadata.json"),
    )

    # Test invalid input
    with pytest.raises(StorageError):
        storage.add_embedding(None, {"type": "test"})  # type: ignore

    # Test invalid search query
    with pytest.raises(StorageError):
        storage.search_similar(None, k=1)  # type: ignore


def test_configuration_errors() -> None:
    """Test configuration error scenarios."""
    # Test invalid config values
    config = VideoConfig()
    config.max_file_size = -1
    with pytest.raises(ConfigurationError):
        config.validate()

    # Test empty supported formats
    config = VideoConfig()
    config.supported_formats = set()
    with pytest.raises(ConfigurationError):
        config.validate()

    # Test invalid scene length
    config = VideoConfig()
    config.min_scene_length = 0
    with pytest.raises(ConfigurationError):
        config.validate()

    # Test invalid max scenes
    config = VideoConfig()
    config.max_scenes = -1
    with pytest.raises(ConfigurationError):
        config.validate()


def test_edge_cases(mock_env_vars: dict[str, str]) -> None:
    """Test various edge cases."""
    config = ProcessingConfig()
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


def test_concurrent_access() -> None:
    """Test concurrent access scenarios."""
    config = ProcessingConfig()
    pipeline = VideoPipeline(config)
    errors: queue.Queue[Exception] = queue.Queue()

    # Create a test video that all threads will use
    with create_test_video(duration=1.0) as test_video_path:

        def process_video() -> None:
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


def test_resource_cleanup() -> None:
    """Test resource cleanup in error scenarios."""
    config = ProcessingConfig()
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

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def __enter__(self) -> str:
        return str(self.path)

    def __exit__(
        self,
        exc_type: type | None,
        exc_val: Exception | None,
        exc_tb: Any | None,
    ) -> None:
        try:
            self.path.unlink()
        except Exception:
            pass


def create_test_video(duration: float) -> VideoContextManager:
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
        result = subprocess.run(cmd, check=True, capture_output=True)

        # Verify the file was created
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError("Failed to create test video file")

        return VideoContextManager(path)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create video: {e.stderr.decode()}")


def create_silent_video() -> VideoContextManager:
    """Create a test video with no audio."""
    path = Path(tempfile.mktemp(suffix=".mp4"))
    fps = 30
    duration = 1  # 1 second
    size = (640, 480)

    try:
        # Try different codecs in order of preference
        codecs = ["mp4v", "avc1", "h264"]
        out = None

        for codec in codecs:
            try:
                fourcc = cv2.VideoWriter_fourcc(*codec)  # type: ignore
                out = cv2.VideoWriter(str(path), fourcc, fps, size)
                if out is not None and out.isOpened():
                    break
            except Exception:
                if out is not None:
                    out.release()
                continue

        if out is None or not out.isOpened():
            raise RuntimeError("Failed to initialize video writer with any codec")

        # Generate frames (white background)
        for _ in range(int(fps * duration)):
            frame = np.ones((size[1], size[0], 3), dtype=np.uint8) * 255
            out.write(frame)

        out.release()
        return VideoContextManager(path)
    except Exception as e:
        if out is not None:
            out.release()
        if path.exists():
            path.unlink()
        raise RuntimeError(f"Failed to create silent video: {e!s}")


def create_black_video() -> VideoContextManager:
    """Create a test video with no visual content (black frames)."""
    path = Path(tempfile.mktemp(suffix=".mp4"))
    fps = 30
    duration = 1  # 1 second
    size = (640, 480)

    try:
        # Try different codecs in order of preference
        codecs = ["mp4v", "avc1", "h264"]
        out = None

        for codec in codecs:
            try:
                fourcc = cv2.VideoWriter_fourcc(*codec)  # type: ignore
                out = cv2.VideoWriter(str(path), fourcc, fps, size)
                if out is not None and out.isOpened():
                    break
            except Exception:
                if out is not None:
                    out.release()
                continue

        if out is None or not out.isOpened():
            raise RuntimeError("Failed to initialize video writer with any codec")

        # Generate frames (black background)
        for _ in range(int(fps * duration)):
            frame = np.zeros((size[1], size[0], 3), dtype=np.uint8)
            out.write(frame)

        out.release()
        return VideoContextManager(path)
    except Exception as e:
        if out is not None:
            out.release()
        if path.exists():
            path.unlink()
        raise RuntimeError(f"Failed to create black video: {e!s}")


def get_resource_usage() -> dict[str, float]:
    """Get current resource usage statistics."""
    try:
        import psutil

        process = psutil.Process()
        return {
            "memory": process.memory_info().rss,
            "cpu_percent": process.cpu_percent(),
            "threads": len(process.threads()),
            "open_files": len(process.open_files()),
        }
    except ImportError:
        # Return dummy values if psutil is not available
        return {
            "memory": 0.0,
            "cpu_percent": 0.0,
            "threads": 0.0,
            "open_files": 0.0,
        }


def assert_resources_cleaned_up(
    initial: dict[str, float], final: dict[str, float]
) -> None:
    """Assert that resources were properly cleaned up."""
    # Allow for some variance in resource usage
    memory_threshold = 1.1  # 10% increase allowed
    cpu_threshold = 5.0  # 5% difference allowed

    assert (
        final["memory"] <= initial["memory"] * memory_threshold
    ), "Memory not properly cleaned up"
    assert (
        abs(final["cpu_percent"] - initial["cpu_percent"]) <= cpu_threshold
    ), "CPU usage not normalized"
    assert (
        final["threads"] <= initial["threads"]
    ), "Thread count not properly cleaned up"
    assert (
        final["open_files"] <= initial["open_files"]
    ), "Open files not properly cleaned up"
