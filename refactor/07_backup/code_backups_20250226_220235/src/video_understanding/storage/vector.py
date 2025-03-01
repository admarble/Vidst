"""Vector storage functionality.

Example usage:
    >>> # Initialize storage
    >>> config = VectorStorageConfig(dimension=768)
    >>> store = VectorStorage(config)
    >>>
    >>> # Search for similar embeddings
    >>> query = np.random.randn(768).astype(np.float32)
    >>> # Returns List[SearchResult]
    >>> results = store.search_similar(query, k=5)
    >>>
    >>> # Retrieve specific embedding
    >>> embedding = store.get_embedding("id123")
    >>>
    >>> # Create batch of embeddings
    >>> embeddings = np.random.randn(10, 768).astype(np.float32)
    >>> metadata_list = [
    ...     {
    ...         "id": f"vec_{i}",
    ...         "source": "video_123",
    ...         "timestamp": i * 5.0,
    ...     }
    ...     for i in range(10)
    ... ]
    >>> store.add_batch(embeddings, metadata_list)
"""

# Standard library imports
import json
import logging
import os
from typing import (
    TYPE_CHECKING,
    Optional,
    TypedDict,
    cast,
    Callable,
)
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import faiss
import numpy as np
import numpy.typing as npt

from ..core.exceptions import FileValidationError, StorageError, ValidationError

logger = logging.getLogger(__name__)


class VectorMetadata(TypedDict, total=True):
    """Type definition for vector metadata.

    Required Keys:
        type: Type of the vector (e.g., "frame", "scene", "text")
        timestamp: Generation timestamp in ISO format
        model_version: Version of the model used
        confidence: Optional confidence score [0.0-1.0]
        source_frame: Optional frame number for frame embeddings
        duration: Optional duration in seconds for scene embeddings
    """

    type: str
    timestamp: str
    model_version: str
    confidence: float | None
    source_frame: int | None
    duration: float | None


class SearchResult(TypedDict, total=True):
    """Type definition for search results.

    Keys:
        id: Unique identifier of the found embedding
        distance: L2 distance from query vector
        metadata: Associated metadata of the found embedding
        similarity: Normalized similarity score [0.0-1.0]
    """

    id: str
    distance: float
    metadata: VectorMetadata
    similarity: float


@dataclass
class VectorEmbedding:
    """Vector embedding container for video content analysis.

    A structured container for vector embeddings generated from video content
    analysis. Ensures consistent storage of embeddings and their associated
    metadata.

    Attributes:
        video_id: Unique identifier for the source video
        segment_id: Identifier for the specific video segment
                   (format: "<timestamp>_<type>")
        embedding: Vector embedding array (must be normalized to unit length)
        metadata: Additional metadata about the embedding
    """

    video_id: str
    segment_id: str
    embedding: npt.NDArray[np.float32]
    metadata: VectorMetadata


class VectorStorageError(Exception):
    """Exception raised for vector storage related errors."""


def validate_embedding(embedding: np.ndarray, expected_dim: int) -> None:
    """Validate embedding vector.

    Args:
        embedding: Vector to validate (:class:`numpy.ndarray`)
        expected_dim: Expected dimensionality

    Raises:
        ValidationError: If embedding is invalid
    """
    if not isinstance(embedding, np.ndarray):
        raise ValidationError("Embedding must be a numpy array")

    if embedding.dtype not in (np.float32, np.float64):
        raise ValidationError(
            f"Embedding must be float32 or float64, got {embedding.dtype}"
        )

    if embedding.shape != (expected_dim,):
        raise ValidationError(
            f"Expected {expected_dim} dimensions, got {embedding.shape}"
        )

    if not np.all(np.isfinite(embedding)):
        raise ValidationError("Embedding contains non-finite values")


