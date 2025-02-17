"""Cache implementation for storing intermediate results."""

import json
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

from src.core.exceptions import StorageError


class Cache:
    """Cache for storing intermediate processing results."""

    def __init__(self, cache_dir: Path = None, ttl: int = 86400):
        """Initialize cache.

        Args:
            cache_dir: Directory to store cache files
            ttl: Time to live in seconds (default: 24 hours)
        """
        self.cache_dir = cache_dir or Path("cache")
        self.ttl = ttl
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def lock(self) -> threading.Lock:
        """Get the thread lock.

        Returns:
            The thread lock
        """
        return self._lock

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise

        Raises:
            StorageError: If key is not a string
        """
        if not isinstance(key, str):
            raise StorageError("Cache key must be a string")

        # Check memory cache first
        with self.lock:
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                if time.time() - entry["timestamp"] < self.ttl:
                    return entry["data"]
                del self.memory_cache[key]

        # Check file cache
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    entry = json.load(f)
                    if time.time() - entry["timestamp"] < self.ttl:
                        # Update memory cache
                        with self.lock:
                            self.memory_cache[key] = entry
                        return entry["data"]
                    cache_file.unlink()
            except Exception as e:
                raise StorageError(f"Failed to read cache file: {str(e)}")

        return None

    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache

        Raises:
            StorageError: If key is not a string or value is not a dictionary
        """
        if not isinstance(key, str):
            raise StorageError("Cache key must be a string")

        if not isinstance(value, dict):
            raise StorageError("Cache value must be a dictionary")

        entry = {"timestamp": time.time(), "data": value}

        # Update memory cache
        with self.lock:
            self.memory_cache[key] = entry

        # Update file cache
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(entry, f)
        except PermissionError as e:
            raise StorageError(f"Failed to write cache file: {str(e)}")
        except Exception as e:
            raise StorageError(f"Failed to write cache file: {str(e)}")

    def clear(self) -> None:
        """Clear all cached data."""
        # Clear memory cache
        with self.lock:
            self.memory_cache.clear()

        # Clear file cache
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                except PermissionError:
                    continue
        except Exception as e:
            raise StorageError(f"Failed to clear cache: {str(e)}")

    def cleanup(self) -> None:
        """Remove expired entries from cache."""
        current_time = time.time()

        # Clean memory cache
        with self.lock:
            expired_keys = [
                key
                for key, entry in self.memory_cache.items()
                if current_time - entry["timestamp"] >= self.ttl
            ]
            for key in expired_keys:
                del self.memory_cache[key]

        # Clean file cache
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file) as f:
                        entry = json.load(f)
                        if current_time - entry["timestamp"] >= self.ttl:
                            cache_file.unlink()
                except (PermissionError, json.JSONDecodeError):
                    continue
        except Exception as e:
            raise StorageError(f"Failed to cleanup cache: {str(e)}")
