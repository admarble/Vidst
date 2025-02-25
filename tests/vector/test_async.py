"""Tests for asynchronous vector storage operations."""

import asyncio
from pathlib import Path
import numpy as np
import pytest
import pytest_asyncio

from video_understanding.storage.vector.async_storage import AsyncVectorStorage
from video_understanding.storage.vector.config import VectorStorageConfig
from video_understanding.storage.vector.types import VectorMetadata
from video_understanding.storage.vector.exceptions import StorageOperationError

@pytest_asyncio.fixture
async def async_store(
    temp_dir: Path,
    dimension: int
) -> AsyncVectorStorage:
    """Create async vector store instance."""
    config = VectorStorageConfig(
        dimension=dimension,
        index_path=temp_dir / "async_index.faiss",
        metadata_path=temp_dir / "async_metadata.json"
    )
    return await AsyncVectorStorage.create(config)

@pytest.mark.asyncio
async def test_async_add_embedding(
    async_store: AsyncVectorStorage,
    sample_vector: np.ndarray,
    sample_metadata: VectorMetadata
) -> None:
    """Test async embedding addition."""
    embedding_id = await async_store.add_embedding(
        sample_vector,
        sample_metadata
    )
    assert embedding_id is not None

    # Verify addition
    stored_vector, stored_metadata = await async_store.get_embedding(embedding_id)
    np.testing.assert_array_almost_equal(stored_vector, sample_vector)
    assert stored_metadata == sample_metadata

@pytest.mark.asyncio
async def test_async_batch_add(
    async_store: AsyncVectorStorage,
    sample_vectors: np.ndarray,
    sample_metadata: VectorMetadata
) -> None:
    """Test async batch addition."""
    metadata_list = [sample_metadata for _ in range(len(sample_vectors))]

    embedding_ids = await async_store.batch_add_embeddings(
        sample_vectors,
        metadata_list
    )
    assert len(embedding_ids) == len(sample_vectors)

    # Verify all additions
    for i, embedding_id in enumerate(embedding_ids):
        vector, metadata = await async_store.get_embedding(embedding_id)
        np.testing.assert_array_almost_equal(vector, sample_vectors[i])
        assert metadata == sample_metadata

@pytest.mark.asyncio
async def test_async_search(
    async_store: AsyncVectorStorage,
    sample_vectors: np.ndarray
) -> None:
    """Test async similarity search."""
    # Add vectors
    metadata_list = [
        VectorMetadata(
            type="test",
            timestamp="2024-01-01T00:00:00Z",
            model_version="1.0.0",
            confidence=0.95,
            source_frame=None,
            duration=None
        )
        for _ in range(len(sample_vectors))
    ]
    await async_store.batch_add_embeddings(sample_vectors, metadata_list)

    # Search
    query = sample_vectors[0]
    results = await async_store.search_similar(query, k=5)

    assert len(results) == 5
    assert results[0]["similarity"] > 0.99  # First result should be self

@pytest.mark.asyncio
async def test_async_concurrent_operations(
    async_store: AsyncVectorStorage,
    sample_vectors: np.ndarray,
    sample_metadata: VectorMetadata
) -> None:
    """Test concurrent async operations."""
    # Create multiple concurrent tasks
    tasks = []
    for i in range(5):
        vector = sample_vectors[i]
        tasks.append(
            async_store.add_embedding(vector, sample_metadata)
        )

    # Run concurrently
    embedding_ids = await asyncio.gather(*tasks)
    assert len(embedding_ids) == 5

    # Verify all additions succeeded
    for i, embedding_id in enumerate(embedding_ids):
        vector, metadata = await async_store.get_embedding(embedding_id)
        np.testing.assert_array_almost_equal(vector, sample_vectors[i])
        assert metadata == sample_metadata

@pytest.mark.asyncio
async def test_async_error_handling(
    async_store: AsyncVectorStorage,
    sample_vector: np.ndarray
) -> None:
    """Test async error handling."""
    invalid_metadata = {
        "type": "test",
        "timestamp": "invalid",  # Invalid timestamp
        "model_version": "1.0.0",
        "confidence": None,
        "source_frame": None,
        "duration": None,
    }

    with pytest.raises(StorageOperationError):
        await async_store.add_embedding(
            sample_vector,
            invalid_metadata  # type: ignore
        )

@pytest.mark.asyncio
async def test_async_connection_pool(
    temp_dir: Path,
    dimension: int,
    sample_vector: np.ndarray,
    sample_metadata: VectorMetadata
) -> None:
    """Test async connection pooling."""
    config = VectorStorageConfig(
        dimension=dimension,
        index_path=temp_dir / "pool_index.faiss",
        metadata_path=temp_dir / "pool_metadata.json"
    )

    # Create multiple store instances
    stores = await asyncio.gather(*[
        AsyncVectorStorage.create(config)
        for _ in range(3)
    ])

    # Perform concurrent operations across instances
    tasks = []
    for store in stores:
        tasks.append(
            store.add_embedding(sample_vector, sample_metadata)
        )

    # All operations should succeed
    results = await asyncio.gather(*tasks)
    assert len(results) == len(stores)

    # Verify consistency across instances
    for store in stores:
        size = await store.get_size()
        assert size == len(stores)  # Each store should see all additions

@pytest.mark.asyncio
async def test_async_resource_cleanup(
    temp_dir: Path,
    dimension: int
) -> None:
    """Test async resource cleanup."""
    config = VectorStorageConfig(
        dimension=dimension,
        index_path=temp_dir / "cleanup_index.faiss",
        metadata_path=temp_dir / "cleanup_metadata.json"
    )

    # Create and close store
    store = await AsyncVectorStorage.create(config)
    await store.close()

    # Verify resources are released
    assert store.is_closed()

    # Operations after close should fail
    with pytest.raises(StorageOperationError):
        await store.get_size()

@pytest.mark.asyncio
async def test_async_batch_optimization(
    async_store: AsyncVectorStorage,
    dimension: int
) -> None:
    """Test async batch processing optimization."""
    # Create large batch
    n_vectors = 10000
    vectors = np.random.randn(n_vectors, dimension).astype(np.float32)
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)

    metadata_list = [
        VectorMetadata(
            type="test",
            timestamp="2024-01-01T00:00:00Z",
            model_version="1.0.0",
            confidence=0.95,
            source_frame=None,
            duration=None
        )
        for _ in range(n_vectors)
    ]

    # Process in optimized batches
    start_time = asyncio.get_event_loop().time()
    embedding_ids = await async_store.batch_add_embeddings(
        vectors,
        metadata_list,
        batch_size=1000  # Process in smaller batches
    )
    end_time = asyncio.get_event_loop().time()

    assert len(embedding_ids) == n_vectors
    processing_time = end_time - start_time
    assert processing_time < 60  # Should process within reasonable time
