"""
Example usage of the service interfaces.

This module demonstrates how to use the service interfaces with the new
configuration management system.
"""

import asyncio
import logging
from typing import Any, Dict

from src.core.services.base import BaseService, ServiceConfig
from src.core.services.config import CircuitBreakerConfig, RetryConfig
from src.core.services.error_handling import (
    EnhancedServiceError,
    ErrorCategory,
    ErrorSeverity,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExampleServiceConfig(ServiceConfig):
    """Example service configuration."""

    api_key: str
    api_url: str = "https://api.example.com"

    # Customize circuit breaker configuration
    circuit_breaker: CircuitBreakerConfig = CircuitBreakerConfig(
        enabled=True,
        failure_threshold=3,  # Lower threshold for example
        reset_timeout=30,  # Shorter timeout for example
    )

    # Customize retry configuration
    retry: RetryConfig = RetryConfig(
        max_retries=2,  # Fewer retries for example
        base_delay=0.5,  # Shorter delay for example
        max_delay=5.0,  # Lower max delay for example
        backoff_factor=1.5,  # Smaller backoff factor
        jitter=True,
    )


class ExampleService(BaseService[ExampleServiceConfig]):
    """Example service implementation."""

    config_class = ExampleServiceConfig

    def __init__(self, config: ExampleServiceConfig):
        """Initialize the service."""
        super().__init__(config)
        self._connected = False
        self._client = None

        # Create a circuit breaker from the configuration
        self.circuit_breaker = self.config.create_circuit_breaker()

        # Create retry decorators from the configuration
        self.retry_decorator = self.config.create_retry_decorator()
        self.simple_retry = self.config.create_simple_retry_decorator()
        self.connection_retry = self.config.create_connection_retry_decorator()

    async def initialize(self) -> None:
        """Initialize the service."""
        logger.info("[%s] Initializing service", self.config.service_name)

        # Use the connection retry decorator for initialization
        @self.connection_retry
        async def connect():
            # Simulate connection
            await asyncio.sleep(0.1)
            return "connected"

        result = await connect()
        self._connected = True
        logger.info("[%s] Service initialized: %s", self.config.service_name, result)

    async def shutdown(self) -> None:
        """Shutdown the service."""
        logger.info("[%s] Shutting down service", self.config.service_name)

        # Simulate disconnection
        await asyncio.sleep(0.1)
        self._connected = False

        logger.info("[%s] Service shut down", self.config.service_name)

    async def get_data(self, resource_id: str) -> Dict[str, Any]:
        """Get data from the service.

        This method demonstrates using the circuit breaker and retry logic.

        Args:
            resource_id: ID of the resource to get

        Returns:
            Resource data

        Raises:
            EnhancedServiceError: If the operation fails
        """
        if not self._connected:
            raise EnhancedServiceError(
                message="Service is not connected",
                service_name=self.config.service_name,
                category=ErrorCategory.SERVICE_UNAVAILABLE,
                severity=ErrorSeverity.ERROR,
            )

        # Use the circuit breaker to execute the operation
        if self.circuit_breaker:
            return await self.circuit_breaker.execute(self._get_data_impl, resource_id)
        else:
            return await self._get_data_impl(resource_id)

    @property
    def is_connected(self) -> bool:
        """Check if the service is connected."""
        return self._connected

    async def _get_data_impl(self, resource_id: str) -> Dict[str, Any]:
        """Implementation of get_data."""
        # Simulate API call
        await asyncio.sleep(0.1)

        # Return mock data
        return {
            "id": resource_id,
            "name": f"Resource {resource_id}",
            "status": "active",
        }


async def main():
    """Run the example."""
    # Create a service configuration
    config = ExampleServiceConfig(
        service_name="example_service",
        api_key="example_key",
        api_url="https://api.example.com",
        timeout=30.0,  # Default timeout in seconds
    )

    # Create a service instance
    service = ExampleService(config)

    try:
        # Initialize the service
        await service.initialize()

        # Use the service
        data = await service.get_data("123")
        logger.info("Got data: %s", data)

    finally:
        # Shutdown the service
        await service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
