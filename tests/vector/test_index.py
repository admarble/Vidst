"""Tests for FAISS vector index operations."""

from pathlib import Path
import numpy as np
import pytest
import faiss

from video_understanding.storage.vector.storage import VectorIndex
from video_understanding.storage.vector.exceptions import StorageOperationError

@pytest.fixture
def index(dimension: int) -> VectorIndex:
    """Create a test vector index."""
    return VectorIndex(dimension=dimension)

def test_index_creation(dimension: int) -> None:
    """Test index creation with different types."""
    # Test flat index
    index = VectorIndex(dimension=dimension, index_type="flat")
    assert isinstance(index.index, faiss.IndexFlatL2)

    # Test HNSW index
    index = VectorIndex(dimension=dimension, index_type="hnsw")
    assert isinstance(index.index, faiss.IndexHNSWFlat)

    # Test IVF index
    index = VectorIndex(dimension=dimension, index_type="ivf")
    assert isinstance(index.index, faiss.IndexIVFFlat)

    # Test invalid index type
    with pytest.raises(ValueError):
        VectorIndex(dimension=dimension, index_type="invalid")

def test_index_add(index: VectorIndex, sample_vector: np.ndarray) -> None:
    """Test adding vectors to index."""
    # Add single vector
    vector = sample_vector.reshape(1, -1)
    index.add(vector)
    assert index.size == 1

    # Add batch of vectors
    vectors = np.random.randn(10, index.dimension).astype(np.float32)
    index.add(vectors)
    assert index.size == 11

    # Test adding invalid shape
    with pytest.raises(StorageOperationError):
        index.add(sample_vector.reshape(-1))

def test_index_search(
    index: VectorIndex,
    sample_vectors: np.ndarray
) -> None:
    """Test vector search."""
    # Add vectors
    index.add(sample_vectors)

    # Search with first vector
    query = sample_vectors[0].reshape(1, -1)
    distances, indices = index.search(query, k=5)

    assert distances.shape == (1, 5)
    assert indices.shape == (1, 5)
    assert indices[0][0] == 0  # First result should be the query vector
    assert np.abs(distances[0][0]) < 1e-5  # Distance to self should be ~0

    # Test invalid k
    with pytest.raises(StorageOperationError):
        index.search(query, k=0)

    # Test invalid query shape
    with pytest.raises(StorageOperationError):
        index.search(query.reshape(-1), k=5)

def test_index_persistence(
    temp_dir: Path,
    dimension: int,
    sample_vectors: np.ndarray
) -> None:
    """Test index persistence."""
    path = temp_dir / "test.faiss"

    # Create and save index
    index1 = VectorIndex(dimension=dimension, index_path=path)
    index1.add(sample_vectors)
    index1.save()

    # Load index
    index2 = VectorIndex(dimension=dimension, index_path=path)
    assert index2.size == len(sample_vectors)

    # Compare search results
    query = sample_vectors[0].reshape(1, -1)
    distances1, indices1 = index1.search(query, k=5)
    distances2, indices2 = index2.search(query, k=5)

    np.testing.assert_array_almost_equal(distances1, distances2)
    np.testing.assert_array_equal(indices1, indices2)

def test_index_large_batch(dimension: int) -> None:
    """Test index performance with large batch."""
    index = VectorIndex(dimension=dimension)

    # Create large batch of vectors
    n_vectors = 10000
    vectors = np.random.randn(n_vectors, dimension).astype(np.float32)
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)

    # Add vectors
    index.add(vectors)
    assert index.size == n_vectors

    # Test search performance
    query = vectors[0].reshape(1, -1)
    distances, indices = index.search(query, k=100)
    assert distances.shape == (1, 100)
    assert indices.shape == (1, 100)

def test_index_error_handling(index: VectorIndex) -> None:
    """Test error handling."""
    # Test uninitialized index
    index.index = None
    with pytest.raises(StorageOperationError, match="not initialized"):
        index.add(np.random.randn(1, index.dimension).astype(np.float32))

    with pytest.raises(StorageOperationError, match="not initialized"):
        index.search(
            np.random.randn(1, index.dimension).astype(np.float32),
            k=5
        )

def test_index_save_load_error_handling(temp_dir: Path, dimension: int) -> None:
    """Test save/load error handling."""
    non_existent = temp_dir / "non_existent" / "index.faiss"
    index = VectorIndex(dimension=dimension, index_path=non_existent)

    # Test save to invalid path
    with pytest.raises(StorageOperationError):
        index.save()

    # Test load from non-existent file
    with pytest.raises(StorageOperationError):
        index.load()

    # Test load corrupted file
    corrupted = temp_dir / "corrupted.faiss"
    corrupted.write_bytes(b"corrupted data")
    index = VectorIndex(dimension=dimension, index_path=corrupted)
    with pytest.raises(StorageOperationError):
        index.load()

@pytest.mark.parametrize("index_type", ["flat", "hnsw", "ivf"])
def test_index_types_search(
    index_type: str,
    dimension: int,
    sample_vectors: np.ndarray
) -> None:
    """Test search with different index types."""
    index = VectorIndex(dimension=dimension, index_type=index_type)
    index.add(sample_vectors)

    # Search with first vector
    query = sample_vectors[0].reshape(1, -1)
    distances, indices = index.search(query, k=5)

    assert distances.shape == (1, 5)
    assert indices.shape == (1, 5)
    assert indices[0][0] == 0  # First result should be the query vector
    assert np.abs(distances[0][0]) < 1e-5  # Distance to self should be ~0

def test_index_reuse(
    temp_dir: Path,
    dimension: int,
    sample_vectors: np.ndarray
) -> None:
    """Test index reuse across instances."""
    path = temp_dir / "reuse.faiss"

    # First instance
    index1 = VectorIndex(dimension=dimension, index_path=path)
    index1.add(sample_vectors[:5])
    index1.save()
    assert index1.size == 5

    # Second instance, add more vectors
    index2 = VectorIndex(dimension=dimension, index_path=path)
    assert index2.size == 5
    index2.add(sample_vectors[5:])
    index2.save()
    assert index2.size == 10

    # Third instance, verify all vectors
    index3 = VectorIndex(dimension=dimension, index_path=path)
    assert index3.size == 10

    # Search should find vectors from both additions
    query = sample_vectors[0].reshape(1, -1)
    distances, indices = index3.search(query, k=10)
    assert len(indices[0]) == 10
