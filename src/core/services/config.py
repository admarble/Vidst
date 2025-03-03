"""
Configuration management for services.

This module provides a standardized way to configure services using Pydantic models.
It includes configuration for common patterns like circuit breakers and retries.
"""

from typing import Optional, Tuple, Type, Union

from pydantic import BaseModel, Field, validator


class CircuitBreakerConfig(BaseModel):
    """Configuration for circuit breaker pattern.

    The circuit breaker pattern prevents repeated calls to a failing service,
    allowing it time to recover.
    """

    enabled: bool = Field(True, description="Whether to enable the circuit breaker")
    failure_threshold: int = Field(
        5, description="Number of failures before circuit opens"
    )
    reset_timeout: int = Field(
        60, description="Seconds to wait before attempting reset"
    )

    @validator("failure_threshold")
    def validate_failure_threshold(cls, v):
        if v < 1:
            raise ValueError("failure_threshold must be at least 1")
        return v

    @validator("reset_timeout")
    def validate_reset_timeout(cls, v):
        if v < 1:
            raise ValueError("reset_timeout must be at least 1")
        return v

    def create_circuit_breaker(self, service_name: Optional[str] = None):
        """Create a CircuitBreaker instance from this configuration.

        Args:
            service_name: Optional service name for error reporting

        Returns:
            CircuitBreaker instance or None if circuit breaker is disabled
        """
        if not self.enabled:
            return None

        from src.core.services.utils import CircuitBreaker

        return CircuitBreaker(
            failure_threshold=self.failure_threshold,
            reset_timeout=self.reset_timeout,
            service_name=service_name,
        )


class RetryConfig(BaseModel):
    """Configuration for retry logic.

    Retry logic allows operations to be retried if they fail with transient errors.
    """

    max_retries: int = Field(3, description="Maximum number of retry attempts")
    base_delay: float = Field(1.0, description="Base delay between retries in seconds")
    max_delay: float = Field(
        60.0, description="Maximum delay between retries in seconds"
    )
    backoff_factor: float = Field(
        2.0, description="Factor by which the delay increases"
    )
    jitter: bool = Field(True, description="Whether to add random jitter to the delay")

    @validator("max_retries")
    def validate_max_retries(cls, v):
        if v < 0:
            raise ValueError("max_retries must be non-negative")
        return v

    @validator("base_delay", "max_delay")
    def validate_delays(cls, v):
        if v <= 0:
            raise ValueError("delay values must be positive")
        return v

    @validator("backoff_factor")
    def validate_backoff_factor(cls, v):
        if v <= 1:
            raise ValueError("backoff_factor must be greater than 1")
        return v

    def create_retry_decorator(
        self,
        service_name: Optional[str] = None,
        exceptions: Optional[
            Union[Type[Exception], Tuple[Type[Exception], ...]]
        ] = None,
    ):
        """Create a retry decorator from this configuration.

        Args:
            service_name: Optional service name for logging
            exceptions: Exception types that trigger a retry

        Returns:
            Retry decorator function
        """
        from src.core.services.utils import async_retry, TRANSIENT_ERRORS

        return async_retry(
            max_retries=self.max_retries,
            base_delay=self.base_delay,
            max_delay=self.max_delay,
            backoff_factor=self.backoff_factor,
            jitter=self.jitter,
            exceptions=exceptions or TRANSIENT_ERRORS,
            service_name=service_name,
        )

    def create_simple_retry_decorator(self, service_name: Optional[str] = None):
        """Create a simple retry decorator with reasonable defaults.

        Args:
            service_name: Optional service name for logging

        Returns:
            Simple retry decorator function
        """
        from src.core.services.utils import simple_retry

        return simple_retry(
            max_retries=self.max_retries,
            base_delay=self.base_delay,
            service_name=service_name,
        )

    def create_connection_retry_decorator(self, service_name: Optional[str] = None):
        """Create a connection retry decorator specialized for network operations.

        Args:
            service_name: Optional service name for logging

        Returns:
            Connection retry decorator function
        """
        from src.core.services.utils import connection_retry

        return connection_retry(
            max_retries=self.max_retries,
            service_name=service_name,
        )
