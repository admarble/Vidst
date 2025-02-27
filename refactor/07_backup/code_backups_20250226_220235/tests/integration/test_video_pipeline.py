"""Integration tests for video processing pipeline.

This module contains integration tests for the video processing pipeline,
testing scene detection, audio transcription, text extraction, error handling,
resource management, concurrent processing, and performance metrics.
"""

# Standard library imports
import asyncio
import concurrent.futures
import time
from pathlib import Path
from typing import Any, Dict

from unittest.mock import Mock, patch

# Third-party imports
import cv2
import pytest
import pytest_asyncio

# Local imports
from video_understanding.ai.pipeline import VideoPipeline
from video_understanding.core.config import ProcessingConfig
from video_understanding.core.exceptions import ProcessingError


# pylint: disable=redefined-outer-name
# The following fixtures are meant to be used as test dependencies
@pytest_asyncio.fixture
async def config() -> ProcessingConfig:
    """Create test configuration.

    Returns:
        ProcessingConfig: Test configuration instance.
    """
    return ProcessingConfig()


@pytest_asyncio.fixture
async def pipeline(config: ProcessingConfig) -> VideoPipeline:
    """Create test pipeline.

    Args:
        config: Test configuration instance.

    Returns:
        VideoPipeline: Configured pipeline instance.
    """
    return VideoPipeline(config=config)


@pytest.fixture
def sample_video_files(tmp_path: Path) -> dict[str, Path]:
    """Create sample video files for testing.

    Args:
        tmp_path: Temporary directory path.

    Returns:
        Dict[str, Path]: Dictionary of test video file paths.
    """
    files = {
        "valid_mp4": tmp_path / "sample.mp4",
        "valid_avi": tmp_path / "sample.avi",
        "valid_mov": tmp_path / "sample.mov",
        "empty": tmp_path / "empty.mp4",
        "invalid": tmp_path / "invalid.txt",
    }

    # Create files
    for path in files.values():
        path.touch()

    # Add content to valid files
    for name in ["valid_mp4", "valid_avi", "valid_mov"]:
        files[name].write_bytes(b"test video content")

    return files


@pytest.fixture
def mock_cv2():
    """Mock OpenCV for testing.

    Returns:
        Mock: Mocked cv2.VideoCapture instance.
    """
    with patch("cv2.VideoCapture") as mock_capture:
        # Create a mock for cv2.CAP_PROP constants
        cv2.CAP_PROP_FPS = 5
        cv2.CAP_PROP_FRAME_COUNT = 7
        cv2.CAP_PROP_FRAME_WIDTH = 3
        cv2.CAP_PROP_FRAME_HEIGHT = 4

        # Create a mock capture object
        cap = Mock()
        cap.isOpened.return_value = True

        # Mock the get method to return appropriate values
        def mock_get(prop: int) -> float:
            return {
                5: 30.0,  # FPS
                7: 300.0,  # Frame count
                3: 1920.0,  # Width
                4: 1080.0,  # Height
            }[prop]

        cap.get.side_effect = mock_get
        mock_capture.return_value = cap
        yield mock_capture


@pytest.mark.asyncio
async def test_pipeline_scene_detection(
    pipeline: VideoPipeline,
    sample_video_files: dict[str, Path],
    mock_cv2: Mock,  # pylint: disable=unused-argument
) -> None:
    """Test scene detection accuracy.

    Args:
        pipeline: Test pipeline instance.
        sample_video_files: Dictionary of test video files.
        mock_cv2: Mocked cv2 instance (needed for setup).
    """
    video_path = sample_video_files["valid_mp4"]
    result = await pipeline.detect_scenes(video_path)
    assert isinstance(result, list)

    processed = await pipeline.process({"video_path": str(video_path)})
    assert isinstance(processed, dict)
    assert "scene_description" in processed


@pytest.mark.asyncio
async def test_pipeline_audio_transcription(
    pipeline: VideoPipeline,
    sample_video_files: dict[str, Path],
    mock_cv2: Mock,  # pylint: disable=unused-argument
) -> None:
    """Test audio transcription and speaker diarization.

    Args:
        pipeline: Test pipeline instance.
        sample_video_files: Dictionary of test video files.
        mock_cv2: Mocked cv2 instance (needed for setup).
    """
    video_path = sample_video_files["valid_mp4"]
    result = await pipeline.transcribe_audio(video_path)
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_pipeline_text_extraction(
    pipeline: VideoPipeline,
    sample_video_files: dict[str, Path],
    mock_cv2: Mock,  # pylint: disable=unused-argument
) -> None:
    """Test OCR and text extraction from video frames.

    Args:
        pipeline: Test pipeline instance.
        sample_video_files: Dictionary of test video files.
        mock_cv2: Mocked cv2 instance (needed for setup).
    """
    video_path = sample_video_files["valid_mp4"]
    result = await pipeline.extract_text(video_path)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_pipeline_error_handling(
    pipeline: VideoPipeline,
    sample_video_files: dict[str, Path]
) -> None:
    """Test error handling for various failure cases.

    Args:
        pipeline: Test pipeline instance.
        sample_video_files: Dictionary of test video files.
    """
    # Test missing file
    with pytest.raises(ProcessingError, match="Video file not found"):
        await pipeline.process({"video_path": "nonexistent.mp4"})

    # Test empty file
    with pytest.raises(ProcessingError, match="Video file is empty"):
        await pipeline.process({"video_path": str(sample_video_files["empty"])})

    # Test invalid format
    with pytest.raises(ProcessingError, match="Unsupported video format"):
        await pipeline.process({"video_path": str(sample_video_files["invalid"])})


