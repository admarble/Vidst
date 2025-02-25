"""Unit tests for storage components (cache and vector storage)."""

import asyncio
import os
import tempfile
import threading
import time
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

import numpy as np
import pytest

from video_understanding.core.exceptions import StorageError
from video_understanding.storage.cache import Cache
from video_understanding.storage.vector import VectorMetadata, VectorStorage, VectorStorageConfig

# ============================================================================
# Cache Tests
# ============================================================================


@pytest.fixture
def temp_cache_dir() -> Generator[Path, None, None]:
    """Fixture to create a temporary directory for cache testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def cache(temp_cache_dir: Path) -> Cache:
    """Fixture to create a Cache instance with temporary directory."""
    return Cache(cache_dir=temp_cache_dir)


@pytest.fixture
def readonly_cache_dir() -> Generator[Path, None, None]:
    """Fixture to create a read-only directory for testing permission errors."""
    with tempfile.TemporaryDirectory() as temp_dir:
        dir_path = Path(temp_dir)
        # Create a subdirectory that will be read-only
        readonly_dir = dir_path / "readonly"
        readonly_dir.mkdir()
        # Make it read-only
        os.chmod(readonly_dir, 0o444)
        yield readonly_dir
        # Restore permissions for cleanup
        os.chmod(readonly_dir, 0o777)


class TestCache:
    """Test suite for Cache implementation."""

    def test_init_default(self) -> None:
        """Test default cache initialization."""
        cache = Cache()
        assert cache.ttl == 86400  # Default TTL
        assert cache.cache_dir.exists()
        assert cache.cache_dir.is_dir()

    def test_init_custom(self, temp_cache_dir: Path) -> None:
        """Test cache initialization with custom parameters."""
        custom_ttl = 3600
        cache = Cache(cache_dir=temp_cache_dir, ttl=custom_ttl)
        assert cache.ttl == custom_ttl
        assert cache.cache_dir == temp_cache_dir

    def test_set_get_valid(self, cache: Cache) -> None:
        """Test setting and getting valid cache entries."""
        test_data = {"key1": "value1", "key2": 42}
        cache.set("test_key", test_data)
        result = cache.get("test_key")
        assert result == test_data

    def test_get_nonexistent(self, cache: Cache) -> None:
        """Test getting non-existent cache entry."""
        assert cache.get("nonexistent") is None

    def test_get_expired(self, cache: Cache) -> None:
        """Test getting expired cache entry."""
        cache = Cache(ttl=1)  # 1 second TTL
        cache.set("test_key", {"data": "value"})
        time.sleep(1.1)  # Wait for expiration
        assert cache.get("test_key") is None

    def test_invalid_key_type(self, cache: Cache) -> None:
        """Test error handling for invalid key types."""
        with pytest.raises(StorageError, match="Cache key must be a string"):
            cache.set(123, {"data": "value"})  # type: ignore

        with pytest.raises(StorageError, match="Cache key must be a string"):
            cache.get(123)  # type: ignore

    def test_invalid_value_type(self, cache: Cache) -> None:
        """Test error handling for invalid value types."""
        with pytest.raises(StorageError, match="Cache value must be a dictionary"):
            cache.set("test_key", "not_a_dict")  # type: ignore

    def test_clear(self, cache: Cache) -> None:
        """Test clearing all cached data."""
        test_data = {"key1": "value1"}
        cache.set("test_key", test_data)
        cache.clear()
        assert cache.get("test_key") is None

    def test_cleanup(self, cache: Cache) -> None:
        """Test cleanup of expired entries."""
        cache = Cache(ttl=1)  # 1 second TTL
        cache.set("test_key1", {"data": "value1"})
        time.sleep(1.1)  # Wait for first entry to expire
        cache.set("test_key2", {"data": "value2"})

        cache.cleanup()
        assert cache.get("test_key1") is None
        assert cache.get("test_key2") is not None

    def test_file_corruption(self, cache: Cache) -> None:
        """Test handling of corrupted cache files."""
        # Create a corrupted cache file
        cache_file = cache.cache_dir / "corrupted.json"
        cache_file.write_text("invalid json content")

        # Attempt to read corrupted file
        with pytest.raises(StorageError, match="Failed to read cache file"):
            cache.get("corrupted")

    def test_permission_errors(self, cache: Cache) -> None:
        """Test handling of permission errors."""
        # Mock file for set operation
        mock_file_set = MagicMock()
        mock_file_set.exists.return_value = True

        # Test set operation
        with patch("pathlib.Path.__truediv__", return_value=mock_file_set):
            with patch(
                "builtins.open", side_effect=PermissionError("Permission denied")
            ):
                with pytest.raises(StorageError, match="Failed to write cache file"):
                    cache.set("test_key", {"data": "value"})

        # Test clear operation - glob itself raises error
        with patch(
            "pathlib.Path.glob", side_effect=PermissionError("Permission denied")
        ):
            with pytest.raises(StorageError, match="Failed to clear cache"):
                cache.clear()

        # Test cleanup operation - glob raises error
        with patch(
            "pathlib.Path.glob", side_effect=PermissionError("Permission denied")
        ):
            with pytest.raises(StorageError, match="Failed to cleanup cache"):
                cache.cleanup()

    def test_file_system_errors(self, cache: Cache) -> None:
        """Test handling of various file system errors."""
        mock_file = MagicMock()
        mock_file.exists.return_value = True

        # Test JSON decode error
        with patch("pathlib.Path.__truediv__", return_value=mock_file):
            with patch("builtins.open", mock_open(read_data="invalid json")):
                with pytest.raises(StorageError, match="Failed to read cache file"):
                    cache.get("test_key")

        # Test IO error
        mock_file.exists.return_value = True
        with patch("pathlib.Path.__truediv__", return_value=mock_file):
            with patch("builtins.open", side_effect=IOError):
                with pytest.raises(StorageError, match="Failed to write cache file"):
                    cache.set("test_key", {"data": "value"})

        # Test file not found error
        with patch("pathlib.Path.glob", return_value=[]):
            cache.cleanup()  # Should handle gracefully
            cache.clear()  # Should handle gracefully

    def test_file_read_errors(self, cache: Cache) -> None:
        """Test handling of file read errors."""
        # Create a file that exists but can't be read
        unreadable_file = cache.cache_dir / "unreadable.json"
        unreadable_file.write_text('{"timestamp": 0, "data": {}}')
        os.chmod(unreadable_file, 0o000)

        try:
            # Attempt to read unreadable file
            with pytest.raises(StorageError, match="Failed to read cache file"):
                cache.get("unreadable")
        finally:
            # Restore permissions for cleanup
            os.chmod(unreadable_file, 0o666)

    def test_cleanup_with_invalid_files(self, cache: Cache) -> None:
        """Test cleanup with invalid/unreadable files."""
        # Create an unreadable file
        bad_file = cache.cache_dir / "unreadable.json"
        bad_file.write_text('{"timestamp": 0, "data": {}}')
        os.chmod(bad_file, 0o000)

        try:
            # Cleanup should handle unreadable files gracefully
            cache.cleanup()
        finally:
            # Restore permissions for cleanup
            os.chmod(bad_file, 0o666)

    def test_concurrent_file_operations(self, cache: Cache) -> None:
        """Test concurrent file operations."""

        def write_operation() -> None:
            for i in range(10):
                cache.set(f"concurrent_key_{i}", {"data": f"value_{i}"})
                time.sleep(0.01)

        def read_operation() -> None:
            for i in range(10):
                cache.get(f"concurrent_key_{i}")
                time.sleep(0.01)

        # Create and start threads
        write_thread = threading.Thread(target=write_operation)
        read_thread = threading.Thread(target=read_operation)

        write_thread.start()
        read_thread.start()

        write_thread.join()
        read_thread.join()

    @pytest.mark.asyncio
    async def test_concurrent_access(self, cache: Cache) -> None:
        """Test thread safety for concurrent access."""

        async def write_task(key: str, value: dict[str, Any]) -> None:
            cache.set(key, value)
            await asyncio.sleep(0.1)

        async def read_task(key: str) -> dict[str, Any] | None:
            return cache.get(key)

        # Create concurrent write and read tasks
        write_tasks = [write_task(f"key{i}", {"data": f"value{i}"}) for i in range(5)]
        read_tasks = [read_task(f"key{i}") for i in range(5)]

        # Run tasks concurrently
        await asyncio.gather(*write_tasks)
        results = await asyncio.gather(*read_tasks)

        # Verify results
        for i, result in enumerate(results):
            assert result is not None
            assert result["data"] == f"value{i}"

    def test_get_error_handling(self, cache: Cache) -> None:
        """Test error handling in get method."""
        mock_file = MagicMock()
        mock_file.exists.return_value = True

        # Test general exception in get
        with patch("pathlib.Path.__truediv__", return_value=mock_file):
            with patch("builtins.open", side_effect=Exception("Unexpected error")):
                with pytest.raises(StorageError, match="Failed to read cache file"):
                    cache.get("test_key")

    def test_cleanup_error_handling(self, cache: Cache) -> None:
        """Test error handling in cleanup method."""
        # Create a file that will cause an error during cleanup
        test_file = cache.cache_dir / "error.json"
        test_file.write_text('{"timestamp": 0, "data": {}}')

        # Mock the unlink operation to raise an unexpected error
        with patch("pathlib.Path.unlink", side_effect=Exception("Unexpected error")):
            with pytest.raises(StorageError, match="Failed to cleanup cache"):
                cache.cleanup()


# ============================================================================
# Vector Storage Tests
# ============================================================================


@pytest.fixture
def temp_vector_dir() -> Generator[Path, None, None]:
    """Fixture to create a temporary directory for vector storage testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def vector_storage(temp_vector_dir: Path) -> VectorStorage:
    """Fixture to create a VectorStorage instance with temporary directory."""
    config = VectorStorageConfig(
        dimension=768,  # Using standard BERT dimension
        index_path=temp_vector_dir / "index.faiss",
        metadata_path=temp_vector_dir / "metadata.json",
    )
    return VectorStorage(config)