def validate_metadata(metadata: VectorMetadata) -> None:
    """Validate metadata dictionary.

    Args:
        metadata: Metadata to validate

    Raises:
        ValidationError: If metadata is invalid
    """
    if not isinstance(metadata, dict):
        raise ValidationError("Metadata must be a dictionary")

    required_fields = ["type", "timestamp", "model_version"]
    for field in required_fields:
        if field not in metadata:
            raise ValidationError(f"Missing required metadata field: {field}")

    if not isinstance(metadata["type"], str):
        raise ValidationError("Metadata type must be a string")

    try:
        datetime.fromisoformat(metadata["timestamp"])
    except ValueError as e:
        raise ValidationError("Invalid timestamp format in metadata") from e

    if not isinstance(metadata["model_version"], str):
        raise ValidationError("Model version must be a string")


def validate_vector_store_path(path: Path) -> None:
    """Validate a path for vector storage.

    Args:
        path: Path to validate

    Raises:
        FileValidationError: If path is invalid
    """
    if not path.parent.exists():
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise FileValidationError(f"Failed to create directory {path.parent}: {e}")

    if path.exists() and not os.access(str(path), os.W_OK):
        raise FileValidationError(f"No write permission for {path}")


class VectorStorageConfig:
    """Configuration for VectorStorage.

    Attributes:
        dimension: Dimensionality of vectors to store
        index_path: Path to save/load the FAISS index
        metadata_path: Path to save/load metadata
        similarity_threshold: Minimum similarity score for matches (default: 0.8)
        auto_save: Whether to auto-save after modifications (default: True)
    """

    def __init__(
        self,
        dimension: int,
        index_path: Path | str,
        metadata_path: Path | str,
        similarity_threshold: float = 0.8,
        auto_save: bool = True,
    ) -> None:
        """Initialize VectorStorageConfig.

        Args:
            dimension: Dimensionality of vectors to store
            index_path: Path to save/load the FAISS index
            metadata_path: Path to save/load metadata
            similarity_threshold: Minimum similarity score for matches (default: 0.8)
            auto_save: Whether to auto-save after modifications (default: True)
        """
        self.dimension = dimension
        self.index_path = Path(index_path) if isinstance(index_path, str) else index_path
        self.metadata_path = Path(metadata_path) if isinstance(metadata_path, str) else metadata_path
        self.similarity_threshold = similarity_threshold
        self.auto_save = auto_save
        self._validate()

    def _validate(self) -> None:
        """Validate configuration."""
        if not isinstance(self.dimension, int) or self.dimension <= 0:
            raise ValidationError("Dimension must be a positive integer")
        if not isinstance(self.index_path, Path):
            raise ValidationError("Index path must be a Path object")
        if not isinstance(self.metadata_path, Path):
            raise ValidationError("Metadata path must be a Path object")
        if not isinstance(self.similarity_threshold, float) or not 0 <= self.similarity_threshold <= 1:
            raise ValidationError("Similarity threshold must be a float between 0 and 1")
        if not isinstance(self.auto_save, bool):
            raise ValidationError("Auto save must be a boolean")

        # Validate paths
        validate_vector_store_path(self.index_path)
        validate_vector_store_path(self.metadata_path)

    def __eq__(self, other: object) -> bool:
        """Compare two configurations for equality."""
        if not isinstance(other, VectorStorageConfig):
            return NotImplemented
        return (
            self.dimension == other.dimension
            and self.index_path == other.index_path
            and self.metadata_path == other.metadata_path
            and self.similarity_threshold == other.similarity_threshold
            and self.auto_save == other.auto_save
        )

    def __repr__(self) -> str:
        """Return string representation of configuration."""
        return (
            f"VectorStorageConfig(dimension={self.dimension}, "
            f"index_path={self.index_path}, "
            f"metadata_path={self.metadata_path}, "
            f"similarity_threshold={self.similarity_threshold}, "
            f"auto_save={self.auto_save})"
        )

    def __hash__(self) -> int:
        """Return hash of configuration."""
        return hash((
            self.dimension,
            self.index_path,
            self.metadata_path,
            self.similarity_threshold,
            self.auto_save,
        ))

    @property
    def index_dir(self) -> Path:
        """Get directory containing the index file."""
        return self.index_path.parent

    @property
    def metadata_dir(self) -> Path:
        """Get directory containing the metadata file."""
        return self.metadata_path.parent

    @property
    def index_name(self) -> str:
        """Get name of the index file."""
        return self.index_path.name

    @property
    def metadata_name(self) -> str:
        """Get name of the metadata file."""
        return self.metadata_path.name

    @classmethod
    def from_dict(cls, data: dict) -> "VectorStorageConfig":
        """Create configuration from dictionary."""
        return cls(
            dimension=data["dimension"],
            index_path=data["index_path"],
            metadata_path=data["metadata_path"],
            similarity_threshold=data.get("similarity_threshold", 0.8),
            auto_save=data.get("auto_save", True),
        )

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "dimension": self.dimension,
            "index_path": str(self.index_path),
            "metadata_path": str(self.metadata_path),
            "similarity_threshold": self.similarity_threshold,
            "auto_save": self.auto_save,
        }

    @classmethod
    def create_default(cls, base_dir: Path | str, dimension: int) -> "VectorStorageConfig":
        """Create default configuration.

        Args:
            base_dir: Base directory for storing index and metadata files
            dimension: Dimensionality of vectors to store

        Returns:
            Default configuration
        """
        base_dir = Path(base_dir) if isinstance(base_dir, str) else base_dir
        return cls(
            dimension=dimension,
            index_path=base_dir / "index.faiss",
            metadata_path=base_dir / "metadata.json",
        )

    @classmethod
    def create_from_paths(
        cls,
        dimension: int,
        index_path: Path | str,
        metadata_path: Path | str,
        similarity_threshold: float = 0.8,
        auto_save: bool = True,
    ) -> "VectorStorageConfig":
        """Create configuration from paths.

        Args:
            dimension: Dimensionality of vectors to store
            index_path: Path to save/load the FAISS index
            metadata_path: Path to save/load metadata
            similarity_threshold: Minimum similarity score for matches (default: 0.8)
            auto_save: Whether to auto-save after modifications (default: True)

        Returns:
            Configuration with specified paths
        """
        return cls(
            dimension=dimension,
            index_path=index_path,
            metadata_path=metadata_path,
            similarity_threshold=similarity_threshold,
            auto_save=auto_save,
        )

    @classmethod
    def create_from_config(cls, config: "VectorStorageConfig") -> "VectorStorageConfig":
        """Create configuration from another configuration.

        Args:
            config: Configuration to copy

        Returns:
            Copy of configuration
        """
        return cls(
            dimension=config.dimension,
            index_path=config.index_path,
            metadata_path=config.metadata_path,
            similarity_threshold=config.similarity_threshold,
            auto_save=config.auto_save,
        )

    @classmethod
    def create_from_base_dir(cls, base_dir: Path | str, config: "VectorStorageConfig") -> "VectorStorageConfig":
        """Create configuration from base directory and another configuration.

        Args:
            base_dir: Base directory for storing index and metadata files
            config: Configuration to copy paths from

        Returns:
            Configuration with updated paths
        """
        base_dir = Path(base_dir) if isinstance(base_dir, str) else base_dir
        return cls(
            dimension=config.dimension,
            index_path=base_dir / config.index_name,
            metadata_path=base_dir / config.metadata_name,
            similarity_threshold=config.similarity_threshold,
            auto_save=config.auto_save,
        )


