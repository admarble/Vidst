"""Test module for Scene model.

This module contains tests for the Scene dataclass and its methods.
"""

from datetime import datetime
from pathlib import Path
from typing import cast
from uuid import UUID, uuid4

import pytest

from video_understanding.models.scene import Scene


@pytest.fixture
def video_id():
    """Create a test video ID."""
    return uuid4()


@pytest.fixture
def scene_id():
    """Create a test scene ID."""
    return uuid4()


@pytest.fixture
def basic_scene(video_id):
    """Create a basic valid scene."""
    return Scene(
        video_id=video_id,
        start_time=0.0,
        end_time=5.0,
    )


@pytest.fixture
def full_scene(video_id, scene_id, tmp_path):
    """Create a scene with all attributes set."""
    keyframe_path = tmp_path / "keyframe.jpg"
    keyframe_path.write_bytes(b"mock keyframe")

    return Scene(
        id=scene_id,
        video_id=video_id,
        start_time=0.0,
        end_time=5.0,
        keyframe_path=keyframe_path,
        confidence_score=0.95,
        metadata={"tags": ["action", "dialog"]},
        created_at=datetime(2024, 1, 1, 12, 0),
    )


def test_scene_creation_minimal(video_id):
    """Test creating a scene with minimal required attributes."""
    scene = Scene(
        video_id=video_id,
        start_time=0.0,
        end_time=5.0,
    )

    assert isinstance(scene.id, UUID)
    assert scene.video_id == video_id
    assert scene.start_time == 0.0
    assert scene.end_time == 5.0
    assert scene.keyframe_path is None
    assert scene.confidence_score == 0.0
    assert scene.metadata == {}
    assert isinstance(scene.created_at, datetime)


def test_scene_creation_full(full_scene, video_id, scene_id):
    """Test creating a scene with all attributes."""
    assert full_scene.id == scene_id
    assert full_scene.video_id == video_id
    assert full_scene.start_time == 0.0
    assert full_scene.end_time == 5.0
    assert isinstance(full_scene.keyframe_path, Path)
    assert full_scene.confidence_score == 0.95
    assert full_scene.metadata == {"tags": ["action", "dialog"]}
    assert full_scene.created_at == datetime(2024, 1, 1, 12, 0)


def test_scene_post_init_uuid_conversion():
    """Test UUID string conversion in post_init."""
    video_id_str = str(uuid4())
    scene_id_str = str(uuid4())

    # Create UUIDs from strings for type safety
    video_id = UUID(video_id_str)
    scene_id = UUID(scene_id_str)

    scene = Scene(
        id=scene_id,
        video_id=video_id,
        start_time=0.0,
        end_time=5.0,
    )

    assert isinstance(scene.id, UUID)
    assert isinstance(scene.video_id, UUID)
    assert str(scene.id) == scene_id_str
    assert str(scene.video_id) == video_id_str


def test_scene_invalid_times():
    """Test scene creation with invalid time values."""
    video_id = uuid4()

    # Test negative start time
    with pytest.raises(ValueError, match="Start time cannot be negative"):
        Scene(
            video_id=video_id,
            start_time=-1.0,
            end_time=5.0,
        )

    # Test end time before start time
    with pytest.raises(ValueError, match="End time must be greater than start time"):
        Scene(
            video_id=video_id,
            start_time=5.0,
            end_time=3.0,
        )


def test_scene_duration(basic_scene):
    """Test scene duration calculation."""
    assert basic_scene.duration == 5.0


def test_scene_has_keyframe(full_scene, tmp_path):
    """Test has_keyframe property."""
    # Test with existing keyframe
    assert full_scene.has_keyframe is True

    # Test with nonexistent keyframe
    scene = Scene(
        video_id=uuid4(),
        start_time=0.0,
        end_time=5.0,
        keyframe_path=tmp_path / "nonexistent.jpg",
    )
    assert scene.has_keyframe is False

    # Test with no keyframe path
    scene = Scene(
        video_id=uuid4(),
        start_time=0.0,
        end_time=5.0,
    )
    assert scene.has_keyframe is False


def test_scene_to_dict(full_scene):
    """Test conversion to dictionary."""
    scene_dict = full_scene.to_dict()

    assert isinstance(scene_dict, dict)
    assert scene_dict["id"] == str(full_scene.id)
    assert scene_dict["video_id"] == str(full_scene.video_id)
    assert scene_dict["start_time"] == full_scene.start_time
    assert scene_dict["end_time"] == full_scene.end_time
    assert scene_dict["duration"] == full_scene.duration
    assert scene_dict["keyframe_path"] == str(full_scene.keyframe_path)
    assert scene_dict["confidence_score"] == full_scene.confidence_score
    assert scene_dict["metadata"] == full_scene.metadata
    assert scene_dict["created_at"] == full_scene.created_at.isoformat()


def test_scene_from_dict(full_scene):
    """Test creation from dictionary."""
    scene_dict = full_scene.to_dict()
    # Remove duration field as it's a computed property
    scene_dict.pop("duration")
    new_scene = Scene.from_dict(scene_dict)

    assert new_scene.id == full_scene.id
    assert new_scene.video_id == full_scene.video_id
    assert new_scene.start_time == full_scene.start_time
    assert new_scene.end_time == full_scene.end_time
    assert new_scene.keyframe_path == full_scene.keyframe_path
    assert new_scene.confidence_score == full_scene.confidence_score
    assert new_scene.metadata == full_scene.metadata
    assert new_scene.created_at == full_scene.created_at


def test_scene_validate(full_scene, tmp_path):
    """Test scene validation."""
    # Test valid scene
    assert full_scene.validate() is True

    # Test invalid duration
    invalid_duration = Scene(
        video_id=uuid4(),
        start_time=0.0,
        end_time=1.0,  # Less than 2 seconds
    )
    assert invalid_duration.validate() is False

    # Test invalid keyframe
    invalid_keyframe = Scene(
        video_id=uuid4(),
        start_time=0.0,
        end_time=5.0,
        keyframe_path=tmp_path / "nonexistent.jpg",
    )
    assert invalid_keyframe.validate() is False

    # Test invalid confidence score
    invalid_confidence = Scene(
        video_id=uuid4(),
        start_time=0.0,
        end_time=5.0,
        confidence_score=1.5,  # Greater than 1.0
    )
    assert invalid_confidence.validate() is False


def test_scene_validate_error_handling():
    """Test validation error handling."""
    # Create a scene that will raise an exception during validation
    scene = Scene(
        video_id=uuid4(),
        start_time=0.0,
        end_time=5.0,
    )

    # Create a mock object that will raise an exception when accessed
    class MockPath:
        def exists(self) -> bool:
            raise RuntimeError("Test error")

    # Set keyframe_path to the mock object
    scene.keyframe_path = cast(Path, MockPath())

    assert scene.validate() is False
