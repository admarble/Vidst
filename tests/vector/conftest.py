"""Test fixtures for vector storage tests."""

import os
import tempfile
from pathlib import Path
from typing import AsyncIterator, Iterator
import numpy as np
import pytest
import pytest_asyncio
from datetime import datetime, timezone

from video_understanding.storage.vector.types import VectorMetadata, VectorEmbedding
from video_understanding.storage.vector.config import VectorStorageConfig

@pytest.fixture
def dimension() -> int:
    """Vector dimension for tests."""
    return 768

@pytest.fixture
def temp_dir() -> Iterator[Path]:
    """Temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def config(temp_dir: Path, dimension: int) -> VectorStorageConfig:
    """Test configuration."""
    return VectorStorageConfig(
        dimension=dimension,
        index_path=temp_dir / "index.faiss",
        metadata_path=temp_dir / "metadata.json",
        index_type="flat",
        similarity_threshold=0.8,
        max_vectors=1000,
        cache_size_bytes=1024 * 1024,  # 1MB
        auto_save=True
    )

@pytest.fixture
def sample_vector(dimension: int) -> np.ndarray:
    """Sample vector for tests."""
    vector = np.random.randn(dimension).astype(np.float32)
    return vector / np.linalg.norm(vector)  # Normalize

@pytest.fixture
def sample_vectors(dimension: int) -> np.ndarray:
    """Sample vectors for batch tests."""
    vectors = np.random.randn(10, dimension).astype(np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / norms  # Normalize

@pytest.fixture
def sample_metadata() -> VectorMetadata:
    """Sample metadata for tests."""
    return VectorMetadata(
        type="test",
        timestamp=datetime.now(timezone.utc).isoformat(),
        model_version="1.0.0",
        confidence=0.95,
        source_frame=None,
        duration=None
    )

@pytest.fixture
def sample_embedding(
    sample_vector: np.ndarray,
    sample_metadata: VectorMetadata
) -> VectorEmbedding:
    """Sample embedding for tests."""
    return VectorEmbedding(
        video_id="test_video",
        segment_id="test_segment",
        embedding=sample_vector,
        metadata=sample_metadata
    )

@pytest.fixture
def sample_embeddings(
    sample_vectors: np.ndarray,
    sample_metadata: VectorMetadata
) -> list[VectorEmbedding]:
    """Sample embeddings for batch tests."""
    return [
        VectorEmbedding(
            video_id=f"test_video_{i}",
            segment_id=f"test_segment_{i}",
            embedding=vector,
            metadata=sample_metadata
        )
        for i, vector in enumerate(sample_vectors)
    ]

@pytest_asyncio.fixture
async def storage_paths(temp_dir: Path) -> AsyncIterator[tuple[Path, Path]]:
    """Paths for storage tests."""
    index_path = temp_dir / "test_index.faiss"
    metadata_path = temp_dir / "test_metadata.json"
    yield index_path, metadata_path
    # Cleanup
    if index_path.exists():
        os.unlink(index_path)
    if metadata_path.exists():
        os.unlink(metadata_path)

@pytest.fixture
def env_vars(storage_paths: tuple[Path, Path]) -> Iterator[None]:
    """Environment variables for config tests."""
    index_path, metadata_path = storage_paths
    original = dict(os.environ)
    os.environ.update({
        "VECTOR_STORAGE_DIMENSION": "768",
        "VECTOR_STORAGE_INDEX_TYPE": "flat",
        "VECTOR_STORAGE_INDEX_PATH": str(index_path),
        "VECTOR_STORAGE_METADATA_PATH": str(metadata_path),
        "VECTOR_STORAGE_SIMILARITY_THRESHOLD": "0.8",
        "VECTOR_STORAGE_MAX_VECTORS": "1000",
        "VECTOR_STORAGE_CACHE_SIZE_BYTES": "1048576",
        "VECTOR_STORAGE_AUTO_SAVE": "true"
    })
    yield
    os.environ.clear()
    os.environ.update(original)
