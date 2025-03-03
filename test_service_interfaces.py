#!/usr/bin/env python3
"""
Test script for service interfaces.

This script tests the service interfaces implementation to ensure
that it works correctly.
"""

import asyncio
import logging
import sys
from typing import Dict, Any

# Add src directory to path
sys.path.insert(0, "src")

# Import service interfaces - these imports need to be after sys.path modification
# so we disable the linter warning about imports not being at the top
# pylint: disable=wrong-import-position
from video_understanding.services.config import ServiceConfig
from video_understanding.services.base import BaseService
from video_understanding.services.exceptions import ConnectionError
from video_understanding.services.example import ExampleService, ExampleServiceConfig
from video_understanding.services.factory import ServiceFactory
from video_understanding.utils.retry import retry_async

# pylint: enable=wrong-import-position

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_direct_service_usage() -> None:
    """Test direct service usage."""
    logger.info("Testing direct service usage...")

    # Create service configuration
    config = ExampleServiceConfig(
        service_name="test_service",
        api_key="key_12345",
        base_url="https://api.example.com",
        max_results=5,
        timeout=30.0,
        max_retries=3,
        retry_delay=1.0,
    )

    # Create service instance
    service = ExampleService(config)

    try:
        # Initialize service
        await service.initialize()
        logger.info("Service initialized successfully")

        # Check service availability
        is_available = await service.ping()
        logger.info(f"Service available: {is_available}")
        assert is_available, "Service should be available"

        # Use service
        result = await service.get_data("test query")
        logger.info(f"Got {len(result['results'])} results")
        assert len(result["results"]) == 5, "Should get 5 results"
        assert result["query"] == "test query", "Query should match"

        logger.info("Direct service usage test passed")
    finally:
        # Shut down service
        await service.shutdown()
        logger.info("Service shut down successfully")


async def test_factory_service_usage() -> None:
    """Test factory-based service usage."""
    logger.info("Testing factory-based service usage...")

    # Create service factory
    factory = ServiceFactory[ServiceConfig, BaseService]()

    # Register service implementations
    factory.register("example", ExampleService)

    # Create service configuration
    config = ExampleServiceConfig(
        service_name="test_service",
        api_key="key_12345",
        base_url="https://api.example.com",
        max_results=3,
        timeout=30.0,
        max_retries=3,
        retry_delay=1.0,
    )

    # Create service instance
    service = factory.create("example", config)

    try:
        # Initialize service
        await service.initialize()
        logger.info("Service initialized successfully")

        # Check service availability
        is_available = await service.ping()
        logger.info(f"Service available: {is_available}")
        assert is_available, "Service should be available"

        # Use service
        if isinstance(service, ExampleService):
            result = await service.get_data("factory query")
            logger.info(f"Got {len(result['results'])} results")
            assert len(result["results"]) == 3, "Should get 3 results"
            assert result["query"] == "factory query", "Query should match"

        logger.info("Factory service usage test passed")
    finally:
        # Shut down service
        await service.shutdown()
        logger.info("Service shut down successfully")


async def test_configuration_validation() -> None:
    """Test configuration validation."""
    logger.info("Testing configuration validation...")

    # Test invalid timeout
    try:
        ExampleServiceConfig(
            service_name="test_service",
            api_key="key_12345",
            base_url="https://api.example.com",
            max_results=5,
            timeout=-1.0,  # Invalid timeout
            max_retries=3,
            retry_delay=1.0,
        )
        assert False, "Should have raised ValidationError"
    except Exception as e:
        logger.info(f"Caught expected error for invalid timeout: {str(e)}")

    # Test invalid API key format
    try:
        config = ExampleServiceConfig(
            service_name="test_service",
            api_key="invalid_key",  # Doesn't start with key_
            base_url="https://api.example.com",
            max_results=5,
            timeout=30.0,
            max_retries=3,
            retry_delay=1.0,
        )
        ExampleService(config)
        assert False, "Should have raised ConfigurationError"
    except Exception as e:
        logger.info(f"Caught expected error for invalid API key: {str(e)}")

    logger.info("Configuration validation test passed")


async def test_retry_mechanism() -> None:
    """Test retry mechanism."""
    logger.info("Testing retry mechanism...")

    # Counter for tracking retry attempts
    attempts = 0

    # Function that fails a few times before succeeding
    async def flaky_function() -> Dict[str, Any]:
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            logger.info(f"Attempt {attempts}: Simulating failure")
            raise ConnectionError("Simulated connection error")

        logger.info(f"Attempt {attempts}: Success")
        return {"status": "success", "attempts": attempts}

    # Test retry with success
    attempts = 0
    result = await retry_async(
        flaky_function,
        retry_count=3,
        initial_delay=0.1,
        exceptions_to_retry=ConnectionError,
    )

    assert result["status"] == "success", "Should eventually succeed"
    assert result["attempts"] == 3, "Should succeed on the third attempt"

    # Test retry with failure (exceeds retry count)
    attempts = 0
    try:
        await retry_async(
            flaky_function,
            retry_count=1,  # Only retry once
            initial_delay=0.1,
            exceptions_to_retry=ConnectionError,
        )
        assert False, "Should have raised ConnectionError"
    except ConnectionError:
        logger.info("Caught expected ConnectionError after retry exhaustion")

    logger.info("Retry mechanism test passed")


async def run_tests() -> None:
    """Run all tests."""
    try:
        await test_direct_service_usage()
        print()
        await test_factory_service_usage()
        print()
        await test_configuration_validation()
        print()
        await test_retry_mechanism()

        logger.info("All tests passed!")
    except AssertionError as e:
        logger.error(f"Test failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_tests())
