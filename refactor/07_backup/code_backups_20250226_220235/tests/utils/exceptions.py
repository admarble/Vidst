"""Custom exceptions for testing.

This module defines custom exceptions used in performance testing to simulate
and handle various error conditions in a controlled manner.

Exception Hierarchy:
- ProcessingError
  - VideoProcessingError
- StorageError

These exceptions help test error handling, recovery mechanisms, and system
stability under various failure conditions.
"""


class ProcessingError(Exception):
    """Base exception for processing errors.

    Used for general processing failures that don't fit more specific categories.
    This serves as the base class for more specific processing errors.

    Attributes:
        message: Error description
        details: Additional error details (optional)
    """

    pass


class VideoProcessingError(ProcessingError):
    """Exception for video processing errors.

    Used for errors specific to video processing operations such as:
    - Format conversion failures
    - Frame extraction errors
    - Codec issues
    - Resolution problems

    Attributes:
        message: Error description
        video_path: Path to the problematic video
        details: Additional error details (optional)
    """

    pass


class StorageError(Exception):
    """Exception for storage errors.

    Used for errors related to data storage operations including:
    - File system errors
    - Cache operations
    - Vector storage issues
    - Database operations

    Attributes:
        message: Error description
        operation: Failed storage operation
        details: Additional error details (optional)
    """

    pass
