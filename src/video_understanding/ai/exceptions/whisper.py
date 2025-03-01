"""OpenAI Whisper API exceptions."""

from ...core.exceptions import ModelError


class WhisperError(ModelError):
    """Base exception for Whisper API errors."""

    def __init__(self, message: str, cause: Exception | None = None, details: dict | None = None):
        """Initialize the error.

        Args:
            message: The error message
            cause: The underlying cause of this error
            details: Additional error details
        """
        super().__init__(message, cause)
        self.details = details or {}


class RateLimitError(WhisperError):
    """Exception raised when API rate limits are exceeded."""
    pass


class AudioError(WhisperError):
    """Exception raised when audio processing fails."""
    pass


class ValidationError(WhisperError):
    """Exception raised when input validation fails."""
    pass


class APIError(WhisperError):
    """Exception raised when API requests fail."""
    pass


class TranscriptionError(WhisperError):
    """Exception raised when transcription fails."""
    pass


__all__ = [
    'WhisperError',
    'RateLimitError',
    'AudioError',
    'ValidationError',
    'APIError',
    'TranscriptionError',
]
