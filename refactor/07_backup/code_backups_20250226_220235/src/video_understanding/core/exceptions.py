"""Core exception classes for the Video Understanding AI project.

This module defines all the custom exceptions used throughout the project.
Each exception class is properly documented and referenced.

Example:
    Basic exception handling:

    >>> try:
    ...     process_video(file_path)
    ... except VideoUnderstandingError as e:
    ...     logger.error(f"Processing failed: {e}")
    ...     if e.__cause__:
    ...         logger.debug(f"Caused by: {e.__cause__}")

    Converting standard exceptions:

    >>> try:
    ...     result = api_call()
    ... except Exception as e:
    ...     raise handle_error(e)

:no-index:
"""


class VideoUnderstandingError(Exception):
    """Base exception class for all Video Understanding AI errors.

    This is the root exception class for all custom exceptions in the project.
    It provides support for error cause tracking and consistent error handling.

    Example:
        >>> try:
        ...     raise ValueError("Invalid input")
        ... except ValueError as e:
        ...     raise VideoUnderstandingError("Processing failed", cause=e)

    Args:
        message: The error message
        cause: The original exception that caused this error

    :no-index:
    """

    def __init__(self, message: str, cause: BaseException | None = None):
        """Initialize with optional cause.

        Args:
            message: The error message
            cause: The original exception that caused this error
        """
        self.cause = cause
        super().__init__(message)


class ValidationError(VideoUnderstandingError):
    """Raised when input validation fails.

    :no-index:
    """

    pass


class ProcessingError(VideoUnderstandingError):
    """Raised when video processing fails.

    :no-index:
    """

    pass


class StorageError(VideoUnderstandingError):
    """Raised when storage operations fail.

    :no-index:
    """

    pass


class ConfigurationError(VideoUnderstandingError):
    """Raised when configuration is invalid.

    :no-index:
    """

    pass


class APIError(VideoUnderstandingError):
    """Raised when API operations fail.

    :no-index:
    """

    pass


class ModelError(VideoUnderstandingError):
    """Raised when model operations fail.

    This exception serves as the base class for all model-related errors.
    It properly handles error causes and provides a consistent interface
    for error handling across different model implementations.

    Example:
        >>> try:
        ...     model.predict(input_data)
        ... except ValueError as e:
        ...     raise ModelError("Prediction failed", cause=e)

    Args:
        message: The error message
        cause: The original exception that caused this error

    :no-index:
    """

    def __init__(self, message: str, cause: BaseException | None = None):
        """Initialize with optional cause.

        Args:
            message: The error message
            cause: The original exception that caused this error
        """
        super().__init__(message, cause)
        if cause:
            self.__cause__ = cause


class ResourceError(VideoUnderstandingError):
    """Raised when resource management fails.

    :no-index:
    """

    pass


class SystemError(VideoUnderstandingError):
    """Raised when system-level operations fail.

    :no-index:
    """

    pass


class TimeoutError(VideoUnderstandingError):
    """Raised when operations timeout.

    :no-index:
    """

    pass


class MemoryError(VideoUnderstandingError):
    """Raised when memory operations fail.

    :no-index:
    """

    pass


class PipelineError(VideoUnderstandingError):
    """Raised when pipeline operations fail.

    :no-index:
    """

    pass


class VideoFormatError(ProcessingError):
    """Raised when video format is invalid.

    :no-index:
    """

    pass


class VideoProcessingError(ProcessingError):
    """Raised when video processing fails.

    Args:
        message: The error message
        cause: The original exception that caused this error
        video_path: The path to the video file being processed

    :no-index:
    """

    def __init__(
        self,
        message: str,
        cause: BaseException | None = None,
        video_path: str | None = None,
    ):
        """Initialize with optional cause and video path.

        Args:
            message: The error message
            cause: The original exception that caused this error
            video_path: The path to the video file being processed
        """
        super().__init__(message, cause)
        self.video_path = video_path


class AudioProcessingError(ProcessingError):
    """Raised when audio processing fails.

    :no-index:
    """

    pass


class TranscriptionError(AudioProcessingError):
    """Raised when transcription fails.

    :no-index:
    """

    pass


class OCRError(ProcessingError):
    """Raised when OCR processing fails.

    :no-index:
    """

    pass


class RateLimitError(APIError):
    """Raised when API rate limits are exceeded.

    :no-index:
    """

    pass


