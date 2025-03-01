"""Type definitions for vector storage functionality.

This module contains all type definitions used across the vector storage package,
including TypedDicts, type aliases, and protocols for better interface definitions.
"""

from typing import TypeVar, Protocol, TypedDict, Optional
import numpy as np
import numpy.typing as npt

# Type variables for generic type parameters
T = TypeVar('T')
VectorT = TypeVar('VectorT', bound=npt.NDArray[np.float32])

# Type aliases for numpy arrays
VectorArray = npt.NDArray[np.float32]
VectorBatch = npt.NDArray[np.float32]

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
    confidence: Optional[float]
    source_frame: Optional[int]
    duration: Optional[float]

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
    def __init__(
        self,
        video_id: str,
        segment_id: str,
        embedding: VectorArray,
        metadata: VectorMetadata
    ) -> None:
        self.video_id = video_id
        self.segment_id = segment_id
        self.embedding = embedding
        self.metadata = metadata

class VectorStore(Protocol):
    """Protocol defining the interface for vector storage implementations."""

    async def add(self, embedding: VectorEmbedding) -> str:
        """Add a single embedding to the store."""
        ...

    async def add_batch(self, embeddings: list[VectorEmbedding]) -> list[str]:
        """Add multiple embeddings efficiently."""
        ...

    async def search(
        self,
        query: VectorArray,
        k: int = 5
    ) -> list[SearchResult]:
        """Search for similar vectors."""
        ...

    async def get(self, id: str) -> VectorEmbedding:
        """Get a specific embedding by ID."""
        ...

    async def delete(self, id: str) -> None:
        """Delete an embedding by ID."""
        ...
