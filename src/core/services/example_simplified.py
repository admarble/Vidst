"""
Example implementation of the simplified service interface.

This module demonstrates how to use the simplified service interface to create
a service implementation with standardized error handling and configuration.
"""

import asyncio
import random
from typing import Any, Dict, List, Optional

from pydantic import Field

from src.core.services.error_handling import (
    EnhancedServiceError,
    ErrorCategory,
    ErrorSeverity,
)
from src.core.services.simplified import SimpleService, SimpleServiceConfig


class ExampleServiceConfig(SimpleServiceConfig):
    """Configuration for the example service."""

    api_key: str = Field(..., description="API key for authentication")
    api_url: str = Field("https://api.example.com", description="API URL")
    cache_ttl: int = Field(300, description="Cache TTL in seconds")


class ExampleSimplifiedService(SimpleService[ExampleServiceConfig]):
    """Example implementation of the simplified service interface.

    This class demonstrates how to implement a service using the simplified
    service interface with standardized error handling and configuration.
    """

    # Override the config_class class variable
    config_class = ExampleServiceConfig

    def __init__(self, config: ExampleServiceConfig):
        """Initialize the example service.

        Args:
            config: Service configuration
        """
        super().__init__(config)
        self._connected = False
        self._data_cache = {}

    def validate_config(self) -> None:
        """Validate the service configuration.

        Raises:
            EnhancedServiceError: If configuration is invalid
        """
        super().validate_config()

        # Additional validation for example service
        if not self.config.api_key.startswith("key_"):
            raise EnhancedServiceError(
                message="API key must start with 'key_'",
                service_name=self.config.service_name,
                category=ErrorCategory.INVALID_INPUT,
                severity=ErrorSeverity.ERROR,
                retry_allowed=False,
            )

    async def _initialize_impl(self) -> None:
        """Implementation of service initialization.

        Raises:
            EnhancedServiceError: If initialization fails
        """
        # Simulate API connection
        await asyncio.sleep(0.5)

        # Simulate random connection failure (10% chance)
        if random.random() < 0.1:
            raise EnhancedServiceError(
                message="Failed to connect to API",
                service_name=self.config.service_name,
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.ERROR,
                retry_allowed=True,
            )

        self._connected = True

    async def _shutdown_impl(self) -> None:
        """Implementation of service shutdown.

        Raises:
            EnhancedServiceError: If shutdown fails
        """
        # Simulate API disconnection
        await asyncio.sleep(0.2)
        self._connected = False
        self._data_cache = {}

    async def _health_check_impl(self) -> Dict[str, Any]:
        """Implementation of service health check.

        Returns:
            Dictionary with health check information

        Raises:
            EnhancedServiceError: If health check fails
        """
        if not self._connected:
            raise EnhancedServiceError(
                message="Service is not connected",
                service_name=self.config.service_name,
                category=ErrorCategory.SERVICE_UNAVAILABLE,
                severity=ErrorSeverity.WARNING,
                retry_allowed=True,
            )

        return {
            "connected": True,
            "cache_size": len(self._data_cache),
            "api_url": self.config.api_url,
        }

    async def get_data(
        self, query: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get data from the service.

        Args:
            query: Query string
            limit: Maximum number of results to return

        Returns:
            List of data items

        Raises:
            EnhancedServiceError: If data retrieval fails
        """
        # Use the execute_with_retry method to handle retries and circuit breaking
        return await self.execute_with_retry(self._get_data_impl, query, limit)

    async def _get_data_impl(
        self, query: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Implementation of data retrieval.

        Args:
            query: Query string
            limit: Maximum number of results to return

        Returns:
            List of data items

        Raises:
            EnhancedServiceError: If data retrieval fails
        """
        if not self._connected:
            raise EnhancedServiceError(
                message="Service is not connected",
                service_name=self.config.service_name,
                category=ErrorCategory.SERVICE_UNAVAILABLE,
                severity=ErrorSeverity.ERROR,
                retry_allowed=True,
            )

        # Check cache first
        cache_key = f"{query}:{limit}"
        if cache_key in self._data_cache:
            return self._data_cache[cache_key]

        # Simulate API call
        await asyncio.sleep(0.3)

        # Simulate random failure (20% chance)
        if random.random() < 0.2:
            error_type = random.choice(
                [
                    ErrorCategory.NETWORK,
                    ErrorCategory.TIMEOUT,
                    ErrorCategory.SERVICE_UNAVAILABLE,
                ]
            )

            raise EnhancedServiceError(
                message=f"API call failed: {error_type.value}",
                service_name=self.config.service_name,
                category=error_type,
                severity=ErrorSeverity.ERROR,
                retry_allowed=True,
            )

        # Generate some fake data
        result_count = limit or random.randint(1, 10)
        results = [
            {
                "id": f"item_{i}",
                "name": f"Result {i} for {query}",
                "score": random.random(),
                "timestamp": int(asyncio.get_event_loop().time()),
            }
            for i in range(result_count)
        ]

        # Cache the results
        self._data_cache[cache_key] = results

        return results


async def example_usage():
    """Demonstrate usage of the simplified service interface."""

    # Create a service configuration
    config = ExampleServiceConfig(
        service_name="example_service",
        api_key="key_12345",
        api_url="https://api.example.com",
        cache_ttl=60,
        timeout=30.0,
        max_retries=3,
        retry_delay=1.0,
        circuit_breaker_enabled=True,
        failure_threshold=5,
        reset_timeout=60,
        log_level="INFO",
    )

    # Create a service instance
    service = ExampleSimplifiedService(config)

    try:
        # Initialize the service
        await service.initialize()

        # Check service health
        health = await service.health_check()
        print(f"Service health: {health}")

        # Use the service
        data = await service.get_data("test_query", limit=5)
        print(f"Got data: {data}")

    finally:
        # Shutdown the service
        await service.shutdown()


if __name__ == "__main__":
    asyncio.run(example_usage())
