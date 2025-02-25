import pytest
from unittest.mock import Mock, patch
import numpy as np
from src.core.processing.text import OCRProcessor, TextDetector

class TestOCRProcessor:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
        self.processor = OCRProcessor()

    def test_basic_text_extraction(self):
        """Test basic text extraction from an image."""
        mock_text = "Sample text in video"
        with patch('src.core.processing.text.ocr.extract_text', return_value=mock_text):
            result = self.processor.process_frame(self.test_image)
            assert isinstance(result, dict)
            assert "text" in result
            assert result["text"] == mock_text

    def test_text_with_timestamps(self):
        """Test text extraction with timestamp information."""
        result = self.processor.process_frame(self.test_image, timestamp=10.5)
        assert "timestamp" in result
        assert result["timestamp"] == 10.5

    def test_multiple_text_regions(self):
        """Test handling of multiple text regions in a frame."""
        mock_regions = [
            {"text": "Region 1", "confidence": 0.95, "bbox": (10, 10, 100, 30)},
            {"text": "Region 2", "confidence": 0.88, "bbox": (200, 200, 300, 230)}
        ]
        with patch('src.core.processing.text.ocr.detect_text_regions', return_value=mock_regions):
            result = self.processor.process_frame(self.test_image)
            assert "regions" in result
            assert len(result["regions"]) == 2
            assert all("confidence" in region for region in result["regions"])

class TestTextDetector:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.detector = TextDetector()
        self.test_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

    def test_code_block_detection(self):
        """Test detection of code blocks in frame."""
        result = self.detector.detect_code_blocks(self.test_frame)
        assert isinstance(result, list)
        for block in result:
            assert "type" in block
            assert "content" in block
            assert "confidence" in block

    def test_text_formatting_detection(self):
        """Test detection of text formatting (bold, italic, etc.)."""
        result = self.detector.detect_formatting(self.test_frame)
        assert isinstance(result, dict)
        assert "formatting" in result
        assert isinstance(result["formatting"], list)

    def test_confidence_filtering(self):
        """Test filtering of low-confidence detections."""
        detector = TextDetector(min_confidence=0.8)
        result = detector.detect_text(self.test_frame)
        assert all(r["confidence"] >= 0.8 for r in result if "confidence" in r)
