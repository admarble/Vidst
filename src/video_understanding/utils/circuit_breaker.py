import time
import asyncio
from typing import Callable, Any, TypeVar, cast
from loguru import logger

T = TypeVar("T")


class CircuitBreakerOpenError(Exception):
    """Error raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """Circuit breaker implementation for service resiliency."""

    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before circuit opens
            reset_timeout: Seconds to wait before attempting reset
        """
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.is_open = False
        self.last_failure_time = 0

    async def execute(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
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
                logger.info("Circuit breaker attempting reset")
                self.is_open = False
                self.failure_count = 0
            else:
                logger.warning("Circuit breaker open, call rejected")
                time_remaining = self.reset_timeout - (
                    current_time - self.last_failure_time
                )
                raise CircuitBreakerOpenError(
                    f"Circuit breaker open. Try again in {time_remaining:.2f}s"
                )

        try:
            # Check if function is coroutine
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Successful call, reset failure count
            self.failure_count = 0
            return cast(T, result)

        except Exception:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                logger.error(
                    f"Circuit breaker threshold exceeded "
                    f"({self.failure_count}/{self.failure_threshold}). "
                    f"Opening circuit."
                )
                self.is_open = True

            # Re-raise the original exception
            raise
