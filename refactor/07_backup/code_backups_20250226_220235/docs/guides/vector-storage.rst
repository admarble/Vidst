
Vector Storage Guide









































Overview





















This guide covers vector storage implementation and usage in the Video Understanding AI system.






















Why Vector Storage?





















- Efficient similarity search across video content
- Fast retrieval of related video segments
- Semantic understanding of video content
- Scalable storage of high-dimensional embeddings
- Support for metadata and context






















Architecture





















The vector storage system consists of:

Core Components


























1. Vector Store

   - In-memory storage for fast access
   - Configurable dimensions
   - Metadata association

2. Search Engine

   - Cosine similarity matching
   - K-nearest neighbor search
   - Batch search capabilities

Getting Started


---------------





---------------





---------------





---------------





---------------





---------------













Basic Setup


























Initialize and use the vector storage:

.. code-block:: python

      from src.storage.vector import VectorStorage
      import numpy as np

      Initialize with default OpenAI dimensions (1536)








=





=


      Or specify custom dimensions








=





=









=





=

Common Use Cases


----------------





----------------





----------------





----------------





----------------





----------------













Storing Video Frame Embeddings


























Store and manage video frame embeddings:

.. code-block:: python

      def store_frame_embeddings(video_id: str, frames: List[Dict[str, Any]]):
         storage = VectorStorage()

         for frame in frames:

            Generate unique key








=





=


            Store embedding with metadata








=





=

                  key=key,
                  vector=frame['embedding'],
                  metadata={
                     'video_id': video_id,
                     'timestamp': frame['timestamp'],
                     'frame_info': frame['info']
                  }
            )

Semantic Search


























Search for similar video content:

.. code-block:: python

      def search_similar_frames(query_embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
         storage = VectorStorage()

         Search for similar frames








=





=


         Fetch metadata for results








=





=

         for key, similarity in results:
            metadata = storage.get_metadata(key)
            enriched_results.append({
                  'key': key,
                  'similarity': similarity,
                  'metadata': metadata
            })

         return enriched_results

Batch Processing


























Efficiently process multiple vectors:

.. code-block:: python

      def batch_store_vectors(vectors: List[Tuple[str, np.ndarray, Dict[str, Any]]]):
         storage = VectorStorage()

         Store vectors in batch








=





=

            try:
                  storage.store(key, vector, metadata)
            except Exception as e:
                  logger.error(f"Failed to store vector {key}: {str(e)}")
                  continue

Best Practices


--------------





--------------





--------------





--------------





--------------





--------------













Vector Management


























1. **Consistent Dimensionality**:

   .. code-block:: python

         def validate_vector(vector: np.ndarray, expected_dim: int = 1536) -> bool:
            if vector.shape != (expected_dim,):
                  raise ValueError(
                     f"Vector dimension mismatch. Expected {expected_dim}, "
                     f"got {vector.shape[0]}"
                  )
            return True

2. **Memory Optimization**:

   .. code-block:: python

         def optimize_storage(storage: VectorStorage):

            Convert to float32 for memory efficiency








=





=

                  k: v.astype(np.float32)
                  for k, v in storage.vectors.items()
            }

            Update storage








=





=


Metadata Organization


























1. **Structured Metadata**:

   .. code-block:: python

         def create_metadata(
            video_id: str,
            timestamp: float,
            frame_info: Dict[str, Any]
         ) -> Dict[str, Any]:
            return {
                  'video_id': video_id,
                  'timestamp': timestamp,
                  'frame_info': frame_info,
                  'created_at': datetime.now().isoformat(),
                  'version': '1.0'
            }

2. **Metadata Validation**:

   .. code-block:: python

         def validate_metadata(metadata: Dict[str, Any]) -> bool:
            required_fields = {'video_id', 'timestamp'}

            if not all(field in metadata for field in required_fields):
                  raise ValueError(f"Missing required fields: {required_fields}")

            return True

Error Handling


























Implement robust error handling:

