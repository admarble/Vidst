"""Output module for Video Understanding AI.

This module handles processing results and output formatting.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from .exceptions import FileValidationError, OutputError, ValidationError


class ProcessingStatus(Enum):
    """Video processing status enumeration.

    This enum represents the possible states of video processing in the system.
    It follows a state machine pattern where transitions between states must
    follow defined rules to maintain system consistency.

    States:
        PENDING: Initial state when a video is queued for processing
            - Initial state for all videos
            - Indicates the video is waiting to be processed
            - Can transition to: PROCESSING

        PROCESSING: Video is actively being processed
            - Indicates the video is currently being analyzed
            - Progress can be tracked via processing_progress field
            - Can transition to: COMPLETED, FAILED

        COMPLETED: Processing finished successfully
            - All processing stages completed successfully
            - Results are available for retrieval
            - Terminal state, no further transitions

        FAILED: Processing encountered an error
            - Processing stopped due to an error
            - Error details available in error_message field
            - Terminal state, no further transitions

    Valid State Transitions:
        PENDING -> PROCESSING: When processing begins
        PROCESSING -> COMPLETED: When all stages complete successfully
        PROCESSING -> FAILED: When an error occurs during processing

    Example:
        >>> from video_understanding.core.output import ProcessingStatus
        >>> # Initialize video status
        >>> status = ProcessingStatus.PENDING
        >>> # Start processing
        >>> status = ProcessingStatus.PROCESSING
        >>> try:
        ...     # Process video...
        ...     status = ProcessingStatus.COMPLETED
        ... except Exception as e:
        ...     status = ProcessingStatus.FAILED
        ...     error_message = str(e)

    Note:
        - Status changes should only occur through the VideoProcessor class
        - Direct enum value changes should be avoided
        - Always check current status before state transitions
        - Invalid state transitions should raise ValidationError
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

    @property
    def is_terminal(self) -> bool:
        """Check if this is a terminal state.

        Returns:
            bool: True if status is COMPLETED or FAILED
        """
        return self in (ProcessingStatus.COMPLETED, ProcessingStatus.FAILED)

    @property
    def can_transition_to(self) -> list["ProcessingStatus"]:
        """Get valid states this status can transition to.

        Returns:
            List[ProcessingStatus]: List of valid next states
        """
        transitions = {
            ProcessingStatus.PENDING: [ProcessingStatus.PROCESSING],
            ProcessingStatus.PROCESSING: [
                ProcessingStatus.COMPLETED,
                ProcessingStatus.FAILED,
            ],
            ProcessingStatus.COMPLETED: [],
            ProcessingStatus.FAILED: [],
        }
        return transitions[self]

    def validate_transition(self, new_status: "ProcessingStatus") -> None:
        """Validate if a transition to new_status is allowed.

        Args:
            new_status: The status to transition to

        Raises:
            ValidationError: If the transition is not allowed
        """
        if new_status not in self.can_transition_to:
            raise ValidationError(
                f"Invalid status transition: {self.value} -> {new_status.value}"
            )


@dataclass
class Scene:
    """Scene information container.

    Attributes:
        scene_id: Unique identifier for the scene
        start_time: Start time in seconds
        end_time: End time in seconds
        keyframe_path: Path to keyframe image
        transcript: Scene transcript
        metadata: Additional metadata dictionary
    """

    scene_id: str
    start_time: float
    end_time: float
    keyframe_path: Path | None
    transcript: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingResult:
    """Processing result container.

    Attributes:
        video_id: Unique identifier for the video
        status: Processing status
        scenes: List of detected scenes
        transcript: Full video transcript
        metadata: Additional metadata dictionary
        created_at: Creation timestamp
        updated_at: Last update timestamp
        error: Error message if processing failed
    """

    video_id: str
    status: ProcessingStatus
    scenes: list[Scene]
    transcript: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    error: str | None = None