class VectorStorage:
    """Vector storage using FAISS for efficient similarity search.

    This class provides a high-level interface for storing and retrieving vector
    embeddings using FAISS as the underlying search engine. It handles
    persistence, metadata management, and provides convenient search
    functionality.

    The class follows the singleton pattern to ensure only one instance exists.
    """

    _instance: Optional["VectorStorage"] = None
    _config: Optional[VectorStorageConfig] = None

    def __init__(self, config: VectorStorageConfig) -> None:
        """Initialize vector storage.

        Args:
            config: Configuration for the vector storage

        Raises:
            StorageError: If initialization fails
        """
        if VectorStorage._instance is not None:
            raise StorageError(
                "VectorStorage is a singleton. Use get_instance() instead."
            )

        self.config = config
        self.dimension = config.dimension
        self.index_path = config.index_path
        self.metadata_path = config.metadata_path
        self.similarity_threshold = config.similarity_threshold
        self.auto_save = config.auto_save

        # Initialize empty index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.vectors = np.zeros((0, self.dimension), dtype=np.float32)
        self.metadata: dict[str, VectorMetadata] = {}

        # Load existing data if available
        self._load_if_exists()

        VectorStorage._instance = self
        VectorStorage._config = config

    @classmethod
    def get_instance(cls) -> "VectorStorage":
        """Get the singleton instance of VectorStorage.

        Returns:
            The VectorStorage instance

        Raises:
            StorageError: If instance hasn't been initialized
        """
        if cls._instance is None:
            if cls._config is None:
                raise StorageError(
                    "VectorStorage not initialized. Create an instance first."
                )
            cls._instance = cls(cls._config)
        return cls._instance

    @classmethod
    def initialize(cls, config: VectorStorageConfig) -> "VectorStorage":
        """Initialize the singleton instance.

        Args:
            config: Configuration for the vector storage

        Returns:
            The VectorStorage instance

        Raises:
            StorageError: If already initialized
        """
        if cls._instance is not None:
            raise StorageError("VectorStorage already initialized")
        return cls(config)

    def _load_if_exists(self) -> None:
        """Load existing index and metadata if available.

        Raises:
            StorageError: If loading fails
        """
        try:
            if self.index_path.exists():
                try:
                    self.index = cast(
                        faiss.IndexFlatL2, faiss.read_index(str(self.index_path))
                    )
                except Exception as e:
                    raise StorageError("Failed to load FAISS index") from e

            if self.metadata_path.exists():
                try:
                    with open(self.metadata_path, encoding="utf-8") as f:
                        loaded = json.load(f)
                        self.metadata = dict(loaded["metadata"].items())
                        self.vectors = np.array(loaded["vectors"], dtype=np.float32)
                except json.JSONDecodeError as e:
                    raise StorageError("Invalid JSON in metadata file") from e
                except Exception as e:
                    raise StorageError("Failed to load metadata") from e

        except Exception as e:
            raise StorageError("Unexpected error loading vector store") from e

    def save(self) -> None:
        """Save the current index and metadata to disk.

        Raises:
            StorageError: If saving fails
        """
        try:
            # Save FAISS index
            try:
                faiss.write_index(self.index, str(self.index_path))
            except Exception as e:
                raise StorageError(f"Failed to save FAISS index: {e!s}") from e

            # Save metadata
            try:
                with open(self.metadata_path, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "metadata": self.metadata,
                            "vectors": self.vectors.tolist(),
                            "dimension": self.dimension,
                        },
                        f,
                        indent=2,
                    )
            except Exception as e:
                raise StorageError(f"Failed to save metadata: {e!s}") from e

        except StorageError:
            raise
        except Exception as e:
            raise StorageError(f"Unexpected error saving vector store: {e!s}") from e

    def add_embedding(
        self,
        embedding: npt.NDArray[np.float32],
        metadata: VectorMetadata,
        embedding_id: str | None = None,
    ) -> str:
        """Add a new embedding to the store.

        Args:
            embedding: Vector embedding to store
            metadata: Associated metadata dictionary
            embedding_id: Optional custom ID

        Returns:
            ID of the stored embedding

        Raises:
            ValidationError: If embedding or metadata is invalid
            StorageError: If storage fails
        """
        try:
            # Validate inputs
            validate_embedding(embedding, self.dimension)
            validate_metadata(metadata)

            # Generate or validate ID
            if embedding_id is None:
                embedding_id = str(len(self.metadata))
            elif embedding_id in self.metadata:
                raise ValidationError(f"Embedding ID {embedding_id} already exists")

            # Add to FAISS index
            vector = embedding.reshape(1, -1).astype(np.float32)
            self.index.add(vector)  # type: ignore
            self.metadata[embedding_id] = metadata
            self.vectors = np.vstack([self.vectors, embedding])

            if self.auto_save:
                self.save()

            return embedding_id

        except ValidationError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to add embedding: {e}") from e

    def batch_add_embeddings(
        self,
        embeddings: npt.NDArray[np.float32],
        metadata_list: list[VectorMetadata],
        embedding_ids: list[str] | None = None,
    ) -> list[str]:
        """Add multiple embeddings in batch.

        This method efficiently adds multiple embeddings and their metadata
        in a single operation. It's more efficient than adding embeddings
        individually.

        Args:
            embeddings: Matrix of embeddings (shape: (n_embeddings, dimension))
            metadata_list: List of metadata dictionaries
            embedding_ids: Optional list of custom IDs

        Returns:
            List of assigned embedding IDs

        Raises:
            ValidationError: If batch adding fails or inputs are invalid

        Example:
            >>> # Prepare batch
            >>> n_embeddings = 10
            >>> embeddings = np.random.randn(n_embeddings, 768).astype(np.float32)
            >>> metadata_list = [
            ...     {
            ...         "video_id": f"video{i}",
            ...         "timestamp": f"00:0{i}:00",
            ...         "type": "scene"
            ...     }
            ...     for i in range(n_embeddings)
            ... ]
            >>>
            >>> # Add batch
            >>> embedding_ids = store.batch_add_embeddings(
            ...     embeddings=embeddings,
            ...     metadata_list=metadata_list
            ... )
            >>> print(f"Added {len(embedding_ids)} embeddings")

        Notes:
            - More efficient than individual additions
            - Embeddings matrix must be 2D
            - Number of metadata entries must match embeddings
            - Consider memory usage for large batches
        """
        try:
            # Validate inputs
            if len(embeddings) != len(metadata_list):
                raise ValidationError(
                    "Number of embeddings and metadata entries must match"
                )

            if embedding_ids is not None and len(embedding_ids) != len(embeddings):
                raise ValidationError("Number of IDs must match number of embeddings")

            # Generate IDs if not provided
            if embedding_ids is None:
                embedding_ids = [
                    str(len(self.metadata) + i) for i in range(len(embeddings))
                ]

            # Validate all embeddings and metadata
            for emb, meta in zip(embeddings, metadata_list, strict=False):
                validate_embedding(emb, self.dimension)
                validate_metadata(meta)

            # Add to FAISS index
            vectors = embeddings.astype(np.float32)
            self.index.add(vectors)  # type: ignore
            for idx, meta in zip(embedding_ids, metadata_list, strict=False):
                self.metadata[idx] = meta
            self.vectors = np.vstack([self.vectors, embeddings])

            if self.auto_save:
                self.save()

            return embedding_ids

        except ValidationError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to add embeddings in batch: {e}") from e

    def search_similar(
        self,
        query: npt.NDArray[np.float32],
        k: int = 5,
        filter_fn: Callable[[SearchResult], bool] | None = None,
    ) -> list[SearchResult]:
        """Search for similar embeddings.

        Args:
            query: Query vector (shape: (dimension,))
            k: Number of results to return (default: 5)
            filter_fn: Optional function to filter results

        Returns:
            List of SearchResult objects sorted by similarity (highest first)

        Raises:
            ValidationError: If query has wrong shape
            StorageError: If search fails
        """
        try:
            validate_embedding(query, self.dimension)

            # Perform search
            query_vector = query.reshape(1, -1).astype(np.float32)
            if TYPE_CHECKING:
                search_result = self.index.search(query_vector, k, None)  # type: ignore
            else:
                search_result = self.index.search(query_vector, k)
            distances, indices = search_result

            # Process results
            results: list[SearchResult] = []
            for dist, idx in zip(distances[0], indices[0], strict=False):
                if idx == -1:  # No more results
                    break

                similarity = 1.0 / (1.0 + dist)  # Convert distance to similarity
                result = SearchResult(
                    id=str(idx),
                    distance=float(dist),
                    metadata=self.metadata[str(idx)],
                    similarity=similarity,
                )

                if filter_fn is None or filter_fn(result):
                    results.append(result)

            return results

        except ValidationError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to search similar vectors: {e}") from e

    def retrieve_embedding(
        self, embedding_id: str
    ) -> tuple[npt.NDArray[np.float32], VectorMetadata]:
        """Retrieve an embedding and its metadata by ID.

        Args:
            embedding_id: ID of the embedding to retrieve

        Returns:
            Tuple containing:
                - The vector embedding (shape: (dimension,))
                - Associated metadata dictionary

        Raises:
            VectorStorageError: If retrieval fails or ID not found
        """
        try:
            if embedding_id not in self.metadata:
                raise VectorStorageError(f"Embedding ID {embedding_id} not found")

            # Reconstruct embedding from index
            embedding = np.zeros((1, self.dimension), dtype=np.float32)
            self.index.reconstruct(int(embedding_id), embedding.reshape(-1))

            return embedding.reshape(-1), self.metadata[embedding_id]

        except Exception as e:
            logger.error("Failed to retrieve embedding: %s", e)
            raise VectorStorageError(f"Failed to retrieve embedding: {e}") from e

    def delete_embedding(self, embedding_id: str, save: bool = True) -> None:
        """Delete an embedding and its metadata.

        Args:
            embedding_id: ID of the embedding to delete
            save: Whether to save changes to disk (default: True)

        Raises:
            VectorStorageError: If deletion fails or ID not found
        """
        try:
            if embedding_id not in self.metadata:
                raise VectorStorageError(f"Embedding ID {embedding_id} not found")

            # Remove from index and metadata
            self.index.remove_ids(np.array([int(embedding_id)], dtype=np.int64))
            del self.metadata[embedding_id]

            if save and self.auto_save:
                self.save()

        except Exception as e:
            logger.error("Failed to delete embedding: %s", e)
            raise VectorStorageError(f"Failed to delete embedding: {e}") from e

    def clear(self, save: bool = True) -> None:
        """Clear all embeddings and metadata.

        Args:
            save: Whether to save the empty state to disk (default: True)

        Raises:
            VectorStorageError: If clearing fails
        """
        try:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata.clear()
            self.vectors = np.zeros((0, self.dimension), dtype=np.float32)

            if save and self.auto_save:
                self.save()

        except Exception as e:
            logger.error("Failed to clear vector store: %s", e)
            raise VectorStorageError(f"Failed to clear vector store: {e}") from e


