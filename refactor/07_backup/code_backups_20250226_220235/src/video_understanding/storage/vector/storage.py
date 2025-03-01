"""Vector storage implementation using FAISS.

This module provides the core vector storage functionality, including FAISS index
management, connection pooling, and high-level storage operations.
"""

import asyncio
import contextlib
from pathlib import Path
from typing import AsyncIterator, Dict, List, Optional, Tuple, cast
import numpy as np
import faiss

from .types import VectorMetadata, SearchResult, VectorEmbedding, VectorArray
from .config import VectorStorageConfig
from .metadata import MetadataStore
from .exceptions import (
    StorageOperationError,
    ValidationError,
    ResourceExhaustedError,
    ConnectionError,
)
from .utils import validate_embedding, wrap_errors

# Update type definition
IndexType = faiss.Index | faiss.IndexFlatL2 | faiss.IndexHNSWFlat | faiss.IndexIVFFlat

class VectorIndex:
    """Low-level FAISS index operations.

    This class handles direct interactions with the FAISS index, including
    creation, loading, saving, and vector operations.

    Attributes:
        dimension: Vector dimension
        index_type: Type of FAISS index
        index_path: Path to save/load index
    """

    def __init__(
        self,
        dimension: int,
        index_type: str = "flat",
        index_path: Optional[Path] = None
    ) -> None:
        """Initialize vector index.

        Args:
            dimension: Vector dimension
            index_type: Type of FAISS index
            index_path: Optional path to save/load index
        """
        self.dimension = dimension
        self.index_type = index_type
        self.index_path = index_path
        self.index: Optional[IndexType] = None
        self._create_index()

    def _create_index(self) -> None:
        """Create FAISS index based on configuration."""
        try:
            if self.index_type == "flat":
                self.index = faiss.IndexFlatL2(self.dimension)
            elif self.index_type == "hnsw":
                self.index = faiss.IndexHNSWFlat(self.dimension, 32)
            elif self.index_type == "ivf":
                quantizer = faiss.IndexFlatL2(self.dimension)
                self.index = faiss.IndexIVFFlat(
                    quantizer, self.dimension, 100, faiss.METRIC_L2
                )
                if not self.index.is_trained:
                    # type: ignore[attr-defined, call-arg] # FAISS-specific method
                    self.index.train(np.zeros((1, self.dimension), dtype=np.float32))
            else:
                raise ValueError(f"Unsupported index type: {self.index_type}")

            if self.index_path and self.index_path.exists():
                self.load()
        except Exception as e:
            raise StorageOperationError(f"Failed to create index: {e}") from e

    def add(self, x: np.ndarray) -> None:
        """Add vectors to index.

        Args:
            x: Vectors to add (shape: (n_vectors, dimension))

        Raises:
            StorageOperationError: If addition fails
        """
        if self.index is None:
            raise StorageOperationError("Index not initialized")

        try:
            # type: ignore[attr-defined, call-arg] # FAISS-specific method
            self.index.add(x)
        except Exception as e:
            raise StorageOperationError(f"Failed to add vectors: {e}") from e

    def search(
        self, x: np.ndarray, k: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Search for similar vectors.

        Args:
            x: Query vector(s) (shape: (n_queries, dimension))
            k: Number of results per query

        Returns:
            Tuple of (distances, indices)

        Raises:
            StorageOperationError: If search fails
        """
        if self.index is None:
            raise StorageOperationError("Index not initialized")

        try:
            # type: ignore[attr-defined, call-arg] # FAISS-specific method
            distances, indices = self.index.search(x, k)
            return cast(np.ndarray, distances), cast(np.ndarray, indices)
        except Exception as e:
            raise StorageOperationError(f"Failed to search vectors: {e}") from e

    def save(self) -> None:
        """Save index to disk.

        Raises:
            StorageOperationError: If saving fails
        """
        if self.index is None or self.index_path is None:
            return

        try:
            faiss.write_index(self.index, str(self.index_path))
        except Exception as e:
            raise StorageOperationError(f"Failed to save index: {e}") from e

    def load(self) -> None:
        """Load index from disk.

        Raises:
            StorageOperationError: If loading fails
        """
        if self.index_path is None:
            return

        try:
            self.index = faiss.read_index(str(self.index_path))
        except Exception as e:
            raise StorageOperationError(f"Failed to load index: {e}") from e

    @property
    def size(self) -> int:
        """Get number of vectors in index."""
        return 0 if self.index is None else self.index.ntotal

    def __len__(self) -> int:
        return self.size

class ConnectionPool:
    """Manages pool of vector index connections.

    This class handles the lifecycle of vector index instances, including
    creation, cleanup, and health checks.

    Attributes:
        config: Vector storage configuration
        max_connections: Maximum number of connections
        min_connections: Minimum number of connections
    """

    def __init__(
        self,
        config: VectorStorageConfig,
        max_connections: int = 10,
        min_connections: int = 1
    ) -> None:
        """Initialize connection pool.

        Args:
            config: Vector storage configuration
            max_connections: Maximum number of connections
            min_connections: Minimum number of connections
        """
        self.config = config
        self.max_connections = max_connections
        self.min_connections = min_connections
        self._available: asyncio.Queue[VectorIndex] = asyncio.Queue()
        self._in_use: Dict[VectorIndex, asyncio.Task] = {}
        self._lock = asyncio.Lock()
        self._closed = False

    async def initialize(self) -> None:
        """Initialize connection pool.

        Raises:
            ConnectionError: If initialization fails
        """
        try:
            async with self._lock:
                for _ in range(self.min_connections):
                    index = VectorIndex(
                        dimension=self.config.dimension,
                        index_type=self.config.index_type,
                        index_path=self.config.index_path
                    )
                    await self._available.put(index)
        except Exception as e:
            raise ConnectionError(f"Failed to initialize pool: {e}") from e

    async def acquire(self) -> VectorIndex:
        """Acquire a vector index from the pool.

        Returns:
            Vector index instance

        Raises:
            ResourceExhaustedError: If pool is exhausted
            ConnectionError: If acquisition fails
        """
        if self._closed:
            raise ConnectionError("Pool is closed")

        try:
            # Try to get an available connection
            try:
                return await asyncio.wait_for(
                    self._available.get(), timeout=1.0
                )
            except asyncio.TimeoutError:
                pass

            # Create new connection if possible
            async with self._lock:
                if len(self._in_use) < self.max_connections:
                    index = VectorIndex(
                        dimension=self.config.dimension,
                        index_type=self.config.index_type,
                        index_path=self.config.index_path
                    )
                    return index

            # Wait for available connection
            return await self._available.get()
        except Exception as e:
            if isinstance(e, asyncio.TimeoutError):
                raise ResourceExhaustedError("Connection pool exhausted")
            raise ConnectionError(f"Failed to acquire connection: {e}") from e

    async def release(self, index: VectorIndex) -> None:
        """Release a vector index back to the pool.

        Args:
            index: Vector index to release

        Raises:
            ConnectionError: If release fails
        """
        if self._closed:
            return

        try:
            if task := self._in_use.pop(index, None):
                task.cancel()
            await self._available.put(index)
        except Exception as e:
            raise ConnectionError(f"Failed to release connection: {e}") from e

    async def close(self) -> None:
        """Close all connections in the pool."""
        self._closed = True
        while not self._available.empty():
            index = await self._available.get()
            index.save()

        for index, task in self._in_use.items():
            task.cancel()
            index.save()

        self._in_use.clear()

class VectorStorage:
    """High-level vector storage interface.

    This class provides the main interface for vector storage operations,
    coordinating between the vector index and metadata store.

    Attributes:
        config: Vector storage configuration
        metadata: Metadata store instance
        pool: Connection pool instance
    """

    def __init__(self, config: VectorStorageConfig) -> None:
        """Initialize vector storage.

        Args:
            config: Vector storage configuration
        """
        self.config = config
        self.metadata = MetadataStore(config.metadata_path, config.auto_save)
        self.pool = ConnectionPool(config)
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize storage.

        Raises:
            StorageOperationError: If initialization fails
        """
        if self._initialized:
            return

        try:
            async with self._lock:
                if not self._initialized:
                    await self.pool.initialize()
                    self._initialized = True
        except Exception as e:
            raise StorageOperationError(f"Failed to initialize storage: {e}") from e

    @contextlib.asynccontextmanager
    async def _get_index(self) -> AsyncIterator[VectorIndex]:
        """Get vector index from pool.

        Yields:
            Vector index instance
        """
        index = await self.pool.acquire()
        try:
            yield index
        finally:
            await self.pool.release(index)

    async def add(self, embedding: VectorEmbedding) -> str:
        """Add a single embedding.

        Args:
            embedding: Vector embedding to add

        Returns:
            ID of added embedding

        Raises:
            ValidationError: If embedding is invalid
            StorageOperationError: If addition fails
        """
        # Validate embedding
        validate_embedding(embedding.embedding, self.config.dimension)

        try:
            # Generate ID and add metadata
            embedding_id = f"{embedding.video_id}_{embedding.segment_id}"
            self.metadata.add(embedding_id, embedding.metadata)

            # Add to index
            async with self._get_index() as index:
                vector = embedding.embedding.reshape(1, -1)
                index.add(vector)
                if self.config.auto_save:
                    index.save()

            return embedding_id
        except Exception as e:
            raise StorageOperationError(f"Failed to add embedding: {e}") from e

    async def add_batch(
        self, embeddings: List[VectorEmbedding]
    ) -> List[str]:
        """Add multiple embeddings efficiently.

        Args:
            embeddings: List of embeddings to add

        Returns:
            List of assigned IDs

        Raises:
            ValidationError: If any embedding is invalid
            StorageOperationError: If addition fails
        """
        if not embeddings:
            return []

        try:
            # Generate IDs and prepare vectors
            embedding_ids = []
            vectors = []

            for emb in embeddings:
                # Validate embedding
                validate_embedding(emb.embedding, self.config.dimension)

                # Generate ID and add metadata
                embedding_id = f"{emb.video_id}_{emb.segment_id}"
                self.metadata.add(embedding_id, emb.metadata)
                embedding_ids.append(embedding_id)
                vectors.append(emb.embedding)

            # Add to index
            async with self._get_index() as index:
                vectors_array = np.stack(vectors)
                index.add(vectors_array)
                if self.config.auto_save:
                    index.save()

            return embedding_ids
        except Exception as e:
            raise StorageOperationError(f"Failed to add embeddings: {e}") from e

    async def search(
        self, query: VectorArray, k: int = 5
    ) -> List[SearchResult]:
        """Search for similar vectors.

        Args:
            query: Query vector
            k: Number of results to return

        Returns:
            List of search results

        Raises:
            ValidationError: If query is invalid
            StorageOperationError: If search fails
        """
        # Validate query
        validate_embedding(query, self.config.dimension)

        try:
            # Search index
            async with self._get_index() as index:
                distances, indices = index.search(
                    query.reshape(1, -1), k
                )

            # Process results
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx == -1:  # No more results
                    break

                embedding_id = str(idx)
                metadata = self.metadata.get(embedding_id)
                similarity = 1.0 / (1.0 + dist)  # Convert distance to similarity

                if similarity >= self.config.similarity_threshold:
                    results.append(SearchResult(
                        id=embedding_id,
                        distance=float(dist),
                        metadata=metadata,
                        similarity=similarity
                    ))

            return results
        except Exception as e:
            raise StorageOperationError(f"Failed to search vectors: {e}") from e

    async def get(self, id: str) -> VectorEmbedding:
        """Get a specific embedding.

        Args:
            id: Embedding ID

        Returns:
            Vector embedding

        Raises:
            StorageOperationError: If retrieval fails
        """
        try:
            # Get metadata
            metadata = self.metadata.get(id)

            # Get vector from index
            async with self._get_index() as index:
                if index.index is None:
                    raise StorageOperationError("Index not initialized")

                vector = np.zeros((1, self.config.dimension), dtype=np.float32)
                # type: ignore[attr-defined, call-arg] # FAISS-specific method
                index.index.reconstruct(int(id), vector.reshape(-1))

            # Parse ID components
            video_id, segment_id = id.split('_', 1)

            return VectorEmbedding(
                video_id=video_id,
                segment_id=segment_id,
                embedding=vector.reshape(-1),
                metadata=metadata
            )
        except Exception as e:
            raise StorageOperationError(f"Failed to get embedding: {e}") from e

    async def delete(self, id: str) -> None:
        """Delete an embedding.

        Args:
            id: Embedding ID

        Raises:
            StorageOperationError: If deletion fails
        """
        try:
            # Delete from metadata
            self.metadata.delete(id)

            # Delete from index
            async with self._get_index() as index:
                if index.index is None:
                    raise StorageOperationError("Index not initialized")

                # type: ignore[attr-defined, call-arg] # FAISS-specific method
                index.index.remove_ids(np.array([int(id)], dtype=np.int64))
                if self.config.auto_save:
                    index.save()
        except Exception as e:
            raise StorageOperationError(f"Failed to delete embedding: {e}") from e

    async def close(self) -> None:
        """Close storage and release resources."""
        await self.pool.close()

    async def __aenter__(self) -> "VectorStorage":
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
