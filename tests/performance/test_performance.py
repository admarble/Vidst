"""Performance tests for the video processing system."""

import tempfile
import time
from pathlib import Path
from typing import Dict, List

import psutil
import pytest

from src.ai.pipeline import VideoPipeline
from src.core.config import VideoConfig
from src.core.exceptions import ProcessingError
from src.storage.vector import VectorStorage
from src.video.upload import VideoUploader


class PerformanceMetrics:
    def __init__(self):
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss
        self.measurements: List[Dict] = []

    def measure(self, label: str):
        current_time = time.time()
        current_memory = psutil.Process().memory_info().rss

        self.measurements.append(
            {
                "label": label,
                "time_elapsed": current_time - self.start_time,
                "memory_used": current_memory - self.start_memory,
                "cpu_percent": psutil.cpu_percent(),
            }
        )

    def get_report(self) -> Dict:
        return {
            "total_time": time.time() - self.start_time,
            "peak_memory": max(m["memory_used"] for m in self.measurements),
            "measurements": self.measurements,
        }


@pytest.fixture
def performance_metrics():
    return PerformanceMetrics()


@pytest.fixture
def sample_videos():
    """Create sample videos of different sizes and durations."""
    videos = {}

    # Small video (10MB, 30s)
    videos["small"] = create_test_video(size_mb=10, duration=30)

    # Medium video (100MB, 5min)
    videos["medium"] = create_test_video(size_mb=100, duration=300)

    # Large video (500MB, 30min)
    videos["large"] = create_test_video(size_mb=500, duration=1800)

    yield videos

    # Cleanup
    for video in videos.values():
        Path(video).unlink()


def test_upload_performance(performance_metrics, sample_videos):
    """Test upload performance for different video sizes."""
    config = VideoConfig()
    uploader = VideoUploader(config)

    for size, video_path in sample_videos.items():
        performance_metrics.measure(f"start_upload_{size}")

        result = uploader.upload(video_path)

        performance_metrics.measure(f"end_upload_{size}")

        # Verify upload speed meets requirements
        upload_time = get_measurement_duration(performance_metrics, f"upload_{size}")
        file_size = Path(video_path).stat().st_size
        upload_speed = file_size / upload_time

        assert upload_speed >= 10 * 1024 * 1024  # Minimum 10MB/s


def test_processing_pipeline_performance(performance_metrics, sample_videos):
    """Test full pipeline processing performance."""
    config = VideoConfig()
    pipeline = VideoPipeline(config)

    for size, video_path in sample_videos.items():
        performance_metrics.measure(f"start_process_{size}")

        result = pipeline.process(video_path)

        performance_metrics.measure(f"end_process_{size}")

        # Verify processing time is within limits
        process_time = get_measurement_duration(performance_metrics, f"process_{size}")
        video_duration = get_video_duration(video_path)

        assert process_time <= video_duration * 2  # Max 2x realtime


def test_memory_usage(performance_metrics):
    """Test memory usage during concurrent processing."""
    config = VideoConfig()
    pipeline = VideoPipeline(config)

    performance_metrics.measure("start_memory_test")

    # Process multiple videos concurrently
    videos = [create_test_video(size_mb=100, duration=60) for _ in range(3)]

    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(pipeline.process, video) for video in videos]
        concurrent.futures.wait(futures)

    performance_metrics.measure("end_memory_test")

    # Verify memory usage
    peak_memory = performance_metrics.get_report()["peak_memory"]
    assert peak_memory <= 4 * 1024 * 1024 * 1024  # Max 4GB


def test_vector_search_performance(performance_metrics):
    """Test vector search performance with large datasets."""
    storage = VectorStorage()

    # Generate test vectors
    import numpy as np

    vectors = np.random.rand(10000, 512)  # 10K vectors

    performance_metrics.measure("start_index")

    # Index vectors
    for vector in vectors:
        storage.store_vector(vector)

    performance_metrics.measure("end_index")

    # Test search performance
    query = np.random.rand(512)

    performance_metrics.measure("start_search")
    results = storage.search(query, limit=10)
    performance_metrics.measure("end_search")

    # Verify search speed
    search_time = get_measurement_duration(performance_metrics, "search")
    assert search_time < 0.1  # Max 100ms per search