def store_embedding(embedding: VectorEmbedding) -> str:
    """Store a single embedding.

    Args:
        embedding: The embedding to store

    Returns:
        The ID of the stored embedding

    Raises:
        StorageError: If storing fails
    """
    try:
        config = VectorStorageConfig(
            dimension=embedding.embedding.shape[0],
            index_path=Path("vectors/index.faiss"),
            metadata_path=Path("vectors/metadata.json"),
        )
        store = VectorStorage(config)
        embedding_id = store.add_embedding(embedding.embedding, embedding.metadata)
        logger.info("Embedding stored with ID: %s", embedding_id)
        return embedding_id
    except Exception as e:
        raise StorageError(f"Failed to store embedding: {e}") from e


def search_similar(
    query_vector: npt.NDArray[np.float32], top_k: int = 5
) -> list[SearchResult]:
    """Search for similar embeddings.

    Args:
        query_vector: The query vector to search with
        top_k: Number of results to return (default: 5)

    Returns:
        List of search results sorted by similarity

    Raises:
        StorageError: If search fails
    """
    try:
        config = VectorStorageConfig(
            dimension=query_vector.shape[0],
            index_path=Path("vectors/index.faiss"),
            metadata_path=Path("vectors/metadata.json"),
        )
        store = VectorStorage(config)
        results = store.search_similar(query_vector, top_k)
        return results
    except Exception as e:
        raise StorageError(f"Failed to search similar embeddings: {e}") from e


