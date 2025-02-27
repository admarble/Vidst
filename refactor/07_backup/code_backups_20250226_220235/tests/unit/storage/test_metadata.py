"""Test module for metadata storage.

This module contains tests for video metadata storage functionality.
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from video_understanding.core.exceptions import StorageError
from video_understanding.storage.metadata import (
    MetadataStore,
    VideoMetadata,
    retrieve_metadata,
    store_metadata,
)

# Test data
SAMPLE_METADATA = {
    "video_id": "test123",
    "file_path": "/test/video.mp4",
    "duration": 10.0,
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
    "metadata": {"title": "Test Video", "tags": ["test", "video"]},
}


@pytest.fixture
def video_metadata():
    """Create a sample VideoMetadata instance."""
    return VideoMetadata(
        video_id="test123",
        file_path=Path("/test/video.mp4"),
        duration=10.0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={"title": "Test Video", "tags": ["test", "video"]},
    )


@pytest.fixture
def metadata_store(tmp_path):
    """Create a MetadataStore instance with temporary database."""
    db_path = tmp_path / "metadata.json"
    return MetadataStore(db_path)


class TestVideoMetadata:
    def test_metadata_creation(self, video_metadata):
        """Test VideoMetadata creation with valid data."""
        assert video_metadata.video_id == "test123"
        assert video_metadata.file_path == Path("/test/video.mp4")
        assert video_metadata.duration == 10.0
        assert isinstance(video_metadata.created_at, datetime)
        assert isinstance(video_metadata.updated_at, datetime)
        assert video_metadata.metadata["title"] == "Test Video"

    def test_to_dict(self, video_metadata):
        """Test conversion of VideoMetadata to dictionary."""
        data = video_metadata.to_dict()
        assert isinstance(data, dict)
        assert data["video_id"] == "test123"
        assert data["file_path"] == "/test/video.mp4"
        assert isinstance(data["created_at"], str)
        assert isinstance(data["updated_at"], str)
        assert data["metadata"]["title"] == "Test Video"

    def test_from_dict(self):
        """Test creation of VideoMetadata from dictionary."""
        metadata = VideoMetadata.from_dict(SAMPLE_METADATA)
        assert metadata.video_id == "test123"
        assert metadata.file_path == Path("/test/video.mp4")
        assert metadata.duration == 10.0
        assert isinstance(metadata.created_at, datetime)
        assert isinstance(metadata.updated_at, datetime)
        assert metadata.metadata["title"] == "Test Video"


class TestMetadataStore:
    def test_store_initialization(self, metadata_store):
        """Test MetadataStore initialization."""
        assert metadata_store.db_path.exists()
        with open(metadata_store.db_path) as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert len(data) == 0

    def test_store_metadata(self, metadata_store, video_metadata):
        """Test storing metadata."""
        metadata_store.store(video_metadata)

        # Verify stored data
        with open(metadata_store.db_path) as f:
            data = json.load(f)
            assert video_metadata.video_id in data
            stored = data[video_metadata.video_id]
            assert stored["file_path"] == str(video_metadata.file_path)
            assert stored["duration"] == video_metadata.duration

    def test_store_invalid_metadata(self, metadata_store):
        """Test storing invalid metadata."""
        with pytest.raises(StorageError):
            metadata_store.store("invalid")

    def test_retrieve_metadata(self, metadata_store, video_metadata):
        """Test retrieving metadata."""
        # Store metadata first
        metadata_store.store(video_metadata)

        # Retrieve and verify
        retrieved = metadata_store.retrieve(video_metadata.video_id)
        assert isinstance(retrieved, VideoMetadata)
        assert retrieved.video_id == video_metadata.video_id
        assert retrieved.file_path == video_metadata.file_path
        assert retrieved.duration == video_metadata.duration

    def test_retrieve_nonexistent(self, metadata_store):
        """Test retrieving nonexistent metadata."""
        retrieved = metadata_store.retrieve("nonexistent")
        assert retrieved is None

    def test_retrieve_invalid_id(self, metadata_store):
        """Test retrieving with invalid video ID."""
        with pytest.raises(StorageError):
            metadata_store.retrieve("")

    def test_update_metadata(self, metadata_store, video_metadata):
        """Test updating metadata."""
        # Store initial metadata
        metadata_store.store(video_metadata)

        # Update metadata
        new_metadata = {"title": "Updated Video", "tags": ["updated"]}
        metadata_store.update(video_metadata.video_id, new_metadata)

        # Verify update
        retrieved = metadata_store.retrieve(video_metadata.video_id)
        assert retrieved.metadata == new_metadata
        assert retrieved.updated_at > video_metadata.updated_at

    def test_update_nonexistent(self, metadata_store):
        """Test updating nonexistent metadata."""
        with pytest.raises(StorageError):
            metadata_store.update("nonexistent", {"title": "New"})

    def test_update_invalid_metadata(self, metadata_store, video_metadata):
        """Test updating with invalid metadata."""
        metadata_store.store(video_metadata)
        with pytest.raises(StorageError):
            metadata_store.update(video_metadata.video_id, "invalid")

    @patch("builtins.open", new_callable=mock_open)
    def test_store_file_error(self, mock_file, metadata_store, video_metadata):
        """Test storing metadata with file error."""
        mock_file.side_effect = OSError("File error")
        with pytest.raises(StorageError):
            metadata_store.store(video_metadata)

    @patch("builtins.open", new_callable=mock_open)
    def test_retrieve_file_error(self, mock_file, metadata_store):
        """Test retrieving metadata with file error."""
        mock_file.side_effect = OSError("File error")
        with pytest.raises(StorageError):
            metadata_store.retrieve("test123")


def test_store_metadata_function(tmp_path):
    """Test the store_metadata convenience function."""
    db_path = tmp_path / "metadata.db"
    with patch("src.storage.metadata.MetadataStore") as mock_store:
        store_metadata("test123", {"title": "Test"})
        mock_store.assert_called_once()
        mock_store.return_value.store.assert_called_once()


def test_retrieve_metadata_function(tmp_path):
    """Test the retrieve_metadata convenience function."""
    db_path = tmp_path / "metadata.db"
    with patch("src.storage.metadata.MetadataStore") as mock_store:
        mock_store.return_value.retrieve.return_value = VideoMetadata(
            video_id="test123",
            file_path=Path("/test/video.mp4"),
            duration=10.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"title": "Test"},
        )
        result = retrieve_metadata("test123")
        assert result == {"title": "Test"}
        mock_store.assert_called_once()
        mock_store.return_value.retrieve.assert_called_once_with("test123")
