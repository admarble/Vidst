"""Type definitions and constants for Twelve Labs integration.

This module defines the core data structures and types used throughout
the Twelve Labs integration. It provides type safety and validation for:

- Task types and configurations
- Video metadata
- API responses
- Search results

All types are designed to be immutable and self-documenting.

:no-index:
"""

from enum import Enum
from typing import Any, TypedDict, TypeVar

T = TypeVar("T")


class TaskType(Enum):
    """Task types supported by Twelve Labs API.

    This enum defines the valid task types that can be submitted to the
    Twelve Labs API for video processing.

    Attributes:
        SCENE_DETECTION: Detect and segment scenes in video
        TRANSCRIPTION: Generate text transcription from audio
        TEXT_EXTRACTION: Extract visible text from video frames

    Example:
        >>> task = TaskType.SCENE_DETECTION
        >>> task.value
        'scene_detection'

    :no-index:
    """

    SCENE_DETECTION = "scene_detection"
    TRANSCRIPTION = "transcription"
    TEXT_EXTRACTION = "text_extraction"


class VideoMetadata(TypedDict):
    """Video metadata structure.

    Contains metadata about a processed video including its unique
    identifier, storage location, and technical details.

    Attributes:
        video_id: Unique identifier for the video
        index_name: Name of the index where video is stored
        duration: Video duration in seconds
        format: Video file format (e.g., 'mp4')

    Example:
        >>> metadata = VideoMetadata(
        ...     video_id="vid_123",
        ...     index_name="default",
        ...     duration=120.5,
        ...     format="mp4"
        ... )

    :no-index:
    """

    video_id: str
    index_name: str
    duration: float
    format: str


class TaskOptions(TypedDict, total=False):
    """Task options with optional fields.

    Configuration options that can be passed to video processing tasks.
    All fields are optional and will use API defaults if not specified.

    Attributes:
        confidence_threshold: Minimum confidence score (0.0 to 1.0)
        max_scenes: Maximum number of scenes to detect
        language: ISO language code for transcription
        include_metadata: Whether to include video metadata

    Example:
        >>> options = TaskOptions(
        ...     confidence_threshold=0.8,
        ...     max_scenes=100,
        ...     language="en",
        ...     include_metadata=True
        ... )

    :no-index:
    """

    confidence_threshold: float
    max_scenes: int
    language: str
    include_metadata: bool


class TaskResult(TypedDict):
    """Task result structure.

    Contains the result of a completed task including its status
    and any error information.

    Attributes:
        task_id: Unique identifier for the task
        status: Current status ("completed", "failed", etc.)
        result: Task-specific result data
        error: Error message if task failed
        video_id: ID of processed video (for upload tasks)

    Example:
        >>> result = TaskResult(
        ...     task_id="task_123",
        ...     status="completed",
        ...     result={"scenes": [...]},
        ...     error=None,
        ...     video_id="vid_123"
        ... )

    :no-index:
    """

    task_id: str
    status: str
    result: dict[str, Any]
    error: str | None
    video_id: str | None


class SearchResult(TypedDict):
    """Search result structure.

    Contains information about a video segment matching a search query.

    Attributes:
        video_id: ID of the matched video
        confidence: Match confidence score (0.0 to 1.0)
        start_time: Start time of matched segment in seconds
        end_time: End time of matched segment in seconds
        metadata: Additional metadata about the match

    Example:
        >>> match = SearchResult(
        ...     video_id="vid_123",
        ...     confidence=0.95,
        ...     start_time=10.5,
        ...     end_time=15.2,
        ...     metadata={"scene_type": "dialogue"}
        ... )

    :no-index:
    """

    video_id: str
    confidence: float
    start_time: float
    end_time: float
    metadata: dict[str, Any]


def dict_pop(d: dict[str, Any], key: str, default: T | None = None) -> Any | T:
    """Remove specified key and return the corresponding value.

    Args:
        d: Dictionary to pop from
        key: The key to remove
        default: Value to return if key not found

    Returns:
        The value for the removed key, or default if not found
    """
    return d.pop(key, default)


def dict_update(d: dict[str, Any], other: dict[str, Any]) -> None:
    """Update dictionary with elements from another dictionary.

    Args:
        d: Dictionary to update
        other: Dictionary to update from
    """
    d.update(other)
