"""Custom exceptions for Twelve Labs integration."""

from video_understanding.core.exceptions import ModelError


class TwelveLabsError(ModelError):
    """Base exception for Twelve Labs errors."""


class RateLimitError(TwelveLabsError):
    """Rate limit exceeded."""


class TaskError(TwelveLabsError):
    """Task processing error."""


class ValidationError(TwelveLabsError):
    """Input validation error."""


class APIError(TwelveLabsError):
    """API communication error."""


class ResourceError(TwelveLabsError):
    """Resource management error."""
