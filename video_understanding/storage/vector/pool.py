"""Vector storage connection pool implementation."""

import asyncio
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

from video_understanding.storage.vector.config import VectorStorageConfig
from video_understanding.storage.vector.async_storage import AsyncVectorStorage
from video_understanding.storage.vector.exceptions import StorageOperationError

logger = logging.getLogger(__name__)

class PoolConfig:
    """Configuration for connection pool."""

    def __init__(
        self,
        min_size: int = 2,
        max_size: int = 10,
        max_idle_time: int = 300,  # 5 minutes
        max_lifetime: int = 3600,  # 1 hour
        health_check_interval: int = 60,  # 1 minute
    ) -> None:
        """Initialize pool configuration."""
        self.min_size = min_size
        self.max_size = max_size
        self.max_idle_time = max_idle_time
        self.max_lifetime = max_lifetime
        self.health_check_interval = health_check_interval

class PoolConnection:
    """Connection pool entry."""

    def __init__(self, store: AsyncVectorStorage) -> None:
        """Initialize pool connection."""
        self.store = store
        self.created_at = datetime.now()
        self.last_used_at = self.created_at
        self.in_use = False
        self.health_check_failed = False

class VectorStoragePool:
    """Connection pool for vector storage."""

    def __init__(
        self,
        storage_config: VectorStorageConfig,
        pool_config: Optional[PoolConfig] = None
    ) -> None:
        """Initialize connection pool."""
        self.storage_config = storage_config
        self.pool_config = pool_config or PoolConfig()
        self._connections: Dict[str, PoolConnection] = {}
        self._available_ids: Set[str] = set()
        self._lock = asyncio.Lock()
        self._closed = False
        self._health_check_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the connection pool."""
        if self._closed:
            raise StorageOperationError("Pool is closed")

        # Initialize minimum connections
        async with self._lock:
            for _ in range(self.pool_config.min_size):
                await self._create_connection()

        # Start health check task
        self._health_check_task = asyncio.create_task(self._health_check_loop())

    async def _create_connection(self) -> str:
        """Create a new connection."""
        store = await AsyncVectorStorage.create(self.storage_config)
        conn_id = f"conn_{len(self._connections)}"
        self._connections[conn_id] = PoolConnection(store)
        self._available_ids.add(conn_id)
        return conn_id

    async def acquire(self) -> AsyncVectorStorage:
        """Acquire a connection from the pool."""
        if self._closed:
            raise StorageOperationError("Pool is closed")

        async with self._lock:
            # Try to get an available connection
            while True:
                if self._available_ids:
                    conn_id = self._available_ids.pop()
                    conn = self._connections[conn_id]

                    # Check if connection is still valid
                    if await self._validate_connection(conn):
                        conn.in_use = True
                        conn.last_used_at = datetime.now()
                        return conn.store

                    # Remove invalid connection
                    del self._connections[conn_id]

                # Create new connection if possible
                if len(self._connections) < self.pool_config.max_size:
                    conn_id = await self._create_connection()
                    conn = self._connections[conn_id]
                    conn.in_use = True
                    self._available_ids.remove(conn_id)
                    return conn.store

                # Wait for a connection to become available
                await asyncio.sleep(0.1)

    async def release(self, store: AsyncVectorStorage) -> None:
        """Release a connection back to the pool."""
        if self._closed:
            return

        async with self._lock:
            # Find connection by store instance
            for conn_id, conn in self._connections.items():
                if conn.store is store:
                    conn.in_use = False
                    conn.last_used_at = datetime.now()
                    self._available_ids.add(conn_id)
                    return

    async def _validate_connection(self, conn: PoolConnection) -> bool:
        """Validate a connection."""
        # Check lifetime
        if (datetime.now() - conn.created_at).total_seconds() > self.pool_config.max_lifetime:
            return False

        # Check idle time
        if (datetime.now() - conn.last_used_at).total_seconds() > self.pool_config.max_idle_time:
            return False

        # Check health
        if conn.health_check_failed:
            return False

        return True

    async def _health_check_loop(self) -> None:
        """Run periodic health checks."""
        while not self._closed:
            try:
                await self._run_health_checks()
                await asyncio.sleep(self.pool_config.health_check_interval)
            except Exception as e:
                logger.error("Health check failed: %s", e)

    async def _run_health_checks(self) -> None:
        """Run health checks on all connections."""
        async with self._lock:
            for conn_id, conn in list(self._connections.items()):
                if not conn.in_use:
                    try:
                        # Basic health check
                        size = await conn.store.get_size()
                        conn.health_check_failed = False
                    except Exception:
                        conn.health_check_failed = True
                        if conn_id in self._available_ids:
                            self._available_ids.remove(conn_id)

    async def close(self) -> None:
        """Close the connection pool."""
        if self._closed:
            return

        self._closed = True

        # Cancel health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        # Close all connections
        async with self._lock:
            for conn in self._connections.values():
                try:
                    await conn.store.close()
                except Exception as e:
                    logger.error("Failed to close connection: %s", e)

            self._connections.clear()
            self._available_ids.clear()

    @property
    def size(self) -> int:
        """Get current pool size."""
        return len(self._connections)

    @property
    def available(self) -> int:
        """Get number of available connections."""
        return len(self._available_ids)

    @property
    def in_use(self) -> int:
        """Get number of connections in use."""
        return len(self._connections) - len(self._available_ids)
