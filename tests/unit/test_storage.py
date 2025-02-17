"""Unit tests for storage components (cache and vector storage)."""

import asyncio
import json
import os
import shutil
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, mock_open, patch

import numpy as np
import pytest

from src.core.exceptions import StorageError
from src.storage.cache import Cache
from src.storage.vector import VectorStorage

# ============================================================================
# Cache Tests
# ============================================================================


@pytest.fixture
def temp_cache_dir():
    """Fixture to create a temporary directory for cache testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def cache(temp_cache_dir):
    """Fixture to create a Cache instance with temporary directory."""
    return Cache(cache_dir=temp_cache_dir)


@pytest.fixture
def readonly_cache_dir():
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

    def test_init_default(self):
        """Test default cache initialization."""
        cache = Cache()
        assert cache.ttl == 86400  # Default TTL
        assert cache.cache_dir.exists()
        assert cache.cache_dir.is_dir()

    def test_init_custom(self, temp_cache_dir):
        """Test cache initialization with custom parameters."""
        custom_ttl = 3600
        cache = Cache(cache_dir=temp_cache_dir, ttl=custom_ttl)
        assert cache.ttl == custom_ttl
        assert cache.cache_dir == temp_cache_dir

    def test_set_get_valid(self, cache):
        """Test setting and getting valid cache entries."""
        test_data = {"key1": "value1", "key2": 42}
        cache.set("test_key", test_data)
        result = cache.get("test_key")
        assert result == test_data

    def test_get_nonexistent(self, cache):
        """Test getting non-existent cache entry."""
        assert cache.get("nonexistent") is None

    def test_get_expired(self, cache):
        """Test getting expired cache entry."""
        cache = Cache(ttl=1)  # 1 second TTL
        cache.set("test_key", {"data": "value"})
        time.sleep(1.1)  # Wait for expiration
        assert cache.get("test_key") is None

    def test_invalid_key_type(self, cache):
        """Test error handling for invalid key types."""
        with pytest.raises(StorageError, match="Cache key must be a string"):
            cache.set(123, {"data": "value"})

        with pytest.raises(StorageError, match="Cache key must be a string"):
            cache.get(123)

    def test_invalid_value_type(self, cache):
        """Test error handling for invalid value types."""
        with pytest.raises(StorageError, match="Cache value must be a dictionary"):
            cache.set("test_key", "not_a_dict")

    def test_clear(self, cache):
        """Test clearing all cached data."""
        test_data = {"key1": "value1"}
        cache.set("test_key", test_data)
        cache.clear()
        assert cache.get("test_key") is None

    def test_cleanup(self, cache):
        """Test cleanup of expired entries."""
        cache = Cache(ttl=1)  # 1 second TTL
        cache.set("test_key1", {"data": "value1"})
        time.sleep(1.1)  # Wait for first entry to expire
        cache.set("test_key2", {"data": "value2"})

        cache.cleanup()
        assert cache.get("test_key1") is None
        assert cache.get("test_key2") is not None

    def test_file_corruption(self, cache):
        """Test handling of corrupted cache files."""
        # Create a corrupted cache file
        cache_file = cache.cache_dir / "corrupted.json"
        cache_file.write_text("invalid json content")

        # Attempt to read corrupted file
        with pytest.raises(StorageError, match="Failed to read cache file"):
            cache.get("corrupted")

    def test_permission_errors(self, cache):
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

    def test_file_system_errors(self, cache):
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

    def test_file_read_errors(self, cache):
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

    def test_cleanup_with_invalid_files(self, cache):
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

    def test_concurrent_file_operations(self, cache):
        """Test concurrent file operations."""

        def write_operation():
            for i in range(10):
                cache.set(f"concurrent_key_{i}", {"data": f"value_{i}"})
                time.sleep(0.01)

        def read_operation():
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
    async def test_concurrent_access(self, cache):
        """Test thread safety for concurrent access."""

        async def write_task(key: str, value: Dict[str, Any]):
            cache.set(key, value)
            await asyncio.sleep(0.1)

        async def read_task(key: str):
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

    def test_get_error_handling(self, cache):
        """Test error handling in get method."""
        mock_file = MagicMock()
        mock_file.exists.return_value = True

        # Test general exception in get
        with patch("pathlib.Path.__truediv__", return_value=mock_file):
            with patch("builtins.open", side_effect=Exception("Unexpected error")):
                with pytest.raises(StorageError, match="Failed to read cache file"):
                    cache.get("test_key")

    def test_cleanup_error_handling(self, cache):
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
def vector_storage():
    """Fixture to create a VectorStorage instance."""
    return VectorStorage(dimension=4)  # Using small dimension for testing


class TestVectorStorage:
    """Test suite for VectorStorage implementation."""

    def test_init(self):
        """Test vector storage initialization."""
        storage = VectorStorage(dimension=1536)
        assert storage.dimension == 1536
        assert len(storage.vectors) == 0
        assert len(storage.metadata) == 0

    def test_store_retrieve_valid(self, vector_storage):
        """Test storing and retrieving valid vectors."""
        vector = np.array([1.0, 2.0, 3.0, 4.0])
        metadata = {"description": "test vector"}

        vector_storage.store("test_key", vector, metadata)

        retrieved = vector_storage.retrieve("test_key")
        assert np.array_equal(retrieved, vector)

        retrieved_metadata = vector_storage.get_metadata("test_key")
        assert retrieved_metadata == metadata

    def test_store_invalid_vector(self, vector_storage):
        """Test error handling for invalid vectors."""
        # Test None vector
        with pytest.raises(StorageError, match="Vector cannot be None"):
            vector_storage.store("test_key", None)

        # Test wrong dimension
        wrong_dim = np.array([1.0, 2.0])
        with pytest.raises(StorageError, match="Invalid vector dimension"):
            vector_storage.store("test_key", wrong_dim)

        # Test invalid type
        with pytest.raises(StorageError, match="Vector must be a numpy array"):
            vector_storage.store("test_key", [1.0, 2.0, 3.0, 4.0])

    def test_retrieve_nonexistent(self, vector_storage):
        """Test retrieving non-existent vector."""
        assert vector_storage.retrieve("nonexistent") is None
        assert vector_storage.get_metadata("nonexistent") is None

    def test_search_empty(self, vector_storage):
        """Test search with empty storage."""
        query = np.array([1.0, 2.0, 3.0, 4.0])
        results = vector_storage.search(query)
        assert len(results) == 0

    def test_search_invalid_k(self, vector_storage):
        """Test search with invalid k values."""
        query = np.array([1.0, 2.0, 3.0, 4.0])
        results = vector_storage.search(query, k=0)
        assert len(results) == 0

        results = vector_storage.search(query, k=-1)
        assert len(results) == 0

    def test_search_results(self, vector_storage):
        """Test search results ordering."""
        # Store some test vectors
        vectors = {
            "v1": np.array([1.0, 0.0, 0.0, 0.0]),
            "v2": np.array([0.0, 1.0, 0.0, 0.0]),
            "v3": np.array([1.0, 1.0, 0.0, 0.0]) / np.sqrt(2),
        }

        for key, vector in vectors.items():
            vector_storage.store(key, vector)

        # Search with a query vector
        query = np.array([1.0, 0.0, 0.0, 0.0])
        results = vector_storage.search(query, k=3)

        # Check results order
        assert len(results) == 3
        assert results[0][0] == "v1"  # Most similar
        assert abs(results[0][1] - 1.0) < 1e-6  # Cosine similarity should be 1.0

        # v3 should be more similar to query than v2
        assert results[1][0] == "v3"
        assert results[2][0] == "v2"

    def test_search_with_zero_vectors(self, vector_storage):
        """Test search behavior with zero vectors."""
        # Store a zero vector
        zero_vector = np.zeros(4)
        vector_storage.store("zero", zero_vector)

        # Store a normal vector
        normal_vector = np.array([1.0, 0.0, 0.0, 0.0])
        vector_storage.store("normal", normal_vector)

        # Search with a query vector
        query = np.array([1.0, 0.0, 0.0, 0.0])
        results = vector_storage.search(query, k=2)

        # Zero vector should be excluded from results
        assert len(results) == 1
        assert results[0][0] == "normal"

    def test_search_invalid_query(self, vector_storage):
        """Test search with invalid query vectors."""
        # Test zero query vector
        zero_query = np.zeros(4)
        with pytest.raises(StorageError, match="Cannot normalize zero vector"):
            vector_storage.search(zero_query)

        # Test None query
        with pytest.raises(StorageError, match="Query vector cannot be None"):
            vector_storage.search(None)

        # Test wrong dimension
        wrong_dim = np.array([1.0, 2.0])
        with pytest.raises(StorageError, match="Invalid vector dimension"):
            vector_storage.search(wrong_dim)

    @pytest.mark.asyncio
    async def test_concurrent_access(self, vector_storage):
        """Test thread safety for concurrent access."""

        async def store_task(key: str, value: np.ndarray):
            vector_storage.store(key, value)
            await asyncio.sleep(0.1)

        async def retrieve_task(key: str):
            return vector_storage.retrieve(key)

        # Create test vectors
        vectors = [np.array([float(i), 0.0, 0.0, 0.0]) for i in range(5)]

        # Create concurrent store and retrieve tasks
        store_tasks = [
            store_task(f"key{i}", vector) for i, vector in enumerate(vectors)
        ]
        retrieve_tasks = [retrieve_task(f"key{i}") for i in range(5)]

        # Run tasks concurrently
        await asyncio.gather(*store_tasks)
        results = await asyncio.gather(*retrieve_tasks)

        # Verify results
        for i, (result, original) in enumerate(zip(results, vectors)):
            assert np.array_equal(result, original)

    def test_search_edge_cases(self, vector_storage):
        """Test vector search edge cases."""
        # Store vectors with different magnitudes
        vectors = {
            "small": np.array([1e-10, 0.0, 0.0, 0.0]),
            "large": np.array([1e10, 0.0, 0.0, 0.0]),
            "normal": np.array([1.0, 0.0, 0.0, 0.0]),
        }

        for key, vector in vectors.items():
            vector_storage.store(key, vector)

        # Search with a normal query
        query = np.array([1.0, 0.0, 0.0, 0.0])
        results = vector_storage.search(query, k=3)

        # All vectors should be normalized, so they should all have the same similarity
        assert len(results) == 3
        for key, similarity in results:
            assert abs(similarity - 1.0) < 1e-6

    def test_vector_normalization_edge_cases(self, vector_storage):
        """Test vector normalization edge cases."""
        # Test with moderately small/large vectors (avoiding numerical instability)
        small_vector = np.array([1e-8, 0.0, 0.0, 0.0])
        vector_storage.store("small", small_vector)

        large_vector = np.array([1e8, 0.0, 0.0, 0.0])
        vector_storage.store("large", large_vector)

        # Search with a normal query
        query = np.array([1.0, 0.0, 0.0, 0.0])
        results = vector_storage.search(query, k=2)

        # Both vectors should be normalized and have perfect similarity
        assert len(results) == 2
        for key, similarity in results:
            assert abs(similarity - 1.0) < 1e-6
