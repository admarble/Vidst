"""Unit tests for main video understanding exceptions."""

import pytest
from video_understanding.exceptions import (
    VideoUnderstandingError,
    SecurityError,
    IntegrityError,
    ProcessingError,
    ConfigurationError,
    UploadError,
    StorageError,
    AIModelError,
    ValidationError,
    ResourceError,
)


def test_base_exception():
    """Test the base VideoUnderstandingError."""
    error_msg = "Base error"
    with pytest.raises(VideoUnderstandingError) as exc_info:
        raise VideoUnderstandingError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, Exception)


def test_security_error():
    """Test SecurityError exception."""
    error_msg = "Security violation detected"
    with pytest.raises(SecurityError) as exc_info:
        raise SecurityError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, VideoUnderstandingError)


def test_integrity_error():
    """Test IntegrityError exception."""
    error_msg = "File integrity check failed"
    with pytest.raises(IntegrityError) as exc_info:
        raise IntegrityError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, VideoUnderstandingError)


def test_processing_error():
    """Test ProcessingError exception."""
    error_msg = "Video processing failed"
    with pytest.raises(ProcessingError) as exc_info:
        raise ProcessingError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, VideoUnderstandingError)


def test_configuration_error():
    """Test ConfigurationError exception."""
    error_msg = "Invalid configuration"
    with pytest.raises(ConfigurationError) as exc_info:
        raise ConfigurationError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, VideoUnderstandingError)


def test_upload_error():
    """Test UploadError exception."""
    error_msg = "Upload failed"
    with pytest.raises(UploadError) as exc_info:
        raise UploadError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, VideoUnderstandingError)


def test_storage_error():
    """Test StorageError exception."""
    error_msg = "Storage operation failed"
    with pytest.raises(StorageError) as exc_info:
        raise StorageError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, VideoUnderstandingError)


def test_ai_model_error():
    """Test AIModelError exception."""
    error_msg = "Model inference failed"
    with pytest.raises(AIModelError) as exc_info:
        raise AIModelError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, VideoUnderstandingError)


def test_validation_error():
    """Test ValidationError exception."""
    error_msg = "Validation failed"
    with pytest.raises(ValidationError) as exc_info:
        raise ValidationError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, VideoUnderstandingError)


def test_resource_error():
    """Test ResourceError exception."""
    error_msg = "Resource not available"
    with pytest.raises(ResourceError) as exc_info:
        raise ResourceError(error_msg)
    assert str(exc_info.value) == error_msg
    assert isinstance(exc_info.value, VideoUnderstandingError)


def test_exception_hierarchy():
    """Test the exception class hierarchy."""
    # All exceptions should inherit from VideoUnderstandingError
    assert issubclass(SecurityError, VideoUnderstandingError)
    assert issubclass(IntegrityError, VideoUnderstandingError)
    assert issubclass(ProcessingError, VideoUnderstandingError)
    assert issubclass(ConfigurationError, VideoUnderstandingError)
    assert issubclass(UploadError, VideoUnderstandingError)
    assert issubclass(StorageError, VideoUnderstandingError)
    assert issubclass(AIModelError, VideoUnderstandingError)
    assert issubclass(ValidationError, VideoUnderstandingError)
    assert issubclass(ResourceError, VideoUnderstandingError)


def test_exception_with_details():
    """Test exceptions with additional details."""
    details = {
        "operation": "file_upload",
        "file": "video.mp4",
        "reason": "file too large"
    }
    error_msg = f"Upload failed: {details}"

    with pytest.raises(UploadError) as exc_info:
        raise UploadError(error_msg)

    assert str(exc_info.value) == error_msg
    assert all(key in str(exc_info.value) for key in details.keys())
