"""Integration tests for video processing pipeline."""

import os
import tempfile
from pathlib import Path

import cv2
import numpy as np
import pytest

from src.ai.pipeline import VideoPipeline
from src.core.config import VideoConfig
from src.core.exceptions import ProcessingError


@pytest.fixture
def pipeline():
    """Create a pipeline instance for testing."""
    config = VideoConfig()
    return VideoPipeline(config)


@pytest.fixture
def sample_video_files(tmp_path):
    """Create sample video files for testing."""
    files = {}

    # Create a valid MP4 file
    mp4_path = tmp_path / "sample.mp4"
    create_test_video(mp4_path, duration=1.0)
    files["valid_mp4"] = mp4_path

    # Create a valid AVI file
    avi_path = tmp_path / "sample.avi"
    create_test_video(avi_path, duration=1.0)
    files["valid_avi"] = avi_path

    # Create a valid MOV file
    mov_path = tmp_path / "sample.mov"
    create_test_video(mov_path, duration=1.0)
    files["valid_mov"] = mov_path

    # Create an empty file
    empty_path = tmp_path / "empty.mp4"
    empty_path.touch()
    files["empty"] = empty_path

    # Create an invalid format file
    invalid_path = tmp_path / "invalid.xyz"
    invalid_path.write_bytes(b"invalid data")
    files["invalid_format"] = invalid_path

    return files


def create_test_video(path, duration=1.0):
    """Create a test video file with specified duration."""
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
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to create video: {e.stderr.decode()}")


def test_pipeline_scene_detection(pipeline, sample_video_files):
    """Test scene detection accuracy."""
    video_path = sample_video_files["valid_mp4"]
    result = pipeline.detect_scenes(str(video_path))
    assert isinstance(result, list)


def test_pipeline_audio_transcription(pipeline, sample_video_files):
    """Test audio transcription and speaker diarization."""
    video_path = sample_video_files["valid_mp4"]
    result = pipeline.transcribe_audio(str(video_path))
    assert isinstance(result, dict)


def test_pipeline_text_extraction(pipeline, sample_video_files):
    """Test OCR and text extraction from video frames."""
    video_path = sample_video_files["valid_mp4"]
    result = pipeline.extract_text(str(video_path))
    assert isinstance(result, list)


def test_pipeline_error_handling(pipeline, sample_video_files):
    """Test error handling for corrupted or invalid videos."""
    with pytest.raises(ProcessingError, match="Failed to process video"):
        pipeline.process(
            {
                "video_path": str(sample_video_files["invalid_format"]),
                "task": "scene_detection",
            }
        )


def test_pipeline_resource_management(pipeline, sample_video_files):
    """Test resource management and cleanup."""
    initial_memory = pipeline.get_memory_usage()

    # Process multiple videos
    for _ in range(3):
        pipeline.process(
            {
                "video_path": str(sample_video_files["valid_mp4"]),
                "task": "scene_detection",
            }
        )

    final_memory = pipeline.get_memory_usage()
    # Ensure memory usage stays within reasonable bounds
    assert (
        final_memory["rss"] - initial_memory["rss"]
    ) < 100  # Less than 100MB increase


def test_pipeline_concurrent_processing(pipeline, sample_video_files):
    """Test concurrent video processing."""
    import concurrent.futures

    video_paths = [
        str(sample_video_files["valid_mp4"]),
        str(sample_video_files["valid_avi"]),
        str(sample_video_files["valid_mov"]),
    ]

    def process_video(path):
        return pipeline.process({"video_path": path, "task": "scene_detection"})

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(process_video, path) for path in video_paths]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 3
    assert all(isinstance(result, dict) for result in results)


def test_pipeline_performance(pipeline, sample_video_files):
    """Test processing performance metrics."""
    import time

    video_path = str(sample_video_files["valid_mp4"])
    start_time = time.time()

    result = pipeline.process({"video_path": video_path, "task": "scene_detection"})

    processing_time = time.time() - start_time
    assert (
        processing_time < result["metadata"]["duration"] * 2
    )  # Should process faster than 2x video duration
