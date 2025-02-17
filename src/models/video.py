"""
Video model representing a video file and its processing state.

This module defines the core Video dataclass used to track video metadata
and processing status throughout the system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Video:
    """
    Represents a video file and its processing metadata.

    Attributes:
        id: Unique identifier for the video
        filename: Original name of the uploaded file
        file_size: Size of the file in bytes
        format: Video format/extension (e.g., 'MP4')
        upload_time: When the video was uploaded
        status: Current processing status
        processing_progress: Optional progress indicator (0-100)
        error_message: Optional error message if processing failed
    """

    filename: str
    file_size: int
    format: str
    id: UUID = field(default_factory=uuid4)
    upload_time: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    processing_progress: Optional[float] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        """Validate the video format and normalize it."""
        if not isinstance(self.id, UUID):
            self.id = UUID(str(self.id))
        self.format = self.format.upper()

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
    def file_path(self) -> str:
        """Get the relative path to the video file"""
        return f"{self.id}/{self.filename}"

    @property
    def is_complete(self) -> bool:
        """Check if video processing is complete."""
        return self.status == "complete"

    @property
    def has_error(self) -> bool:
        """Check if video processing encountered an error."""
        return self.status == "error"

    @classmethod
    def from_path(cls, path: Path, id: UUID, status: str = "pending") -> "Video":
        """Create a Video instance from a file path.

        Args:
            path: Path to video file
            id: Unique identifier for the video
            status: Processing status

        Returns:
            Video instance
        """
        return cls(
            id=id,
            filename=path.name,
            format=path.suffix[1:].upper(),
            status=status,
            file_size=path.stat().st_size,
        )
