"""Base exceptions for AI models."""

from ..core.exceptions import (
    ModelError,
    ValidationError,
    APIError,
    RateLimitError,
    ResourceError,
    ProcessingError,
    ConfigurationError,
    TaskError,
)


class SceneDetectionError(ModelError):
    """Exception raised when scene detection fails."""

    pass


__all__ = [
    "ModelError",
    "ValidationError",
    "APIError",
    "RateLimitError",
    "ResourceError",
    "ProcessingError",
    "ConfigurationError",
    "TaskError",
    "SceneDetectionError",
]
