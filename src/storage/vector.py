"""Vector storage implementation for embeddings."""

import threading
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.core.exceptions import StorageError


class VectorStorage:
    """Manages storage and retrieval of vector embeddings."""

    def __init__(self, dimension: int = 1536):
        """Initialize vector storage.

        Args:
            dimension: Dimension of vectors to store
        """
        self.dimension = dimension
        self.vectors: Dict[str, np.ndarray] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def store(
        self, key: str, vector: np.ndarray, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store a vector with optional metadata.

        Args:
            key: Unique identifier for the vector
            vector: The vector to store
            metadata: Optional metadata associated with the vector

        Raises:
            StorageError: If vector is None, has invalid dimensions, or is not normalized
        """
        if vector is None:
            raise StorageError("Vector cannot be None")

        if not isinstance(vector, np.ndarray):
            raise StorageError("Vector must be a numpy array")

        if vector.shape != (self.dimension,):
            raise StorageError("Invalid vector dimension")

        with self.lock:
            self.vectors[key] = vector.copy()
            if metadata:
                self.metadata[key] = metadata

    def retrieve(self, key: str) -> Optional[np.ndarray]:
        """Retrieve a vector by key.

        Args:
            key: Key of vector to retrieve

        Returns:
            The vector if found, None otherwise
        """
        with self.lock:
            vector = self.vectors.get(key)
            return vector.copy() if vector is not None else None

    def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a vector.

        Args:
            key: Key of vector to get metadata for

        Returns:
            Metadata if found, None otherwise
        """
        with self.lock:
            return self.metadata.get(key)

    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        """Find k nearest neighbors to query vector.

        Args:
            query_vector: Vector to search for
            k: Number of nearest neighbors to return (if k <= 0, returns empty list)

        Returns:
            List of (key, similarity) tuples for k nearest neighbors

        Raises:
            StorageError: If query vector is None, has invalid dimensions, or is not normalized
        """
        if k <= 0:
            return []

        if query_vector is None:
            raise StorageError("Query vector cannot be None")

        if not isinstance(query_vector, np.ndarray):
            raise StorageError("Query vector must be a numpy array")

        if query_vector.shape != (self.dimension,):
            raise StorageError("Invalid vector dimension")

        # Normalize query vector
        query_norm = np.linalg.norm(query_vector)
        if query_norm == 0:
            raise StorageError("Cannot normalize zero vector")
        query_vector = query_vector / query_norm

        with self.lock:
            if not self.vectors:
                return []

            similarities = []
            for key, vector in self.vectors.items():
                # Normalize vector
                vector_norm = np.linalg.norm(vector)
                if vector_norm == 0:
                    continue
                normalized_vector = vector / vector_norm

                # Compute cosine similarity
                similarity = float(np.dot(query_vector, normalized_vector))
                similarities.append((key, similarity))

            return sorted(similarities, key=lambda x: x[1], reverse=True)[:k]
