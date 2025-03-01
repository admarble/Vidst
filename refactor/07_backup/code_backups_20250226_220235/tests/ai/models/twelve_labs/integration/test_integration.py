"""Integration tests for Twelve Labs integration."""

import os
from typing import cast

import pytest

from video_understanding.ai.models.twelve_labs.model import TwelveLabsModel
from video_understanding.ai.models.twelve_labs.types import (
    SearchResult,
    TaskOptions,
    TaskResult,
    TaskType,
)

# Skip tests if API key not available
pytestmark = pytest.mark.skipif(
    os.getenv("TWELVE_LABS_API_KEY") is None,
    reason="TWELVE_LABS_API_KEY environment variable not set",
)


@pytest.fixture
def model():
    """Create a TwelveLabsModel instance."""
    api_key = os.getenv("TWELVE_LABS_API_KEY")
    if api_key is None:
        pytest.skip("TWELVE_LABS_API_KEY environment variable not set")
    return TwelveLabsModel(api_key=api_key)


@pytest.fixture
def test_video_path():
    """Path to test video file."""
    return os.path.join(os.path.dirname(__file__), "fixtures", "test_video.mp4")


async def test_end_to_end_scene_detection(twelve_labs_model, video_path):
    """Test end-to-end scene detection workflow."""
    # Process video
    options = TaskOptions(confidence_threshold=0.8, max_scenes=100)
    result = await twelve_labs_model.process_video(
        video_path, TaskType.SCENE_DETECTION, options
    )

    # Verify result
    assert isinstance(result, dict)
    result = cast(TaskResult, result)
    assert result["status"] == "completed"
    assert "scenes" in result["result"]
    assert len(result["result"]["scenes"]) > 0

    # Verify scene structure
    first_scene = result["result"]["scenes"][0]
    assert "start" in first_scene
    assert "end" in first_scene
    assert first_scene["start"] >= 0
    assert first_scene["end"] > first_scene["start"]


async def test_end_to_end_transcription(twelve_labs_model, video_path):
    """Test end-to-end transcription workflow."""
    # Process video
    options = TaskOptions(confidence_threshold=0.8, language="en")
    result = await twelve_labs_model.process_video(
        video_path, TaskType.TRANSCRIPTION, options
    )

    # Verify result
    assert isinstance(result, dict)
    result = cast(TaskResult, result)
    assert result["status"] == "completed"
    assert "transcription" in result["result"]
    assert len(result["result"]["transcription"]) > 0

    # Verify transcription structure
    first_segment = result["result"]["transcription"][0]
    assert "text" in first_segment
    assert "start" in first_segment
    assert "end" in first_segment
    assert first_segment["start"] >= 0
    assert first_segment["end"] > first_segment["start"]


async def test_end_to_end_text_extraction(twelve_labs_model, video_path):
    """Test end-to-end text extraction workflow."""
    # Process video
    options = TaskOptions(confidence_threshold=0.8)
    result = await twelve_labs_model.process_video(
        video_path, TaskType.TEXT_EXTRACTION, options
    )

    # Verify result
    assert isinstance(result, dict)
    result = cast(TaskResult, result)
    assert result["status"] == "completed"
    assert "text" in result["result"]
    assert len(result["result"]["text"]) > 0

    # Verify text structure
    first_text = result["result"]["text"][0]
    assert "content" in first_text
    assert "timestamp" in first_text
    assert first_text["timestamp"] >= 0


async def test_end_to_end_search(twelve_labs_model, video_path):
    """Test end-to-end search workflow."""
    # First process video
    options = TaskOptions(confidence_threshold=0.8)
    process_result = await twelve_labs_model.process_video(
        video_path, TaskType.SCENE_DETECTION, options
    )
    assert process_result["status"] == "completed"

    # Search video
    video_id = process_result["video_id"]
    search_results = await twelve_labs_model.search_video(video_id, "person talking")

    # Verify search results
    assert len(search_results) > 0
    first_result = search_results[0]
    assert isinstance(first_result, dict)
    first_result = cast(SearchResult, first_result)
    assert first_result["video_id"] == video_id
    assert first_result["confidence"] > 0
    assert first_result["start_time"] >= 0
    assert first_result["end_time"] > first_result["start_time"]
