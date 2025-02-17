# Vector Storage Documentation

## Overview

The `VectorStorage` class provides an efficient in-memory storage system for managing and searching vector embeddings. It supports storing vectors with associated metadata and performing similarity-based searches using cosine similarity.

## Features

- Store and retrieve vector embeddings
- Associate metadata with vectors
- Perform k-nearest neighbor searches
- Cosine similarity-based matching
- Type-safe operations with validation
- Flexible dimension support (default: 1536 for OpenAI embeddings)

## Basic Usage

```python
import numpy as np
from src.storage.vector import VectorStorage

# Initialize storage (default dimension: 1536)
storage = VectorStorage()

# Store a vector with metadata
vector = np.random.rand(1536)  # Example vector
metadata = {"timestamp": "2024-02-07", "source": "video_1"}
storage.store("frame_001", vector, metadata)

# Retrieve vector and metadata
retrieved_vector = storage.retrieve("frame_001")
metadata = storage.get_metadata("frame_001")

# Search for similar vectors
query = np.random.rand(1536)
results = storage.search(query, k=5)  # Get top 5 similar vectors
```

## API Reference

### Constructor

```python
def __init__(self, dimension: int = 1536)
```

Initialize vector storage with specified dimension.

**Parameters**:
- `dimension`: Vector dimension (default: 1536 for OpenAI embeddings)

### Methods

#### store()

```python
def store(
    self,
    key: str,
    vector: np.ndarray,
    metadata: Optional[Dict[str, Any]] = None
) -> None
```

Store a vector with optional metadata.

**Parameters**:
- `key`: Unique identifier for the vector
- `vector`: The vector to store (numpy array)
- `metadata`: Optional metadata dictionary

**Raises**:
- `StorageError`: If vector is None or has invalid dimensions

#### retrieve()

```python
def retrieve(self, key: str) -> Optional[np.ndarray]
```

Retrieve a vector by key.

**Parameters**:
- `key`: Key of vector to retrieve

**Returns**:
- The vector if found, None otherwise

#### get_metadata()

```python
def get_metadata(self, key: str) -> Optional[Dict[str, Any]]
```

Get metadata for a vector.

**Parameters**:
- `key`: Key of vector to get metadata for

**Returns**:
- Metadata dictionary if found, None otherwise

#### search()

```python
def search(
    self,
    query_vector: np.ndarray,
    k: int = 5
) -> List[tuple[str, float]]
```

Find k nearest neighbors to query vector using cosine similarity.

**Parameters**:
- `query_vector`: Vector to search for
- `k`: Number of nearest neighbors to return (default: 5)

**Returns**:
- List of (key, similarity) tuples for k nearest neighbors

**Raises**:
- `StorageError`: If query vector is None or has invalid dimensions

## Examples

### Basic Vector Storage

```python
import numpy as np
from src.storage.vector import VectorStorage

# Initialize storage
storage = VectorStorage(dimension=512)  # Custom dimension

# Create and store vectors
vector1 = np.random.rand(512)
vector2 = np.random.rand(512)

storage.store("vec1", vector1, {"type": "frame_embedding"})
storage.store("vec2", vector2, {"type": "audio_embedding"})

# Retrieve vectors
vec1 = storage.retrieve("vec1")
metadata1 = storage.get_metadata("vec1")
```

### Similarity Search

```python
import numpy as np
from src.storage.vector import VectorStorage

# Initialize storage with vectors
storage = VectorStorage()
for i in range(100):
    vector = np.random.rand(1536)
    storage.store(f"vec_{i}", vector, {"index": i})

# Perform similarity search
query = np.random.rand(1536)
results = storage.search(query, k=5)

# Process results
for key, similarity in results:
    metadata = storage.get_metadata(key)
    print(f"Vector {key}: similarity={similarity:.3f}, metadata={metadata}")
```

### Error Handling

```python
import numpy as np
from src.storage.vector import VectorStorage
from src.core.exceptions import StorageError

storage = VectorStorage(dimension=1536)

try:
    # This will raise an error (wrong dimension)
    invalid_vector = np.random.rand(512)
    storage.store("invalid", invalid_vector)
except StorageError as e:
    print(f"Storage error: {e}")

try:
    # This will raise an error (invalid type)
    storage.store("invalid", [1, 2, 3])
except StorageError as e:
    print(f"Storage error: {e}")
```

## Best Practices

1. **Memory Management**:
   - Monitor memory usage for large vector collections
   - Consider batch processing for large datasets
   - Clear unused vectors when possible

2. **Performance Optimization**:
   - Use appropriate vector dimensions
   - Consider indexing for large-scale search
   - Batch similar operations when possible

3. **Error Handling**:
   - Always handle StorageError exceptions
   - Validate vector dimensions before storage
   - Check return values for None

4. **Metadata Usage**:
   - Keep metadata concise and relevant
   - Use consistent metadata schema
   - Include timestamps for temporal data

## Performance Considerations

- Memory usage scales linearly with number of vectors
- Search complexity is O(n) where n is number of stored vectors
- Consider using approximate nearest neighbor algorithms for large-scale deployments
- Batch operations when storing or searching multiple vectors 