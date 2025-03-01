"""Custom exceptions for vector storage functionality.

This module contains all custom exceptions used across the vector storage package.
Each exception is designed to represent a specific type of error that can occur
during vector storage operations.
"""

class VectorStorageError(Exception):
    """Base exception for all vector storage related errors."""
    pass

class ValidationError(VectorStorageError):
    """Exception raised when validation fails for inputs or configuration."""
    pass

class ConfigurationError(VectorStorageError):
    """Exception raised when there are issues with configuration."""
    pass

class StorageOperationError(VectorStorageError):
    """Exception raised when a storage operation fails."""
    pass

class FileOperationError(VectorStorageError):
    """Exception raised when file operations fail."""
    pass

class MetadataError(VectorStorageError):
    """Exception raised when there are issues with metadata handling."""
    pass

class ConnectionError(VectorStorageError):
    """Exception raised when connection to storage backend fails."""
    pass

class ResourceExhaustedError(VectorStorageError):
    """Exception raised when system resources are exhausted."""
    pass

class NotFoundError(VectorStorageError):
    """Exception raised when a requested resource is not found."""
    pass

class DuplicateError(VectorStorageError):
    """Exception raised when attempting to create a duplicate resource."""
    pass

class StateError(VectorStorageError):
    """Exception raised when operation is invalid for current state."""
    pass

class VersionError(VectorStorageError):
    """Exception raised when there are version compatibility issues."""
    pass