class AuthenticationError(APIError):
    """Raised when authentication fails.

    :no-index:
    """

    pass


class ResourceNotFoundError(VideoUnderstandingError):
    """Raised when a requested resource is not found.

    :no-index:
    """

    pass


class ResourceExistsError(VideoUnderstandingError):
    """Raised when a resource already exists.

    :no-index:
    """

    pass


class ConcurrencyError(VideoUnderstandingError):
    """Raised when concurrent operations fail.

    :no-index:
    """

    pass


class DependencyError(VideoUnderstandingError):
    """Raised when dependency operations fail.

    :no-index:
    """

    pass


class ModelLoadError(ModelError):
    """Raised when model loading fails.

    :no-index:
    """

    pass


class ModelInferenceError(ModelError):
    """Raised when model inference fails.

    :no-index:
    """

    pass


class StageError(PipelineError):
    """Raised when a pipeline stage fails.

    :no-index:
    """

    pass


class FileValidationError(VideoUnderstandingError):
    """Raised when file validation fails.

    :no-index:
    """

    def __init__(self, message: str, cause: BaseException | None = None):
        """Initialize with optional cause.

        Args:
            message: The error message
            cause: The original exception that caused this error
        """
        super().__init__(message, cause)


class OutputError(VideoUnderstandingError):
    """Raised when output operations fail.

    :no-index:
    """

    pass


class CustomTimeoutError(TimeoutError):
    """Custom timeout error class.

    :no-index:
    """

    pass


class CustomMemoryError(MemoryError):
    """Custom memory error class.

    :no-index:
    """

    pass


class TwelveLabsError(APIError):
    """Raised when Twelve Labs API operations fail.

    :no-index:
    """

    pass


class TaskError(TwelveLabsError):
    """Raised when a task fails or times out.

    :no-index:
    """

    pass


class ResourceExceededError(VideoProcessingError):
    """Exception raised when resource limits are exceeded."""

    pass


class ConcurrencyLimitError(VideoProcessingError):
    """Exception raised when concurrent processing limit is exceeded."""

    pass


class SecurityError(VideoUnderstandingError):
    """Exception raised for security-related errors."""

    pass


class IntegrityError(VideoUnderstandingError):
    """Exception raised for file integrity errors."""

    pass


class UploadError(VideoUnderstandingError):
    """Exception raised for upload-related errors."""

    pass


# Map standard exceptions to custom exceptions
ERROR_MAP: dict[type[BaseException], type[VideoUnderstandingError]] = {
    ValueError: ValidationError,
    FileNotFoundError: ResourceNotFoundError,
    PermissionError: AuthenticationError,
    TimeoutError: CustomTimeoutError,
    MemoryError: CustomMemoryError,
    ImportError: DependencyError,
    RuntimeError: ProcessingError,
    NotImplementedError: ProcessingError,
    OSError: StorageError,
    IOError: StorageError,
    KeyError: ValidationError,
    TypeError: ValidationError,
    IndexError: ValidationError,
    AttributeError: ConfigurationError,
    ModuleNotFoundError: DependencyError,
    ConnectionError: APIError,
    InterruptedError: ConcurrencyError,
    BlockingIOError: ConcurrencyError,
    BrokenPipeError: StorageError,
    BufferError: CustomMemoryError,
    LookupError: ResourceNotFoundError,
}


def handle_error(error: BaseException) -> VideoUnderstandingError:
    """Convert standard Python exceptions to custom exceptions.

    This function maps standard Python exceptions to our custom exception hierarchy.
    It preserves the error cause chain and provides consistent error handling.

    Example:
        >>> try:
        ...     process_data()
        ... except Exception as e:
        ...     raise handle_error(e)

    Args:
        error: The original exception to convert

    Returns:
        A custom VideoUnderstandingError instance

    Example mappings:
        - ValueError -> ValidationError
        - FileNotFoundError -> ResourceNotFoundError
        - PermissionError -> AuthenticationError
        - TimeoutError -> CustomTimeoutError
        - MemoryError -> CustomMemoryError
    """
    if isinstance(error, VideoUnderstandingError):
        return error

    error_class = ERROR_MAP.get(type(error), VideoUnderstandingError)

    # Handle nested exceptions
    cause = error.__cause__ if hasattr(error, "__cause__") else None
    if cause:
        cause = handle_error(cause)

    return error_class(str(error), cause=cause)
