"""Performance benchmarks for video processing pipeline.

This module contains comprehensive benchmarks for measuring the performance of
various components in the video processing pipeline, including:
- Scene detection
- Audio transcription
- Text extraction
- End-to-end processing
- Memory usage
- Concurrent processing capabilities

Requirements:
    - pytest-benchmark: For performance measurements
    - memory-profiler: For memory usage tracking
    - OpenCV (cv2): For video processing
    - numpy: For frame generation

Example Usage:
    Run all benchmarks:
        pytest benchmarks/test_performance.py --benchmark-only

    Run memory profiling:
        pytest benchmarks/test_performance.py -v -k test_memory_usage

    Run specific benchmark:
        pytest benchmarks/test_performance.py -v -k test_scene_detection_performance

Notes:
    - Benchmarks use randomly generated video files of different sizes
    - Processing time is validated against 2x real-time requirement
    - Memory profiling is available for resource usage analysis
    - Concurrent processing tests validate parallel execution
"""

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, Generator

import cv2
import numpy as np
import pytest
import pytest_asyncio
from memory_profiler import profile

from video_understanding.ai.pipeline import VideoPipeline
from video_understanding.core.config import ProcessingConfig


# Configuration for benchmarks
BENCHMARK_CONFIG = {
    "min_rounds": 5,  # Minimum number of rounds to run
    "max_time": 30,  # Maximum time in seconds to run
    "timer": "perf_counter",  # Use performance counter for timing
    "warmup": True,  # Enable warmup rounds
}


@pytest.fixture
def benchmark_config() -> ProcessingConfig:
    """Create benchmark configuration.

    Returns:
        ProcessingConfig: Benchmark configuration instance with default settings
            for testing. The actual parameters should match your ProcessingConfig
            implementation.
    """
    # Note: Update these parameters to match your ProcessingConfig implementation
    return ProcessingConfig()


@pytest.fixture
def sample_videos(tmp_path: Path) -> Dict[str, Path]:
    """Create sample videos for benchmarking.

    This fixture generates synthetic video files of different sizes for testing:
    - small: 640x480, 100 frames
    - medium: 1280x720, 300 frames
    - large: 1920x1080, 600 frames

    All videos are generated at 30 fps with random frame content.

    Args:
        tmp_path: Temporary directory path provided by pytest.

    Returns:
        Dict[str, Path]: Dictionary mapping size labels to video file paths.
    """
    videos = {}

    # Create different types of sample videos
    for name, (frames, fps, width, height) in {
        "small": (100, 30, 640, 480),
        "medium": (300, 30, 1280, 720),
        "large": (600, 30, 1920, 1080),
    }.items():
        path = tmp_path / f"{name}.mp4"
        # Note: VideoWriter_fourcc is a function in cv2, may need version check
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(path), fourcc, fps, (width, height))

        # Generate random frames
        for _ in range(frames):
            frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
            out.write(frame)

        out.release()
        videos[name] = path

    return videos


@pytest_asyncio.fixture
async def pipeline(benchmark_config: ProcessingConfig) -> VideoPipeline:
    """Create pipeline instance for benchmarking.

    Args:
        benchmark_config: Benchmark configuration instance.

    Returns:
        VideoPipeline: Configured pipeline instance for testing.
    """
    return VideoPipeline(config=benchmark_config)


def test_scene_detection_performance(
    benchmark,
    pipeline: VideoPipeline,
    sample_videos: Dict[str, Path]
) -> None:
    """Benchmark scene detection performance.

    This test measures the performance of the scene detection component
    using a medium-sized video file. The benchmark runs multiple iterations
    to get statistically significant results.

    Args:
        benchmark: Pytest benchmark fixture for performance measurement.
        pipeline: Pipeline instance for testing.
        sample_videos: Dictionary of sample video files.
    """
    video_path = sample_videos["medium"]

    async def run_detection() -> None:
        await pipeline.detect_scenes(video_path)

    benchmark.pedantic(
        lambda: asyncio.run(run_detection()),
        **BENCHMARK_CONFIG
    )


def test_audio_transcription_performance(
    benchmark,
    pipeline: VideoPipeline,
    sample_videos: Dict[str, Path]
) -> None:
    """Benchmark audio transcription performance.

    This test measures the performance of the audio transcription component
    using a medium-sized video file. Note that the synthetic test videos
    don't contain actual audio, so this is primarily a pipeline test.

    Args:
        benchmark: Pytest benchmark fixture for performance measurement.
        pipeline: Pipeline instance for testing.
        sample_videos: Dictionary of sample video files.
    """
    video_path = sample_videos["medium"]

    async def run_transcription() -> None:
        await pipeline.transcribe_audio(video_path)

    benchmark.pedantic(
        lambda: asyncio.run(run_transcription()),
        **BENCHMARK_CONFIG
    )


