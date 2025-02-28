# Vidst Vector Database API Integration Strategy

## Executive Summary

This document outlines a strategic approach for replacing the self-hosted FAISS vector storage implementation in the Vidst project with Pinecone's managed vector database API. This integration represents the highest-impact opportunity for simplification while maintaining or improving core functionality. The primary benefits include:

1. **Infrastructure Simplification**: Elimination of complex vector database setup and management
2. **Improved Scalability**: Automatic scaling without infrastructure planning
3. **Enhanced Performance**: Optimized similarity search capabilities for multimedia content
4. **Reduced Maintenance**: No need for index tuning, updates, or server management
5. **API-First Architecture**: Alignment with the project's API consolidation strategy

The proposed integration follows a phased approach, prioritizing core similarity search functionality while providing a clear migration path from the existing FAISS implementation. This strategy directly supports the project's scope realignment goals by simplifying architecture, reducing infrastructure requirements, and accelerating development of the POC's core functionality.

## Current Implementation Assessment

### FAISS Implementation Analysis

The Vidst project currently uses FAISS for vector storage and similarity search, implemented in the following locations:

| Component | Purpose | Implementation Location |
|-----------|---------|-------------------------|
| Vector Storage | Store and search embeddings | `src/video_understanding/storage/vector/storage.py` |
| Index Management | Create and update indexes | `src/video_understanding/storage/vector/utils.py` |
| Embedding Generation | Create vector representations | `src/video_understanding/ai/models/base.py` |
| Search Interface | Query vector storage | `src/video_understanding/core/processing/pipeline.py` |

### Identified Limitations

1. **Infrastructure Complexity**: Requires dedicated resources for vector database hosting
2. **Performance Tuning**: Manual optimization needed for index performance 
3. **Scaling Challenges**: Requires careful resource planning for larger datasets
4. **Integration Overhead**: Custom code needed for persistence, batching, and error handling
5. **Limited Metadata**: Basic metadata support requiring additional storage solutions

### Current Usage Patterns

The FAISS implementation is primarily used for:

1. **Scene Embedding Storage**: Vector representations of visual scenes
2. **Semantic Similarity Search**: Finding related content based on embeddings
3. **Content Deduplication**: Identifying similar or duplicate content
4. **Multimodal Matching**: Connecting text queries to visual content

## Pinecone Capabilities Analysis

Pinecone is a managed vector database service specifically designed for machine learning applications. Its key capabilities include:

### Core Features

1. **Serverless Architecture**: No infrastructure to manage or scale
2. **Real-Time Updates**: Immediate indexing of new vectors
3. **Hybrid Search**: Combines semantic and keyword search
4. **Rich Metadata**: Store and filter on metadata alongside vectors
5. **Optimized Performance**: Purpose-built for similarity search operations

### Technical Specifications

| Feature | Specification | Comparison to FAISS |
|---------|---------------|---------------------|
| Vector Dimensions | Up to 20,000 dimensions | Comparable to FAISS |
| Index Size | Billions of vectors | Superior for cloud scaling |
| Query Speed | ~10ms p95 latency | Superior for cloud deployment |
| Distance Metrics | Cosine, Euclidean, Dot Product | Equivalent to FAISS |
| Updates | Real-time | Superior to FAISS batch updates |
| Metadata Filtering | Advanced filtering capabilities | Superior to basic FAISS |

### Performance Considerations

1. **Latency**: 10-50ms for typical queries (depending on complexity)
2. **Throughput**: 100+ queries per second on standard plans
3. **Scaling**: Automatic scaling based on vector count and operation volume
4. **Reliability**: 99.95% uptime SLA with managed infrastructure

### Cost Structure

| Tier | Vectors | QPS | Monthly Cost (Est.) |
|------|---------|-----|---------------------|
| Free | 100,000 | 5 | $0 |
| Starter | 5M | 50 | $70-$100 |
| Standard | 100M | 100+ | $300+ |

The free tier is sufficient for POC development, with reasonable scaling costs as the project grows.

## Integration Strategy

Based on the capabilities assessment, we recommend a **phased replacement strategy**:

### Phase 1: Direct Replacement

Replace the core FAISS functionality with Pinecone API calls while maintaining the same interfaces to minimize disruption to dependent code.

