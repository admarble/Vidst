"""Tests for vector storage metadata management."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

from video_understanding.storage.vector.metadata import (
    MetadataStore,
    MetadataVersion,
    TypeQuery,
    TimeRangeQuery,
)
from video_understanding.storage.vector.exceptions import (
    MetadataError,
    ValidationError,
)
from video_understanding.storage.vector.types import VectorMetadata

def test_metadata_version_parsing() -> None:
    """Test version string parsing."""
    major, minor, patch = MetadataVersion.parse_version("1.2.3")
    assert major == 1
    assert minor == 2
    assert patch == 3

    with pytest.raises(ValidationError):
        MetadataVersion.parse_version("invalid")

def test_metadata_version_comparison() -> None:
    """Test version comparison."""
    assert MetadataVersion.requires_migration("0.9.0")
    assert not MetadataVersion.requires_migration(MetadataVersion.CURRENT_VERSION)
    assert not MetadataVersion.requires_migration("2.0.0")

def test_metadata_store_init(temp_dir: Path) -> None:
    """Test metadata store initialization."""
    store = MetadataStore(temp_dir / "metadata.json")
    assert store.size == 0
    assert len(store) == 0

def test_metadata_store_add(
    temp_dir: Path,
    sample_metadata: VectorMetadata
) -> None:
    """Test adding metadata."""
    store = MetadataStore(temp_dir / "metadata.json")
    store.add("test_id", sample_metadata)
    assert store.size == 1
    assert "test_id" in store

    # Test duplicate
    with pytest.raises(MetadataError):
        store.add("test_id", sample_metadata)

def test_metadata_store_get(
    temp_dir: Path,
    sample_metadata: VectorMetadata
) -> None:
    """Test getting metadata."""
    store = MetadataStore(temp_dir / "metadata.json")
    store.add("test_id", sample_metadata)

    metadata = store.get("test_id")
    assert metadata == sample_metadata

    with pytest.raises(MetadataError):
        store.get("nonexistent")

def test_metadata_store_delete(
    temp_dir: Path,
    sample_metadata: VectorMetadata
) -> None:
    """Test deleting metadata."""
    store = MetadataStore(temp_dir / "metadata.json")
    store.add("test_id", sample_metadata)
    assert store.size == 1

    store.delete("test_id")
    assert store.size == 0
    assert "test_id" not in store

    with pytest.raises(MetadataError):
        store.delete("nonexistent")

def test_metadata_store_clear(
    temp_dir: Path,
    sample_metadata: VectorMetadata
) -> None:
    """Test clearing metadata."""
    store = MetadataStore(temp_dir / "metadata.json")
    store.add("test_id1", sample_metadata)
    store.add("test_id2", sample_metadata)
    assert store.size == 2

    store.clear()
    assert store.size == 0

def test_metadata_store_persistence(
    temp_dir: Path,
    sample_metadata: VectorMetadata
) -> None:
    """Test metadata persistence."""
    path = temp_dir / "metadata.json"

    # Add data
    store1 = MetadataStore(path)
    store1.add("test_id", sample_metadata)
    store1.save()

    # Load in new instance
    store2 = MetadataStore(path)
    assert store2.size == 1
    assert store2.get("test_id") == sample_metadata

def test_metadata_store_validation(temp_dir: Path) -> None:
    """Test metadata validation."""
    store = MetadataStore(temp_dir / "metadata.json")

    # Missing required fields
    invalid_metadata: VectorMetadata = {  # type: ignore
        "type": "test",
        "timestamp": "invalid",  # Invalid timestamp
        "model_version": "1.0.0",
        "confidence": None,
        "source_frame": None,
        "duration": None,
    }

    with pytest.raises(ValidationError):
        store.add("test_id", invalid_metadata)

def test_metadata_type_query(
    temp_dir: Path,
    sample_metadata: VectorMetadata
) -> None:
    """Test type query."""
    store = MetadataStore(temp_dir / "metadata.json")
    store.add("test_id", sample_metadata)

    # Matching query
    query = TypeQuery("test")
    results = list(store.query(query))
    assert len(results) == 1
    assert results[0][0] == "test_id"
    assert results[0][1] == sample_metadata

    # Non-matching query
    query = TypeQuery("nonexistent")
    results = list(store.query(query))
    assert len(results) == 0

def test_metadata_time_range_query(
    temp_dir: Path,
    sample_metadata: VectorMetadata
) -> None:
    """Test time range query."""
    store = MetadataStore(temp_dir / "metadata.json")

    # Add metadata with different timestamps
    now = datetime.now(timezone.utc)
    metadata1 = dict(sample_metadata)
    metadata1["timestamp"] = now.isoformat()
    metadata2 = dict(sample_metadata)
    metadata2["timestamp"] = (now - timedelta(hours=1)).isoformat()

    store.add("id1", metadata1)  # type: ignore
    store.add("id2", metadata2)  # type: ignore

    # Query full range
    query = TimeRangeQuery(
        start=now - timedelta(hours=2),
        end=now + timedelta(hours=1)
    )
    results = list(store.query(query))
    assert len(results) == 2

    # Query partial range
    query = TimeRangeQuery(
        start=now - timedelta(minutes=30),
        end=now + timedelta(hours=1)
    )
    results = list(store.query(query))
    assert len(results) == 1
    assert results[0][0] == "id1"

def test_metadata_auto_save(
    temp_dir: Path,
    sample_metadata: VectorMetadata
) -> None:
    """Test auto-save functionality."""
    path = temp_dir / "metadata.json"

    # With auto-save
    store1 = MetadataStore(path, auto_save=True)
    store1.add("test_id", sample_metadata)

    # Should be saved automatically
    store2 = MetadataStore(path)
    assert store2.size == 1
    assert store2.get("test_id") == sample_metadata

    # Without auto-save
    store3 = MetadataStore(path, auto_save=False)
    store3.add("test_id2", sample_metadata)

    # Should not be saved
    store4 = MetadataStore(path)
    assert store4.size == 1
    assert "test_id2" not in store4

def test_metadata_file_corruption(temp_dir: Path) -> None:
    """Test handling of corrupted metadata file."""
    path = temp_dir / "metadata.json"

    # Write invalid JSON
    with open(path, "w") as f:
        f.write("invalid json")

    with pytest.raises(MetadataError):
        MetadataStore(path)
