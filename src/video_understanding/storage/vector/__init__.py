"""Vector storage functionality for video understanding.

This package provides functionality for storing and retrieving vector embeddings
generated from video content analysis.
"""

from .types import (
    VectorMetadata,
    SearchResult,
    VectorEmbedding,
    VectorStore,
    VectorArray,
    VectorBatch,
)
from .exceptions import (
    VectorStorageError,
    ValidationError,
    ConfigurationError,
    StorageOperationError,
    FileOperationError,
    MetadataError,
    ConnectionError,
    ResourceExhaustedError,
    NotFoundError,
    DuplicateError,
    StateError,
    VersionError,
)
from .utils import (
    validate_embedding,
    validate_metadata,
    normalize_vector,
    wrap_errors,
    retry_operation,
)

__all__ = [
    # Types
    'VectorMetadata',
    'SearchResult',
    'VectorEmbedding',
    'VectorStore',
    'VectorArray',
    'VectorBatch',

    # Exceptions
    'VectorStorageError',
    'ValidationError',
    'ConfigurationError',
    'StorageOperationError',
    'FileOperationError',
    'MetadataError',
    'ConnectionError',
    'ResourceExhaustedError',
    'NotFoundError',
    'DuplicateError',
    'StateError',
    'VersionError',

    # Utilities
    'validate_embedding',
    'validate_metadata',
    'normalize_vector',
    'wrap_errors',
    'retry_operation',
]
