"""OCR module for text extraction from video frames.

This module provides text extraction functionality using EasyOCR.
"""

from dataclasses import dataclass
from typing import Any

import easyocr
import numpy as np

from video_understanding.core.exceptions import OCRError


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
