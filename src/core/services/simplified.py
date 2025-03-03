"""
Simplified service interfaces for POC.

This module provides simplified service interfaces for the POC, with standardized
error handling, configuration management, and common patterns.
"""

import asyncio
import logging
import random
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Dict, Generic, Type, TypeVar

from pydantic import Field

from src.core.services.base import ServiceConfig
from src.core.services.error_handling import (
    EnhancedServiceError,
    ErrorCategory,
    ErrorSeverity,
    handle_service_errors,
    is_retryable_error,
)

# Set up logging
logger = logging.getLogger(__name__)

# Type variables for generic typing
ConfigT = TypeVar("ConfigT", bound="SimpleServiceConfig")
T = TypeVar("T")


class SimpleServiceConfig(ServiceConfig):
    """Simplified configuration model for services.

    This configuration model provides a minimal set of configuration options
    that are common to most services.
    """

    # Basic service configuration
    service_name: str = Field(
        ..., description="Name of the service for logging and identification"
    )
    timeout: float = Field(
        30.0, description="Default timeout in seconds for service operations"
    )

    # Using parent ServiceConfig for retry and circuit breaker

    # Logging configuration
    log_level: str = Field("INFO", description="Log level for service operations")

    class Config:
        """Pydantic configuration."""

        extra = "ignore"


class SimpleService(Generic[ConfigT], ABC):
    """Simplified base class for services.

    This class provides a consistent interface for services with simplified
    error handling, configuration management, and common patterns.
    """

    # Class variable to store the configuration type
    config_class: Type[ConfigT] = SimpleServiceConfig  # type: ignore

    def __init__(self, config: ConfigT):
        """Initialize the service with configuration.

        Args:
            config: Service configuration

        Raises:
            EnhancedServiceError: If configuration is invalid
        """
        self.config = config
        self.circuit_breaker = None

        # Initialize circuit breaker from configuration
        if self.config.circuit_breaker.enabled:
            self.circuit_breaker = self.config.create_circuit_breaker()

        try:
            self.validate_config()
        except Exception as e:
            raise EnhancedServiceError(
                message=f"Invalid configuration: {str(e)}",
                service_name=self.config.service_name,
                category=ErrorCategory.INVALID_INPUT,
                severity=ErrorSeverity.ERROR,
                exception=e,
                retry_allowed=False,
            )

    def validate_config(self) -> None:
        """Validate the service configuration.

        This method can be overridden by subclasses to perform additional
        validation beyond what Pydantic provides.

        Raises:
            EnhancedServiceError: If configuration is invalid
        """
        # Basic validation is handled by Pydantic
        # Subclasses can override this method to add additional validation
        pass

    @handle_service_errors(
        default_message="Failed to initialize service",
        log_level=ErrorSeverity.ERROR,
        default_category=ErrorCategory.INTERNAL_ERROR,
    )
    async def initialize(self) -> None:
        """Initialize the service.

        This method should be called after creating the service instance
        to perform any necessary setup, such as establishing connections.

        Raises:
            EnhancedServiceError: If initialization fails
        """
        logger.info("[%s] Initializing service", self.config.service_name)
        await self._initialize_impl()
        logger.info("[%s] Service initialized", self.config.service_name)

    @abstractmethod
    async def _initialize_impl(self) -> None:
        """Implementation of service initialization.

        This method should be implemented by subclasses to perform
        service-specific initialization.

        Raises:
            EnhancedServiceError: If initialization fails
        """
        pass

    @handle_service_errors(
        default_message="Failed to shutdown service",
        log_level=ErrorSeverity.ERROR,
        default_category=ErrorCategory.INTERNAL_ERROR,
    )
    async def shutdown(self) -> None:
        """Shutdown the service.

        This method should be called before disposing of the service instance
        to perform any necessary cleanup, such as closing connections.

        Raises:
            EnhancedServiceError: If shutdown fails
        """
        logger.info("[%s] Shutting down service", self.config.service_name)
        await self._shutdown_impl()
        logger.info("[%s] Service shut down", self.config.service_name)

    @abstractmethod
    async def _shutdown_impl(self) -> None:
        """Implementation of service shutdown.

        This method should be implemented by subclasses to perform
        service-specific shutdown.

        Raises:
            EnhancedServiceError: If shutdown fails
        """
        pass

    @handle_service_errors(
        default_message="Service health check failed",
        log_level=ErrorSeverity.WARNING,
        default_category=ErrorCategory.SERVICE_UNAVAILABLE,
    )
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the service.

        This method checks the health of the service and returns a dictionary
        with health information.

        Returns:
            Dictionary with health information

        Raises:
            EnhancedServiceError: If health check fails
        """
        logger.debug("[%s] Performing health check", self.config.service_name)
        result = await self._health_check_impl()
        logger.debug("[%s] Health check completed", self.config.service_name)
        return result

    async def _health_check_impl(self) -> Dict[str, Any]:
        """Implementation of service health check.

        This method can be overridden by subclasses to perform
        service-specific health checks.

        Returns:
            Dictionary with health information

        Raises:
            EnhancedServiceError: If health check fails
        """
        # Default implementation returns basic health information
        return {
            "service": self.config.service_name,
            "status": "ok",
        }

    async def execute_with_retry(
        self, func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
    ) -> T:
        """Execute a function with retry logic.

        This method executes a function and retries it if it fails with
        a retryable error, using exponential backoff.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result of the function

        Raises:
            EnhancedServiceError: If function fails after all retries
        """
        # Use retry configuration from service config
        max_retries = kwargs.pop("max_retries", self.config.retry.max_retries)
        retry_delay = kwargs.pop("retry_delay", self.config.retry.base_delay)
        max_delay = kwargs.pop("max_delay", self.config.retry.max_delay)
        backoff_factor = kwargs.pop("backoff_factor", self.config.retry.backoff_factor)
        jitter = kwargs.pop("jitter", self.config.retry.jitter)

        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                # If circuit breaker is enabled, use it
                if self.circuit_breaker:
                    return await self.circuit_breaker.execute(func, *args, **kwargs)
                else:
                    return await func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                # Check if we should retry
                if attempt == max_retries or not is_retryable_error(e):
                    # If it's already an EnhancedServiceError, re-raise it
                    if isinstance(e, EnhancedServiceError):
                        raise

                    # Otherwise, convert it to an EnhancedServiceError
                    category = ErrorCategory.INTERNAL_ERROR
                    if hasattr(e, "category"):
                        category = getattr(e, "category")

                    error_msg = (
                        f"Operation failed after {attempt + 1} attempts: {str(e)}"
                    )
                    raise EnhancedServiceError(
                        message=error_msg,
                        service_name=self.config.service_name,
                        category=category,
                        severity=ErrorSeverity.ERROR,
                        exception=e,
                        retry_allowed=False,
                    )

                # Calculate delay with exponential backoff
                delay = min(retry_delay * (backoff_factor**attempt), max_delay)

                # Add jitter if enabled
                if jitter:
                    delay = delay * (0.5 + random.random())

                # Log the retry
                logger.warning(
                    "[%s] Attempt %s/%s failed: %s. Retrying in %.2fs",
                    self.config.service_name,
                    attempt + 1,
                    max_retries + 1,
                    str(e),
                    delay,
                )

                # Wait before retrying
                await asyncio.sleep(delay)

        # This should never be reached due to the raise in the exception handler
        assert last_exception is not None
        raise last_exception
