Scene Detection API
================

Scene Analysis Components
----------------------

The scene detection system provides functionality for identifying and analyzing scene changes in videos.

SceneDetector
~~~~~~~~~~~

.. py:class:: SceneDetector(config: SceneConfig)

   Main class for scene detection and analysis.

   :param config: Configuration for scene detection
   :type config: SceneConfig

Methods
^^^^^^^

.. py:method:: detect_scenes(video: Video) -> List[Scene]

   Detects scene changes in a video.

   :param video: Input video object
   :type video: Video
   :return: List of detected scenes
   :rtype: List[Scene]

.. py:method:: analyze_scene(scene: Scene) -> SceneAnalysis

   Performs detailed analysis of a scene.

   :param scene: Scene object to analyze
   :type scene: Scene
   :return: Analysis results for the scene
   :rtype: SceneAnalysis

Scene Classes
~~~~~~~~~~

.. py:class:: Scene

   Represents a detected scene in a video.

   .. py:attribute:: start_time
      :type: float

      Start time of the scene in seconds.

   .. py:attribute:: end_time
      :type: float

      End time of the scene in seconds.

   .. py:attribute:: keyframe
      :type: np.ndarray

      Representative frame for the scene.

   .. py:attribute:: scene_type
      :type: str

      Type of scene (e.g., "presentation", "demonstration", "discussion").

.. py:class:: SceneAnalysis

   Results of scene analysis.

   .. py:attribute:: content_summary
      :type: str

      Summary of scene content.

   .. py:attribute:: detected_objects
      :type: List[Detection]

      Objects detected in the scene.

   .. py:attribute:: text_content
      :type: List[TextRegion]

      Text extracted from the scene.

Configuration
~~~~~~~~~~~

.. py:class:: SceneConfig

   Configuration for scene detection.

   .. py:attribute:: threshold
      :type: float

      Threshold for scene change detection.

   .. py:attribute:: min_scene_length
      :type: float

      Minimum length of a scene in seconds.

   .. py:attribute:: analyze_content
      :type: bool

      Enable detailed content analysis.

Usage Examples
~~~~~~~~~~~

Basic Scene Detection
^^^^^^^^^^^^^^^^^

.. code-block:: python

   from video_understanding import SceneDetector, SceneConfig

   # Initialize detector
   config = SceneConfig(
       threshold=0.3,
       min_scene_length=2.0,
       analyze_content=True
   )
   detector = SceneDetector(config)

   # Detect scenes
   scenes = detector.detect_scenes(video)
   for scene in scenes:
       print(f"Scene from {scene.start_time}s to {scene.end_time}s")

Scene Analysis
^^^^^^^^^^^

.. code-block:: python

   # Analyze specific scene
   scene = scenes[0]
   analysis = detector.analyze_scene(scene)

   print(f"Scene summary: {analysis.content_summary}")
   print(f"Objects detected: {len(analysis.detected_objects)}")
   print(f"Text regions found: {len(analysis.text_content)}")

Advanced Usage
^^^^^^^^^^^

.. code-block:: python

   # Configure for presentation analysis
   config = SceneConfig(
       threshold=0.4,
       min_scene_length=5.0,
       analyze_content=True,
       detect_presentations=True
   )
   detector = SceneDetector(config)

   # Process video
   scenes = detector.detect_scenes(video)
   presentations = [s for s in scenes if s.scene_type == "presentation"]

   for scene in presentations:
       analysis = detector.analyze_scene(scene)
       print(f"Presentation content: {analysis.content_summary}")
