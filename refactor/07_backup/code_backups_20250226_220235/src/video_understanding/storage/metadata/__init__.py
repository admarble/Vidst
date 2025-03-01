"""Metadata storage module for video understanding."""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TypeVar

T = TypeVar("T", bound="VideoMetadata | SceneMetadata")


class MetadataError(Exception):
    """Base exception for metadata-related errors."""
    pass


@dataclass
class SceneMetadata:
    """Scene metadata container."""

    scene_id: str
    start_time: float
    end_time: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoMetadata:
    """Video metadata container."""

    video_id: str
    title: str
    duration: float
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


class MetadataStore:
    """Storage for video and scene metadata."""

    def __init__(self) -> None:
        self._videos: dict[str, VideoMetadata] = {}

    def add_video(self, metadata: VideoMetadata) -> None:
        """Add or update video metadata."""
        self._videos[metadata.video_id] = metadata

    def get_video(self, video_id: str) -> VideoMetadata:
        """Get video metadata by ID."""
        if video_id not in self._videos:
            raise KeyError(f"Video {video_id} not found")
        return self._videos[video_id]

    def delete_video(self, video_id: str) -> None:
        """Delete video metadata."""
        if video_id in self._videos:
            del self._videos[video_id]

    def list_videos(self) -> list[VideoMetadata]:
        """List all video metadata."""
        return list(self._videos.values())

    def search_videos(
        self,
        tag: str | None = None,
        speaker: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[VideoMetadata]:
        """Search videos by criteria."""
        results = []

        for video in self._videos.values():
            matches = True

            if tag and tag not in video.metadata.get("tags", []):
                matches = False
            if speaker and speaker not in video.metadata.get("speakers", []):
                matches = False
            if start_date and video.created_at < start_date:
                matches = False
            if end_date and video.created_at > end_date:
                matches = False

            if matches:
                results.append(video)

        return results

    def clear(self) -> None:
        """Clear all metadata."""
        self._videos.clear()

    @property
    def size(self) -> int:
        """Get the number of stored video metadata entries."""
        return len(self._videos)


def store_metadata(
    metadata: VideoMetadata | SceneMetadata,
    storage_path: str,
    create_dirs: bool = True,
) -> str:
    """Store metadata to a JSON file.

    Args:
        metadata: The metadata to store
        storage_path: Base directory to store metadata
        create_dirs: Whether to create directories if they don't exist

    Returns:
        Path to the stored metadata file
    """
    if create_dirs:
        os.makedirs(storage_path, exist_ok=True)

    # Convert metadata to dictionary
    metadata_dict = {
        "type": metadata.__class__.__name__,
        "data": {
            k: (v.isoformat() if isinstance(v, datetime) else v)
            for k, v in metadata.__dict__.items()
        },
    }

    # Generate filename
    if isinstance(metadata, VideoMetadata):
        filename = f"video_{metadata.video_id}.json"
    else:  # SceneMetadata
        filename = f"scene_{metadata.start_time}_{metadata.end_time}.json"

    file_path = os.path.join(storage_path, filename)

    # Write metadata to file
    with open(file_path, "w") as f:
        json.dump(metadata_dict, f, indent=2)

    return file_path


def retrieve_metadata(file_path: str, metadata_type: type[T]) -> T:
    """Retrieve metadata from a JSON file.

    Args:
        file_path: Path to the metadata file
        metadata_type: Type of metadata to retrieve (VideoMetadata or SceneMetadata)

    Returns:
        Retrieved metadata object

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file contains invalid metadata
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Metadata file not found: {file_path}")

    with open(file_path) as f:
        metadata_dict = json.load(f)

    if metadata_dict["type"] != metadata_type.__name__:
        raise ValueError(
            f"Metadata type mismatch. Expected {metadata_type.__name__}, "
            f"got {metadata_dict['type']}"
        )

    data = metadata_dict["data"]

    # Convert datetime strings back to datetime objects
    if metadata_type == VideoMetadata:
        if data["created_at"]:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data["processed_at"]:
            data["processed_at"] = datetime.fromisoformat(data["processed_at"])

        # Convert scene dictionaries to SceneMetadata objects
        scenes = []
        for scene_dict in data["scenes"]:
            scenes.append(SceneMetadata(**scene_dict))
        data["scenes"] = scenes

    return metadata_type(**data)


def update_metadata(
    file_path: str, updates: dict[str, Any], metadata_type: type[T]
) -> T:
    """Update an existing metadata file with new values.

    Args:
        file_path: Path to the metadata file
        updates: Dictionary of fields to update
        metadata_type: Type of metadata to update

    Returns:
        Updated metadata object

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file contains invalid metadata
    """
    # First retrieve existing metadata
    metadata = retrieve_metadata(file_path, metadata_type)

    # Update fields
    for key, value in updates.items():
        if hasattr(metadata, key):
            # Handle special cases
            if key == "scenes" and isinstance(metadata, VideoMetadata):
                scenes = []
                for scene_dict in value:
                    scenes.append(SceneMetadata(**scene_dict))
                setattr(metadata, key, scenes)
            elif key in ["created_at", "processed_at"] and value is not None:
                if isinstance(value, str):
                    setattr(metadata, key, datetime.fromisoformat(value))
                else:
                    setattr(metadata, key, value)
            else:
                setattr(metadata, key, value)
        else:
            raise ValueError(f"Invalid field for {metadata_type.__name__}: {key}")

    # Store updated metadata
    store_metadata(metadata, os.path.dirname(file_path))

    return metadata
