from typing import Dict, List, Any
from abc import ABC, abstractmethod
import numpy as np


class BaseOCRService(ABC):
    """Base interface for OCR service implementations."""

    @abstractmethod
    def extract_text(
        self,
        image: np.ndarray,
        detect_language: bool = False,
        confidence_threshold: float = 0.7,
    ) -> Dict[str, Any]:
        """Extract text from an image.

        Args:
            image: Numpy array of image data
            detect_language: Whether to detect language
            confidence_threshold: Minimum confidence for returned results

        Returns:
            Dictionary containing:
                text: Extracted text
                blocks: List of text blocks with positions
                confidence: Overall confidence score
                language: Detected language (if detect_language=True)

        Raises:
            OCRServiceError: If there's an error during text extraction
        """
        pass

    @abstractmethod
    def batch_extract_text(
        self,
        images: List[np.ndarray],
        max_batch_size: int = 10,
        detect_language: bool = False,
        confidence_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Extract text from multiple images.

        Args:
            images: List of numpy arrays of image data
            max_batch_size: Maximum batch size for processing
            detect_language: Whether to detect language
            confidence_threshold: Minimum confidence for returned results

        Returns:
            List of dictionaries with extraction results

        Raises:
            OCRServiceError: If there's an error during batch text extraction
        """
        pass

    @abstractmethod
    def detect_tables(
        self,
        image: np.ndarray,
        confidence_threshold: float = 0.7,
    ) -> Dict[str, Any]:
        """Detect tables in an image.

        Args:
            image: Numpy array of image data
            confidence_threshold: Minimum confidence for returned results

        Returns:
            Dictionary containing:
                tables: List of detected tables with positions and content
                confidence: Overall confidence score

        Raises:
            OCRServiceError: If there's an error during table detection
        """
        pass