def test_text_extraction_performance(
    benchmark,
    pipeline: VideoPipeline,
    sample_videos: Dict[str, Path]
) -> None:
    """Benchmark text extraction performance.

    This test measures the performance of the text extraction component
    using a medium-sized video file. Note that the synthetic test videos
    don't contain actual text, so this is primarily a pipeline test.

    Args:
        benchmark: Pytest benchmark fixture for performance measurement.
        pipeline: Pipeline instance for testing.
        sample_videos: Dictionary of sample video files.
    """
    video_path = sample_videos["medium"]

    async def run_extraction() -> None:
        await pipeline.extract_text(video_path)

    benchmark.pedantic(
        lambda: asyncio.run(run_extraction()),
        **BENCHMARK_CONFIG
    )


@profile
def test_memory_usage(
    pipeline: VideoPipeline,
    sample_videos: Dict[str, Path]
) -> None:
    """Benchmark memory usage during processing.

    This test profiles memory usage during full pipeline processing of a
    large video file. The @profile decorator from memory_profiler provides
    detailed memory usage statistics.

    Args:
        pipeline: Pipeline instance for testing.
        sample_videos: Dictionary of sample video files.
    """
    video_path = sample_videos["large"]

    async def run_processing() -> None:
        await pipeline.process({
            "video_path": str(video_path),
            "task": "full_pipeline"
        })

    asyncio.run(run_processing())


def test_concurrent_processing_performance(
    benchmark,
    pipeline: VideoPipeline,
    sample_videos: Dict[str, Path]
) -> None:
    """Benchmark concurrent processing performance.

    This test measures the performance of concurrent video processing by
    running scene detection on multiple videos of different sizes simultaneously.

    Args:
        benchmark: Pytest benchmark fixture for performance measurement.
        pipeline: Pipeline instance for testing.
        sample_videos: Dictionary of sample video files.
    """
    video_paths = [
        str(sample_videos["small"]),
        str(sample_videos["medium"]),
        str(sample_videos["large"])
    ]

    async def run_concurrent() -> None:
        tasks = [
            pipeline.process({"video_path": path, "task": "scene_detection"})
            for path in video_paths
        ]
        await asyncio.gather(*tasks)

    benchmark.pedantic(
        lambda: asyncio.run(run_concurrent()),
        **BENCHMARK_CONFIG
    )


@pytest.mark.parametrize("video_size", ["small", "medium", "large"])
def test_processing_speed_by_size(
    benchmark,
    pipeline: VideoPipeline,
    sample_videos: Dict[str, Path],
    video_size: str
) -> None:
    """Benchmark processing speed for different video sizes.

    This test verifies that processing time remains within 2x real-time
    for videos of different sizes. The test is parameterized to run
    with small, medium, and large video files.

    Args:
        benchmark: Pytest benchmark fixture for performance measurement.
        pipeline: Pipeline instance for testing.
        sample_videos: Dictionary of sample video files.
        video_size: Size of video to test ("small", "medium", or "large").
    """
    video_path = sample_videos[video_size]

    async def run_processing() -> None:
        await pipeline.process({
            "video_path": str(video_path),
            "task": "full_pipeline"
        })

    # Run benchmark and compare against video duration
    result = benchmark.pedantic(
        lambda: asyncio.run(run_processing()),
        **BENCHMARK_CONFIG
    )

    # Get video duration
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()

    video_duration = frame_count / fps
    # Access mean from benchmark result statistics
    processing_time = result.stats.get("mean", 0)

    # Assert processing is faster than 2x real-time
    assert processing_time <= video_duration * 2, (
        f"Processing time ({processing_time:.2f}s) exceeded 2x "
        f"video duration ({video_duration * 2:.2f}s)"
    )


def test_end_to_end_pipeline_performance(
    benchmark,
    pipeline: VideoPipeline,
    sample_videos: Dict[str, Path]
) -> None:
    """Benchmark end-to-end pipeline performance.

    This test measures the performance of the complete video processing
    pipeline using a medium-sized video file. It runs the full pipeline
    including scene detection, audio transcription, and text extraction.

    Args:
        benchmark: Pytest benchmark fixture for performance measurement.
        pipeline: Pipeline instance for testing.
        sample_videos: Dictionary of sample video files.
    """
    video_path = sample_videos["medium"]

    async def run_pipeline() -> None:
        await pipeline.process({
            "video_path": str(video_path),
            "task": "full_pipeline"
        })

    benchmark.pedantic(
        lambda: asyncio.run(run_pipeline()),
        **BENCHMARK_CONFIG
    )
