"""
Service factory for creating service instances.

This module provides a factory class for creating service instances based on
configuration. It allows for dynamic service selection and instantiation.
"""

from typing import Any, Dict, Generic, Type, TypeVar

from src.core.services.base import BaseService, ConfigurationError, ServiceConfig

# Type variables for generic typing
ConfigT = TypeVar("ConfigT", bound=ServiceConfig)
ServiceT = TypeVar("ServiceT", bound=BaseService)


class ServiceFactory(Generic[ConfigT, ServiceT]):
    """Factory for creating service instances.

    This class provides a way to create service instances based on configuration.
    It allows for dynamic service selection and instantiation.

    Attributes:
        service_registry: Registry of service implementations
    """

    def __init__(self):
        """Initialize the service factory."""
        self.service_registry: Dict[str, Type[ServiceT]] = {}

    def register(self, service_type: str, service_class: Type[ServiceT]) -> None:
        """Register a service implementation.

        Args:
            service_type: Type identifier for the service
            service_class: Service class to register
        """
        self.service_registry[service_type] = service_class

    def create(self, service_type: str, config: ConfigT, **kwargs: Any) -> ServiceT:
        """Create a service instance.

        Args:
            service_type: Type identifier for the service
            config: Service configuration
            **kwargs: Additional arguments to pass to the service constructor

        Returns:
            Service instance

        Raises:
            ConfigurationError: If service type is not registered
        """
        if service_type not in self.service_registry:
            registered_types = ", ".join(self.service_registry.keys())
            raise ConfigurationError(
                f"Service type '{service_type}' not registered. "
                f"Available types: {registered_types}"
            )

        service_class = self.service_registry[service_type]
        return service_class(config, **kwargs)