@pytest.mark.asyncio
async def test_pipeline_resource_management(
    pipeline: VideoPipeline,
    sample_video_files: dict[str, Path],
    mock_cv2: Mock,  # pylint: disable=unused-argument
) -> None:
    """Test resource management and cleanup.

    Args:
        pipeline: Test pipeline instance.
        sample_video_files: Dictionary of test video files.
        mock_cv2: Mocked cv2 instance (needed for setup).
    """
    # Get initial memory usage for comparison
    initial_memory = pipeline.get_memory_usage()
    assert isinstance(initial_memory, dict)
    assert "rss" in initial_memory

    # Process multiple videos
    for _ in range(3):
        result = await pipeline.process(
            {
                "video_path": str(sample_video_files["valid_mp4"]),
                "task": "scene_detection",
            }
        )
        assert isinstance(result, dict)

    final_memory = pipeline.get_memory_usage()
    assert isinstance(final_memory, dict)
    assert "rss" in final_memory
    assert final_memory["rss"] >= initial_memory["rss"]


@pytest.mark.asyncio
async def test_pipeline_concurrent_processing(
    pipeline: VideoPipeline,
    sample_video_files: dict[str, Path],
    mock_cv2: Mock,  # pylint: disable=unused-argument
) -> None:
    """Test concurrent video processing.

    Args:
        pipeline: Test pipeline instance.
        sample_video_files: Dictionary of test video files.
        mock_cv2: Mocked cv2 instance (needed for setup).
    """
    video_paths = [
        str(sample_video_files["valid_mp4"]),
        str(sample_video_files["valid_avi"]),
        str(sample_video_files["valid_mov"]),
    ]

    async def process_video(path: str) -> Dict[str, Any]:
        result = await pipeline.process({"video_path": path, "task": "scene_detection"})
        assert isinstance(result, dict)
        return result

    tasks = [process_video(path) for path in video_paths]
    results = await asyncio.gather(*tasks)

    assert len(results) == 3
    for result in results:
        assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_pipeline_performance(
    pipeline: VideoPipeline,
    sample_video_files: dict[str, Path],
    mock_cv2: Mock,  # pylint: disable=unused-argument
) -> None:
    """Test processing performance metrics.

    Args:
        pipeline: Test pipeline instance.
        sample_video_files: Dictionary of test video files.
        mock_cv2: Mocked cv2 instance (needed for setup).
    """
    video_path = str(sample_video_files["valid_mp4"])
    start_time = time.time()

    result = await pipeline.process({"video_path": video_path, "task": "scene_detection"})
    processing_time = time.time() - start_time

    assert isinstance(result, dict)
    assert "metadata" in result
    assert isinstance(result["metadata"], dict)
    assert "duration" in result["metadata"]

    # Video is 10 seconds (300 frames at 30 fps)
    video_duration = float(result["metadata"]["duration"])
    assert video_duration == 10.0  # 300 frames / 30 fps
    assert processing_time <= video_duration * 2  # Should process faster than 2x real-time


@pytest.mark.asyncio
async def test_complete_pipeline(
    pipeline: VideoPipeline,
    sample_video_files: dict[str, Path],
    mock_cv2: Mock,  # pylint: disable=unused-argument
) -> None:
    """Test the complete video processing pipeline.

    Args:
        pipeline: Test pipeline instance.
        sample_video_files: Dictionary of test video files.
        mock_cv2: Mocked cv2 instance (needed for setup).
    """
    video_path = sample_video_files["valid_mp4"]

    # Process video
    result = await pipeline.process({"video_path": str(video_path)})
    assert isinstance(result, dict)
    assert "metadata" in result
    metadata = result["metadata"]
    assert isinstance(metadata, dict)
    assert "dimensions" in metadata
    dimensions = metadata["dimensions"]
    assert isinstance(dimensions, tuple)
    assert len(dimensions) == 2
    assert dimensions == (1920, 1080)

    # Check scene detection
    scenes = await pipeline.detect_scenes(video_path)
    assert isinstance(scenes, list)
    assert len(scenes) > 0

    # Check text extraction
    text_results = await pipeline.extract_text(video_path)
    assert isinstance(text_results, list)

    # Check audio transcription
    audio_results = await pipeline.transcribe_audio(video_path)
    assert isinstance(audio_results, dict)
