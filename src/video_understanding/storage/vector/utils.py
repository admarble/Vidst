"""Utility functions for vector storage functionality.

This module contains utility functions used across the vector storage package,
including validation, error handling, and common operations.
"""

import logging
import functools
from typing import TypeVar, Callable, Any, ParamSpec
from datetime import datetime
import numpy as np
import numpy.typing as npt

from .types import VectorMetadata, VectorArray
from .exceptions import ValidationError

logger = logging.getLogger(__name__)

P = ParamSpec('P')
T = TypeVar('T')

def validate_embedding(embedding: npt.NDArray[np.float32], expected_dim: int) -> None:
    """Validate embedding vector.

    Args:
        embedding: Vector to validate
        expected_dim: Expected dimensionality

    Raises:
        ValidationError: If embedding is invalid
    """
    if not isinstance(embedding, np.ndarray):
        raise ValidationError("Embedding must be a numpy array")

    if embedding.dtype not in (np.float32, np.float64):
        raise ValidationError(
            f"Embedding must be float32 or float64, got {embedding.dtype}"
        )

    if embedding.shape != (expected_dim,):
        raise ValidationError(
            f"Expected {expected_dim} dimensions, got {embedding.shape}"
        )

    if not np.all(np.isfinite(embedding)):
        raise ValidationError("Embedding contains non-finite values")

def validate_metadata(metadata: VectorMetadata) -> None:
    """Validate metadata dictionary.

    Args:
        metadata: Metadata to validate

    Raises:
        ValidationError: If metadata is invalid
    """
    if not isinstance(metadata, dict):
        raise ValidationError("Metadata must be a dictionary")

    required_fields = ["type", "timestamp", "model_version"]
    for field in required_fields:
        if field not in metadata:
            raise ValidationError(f"Missing required metadata field: {field}")

    if not isinstance(metadata["type"], str):
        raise ValidationError("Metadata type must be a string")

    try:
        datetime.fromisoformat(metadata["timestamp"])
    except ValueError as e:
        raise ValidationError("Invalid timestamp format in metadata") from e

    if not isinstance(metadata["model_version"], str):
        raise ValidationError("Model version must be a string")

def normalize_vector(vector: VectorArray) -> VectorArray:
    """Normalize a vector to unit length.

    Args:
        vector: Vector to normalize

    Returns:
        Normalized vector
    """
    norm = np.linalg.norm(vector)
    if norm == 0:
        raise ValidationError("Cannot normalize zero vector")
    return vector / norm

def wrap_errors(error_cls: type[Exception]) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to wrap function errors in a specific exception class.

    Args:
        error_cls: Exception class to wrap errors in

    Returns:
        Decorated function
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if isinstance(e, error_cls):
                    raise
                raise error_cls(str(e)) from e
        return wrapper
    return decorator

def retry_operation(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,)
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to retry operations with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts in seconds
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exceptions to catch

    Returns:
        Decorated function
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            import time
            attempt = 1
            current_delay = delay

            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise
                    logger.warning(
                        "Operation failed (attempt %d/%d): %s",
                        attempt,
                        max_attempts,
                        str(e)
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1

            raise RuntimeError("Should not reach here")
        return wrapper
    return decorator
