
Twelve Labs Model

=================











.. automodule:: src.ai.models.twelve_labs

   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Overview


--------





--------





--------





--------





--------




The Twelve Labs model implementation for video understanding and analysis using the Twelve Labs API.

Resource Management


-------------------





-------------------





-------------------





-------------------





-------------------




The model implements robust resource management to ensure proper cleanup of system resources,
API connections, and temporary files. This is particularly important for long-running
applications and systems processing multiple videos.





Cleanup Mechanisms


------------------
























The model provides two main cleanup mechanisms:

1. Explicit Cleanup (Recommended)

   .. code-block:: python

      model = TwelveLabsModel(api_key)
      try:
            await model.process(video_data)
      finally:

            await model.close()  Explicit cleanup








^





"

2. Automatic Cleanup (Fallback)

   The model implements ``__del__`` for automatic cleanup during garbage collection,
   but this should not be relied upon as the primary cleanup mechanism.

   .. warning::
      Do not rely on automatic cleanup in production code. Always use explicit cleanup
      via ``close()`` when possible.

Cleanup Scenarios


-----------------





-----------------





-----------------





-----------------





-----------------








-----------------










The cleanup system handles various scenarios:

1. **Normal Operatio***n**

   - Explicit ``close()`` call
   - All resources properly released
   - Active tasks cancelled
   - API client closed

2. **Running Event Loo***p**

   - Non-blocking cleanup
   - Task scheduled in existing loop
   - Asynchronous resource release

3. **No Event Loo***p**

   - Temporary loop creation
   - Synchronous cleanup
   - Loop properly closed

4. **Interpreter Shutdow***n**

   - Graceful cleanup skip
   - No errors raised
   - Safe termination




Best Practices





































Follow these guidelines for proper resource management:

1. Always use explicit cleanup:

   .. code-block:: python

      async with TwelveLabsModel(api_key) as model:
            await model.process(video_data)

2. Handle cleanup in error cases:

   .. code-block:: python

      try:
            await model.process(video_data)
      except Exception:

            Handle error








"





"

      finally:
            await model.close()

3. Monitor active tasks:

   .. code-block:: python

      Check active tasks before cleanup








"





"

            logger.warning(f"Cleaning up {len(model._active_tasks)} active tasks")
      await model.close()

Implementation Details


----------------------





----------------------





----------------------





----------------------





----------------------





----------------------













The cleanup implementation is designed to be:

- **Robus***t**: Handles all error cases gracefully***
- **Non-blockin***g**: Uses asynchronous cleanup when possible***
- **Complet***e**: Ensures all resources are released***
- **Saf***e**: Prevents resource leaks and shutdown errors***




Testing


































The cleanup system is thoroughly tested for various scenarios:

.. code-block:: python

   Test explicit cleanup










"





"

   assert len(model._active_tasks) == 0

   Test cleanup with active tasks










"





"

   await model.close()
   assert len(model._active_tasks) == 0

   Test cleanup during shutdown










"





"

               side_effect=RuntimeError("Loop closed")):

         model.__del__()  Should not raise exceptions








"





"

Twelve Labs Integration


-----------------------





-----------------------





-----------------------





-----------------------





-----------------------








-----------------------










.. automodule:: src.ai.models.twelve_labs

   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: src.ai.models.twelve_labs.model

   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

.. automodule:: src.ai.models.twelve_labs.types

   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:




Quick Start


































.. code-block:: python

   from src.ai.models.twelve_labs import TwelveLabsModel
   from src.ai.models.twelve_labs.types import TaskType

   Initialize the model










"





"


   Process a video










"





"

         "video_path": "path/to/video.mp4",
         "task": TaskType.SCENE_DETECTION,
         "options": {"confidence_threshold": 0.8}

   })

   Search across processed videos










"





"

         "person explaining neural networks",
         confidence_threshold=0.7

   )

   Clean up resources










"





"


Features


--------





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


































The following settings can be configured:

- ``MAX_FILE_SIZE``: Maximum video file size (default: 2GB)
- ``SUPPORTED_FORMATS``: Supported video formats (mp4, avi, mov)
- ``DEFAULT_INDEX``: Default search index name
- ``CHUNK_SIZE``: Upload chunk size (default: 1MB)
- ``MAX_RETRIES``: Maximum retry attempts (default: 3)
- ``INITIAL_BACKOFF``: Initial retry delay (default: 1s)
- ``MAX_BACKOFF``: Maximum retry delay (default: 30s)

Testing































The module includes comprehensive test coverage using pytest. Tests are organized in the
``tests/ai/models/twelve_labs/`` directory:

- ``unit/``: Unit tests for individual components
- ``integration/``: Integration tests with the API
- ``fixtures/``: Test data and mock responses




Test Configuration


































Tests use a specific pylint configuration defined in ``.pylintrc``:

.. code-block:: ini

   [MESSAGES CONTROL]
   disable=

         W0621,  redefined-outer-name - expected with pytest fixtures
         W0212,  protected-access - sometimes necessary in tests
         C0411,  wrong-import-order - handled by other tools
         E1101,  no-member - false positives with dynamic attributes
         R0801,  duplicate-code - common in tests
         C0116,  missing-function-docstring - docstrings present in test names
         C0115   missing-class-docstring - docstrings present in test names




Running Tests

























To run tests with proper lint checking:

.. code-block:: bash

   Run tests
   pytest tests/ai/models/twelve_labs/

   Run with lint checking
   pylint --rcfile=tests/ai/models/twelve_labs/.pylintrc tests/ai/models/twelve_labs/




Test Best Practices

























1. **Mock Usag***e**

   - Use fixtures for common mock objects
   - Simulate API responses accurately
   - Handle async operations properly
   - Clean up resources after tests

2. **Protected Acces***s**

   - Use ``pylint: disable=protected-access`` for test-specific access
   - Document why protected access is needed
   - Keep protected access minimal

3. **Import Organizatio***n**

   - Group imports by type:
      - Standard library
      - Third-party
      - Local imports

   - Remove unused imports
   - Maintain consistent order

4. **Type Checkin***g**

   - Use proper type hints
   - Validate TypedDict usage
   - Handle optional fields appropriately
   - Test type validation




API Reference

























.. automodule:: src.ai.models.twelve_labs

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




























Contributing

























Indices and Tables





























\* :doc:`/modindex`*
