"""OCR module for text extraction from video frames.

This module provides text extraction functionality using EasyOCR.
"""

from dataclasses import dataclass
from typing import Any, List, Dict, Optional

import easyocr
import numpy as np
import logging
from pathlib import Path
import cv2

from video_understanding.core.exceptions import OCRError

logger = logging.getLogger(__name__)


@dataclass
class ExtractedText:
    """Container for extracted text data.

    Attributes:
        text: The extracted text string
        confidence: Confidence score for the extraction
        bounding_box: Coordinates of text bounding box
    """

    text: str
    confidence: float
    bounding_box: list[list[int]]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary containing text data
        """
        return {
            "text": self.text,
            "confidence": self.confidence,
            "bounding_box": self.bounding_box,
        }


class TextExtractor:
    """Text extraction from images using EasyOCR."""

    def __init__(
        self,
        languages: list[str] | None = None,
        confidence_threshold: float = 0.5,
        gpu: bool = False,
    ) -> None:
        """Initialize text extractor.

        Args:
            languages: List of languages to detect
            confidence_threshold: Minimum confidence threshold
            gpu: Whether to use GPU
        """
        try:
            self.reader = easyocr.Reader(languages or ["en"], gpu=gpu)
            self.confidence_threshold = confidence_threshold
        except Exception as e:
            raise OCRError("Failed to initialize EasyOCR") from e

    def extract_text(self, frame: np.ndarray) -> list[ExtractedText]:
        """Extract text from a video frame.

        Args:
            frame: Video frame as numpy array

        Returns:
            List of extracted text results

        Raises:
            OCRError: If text extraction fails
        """
        try:
            results = self.reader.readtext(frame)
            extracted = []
            for bbox, text, conf in results:
                if conf >= self.confidence_threshold:
                    extracted.append(
                        ExtractedText(
                            text=text,
                            confidence=conf,
                            bounding_box=bbox,
                        )
                    )
            return extracted
        except Exception as e:
            raise OCRError("Failed to extract text from frame") from e


class OCRProcessor:
    """Processes video frames for text extraction."""

    def __init__(self, languages: Optional[List[str]] = None):
        """Initialize OCR processor.

        Args:
            languages: List of language codes to detect
        """
        self.languages = languages or ["eng"]
        self.confidence_threshold = 0.7

    async def process(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process video file for text extraction.

        Args:
            file_path: Path to video file

        Returns:
            List of text extraction results

        Raises:
            FileNotFoundError: If the video file does not exist
            OCRError: If text extraction fails
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Video file not found: {file_path}")

        results = []
        cap = cv2.VideoCapture(str(file_path))

        if not cap.isOpened():
            cap.release()
            raise OCRError(f"Failed to open video file: {file_path}")

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Process frame
                frame_results = await self._process_frame(frame)
                if frame_results:
                    results.extend(frame_results)

        finally:
            cap.release()

        return results

    async def _process_frame(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Process a single frame for text extraction.

        Args:
            frame: Video frame as numpy array

        Returns:
            List of text extraction results for frame
        """
        # TODO: Implement actual OCR processing
        # This is a placeholder that returns no results
        return []

    def set_confidence_threshold(self, threshold: float) -> None:
        """Set confidence threshold for text detection.

        Args:
            threshold: Confidence threshold (0.0 to 1.0)
        """
        self.confidence_threshold = max(0.0, min(1.0, threshold))
