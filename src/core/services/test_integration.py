"""
Test script for the simplified service interfaces.

This script demonstrates the integration of the simplified service interfaces
with the error handling patterns.
"""

import asyncio
import logging
import random
import sys
from typing import Any, Dict

from src.core.services.error_handling import (
    EnhancedServiceError,
    ErrorCategory,
    ErrorSeverity,
)
from src.core.services.simplified import SimpleService, SimpleServiceConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("test_integration")


# Test service configuration
class TestServiceConfig(SimpleServiceConfig):
    """Test service configuration."""

    api_key: str
    endpoint: str
    test_mode: bool = True
    timeout: float
    max_retries: int
    retry_delay: float
    circuit_breaker_enabled: bool
    failure_threshold: int
    reset_timeout: float
    log_level: str


# Test service implementation
class TestService(SimpleService[TestServiceConfig]):
    """Test service implementation."""

    config_class = TestServiceConfig

    def __init__(self, config: TestServiceConfig):
        """Initialize the test service."""
        super().__init__(config)
        self._connected = False
        self._failure_count = 0
        self._data = {}

    async def _initialize_impl(self) -> None:
        """Initialize the test service."""
        logger.info("Initializing test service...")

        # Simulate connection delay
        await asyncio.sleep(0.5)

        # Simulate random initialization failure
        if random.random() < 0.3 and not self.config.test_mode:
            raise EnhancedServiceError(
                message="Failed to initialize test service",
                service_name=self.config.service_name,
                category=ErrorCategory.SERVICE_UNAVAILABLE,
                severity=ErrorSeverity.ERROR,
                retry_allowed=True,
            )

        self._connected = True
        logger.info("Test service initialized")

    async def _shutdown_impl(self) -> None:
        """Shutdown the test service."""
        logger.info("Shutting down test service...")

        # Simulate shutdown delay
        await asyncio.sleep(0.3)

        self._connected = False
        self._data = {}
        logger.info("Test service shut down")

    async def _health_check_impl(self) -> Dict[str, Any]:
        """Check the health of the test service."""
        if not self._connected:
            raise EnhancedServiceError(
                message="Test service is not connected",
                service_name=self.config.service_name,
                category=ErrorCategory.SERVICE_UNAVAILABLE,
                severity=ErrorSeverity.WARNING,
                retry_allowed=True,
            )

        return {
            "connected": True,
            "endpoint": self.config.endpoint,
            "test_mode": self.config.test_mode,
            "data_count": len(self._data),
        }

    async def get_data(self, key: str) -> Dict[str, Any]:
        """Get data from the test service.

        Args:
            key: Data key

        Returns:
            Data item

        Raises:
            EnhancedServiceError: If data retrieval fails
        """
        return await self.execute_with_retry(self._get_data_impl, key)

    async def _get_data_impl(self, key: str) -> Dict[str, Any]:
        """Implementation of data retrieval.

        Args:
            key: Data key

        Returns:
            Data item

        Raises:
            EnhancedServiceError: If data retrieval fails
        """
        if not self._connected:
            raise EnhancedServiceError(
                message="Test service is not connected",
                service_name=self.config.service_name,
                category=ErrorCategory.SERVICE_UNAVAILABLE,
                severity=ErrorSeverity.ERROR,
                retry_allowed=True,
            )

        # Check if data exists
        if key in self._data:
            return self._data[key]

        # Simulate API call
        await asyncio.sleep(0.2)

        # Simulate transient failure
        self._failure_count += 1
        if self._failure_count % 3 == 0:
            error_type = random.choice(
                [
                    ErrorCategory.NETWORK,
                    ErrorCategory.TIMEOUT,
                    ErrorCategory.SERVICE_UNAVAILABLE,
                ]
            )

            raise EnhancedServiceError(
                message=f"Simulated failure: {error_type.value}",
                service_name=self.config.service_name,
                category=error_type,
                severity=ErrorSeverity.ERROR,
                retry_allowed=True,
            )

        # Create data item
        data_item = {
            "id": key,
            "name": f"Test data for {key}",
            "timestamp": asyncio.get_event_loop().time(),
            "random_value": random.random(),
        }

        # Store in cache
        self._data[key] = data_item

        return data_item

    async def create_data(self, key: str, value: Dict[str, Any]) -> Dict[str, Any]:
        """Create data in the test service.

        Args:
            key: Data key
            value: Data value

        Returns:
            Created data item

        Raises:
            EnhancedServiceError: If data creation fails
        """
        return await self.execute_with_retry(self._create_data_impl, key, value)

    async def _create_data_impl(
        self, key: str, value: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Implementation of data creation.

        Args:
            key: Data key
            value: Data value

        Returns:
            Created data item

        Raises:
            EnhancedServiceError: If data creation fails
        """
        if not self._connected:
            raise EnhancedServiceError(
                message="Test service is not connected",
                service_name=self.config.service_name,
                category=ErrorCategory.SERVICE_UNAVAILABLE,
                severity=ErrorSeverity.ERROR,
                retry_allowed=True,
            )

        # Check if data already exists
        if key in self._data:
            raise EnhancedServiceError(
                message=f"Data with key '{key}' already exists",
                service_name=self.config.service_name,
                category=ErrorCategory.INVALID_INPUT,
                severity=ErrorSeverity.WARNING,
                retry_allowed=False,
            )

        # Simulate API call
        await asyncio.sleep(0.2)

        # Create data item
        data_item = {
            "id": key,
            "timestamp": asyncio.get_event_loop().time(),
            **value,
        }

        # Store in cache
        self._data[key] = data_item

        return data_item


async def test_normal_operation():
    """Test normal operation of the service."""
    logger.info("=== Testing normal operation ===")

    # Create service configuration
    config = TestServiceConfig(
        service_name="test_service",
        api_key="test_key_123",
        endpoint="https://api.example.com/test",
        test_mode=True,
        timeout=5.0,
        max_retries=3,
        retry_delay=0.5,
        circuit_breaker_enabled=True,
        failure_threshold=3,
        reset_timeout=5,
        log_level="INFO",
    )

    # Create service instance
    service = TestService(config)

    try:
        # Initialize service
        await service.initialize()

        # Check health
        health = await service.health_check()
        logger.info(f"Health check: {health}")

        # Get data (should create new data)
        data1 = await service.get_data("key1")
        logger.info(f"Got data: {data1}")

        # Get same data again (should return cached data)
        data2 = await service.get_data("key1")
        logger.info(f"Got cached data: {data2}")

        # Create data
        created = await service.create_data("key2", {"name": "Test Item", "value": 42})
        logger.info(f"Created data: {created}")

        # Try to create duplicate data (should fail with non-retryable error)
        try:
            await service.create_data("key2", {"name": "Duplicate", "value": 99})
        except EnhancedServiceError as e:
            logger.info(f"Expected error: {e}")

    finally:
        # Shutdown service
        await service.shutdown()


async def test_error_handling():
    """Test error handling in the service."""
    logger.info("=== Testing error handling ===")

    # Create service configuration with circuit breaker enabled
    config = TestServiceConfig(
        service_name="test_service_errors",
        api_key="test_key_456",
        endpoint="https://api.example.com/test",
        test_mode=True,
        timeout=5.0,
        max_retries=3,
        retry_delay=0.5,
        circuit_breaker_enabled=True,
        failure_threshold=3,
        reset_timeout=5,
        log_level="INFO",
    )

    # Create service instance
    service = TestService(config)

    try:
        # Initialize service
        await service.initialize()

        # Make multiple requests to trigger failures and retries
        for i in range(10):
            try:
                data = await service.get_data(f"error_key_{i}")
                logger.info(f"Got data {i}: {data}")
            except EnhancedServiceError as e:
                logger.info(f"Error {i}: {e}")

            # Small delay between requests
            await asyncio.sleep(0.1)

    finally:
        # Shutdown service
        await service.shutdown()


async def main():
    """Run the integration tests."""
    logger.info("Starting integration tests...")

    # Test normal operation
    await test_normal_operation()

    # Test error handling
    await test_error_handling()

    logger.info("Integration tests completed")


if __name__ == "__main__":
    asyncio.run(main())
