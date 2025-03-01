"""Base exceptions for video understanding."""

class VideoUnderstandingError(Exception):
    """Base exception for video understanding errors."""
    pass

class SecurityError(VideoUnderstandingError):
    """Exception raised for security-related errors."""
    pass

class IntegrityError(VideoUnderstandingError):
    """Exception raised for file integrity errors."""
    pass

class ProcessingError(VideoUnderstandingError):
    """Exception raised for video processing errors."""
    pass

class ConfigurationError(VideoUnderstandingError):
    """Exception raised for configuration errors."""
    pass

class UploadError(VideoUnderstandingError):
    """Exception raised for upload-related errors."""
    pass

class StorageError(VideoUnderstandingError):
    """Exception raised for storage-related errors."""
    pass

class AIModelError(VideoUnderstandingError):
    """Exception raised for AI model-related errors."""
    pass

class ValidationError(VideoUnderstandingError):
    """Exception raised for validation errors."""
    pass

class ResourceError(VideoUnderstandingError):
    """Exception raised for resource-related errors."""
    pass
