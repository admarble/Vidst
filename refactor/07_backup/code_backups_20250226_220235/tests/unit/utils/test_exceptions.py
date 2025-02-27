"""Unit tests for utility exceptions."""

import pytest
from video_understanding.utils.exceptions import (
    VideoUnderstandingError,
    ValidationError,
    VideoFormatError,
    VideoIntegrityError,
    SecurityError,
    StorageError,
    ProcessingError,
    QuarantineError,
)


def test_base_exception():
    """Test the base VideoUnderstandingError."""
    error_msg = "Base error"
    with pytest.raises(VideoUnderstandingError) as exc_info:
        raise VideoUnderstandingError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, Exception)


def test_validation_error():
    """Test ValidationError exception."""
    error_msg = "Validation failed"
    with pytest.raises(ValidationError) as exc_info:
        raise ValidationError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, VideoUnderstandingError)


def test_video_format_error():
    """Test VideoFormatError exception."""
    error_msg = "Unsupported video format"
    with pytest.raises(VideoFormatError) as exc_info:
        raise VideoFormatError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, ValidationError)
    assert isinstance(exc_info.value, VideoUnderstandingError)


def test_video_integrity_error():
    """Test VideoIntegrityError exception."""
    error_msg = "Video file corrupted"
    with pytest.raises(VideoIntegrityError) as exc_info:
        raise VideoIntegrityError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, ValidationError)
    assert isinstance(exc_info.value, VideoUnderstandingError)


def test_security_error():
    """Test SecurityError exception."""
    error_msg = "Security check failed"
    with pytest.raises(SecurityError) as exc_info:
        raise SecurityError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, VideoUnderstandingError)


def test_storage_error():
    """Test StorageError exception."""
    error_msg = "Storage operation failed"
    with pytest.raises(StorageError) as exc_info:
        raise StorageError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, VideoUnderstandingError)


def test_processing_error():
    """Test ProcessingError exception."""
    error_msg = "Processing failed"
    with pytest.raises(ProcessingError) as exc_info:
        raise ProcessingError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, VideoUnderstandingError)


def test_quarantine_error():
    """Test QuarantineError exception."""
    error_msg = "Quarantine operation failed"
    with pytest.raises(QuarantineError) as exc_info:
        raise QuarantineError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, VideoUnderstandingError)


def test_exception_hierarchy():
    """Test the exception class hierarchy."""
    # Test base class relationships
    assert issubclass(ValidationError, VideoUnderstandingError)
    assert issubclass(SecurityError, VideoUnderstandingError)
    assert issubclass(StorageError, VideoUnderstandingError)
    assert issubclass(ProcessingError, VideoUnderstandingError)
    assert issubclass(QuarantineError, VideoUnderstandingError)

    # Test validation error hierarchy
    assert issubclass(VideoFormatError, ValidationError)
    assert issubclass(VideoIntegrityError, ValidationError)
    assert issubclass(VideoFormatError, VideoUnderstandingError)
    assert issubclass(VideoIntegrityError, VideoUnderstandingError)


def test_exception_with_details():
    """Test exceptions with additional details."""
    # Test format error with details
    format_details = {
        "file": "video.avi",
        "format": "AVI",
        "supported_formats": ["MP4", "MOV"]
    }
    format_msg = f"Unsupported format: {format_details}"
    with pytest.raises(VideoFormatError) as exc_info:
        raise VideoFormatError(format_msg)
    assert all(key in str(exc_info.value) for key in format_details.keys())

    # Test integrity error with details
    integrity_details = {
        "file": "video.mp4",
        "check": "checksum",
        "expected": "abc123",
        "actual": "def456"
    }
    integrity_msg = f"Integrity check failed: {integrity_details}"
    with pytest.raises(VideoIntegrityError) as exc_info:
        raise VideoIntegrityError(integrity_msg)
    assert all(key in str(exc_info.value) for key in integrity_details.keys())