class TestVectorStorage:
    """Test suite for VectorStorage implementation."""

    def test_init_default(self, temp_vector_dir: Path) -> None:
        """Test default vector storage initialization."""
        config = VectorStorageConfig(
            dimension=768,
            index_path=temp_vector_dir / "index.faiss",
            metadata_path=temp_vector_dir / "metadata.json",
        )
        storage = VectorStorage(config)
        assert storage.config.dimension == 768
        assert storage.config.similarity_threshold == 0.8
        assert storage.config.auto_save is True

    def test_init_custom(self, temp_vector_dir: Path) -> None:
        """Test vector storage initialization with custom parameters."""
        config = VectorStorageConfig(
            dimension=512,
            index_path=temp_vector_dir / "custom_index.faiss",
            metadata_path=temp_vector_dir / "custom_metadata.json",
            similarity_threshold=0.9,
            auto_save=False,
        )
        storage = VectorStorage(config)
        assert storage.config.dimension == 512
        assert storage.config.similarity_threshold == 0.9
        assert storage.config.auto_save is False

    def test_add_retrieve_embedding(self, vector_storage: VectorStorage) -> None:
        """Test adding and retrieving embeddings."""
        # Create test embedding
        embedding = np.random.randn(768).astype(np.float32)
        norm = np.linalg.norm(embedding)
        embedding = (embedding / norm).astype(np.float32)

        metadata: VectorMetadata = {
            "type": "scene",
            "timestamp": "2024-03-20T10:00:00",
            "model_version": "v1.0",
            "confidence": 0.95,
            "source_frame": None,
            "duration": 5.0,
        }

        # Add embedding
        embedding_id = vector_storage.add_embedding(embedding, metadata)

        # Retrieve and verify
        retrieved_embedding, retrieved_metadata = vector_storage.retrieve_embedding(
            embedding_id
        )
        np.testing.assert_array_almost_equal(embedding, retrieved_embedding)
        assert retrieved_metadata == metadata

    def test_search_similar(self, vector_storage: VectorStorage) -> None:
        """Test similarity search functionality."""
        # Create and add test embeddings
        embeddings = []
        metadata_list = []

        for i in range(5):
            embedding = np.random.randn(768).astype(np.float32)
            norm = np.linalg.norm(embedding)
            embedding = (embedding / norm).astype(np.float32)
            embeddings.append(embedding)

            metadata: VectorMetadata = {
                "type": "scene",
                "timestamp": f"2024-03-20T10:0{i}:00",
                "model_version": "v1.0",
                "confidence": 0.9 + i * 0.02,
                "source_frame": None,
                "duration": 5.0,
            }
            metadata_list.append(metadata)

            vector_storage.add_embedding(embedding, metadata)

        # Search with first embedding as query
        results = vector_storage.search_similar(embeddings[0], k=3)

        assert len(results) <= 3
        assert all(isinstance(r["similarity"], float) for r in results)
        assert all(isinstance(r["distance"], float) for r in results)
        assert all(isinstance(r["id"], str) for r in results)
        assert all(isinstance(r["metadata"], dict) for r in results)

    def test_delete_embedding(self, vector_storage: VectorStorage) -> None:
        """Test deleting embeddings."""
        # Add test embedding
        embedding = np.random.randn(768).astype(np.float32)
        norm = np.linalg.norm(embedding)
        embedding = (embedding / norm).astype(np.float32)

        metadata: VectorMetadata = {
            "type": "scene",
            "timestamp": "2024-03-20T10:00:00",
            "model_version": "v1.0",
            "confidence": 0.95,
            "source_frame": None,
            "duration": 5.0,
        }

        embedding_id = vector_storage.add_embedding(embedding, metadata)

        # Delete embedding
        vector_storage.delete_embedding(embedding_id)

        # Verify deletion
        with pytest.raises(StorageError):
            vector_storage.retrieve_embedding(embedding_id)

    def test_clear(self, vector_storage: VectorStorage) -> None:
        """Test clearing all embeddings."""
        # Add test embedding
        embedding = np.random.randn(768).astype(np.float32)
        norm = np.linalg.norm(embedding)
        embedding = (embedding / norm).astype(np.float32)

        metadata: VectorMetadata = {
            "type": "scene",
            "timestamp": "2024-03-20T10:00:00",
            "model_version": "v1.0",
            "confidence": 0.95,
            "source_frame": None,
            "duration": 5.0,
        }

        vector_storage.add_embedding(embedding, metadata)

        # Clear storage
        vector_storage.clear()

        # Verify storage is empty
        results = vector_storage.search_similar(embedding, k=1)
        assert len(results) == 0