### Phase 2: Feature Enhancement

Leverage Pinecone's advanced features to enhance the video understanding capabilities:

1. **Metadata Filtering**: Implement filtering based on scene properties
2. **Hybrid Search**: Combine text and vector search for more accurate results
3. **Namespace Management**: Organize embeddings by video or content type

### Phase 3: Architecture Optimization

Refactor the architecture to fully leverage the cloud-native benefits:

1. **Webhook Integration**: Real-time updates on query patterns
2. **Serverless Processing**: Align with other serverless components
3. **Performance Monitoring**: Implement Pinecone observability features

## Implementation Guide

### Prerequisites

1. Create a Pinecone account: https://www.pinecone.io/
2. Create an API key from the Pinecone console
3. Install the Pinecone client library:
   ```bash
   pip install pinecone-client
   ```

### Base Implementation

Create a Pinecone vector storage implementation that follows the same interface as the current FAISS implementation:

```python
# src/video_understanding/storage/vector/pinecone_storage.py
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pinecone
from pydantic import BaseModel
from loguru import logger

from video_understanding.storage.vector.base import BaseVectorStorage
from video_understanding.utils.exceptions import VectorStorageError


class PineconeConfig(BaseModel):
    """Configuration for Pinecone vector storage."""
    api_key: str
    environment: str = "us-west1-gcp"
    dimension: int = 1536  # Default for many embedding models
    metric: str = "cosine"
    namespace: Optional[str] = None
    index_name: str = "vidst-vectors"


class PineconeVectorStorage(BaseVectorStorage):
    """Pinecone implementation of vector storage."""
    
    def __init__(self, config: PineconeConfig):
        """Initialize Pinecone vector storage.
        
        Args:
            config: Configuration for Pinecone
        """
        self.config = config
        self.initialized = False
        self._initialize()
        
    def _initialize(self) -> None:
        """Initialize Pinecone client and ensure index exists."""
        try:
            # Initialize Pinecone client
            pinecone.init(
                api_key=self.config.api_key,
                environment=self.config.environment
            )
            
            # Check if index exists, create if not
            if self.config.index_name not in pinecone.list_indexes():
                logger.info(f"Creating Pinecone index: {self.config.index_name}")
                pinecone.create_index(
                    name=self.config.index_name,
                    dimension=self.config.dimension,
                    metric=self.config.metric
                )
                
            # Connect to index
            self.index = pinecone.Index(self.config.index_name)
            self.initialized = True
            logger.info(f"Initialized Pinecone vector storage with index: {self.config.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise VectorStorageError(f"Pinecone initialization error: {str(e)}")
            
    def add_vectors(self, vectors: np.ndarray, ids: List[str], metadata: Optional[List[Dict[str, Any]]] = None) -> None:
        """Add vectors to the index.
        
        Args:
            vectors: Numpy array of vectors to add
            ids: List of IDs corresponding to vectors
            metadata: Optional list of metadata dictionaries
            
        Raises:
            VectorStorageError: If there's an error adding vectors
        """
        try:
            # Prepare vector data for Pinecone
            vector_data = []
            for i, vec in enumerate(vectors):
                item = (ids[i], vec.tolist())
                if metadata and i < len(metadata):
                    item = (ids[i], vec.tolist(), metadata[i])
                vector_data.append(item)
                
            # Upsert vectors to Pinecone
            self.index.upsert(
                vectors=vector_data,
                namespace=self.config.namespace
            )
            logger.debug(f"Added {len(vectors)} vectors to Pinecone index")
            
        except Exception as e:
            logger.error(f"Failed to add vectors to Pinecone: {str(e)}")
            raise VectorStorageError(f"Pinecone add vectors error: {str(e)}")
            
    def search(self, query_vector: np.ndarray, top_k: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[Tuple[str, float, Optional[Dict[str, Any]]]]:
        """Search for similar vectors.
        
        Args:
            query_vector: Query vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of tuples (id, score, metadata)
            
        Raises:
            VectorStorageError: If there's an error during search
        """
        try:
            # Convert numpy array to list
            query = query_vector.tolist()
            
            # Perform query
            results = self.index.query(
                vector=query,
                top_k=top_k,
                namespace=self.config.namespace,
                filter=filter_metadata,
                include_metadata=True
            )
            
            # Format results to match expected return format
            formatted_results = []
            for match in results.matches:
                result = (match.id, match.score, match.metadata)
                formatted_results.append(result)
                
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search vectors in Pinecone: {str(e)}")
            raise VectorStorageError(f"Pinecone search error: {str(e)}")
            
    def delete_vectors(self, ids: List[str]) -> None:
        """Delete vectors from the index.
        
        Args:
            ids: List of vector IDs to delete
            
        Raises:
            VectorStorageError: If there's an error deleting vectors
        """
        try:
            self.index.delete(
                ids=ids,
                namespace=self.config.namespace
            )
            logger.debug(f"Deleted {len(ids)} vectors from Pinecone index")
            
        except Exception as e:
            logger.error(f"Failed to delete vectors from Pinecone: {str(e)}")
            raise VectorStorageError(f"Pinecone delete vectors error: {str(e)}")
            
    def get_vector_count(self) -> int:
        """Get the number of vectors in the index.
        
        Returns:
            Number of vectors
            
        Raises:
            VectorStorageError: If there's an error getting vector count
        """
        try:
            stats = self.index.describe_index_stats()
            namespace_count = stats.namespaces.get(self.config.namespace or '', {}).get('vector_count', 0)
            return namespace_count if self.config.namespace else stats.total_vector_count
            
        except Exception as e:
            logger.error(f"Failed to get vector count from Pinecone: {str(e)}")
            raise VectorStorageError(f"Pinecone vector count error: {str(e)}")
            
    def clear(self) -> None:
        """Clear all vectors from the index.
        
        Raises:
            VectorStorageError: If there's an error clearing vectors
        """
        try:
            if self.config.namespace:
                # Delete only vectors in the namespace
                self.index.delete(
                    delete_all=True,
                    namespace=self.config.namespace
                )
            else:
                # Delete all vectors in the index
                self.index.delete(delete_all=True)
                
            logger.info(f"Cleared all vectors from Pinecone index")
            
        except Exception as e:
            logger.error(f"Failed to clear vectors from Pinecone: {str(e)}")
            raise VectorStorageError(f"Pinecone clear vectors error: {str(e)}")
```

