"""
Base service interface framework for Vidst.

This module provides a consistent way to configure services using Pydantic models,
a standardized error hierarchy, and a simple base service class that all services
will inherit from.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, Type, TypeVar

from pydantic import BaseModel, Field

# Configuration type variable for generic typing
ConfigT = TypeVar("ConfigT", bound="ServiceConfig")


class ServiceConfig(BaseModel):
    """Base configuration model for all services.

    All service configurations should inherit from this class and define
    their specific configuration parameters.
    """

    service_name: str = Field(
        ..., description="Name of the service for logging and identification"
    )
    timeout: float = Field(
        30.0, description="Default timeout in seconds for service operations"
    )
    max_retries: int = Field(
        3, description="Maximum number of retry attempts for failed operations"
    )

    class Config:
        """Pydantic configuration."""

        # Allow extra fields for forward compatibility
        extra = "ignore"


class ServiceError(Exception):
    """Base exception for all service-related errors."""

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the service error.

        Args:
            message: Error message
            service_name: Name of the service that raised the error
            status_code: Optional status code (e.g., HTTP status code)
            details: Optional additional error details
        """
        self.service_name = service_name
        self.status_code = status_code
        self.details = details or {}

        # Format the error message with service name if available
        formatted_message = f"[{service_name}] {message}" if service_name else message
        super().__init__(formatted_message)


class ConfigurationError(ServiceError):
    """Error raised when service configuration is invalid."""

    pass


class AuthenticationError(ServiceError):
    """Error raised when authentication with a service fails."""

    pass


class RateLimitError(ServiceError):
    """Error raised when a service rate limit is exceeded."""

    pass


class ResourceNotFoundError(ServiceError):
    """Error raised when a requested resource is not found."""

    pass


class ServiceUnavailableError(ServiceError):
    """Error raised when a service is unavailable."""

    pass


class BaseService(Generic[ConfigT], ABC):
    """Base class for all services.

    This class provides a consistent interface for all services and handles
    common functionality like configuration validation.

    Attributes:
        config: Service configuration
    """

    # Class variable to store the configuration type
    config_class: Type[ConfigT] = ServiceConfig  # type: ignore

    def __init__(self, config: ConfigT):
        """Initialize the service with configuration.

        Args:
            config: Service configuration

        Raises:
            ConfigurationError: If configuration is invalid
        """
        self.config = config
        self.validate_config()

    def validate_config(self) -> None:
        """Validate the service configuration.

        This method can be overridden by subclasses to perform additional
        validation beyond what Pydantic provides.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Basic validation is handled by Pydantic
        # Subclasses can override this method to add additional validation
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service.

        This method should be called after creating the service instance
        to perform any necessary setup, such as establishing connections.

        Raises:
            ServiceError: If initialization fails
        """
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the service.

        This method should be called before disposing of the service instance
        to perform any necessary cleanup, such as closing connections.

        Raises:
            ServiceError: If shutdown fails
        """
        pass
