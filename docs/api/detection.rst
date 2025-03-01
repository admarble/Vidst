Object Detection API
====================

Detection Components
--------------------

The object detection system provides functionality for identifying and tracking objects within video frames.

ObjectDetector
~~~~~~~~~~~~

.. py:class:: ObjectDetector(model_config: ModelConfig)

   Main class for object detection in video frames.

   :param model_config: Configuration for the detection model
   :type model_config: ModelConfig

Methods
^^^^^^^

.. py:method:: detect_objects(frame: np.ndarray) -> List[Detection]

   Detects objects in a single frame.

   :param frame: Input frame as numpy array
   :type frame: np.ndarray
   :return: List of detected objects
   :rtype: List[Detection]

.. py:method:: batch_detect(frames: List[np.ndarray]) -> List[List[Detection]]

   Performs batch detection on multiple frames.

   :param frames: List of input frames
   :type frames: List[np.ndarray]
   :return: List of detection results for each frame
   :rtype: List[List[Detection]]

Detection Classes
~~~~~~~~~~~~~~

.. py:class:: Detection

   Represents a detected object in a frame.

   .. py:attribute:: bbox
      :type: BoundingBox

      Bounding box coordinates of the detected object.

   .. py:attribute:: confidence
      :type: float

      Detection confidence score.

   .. py:attribute:: class_id
      :type: int

      Class identifier for the detected object.

   .. py:attribute:: class_name
      :type: str

      Human-readable name of the detected class.

.. py:class:: BoundingBox

   Represents a bounding box in normalized coordinates.

   .. py:attribute:: x1
      :type: float

      Normalized left coordinate.

   .. py:attribute:: y1
      :type: float

      Normalized top coordinate.

   .. py:attribute:: x2
      :type: float

      Normalized right coordinate.

   .. py:attribute:: y2
      :type: float

      Normalized bottom coordinate.

Configuration
~~~~~~~~~~~

.. py:class:: ModelConfig

   Configuration for the detection model.

   .. py:attribute:: confidence_threshold
      :type: float

      Minimum confidence threshold for detections.

   .. py:attribute:: nms_threshold
      :type: float

      Non-maximum suppression threshold.

   .. py:attribute:: model_type
      :type: str

      Type of detection model to use.

Usage Examples
~~~~~~~~~~~

Basic Detection
^^^^^^^^^^^^^^^

.. code-block:: python

   from video_understanding import ObjectDetector, ModelConfig

   # Initialize detector
   config = ModelConfig(
         confidence_threshold=0.5,
         nms_threshold=0.4,
         model_type="yolov5"
   )
   detector = ObjectDetector(config)

   # Detect objects in a frame
   detections = detector.detect_objects(frame)
   for detection in detections:
         print(f"Found {detection.class_name} with confidence {detection.confidence}")

Batch Processing
^^^^^^^^^^^^^^^^

.. code-block:: python

   # Process multiple frames at once
   frames = [frame1, frame2, frame3]
   batch_results = detector.batch_detect(frames)

   for frame_idx, detections in enumerate(batch_results):
         print(f"Frame {frame_idx}: Found {len(detections)} objects")
