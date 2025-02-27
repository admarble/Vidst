"""Custom assertions for test validation."""

from typing import Any

import numpy as np


def assert_video_metadata(metadata: dict[str, Any]) -> None:
    """Assert video metadata structure and types."""
    assert isinstance(metadata, dict), "Metadata must be a dictionary"
    required_fields = ["id", "duration", "fps", "resolution", "format"]
    for field in required_fields:
        assert field in metadata, f"Missing required field: {field}"
    assert isinstance(metadata["duration"], (int, float)), "Duration must be numeric"
    assert isinstance(metadata["fps"], (int, float)), "FPS must be numeric"
    assert isinstance(metadata["resolution"], tuple), "Resolution must be a tuple"
    assert len(metadata["resolution"]) == 2, "Resolution must have width and height"


def assert_scene_data(scenes: list[dict[str, Any]]) -> None:
    """Assert scene detection data structure and validity."""
    assert isinstance(scenes, list), "Scenes must be a list"
    for scene in scenes:
        assert isinstance(scene, dict), "Each scene must be a dictionary"
        required_fields = ["start_time", "end_time", "confidence"]
        for field in required_fields:
            assert field in scene, f"Missing required field in scene: {field}"
        assert scene["start_time"] >= 0, "Start time must be non-negative"
        assert (
            scene["end_time"] > scene["start_time"]
        ), "End time must be after start time"
        assert 0 <= scene["confidence"] <= 1, "Confidence must be between 0 and 1"


def assert_transcription_data(transcription: dict[str, Any]) -> None:
    """Assert transcription data structure and validity."""
    assert isinstance(transcription, dict), "Transcription must be a dictionary"
    assert "segments" in transcription, "Missing segments in transcription"
    assert isinstance(transcription["segments"], list), "Segments must be a list"

    for segment in transcription["segments"]:
        assert isinstance(segment, dict), "Each segment must be a dictionary"
        required_fields = ["start", "end", "text", "confidence"]
        for field in required_fields:
            assert field in segment, f"Missing required field in segment: {field}"
        assert segment["start"] >= 0, "Start time must be non-negative"
        assert segment["end"] > segment["start"], "End time must be after start time"
        assert isinstance(segment["text"], str), "Text must be a string"
        assert 0 <= segment["confidence"] <= 1, "Confidence must be between 0 and 1"


def assert_frame_data(frame: np.ndarray | bytes) -> None:
    """Assert video frame data validity."""
    if isinstance(frame, np.ndarray):
        assert len(frame.shape) in [2, 3], "Frame must be 2D or 3D array"
        if len(frame.shape) == 3:
            assert frame.shape[2] in [1, 3, 4], "Invalid number of channels"
    else:
        assert isinstance(frame, bytes), "Frame must be numpy array or bytes"
