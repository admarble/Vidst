"""
Utility functions for services.

This module provides utility functions for services, such as retry mechanisms
and circuit breakers.
"""

import asyncio
import logging
import random
import time
from functools import wraps
from typing import Any, Awaitable, Callable, Optional, Tuple, Type, TypeVar, Union

from src.core.services.base import ServiceError

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for generic typing
T = TypeVar("T")


class CircuitBreakerOpenError(ServiceError):
    """Error raised when circuit breaker is open."""


class CircuitBreaker:
    """Circuit breaker implementation for service resiliency.

    The circuit breaker pattern prevents repeated calls to a failing service,
    allowing it time to recover. It has three states:

    - Closed: Normal operation, calls pass through
    - Open: Service is failing, calls are blocked
    - Half-open: Testing if service has recovered

    Attributes:
        failure_threshold: Number of failures before circuit opens
        reset_timeout: Seconds to wait before attempting reset
        failure_count: Current number of consecutive failures
        is_open: Whether the circuit is open
        last_failure_time: Timestamp of the last failure
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: int = 60,
        service_name: Optional[str] = None,
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before circuit opens
            reset_timeout: Seconds to wait before attempting reset
            service_name: Optional service name for error reporting
        """
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.service_name = service_name
        self.failure_count = 0
        self.is_open = False
        self.last_failure_time = 0

    async def execute(
        self, func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
    ) -> T:
        """Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result of the function

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Original exception if function fails
        """
        if self.is_open:
            current_time = time.time()
            if current_time - self.last_failure_time >= self.reset_timeout:
                # Try to reset circuit
                logger.info("[%s] Circuit breaker attempting reset", self.service_name)
                self.is_open = False
                self.failure_count = 0
            else:
                remaining = self.reset_timeout - (current_time - self.last_failure_time)
                logger.warning(
                    "[%s] Circuit breaker open, call rejected", self.service_name
                )
                raise CircuitBreakerOpenError(
                    f"Circuit breaker open. Try again in {remaining:.2f}s",
                    service_name=self.service_name,
                )

        try:
            # Execute the coroutine function
            result = await func(*args, **kwargs)

            # Successful call, reset failure count
            self.failure_count = 0
            return result

        except Exception:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                logger.error(
                    "[%s] Circuit breaker threshold reached (%s failures). "
                    "Opening circuit.",
                    self.service_name,
                    self.failure_count,
                )
                self.is_open = True

            # Re-raise the original exception
            raise


# Common transient error types that are typically safe to retry
TRANSIENT_ERRORS = (
    ConnectionError,  # Network connection issues
    TimeoutError,  # Operation timeouts
    OSError,  # Low-level OS errors (often network-related)
)

# Service-specific errors that should be retried
SERVICE_ERRORS = (
    "ServiceUnavailableError",  # Service temporarily unavailable
    "RateLimitError",  # Rate limit exceeded
)


def async_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = TRANSIENT_ERRORS,
    service_name: Optional[str] = None,
):
    """Decorator for async functions to implement retry logic with exponential backoff.

    This utility retries operations that fail with specified exceptions, using
    configurable retry count and delay parameters. It logs retry attempts and
    failures, and works with service error types.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor by which the delay increases with each retry
        jitter: Whether to add random jitter to the delay
        exceptions: Exception type or tuple of exception types that trigger a retry
        service_name: Optional service name for logging

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            service_prefix = f"[{service_name}] " if service_name else ""

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, TimeoutError, OSError, ServiceError) as e:
                    # Check if this exception should be retried
                    should_retry = False

                    # Check if it's one of the specified exception types
                    if isinstance(e, exceptions):
                        should_retry = True

                    # Check if it's a service error that should be retried
                    if isinstance(e, ServiceError):
                        error_type = e.__class__.__name__
                        if error_type in SERVICE_ERRORS:
                            should_retry = True

                    if not should_retry or attempt == max_retries:
                        if attempt > 0:  # Only log if we've attempted retries
                            logger.error(
                                "%sFailed after %s retries: %s",
                                service_prefix,
                                attempt,
                                str(e),
                            )
                        raise

                    last_exception = e

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (backoff_factor**attempt), max_delay)

                    # Add jitter if enabled
                    if jitter:
                        delay = delay * (0.5 + random.random())

                    # Log the error and retry information
                    error_type = e.__class__.__name__
                    logger.warning(
                        "%sAttempt %s/%s failed with %s: %s. Retrying in %.2fs",
                        service_prefix,
                        attempt + 1,
                        max_retries + 1,
                        error_type,
                        str(e),
                        delay,
                    )
                    await asyncio.sleep(delay)

            # This should never be reached due to the raise in the exception handler
            assert last_exception is not None
            raise last_exception

        return wrapper

    return decorator


def simple_retry(
    max_retries: int = 3, base_delay: float = 1.0, service_name: Optional[str] = None
):
    """Simplified retry decorator for common transient errors.

    This is a simpler version of async_retry with reasonable defaults
    for retrying operations that fail with common transient errors.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        service_name: Optional service name for logging

    Returns:
        Decorated function with retry logic
    """
    return async_retry(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=10.0,
        backoff_factor=1.5,
        jitter=True,
        exceptions=TRANSIENT_ERRORS,
        service_name=service_name,
    )


def connection_retry(max_retries: int = 5, service_name: Optional[str] = None):
    """Specialized retry decorator for connection-related errors.

    This decorator is specifically designed for retrying operations that fail
    with connection-related errors, which are common when working with external APIs.

    Args:
        max_retries: Maximum number of retry attempts
        service_name: Optional service name for logging

    Returns:
        Decorated function with retry logic
    """
    return async_retry(
        max_retries=max_retries,
        base_delay=2.0,
        max_delay=30.0,
        backoff_factor=2.0,
        jitter=True,
        exceptions=TRANSIENT_ERRORS,
        service_name=service_name,
    )
