API Reference

=============

This section provides detailed API documentation for the Video Understanding AI system.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   processor
   detection
   ocr
   scene
   cache
   reference

Core Components


---------------

The system consists of several core components that work together to analyze video content:

********************************************
* :doc:`detection` - Object detection system
********************************************
*******************************************
* :doc:`cache` - Caching and storage system
*******************************************

Getting Started


-------------

For a quick start, check out the :doc:`processor` documentation and the example below:

.. code-block:: python

   from video_understanding import VideoProcessor, ProcessorConfig

   # Initialize processor
   config = ProcessorConfig(
         detection_enabled=True,
         ocr_enabled=True
   )
   processor = VideoProcessor(config)

   # Process video
   with processor.process(video) as context:
         results = processor.analyze_frames(context)
         print(f"Found {len(results['objects'])} objects")

For more examples, see the :doc:`../guides/getting_started` guide.

.. toctree::

   :maxdepth: 2
   :caption: Core

   core/processing
   core/input
   core/output
   core/config
   core/exceptions
   core/metrics
   core/logging

AI Models


---------





---------





---------





---------





---------




.. toctree::

   :maxdepth: 2
   :caption: AI

   ai/models/base
   ai/models/twelve_labs
   ai/models/gpt4v
   ai/models/gemini
   ai/models/whisper
   ai/pipeline
   ai/exceptions

Storage


-------





-------





-------





-------





-------




.. toctree::

   :maxdepth: 2
   :caption: Storage

   storage/vector
   storage/cache
   storage/metadata
   storage/exceptions

Common Utilities


----------------





----------------





----------------





----------------





----------------




.. toctree::

   :maxdepth: 2
   :caption: Utilities

   reference
   cache

Indices and Tables


------------------





------------------





------------------





------------------





------------------








\* :ref:`modindex`*
