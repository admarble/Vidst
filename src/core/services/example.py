"""
Example service implementation using the service interface framework.

This module demonstrates how to use the service interface framework to create
a simple service implementation.
"""

from typing import Dict, List, Optional

from pydantic import Field

from src.core.services.base import (
    BaseService,
    ConfigurationError,
    ServiceConfig,
    ServiceError,
)


class ExampleServiceConfig(ServiceConfig):
    """Configuration for the example service."""

    api_key: str = Field(..., description="API key for authentication")
    api_url: str = Field("https://api.example.com", description="API URL")
    cache_ttl: int = Field(300, description="Cache TTL in seconds")


class ExampleServiceError(ServiceError):
    """Error raised by the example service."""

    pass


class ExampleService(BaseService[ExampleServiceConfig]):
    """Example service implementation.

    This class demonstrates how to implement a service using the base service
    interface.
    """

    # Override the config_class class variable
    config_class = ExampleServiceConfig

    def __init__(self, config: ExampleServiceConfig):
        """Initialize the example service.

        Args:
            config: Service configuration
        """
        super().__init__(config)
        self.client = None

    def validate_config(self) -> None:
        """Validate the service configuration.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        super().validate_config()

        # Additional validation beyond what Pydantic provides
        if not self.config.api_key.startswith("key_"):
            raise ConfigurationError(
                "API key must start with 'key_'", service_name=self.config.service_name
            )

    async def initialize(self) -> None:
        """Initialize the service.

        This method should be called after creating the service instance
        to perform any necessary setup, such as establishing connections.

        Raises:
            ServiceError: If initialization fails
        """
        try:
            # In a real implementation, this would create an API client
            self.client = {
                "api_key": self.config.api_key,
                "api_url": self.config.api_url,
            }

            # Test the connection
            await self.ping()
        except Exception as e:
            raise ExampleServiceError(
                f"Failed to initialize service: {str(e)}",
                service_name=self.config.service_name,
            )

    async def shutdown(self) -> None:
        """Shutdown the service.

        This method should be called before disposing of the service instance
        to perform any necessary cleanup, such as closing connections.

        Raises:
            ServiceError: If shutdown fails
        """
        try:
            # In a real implementation, this would close the API client
            self.client = None
        except Exception as e:
            raise ExampleServiceError(
                f"Failed to shutdown service: {str(e)}",
                service_name=self.config.service_name,
            )

    async def ping(self) -> bool:
        """Ping the service to check if it's available.

        Returns:
            True if the service is available

        Raises:
            ExampleServiceError: If the service is unavailable
        """
        try:
            # In a real implementation, this would ping the API
            return True
        except Exception as e:
            raise ExampleServiceError(
                f"Failed to ping service: {str(e)}",
                service_name=self.config.service_name,
            )

    async def get_data(self, query: str, limit: Optional[int] = None) -> List[Dict]:
        """Get data from the service.

        Args:
            query: Query string
            limit: Maximum number of results to return

        Returns:
            List of data items

        Raises:
            ExampleServiceError: If there's an error getting data
        """
        try:
            # In a real implementation, this would call the API
            return [{"id": 1, "name": "Example", "query": query, "limit": limit}]
        except Exception as e:
            raise ExampleServiceError(
                f"Failed to get data: {str(e)}", service_name=self.config.service_name
            )
