"""Video data models.

This module defines the data models used to represent videos and their
processing status in the system.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4


class ProcessingStatus(str, Enum):
    """Enumeration of possible video processing statuses."""
    PENDING = "pending"
    UPLOADING = "uploading"
    VALIDATING = "validating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    QUARANTINED = "quarantined"


@dataclass
class VideoFile:
    """Information about a video file.

    Attributes:
        filename: Original name of the file
        file_path: Current path to the file in the system
        format: Video format (e.g., MP4, AVI)
        file_size: Size of the file in bytes
        created_at: When the file was created in the system
        modified_at: When the file was last modified
    """
    filename: str
    file_path: str
    format: str
    file_size: int
    created_at: datetime = datetime.now()
    modified_at: datetime = datetime.now()

    def __post_init__(self) -> None:
        """Validate the video file information."""
        if not self.filename:
            raise ValueError("Filename cannot be empty")
        if not self.file_path:
            raise ValueError("File path cannot be empty")
        if not self.format:
            self.format = Path(self.filename).suffix[1:].upper()


@dataclass
class VideoProcessingInfo:
    """Information about video processing status and progress.

    Attributes:
        status: Current processing status
        progress: Processing progress (0-100)
        start_time: When processing started
        end_time: When processing completed
        error: Error message if processing failed
    """
    status: ProcessingStatus = ProcessingStatus.PENDING
    progress: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None

    def update_progress(self, progress: float) -> None:
        """Update the processing progress.

        Args:
            progress: New progress value between 0 and 100
        """
        self.progress = min(max(progress, 0.0), 100.0)

    def mark_completed(self) -> None:
        """Mark processing as completed."""
        self.status = ProcessingStatus.COMPLETED
        self.progress = 100.0
        self.end_time = datetime.now()

    def mark_failed(self, error: str) -> None:
        """Mark processing as failed with an error message.

        Args:
            error: Error message describing what went wrong
        """
        self.status = ProcessingStatus.FAILED
        self.error = error
        self.end_time = datetime.now()

    @property
    def is_complete(self) -> bool:
        """Check if video processing is complete."""
        return self.status == ProcessingStatus.COMPLETED

    @property
    def has_error(self) -> bool:
        """Check if video processing encountered an error."""
        return self.status == ProcessingStatus.FAILED


@dataclass
class VideoMetadata:
    """Technical metadata about a video.

    Attributes:
        duration: Duration in seconds
        width: Frame width in pixels
        height: Frame height in pixels
        fps: Frames per second
        codec: Video codec used
        total_frames: Total number of frames
    """
    duration: float
    width: int
    height: int
    fps: float
    codec: str
    total_frames: int

    def __post_init__(self) -> None:
        """Validate video metadata."""
        if self.duration <= 0:
            raise ValueError("Duration must be positive")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Dimensions must be positive")
        if self.fps <= 0:
            raise ValueError("FPS must be positive")
        if self.total_frames <= 0:
            raise ValueError("Total frames must be positive")


@dataclass
class Video:
    """Main video model containing all video information.

    Attributes:
        id: Unique identifier for the video
        file_info: Information about the video file
        processing: Processing status and progress
        metadata: Technical metadata (available after processing)
    """
    id: UUID
    file_info: VideoFile
    processing: VideoProcessingInfo
    metadata: Optional[VideoMetadata] = None

    def __post_init__(self) -> None:
        """Validate the video ID and initialize if needed."""
        if not isinstance(self.id, UUID):
            self.id = UUID(str(self.id))

    def __eq__(self, other: object) -> bool:
        """Compare videos based on their ID.

        Args:
            other: Another Video instance to compare with

        Returns:
            True if the videos have the same ID, False otherwise
        """
        if not isinstance(other, Video):
            return NotImplemented
        return self.id == other.id

    @property
    def filename(self) -> str:
        """Get the original filename."""
        return self.file_info.filename

    @property
    def file_path(self) -> str:
        """Get the current file path."""
        return self.file_info.file_path

    @property
    def format(self) -> str:
        """Get the video format."""
        return self.file_info.format

    @property
    def duration(self) -> Optional[float]:
        """Get the video duration if metadata is available."""
        return self.metadata.duration if self.metadata else None

    @classmethod
    def from_path(
        cls,
        path: Path,
        id: Optional[UUID] = None,
        status: ProcessingStatus = ProcessingStatus.PENDING
    ) -> "Video":
        """Create a Video instance from a file path.

        Args:
            path: Path to video file
            id: Optional unique identifier for the video
            status: Initial processing status

        Returns:
            Video instance
        """
        file_info = VideoFile(
            filename=path.name,
            file_path=str(path),
            format=path.suffix[1:].upper(),
            file_size=path.stat().st_size,
        )
        processing = VideoProcessingInfo(status=status)
        return cls(
            id=id or uuid4(),
            file_info=file_info,
            processing=processing,
        )