def optimize_index() -> None:
    """Optimize the FAISS index for better search performance.

    This function performs optimization operations on the FAISS index to improve
    search performance. It should be called periodically, especially after adding
    many vectors.

    Example:
        >>> from video_understanding.storage.vector import optimize_index
        >>> optimize_index()

    Raises:
        StorageError: If optimization fails
    """
    try:
        # Get the global vector storage instance
        store = VectorStorage.get_instance()

        # Ensure vectors are in correct format
        if store.vectors.shape[0] > 0:
            vectors = np.ascontiguousarray(store.vectors, dtype=np.float32)

            # Train index if needed
            if isinstance(store.index, faiss.IndexIVFFlat):
                if not store.index.is_trained:
                    logger.info("Training FAISS index...")
                    if TYPE_CHECKING:
                        store.index.train(vectors, None)  # type: ignore
                    else:
                        store.index.train(vectors)

            # Add vectors to index if needed
            if store.index.ntotal == 0:
                logger.info("Adding vectors to FAISS index...")
                if TYPE_CHECKING:
                    store.index.add(vectors, None)  # type: ignore
                else:
                    store.index.add(vectors)

        logger.info("Index optimization complete")
    except Exception as e:
        raise StorageError(f"Failed to optimize index: {e}") from e


def retrieve_embedding(
    embedding_id: str,
) -> tuple[npt.NDArray[np.float32], VectorMetadata]:
    """Retrieve a specific embedding and its metadata by ID.

    Args:
        embedding_id: Unique identifier of the embedding to retrieve

    Returns:
        Tuple containing:
            - The embedding vector as a numpy array
            - Associated metadata dictionary

    Example:
        >>> from video_understanding.storage.vector import retrieve_embedding
        >>> vector, metadata = retrieve_embedding("video123_00:01:30_scene")
        >>> print(f"Vector shape: {vector.shape}")
        >>> print(f"Metadata: {metadata}")

    Raises:
        StorageError: If embedding cannot be found or retrieved
    """
    try:
        # Get the global vector storage instance
        store = VectorStorage.get_instance()
        return store.retrieve_embedding(embedding_id)
    except Exception as e:
        raise StorageError(f"Failed to retrieve embedding {embedding_id}: {e}") from e


