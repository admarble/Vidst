"""
Test implementation for the service interface framework and async retry utility.

This script provides a simple way to test the functionality of the service
interface framework and async retry utility.
"""

import asyncio
import logging
import random
import sys
from typing import Dict

from src.core.services.base import BaseService, ServiceConfig, ServiceError
from src.core.services.utils import CircuitBreaker, async_retry, connection_retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("test_implementation")


class TestServiceError(ServiceError):
    """Error raised by the test service."""

    pass


class TestServiceConfig(ServiceConfig):
    """Configuration for the test service."""

    endpoint_url: str = "https://example.com/api"
    timeout: float = 5.0
    max_retries: int = 3


class TestService(BaseService[TestServiceConfig]):
    """Test service implementation.

    This class demonstrates a simple service implementation using the base
    service interface.
    """

    config_class = TestServiceConfig

    def __init__(self, config: TestServiceConfig):
        """Initialize the test service."""
        super().__init__(config)
        self.client = None
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize the service."""
        logger.info("Initializing test service...")

        # Simulate initialization with potential failure
        if random.random() < 0.3:
            raise TestServiceError(
                "Failed to initialize service (simulated)",
                service_name=self.config.service_name,
            )

        self.client = {"endpoint": self.config.endpoint_url}
        self.initialized = True
        logger.info("Test service initialized successfully")

    async def shutdown(self) -> None:
        """Shutdown the service."""
        logger.info("Shutting down test service...")
        self.client = None
        self.initialized = False
        logger.info("Test service shut down successfully")

    @connection_retry(max_retries=2, service_name="test_service")
    async def fetch_data(self, query: str) -> Dict:
        """Fetch data from the service with retry.

        This method demonstrates the use of the retry decorator.
        """
        logger.info(f"Fetching data with query: {query}")

        # Simulate random failures
        if random.random() < 0.7:
            raise ConnectionError("Connection failed (simulated)")

        return {"query": query, "result": "success"}


async def test_circuit_breaker():
    """Test the circuit breaker functionality."""
    logger.info("\n=== Testing Circuit Breaker ===")

    # Create a circuit breaker
    breaker = CircuitBreaker(
        failure_threshold=2, reset_timeout=3, service_name="test_circuit_breaker"
    )

    # Define a function that will fail most of the time
    async def flaky_function() -> str:
        if random.random() < 0.8:
            raise ConnectionError("Connection failed (simulated)")
        return "success"

    # Try multiple calls with circuit breaker
    for i in range(5):
        try:
            result = await breaker.execute(flaky_function)
            logger.info(f"Call {i+1} succeeded: {result}")
        except Exception as e:
            logger.error(f"Call {i+1} failed: {e}")

        # Wait a bit between calls
        await asyncio.sleep(1)

    # Wait for circuit breaker to reset
    logger.info("Waiting for circuit breaker to reset...")
    await asyncio.sleep(4)

    # Try again after reset
    try:
        result = await breaker.execute(flaky_function)
        logger.info(f"Call after reset succeeded: {result}")
    except Exception as e:
        logger.error(f"Call after reset failed: {e}")


async def test_retry_decorator():
    """Test the retry decorator functionality."""
    logger.info("\n=== Testing Retry Decorator ===")

    # Define a function with retry
    @async_retry(max_retries=3, base_delay=0.5, jitter=True, service_name="test_retry")
    async def retry_function() -> str:
        if random.random() < 0.7:
            raise TimeoutError("Operation timed out (simulated)")
        return "success"

    # Call the function
    try:
        result = await retry_function()
        logger.info(f"Function succeeded after retries: {result}")
    except Exception as e:
        logger.error(f"Function failed after all retries: {e}")


async def test_service_implementation():
    """Test the service implementation."""
    logger.info("\n=== Testing Service Implementation ===")

    # Create service configuration
    config = TestServiceConfig(
        service_name="test_service",
        endpoint_url="https://example.com/api",
        timeout=3.0,
        max_retries=2,
    )

    # Create service instance
    service = TestService(config)

    try:
        # Initialize service
        await service.initialize()

        # Call service method with retry
        try:
            data = await service.fetch_data("test_query")
            logger.info(f"Fetch data succeeded: {data}")
        except Exception as e:
            logger.error(f"Fetch data failed: {e}")

    except Exception as e:
        logger.error(f"Service initialization failed: {e}")

    finally:
        # Shutdown service
        await service.shutdown()


async def main():
    """Run all tests."""
    logger.info(
        "Starting tests for service interface framework and async retry utility"
    )

    # Set random seed for reproducibility
    random.seed(42)

    # Test circuit breaker
    await test_circuit_breaker()

    # Test retry decorator
    await test_retry_decorator()

    # Test service implementation
    await test_service_implementation()

    logger.info("All tests completed")


if __name__ == "__main__":
    # Run the tests
    asyncio.run(main())
