"""Metadata storage module for Video Understanding AI.

This module handles storage and retrieval of video metadata.
"""

import json

# Standard library imports
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Local imports
from ..core.exceptions import StorageError


@dataclass
class VideoBasicInfo:
    """Basic video information.

    Attributes:
        video_id: Unique identifier for the video
        file_path: Path to the video file
        duration: Duration in seconds
    """

    video_id: str
    file_path: Path
    duration: float


@dataclass
class VideoTimestamps:
    """Video timestamp information.

    Attributes:
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    created_at: datetime
    updated_at: datetime


@dataclass
class VideoMetadata:
    """Video metadata container for storing video information.

    Combines basic info, timestamps, and additional metadata.

    Attributes:
        basic_info: Basic video information
        timestamps: Video timestamps
        metadata: Additional metadata dictionary
    """

    basic_info: VideoBasicInfo
    timestamps: VideoTimestamps
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary.

        Returns:
            Dictionary representation of metadata
        """
        data = {
            "video_id": self.basic_info.video_id,
            "file_path": str(self.basic_info.file_path),
            "duration": self.basic_info.duration,
            "created_at": self.timestamps.created_at.isoformat(),
            "updated_at": self.timestamps.updated_at.isoformat(),
            "metadata": self.metadata,
        }
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VideoMetadata":
        """Create metadata from dictionary.

        Args:
            data: Dictionary representation of metadata

        Returns:
            VideoMetadata instance
        """
        basic_info = VideoBasicInfo(
            video_id=data["video_id"],
            file_path=Path(data["file_path"]),
            duration=data["duration"],
        )
        timestamps = VideoTimestamps(
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
        return cls(
            basic_info=basic_info, timestamps=timestamps, metadata=data["metadata"]
        )


class MetadataStore:
    """Storage for video metadata.

    Attributes:
        db_path: Path to metadata database
    """

    def __init__(self, db_path: Path) -> None:
        """Initialize metadata store.

        Args:
            db_path: Path to metadata database

        Raises:
            StorageError: If initialization fails
        """
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Initialize the metadata database.

        Raises:
            StorageError: If initialization fails
        """
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.db_path.exists():
                with open(self.db_path, "w", encoding="utf-8") as f:
                    json.dump({}, f)
        except Exception as e:
            raise StorageError(f"Failed to initialize metadata store: {e}") from e

    def _load_db(self) -> dict[str, dict[str, Any]]:
        """Load metadata database.

        Returns:
            Dictionary of video metadata

        Raises:
            StorageError: If loading fails
        """
        try:
            with open(self.db_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise StorageError(f"Failed to load metadata store: {e}") from e

    def _save_db(self, data: dict[str, dict[str, Any]]) -> None:
        """Save metadata database.

        Args:
            data: Dictionary of video metadata

        Raises:
            StorageError: If saving fails
        """
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise StorageError(f"Failed to save metadata store: {e}") from e

    def store(self, metadata: VideoMetadata) -> None:
        """Store video metadata.

        Args:
            metadata: Video metadata to store

        Raises:
            StorageError: If storage fails
        """
        if not isinstance(metadata, VideoMetadata):
            raise StorageError("Invalid metadata type")

        try:
            db = self._load_db()
            db[metadata.basic_info.video_id] = metadata.to_dict()
            self._save_db(db)
        except Exception as e:
            raise StorageError(f"Failed to store metadata: {e}") from e

    def retrieve(self, video_id: str) -> VideoMetadata | None:
        """Retrieve video metadata.

        Args:
            video_id: Video identifier

        Returns:
            VideoMetadata if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        if not video_id:
            raise StorageError("Invalid video ID")

        try:
            db = self._load_db()
            data = db.get(video_id)
            return VideoMetadata.from_dict(data) if data else None
        except Exception as e:
            raise StorageError(f"Failed to retrieve metadata: {e}") from e

    def update(self, video_id: str, metadata: dict[str, Any]) -> None:
        """Update video metadata.

        Args:
            video_id: Video identifier
            metadata: New metadata dictionary

        Raises:
            StorageError: If update fails
        """
        if not video_id:
            raise StorageError("Invalid video ID")
        if not isinstance(metadata, dict):
            raise StorageError("Invalid metadata type")

        try:
            db = self._load_db()
            if video_id not in db:
                raise StorageError(f"Video {video_id} not found")

            data = db[video_id]
            data["metadata"] = metadata
            data["updated_at"] = datetime.now().isoformat()
            self._save_db(db)
        except Exception as e:
            raise StorageError(f"Failed to update metadata: {e}") from e


def store_metadata(video_id: str, metadata: dict[str, Any]) -> None:
    """Store metadata for a video.

    Args:
        video_id: Video identifier
        metadata: Metadata dictionary

    Raises:
        StorageError: If storage fails
    """
    if not video_id or not video_id.strip():
        raise StorageError("Invalid video ID")
    if not isinstance(metadata, dict):
        raise StorageError("Invalid metadata type")

    try:
        store = MetadataStore(Path("/tmp/metadata.db"))
        store.store(
            VideoMetadata(
                basic_info=VideoBasicInfo(
                    video_id=video_id,
                    file_path=Path(metadata.get("file_path", "")),
                    duration=float(metadata.get("duration", 0.0)),
                ),
                timestamps=VideoTimestamps(
                    created_at=datetime.now(), updated_at=datetime.now()
                ),
                metadata=metadata,
            )
        )
    except Exception as e:
        raise StorageError(f"Failed to store metadata: {e}") from e


def retrieve_metadata(video_id: str) -> dict[str, Any] | None:
    """Retrieve metadata for a video.

    Args:
        video_id: Video identifier

    Returns:
        Metadata dictionary if found, None otherwise

    Raises:
        StorageError: If retrieval fails
    """
    if not video_id or not video_id.strip():
        raise StorageError("Invalid video ID")

    try:
        store = MetadataStore(Path("/tmp/metadata.db"))
        metadata = store.retrieve(video_id)
        return metadata.metadata if metadata else None
    except Exception as e:
        raise StorageError(f"Failed to retrieve metadata: {e}") from e


def update_metadata(video_id: str, metadata: dict[str, Any]) -> None:
    """Update metadata for a video.

    Args:
        video_id: Video identifier
        metadata: New metadata dictionary

    Raises:
        StorageError: If update fails
    """
    if not video_id or not video_id.strip():
        raise StorageError("Invalid video ID")
    if not isinstance(metadata, dict):
        raise StorageError("Invalid metadata type")

    try:
        store = MetadataStore(Path("/tmp/metadata.db"))
        store.update(video_id, metadata)
    except Exception as e:
        raise StorageError(f"Failed to update metadata: {e}") from e
