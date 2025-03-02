"""
Service interfaces for Vidst.

This package provides a consistent way to configure services using Pydantic models,
a standardized error hierarchy, and a simple base service class that all services
will inherit from.
"""

from src.core.services.base import (
    AuthenticationError,
    BaseService,
    ConfigurationError,
    RateLimitError,
    ResourceNotFoundError,
    ServiceConfig,
    ServiceError,
    ServiceUnavailableError,
)
from src.core.services.error_handling import (
    EnhancedServiceError,
    ErrorCategory,
    ErrorSeverity,
    classify_error,
    handle_service_errors,
    is_retryable_error,
)
from src.core.services.factory import ServiceFactory
from src.core.services.simplified import SimpleService, SimpleServiceConfig
from src.core.services.utils import CircuitBreaker, CircuitBreakerOpenError, async_retry

__all__ = [
    "AuthenticationError",
    "BaseService",
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "ConfigurationError",
    "EnhancedServiceError",
    "ErrorCategory",
    "ErrorSeverity",
    "RateLimitError",
    "ResourceNotFoundError",
    "ServiceConfig",
    "ServiceError",
    "ServiceFactory",
    "ServiceUnavailableError",
    "SimpleService",
    "SimpleServiceConfig",
    "async_retry",
    "classify_error",
    "handle_service_errors",
    "is_retryable_error",
]
