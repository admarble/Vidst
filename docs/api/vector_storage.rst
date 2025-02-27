Vector Storage API
================

The vector storage module provides high-performance vector storage and similarity search functionality using FAISS.

Core Components
-------------

.. module:: video_understanding.storage.vector
   :synopsis: Vector storage functionality

.. autoclass:: VectorStorage
   :members:
   :undoc-members:
   :show-inheritance:

   The main vector storage class providing high-level operations.

   Example::

      >>> from video_understanding.storage.vector import VectorStorage, VectorStorageConfig
      >>>
      >>> # Initialize storage
      >>> config = VectorStorageConfig(dimension=768)
      >>> store = VectorStorage(config)
      >>>
      >>> # Add vectors
      >>> vectors = np.random.randn(10, 768).astype(np.float32)
      >>> metadata_list = [
      ...     {
      ...         "type": "frame",
      ...         "timestamp": "2024-01-01T00:00:00Z",
      ...         "model_version": "1.0.0"
      ...     }
      ...     for _ in range(10)
      ... ]
      >>> store.batch_add_embeddings(vectors, metadata_list)
      >>>
      >>> # Search similar vectors
      >>> query = vectors[0]
      >>> results = store.search_similar(query, k=5)
      >>> for r in results:
      ...     print(f"Match {r['id']}: {r['similarity']:.3f}")

Asynchronous Storage
------------------

.. autoclass:: AsyncVectorStorage
   :members:
   :undoc-members:
   :show-inheritance:

   Asynchronous interface for vector storage operations.

   Example::

      >>> import asyncio
      >>> from video_understanding.storage.vector import AsyncVectorStorage
      >>>
      >>> async def example():
      ...     store = await AsyncVectorStorage.create(config)
      ...
      ...     # Add vectors asynchronously
      ...     embedding_ids = await store.batch_add_embeddings(
      ...         vectors,
      ...         metadata_list,
      ...         batch_size=1000
      ...     )
      ...
      ...     # Search similar vectors
      ...     results = await store.search_similar(query, k=5)
      ...
      ...     await store.close()
      >>>
      >>> asyncio.run(example())

Connection Pool
-------------

.. autoclass:: VectorStoragePool
   :members:
   :undoc-members:
   :show-inheritance:

   Connection pool for managing multiple vector storage instances.

   Example::

      >>> async def pool_example():
      ...     # Create pool
      ...     pool = VectorStoragePool(
      ...         storage_config=config,
      ...         pool_config=PoolConfig(
      ...             min_size=2,
      ...             max_size=10
      ...         )
      ...     )
      ...     await pool.start()
      ...
      ...     # Acquire connection
      ...     store = await pool.acquire()
      ...     try:
      ...         results = await store.search_similar(query, k=5)
      ...     finally:
      ...         await pool.release(store)
      ...
      ...     await pool.close()

Resource Management
----------------

.. autoclass:: ResourceMonitor
   :members:
   :undoc-members:
   :show-inheritance:

   Resource monitoring and quota management.

   Example::

      >>> async def resource_example():
      ...     monitor = ResourceMonitor(
      ...         quota=ResourceQuota(
      ...             max_memory_bytes=4 * 1024**3,  # 4GB
      ...             max_vectors=1_000_000
      ...         )
      ...     )
      ...     await monitor.start()
      ...
      ...     # Use resource context
      ...     async with ResourceContext(monitor, "add", vectors=vectors):
      ...         await store.batch_add_embeddings(vectors, metadata_list)
      ...
      ...     # Check resource usage
      ...     stats = monitor.get_stats()
      ...     print(f"Memory usage: {stats['memory_rss'] / 1024**2:.1f} MB")
      ...
      ...     await monitor.stop()

Configuration
-----------

.. autoclass:: VectorStorageConfig
   :members:
   :undoc-members:
   :show-inheritance:

   Configuration for vector storage.

.. autoclass:: PoolConfig
   :members:
   :undoc-members:
   :show-inheritance:

   Configuration for connection pool.

.. autoclass:: ResourceQuota
   :members:
   :undoc-members:
   :show-inheritance:

   Resource quotas and limits.

Types and Exceptions
-----------------

.. autoclass:: VectorMetadata
   :members:
   :undoc-members:
   :show-inheritance:

   Type definition for vector metadata.

.. autoclass:: SearchResult
   :members:
   :undoc-members:
   :show-inheritance:

   Type definition for search results.

.. autoexception:: StorageError
   :members:
   :show-inheritance:

   Base exception for storage errors.

.. autoexception:: StorageOperationError
   :members:
   :show-inheritance:

   Exception for storage operation errors.

.. autoexception:: ResourceExceededError
   :members:
   :show-inheritance:

   Exception for exceeded resource quotas.

Performance Considerations
-----------------------

Vector Dimensionality
^^^^^^^^^^^^^^^^^^^
- Choose appropriate vector dimension based on model output
- Higher dimensions provide better accuracy but use more memory
- Common dimensions: 768 (BERT), 512 (ResNet), 1024 (CLIP)

Index Types
^^^^^^^^^^
- ``flat``: Exact search, best for small datasets (<100K vectors)
- ``hnsw``: Approximate search, good balance of speed and accuracy
- ``ivf``: Approximate search, best for very large datasets (>1M vectors)

Batch Processing
^^^^^^^^^^^^^
- Use batch operations when possible
- Optimal batch size depends on available memory
- Default batch size: 1000 vectors
- Monitor memory usage during batch operations

Resource Management
^^^^^^^^^^^^^^^^
- Set appropriate resource quotas
- Monitor memory usage
- Use connection pooling for concurrent access
- Implement proper cleanup

Example Configurations
-------------------

Small Dataset (<100K vectors)::

   config = VectorStorageConfig(
       dimension=768,
       index_type="flat",
       similarity_threshold=0.8,
       max_vectors=100_000
   )

Medium Dataset (<1M vectors)::

   config = VectorStorageConfig(
       dimension=768,
       index_type="hnsw",
       similarity_threshold=0.7,
       max_vectors=1_000_000
   )

Large Dataset (>1M vectors)::

   config = VectorStorageConfig(
       dimension=768,
       index_type="ivf",
       similarity_threshold=0.6,
       max_vectors=10_000_000
   )

High Concurrency::

   pool_config = PoolConfig(
       min_size=5,
       max_size=20,
       max_idle_time=300,
       health_check_interval=30
   )

   resource_quota = ResourceQuota(
       max_memory_bytes=8 * 1024**3,  # 8GB
       max_vectors=5_000_000,
       max_concurrent_searches=200
   )
