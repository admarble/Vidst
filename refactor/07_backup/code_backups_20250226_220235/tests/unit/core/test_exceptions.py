import pytest
from video_understanding.core.exceptions import (
    VideoUnderstandingError,
    ValidationError,
    ProcessingError,
    StorageError,
    ConfigurationError,
    APIError,
    ModelError,
    ResourceError,
    SystemError,
    TimeoutError,
    MemoryError,
    PipelineError,
    VideoFormatError,
    VideoProcessingError,
    AudioProcessingError,
    TranscriptionError,
    OCRError,
    RateLimitError,
    AuthenticationError,
    ResourceNotFoundError,
    ResourceExistsError,
    ConcurrencyError,
    DependencyError,
    ModelLoadError,
    ModelInferenceError,
    StageError,
    FileValidationError,
    OutputError,
    CustomTimeoutError,
    CustomMemoryError,
    TwelveLabsError,
    TaskError,
    ResourceExceededError,
    ConcurrencyLimitError,
    SecurityError,
    IntegrityError,
    UploadError,
    handle_error,
    ERROR_MAP,
)
import builtins

def test_base_exception_with_cause():
    """Test VideoUnderstandingError with a cause."""
    cause = ValueError("Original error")
    error = VideoUnderstandingError("Test error", cause=cause)
    assert str(error) == "Test error"
    assert error.cause == cause

def test_file_validation_error_with_cause():
    """Test FileValidationError with a cause."""
    cause = OSError("File system error")
    error = FileValidationError("Invalid file", cause=cause)
    assert str(error) == "Invalid file"
    assert error.cause == cause

def test_error_mapping():
    """Test error mapping for standard Python exceptions."""
    test_cases = [
        (ValueError("Invalid value"), ValidationError),
        (FileNotFoundError("File not found"), ResourceNotFoundError),
        (PermissionError("Permission denied"), AuthenticationError),
        (builtins.TimeoutError("Operation timed out"), VideoUnderstandingError),  # Built-in TimeoutError maps to base class
        (MemoryError("Out of memory"), VideoUnderstandingError),  # MemoryError maps to base class
        (ImportError("Import failed"), DependencyError),
        (RuntimeError("Runtime error"), ProcessingError),
        (NotImplementedError("Not implemented"), ProcessingError),
        (OSError("OS error"), StorageError),
        (IOError("IO error"), StorageError),
        (KeyError("Key error"), ValidationError),
        (TypeError("Type error"), ValidationError),
        (IndexError("Index error"), ValidationError),
        (AttributeError("Attribute error"), ConfigurationError),
        (ModuleNotFoundError("Module not found"), DependencyError),
        (ConnectionError("Connection failed"), APIError),
        (InterruptedError("Operation interrupted"), ConcurrencyError),
        (BlockingIOError("IO blocked"), ConcurrencyError),
        (BrokenPipeError("Pipe broken"), StorageError),
        (BufferError("Buffer error"), CustomMemoryError),
        (LookupError("Lookup failed"), ResourceNotFoundError),
    ]

    for original_error, expected_type in test_cases:
        converted = handle_error(original_error)
        assert isinstance(converted, expected_type)
        assert str(converted) == str(original_error)

def test_handle_error_with_custom_exception():
    """Test handle_error with an already custom exception."""
    custom_error = ValidationError("Already custom")
    result = handle_error(custom_error)
    assert result is custom_error  # Should return the same instance

def test_handle_error_with_unknown_exception():
    """Test handle_error with an unknown exception type."""
    class UnknownError(Exception):
        pass

    unknown = UnknownError("Unknown error")
    result = handle_error(unknown)
    assert isinstance(result, VideoUnderstandingError)
    assert str(result) == "Unknown error"

def test_handle_error_with_nested_cause():
    """Test handle_error with nested exception causes."""
    try:
        try:
            try:
                raise ValueError("Root cause")
            except ValueError as ve:
                raise OSError("Middle cause") from ve
        except OSError as oe:
            raise TypeError("Top error") from oe
    except TypeError as te:
        # Handle the top-level error
        result = handle_error(te)

        # Verify top-level error
        assert isinstance(result, ValidationError)
        assert str(result) == "Top error"

        # Verify middle error
        assert isinstance(result.cause, StorageError)
        assert str(result.cause) == "Middle cause"

        # Verify root error
        assert isinstance(result.cause.cause, ValidationError)
        assert str(result.cause.cause) == "Root cause"

        # Verify the chain ends here
        assert result.cause.cause.cause is None

def test_error_hierarchy():
    """Test the exception hierarchy relationships."""
    assert issubclass(ValidationError, VideoUnderstandingError)
    assert issubclass(ProcessingError, VideoUnderstandingError)
    assert issubclass(VideoFormatError, ProcessingError)
    assert issubclass(VideoProcessingError, ProcessingError)
    assert issubclass(AudioProcessingError, ProcessingError)
    assert issubclass(TranscriptionError, AudioProcessingError)
    assert issubclass(OCRError, ProcessingError)
    assert issubclass(RateLimitError, APIError)
    assert issubclass(AuthenticationError, APIError)
    assert issubclass(TwelveLabsError, APIError)
    assert issubclass(TaskError, TwelveLabsError)
    assert issubclass(ResourceExceededError, VideoProcessingError)
    assert issubclass(ConcurrencyLimitError, VideoProcessingError)