def format_timestamp(seconds: float) -> str:
    """Format timestamp in HH:MM:SS.mmm format.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"


def format_scene(scene: Scene) -> dict[str, Any]:
    """Format scene information for output.

    Args:
        scene: Scene object to format

    Returns:
        Formatted scene dictionary
    """
    return {
        "id": scene.scene_id,
        "start_time": format_timestamp(scene.start_time),
        "end_time": format_timestamp(scene.end_time),
        "duration": scene.end_time - scene.start_time,
        "keyframe": str(scene.keyframe_path) if scene.keyframe_path else None,
        "transcript": scene.transcript,
        "metadata": scene.metadata,
    }


def format_result(result: ProcessingResult) -> dict[str, Any]:
    """Format processing result for output.

    Args:
        result: ProcessingResult object to format

    Returns:
        Formatted result dictionary
    """
    return {
        "video_id": result.video_id,
        "status": result.status.value,
        "scenes": [format_scene(scene) for scene in result.scenes],
        "transcript": result.transcript,
        "metadata": result.metadata,
        "created_at": result.created_at.isoformat(),
        "updated_at": result.updated_at.isoformat(),
        "error": result.error,
    }


def validate_output_path(path: Path) -> None:
    """Validate output path.

    Args:
        path: Path to validate

    Raises:
        FileValidationError: If path is invalid or not writable
    """
    try:
        # Check if parent directory exists or can be created
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

        # Check if path is writable by trying to create a test file
        test_file = path.parent / ".test_write"
        test_file.touch()
        test_file.unlink()
    except PermissionError as e:
        raise FileValidationError(
            f"Output path {path} is not writable", file_path=str(path), cause=e
        )
    except Exception as e:
        raise FileValidationError(
            f"Invalid output path {path}: {e!s}", file_path=str(path), cause=e
        )


def validate_input_path(path: Path) -> None:
    """Validate input path.

    Args:
        path: Path to validate

    Raises:
        FileValidationError: If path is invalid or not readable
    """
    if not path.exists():
        raise FileValidationError(
            f"Input file {path} does not exist", file_path=str(path)
        )

    if not path.is_file():
        raise FileValidationError(
            f"Input path {path} is not a file", file_path=str(path)
        )

    try:
        # Check if file is readable
        path.open("r").close()
    except PermissionError as e:
        raise FileValidationError(
            f"Input file {path} is not readable", file_path=str(path), cause=e
        )
    except Exception as e:
        raise FileValidationError(
            f"Invalid input file {path}: {e!s}", file_path=str(path), cause=e
        )


def save_result(result: ProcessingResult, output_path: Path) -> None:
    """Save processing result to file.

    Args:
        result: ProcessingResult object to save
        output_path: Path to output file

    Raises:
        ValidationError: If result is invalid
        FileValidationError: If output path is invalid
        OutputError: If saving fails
    """
    try:
        # Validate output path
        validate_output_path(output_path)

        # Format result as dictionary
        try:
            formatted_result = format_result(result)
        except Exception as e:
            raise ValidationError(f"Failed to format result: {e!s}") from e

        # Save as JSON file
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(formatted_result, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise OutputError(f"Failed to write output file: {e!s}") from e

    except (ValidationError, FileValidationError, OutputError):
        raise
    except Exception as e:
        raise OutputError(f"Unexpected error saving result: {e!s}") from e


def load_result(input_path: Path) -> ProcessingResult:
    """Load processing result from file.

    Args:
        input_path: Path to input file

    Returns:
        Loaded ProcessingResult object

    Raises:
        FileValidationError: If input path is invalid
        ValidationError: If result data is invalid
        OutputError: If loading fails
    """
    try:
        # Validate input path
        validate_input_path(input_path)

        # Load JSON file
        try:
            with open(input_path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON format in {input_path}: {e!s}") from e
        except Exception as e:
            raise OutputError(f"Failed to read input file: {e!s}") from e

        # Parse and validate data
        try:
            # Parse scenes
            scenes = [
                Scene(
                    scene_id=scene["id"],
                    start_time=parse_timestamp(scene["start_time"]),
                    end_time=parse_timestamp(scene["end_time"]),
                    keyframe_path=(
                        Path(scene["keyframe"]) if scene.get("keyframe") else None
                    ),
                    transcript=scene.get("transcript"),
                    metadata=scene.get("metadata", {}),
                )
                for scene in data["scenes"]
            ]

            # Create ProcessingResult object
            return ProcessingResult(
                video_id=data["video_id"],
                status=ProcessingStatus(data["status"]),
                scenes=scenes,
                transcript=data.get("transcript"),
                metadata=data.get("metadata", {}),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                error=data.get("error"),
            )
        except KeyError as e:
            raise ValidationError(
                f"Missing required field in result data: {e!s}"
            ) from e
        except ValueError as e:
            raise ValidationError(f"Invalid value in result data: {e!s}") from e
        except Exception as e:
            raise ValidationError(f"Failed to parse result data: {e!s}") from e

    except (ValidationError, FileValidationError, OutputError):
        raise
    except Exception as e:
        raise OutputError(f"Unexpected error loading result: {e!s}") from e


def parse_timestamp(timestamp: str) -> float:
    """Parse timestamp from HH:MM:SS.mmm format.

    Args:
        timestamp: Timestamp string in format HH:MM:SS.mmm

    Returns:
        Time in seconds

    Raises:
        ValidationError: If timestamp format is invalid
    """
    try:
        # Validate format
        if not timestamp or ":" not in timestamp:
            raise ValueError("Invalid format")

        # Split into components
        parts = timestamp.split(":")
        if len(parts) != 3:
            raise ValueError("Must have hours, minutes, and seconds")

        hours, minutes, seconds = parts

        # Validate numeric values
        hours_val = int(hours)
        minutes_val = int(minutes)
        seconds_val = float(seconds)

        # Validate ranges
        if hours_val < 0 or hours_val >= 24:
            raise ValueError("Hours must be between 0 and 23")
        if minutes_val < 0 or minutes_val >= 60:
            raise ValueError("Minutes must be between 0 and 59")
        if seconds_val < 0 or seconds_val >= 60:
            raise ValueError("Seconds must be between 0 and 59.999")

        # Calculate total seconds
        total_seconds = hours_val * 3600 + minutes_val * 60 + seconds_val
        return total_seconds

    except Exception as e:
        raise ValidationError(f"Invalid timestamp format: {e}") from e


@dataclass
class VideoScene:
    """Represents a detected scene in a video."""

    start_time: float
    end_time: float
    keyframe_path: str | None
    confidence: float
    scene_type: str
    metadata: dict[str, Any]


@dataclass
class TextBlock:
    """Represents extracted text from video frames."""

    text: str
    timestamp: float
    confidence: float
    bounding_box: dict[str, float] | None
    source_frame: str


@dataclass
class TranscriptionSegment:
    """Represents a transcribed segment of speech."""

    text: str
    start_time: float
    end_time: float
    speaker_id: str | None
    confidence: float


class VideoOutput:
    """Handles formatting and organization of video processing results."""

    def __init__(self, video_id: str):
        self.video_id = video_id
        self.scenes: list[VideoScene] = []
        self.text_blocks: list[TextBlock] = []
        self.transcription: list[TranscriptionSegment] = []
        self.metadata: dict[str, Any] = {}
        self.processing_stats: dict[str, Any] = {}
        self.created_at = datetime.utcnow()

    def add_scene(self, scene: VideoScene) -> None:
        """Add a detected scene to the output."""
        self.scenes.append(scene)

    def add_text_block(self, text_block: TextBlock) -> None:
        """Add an extracted text block to the output."""
        self.text_blocks.append(text_block)

    def add_transcription_segment(self, segment: TranscriptionSegment) -> None:
        """Add a transcription segment to the output."""
        self.transcription.append(segment)

    def update_metadata(self, metadata: dict[str, Any]) -> None:
        """Update video metadata."""
        self.metadata.update(metadata)

    def update_processing_stats(self, stats: dict[str, Any]) -> None:
        """Update processing statistics."""
        self.processing_stats.update(stats)

    def to_dict(self) -> dict[str, Any]:
        """Convert the output to a dictionary format."""
        return {
            "video_id": self.video_id,
            "scenes": [vars(scene) for scene in self.scenes],
            "text_blocks": [vars(block) for block in self.text_blocks],
            "transcription": [vars(segment) for segment in self.transcription],
            "metadata": self.metadata,
            "processing_stats": self.processing_stats,
            "created_at": self.created_at.isoformat(),
        }

    def to_json(self, pretty: bool = False) -> str:
        """Convert the output to a JSON string."""
        indent = 2 if pretty else None
        return json.dumps(self.to_dict(), indent=indent)

    def save_to_file(self, output_path: Path) -> Path:
        """Save the output to a file.

        Args:
            output_path: Path where to save the output

        Returns:
            Path to the saved file

        Raises:
            OutputError: If saving fails
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            return output_path
        except Exception as e:
            raise OutputError(f"Failed to save output: {e}") from e


