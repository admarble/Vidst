"""Resource monitoring and quota management for vector storage."""

import asyncio
import logging
import psutil
from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np

from video_understanding.storage.vector.exceptions import ResourceExceededError

logger = logging.getLogger(__name__)

@dataclass
class ResourceQuota:
    """Resource quotas for vector storage."""

    max_memory_bytes: int = 4 * 1024 * 1024 * 1024  # 4GB
    max_vectors: int = 1_000_000
    max_batch_size: int = 10_000
    max_concurrent_searches: int = 100
    max_vector_dim: int = 1024

class ResourceMonitor:
    """Resource monitor for vector storage."""

    def __init__(
        self,
        quota: Optional[ResourceQuota] = None,
        check_interval: float = 1.0
    ) -> None:
        """Initialize resource monitor."""
        self.quota = quota or ResourceQuota()
        self.check_interval = check_interval
        self._monitor_task: Optional[asyncio.Task] = None
        self._vector_count = 0
        self._concurrent_searches = 0
        self._memory_usage = 0
        self._lock = asyncio.Lock()
        self._closed = False
        self._stats: Dict[str, float] = {}

    async def start(self) -> None:
        """Start resource monitoring."""
        if self._closed:
            raise ResourceExceededError("Monitor is closed")

        self._monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop(self) -> None:
        """Stop resource monitoring."""
        self._closed = True
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

    async def _monitor_loop(self) -> None:
        """Monitor resource usage periodically."""
        while not self._closed:
            try:
                await self._update_stats()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error("Resource monitoring failed: %s", e)

    async def _update_stats(self) -> None:
        """Update resource usage statistics."""
        async with self._lock:
            process = psutil.Process()
            memory_info = process.memory_info()

            self._stats.update({
                "memory_rss": memory_info.rss,
                "memory_vms": memory_info.vms,
                "cpu_percent": process.cpu_percent(),
                "vector_count": self._vector_count,
                "concurrent_searches": self._concurrent_searches
            })

            # Check quotas
            if memory_info.rss > self.quota.max_memory_bytes:
                logger.warning(
                    "Memory usage exceeded: %d > %d bytes",
                    memory_info.rss,
                    self.quota.max_memory_bytes
                )

    async def check_vector_add(
        self,
        vectors: np.ndarray,
        raise_on_exceed: bool = True
    ) -> bool:
        """Check if adding vectors would exceed quotas."""
        async with self._lock:
            new_count = self._vector_count + len(vectors)
            if new_count > self.quota.max_vectors:
                if raise_on_exceed:
                    raise ResourceExceededError(
                        f"Vector count would exceed quota: {new_count} > {self.quota.max_vectors}"
                    )
                return False

            # Estimate memory usage
            vector_bytes = vectors.nbytes
            if vector_bytes > self.quota.max_memory_bytes:
                if raise_on_exceed:
                    raise ResourceExceededError(
                        f"Vector memory would exceed quota: {vector_bytes} > {self.quota.max_memory_bytes}"
                    )
                return False

            return True

    async def register_vector_add(self, count: int = 1) -> None:
        """Register addition of vectors."""
        async with self._lock:
            self._vector_count += count

    async def register_vector_remove(self, count: int = 1) -> None:
        """Register removal of vectors."""
        async with self._lock:
            self._vector_count = max(0, self._vector_count - count)

    async def register_search_start(self) -> None:
        """Register start of search operation."""
        async with self._lock:
            self._concurrent_searches += 1
            if self._concurrent_searches > self.quota.max_concurrent_searches:
                self._concurrent_searches -= 1
                raise ResourceExceededError(
                    f"Too many concurrent searches: {self._concurrent_searches}"
                )

    async def register_search_end(self) -> None:
        """Register end of search operation."""
        async with self._lock:
            self._concurrent_searches = max(0, self._concurrent_searches - 1)

    def get_stats(self) -> Dict[str, float]:
        """Get current resource usage statistics."""
        return dict(self._stats)

    @property
    def vector_count(self) -> int:
        """Get current vector count."""
        return self._vector_count

    @property
    def concurrent_searches(self) -> int:
        """Get current number of concurrent searches."""
        return self._concurrent_searches

class ResourceContext:
    """Context manager for resource monitoring."""

    def __init__(
        self,
        monitor: ResourceMonitor,
        operation: str,
        **kwargs
    ) -> None:
        """Initialize resource context."""
        self.monitor = monitor
        self.operation = operation
        self.kwargs = kwargs

    async def __aenter__(self) -> None:
        """Enter resource context."""
        if self.operation == "search":
            await self.monitor.register_search_start()
        elif self.operation == "add":
            vectors = self.kwargs.get("vectors")
            if vectors is not None:
                await self.monitor.check_vector_add(vectors)
                await self.monitor.register_vector_add(len(vectors))

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit resource context."""
        if self.operation == "search":
            await self.monitor.register_search_end()
        elif self.operation == "remove":
            count = self.kwargs.get("count", 1)
            await self.monitor.register_vector_remove(count)