def test_error_map_completeness():
    """Test that all mapped exception types are valid."""
    for original_type, custom_type in ERROR_MAP.items():
        assert issubclass(original_type, BaseException)
        assert issubclass(custom_type, VideoUnderstandingError)

def test_additional_error_types():
    """Test additional error types that weren't covered."""
    # Test SystemError
    with pytest.raises(SystemError) as exc_info:
        raise SystemError("System failure")
    assert isinstance(exc_info.value, VideoUnderstandingError)
    assert str(exc_info.value) == "System failure"

    # Test TimeoutError
    with pytest.raises(TimeoutError) as exc_info:
        raise TimeoutError("Operation timeout")
    assert isinstance(exc_info.value, VideoUnderstandingError)
    assert str(exc_info.value) == "Operation timeout"

    # Test MemoryError
    with pytest.raises(MemoryError) as exc_info:
        raise MemoryError("Memory allocation failed")
    assert isinstance(exc_info.value, VideoUnderstandingError)
    assert str(exc_info.value) == "Memory allocation failed"

    # Test PipelineError
    with pytest.raises(PipelineError) as exc_info:
        raise PipelineError("Pipeline execution failed")
    assert isinstance(exc_info.value, VideoUnderstandingError)
    assert str(exc_info.value) == "Pipeline execution failed"

def test_processing_error_hierarchy():
    """Test the processing error hierarchy."""
    # Test VideoFormatError
    with pytest.raises(VideoFormatError) as exc_info:
        raise VideoFormatError("Invalid format")
    assert isinstance(exc_info.value, ProcessingError)
    assert isinstance(exc_info.value, VideoUnderstandingError)

    # Test AudioProcessingError
    with pytest.raises(AudioProcessingError) as exc_info:
        raise AudioProcessingError("Audio processing failed")
    assert isinstance(exc_info.value, ProcessingError)
    assert isinstance(exc_info.value, VideoUnderstandingError)

    # Test TranscriptionError
    with pytest.raises(TranscriptionError) as exc_info:
        raise TranscriptionError("Transcription failed")
    assert isinstance(exc_info.value, AudioProcessingError)
    assert isinstance(exc_info.value, ProcessingError)

    # Test OCRError
    with pytest.raises(OCRError) as exc_info:
        raise OCRError("OCR failed")
    assert isinstance(exc_info.value, ProcessingError)
    assert isinstance(exc_info.value, VideoUnderstandingError)

def test_model_error_hierarchy():
    """Test the model error hierarchy."""
    # Test ModelLoadError
    with pytest.raises(ModelLoadError) as exc_info:
        raise ModelLoadError("Model loading failed")
    assert isinstance(exc_info.value, ModelError)
    assert isinstance(exc_info.value, VideoUnderstandingError)

    # Test ModelInferenceError
    with pytest.raises(ModelInferenceError) as exc_info:
        raise ModelInferenceError("Model inference failed")
    assert isinstance(exc_info.value, ModelError)
    assert isinstance(exc_info.value, VideoUnderstandingError)

def test_pipeline_error_hierarchy():
    """Test the pipeline error hierarchy."""
    # Test StageError
    with pytest.raises(StageError) as exc_info:
        raise StageError("Pipeline stage failed")
    assert isinstance(exc_info.value, PipelineError)
    assert isinstance(exc_info.value, VideoUnderstandingError)

def test_resource_errors():
    """Test resource-related errors."""
    # Test ResourceExistsError
    with pytest.raises(ResourceExistsError) as exc_info:
        raise ResourceExistsError("Resource already exists")
    assert isinstance(exc_info.value, VideoUnderstandingError)

    # Test ResourceExceededError
    with pytest.raises(ResourceExceededError) as exc_info:
        raise ResourceExceededError("Resource limit exceeded")
    assert isinstance(exc_info.value, VideoProcessingError)

    # Test ConcurrencyLimitError
    with pytest.raises(ConcurrencyLimitError) as exc_info:
        raise ConcurrencyLimitError("Too many concurrent operations")
    assert isinstance(exc_info.value, VideoProcessingError)

def test_custom_timeout_and_memory_errors():
    """Test our custom TimeoutError and MemoryError classes."""
    # Test CustomTimeoutError
    error = CustomTimeoutError("Custom timeout")
    assert isinstance(error, VideoUnderstandingError)
    assert str(error) == "Custom timeout"

    # Test CustomMemoryError
    error = CustomMemoryError("Custom memory error")
    assert isinstance(error, VideoUnderstandingError)
    assert str(error) == "Custom memory error"