def format_results(
    video_id: str,
    scenes: list[dict[str, Any]],
    text_blocks: list[dict[str, Any]],
    transcription: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
    stats: dict[str, Any] | None = None,
) -> VideoOutput:
    """Format processing results into a structured VideoOutput object.

    Args:
        video_id: Unique identifier for the video
        scenes: List of detected scenes with their metadata
        text_blocks: List of extracted text blocks
        transcription: List of transcription segments
        metadata: Optional video metadata
        stats: Optional processing statistics

    Returns:
        VideoOutput: Structured output containing all processing results
    """
    output = VideoOutput(video_id)

    # Add scenes
    for scene_data in scenes:
        scene = VideoScene(
            start_time=scene_data["start_time"],
            end_time=scene_data["end_time"],
            keyframe_path=scene_data.get("keyframe_path"),
            confidence=scene_data["confidence"],
            scene_type=scene_data["scene_type"],
            metadata=scene_data.get("metadata", {}),
        )
        output.add_scene(scene)

    # Add text blocks
    for block_data in text_blocks:
        block = TextBlock(
            text=block_data["text"],
            timestamp=block_data["timestamp"],
            confidence=block_data["confidence"],
            bounding_box=block_data.get("bounding_box"),
            source_frame=block_data["source_frame"],
        )
        output.add_text_block(block)

    # Add transcription segments
    for segment_data in transcription:
        segment = TranscriptionSegment(
            text=segment_data["text"],
            start_time=segment_data["start_time"],
            end_time=segment_data["end_time"],
            speaker_id=segment_data.get("speaker_id"),
            confidence=segment_data["confidence"],
        )
        output.add_transcription_segment(segment)

    # Add metadata and stats if provided
    if metadata:
        output.update_metadata(metadata)
    if stats:
        output.update_processing_stats(stats)

    return output


def generate_report(
    results: dict[str, Any],
    output_dir: Path | None = None,
) -> Path:
    """Generate a report from processing results.

    Args:
        results: Processing results
        output_dir: Optional output directory

    Returns:
        Path to generated report

    Raises:
        OutputError: If report generation fails
    """
    try:
        output = VideoOutput(results["video_id"])
        formatted = output.to_dict()

        # Create default output directory if not provided
        if output_dir is None:
            output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate output file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"report_{timestamp}.json"

        # Write output
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(formatted, f, indent=2)

        return output_file
    except Exception as e:
        raise OutputError(f"Failed to generate report: {e}") from e


def export_results(
    results: dict[str, Any],
    output_path: Path,
) -> None:
    """Export processing results to a file.

    Args:
        results: Processing results
        output_path: Output file path

    Raises:
        OutputError: If export fails
    """
    try:
        output = VideoOutput(results["video_id"])
        formatted = output.to_dict()

        # Write output
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(formatted, f, indent=2)
    except Exception as e:
        raise OutputError(f"Failed to export results: {e}") from e