### Factory Implementation

Modify the vector storage factory to support Pinecone:

```python
# src/video_understanding/storage/vector/factory.py
from typing import Optional, Union

from video_understanding.storage.vector.base import BaseVectorStorage
from video_understanding.storage.vector.storage import FAISSVectorStorage, FAISSConfig
from video_understanding.storage.vector.pinecone_storage import PineconeVectorStorage, PineconeConfig


class VectorStorageFactory:
    """Factory for creating vector storage instances."""
    
    @staticmethod
    def create(config: Union[FAISSConfig, PineconeConfig]) -> BaseVectorStorage:
        """Create a vector storage instance based on configuration.
        
        Args:
            config: Vector storage configuration
            
        Returns:
            Vector storage instance
            
        Raises:
            ValueError: If configuration type is unknown
        """
        if isinstance(config, FAISSConfig):
            return FAISSVectorStorage(config)
        elif isinstance(config, PineconeConfig):
            return PineconeVectorStorage(config)
        else:
            raise ValueError(f"Unknown vector storage configuration type: {type(config)}")
```

### Configuration Integration

Update the application configuration to support Pinecone:

```python
# src/video_understanding/core/config/config.py (modifications)
from pydantic import BaseSettings, Field

class AppConfig(BaseSettings):
    """Application configuration."""
    # Existing configuration...
    
    # Vector storage configuration
    vector_storage_type: str = Field("pinecone", description="Vector storage type (faiss or pinecone)")
    pinecone_api_key: Optional[str] = Field(None, description="Pinecone API key")
    pinecone_environment: str = Field("us-west1-gcp", description="Pinecone environment")
    pinecone_index_name: str = Field("vidst-vectors", description="Pinecone index name")
    pinecone_dimension: int = Field(1536, description="Pinecone vector dimension")
    
    class Config:
        env_file = ".env"
        env_prefix = "VIDST_"
```

### Usage Example

Demonstrate how to use the Pinecone vector storage in the application:

```python
# Example usage in src/video_understanding/core/processing/pipeline.py
from video_understanding.storage.vector.factory import VectorStorageFactory
from video_understanding.storage.vector.pinecone_storage import PineconeConfig
from video_understanding.core.config.config import get_app_config

# Get application configuration
app_config = get_app_config()

# Create vector storage configuration
if app_config.vector_storage_type.lower() == "pinecone":
    vector_config = PineconeConfig(
        api_key=app_config.pinecone_api_key,
        environment=app_config.pinecone_environment,
        dimension=app_config.pinecone_dimension,
        index_name=app_config.pinecone_index_name
    )
else:
    # Fallback to FAISS configuration
    vector_config = FAISSConfig(
        index_path=app_config.faiss_index_path,
        dimension=app_config.faiss_dimension
    )

# Create vector storage instance
vector_storage = VectorStorageFactory.create(vector_config)

# Example: Store scene embeddings
scene_embeddings = model.get_embeddings(scene_frames)
scene_ids = [f"scene_{video_id}_{i}" for i in range(len(scene_frames))]
scene_metadata = [
    {
        "video_id": video_id,
        "scene_index": i,
        "start_time": scene.start_time,
        "end_time": scene.end_time,
        "duration": scene.end_time - scene.start_time,
        "description": scene.description
    }
    for i, scene in enumerate(scenes)
]

vector_storage.add_vectors(scene_embeddings, scene_ids, scene_metadata)

# Example: Search for similar scenes
query_embedding = model.get_embedding(query_frame)
similar_scenes = vector_storage.search(query_embedding, top_k=5)

# Process results
for scene_id, score, metadata in similar_scenes:
    print(f"Scene: {scene_id}, Similarity: {score:.4f}")
    print(f"  Time: {metadata['start_time']} - {metadata['end_time']}")
    print(f"  Description: {metadata['description']}")
```

### Advanced Usage: Hybrid Search

Example of implementing hybrid search with Pinecone:

```python
# Example of hybrid search implementation
from video_understanding.ai.models.embeddings import get_text_embedding

def hybrid_search(query_text: str, vector_storage, model, top_k: int = 5) -> List[Dict[str, Any]]:
    """Perform hybrid search using both text and vector similarity.
    
    Args:
        query_text: Text query
        vector_storage: Vector storage instance
        model: Embedding model for text
        top_k: Number of results to return
        
    Returns:
        List of search results
    """
    # Generate text embedding
    query_embedding = model.get_text_embedding(query_text)
    
    # Perform vector search
    results = vector_storage.search(query_embedding, top_k=top_k)
    
    # Extract and format results
    formatted_results = []
    for scene_id, score, metadata in results:
        result = {
            "id": scene_id,
            "score": score,
            "metadata": metadata
        }
        formatted_results.append(result)
        
    return formatted_results
```

## Testing & Validation Framework

### Unit Testing

Create unit tests for the Pinecone vector storage implementation:

```python
# tests/unit/storage/vector/test_pinecone_storage.py
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from video_understanding.storage.vector.pinecone_storage import PineconeVectorStorage, PineconeConfig
from video_understanding.utils.exceptions import VectorStorageError


@pytest.fixture
def pinecone_config():
    """Create a Pinecone configuration for testing."""
    return PineconeConfig(
        api_key="test-api-key",
        environment="test-environment",
        dimension=4,
        index_name="test-index"
    )


@pytest.fixture
def mock_pinecone():
    """Create a mock for Pinecone."""
    with patch("pinecone.init") as mock_init, \
         patch("pinecone.list_indexes") as mock_list_indexes, \
         patch("pinecone.create_index") as mock_create_index, \
         patch("pinecone.Index") as mock_index:
        
        # Setup mock behaviors
        mock_list_indexes.return_value = ["test-index"]
        mock_index_instance = MagicMock()
        mock_index.return_value = mock_index_instance
        
        yield {
            "init": mock_init,
            "list_indexes": mock_list_indexes,
            "create_index": mock_create_index,
            "index": mock_index,
            "index_instance": mock_index_instance
        }


def test_initialization(pinecone_config, mock_pinecone):
    """Test Pinecone initialization."""
    # Create storage
    storage = PineconeVectorStorage(pinecone_config)
    
    # Verify initialization
    mock_pinecone["init"].assert_called_once_with(
        api_key="test-api-key",
        environment="test-environment"
    )
    mock_pinecone["list_indexes"].assert_called_once()
    mock_pinecone["create_index"].assert_not_called()  # Index already exists
    mock_pinecone["index"].assert_called_once_with("test-index")
    assert storage.initialized is True


def test_initialization_create_index(pinecone_config, mock_pinecone):
    """Test Pinecone initialization with index creation."""
    # Setup mock to indicate index doesn't exist
    mock_pinecone["list_indexes"].return_value = []
    
    # Create storage
    storage = PineconeVectorStorage(pinecone_config)
    
    # Verify index creation
    mock_pinecone["create_index"].assert_called_once_with(
        name="test-index",
        dimension=4,
        metric="cosine"
    )


def test_add_vectors(pinecone_config, mock_pinecone):
    """Test adding vectors to Pinecone."""
    # Create storage
    storage = PineconeVectorStorage(pinecone_config)
    
    # Test data
    vectors = np.array([[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]])
    ids = ["vec1", "vec2"]
    metadata = [{"key1": "value1"}, {"key2": "value2"}]
    
    # Add vectors
    storage.add_vectors(vectors, ids, metadata)
    
    # Verify upsert was called
    mock_pinecone["index_instance"].upsert.assert_called_once()
    # Extract the call arguments
    call_args = mock_pinecone["index_instance"].upsert.call_args[1]
    assert "vectors" in call_args
    assert len(call_args["vectors"]) == 2
    assert call_args["vectors"][0][0] == "vec1"
    assert call_args["vectors"][0][1] == [1.0, 2.0, 3.0, 4.0]
    assert call_args["vectors"][0][2] == {"key1": "value1"}


def test_search(pinecone_config, mock_pinecone):
    """Test searching vectors in Pinecone."""
    # Create storage
    storage = PineconeVectorStorage(pinecone_config)
    
    # Setup mock search results
    mock_match1 = MagicMock()
    mock_match1.id = "vec1"
    mock_match1.score = 0.9
    mock_match1.metadata = {"key1": "value1"}
    
    mock_match2 = MagicMock()
    mock_match2.id = "vec2"
    mock_match2.score = 0.7
    mock_match2.metadata = {"key2": "value2"}
    
    mock_result = MagicMock()
    mock_result.matches = [mock_match1, mock_match2]
    
    mock_pinecone["index_instance"].query.return_value = mock_result
    
    # Test data
    query_vector = np.array([1.0, 2.0, 3.0, 4.0])
    
    # Search
    results = storage.search(query_vector, top_k=2)
    
    # Verify query was called
    mock_pinecone["index_instance"].query.assert_called_once_with(
        vector=[1.0, 2.0, 3.0, 4.0],
        top_k=2,
        namespace=None,
        filter=None,
        include_metadata=True
    )
    
    # Verify results
    assert len(results) == 2
    assert results[0][0] == "vec1"
    assert results[0][1] == 0.9
    assert results[0][2] == {"key1": "value1"}
    assert results[1][0] == "vec2"
    assert results[1][1] == 0.7
    assert results[1][2] == {"key2": "value2"}
```

### Integration Testing

Create integration tests for the Pinecone vector storage:

```python
# tests/integration/storage/vector/test_pinecone_integration.py
import pytest
import os
import numpy as np
from dotenv import load_dotenv

from video_understanding.storage.vector.pinecone_storage import PineconeVectorStorage, PineconeConfig

# Load environment variables for testing
load_dotenv()

# Skip tests if Pinecone API key is not available
pinecone_api_key = os.getenv("VIDST_PINECONE_API_KEY")
if not pinecone_api_key:
    pytest.skip("Pinecone API key not available", allow_module_level=True)


@pytest.fixture
def pinecone_storage():
    """Create a Pinecone storage instance for testing."""
    config = PineconeConfig(
        api_key=os.getenv("VIDST_PINECONE_API_KEY"),
        environment=os.getenv("VIDST_PINECONE_ENVIRONMENT", "us-west1-gcp"),
        dimension=4,
        index_name=f"vidst-test-{os.getenv('PYTEST_XDIST_WORKER', 'gw0')}"
    )
    storage = PineconeVectorStorage(config)
    
    # Clear the index before testing
    storage.clear()
    
    yield storage


def test_add_and_search(pinecone_storage):
    """Test adding vectors and searching."""
    # Test data
    vectors = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    ids = ["vec1", "vec2", "vec3", "vec4"]
    metadata = [
        {"type": "test", "value": 1},
        {"type": "test", "value": 2},
        {"type": "test", "value": 3},
        {"type": "test", "value": 4}
    ]
    
    # Add vectors
    pinecone_storage.add_vectors(vectors, ids, metadata)
    
    # Check vector count
    count = pinecone_storage.get_vector_count()
    assert count == 4
    
    # Search
    query = np.array([1.0, 0.1, 0.1, 0.1])
    results = pinecone_storage.search(query, top_k=2)
    
    # Verify results
    assert len(results) == 2
    assert results[0][0] == "vec1"  # First result should be vec1 (closest to query)
    
    # Search with filter
    filter_results = pinecone_storage.search(
        query,
        top_k=2,
        filter_metadata={"type": "test", "value": 2}
    )
    
    # Verify filtered results
    assert len(filter_results) == 1
    assert filter_results[0][0] == "vec2"
    
    # Clean up
    pinecone_storage.clear()
    final_count = pinecone_storage.get_vector_count()
    assert final_count == 0
```

### Performance Testing

Create performance tests to compare FAISS and Pinecone:

```python
# tests/performance/storage/vector/test_vector_storage_performance.py
import pytest
import time
import numpy as np
import os
from dotenv import load_dotenv

from video_understanding.storage.vector.storage import FAISSVectorStorage, FAISSConfig
from video_understanding.storage.vector.pinecone_storage import PineconeVectorStorage, PineconeConfig

# Load environment variables for testing
load_dotenv()

# Vector dimensions and counts for testing
DIMENSIONS = 1536  # Common embedding dimension
VECTOR_COUNTS = [100, 1000, 10000]
QUERY_REPEATS = 10

# Skip Pinecone tests if API key is not available
pinecone_api_key = os.getenv("VIDST_PINECONE_API_KEY")
skip_pinecone = pytest.mark.skipif(
    not pinecone_api_key,
    reason="Pinecone API key not available"
)


@pytest.fixture
def faiss_storage():
    """Create a FAISS storage instance for testing."""
    config = FAISSConfig(
        index_path=None,  # In-memory index
        dimension=DIMENSIONS
    )
    return FAISSVectorStorage(config)


@pytest.fixture
def pinecone_storage():
    """Create a Pinecone storage instance for testing."""
    if not pinecone_api_key:
        return None
        
    config = PineconeConfig(
        api_key=pinecone_api_key,
        environment=os.getenv("VIDST_PINECONE_ENVIRONMENT", "us-west1-gcp"),
        dimension=DIMENSIONS,
        index_name=f"vidst-perf-test"
    )
    storage = PineconeVectorStorage(config)
    
    # Clear the index before testing
    storage.clear()
    
    return storage


def generate_test_vectors(count, dim):
    """Generate random test vectors."""
    # Generate random vectors and normalize them
    vectors = np.random.rand(count, dim).astype(np.float32)
    # Normalize vectors for cosine similarity
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    vectors = vectors / norms
    return vectors


def generate_ids(count, prefix="vec"):
    """Generate IDs for test vectors."""
    return [f"{prefix}_{i}" for i in range(count)]


@pytest.mark.parametrize("vector_count", VECTOR_COUNTS)
def test_faiss_performance(faiss_storage, vector_count):
    """Test FAISS performance."""
    # Generate test data
    vectors = generate_test_vectors(vector_count, DIMENSIONS)
    ids = generate_ids(vector_count)
    
    # Measure add time
    start_time = time.time()
    faiss_storage.add_vectors(vectors, ids)
    add_time = time.time() - start_time
    
    # Generate query vector
    query = generate_test_vectors(1, DIMENSIONS)[0]
    
    # Measure search time (average of multiple queries)
    search_times = []
    for _ in range(QUERY_REPEATS):
        start_time = time.time()
        faiss_storage.search(query, top_k=10)
        search_times.append(time.time() - start_time)
    
    avg_search_time = sum(search_times) / len(search_times)
    
    print(f"\nFAISS Performance ({vector_count} vectors):")
    print(f"  Add time: {add_time:.4f}s")
    print(f"  Avg search time: {avg_search_time:.4f}s")
    
    # No specific assertions, just performance measurement


@skip_pinecone
@pytest.mark.parametrize("vector_count", VECTOR_COUNTS)
def test_pinecone_performance(pinecone_storage, vector_count):
    """Test Pinecone performance."""
    # Generate test data
    vectors = generate_test_vectors(vector_count, DIMENSIONS)
    ids = generate_ids(vector_count)
    
    # Measure add time
    start_time = time.time()
    batch_size = 100  # Pinecone recommends batching
    for i in range(0, vector_count, batch_size):
        end_idx = min(i + batch_size, vector_count)
        pinecone_storage.add_vectors(
            vectors[i:end_idx],
            ids[i:end_idx]
        )
    add_time = time.time() - start_time
    
    # Generate query vector
    query = generate_test_vectors(1, DIMENSIONS)[0]
    
    # Measure search time (average of multiple queries)
    search_times = []
    for _ in range(QUERY_REPEATS):
        start_time = time.time()
        pinecone_storage.search(query, top_k=10)
        search_times.append(time.time() - start_time)
    
    avg_search_time = sum(search_times) / len(search_times)
    
    print(f"\nPinecone Performance ({vector_count} vectors):")
    print(f"  Add time: {add_time:.4f}s")
    print(f"  Avg search time: {avg_search_time:.4f}s")
    
    # Clean up
    pinecone_storage.clear()
```

