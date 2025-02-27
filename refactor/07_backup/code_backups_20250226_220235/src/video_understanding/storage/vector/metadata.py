"""Metadata management for vector storage.

This module provides functionality for managing metadata associated with vector
embeddings, including storage, validation, versioning, and querying.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Protocol, TypeVar, Generic

from .types import VectorMetadata
from .exceptions import MetadataError, ValidationError
from .utils import wrap_errors

T = TypeVar('T')

class MetadataVersion:
    """Handles metadata versioning and migrations."""

    CURRENT_VERSION = "1.0.0"

    @staticmethod
    def parse_version(version: str) -> tuple[int, int, int]:
        """Parse version string into components.

        Args:
            version: Version string in format "major.minor.patch"

        Returns:
            Tuple of (major, minor, patch) version numbers

        Raises:
            ValidationError: If version string is invalid
        """
        try:
            major, minor, patch = map(int, version.split('.'))
            return major, minor, patch
        except ValueError as e:
            raise ValidationError(f"Invalid version format: {version}") from e

    @classmethod
    def requires_migration(cls, version: str) -> bool:
        """Check if metadata needs migration.

        Args:
            version: Version string to check

        Returns:
            True if migration is needed
        """
        current = cls.parse_version(cls.CURRENT_VERSION)
        other = cls.parse_version(version)
        return other < current

class MetadataQuery(Protocol[T]):
    """Protocol for metadata query implementations."""

    def matches(self, metadata: VectorMetadata) -> bool:
        """Check if metadata matches query criteria."""
        ...

class TypeQuery(MetadataQuery[str]):
    """Query for matching metadata type."""

    def __init__(self, type_value: str) -> None:
        self.type_value = type_value

    def matches(self, metadata: VectorMetadata) -> bool:
        return metadata["type"] == self.type_value

class TimeRangeQuery(MetadataQuery[tuple[datetime, datetime]]):
    """Query for matching metadata within time range."""

    def __init__(self, start: datetime, end: datetime) -> None:
        self.start = start
        self.end = end

    def matches(self, metadata: VectorMetadata) -> bool:
        try:
            timestamp = datetime.fromisoformat(metadata["timestamp"])
            return self.start <= timestamp <= self.end
        except (KeyError, ValueError):
            return False

class MetadataStore:
    """Manages storage and retrieval of vector metadata.

    This class handles all metadata operations including storage, retrieval,
    querying, and versioning. It ensures metadata consistency and provides
    efficient query capabilities.

    Attributes:
        path: Path to metadata storage file
        auto_save: Whether to automatically save changes
    """

    def __init__(self, path: Path, auto_save: bool = True) -> None:
        """Initialize metadata store.

        Args:
            path: Path to metadata storage file
            auto_save: Whether to automatically save changes
        """
        self.path = path
        self.auto_save = auto_save
        self._metadata: Dict[str, VectorMetadata] = {}
        self._version = MetadataVersion.CURRENT_VERSION
        self._load_if_exists()

    def _load_if_exists(self) -> None:
        """Load metadata from file if it exists."""
        if not self.path.exists():
            return

        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                version = data.get('version', '1.0.0')

                if MetadataVersion.requires_migration(version):
                    self._migrate(version)
                else:
                    self._metadata = data.get('metadata', {})
                    self._version = version
        except Exception as e:
            raise MetadataError(f"Failed to load metadata: {e}") from e

    def _migrate(self, from_version: str) -> None:
        """Migrate metadata from older version.

        Args:
            from_version: Version to migrate from

        Raises:
            MetadataError: If migration fails
        """
        # TODO: Implement migration logic
        raise NotImplementedError("Metadata migration not implemented")

    @wrap_errors(MetadataError)
    def save(self) -> None:
        """Save metadata to file.

        Raises:
            MetadataError: If saving fails
        """
        data = {
            'version': self._version,
            'metadata': self._metadata
        }

        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise MetadataError(f"Failed to save metadata: {e}") from e

    def add(self, id: str, metadata: VectorMetadata) -> None:
        """Add metadata for a vector.

        Args:
            id: Vector ID
            metadata: Vector metadata

        Raises:
            ValidationError: If metadata is invalid
            MetadataError: If operation fails
        """
        from .utils import validate_metadata
        validate_metadata(metadata)

        self._metadata[id] = metadata
        if self.auto_save:
            self.save()

    def get(self, id: str) -> VectorMetadata:
        """Get metadata for a vector.

        Args:
            id: Vector ID

        Returns:
            Vector metadata

        Raises:
            MetadataError: If metadata not found
        """
        try:
            return self._metadata[id]
        except KeyError as e:
            raise MetadataError(f"Metadata not found for ID: {id}") from e

    def delete(self, id: str) -> None:
        """Delete metadata for a vector.

        Args:
            id: Vector ID

        Raises:
            MetadataError: If metadata not found or deletion fails
        """
        try:
            del self._metadata[id]
            if self.auto_save:
                self.save()
        except KeyError as e:
            raise MetadataError(f"Metadata not found for ID: {id}") from e

    def query(self, query: MetadataQuery[Any]) -> Iterator[tuple[str, VectorMetadata]]:
        """Query metadata using query object.

        Args:
            query: Query object implementing MetadataQuery protocol

        Yields:
            Tuples of (id, metadata) for matching entries
        """
        for id, metadata in self._metadata.items():
            if query.matches(metadata):
                yield id, metadata

    def clear(self) -> None:
        """Clear all metadata.

        Raises:
            MetadataError: If operation fails
        """
        self._metadata.clear()
        if self.auto_save:
            self.save()

    @property
    def size(self) -> int:
        """Get number of metadata entries."""
        return len(self._metadata)

    def __len__(self) -> int:
        return self.size

    def __contains__(self, id: str) -> bool:
        return id in self._metadata
