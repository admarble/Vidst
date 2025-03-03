# Vector Storage Service Interface

## Overview

The Vector Storage service interface provides a standardized way to interact with vector databases for similarity search operations. It abstracts away the details of specific vector database implementations, allowing for easy switching between different providers.

## Key Components

### BaseVectorStorage

The `BaseVectorStorage` class provides a standardized interface for vector storage operations:

- **add_vectors**: Add vectors to the storage with optional metadata
- **search**: Search for similar vectors based on a query vector
- **delete_vectors**: Delete vectors from the storage by ID

### PineconeVectorStorage

The `PineconeVectorStorage` class implements the `BaseVectorStorage` interface for the Pinecone vector database:

- **Async/Sync Conversion**: Handles conversion between async API and Pinecone's synchronous client
- **Error Handling**: Provides detailed error messages for Pinecone-specific errors
- **Metadata Management**: Supports storing and retrieving metadata with vectors

## Configuration

### PineconeConfig

The `PineconeConfig` class provides configuration options for the Pinecone vector storage:

```python
class PineconeConfig(ServiceConfig):
    """Configuration for Pinecone vector storage."""
    api_key: str
    environment: str
    index_name: str
    dimension: int = 512
    metric: str = "cosine"
```

## Usage Examples

### Basic Usage

```python
from video_understanding.storage.vector.pinecone import PineconeConfig, PineconeVectorStorage
import numpy as np

# Create configuration
config = PineconeConfig(
    service_name="pinecone_storage",
    api_key="your-pinecone-key",
    environment="production",
    index_name="video-embeddings",
    dimension=512,
)

# Create service instance
vector_storage = PineconeVectorStorage(config)

# Initialize service
await vector_storage.initialize()

# Add vectors
vectors = np.random.rand(3, 512)  # 3 vectors of dimension 512
ids = ["video1_scene1", "video1_scene2", "video1_scene3"]
metadata = [
    {"timestamp": 10.5, "label": "intro"},
    {"timestamp": 35.2, "label": "main_content"},
    {"timestamp": 120.0, "label": "conclusion"},
]
await vector_storage.add_vectors(vectors, ids, metadata)

# Search for similar vectors
query_vector = np.random.rand(512)
results = await vector_storage.search(query_vector, top_k=2)

# Process results
for id, score, metadata in results:
    print(f"ID: {id}, Score: {score}, Metadata: {metadata}")

# Delete vectors
await vector_storage.delete_vectors(["video1_scene1"])

# Shut down service
await vector_storage.shutdown()
```

### Factory-based Usage

```python
from video_understanding.services.factory import ServiceFactory
from video_understanding.storage.vector.base import BaseVectorStorage
from video_understanding.storage.vector.pinecone import PineconeConfig

# Create service factory
factory = ServiceFactory[ServiceConfig, BaseService]()

# Register vector storage implementations
factory.register("pinecone", PineconeVectorStorage)

# Create configuration
config = PineconeConfig(
    service_name="pinecone_storage",
    api_key="your-pinecone-key",
    environment="production",
    index_name="video-embeddings",
)

# Create service instance
vector_storage = factory.create("pinecone", config)

# Use as before
await vector_storage.initialize()
# ...
await vector_storage.shutdown()
```

## Error Handling

```python
from video_understanding.storage.vector.base import VectorStorageError

try:
    await vector_storage.add_vectors(vectors, ids, metadata)
except VectorStorageError as e:
    print(f"Vector storage error: {e}")
    # Handle the error
```

## Implementation Details

### Adding Vectors

The `add_vectors` method adds vectors to the storage:

```python
async def add_vectors(
    self,
    vectors: np.ndarray,
    ids: List[str],
    metadata: Optional[List[Dict[str, Any]]] = None
) -> None:
    """Add vectors to the storage.

    Args:
        vectors: Array of vectors to add
        ids: List of IDs for the vectors
        metadata: Optional list of metadata dictionaries

    Raises:
        VectorStorageError: If adding vectors fails
    """
```

### Searching Vectors

The `search` method searches for similar vectors:

```python
async def search(
    self,
    query_vector: np.ndarray,
    top_k: int = 5
) -> List[Tuple[str, float, Dict[str, Any]]]:
    """Search for similar vectors.

    Args:
        query_vector: Query vector
        top_k: Number of results to return

    Returns:
        List of tuples containing (id, score, metadata)

    Raises:
        VectorStorageError: If search fails
    """
```

### Deleting Vectors

The `delete_vectors` method deletes vectors from the storage:

```python
async def delete_vectors(self, ids: List[str]) -> None:
    """Delete vectors from the storage.

    Args:
        ids: List of vector IDs to delete

    Raises:
        VectorStorageError: If deleting vectors fails
    """
```

## Best Practices

1. **Initialize Before Use**: Always call `initialize()` before using the service.
2. **Proper Shutdown**: Always call `shutdown()` when done to release resources.
3. **Batch Operations**: Use batch operations for better performance when adding or deleting multiple vectors.
4. **Error Handling**: Use try-except blocks to handle potential errors.
5. **Metadata Management**: Use metadata to store additional information about vectors for easier retrieval and filtering.
6. **Dimension Consistency**: Ensure all vectors have the same dimension as specified in the configuration.
7. **ID Management**: Use a consistent ID scheme for vectors to make retrieval and management easier.