## Phased Implementation Timeline

We recommend a phased implementation approach to minimize disruption and validate each component:

### Phase 1: Setup and Basic Integration (3-5 days)

1. **Initial Setup**
   - Create Pinecone account and API keys
   - Implement PineconeVectorStorage class
   - Update configuration to support Pinecone

2. **Basic Testing**
   - Create unit tests for Pinecone integration
   - Verify basic functionality (add, search, delete)
   - Compare performance with existing FAISS implementation

### Phase 2: Feature Parity and Migration (3-4 days)

3. **Implement All Required Features**
   - Metadata filtering
   - Batch operations
   - Error handling and retry logic

4. **Migration Tools**
   - Create script to migrate data from FAISS to Pinecone
   - Implement parallel operation during transition
   - Add validation to ensure data consistency

### Phase 3: Enhanced Features (2-3 days)

5. **Implement Advanced Features**
   - Hybrid search capabilities
   - Namespace management for different content types
   - Optimized batch operations

6. **Performance Optimization**
   - Fine-tune query parameters
   - Implement caching for frequent queries
   - Configure index scaling based on usage patterns

### Phase 4: Documentation and Refinement (1-2 days)

7. **Documentation**
   - Update application documentation
   - Create usage examples
   - Document best practices

8. **Monitoring and Observability**
   - Add performance metrics
   - Implement error tracking
   - Create dashboard for vector storage usage

## Conclusion

Integrating Pinecone as a managed vector database service represents a significant opportunity to simplify the Vidst architecture while maintaining or improving core functionality. By eliminating the need for self-hosted FAISS infrastructure, the project can focus development resources on core video understanding features rather than database management.

The proposed implementation maintains compatibility with existing interfaces while providing a clear path to leverage advanced features in the future. The phased approach allows for incremental validation and ensures a smooth transition from the current implementation.

This integration aligns perfectly with the project's scope realignment goals by:

1. Simplifying architecture to what's necessary for the POC
2. Reducing infrastructure requirements and maintenance overhead
3. Enabling faster iteration on core functionality
4. Providing a more scalable foundation for future development

By adopting Pinecone as a managed service, the Vidst project can achieve a significant reduction in complexity while potentially improving performance and scalability, all with minimal disruption to the existing codebase.

## References

1. [Vidst Scope Realignment Plan](./vidst_scope_realignment_plan.md)
2. [Vidst System Architecture](./vidst_system_architecture.md)
3. [Vidst Dependency Reference](./vidst_dependency_reference.md)
4. [Pinecone Documentation](https://docs.pinecone.io/)
5. [Pinecone Python Client](https://github.com/pinecone-io/pinecone-python-client)
