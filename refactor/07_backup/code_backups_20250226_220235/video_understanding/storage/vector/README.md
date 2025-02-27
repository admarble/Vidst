# Vector Storage Module

High-performance vector storage and similarity search using FAISS.

## Features

- Fast similarity search using FAISS
- Multiple index types (Flat, HNSW, IVF)
- Asynchronous operations
- Connection pooling
- Resource monitoring
- Batch processing
- Metadata management

## Quick Start

```python
from video_understanding.storage.vector import VectorStorage, VectorStorageConfig

# Initialize storage
config = VectorStorageConfig(dimension=768)
store = VectorStorage(config)

# Add vectors
vectors = np.random.randn(10, 768).astype(np.float32)
metadata_list = [
    {
        "type": "frame",
        "timestamp": "2024-01-01T00:00:00Z",
        "model_version": "1.0.0"
    }
    for _ in range(10)
]
store.batch_add_embeddings(vectors, metadata_list)

# Search similar vectors
query = vectors[0]
results = store.search_similar(query, k=5)
```

## Async Usage

```python
import asyncio
from video_understanding.storage.vector import AsyncVectorStorage

async def main():
    store = await AsyncVectorStorage.create(config)
    try:
        results = await store.search_similar(query, k=5)
    finally:
        await store.close()

asyncio.run(main())
```

## Connection Pool

```python
from video_understanding.storage.vector import VectorStoragePool, PoolConfig

async def main():
    pool = VectorStoragePool(
        storage_config=config,
        pool_config=PoolConfig(min_size=2, max_size=10)
    )
    await pool.start()

    store = await pool.acquire()
    try:
        results = await store.search_similar(query, k=5)
    finally:
        await pool.release(store)
        await pool.close()
```

## Resource Management

```python
from video_understanding.storage.vector import ResourceMonitor, ResourceQuota

async def main():
    monitor = ResourceMonitor(
        quota=ResourceQuota(
            max_memory_bytes=4 * 1024**3,  # 4GB
            max_vectors=1_000_000
        )
    )
    await monitor.start()

    async with ResourceContext(monitor, "add", vectors=vectors):
        await store.batch_add_embeddings(vectors, metadata_list)

    await monitor.stop()
```

## Configuration

### Small Dataset (<100K vectors)

```python
config = VectorStorageConfig(
    dimension=768,
    index_type="flat",
    similarity_threshold=0.8,
    max_vectors=100_000
)
```

### Medium Dataset (<1M vectors)

```python
config = VectorStorageConfig(
    dimension=768,
    index_type="hnsw",
    similarity_threshold=0.7,
    max_vectors=1_000_000
)
```

### Large Dataset (>1M vectors)

```python
config = VectorStorageConfig(
    dimension=768,
    index_type="ivf",
    similarity_threshold=0.6,
    max_vectors=10_000_000
)
```

## Performance Tips

1. **Index Type Selection**
   - Use `flat` for small datasets (<100K vectors)
   - Use `hnsw` for medium datasets (<1M vectors)
   - Use `ivf` for large datasets (>1M vectors)

2. **Batch Processing**
   - Use batch operations when possible
   - Optimal batch size: 1000 vectors
   - Monitor memory usage during batch operations

3. **Resource Management**
   - Set appropriate resource quotas
   - Use connection pooling for concurrent access
   - Implement proper cleanup

4. **Memory Usage**
   - Monitor memory with ResourceMonitor
   - Use appropriate index type for dataset size
   - Clean up resources when done

## Dependencies

- Python 3.10+
- FAISS
- NumPy
- psutil

## Installation

```bash
pip install -r requirements.txt
```

## Testing

```bash
pytest tests/vector/
```

## Contributing

1. Follow PEP 8 style guide
2. Add tests for new features
3. Update documentation
4. Run test suite before submitting PR

## License

MIT License
