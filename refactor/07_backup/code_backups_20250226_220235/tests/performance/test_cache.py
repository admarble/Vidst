"""Performance tests for the caching system."""

import random
import string

import pytest

from video_understanding.storage.cache import Cache
from tests.utils.base_test import BasePerformanceTest


class TestCachePerformance(BasePerformanceTest):
    """Test suite for cache performance."""

    @pytest.fixture(autouse=True)
    def setup_cache(self):
        """Set up cache for testing."""
        self.cache = Cache(
            cache_dir=self.config.cache.cache_dir,
            ttl_seconds=self.config.cache.ttl_seconds,
            max_memory_items=self.config.cache.max_memory_items,
            max_size_mb=self.config.cache.max_size_mb,
        )

        # Create test data directory
        self.config.cache.cache_dir.mkdir(parents=True, exist_ok=True)

        yield

        # Cleanup
        with self.cleanup_context() as cleanup_errors:
            try:
                # Remove all cache files
                for cache_file in self.config.cache.cache_dir.glob("*"):
                    try:
                        cache_file.unlink()
                    except Exception as e:
                        cleanup_errors.append(f"Failed to delete {cache_file}: {e!s}")

                # Remove cache directory
                self.config.cache.cache_dir.rmdir()
            except Exception as e:
                cleanup_errors.append(f"Failed to cleanup cache directory: {e!s}")

    def generate_test_data(self, size_kb: int) -> dict:
        """Generate test data of approximately specified size."""
        # Generate random string data
        chars = string.ascii_letters + string.digits
        data_string = "".join(random.choice(chars) for _ in range(size_kb * 1024))

        return {
            "id": f"test_{size_kb}kb",
            "data": data_string,
            "metadata": {"size": size_kb, "timestamp": "2024-01-01T00:00:00Z"},
        }

    def test_write_performance(self):
        """Test cache write performance with different data sizes."""
        test_sizes = [1, 10, 100, 1000]  # sizes in KB

        for size_kb in test_sizes:
            test_data = self.generate_test_data(size_kb)

            # Test write performance
            with self.assert_performance(f"write_{size_kb}kb"):
                self.cache.set(f"test_key_{size_kb}", test_data)

    def test_read_performance(self):
        """Test cache read performance with different data sizes."""
        test_sizes = [1, 10, 100, 1000]  # sizes in KB

        # First write test data
        for size_kb in test_sizes:
            test_data = self.generate_test_data(size_kb)
            self.cache.set(f"test_key_{size_kb}", test_data)

        # Test read performance
        for size_kb in test_sizes:
            with self.assert_performance(f"read_{size_kb}kb"):
                for _ in range(100):  # Do multiple reads to get better metrics
                    value = self.cache.get(f"test_key_{size_kb}")
                    assert (
                        value is not None
                    ), f"Failed to read {size_kb}KB data from cache"

    def test_cache_eviction(self):
        """Test performance of cache eviction under memory pressure."""
        # Fill cache to its limit
        total_items = self.config.cache.max_memory_items
        item_size_kb = 100  # 100KB per item

        # Write items until we hit the limit
        with self.assert_performance("cache_fill"):
            for i in range(total_items):
                test_data = self.generate_test_data(item_size_kb)
                self.cache.set(f"fill_key_{i}", test_data)

        # Now write more items to trigger eviction
        with self.assert_performance("cache_eviction"):
            for i in range(total_items, total_items + 100):
                test_data = self.generate_test_data(item_size_kb)
                self.cache.set(f"evict_key_{i}", test_data)

        # Verify we're still within memory limits
        self.assert_no_errors()

    def test_concurrent_operations(self):
        """Test cache performance under concurrent operations."""
        import queue
        import threading

        results_queue = queue.Queue()
        error_queue = queue.Queue()

        def worker(worker_id: int):
            try:
                # Each worker does a mix of reads and writes
                for i in range(100):
                    # Write operation
                    test_data = self.generate_test_data(10)  # 10KB data
                    self.cache.set(f"worker_{worker_id}_key_{i}", test_data)

                    # Read operation
                    value = self.cache.get(f"worker_{worker_id}_key_{i}")
                    assert (
                        value is not None
                    ), f"Worker {worker_id} failed to read key {i}"

                results_queue.put(f"Worker {worker_id} completed successfully")
            except Exception as e:
                error_queue.put(f"Worker {worker_id} failed: {e!s}")

        # Start multiple threads
        with self.assert_performance("concurrent_operations"):
            threads = []
            for i in range(4):  # Use 4 concurrent threads
                thread = threading.Thread(target=worker, args=(i,))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

        # Check for any errors
        while not error_queue.empty():
            self.record_error("ConcurrencyError", error_queue.get())

        self.assert_no_errors()
