"""Google Gemini API exceptions."""

from ...core.exceptions import ModelError


class GeminiError(ModelError):
    """Base exception for Gemini API errors."""

    def __init__(self, message: str, cause: Exception | None = None, details: dict | None = None):
        """Initialize the error.

        Args:
            message: The error message
            cause: The underlying cause of this error
            details: Additional error details
        """
        super().__init__(message, cause)
        self.details = details or {}


class RateLimitError(GeminiError):
    """Exception raised when API rate limits are exceeded."""
    pass


class TokenLimitError(GeminiError):
    """Exception raised when token limits are exceeded."""
    pass


class ValidationError(GeminiError):
    """Exception raised when input validation fails."""
    pass


class APIError(GeminiError):
    """Exception raised when API requests fail."""
    pass


class ImageError(GeminiError):
    """Exception raised when image processing fails."""
    pass


class SafetyError(GeminiError):
    """Exception raised when content violates safety policies."""
    pass


__all__ = [
    'GeminiError',
    'RateLimitError',
    'TokenLimitError',
    'ValidationError',
    'APIError',
    'ImageError',
    'SafetyError',
]
