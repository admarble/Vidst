"""OpenAI GPT-4V API exceptions."""

from ...core.exceptions import ModelError


class GPT4VError(ModelError):
    """Base exception for GPT-4V API errors."""

    def __init__(self, message: str, cause: Exception | None = None, details: dict | None = None):
        """Initialize the error.

        Args:
            message: The error message
            cause: The underlying cause of this error
            details: Additional error details
        """
        super().__init__(message, cause)
        self.details = details or {}


class RateLimitError(GPT4VError):
    """Exception raised when API rate limits are exceeded."""
    pass


class TokenLimitError(GPT4VError):
    """Exception raised when token limits are exceeded."""
    pass


class ValidationError(GPT4VError):
    """Exception raised when input validation fails."""
    pass


class APIError(GPT4VError):
    """Exception raised when API requests fail."""
    pass


class ImageError(GPT4VError):
    """Exception raised when image processing fails."""
    pass


__all__ = [
    'GPT4VError',
    'RateLimitError',
    'TokenLimitError',
    'ValidationError',
    'APIError',
    'ImageError',
]
