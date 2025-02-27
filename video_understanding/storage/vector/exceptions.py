"""Vector storage exceptions."""

class StorageError(Exception):
    """Base exception for storage errors."""
    pass

class StorageOperationError(StorageError):
    """Exception raised for storage operation errors."""
    pass

class ValidationError(StorageError):
    """Exception raised for validation errors."""
    pass

class ConfigurationError(StorageError):
    """Exception raised for configuration errors."""
    pass

class MetadataError(StorageError):
    """Exception raised for metadata errors."""
    pass

class ResourceExceededError(StorageError):
    """Exception raised when resource quotas are exceeded."""
    pass
