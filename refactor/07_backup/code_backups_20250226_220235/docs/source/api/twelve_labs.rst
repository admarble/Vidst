
Twelve Labs Integration

=======================











Overview


--------





--------





--------





--------





--------




The Twelve Labs integration provides video understanding capabilities through the Twelve Labs API.
This module enables processing and analyzing video content with advanced AI models.

Quick Start


-----------





-----------





-----------





-----------





-----------




.. code-block:: python

      from src.ai.models.twelve_labs import TwelveLabsModel
      from src.ai.models.twelve_labs.types import TaskType

      Initialize the model








=





=


      Process a video








=





=

         "video_path": "path/to/video.mp4",
         "task": TaskType.SCENE_DETECTION,
         "options": {"confidence_threshold": 0.8}
      })

      Search across processed videos








=





=

         "person explaining neural networks",
         confidence_threshold=0.7
      )

      Clean up resources








=





=


Features


--------





--------





--------





--------





--------




- Video Processing Tasks:
      - Scene detection
      - Speech transcription
      - Text extraction
      - Visual search
      - Content understanding

- Key Capabilities:
      - Asynchronous processing
      - Chunked file uploads
      - Progress monitoring
      - Resource management
      - Error handling
      - Input validation

Configuration


-------------





-------------





-------------





-------------





-------------




The following settings can be configured:

- ``MAX_FILE_SIZE``: Maximum video file size (default: 2GB)
- ``SUPPORTED_FORMATS``: Supported video formats (mp4, avi, mov)
- ``DEFAULT_INDEX``: Default search index name
- ``CHUNK_SIZE``: Upload chunk size (default: 1MB)
- ``MAX_RETRIES``: Maximum retry attempts (default: 3)
- ``INITIAL_BACKOFF``: Initial retry delay (default: 1s)
- ``MAX_BACKOFF``: Maximum retry delay (default: 30s)

Example Configuration:

.. code-block:: python

      from src.ai.models.twelve_labs import TwelveLabsModel

      print(f"Max file size: {TwelveLabsModel.MAX_FILE_SIZE}")
      print(f"Supported formats: {TwelveLabsModel.SUPPORTED_FORMATS}")

Error Handling


--------------





--------------





--------------





--------------





--------------




The module provides specific exceptions for different error cases:

.. code-block:: python

      from src.ai.models.twelve_labs.exceptions import ValidationError, ResourceError

      try:
         result = await model.process({
            "video_path": "invalid.mp4",
            "task": TaskType.SCENE_DETECTION
         })
      except ValidationError as e:
         print(f"Invalid input: {e}")
      except ResourceError as e:
         print(f"Processing failed: {e}")

API Reference


-------------





-------------





-------------





-------------





-------------








TwelveLabsModel


---------------
























.. autoclass:: src.ai.models.twelve_labs.model.TwelveLabsModel

      :members:
      :undoc-members:
      :show-inheritance:




Types

























.. automodule:: src.ai.models.twelve_labs.types

      :members:
      :undoc-members:
      :show-inheritance:




Exceptions

























.. automodule:: src.ai.models.twelve_labs.exceptions

      :members:
      :undoc-members:
      :show-inheritance:

Best Practices


--------------





--------------





--------------





--------------





--------------







1. Resource Management

























Always use proper resource cleanup:

.. code-block:: python

      async with TwelveLabsModel(api_key) as model:
         await model.process(...)

      Or explicitly:








"





"

      try:
         await model.process(...)
      finally:
         await model.close()

2. Input Validation


-------------------





-------------------





-------------------





-------------------





-------------------








-------------------










Validate inputs before processing:

.. code-block:: python

      try:
         model.validate(input_data)
      except ValidationError as e:
         print(f"Invalid input: {e}")




3. Error Handling

























Handle specific exceptions:

.. code-block:: python

      try:
         result = await model.process(input_data)
      except ValidationError as e:
         print(f"Invalid input: {e}")
      except ResourceError as e:
         print(f"Processing failed: {e}")
      except Exception as e:
         print(f"Unexpected error: {e}")




4. Progress Monitoring

























Use progress callbacks for long operations:

.. code-block:: python

      def progress_callback(current, total):
         print(f"Progress: {current}/{total} bytes")

      await model.process({
         "video_path": "video.mp4",
         "task": TaskType.SCENE_DETECTION,
         "progress_callback": progress_callback
      })




5. Search Optimization

























Use specific filters for better search results:

.. code-block:: python

      results = await model.search(
         "person explaining neural networks",
         confidence_threshold=0.7,
         filters={
            "duration_range": (0, 300),
            "video_ids": ["vid_123", "vid_456"]
         }
      )




6. Task Configuration

























Configure tasks with appropriate options:

.. code-block:: python

      result = await model.process({
         "video_path": "lecture.mp4",
         "task": TaskType.TRANSCRIPTION,
         "options": {
            "language": "en",
            "speaker_diarization": True,
            "confidence_threshold": 0.8
         }
      })

See Also


--------





--------





--------





--------





--------




- :doc:`../models/index`
- :doc:`../../core/config`
- :doc:`../../core/exceptions`

Indices and tables


------------------





------------------





------------------





------------------





------------------







\* :ref:`modindex`*
