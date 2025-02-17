"""Tests for custom exceptions."""

import pytest

from src.core.exceptions import (
    FileValidationError,
    ProcessingError,
    StorageError,
    VideoProcessingError,
)


def test_video_processing_error():
    """Test VideoProcessingError can be raised with message."""
    with pytest.raises(VideoProcessingError) as exc_info:
        raise VideoProcessingError("Test error")
    assert str(exc_info.value) == "Test error"


def test_file_validation_error():
    """Test FileValidationError inherits correctly and can be raised."""
    with pytest.raises(FileValidationError) as exc_info:
        raise FileValidationError("Invalid file")
    assert str(exc_info.value) == "Invalid file"
    assert isinstance(exc_info.value, VideoProcessingError)


def test_processing_error():
    """Test ProcessingError inherits correctly and can be raised."""
    with pytest.raises(ProcessingError) as exc_info:
        raise ProcessingError("Processing failed")
    assert str(exc_info.value) == "Processing failed"
    assert isinstance(exc_info.value, VideoProcessingError)


def test_storage_error():
    """Test StorageError inherits correctly and can be raised."""
    with pytest.raises(StorageError) as exc_info:
        raise StorageError("Storage operation failed")
    assert str(exc_info.value) == "Storage operation failed"
    assert isinstance(exc_info.value, VideoProcessingError)


def test_exception_chaining():
    """Test exception chaining"""
    try:
        try:
            raise FileValidationError("Original error")
        except FileValidationError as e:
            raise ProcessingError("Chained error") from e
    except ProcessingError as e:
        assert isinstance(e.__cause__, FileValidationError)
        assert str(e.__cause__) == "Original error"
        assert str(e) == "Chained error"
