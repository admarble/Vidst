OCR API
=======

Text Recognition Components
---------------------------

The OCR system provides functionality for extracting and processing text from video frames.

TextRecognizer
~~~~~~~~~~~~

.. py:class:: TextRecognizer(config: OCRConfig)

   Main class for text recognition in video frames.

   :param config: Configuration for OCR processing
   :type config: OCRConfig

Methods
^^^^^^^

.. py:method:: extract_text(frame: np.ndarray) -> List[TextRegion]

   Extracts text regions from a single frame.

   :param frame: Input frame as numpy array
   :type frame: np.ndarray
   :return: List of detected text regions
   :rtype: List[TextRegion]

.. py:method:: batch_extract(frames: List[np.ndarray]) -> List[List[TextRegion]]

   Performs batch text extraction on multiple frames.

   :param frames: List of input frames
   :type frames: List[np.ndarray]
   :return: List of text regions for each frame
   :rtype: List[List[TextRegion]]

Text Classes
~~~~~~~~~~

.. py:class:: TextRegion

   Represents a region of text in a frame.

   .. py:attribute:: bbox
      :type: BoundingBox

      Bounding box coordinates of the text region.

   .. py:attribute:: text
      :type: str

      Extracted text content.

   .. py:attribute:: confidence
      :type: float

      OCR confidence score.

   .. py:attribute:: type
      :type: str

      Type of text (e.g., "paragraph", "heading", "code").

Configuration
~~~~~~~~~~~

.. py:class:: OCRConfig

   Configuration for the OCR system.

   .. py:attribute:: language
      :type: str

      Primary language for OCR.

   .. py:attribute:: min_confidence
      :type: float

      Minimum confidence threshold for text detection.

   .. py:attribute:: enable_layout_analysis
      :type: bool

      Enable advanced layout analysis.

Usage Examples
~~~~~~~~~~~

Basic Text Extraction
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from video_understanding import TextRecognizer, OCRConfig

   # Initialize recognizer
   config = OCRConfig(
         language="en",
         min_confidence=0.7,
         enable_layout_analysis=True
   )
   recognizer = TextRecognizer(config)

   # Extract text from a frame
   text_regions = recognizer.extract_text(frame)
   for region in text_regions:
         print(f"Found text: {region.text} ({region.confidence})")

Code Block Detection
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Configure for code detection
   config = OCRConfig(
         language="en",
         min_confidence=0.8,
         enable_layout_analysis=True,
         detect_code_blocks=True
   )
   recognizer = TextRecognizer(config)

   # Process frame
   text_regions = recognizer.extract_text(frame)
   code_blocks = [r for r in text_regions if r.type == "code"]

   for block in code_blocks:
         print(f"Found code block:\n{block.text}")
