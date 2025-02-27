"""Twelve Labs API exceptions."""

from ...core.exceptions import ModelError


class TwelveLabsError(ModelError):
    """Base exception for Twelve Labs API errors."""

    def __init__(self, message: str, cause: Exception | None = None, details: dict | None = None):
        """Initialize the error.

        Args:
            message: The error message
            cause: The underlying cause of this error
            details: Additional error details
        """
        super().__init__(message, cause)
        self.details = details or {}


class RateLimitError(TwelveLabsError):
    """Exception raised when API rate limits are exceeded."""
    pass


class TaskError(TwelveLabsError):
    """Exception raised when a task fails or is invalid."""
    pass


class ValidationError(TwelveLabsError):
    """Exception raised when input validation fails."""
    pass


class APIError(TwelveLabsError):
    """Exception raised when API requests fail."""
    pass


class ResourceError(TwelveLabsError):
    """Exception raised when resource access fails."""
    pass


__all__ = [
    'TwelveLabsError',
    'RateLimitError',
    'TaskError',
    'ValidationError',
    'APIError',
    'ResourceError',
]
