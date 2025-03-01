Getting Started
===============

This guide will help you get started with the Video Understanding AI system.

Installation
------------

1. Install the package using pip:

   .. code-block:: bash

      pip install video-understanding-ai

2. Install additional dependencies:

   .. code-block:: bash

      pip install -r requirements.txt

Configuration
-------------

1. Set up your API keys:

   .. code-block:: bash

      export OPENAI_API_KEY="your-key-here"
      export TWELVE_LABS_API_KEY="your-key-here"

   Or create a `.env` file:

   .. code-block:: text

      OPENAI_API_KEY=your-key-here
      TWELVE_LABS_API_KEY=your-key-here

2. Basic configuration:

   .. code-block:: python

      from video_understanding import ProcessorConfig

      config = ProcessorConfig(
            detection_enabled=True,
            ocr_enabled=True
      )

Quick Start
-----------

Here's a simple example to get you started:

.. code-block:: python

   from video_understanding import VideoProcessor, ProcessorConfig, Video

   # Load video
   video = Video.from_file("path/to/video.mp4")

   # Configure processor
   config = ProcessorConfig(
         detection_enabled=True,
         ocr_enabled=True
   )
   processor = VideoProcessor(config)

   # Process video
   with processor.process(video) as context:
         results = processor.analyze_frames(context)
         print(f"Found {len(results['objects'])} objects")

Advanced Usage
--------------

Scene Detection
^^^^^^^^^^^^^^^

Detect and analyze scenes in your video:

.. code-block:: python

   from video_understanding import SceneDetector, SceneConfig

   # Configure scene detector
   scene_config = SceneConfig(
         threshold=0.3,
         min_scene_length=2.0,
         analyze_content=True
   )
   detector = SceneDetector(scene_config)

   # Detect scenes
   scenes = detector.detect_scenes(video)
   for scene in scenes:
         print(f"Scene from {scene.start_time}s to {scene.end_time}s")

Text Recognition
^^^^^^^^^^^^^^^^

Extract text from video frames:

.. code-block:: python

   from video_understanding import TextRecognizer, OCRConfig

   # Configure text recognizer
   ocr_config = OCRConfig(
         language="en",
         min_confidence=0.7,
         enable_layout_analysis=True
   )
   recognizer = TextRecognizer(ocr_config)

   # Extract text from frame
   text_regions = recognizer.extract_text(frame)
   for region in text_regions:
         print(f"Found text: {region.text}")

Object Detection
^^^^^^^^^^^^^^^^

Detect objects in video frames:

.. code-block:: python

   from video_understanding import ObjectDetector, ModelConfig

   # Configure object detector
   detector_config = ModelConfig(
         confidence_threshold=0.5,
         nms_threshold=0.4,
         model_type="yolov5"
   )
   detector = ObjectDetector(detector_config)

   # Detect objects
   detections = detector.detect_objects(frame)
   for detection in detections:
         print(f"Found {detection.class_name}")

Best Practices
--------------

1. Memory Management
   - Process videos in chunks for large files
   - Use context managers for proper resource cleanup
   - Enable caching for repeated operations

2. Performance Optimization
   - Use batch processing when possible
   - Enable only needed components
   - Adjust confidence thresholds based on needs

3. Error Handling
   - Always use try-except blocks
   - Validate video files before processing
   - Check API rate limits

Common Issues
-------------

1. Memory Issues
   Solution: Process video in smaller chunks

   .. code-block:: python

      with processor.process(video, chunk_size=1000) as context:
            results = processor.analyze_frames(context)

2. Performance
   Solution: Enable batch processing

   .. code-block:: python

      config = ProcessorConfig(
            batch_size=32,
            enable_batching=True
      )

3. API Rate Limits
   Solution: Implement retry mechanism

   .. code-block:: python

      from video_understanding.utils import retry_with_backoff

      @retry_with_backoff(max_retries=3)
      def process_video(video):
            with processor.process(video) as context:
               return processor.analyze_frames(context)

Next Steps
----------

- Check out the :doc:`../api/index` for detailed API documentation
- See :doc:`../examples/index` for more examples
- Read the :doc:`configuration` guide for advanced settings
- Join our `Discord community <https://discord.gg/video-understanding>`_ for help