def test_api_rate_limits(performance_metrics):
    """Test performance under API rate limits."""
    from src.ai.models.base import BaseModel

    model = BaseModel()

    performance_metrics.measure("start_api_test")

    success_count = 0
    for _ in range(100):
        try:
            model.process("test input")
            success_count += 1
        except Exception:
            pass

    performance_metrics.measure("end_api_test")

    # Verify rate limiting behavior
    total_time = get_measurement_duration(performance_metrics, "api_test")
    requests_per_second = success_count / total_time
    assert requests_per_second <= model.rate_limit


def test_cache_performance(performance_metrics):
    """Test caching performance."""
    from src.storage.cache import Cache

    cache = Cache()

    # Test cache write performance
    performance_metrics.measure("start_cache_write")
    for i in range(1000):
        cache.set(f"key_{i}", f"value_{i}")
    performance_metrics.measure("end_cache_write")

    # Test cache read performance
    performance_metrics.measure("start_cache_read")
    for i in range(1000):
        value = cache.get(f"key_{i}")
    performance_metrics.measure("end_cache_read")

    # Verify cache speed
    read_time = get_measurement_duration(performance_metrics, "cache_read")
    assert read_time / 1000 < 0.001  # Max 1ms per read


@pytest.mark.slow
def test_long_running_stability(performance_metrics):
    """Test system stability over long running periods."""
    config = VideoConfig()
    pipeline = VideoPipeline(config)

    performance_metrics.measure("start_stability")

    # Process videos continuously for 1 hour
    end_time = time.time() + 3600
    videos_processed = 0

    while time.time() < end_time:
        video = create_test_video(size_mb=100, duration=300)
        try:
            pipeline.process(video)
            videos_processed += 1
        except ProcessingError:
            break

    performance_metrics.measure("end_stability")

    # Verify stability metrics
    report = performance_metrics.get_report()
    assert videos_processed >= 10  # Minimum throughput
    assert report["peak_memory"] <= 4 * 1024 * 1024 * 1024  # Memory stability


# Helper functions
def create_test_video(size_mb: int, duration: int) -> Path:
    """Create a test video file of specified size and duration.

    Args:
        size_mb: Size in megabytes
        duration: Duration in seconds

    Returns:
        Path to created video file
    """
    import cv2
    import numpy as np

    # Create a temporary file
    temp_dir = Path("temp_videos")
    temp_dir.mkdir(exist_ok=True)
    video_path = temp_dir / f"test_{size_mb}mb_{duration}s.mp4"

    # Calculate frame size to achieve target file size
    target_bytes = size_mb * 1024 * 1024
    frames = duration * 30  # 30 fps
    bytes_per_frame = target_bytes / frames
    frame_size = int(np.sqrt(bytes_per_frame / 3))  # 3 channels (RGB)

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(video_path), fourcc, 30.0, (frame_size, frame_size))

    # Generate frames
    for _ in range(frames):
        frame = np.random.randint(0, 256, (frame_size, frame_size, 3), dtype=np.uint8)
        out.write(frame)

    out.release()
    return video_path


def get_measurement_duration(metrics: PerformanceMetrics, label: str) -> float:
    """Get duration between start_label and end_label measurements.

    Args:
        metrics: PerformanceMetrics instance containing measurements
        label: Base label without start/end prefix

    Returns:
        Duration in seconds between start and end measurements
    """
    start_label = f"start_{label}"
    end_label = f"end_{label}"

    start_time = None
    end_time = None

    for measurement in metrics.measurements:
        if measurement["label"] == start_label:
            start_time = measurement["time_elapsed"]
        elif measurement["label"] == end_label:
            end_time = measurement["time_elapsed"]

    if start_time is None or end_time is None:
        raise ValueError(f"Could not find start or end measurement for label: {label}")

    return end_time - start_time


def get_video_duration(video_path: str) -> float:
    """Get duration of a video file in seconds.

    Args:
        video_path: Path to the video file

    Returns:
        Duration of the video in seconds
    """
    import cv2

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    # Get frame count and FPS
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Release the video capture object
    cap.release()

    if frame_count <= 0 or fps <= 0:
        raise ValueError(f"Invalid frame count or FPS for video: {video_path}")

    return frame_count / fps
