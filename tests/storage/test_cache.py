"""Unit tests for cache functionality."""

import json
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict

import pytest

from src.core.exceptions import StorageError
from src.storage.cache import Cache


@pytest.fixture
def cache_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for cache files."""
    cache_path = tmp_path / "cache"
    cache_path.mkdir()
    return cache_path


@pytest.fixture
def cache(cache_dir: Path) -> Cache:
    """Create a cache instance with a short TTL for testing."""
    return Cache(cache_dir=cache_dir, ttl=1)  # 1 second TTL for faster testing


def test_cache_initialization(cache_dir: Path):
    """Test cache initialization."""
    cache = Cache(cache_dir=cache_dir)
    assert cache.cache_dir == cache_dir
    assert cache.ttl == 86400  # Default TTL
    assert isinstance(cache.lock, threading.Lock)
    assert isinstance(cache.memory_cache, dict)


def test_cache_set_and_get(cache: Cache):
    """Test basic cache set and get operations."""
    data = {"key": "value"}
    cache.set("test_key", data)

    # Test memory cache
    assert cache.get("test_key") == data

    # Test file cache
    cache_file = cache.cache_dir / "test_key.json"
    assert cache_file.exists()
    with open(cache_file) as f:
        stored_data = json.load(f)
        assert "timestamp" in stored_data
        assert stored_data["data"] == data


def test_cache_expiration(cache: Cache):
    """Test cache entry expiration."""
    data = {"key": "value"}
    cache.set("test_key", data)

    # Wait for TTL to expire
    time.sleep(1.1)

    # Memory cache should expire
    assert cache.get("test_key") is None

    # File cache should be cleaned up
    cache_file = cache.cache_dir / "test_key.json"
    assert not cache_file.exists()


def test_cache_invalid_key(cache: Cache):
    """Test cache operations with invalid keys."""
    # Test setting with invalid key type
    with pytest.raises(StorageError, match="Cache key must be a string"):
        cache.set(123, {"data": "value"})

    # Test getting with invalid key type
    with pytest.raises(StorageError, match="Cache key must be a string"):
        cache.get(123)


def test_cache_clear(cache: Cache):
    """Test clearing the cache."""
    # Set multiple cache entries
    for i in range(3):
        cache.set(f"key_{i}", {"data": f"value_{i}"})

    assert len(cache.memory_cache) == 3
    assert len(list(cache.cache_dir.glob("*.json"))) == 3

    # Clear cache
    cache.clear()

    assert len(cache.memory_cache) == 0
    assert len(list(cache.cache_dir.glob("*.json"))) == 0


def test_cache_cleanup(cache: Cache):
    """Test automatic cache cleanup of expired entries."""
    # Set multiple cache entries
    for i in range(3):
        cache.set(f"key_{i}", {"data": f"value_{i}"})

    # Wait for TTL to expire
    time.sleep(1.1)

    # Trigger cleanup by accessing cache
    cache.cleanup()

    assert len(cache.memory_cache) == 0
    assert len(list(cache.cache_dir.glob("*.json"))) == 0


def test_cache_thread_safety(cache: Cache):
    """Test thread-safe cache operations."""

    def cache_worker():
        for i in range(100):
            cache.set(f"thread_key_{threading.get_ident()}_{i}", {"data": i})
            time.sleep(0.001)  # Small delay to increase chance of race conditions

    # Start multiple threads
    threads = []
    for _ in range(3):
        thread = threading.Thread(target=cache_worker)
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify cache integrity
    assert len(cache.memory_cache) == 300  # 3 threads * 100 entries each


def test_cache_file_errors(cache: Cache, monkeypatch):
    """Test handling of file system errors."""

    # Mock file system errors
    def mock_write_error(*args, **kwargs):
        raise PermissionError("Write access denied")

    monkeypatch.setattr("builtins.open", mock_write_error)

    # Test handling of write errors
    with pytest.raises(StorageError, match="Failed to write cache file"):
        cache.set("test_key", {"data": "value"})


def test_cache_data_corruption(cache: Cache):
    """Test handling of corrupted cache files."""
    # Create corrupted cache file
    cache_file = cache.cache_dir / "corrupted.json"
    cache_file.write_text("invalid json data")

    # Attempt to read corrupted file
    assert cache.get("corrupted") is None


def test_cache_size_limit(cache: Cache):
    """Test cache behavior with large data."""
    # Create large data
    large_data = {"data": "x" * (1024 * 1024)}  # 1MB of data

    # Should handle large data without errors
    cache.set("large_key", large_data)
    retrieved_data = cache.get("large_key")
    assert retrieved_data == large_data