def search_vectors(
    query: npt.NDArray[np.float32],
    k: int = 5,
    filter_fn: Callable[[SearchResult], bool] | None = None,
) -> list[SearchResult]:
    """Search for similar vectors in the storage.

    Args:
        query: Query vector to search for
        k: Number of results to return (default: 5)
        filter_fn: Optional function to filter results

    Returns:
        List of SearchResult objects containing matches

    Example:
        >>> import numpy as np
        >>> from video_understanding.storage.vector import search_vectors
        >>>
        >>> # Create query vector
        >>> query = np.random.randn(768).astype(np.float32)
        >>> query = query / np.linalg.norm(query)
        >>>
        >>> # Search with custom filter
        >>> def filter_scenes(result: SearchResult) -> bool:
        ...     return result["metadata"]["type"] == "scene"
        >>>
        >>> results = search_vectors(query, k=5, filter_fn=filter_scenes)
        >>> for r in results:
        ...     print(f"Match {r['id']}: {r['similarity']:.3f}")

    Raises:
        StorageError: If search operation fails
    """
    try:
        # Get the global vector storage instance
        store = VectorStorage.get_instance()
        return store.search_similar(query, k, filter_fn)
    except Exception as e:
        raise StorageError(f"Failed to search vectors: {e}") from e
