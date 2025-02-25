"""Exceptions for AI models."""

class ModelError(Exception):
    """Base exception for model-related errors."""
    pass

class ValidationError(ModelError):
    """Exception raised when model input validation fails."""
    pass

class APIError(ModelError):
    """Exception raised when API request fails."""
    pass

class RateLimitError(APIError):
    """Exception raised when API rate limit is exceeded."""
    pass

class ResourceError(ModelError):
    """Exception raised when resource access fails."""
    pass

class TaskError(ModelError):
    """Exception raised when task processing fails."""
    pass

class ProcessingError(ModelError):
    """Exception raised when model processing fails."""
    pass

class ConfigurationError(ModelError):
    """Exception raised when model configuration is invalid."""
    pass

# Import twelve_labs exceptions
from .twelve_labs import (
    TwelveLabsError,
    RateLimitError as TwelveLabsRateLimitError,
    TaskError as TwelveLabsTaskError,
    ValidationError as TwelveLabsValidationError,
    APIError as TwelveLabsAPIError,
    ResourceError as TwelveLabsResourceError,
)
