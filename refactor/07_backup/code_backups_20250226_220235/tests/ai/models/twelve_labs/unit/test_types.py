"""Unit tests for Twelve Labs types.

This module contains unit tests for the type definitions used in the Twelve Labs
integration. The tests verify that the TypedDict and Enum classes behave as
expected and properly validate their data.

Note on Lint Configuration:
    This module uses test-specific lint rules defined in ../.pylintrc:
    - Import order follows standard->third-party->local pattern
    - TypedDict instance checks are allowed in tests
    - Dict casting is used for type validation

Example:
    To run these tests with pylint checking:
    ```bash
    pylint --rcfile=tests/ai/models/twelve_labs/.pylintrc tests/ai/models/twelve_labs/
    ```
"""

from typing import Any, cast

import pytest

from video_understanding.ai.models.twelve_labs.types import (
    SearchResult,
    TaskOptions,
    TaskResult,
    TaskType,
    VideoMetadata,
)


def test_task_type_values():
    """Test TaskType enum values."""
    assert TaskType.SCENE_DETECTION.value == "scene_detection"
    assert TaskType.TRANSCRIPTION.value == "transcription"
    assert TaskType.TEXT_EXTRACTION.value == "text_extraction"


def test_task_type_from_string():
    """Test TaskType creation from strings."""
    assert TaskType("scene_detection") == TaskType.SCENE_DETECTION
    assert TaskType("transcription") == TaskType.TRANSCRIPTION
    assert TaskType("text_extraction") == TaskType.TEXT_EXTRACTION


def test_task_type_invalid():
    """Test TaskType with invalid value."""
    with pytest.raises(ValueError):
        TaskType("invalid_task")


def test_video_metadata():
    """Test VideoMetadata type."""
    data: dict[str, Any] = {
        "video_id": "test_123",
        "index_name": "default",
        "duration": 120.5,
        "format": "mp4",
    }
    metadata = VideoMetadata(**data)
    assert metadata["video_id"] == "test_123"
    assert metadata["index_name"] == "default"
    assert metadata["duration"] == 120.5
    assert metadata["format"] == "mp4"


def test_task_options():
    """Test TaskOptions type."""
    # Test with all fields
    data: dict[str, Any] = {
        "confidence_threshold": 0.8,
        "max_scenes": 100,
        "language": "en",
        "include_metadata": True,
    }
    options = cast(dict[str, Any], TaskOptions(**data))
    assert options.get("confidence_threshold") == 0.8
    assert options.get("max_scenes") == 100
    assert options.get("language") == "en"
    assert options.get("include_metadata") is True

    # Test with optional fields omitted
    partial_data: dict[str, Any] = {"confidence_threshold": 0.8}
    partial_options = cast(dict[str, Any], TaskOptions(**partial_data))
    assert partial_options.get("confidence_threshold") == 0.8
    assert partial_options.get("max_scenes") is None


def test_task_result():
    """Test TaskResult type."""
    data: dict[str, Any] = {
        "task_id": "task_123",
        "status": "completed",
        "result": {"scenes": [{"start": 0, "end": 10}]},
        "error": None,
        "video_id": "video_123",
    }
    result = TaskResult(**data)
    assert result["task_id"] == "task_123"
    assert result["status"] == "completed"
    assert isinstance(result["result"], dict)
    assert result["error"] is None
    assert result["video_id"] == "video_123"


def test_search_result():
    """Test SearchResult type."""
    data: dict[str, Any] = {
        "video_id": "video_123",
        "confidence": 0.95,
        "start_time": 5.0,
        "end_time": 15.0,
        "metadata": {"scene_type": "dialogue"},
    }
    result = SearchResult(**data)
    assert result["video_id"] == "video_123"
    assert result["confidence"] == 0.95
    assert result["start_time"] == 5.0
    assert result["end_time"] == 15.0
    assert result["metadata"]["scene_type"] == "dialogue"
