"""
Custom exceptions for video processing and validation.

This module defines the exception hierarchy for handling various
error cases in the video processing pipeline.
"""


class VideoProcessingError(Exception):
    """Base exception for video processing errors"""
    pass


class FileValidationError(VideoProcessingError):
    """Exception raised when file validation fails"""
    pass


class ProcessingError(VideoProcessingError):
    """Exception raised when video processing fails"""
    pass


class StorageError(VideoProcessingError):
    """Exception raised when file storage operations fail"""
    pass
