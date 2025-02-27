"""Twelve Labs model package."""

from .exceptions import (
    APITimeoutError,
    TwelveLabsAPIError,
    TwelveLabsAuthError,
    TwelveLabsConfigError,
    TwelveLabsError,
    TwelveLabsProcessingError,
    TwelveLabsRateLimitError,
    TwelveLabsTimeoutError,
    TwelveLabsValidationError,
)
from .model import TwelveLabsModel
from .types import SearchResult, TaskOptions, TaskResult, TaskType, VideoMetadata

__all__ = [
    "APITimeoutError",
    "SearchResult",
    "TaskOptions",
    "TaskResult",
    "TaskType",
    "TwelveLabsAPIError",
    "TwelveLabsAuthError",
    "TwelveLabsConfigError",
    "TwelveLabsError",
    "TwelveLabsModel",
    "TwelveLabsProcessingError",
    "TwelveLabsRateLimitError",
    "TwelveLabsTimeoutError",
    "TwelveLabsValidationError",
    "VideoMetadata",
]