.. code-block:: python

      from src.core.exceptions import StorageError

      class VectorStorageManager:
         def __init__(self):
            self.storage = VectorStorage()

         def safe_store(
            self,
            key: str,
            vector: np.ndarray,
            metadata: Dict[str, Any]
         ) -> bool:
            try:

                  Validate inputs








=





=

                  validate_metadata(metadata)

                  Store vector








=





=

                  return True

            except StorageError as e:
                  logger.error(f"Storage error for key {key}: {str(e)}")
                  return False

            except ValueError as e:
                  logger.error(f"Validation error for key {key}: {str(e)}")
                  return False

            except Exception as e:
                  logger.error(f"Unexpected error for key {key}: {str(e)}")
                  return False

Performance Optimization


------------------------





------------------------





------------------------





------------------------





------------------------





------------------------













Batch Operations


























.. code-block:: python

         def batch_similarity_search(
            queries: List[np.ndarray],
            k: int = 5
         ) -> Dict[int, List[Tuple[str, float]]]:
            storage = VectorStorage()
            results = {}

            Process queries in batch








=





=

                  results[i] = storage.search(query, k=k)

            return results

Memory Management


























.. code-block:: python

         def monitor_storage_usage(storage: VectorStorage) -> Dict[str, Any]:
            stats = {
                  'vector_count': len(storage.vectors),
                  'dimension': storage.dimension,
                  'estimated_memory': (
                     len(storage.vectors) *
                     storage.dimension *

                     4  bytes per float32








=





=









=





=


            if stats['estimated_memory'] > 1024:  1GB








=





=


            return stats

Advanced Usage


--------------





--------------





--------------





--------------





--------------





--------------













Custom Search Strategies


























Implement custom search logic:

.. code-block:: python

      class CustomVectorSearch:
         def __init__(self, storage: VectorStorage):
            self.storage = storage

         def search_with_filters(
            self,
            query: np.ndarray,
            filters: Dict[str, Any],
            k: int = 5
         ) -> List[Dict[str, Any]]:

            Get initial results








=





=









=





=

            Filter results








=





=

            for key, similarity in results:
                  metadata = self.storage.get_metadata(key)

                  Apply filters








=





=

                     filtered_results.append({
                        'key': key,
                        'similarity': similarity,
                        'metadata': metadata
                     })

                  if len(filtered_results) >= k:
                     break

            return filtered_results[:k]

         def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
            return all(
                  metadata.get(k) == v
                  for k, v in filters.items()
            )

Monitoring and Maintenance


--------------------------





--------------------------





--------------------------





--------------------------





--------------------------





--------------------------













Health Checks


























.. code-block:: python

      class VectorStorageMonitor:
         def __init__(self, storage: VectorStorage):
            self.storage = storage
            self.logger = logging.getLogger('vector_storage')

         def check_health(self) -> Dict[str, Any]:
            stats = {
                  'total_vectors': len(self.storage.vectors),
                  'memory_usage': self._get_memory_usage(),
                  'dimension': self.storage.dimension
            }

            Log health status








=





=


            Check for issues








=





=

                  self.logger.warning("Memory usage exceeds limit")

            return stats

         def _get_memory_usage(self) -> float:

            Calculate memory usage in MB








=





=

                  len(self.storage.vectors) *
                  self.storage.dimension *

                  4  bytes per float32








=





=


Troubleshooting


---------------





---------------





---------------





---------------





---------------





---------------













Common Issues and Solutions


























1. **Memory Issues**:

   - Use float32 instead of float64
   - Implement vector pruning
   - Monitor memory usage
   - Consider disk-based storage for large datasets

2. **Performance Issues**:

   - Use batch operations
   - Optimize search parameters
   - Monitor query times
   - Consider approximate nearest neighbor algorithms

3. **Data Quality Issues**:

   - Validate vector dimensions
   - Check for NaN values
   - Normalize vectors
   - Verify metadata consistency

Additional Resources


--------------------





--------------------





--------------------





--------------------





--------------------





--------------------













- :doc:`/api/storage/vector` - Detailed API documentation
- :doc:`error-handling` - Error handling guide
- :doc:`configuration` - System configuration guide
















Indices and Tables







































\* :ref:`modindex`*
