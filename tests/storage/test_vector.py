"""Unit tests for vector storage functionality."""

from threading import Thread
from typing import List, Tuple

import numpy as np
import pytest

from src.core.exceptions import StorageError
from src.storage.vector import VectorStorage


@pytest.fixture
def storage():
    return VectorStorage(dimension=3)


@pytest.fixture
def sample_vector():
    return np.array([1.0, 0.0, 0.0])


@pytest.fixture
def sample_metadata():
    return {"timestamp": 1234, "label": "test"}


def test_storage_initialization():
    """Test vector storage initialization."""
    storage = VectorStorage(dimension=512)
    assert storage.dimension == 512
    assert len(storage.vectors) == 0
    assert len(storage.metadata) == 0


def test_store_vector(storage, sample_vector, sample_metadata):
    """Test storing a vector with metadata."""
    storage.store("test_key", sample_vector, sample_metadata)

    assert "test_key" in storage.vectors
    assert "test_key" in storage.metadata
    np.testing.assert_array_equal(storage.vectors["test_key"], sample_vector)
    assert storage.metadata["test_key"] == sample_metadata


def test_store_invalid_vector(storage):
    """Test storing invalid vectors."""
    # Test None vector
    with pytest.raises(StorageError, match="Vector cannot be None"):
        storage.store("key", None)

    # Test wrong type
    with pytest.raises(StorageError, match="Vector must be a numpy array"):
        storage.store("key", [1, 2, 3])

    # Test wrong dimension
    wrong_dim_vector = np.array([1.0, 0.0])
    with pytest.raises(StorageError, match="Invalid vector dimension"):
        storage.store("key", wrong_dim_vector)


def test_retrieve_vector(storage, sample_vector, sample_metadata):
    """Test retrieving stored vectors."""
    storage.store("test_key", sample_vector, sample_metadata)

    # Test successful retrieval
    retrieved = storage.retrieve("test_key")
    np.testing.assert_array_equal(retrieved, sample_vector)

    # Test non-existent key
    assert storage.retrieve("nonexistent") is None


def test_get_metadata(storage, sample_vector, sample_metadata):
    """Test retrieving metadata."""
    storage.store("test_key", sample_vector, sample_metadata)

    # Test successful retrieval
    retrieved = storage.get_metadata("test_key")
    assert retrieved == sample_metadata

    # Test non-existent key
    assert storage.get_metadata("nonexistent") is None


def test_search_nearest_neighbors(storage):
    """Test searching for nearest neighbors."""
    # Store some test vectors
    vectors = [
        ("v1", np.array([1.0, 0.0, 0.0])),
        ("v2", np.array([0.0, 1.0, 0.0])),
        ("v3", np.array([0.0, 0.0, 1.0])),
        ("v4", np.array([0.7, 0.7, 0.0])),
    ]

    for key, vector in vectors:
        storage.store(key, vector)

    # Search with exact match
    query = np.array([1.0, 0.0, 0.0])
    results = storage.search(query, k=2)
    assert len(results) == 2
    assert results[0][0] == "v1"  # Most similar should be identical vector
    assert results[1][0] == "v4"  # Second most similar should be [0.7, 0.7, 0.0]

    # Test similarity scores
    assert np.isclose(results[0][1], 1.0)  # Perfect match should have similarity 1.0
    assert results[0][1] > results[1][1]  # First result should be more similar


def test_search_invalid_input(storage):
    """Test search with invalid inputs."""
    # Test None vector
    with pytest.raises(StorageError, match="Query vector cannot be None"):
        storage.search(None)

    # Test wrong type
    with pytest.raises(StorageError, match="Query vector must be a numpy array"):
        storage.search([1, 2, 3])

    # Test wrong dimension
    wrong_dim_vector = np.array([1.0, 0.0])
    with pytest.raises(StorageError, match="Invalid vector dimension"):
        storage.search(wrong_dim_vector)

    # Test zero vector
    zero_vector = np.zeros(3)
    with pytest.raises(StorageError, match="Cannot normalize zero vector"):
        storage.search(zero_vector)


def test_search_empty_storage(storage):
    """Test searching in empty storage."""
    query = np.array([1.0, 0.0, 0.0])
    results = storage.search(query)
    assert len(results) == 0


def test_search_k_parameter(storage, sample_vector):
    """Test k parameter in search."""
    # Store multiple vectors
    for i in range(10):
        vector = np.array([float(i), 0.0, 0.0])
        storage.store(f"v{i}", vector)

    # Test k=0
    results = storage.search(sample_vector, k=0)
    assert len(results) == 0

    # Test k=5
    results = storage.search(sample_vector, k=5)
    assert len(results) == 5

    # Test k larger than number of vectors
    results = storage.search(sample_vector, k=20)
    assert len(results) == 10


def test_thread_safety(storage):
    """Test thread-safe operations."""

    def store_vectors():
        for i in range(100):
            vector = np.array([float(i), 0.0, 0.0])
            storage.store(f"thread_key_{i}", vector)

    threads = [Thread(target=store_vectors) for _ in range(3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(storage.vectors) == 300  # 3 threads * 100 vectors each


def test_vector_normalization(storage):
    """Test vector normalization during search."""
    # Store unnormalized vectors
    v1 = np.array([2.0, 0.0, 0.0])  # Will be normalized to [1, 0, 0]
    v2 = np.array([0.0, 3.0, 0.0])  # Will be normalized to [0, 1, 0]

    storage.store("v1", v1)
    storage.store("v2", v2)

    # Search with unnormalized query
    query = np.array([4.0, 0.0, 0.0])  # Will be normalized to [1, 0, 0]
    results = storage.search(query)

    assert results[0][0] == "v1"
    assert np.isclose(results[0][1], 1.0)  # Should be perfect match after normalization
