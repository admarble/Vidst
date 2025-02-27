
Twelve Labs Model




















.. py:module:: src.ai.models.twelve_labs.model

.. py:currentmodule:: src.ai.models.twelve_labs.model

.. py:class:: TwelveLabsModel

   :module: src.ai.models.twelve_labs.model
   :no-index:

   Implementation of the Twelve Labs video processing model.

   Inherits from :class:`src.ai.models.base.BaseMod`_e`_l`_.

   .. py:attribute:: MAX_FILE_SIZE

      :type: int
      :no-index:

      Maximum file size in bytes (2GB)




   .. py:attribute:: SUPPORTED_FORMATS

      :type: List[str]
      :no-index:

      List of supported video formats ["mp4", "avi", "mov"]




   .. py:method:: process(video_path: str, options: TaskOptions = None) -> TaskResult

      :raises: :exc:`src.core.exceptions.ResourceError`

      Process a video file using Twelve Labs API.

      :param video_path: Path to video file
      :param options: Processing options
      :returns: Processing task result




   .. py:method:: search(query: str, video_id: str = None) -> List[SearchResult]

      :raises: :exc:`src.core.exceptions.ResourceError`

      Search video content using natural language.

      :param query: Search query
      :param video_id: Optional video ID to search within
      :returns: List of search results




   .. py:method:: retry_with_backoff(func: Callable, *arg*s*,*__ESCAPED_42*_*_* **kwargs) -> **A***n***y******

      :raises: :exc:`src.core.exceptions.ModelError`

      Retry a function call with exponential backoff.

      :param func: Function to retry
      :param args: Positional arguments
      :param kwargs: Keyword arguments
      :returns: Function result

























See Also





















* :doc:`/api/ai/models/twelve_labs/typ`_e`_s`*_*_**
* :doc:`/api/ai/models/twelve_labs/exceptio`_n`_s`*_*_**
