Video Processor API
==================

VideoProcessor
------------

The main class for processing video content. This class provides the core functionality for analyzing and processing video files.

.. py:class:: VideoProcessor(config: ProcessorConfig)

   Main class for processing video content.

   :param config: Configuration object for the video processor
   :type config: ProcessorConfig

Methods
~~~~~~~

.. py:method:: process(video: Video) -> UploadContext

   Creates a processing context for a video.

   :param video: Video object to process
   :type video: Video
   :return: Context object for the video processing session
   :rtype: UploadContext

   Example:

   .. code-block:: python

      from video_understanding import VideoProcessor, ProcessorConfig

      # Initialize processor with configuration
      config = ProcessorConfig(
          detection_enabled=True,
          ocr_enabled=True
      )
      processor = VideoProcessor(config)

      # Process video
      with processor.process(video) as context:
          results = processor.analyze_frames(context)
          print(f"Found {len(results['objects'])} objects")

.. py:method:: analyze_frames(context: UploadContext) -> Dict[str, Any]

   Analyzes video frames within the given context.

   :param context: Processing context for the video
   :type context: UploadContext
   :return: Dictionary containing analysis results
   :rtype: Dict[str, Any]

Configuration
~~~~~~~~~~~~

.. py:class:: ProcessorConfig

   Configuration class for VideoProcessor.

   .. py:attribute:: detection_enabled
      :type: bool

      Enable or disable object detection.

   .. py:attribute:: ocr_enabled
      :type: bool

      Enable or disable OCR processing.

   .. py:attribute:: scene_detection_threshold
      :type: float

      Threshold for scene change detection (default: 0.3).

Error Handling
~~~~~~~~~~~~

The VideoProcessor class uses custom exceptions for error handling:

.. py:exception:: VideoProcessingError

   Base exception for video processing errors.

.. py:exception:: VideoFormatError

   Raised when the video format is not supported.

Usage Examples
~~~~~~~~~~~~

Basic Usage
^^^^^^^^^^

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

Advanced Configuration
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   config = ProcessorConfig(
       detection_enabled=True,
       ocr_enabled=True,
       scene_detection_threshold=0.4,
       max_frames=1000,
       batch_size=32
   )
   processor = VideoProcessor(config)
