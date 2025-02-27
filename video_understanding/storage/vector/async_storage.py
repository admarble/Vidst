"""Asynchronous vector storage implementation."""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast
import numpy as np

from video_understanding.storage.vector.config import VectorStorageConfig
from video_understanding.storage.vector.types import VectorMetadata, VectorEmbedding
from video_understanding.storage.vector.exceptions import StorageOperationError
from video_understanding.storage.vector.storage import VectorIndex
from video_understanding.storage.vector.metadata import MetadataStore

class AsyncVectorStorage:
    """Asynchronous vector storage implementation."""

    def __init__(
        self,
        config: VectorStorageConfig,
        index: Optional[VectorIndex] = None,
        metadata: Optional[MetadataStore] = None
    ) -> None:
        """Initialize async vector storage."""
        self.config = config
        self._index = index or VectorIndex(
            dimension=config.dimension,
            index_type=config.index_type,
            index_path=config.index_path
        )
        self._metadata = metadata or MetadataStore(
            path=config.metadata_path,
            auto_save=config.auto_save
        )
        self._lock = asyncio.Lock()
        self._closed = False

    @classmethod
    async def create(cls, config: VectorStorageConfig) -> "AsyncVectorStorage":
        """Create a new async vector storage instance."""
        instance = cls(config)
        await instance._initialize()
        return instance

    async def _initialize(self) -> None:
        """Initialize storage components."""
        try:
            # Run initialization in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._index.load)
        except Exception as e:
            raise StorageOperationError(f"Failed to initialize storage: {e}")

    async def add_embedding(
        self,
        vector: np.ndarray,
        metadata: VectorMetadata
    ) -> str:
        """Add a single embedding asynchronously."""
        if self._closed:
            raise StorageOperationError("Storage is closed")

        # Generate unique ID
        embedding_id = f"emb_{len(self._metadata)}"

        async with self._lock:
            try:
                # Run vector operations in thread pool
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    self._index.add,
                    vector.reshape(1, -1)
                )

                # Add metadata
                self._metadata.add(embedding_id, metadata)

                return embedding_id
            except Exception as e:
                raise StorageOperationError(f"Failed to add embedding: {e}")

    async def batch_add_embeddings(
        self,
        vectors: np.ndarray,
        metadata_list: List[VectorMetadata],
        batch_size: int = 1000
    ) -> List[str]:
        """Add multiple embeddings in batches asynchronously."""
        if len(vectors) != len(metadata_list):
            raise StorageOperationError(
                "Number of vectors and metadata entries must match"
            )

        embedding_ids = []
        total_vectors = len(vectors)

        for i in range(0, total_vectors, batch_size):
            batch_vectors = vectors[i:i + batch_size]
            batch_metadata = metadata_list[i:i + batch_size]
            batch_ids = [f"emb_{len(self._metadata) + j}" for j in range(len(batch_vectors))]

            async with self._lock:
                try:
                    # Process batch in thread pool
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        None,
                        self._index.add,
                        batch_vectors
                    )

                    # Add metadata
                    for j, embedding_id in enumerate(batch_ids):
                        self._metadata.add(embedding_id, batch_metadata[j])

                    embedding_ids.extend(batch_ids)
                except Exception as e:
                    raise StorageOperationError(f"Failed to add batch: {e}")

        return embedding_ids

    async def get_embedding(
        self,
        embedding_id: str
    ) -> Tuple[np.ndarray, VectorMetadata]:
        """Get embedding by ID asynchronously."""
        if self._closed:
            raise StorageOperationError("Storage is closed")

        try:
            # Get metadata
            metadata = self._metadata.get(embedding_id)

            # Get vector index
            index = int(embedding_id.split("_")[1])
            vector = await self._get_vector_by_index(index)

            return vector, metadata
        except Exception as e:
            raise StorageOperationError(f"Failed to get embedding: {e}")

    async def _get_vector_by_index(self, index: int) -> np.ndarray:
        """Get vector by index from FAISS."""
        # This is a placeholder - actual implementation would depend on
        # how vectors are stored and retrieved in the FAISS index
        raise NotImplementedError

    async def search_similar(
        self,
        query: np.ndarray,
        k: int = 5,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors asynchronously."""
        if self._closed:
            raise StorageOperationError("Storage is closed")

        threshold = threshold or self.config.similarity_threshold

        try:
            # Run search in thread pool
            loop = asyncio.get_event_loop()
            distances, indices = await loop.run_in_executor(
                None,
                lambda: self._index.search(query.reshape(1, -1), k)
            )

            # Filter by threshold
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                similarity = 1.0 - distance
                if similarity >= threshold:
                    embedding_id = f"emb_{idx}"
                    metadata = self._metadata.get(embedding_id)
                    results.append({
                        "id": embedding_id,
                        "similarity": similarity,
                        "metadata": metadata
                    })

            return results
        except Exception as e:
            raise StorageOperationError(f"Failed to search: {e}")

    async def get_size(self) -> int:
        """Get storage size asynchronously."""
        if self._closed:
            raise StorageOperationError("Storage is closed")
        return self._index.size

    async def close(self) -> None:
        """Close storage and release resources."""
        if not self._closed:
            async with self._lock:
                try:
                    # Save state
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self._index.save)
                    await loop.run_in_executor(None, self._metadata.save)
                    self._closed = True
                except Exception as e:
                    raise StorageOperationError(f"Failed to close storage: {e}")

    def is_closed(self) -> bool:
        """Check if storage is closed."""
        return self._closed
