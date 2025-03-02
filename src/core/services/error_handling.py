"""
Common error handling patterns for service interfaces.

This module provides standardized error handling patterns for service interfaces,
including error classification, error formatting, and error handling decorators.
"""

import functools
import logging
import traceback
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, Optional, TypeVar, cast

from src.core.services.base import ServiceError

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for generic typing
T = TypeVar("T")


class ErrorSeverity(Enum):
    """Severity levels for service errors."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categories for classifying service errors."""

    # Infrastructure errors
    NETWORK = "network"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTION = "resource_exhaustion"

    # Authentication/authorization errors
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"

    # Client errors
    INVALID_INPUT = "invalid_input"
    RESOURCE_NOT_FOUND = "resource_not_found"
    RATE_LIMIT = "rate_limit"

    # Server errors
    SERVICE_UNAVAILABLE = "service_unavailable"
    INTERNAL_ERROR = "internal_error"

    # Data errors
    DATA_VALIDATION = "data_validation"
    DATA_INTEGRITY = "data_integrity"

    # Unknown/other
    UNKNOWN = "unknown"


class EnhancedServiceError(ServiceError):
    """Enhanced service error with additional metadata.

    This class extends the base ServiceError with additional metadata
    for better error classification, logging, and handling.
    """

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        exception: Optional[Exception] = None,
        retry_allowed: bool = True,
    ):
        """Initialize the enhanced service error.

        Args:
            message: Error message
            service_name: Name of the service that raised the error
            status_code: Optional status code (e.g., HTTP status code)
            details: Optional additional error details
            category: Error category for classification
            severity: Error severity level
            exception: Original exception that caused this error
            retry_allowed: Whether this error can be retried
        """
        self.category = category
        self.severity = severity
        self.exception = exception
        self.retry_allowed = retry_allowed

        # Include exception traceback in details if available
        details = details or {}
        if exception:
            details["exception_type"] = type(exception).__name__
            details["exception_traceback"] = traceback.format_exception(
                type(exception), exception, exception.__traceback__
            )

        super().__init__(message, service_name, status_code, details)


def handle_service_errors(
    default_message: str = "An error occurred while processing the request",
    log_level: ErrorSeverity = ErrorSeverity.ERROR,
    rethrow: bool = True,
    default_category: ErrorCategory = ErrorCategory.UNKNOWN,
):
    """Decorator for handling service errors in a consistent way.

    This decorator catches exceptions, logs them appropriately, and
    optionally rethrows them as EnhancedServiceError instances.

    Args:
        default_message: Default error message if none is provided
        log_level: Default log level for errors
        rethrow: Whether to rethrow caught exceptions
        default_category: Default error category

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await func(*args, **kwargs)
            except EnhancedServiceError as e:
                # Already an enhanced error, just log it
                _log_error(
                    str(e), e.severity, service_name=e.service_name, details=e.details
                )
                if rethrow:
                    raise
                return cast(T, None)  # Type hint for mypy
            except ServiceError as e:
                # Convert to enhanced error
                enhanced = EnhancedServiceError(
                    message=e.args[0] if e.args else default_message,
                    service_name=getattr(e, "service_name", None),
                    status_code=getattr(e, "status_code", None),
                    details=getattr(e, "details", {}),
                    category=default_category,
                    severity=log_level,
                    exception=e,
                )
                _log_error(
                    str(enhanced),
                    enhanced.severity,
                    service_name=enhanced.service_name,
                    details=enhanced.details,
                )
                if rethrow:
                    raise enhanced
                return cast(T, None)  # Type hint for mypy
            except Exception as e:
                # Convert generic exception to enhanced error
                message = str(e) or default_message
                enhanced = EnhancedServiceError(
                    message=message,
                    category=default_category,
                    severity=log_level,
                    exception=e,
                )
                _log_error(message, log_level, details={"exception": str(e)})
                if rethrow:
                    raise enhanced
                return cast(T, None)  # Type hint for mypy

        return wrapper

    return decorator


def _log_error(
    message: str,
    severity: ErrorSeverity,
    service_name: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Log an error with the appropriate severity level.

    Args:
        message: Error message
        severity: Error severity level
        service_name: Optional service name
        details: Optional error details
    """
    log_message = f"[{service_name}] {message}" if service_name else message

    if details:
        log_message = f"{log_message} - Details: {details}"

    if severity == ErrorSeverity.DEBUG:
        logger.debug(log_message)
    elif severity == ErrorSeverity.INFO:
        logger.info(log_message)
    elif severity == ErrorSeverity.WARNING:
        logger.warning(log_message)
    elif severity == ErrorSeverity.ERROR:
        logger.error(log_message)
    elif severity == ErrorSeverity.CRITICAL:
        logger.critical(log_message)
    else:
        logger.error(log_message)  # Default to error level


# Error classification helpers
def classify_error(exception: Exception) -> ErrorCategory:
    """Classify an exception into an error category.

    Args:
        exception: Exception to classify

    Returns:
        Error category
    """
    error_type = type(exception).__name__
    error_message = str(exception).lower()

    # Network errors
    if any(name in error_type for name in ["Connection", "Socket", "Network", "Http"]):
        return ErrorCategory.NETWORK

    # Timeout errors
    if "timeout" in error_type.lower() or "timeout" in error_message:
        return ErrorCategory.TIMEOUT

    # Authentication errors
    if any(
        term in error_message
        for term in ["auth", "unauthorized", "unauthenticated", "token", "credential"]
    ):
        return ErrorCategory.AUTHENTICATION

    # Resource not found
    if "not found" in error_message or "404" in error_message:
        return ErrorCategory.RESOURCE_NOT_FOUND

    # Rate limit errors
    if any(
        term in error_message for term in ["rate limit", "too many requests", "429"]
    ):
        return ErrorCategory.RATE_LIMIT

    # Service unavailable
    if any(
        term in error_message for term in ["unavailable", "down", "maintenance", "503"]
    ):
        return ErrorCategory.SERVICE_UNAVAILABLE

    # Default to unknown
    return ErrorCategory.UNKNOWN


def is_retryable_error(exception: Exception) -> bool:
    """Determine if an error is retryable.

    Args:
        exception: Exception to check

    Returns:
        Whether the error is retryable
    """
    # If it's an enhanced error, check the retry_allowed flag
    if isinstance(exception, EnhancedServiceError):
        return exception.retry_allowed

    # Classify the error
    category = classify_error(exception)

    # These categories are generally retryable
    retryable_categories = [
        ErrorCategory.NETWORK,
        ErrorCategory.TIMEOUT,
        ErrorCategory.RESOURCE_EXHAUSTION,
        ErrorCategory.RATE_LIMIT,
        ErrorCategory.SERVICE_UNAVAILABLE,
    ]

    return category in retryable_categories
