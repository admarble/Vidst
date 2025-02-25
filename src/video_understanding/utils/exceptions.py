"""Custom exceptions for video understanding system.

This module defines the exception hierarchy used across the video understanding
system for proper error handling and reporting.
"""

class VideoUnderstandingError(Exception):
    """Base exception for all video understanding errors."""
    pass


class ValidationError(VideoUnderstandingError):
    """Base exception for validation errors."""
    pass


class VideoFormatError(ValidationError):
    """Raised when video format is invalid or unsupported."""
    pass


class VideoIntegrityError(ValidationError):
    """Raised when video file fails integrity checks."""
    pass


class SecurityError(VideoUnderstandingError):
    """Raised when security checks fail."""
    pass


class StorageError(VideoUnderstandingError):
    """Raised when storage operations fail."""
    pass


class ProcessingError(VideoUnderstandingError):
    """Raised when video processing operations fail."""
    pass


class QuarantineError(VideoUnderstandingError):
    """Raised when quarantine operations fail."""
    pass
