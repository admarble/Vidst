import pytest
from src.core.exceptions import (
    VideoProcessingError,
    FileValidationError,
    ProcessingError,
    StorageError
)

def test_video_processing_error():
    """Test VideoProcessingError base exception"""
    with pytest.raises(VideoProcessingError) as exc_info:
        raise VideoProcessingError("Test error message")
    assert str(exc_info.value) == "Test error message"
    
    # Test inheritance
    error = VideoProcessingError()
    assert isinstance(error, Exception)

def test_file_validation_error():
    """Test FileValidationError"""
    with pytest.raises(FileValidationError) as exc_info:
        raise FileValidationError("Invalid file")
    assert str(exc_info.value) == "Invalid file"
    
    # Test inheritance
    error = FileValidationError()
    assert isinstance(error, VideoProcessingError)
    assert isinstance(error, Exception)

def test_processing_error():
    """Test ProcessingError"""
    with pytest.raises(ProcessingError) as exc_info:
        raise ProcessingError("Processing failed")
    assert str(exc_info.value) == "Processing failed"
    
    # Test inheritance
    error = ProcessingError()
    assert isinstance(error, VideoProcessingError)
    assert isinstance(error, Exception)

def test_storage_error():
    """Test StorageError"""
    with pytest.raises(StorageError) as exc_info:
        raise StorageError("Storage operation failed")
    assert str(exc_info.value) == "Storage operation failed"
    
    # Test inheritance
    error = StorageError()
    assert isinstance(error, VideoProcessingError)
    assert isinstance(error, Exception)

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