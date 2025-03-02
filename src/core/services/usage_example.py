"""
Usage example for the service interface framework.

This module demonstrates how to use the service interface framework to create
and use service instances.
"""

import asyncio
import random
from typing import Dict, List

from src.core.services.example import ExampleService, ExampleServiceConfig
from src.core.services.factory import ServiceFactory
from src.core.services.utils import CircuitBreaker, CircuitBreakerOpenError, async_retry


async def basic_usage_example():
    """Demonstrate basic usage of the service interface framework."""

    # Create a service configuration
    config = ExampleServiceConfig(
        service_name="example_service",
        api_key="key_12345",
        api_url="https://api.example.com",
        cache_ttl=60,
        timeout=60.0,
        max_retries=5,
    )

    # Create a service instance
    service = ExampleService(config)

    try:
        # Initialize the service
        await service.initialize()

        # Use the service
        data = await service.get_data("test_query", limit=10)
        print(f"Got data: {data}")

    finally:
        # Shutdown the service
        await service.shutdown()


async def factory_usage_example():
    """Demonstrate usage of the service factory."""

    # Create a service factory
    factory = ServiceFactory()

    # Register service implementations
    factory.register("example", ExampleService)

    # Create a service configuration
    config = ExampleServiceConfig(
        service_name="example_service",
        api_key="key_12345",
        api_url="https://api.example.com",
        cache_ttl=60,
        timeout=60.0,
        max_retries=5,
    )

    # Create a service instance using the factory
    service = factory.create("example", config)

    try:
        # Initialize the service
        await service.initialize()

        # Use the service
        data = await service.get_data("test_query")
        print(f"Got data: {data}")

    finally:
        # Shutdown the service
        await service.shutdown()


async def retry_usage_example():
    """Demonstrate usage of the retry decorator."""

    # Define a function that might fail
    @async_retry(max_retries=3, base_delay=1.0, jitter=True)
    async def flaky_function() -> List[Dict]:
        # Simulate a random failure
        if random.random() < 0.7:
            raise ConnectionError("Simulated connection error")
        return [{"status": "success"}]

    try:
        # Call the function with retry
        result = await flaky_function()
        print(f"Got result after retries: {result}")

    except ConnectionError as e:
        print(f"Function failed after retries: {e}")


async def circuit_breaker_usage_example():
    """Demonstrate usage of the circuit breaker."""

    # Create a circuit breaker
    breaker = CircuitBreaker(
        failure_threshold=3, reset_timeout=5, service_name="example_service"
    )

    # Define a function that might fail
    async def flaky_function() -> List[Dict]:
        # Simulate a random failure
        if random.random() < 0.7:
            raise ConnectionError("Simulated connection error")
        return [{"status": "success"}]

    # Try multiple calls with circuit breaker
    for i in range(10):
        try:
            # Execute the function with circuit breaker protection
            result = await breaker.execute(flaky_function)
            print(f"Call {i+1} succeeded: {result}")

        except (ConnectionError, CircuitBreakerOpenError) as e:
            print(f"Call {i+1} failed: {e}")

        # Wait a bit between calls
        await asyncio.sleep(1)


async def main():
    """Run all examples."""

    print("\n=== Basic Usage Example ===")
    await basic_usage_example()

    print("\n=== Factory Usage Example ===")
    await factory_usage_example()

    print("\n=== Retry Usage Example ===")
    await retry_usage_example()

    print("\n=== Circuit Breaker Usage Example ===")
    await circuit_breaker_usage_example()


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
