"""Storage types for the video understanding system."""

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray


@dataclass
class VectorMetadata:
    """Metadata for stored vectors."""

    vector_id: str
    source_id: str  # ID of the source (e.g., video_id, scene_id)
    vector_type: str  # Type of vector (e.g., 'frame', 'audio', 'text')
    timestamp: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorStorageConfig:
    """Configuration for vector storage."""

    dimension: int
    max_vectors: int = 1000000
    similarity_threshold: float = 0.8
    index_type: str = "flat"  # or 'hnsw', 'ivf', etc.
    cache_size: int = 1024 * 1024 * 1024  # 1GB


class VectorStorage:
    """Storage for high-dimensional vectors with metadata."""

    def __init__(self, config: VectorStorageConfig):
        self.config = config
        self._vectors: dict[str, NDArray[np.float32]] = {}
        self._metadata: dict[str, VectorMetadata] = {}

    def add(
        self, vector_id: str, vector: NDArray[np.float32], metadata: VectorMetadata
    ) -> None:
        """Add a vector with metadata to storage."""
        if vector.shape != (self.config.dimension,):
            raise ValueError(
                f"Vector dimension mismatch. Expected {self.config.dimension}, "
                f"got {vector.shape[0]}"
            )

        if len(self._vectors) >= self.config.max_vectors:
            raise ValueError("Vector storage is full")

        self._vectors[vector_id] = vector
        self._metadata[vector_id] = metadata

    def get(self, vector_id: str) -> tuple[NDArray[np.float32], VectorMetadata]:
        """Retrieve a vector and its metadata by ID."""
        if vector_id not in self._vectors:
            raise KeyError(f"Vector {vector_id} not found")

        return self._vectors[vector_id], self._metadata[vector_id]

    def delete(self, vector_id: str) -> None:
        """Delete a vector and its metadata."""
        if vector_id in self._vectors:
            del self._vectors[vector_id]
            del self._metadata[vector_id]

    def search(
        self,
        query_vector: NDArray[np.float32],
        k: int = 10,
        threshold: float | None = None,
    ) -> list[tuple[str, float, VectorMetadata]]:
        """Search for similar vectors."""
        if query_vector.shape != (self.config.dimension,):
            raise ValueError(
                f"Query vector dimension mismatch. Expected {self.config.dimension}, "
                f"got {query_vector.shape[0]}"
            )

        threshold = threshold or self.config.similarity_threshold
        results = []

        for vector_id, vector in self._vectors.items():
            similarity = self._compute_similarity(query_vector, vector)
            if similarity >= threshold:
                results.append((vector_id, similarity, self._metadata[vector_id]))

        # Sort by similarity in descending order
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

    def _compute_similarity(
        self, v1: NDArray[np.float32], v2: NDArray[np.float32]
    ) -> float:
        """Compute cosine similarity between two vectors."""
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        return float(dot_product / (norm_v1 * norm_v2))

    def clear(self) -> None:
        """Clear all vectors and metadata."""
        self._vectors.clear()
        self._metadata.clear()

    @property
    def size(self) -> int:
        """Get the number of stored vectors."""
        return len(self._vectors)
