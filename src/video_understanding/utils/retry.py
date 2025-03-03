"""
Retry utilities for handling transient errors.

This module provides utilities for retrying operations that may fail due to
transient errors, such as network issues or rate limiting.
"""

import asyncio
import logging
import random
from functools import wraps
from typing import Any, Awaitable, Callable, List, Optional, Type, TypeVar, Union, cast

from video_understanding.services.exceptions import (
    ConnectionError,
    RateLimitError,
    ServiceError,
    TimeoutError,
)

# Type variables for generic typing
T = TypeVar("T")
ExcType = Union[Type[Exception], List[Type[Exception]]]

# Set up logging
logger = logging.getLogger(__name__)


async def retry_async(
    func: Callable[..., Awaitable[T]],
    *args: Any,
    retry_count: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    exceptions_to_retry: Optional[ExcType] = None,
    **kwargs: Any,
) -> T:
    """Retry an async function with exponential backoff.

    Args:
        func: Async function to retry
        *args: Positional arguments to pass to the function
        retry_count: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor to multiply delay by after each retry
        jitter: Whether to add random jitter to delay
        exceptions_to_retry: Exception types to retry on (defaults to connection errors)
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Result of the function call

    Raises:
        Exception: The last exception raised by the function
    """
    if exceptions_to_retry is None:
        exceptions_to_retry = [ConnectionError, TimeoutError, RateLimitError]

    if not isinstance(exceptions_to_retry, list):
        exceptions_to_retry = [exceptions_to_retry]

    last_exception: Optional[Exception] = None
    delay = initial_delay

    # Try the initial call plus retry_count retries
    for attempt in range(retry_count + 1):
        try:
            return await func(*args, **kwargs)
        except tuple(exceptions_to_retry) as e:
            last_exception = e

            if attempt == retry_count:
                # Last attempt failed, re-raise the exception
                raise

            # Calculate delay with optional jitter
            if jitter:
                delay = min(max_delay, delay * (1 + random.random() * 0.1))
            else:
                delay = min(max_delay, delay)

            # Log the retry
            logger.warning(
                f"Retry {attempt + 1}/{retry_count} after error: {str(e)}. "
                f"Retrying in {delay:.2f} seconds."
            )

            # Wait before retrying
            await asyncio.sleep(delay)

            # Increase delay for next retry
            delay = min(max_delay, delay * backoff_factor)

    # This should never happen, but just in case
    if last_exception:
        raise last_exception

    # This should also never happen, but needed for type checking
    raise RuntimeError("Unexpected error in retry_async")
