"""Object detection module for video processing.

This module provides object detection functionality using YOLOv8.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np
from ultralytics import YOLO

from video_understanding.utils.exceptions import ProcessingError


@dataclass
class DetectedObject:
    """Represents a detected object in a video frame.

    Attributes:
        label: Object class label
        confidence: Detection confidence score
        bbox: Bounding box coordinates [x1, y1, x2, y2]
        frame_number: Frame number where object was detected
    """

    label: str
    confidence: float
    bbox: List[float]
    frame_number: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert detection to dictionary format.

        Returns:
            Dictionary representation of detection
        """
        return {
            "label": self.label,
            "confidence": self.confidence,
            "bbox": self.bbox,
            "frame_number": self.frame_number,
        }


class ObjectDetector:
    """YOLOv8-based object detector for video frames.

    This class handles object detection in video frames using YOLOv8.
    It supports configurable confidence thresholds and model paths.

    Example:
        >>> detector = ObjectDetector()
        >>> frame = cv2.imread("frame.jpg")
        >>> detections = detector.detect_objects(frame)
        >>> for obj in detections:
        ...     print(f"Found {obj.label} with confidence {obj.confidence}")
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence_threshold: float = 0.5,
    ) -> None:
        """Initialize the object detector.

        Args:
            model_path: Path to YOLOv8 model weights (uses yolov8n.pt if None)
            confidence_threshold: Minimum confidence threshold for detections

        Raises:
            ProcessingError: If model initialization fails
        """
        try:
            self.model = YOLO(model_path or "yolov8n.pt")
            self.confidence_threshold = confidence_threshold
        except Exception as e:
            raise ProcessingError(f"Failed to initialize object detector: {e}")

    def detect_objects(
        self,
        frame: np.ndarray,
        frame_number: Optional[int] = None,
    ) -> List[DetectedObject]:
        """Detect objects in a video frame.

        Args:
            frame: Input frame as numpy array (BGR format)
            frame_number: Optional frame number for tracking

        Returns:
            List of detected objects

        Raises:
            ProcessingError: If detection fails
        """
        try:
            # Run inference
            results = self.model(frame, verbose=False)[0]
            detections = []

            # Process results
            for box in results.boxes:
                if box.conf.item() < self.confidence_threshold:
                    continue

                # Get detection info
                label = results.names[box.cls.item()]
                confidence = box.conf.item()
                bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]

                # Create detection object
                detection = DetectedObject(
                    label=label,
                    confidence=confidence,
                    bbox=bbox,
                    frame_number=frame_number or 0,
                )
                detections.append(detection)

            return detections

        except Exception as e:
            raise ProcessingError(f"Object detection failed: {e}")

    def __call__(
        self,
        frame: np.ndarray,
        frame_number: Optional[int] = None,
    ) -> List[DetectedObject]:
        """Callable interface for object detection.

        Args:
            frame: Input frame
            frame_number: Optional frame number

        Returns:
            List of detected objects
        """
        return self.detect_objects(frame, frame_number)
