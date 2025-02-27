.. py:module:: src.storage.vector

Vector Storage


























Overview


--------





--------





--------





--------





--------




The vector storage module provides functionality for storing and retrieving high-dimensional vectors efficiently.

Classes


-------





-------





-------





-------





-------


























VectorStore
























.. py:class:: VectorStore

   A class for storing and retrieving high-dimensional vectors.

   .. py:method:: add_vector(vector: numpy.ndarray, metadata: Dict[str, Any]) -> str

      Add a vector to the store.

      :param vector: The vector to store
      :type vector: :class:`numpy.ndarray`
      :param metadata: Associated metadata
      :returns: ID of the stored vector




   .. py:method:: get_vector(vector_id: str) -> Tuple[numpy.ndarray, Dict[str, Any]]

      Retrieve a vector by ID.

      :param vector_id: ID of the vector to retrieve
      :returns: Tuple of (vector, metadata)
      :rtype: Tuple[:class:`numpy.ndarray`, Dict[str, Any]]




   .. py:method:: search(query_vector: numpy.ndarray, k: int = 10) -> List[Tuple[str, float]]

      Search for similar vectors.

      :param query_vector: Vector to search for
      :type query_vector: :class:`numpy.ndarray`
      :param k: Number of results to return
      :returns: List of (vector_id, similarity) tuples

























VectorMetadata
























.. py:class:: VectorMetadata

   :module: src.storage.vector.types

   Metadata for stored vectors.

   .. py:attribute:: id

      :type: str

      Unique identifier for the vector




   .. py:attribute:: timestamp

      :type: float

      Creation timestamp




   .. py:attribute:: source

      :type: str

      Source of the vector (e.g., "frame", "scene", "text")




   .. py:attribute:: metadata

      :type: Dict[str, Any]

      Additional metadata




   .. py:method:: pop(key: str, default: Any = None) -> Any

      Remove specified key and return the corresponding value.

      :param key: Key to remove
      :param default: Value to return if key not found
      :returns: Value associated with key




   .. py:method:: update(other: Dict[str, Any]) -> None

      Update metadata with values from other dictionary.

      :param other: Dictionary to update from

























SearchResult
























.. py:class:: SearchResult

   :module: src.storage.vector.types

   Result from vector search.

   .. py:attribute:: id

      :type: str

      ID of the found vector




   .. py:attribute:: score

      :type: float

      Similarity score [0-1]




   .. py:attribute:: metadata

      :type: VectorMetadata

      Associated metadata




   .. py:method:: pop(key: str, default: Any = None) -> Any

      Remove specified key and return the corresponding value.

      :param key: Key to remove
      :param default: Value to return if key not found
      :returns: Value associated with key




   .. py:method:: update(other: Dict[str, Any]) -> None

      Update result with values from other dictionary.

      :param other: Dictionary to update from




Exceptions


----------





----------





----------





----------





----------




.. py:exception:: VectorStorageError

   :module: src.storage.vector.exceptions

   Base exception for vector storage errors.

.. py:exception:: ValidationError

   :module: src.core.exceptions

   Raised when vector or metadata validation fails.

.. py:exception:: FileValidationError

   :module: src.core.exceptions

   Raised when file validation fails.

Functions


---------





---------





---------





---------





---------




.. py:function:: validate_vector(vector: numpy.ndarray, expected_dim: int) -> None

   :module: src.storage.vector.validation

   Validate vector dimensions and values.

   :param vector: Vector to validate
   :param expected_dim: Expected dimensionality
   :raises ValidationError: If validation fails

.. py:function:: validate_metadata(metadata: VectorMetadata) -> None

   :module: src.storage.vector.validation

   Validate metadata structure and required fields.

   :param metadata: Metadata to validate
   :raises ValidationError: If validation fails

Example Usage


-------------





-------------





-------------





-------------





-------------




.. code-block:: python

      from src.storage.vector import VectorStore, VectorMetadata
      import numpy as np

      Initialize storage








=





=


      Create metadata








=





=

         id="frame_001",
         timestamp=1234567890,
         source="frame",
         metadata={"video_id": "video_123"}
      )

      Store vector








=





=

      storage.add_vector(vector, metadata)

      Search








=





=

      for key, score in results:
         print(f"Match {key}: {score}")

See Also


--------





--------





--------





--------





--------




\* :doc:`/api/storage/index`*
\* :doc:`/guides/vector-storage`*
