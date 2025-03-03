"""Tests for the configuration management system.

This module contains tests for the configuration management system,
including the CircuitBreakerConfig and RetryConfig classes.
"""

import asyncio
import unittest
from contextlib import suppress

import pytest
from pydantic import ValidationError

from src.core.services.base import ServiceConfig
from src.core.services.config import CircuitBreakerConfig, RetryConfig
from src.core.services.utils import CircuitBreaker

# Constants to replace magic numbers
DEFAULT_FAILURE_THRESHOLD = 5
DEFAULT_RESET_TIMEOUT = 60
CUSTOM_FAILURE_THRESHOLD = 10
CUSTOM_RESET_TIMEOUT = 120
CB_FAILURE_THRESHOLD = 3
CB_RESET_TIMEOUT = 30
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0
DEFAULT_MAX_DELAY = 60.0
DEFAULT_BACKOFF_FACTOR = 2.0
CUSTOM_MAX_RETRIES = 5
CUSTOM_BASE_DELAY = 0.5
CUSTOM_MAX_DELAY = 30.0
CUSTOM_BACKOFF_FACTOR = 1.5
DEFAULT_TIMEOUT = 30.0
CUSTOM_TIMEOUT = 60.0
TEST_RETRY_MAX_RETRIES = 2
SHORT_BASE_DELAY = 0.1
TEST_FAILURE_THRESHOLD = 2
TEST_RESET_TIMEOUT = 1
RESET_TIMEOUT_BUFFER = 0.1


class TestCircuitBreakerConfig(unittest.TestCase):
    """Tests for the CircuitBreakerConfig class."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        config = CircuitBreakerConfig(
            enabled=True,
            failure_threshold=DEFAULT_FAILURE_THRESHOLD,
            reset_timeout=DEFAULT_RESET_TIMEOUT,
        )
        assert config.enabled
        assert config.failure_threshold == DEFAULT_FAILURE_THRESHOLD
        assert config.reset_timeout == DEFAULT_RESET_TIMEOUT

    def test_custom_values(self):
        """Test that custom values are set correctly."""
        config = CircuitBreakerConfig(
            enabled=False,
            failure_threshold=CUSTOM_FAILURE_THRESHOLD,
            reset_timeout=CUSTOM_RESET_TIMEOUT,
        )
        assert not config.enabled
        assert config.failure_threshold == CUSTOM_FAILURE_THRESHOLD
        assert config.reset_timeout == CUSTOM_RESET_TIMEOUT

    def test_validation_failure_threshold(self):
        """Test validation for failure_threshold."""
        with pytest.raises(ValidationError):
            CircuitBreakerConfig(
                enabled=True,
                failure_threshold=0,
                reset_timeout=DEFAULT_RESET_TIMEOUT,
            )

    def test_validation_reset_timeout(self):
        """Test validation for reset_timeout."""
        with pytest.raises(ValidationError):
            CircuitBreakerConfig(
                enabled=True,
                failure_threshold=DEFAULT_FAILURE_THRESHOLD,
                reset_timeout=0,
            )

    def test_create_circuit_breaker(self):
        """Test creating a CircuitBreaker instance."""
        config = CircuitBreakerConfig(
            enabled=True,
            failure_threshold=CB_FAILURE_THRESHOLD,
            reset_timeout=CB_RESET_TIMEOUT,
        )
        circuit_breaker = config.create_circuit_breaker(service_name="test_service")
        assert isinstance(circuit_breaker, CircuitBreaker)
        # Check that circuit_breaker is not None before accessing attributes
        assert circuit_breaker is not None
        if circuit_breaker:  # Add this check to satisfy the linter
            assert circuit_breaker.failure_threshold == CB_FAILURE_THRESHOLD
            assert circuit_breaker.reset_timeout == CB_RESET_TIMEOUT
            assert circuit_breaker.service_name == "test_service"

    def test_create_circuit_breaker_disabled(self):
        """Test creating a CircuitBreaker instance when disabled."""
        config = CircuitBreakerConfig(
            enabled=False,
            failure_threshold=DEFAULT_FAILURE_THRESHOLD,
            reset_timeout=DEFAULT_RESET_TIMEOUT,
        )
        circuit_breaker = config.create_circuit_breaker()
        assert circuit_breaker is None


class TestRetryConfig(unittest.TestCase):
    """Tests for the RetryConfig class."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        config = RetryConfig(
            max_retries=DEFAULT_MAX_RETRIES,
            base_delay=DEFAULT_BASE_DELAY,
            max_delay=DEFAULT_MAX_DELAY,
            backoff_factor=DEFAULT_BACKOFF_FACTOR,
            jitter=True,
        )
        assert config.max_retries == DEFAULT_MAX_RETRIES
        assert config.base_delay == DEFAULT_BASE_DELAY
        assert config.max_delay == DEFAULT_MAX_DELAY
        assert config.backoff_factor == DEFAULT_BACKOFF_FACTOR
        assert config.jitter

    def test_custom_values(self):
        """Test that custom values are set correctly."""
        config = RetryConfig(
            max_retries=CUSTOM_MAX_RETRIES,
            base_delay=CUSTOM_BASE_DELAY,
            max_delay=CUSTOM_MAX_DELAY,
            backoff_factor=CUSTOM_BACKOFF_FACTOR,
            jitter=False,
        )
        assert config.max_retries == CUSTOM_MAX_RETRIES
        assert config.base_delay == CUSTOM_BASE_DELAY
        assert config.max_delay == CUSTOM_MAX_DELAY
        assert config.backoff_factor == CUSTOM_BACKOFF_FACTOR
        assert not config.jitter

    def test_validation_max_retries(self):
        """Test validation for max_retries."""
        with pytest.raises(ValidationError):
            RetryConfig(
                max_retries=-1,
                base_delay=DEFAULT_BASE_DELAY,
                max_delay=DEFAULT_MAX_DELAY,
                backoff_factor=DEFAULT_BACKOFF_FACTOR,
                jitter=True,
            )

    def test_validation_delays(self):
        """Test validation for delay values."""
        with pytest.raises(ValidationError):
            RetryConfig(
                max_retries=DEFAULT_MAX_RETRIES,
                base_delay=0,
                max_delay=DEFAULT_MAX_DELAY,
                backoff_factor=DEFAULT_BACKOFF_FACTOR,
                jitter=True,
            )

        with pytest.raises(ValidationError):
            RetryConfig(
                max_retries=DEFAULT_MAX_RETRIES,
                base_delay=DEFAULT_BASE_DELAY,
                max_delay=0,
                backoff_factor=DEFAULT_BACKOFF_FACTOR,
                jitter=True,
            )

    def test_validation_backoff_factor(self):
        """Test validation for backoff_factor."""
        with pytest.raises(ValidationError):
            RetryConfig(
                max_retries=DEFAULT_MAX_RETRIES,
                base_delay=DEFAULT_BASE_DELAY,
                max_delay=DEFAULT_MAX_DELAY,
                backoff_factor=1.0,
                jitter=True,
            )

    def test_create_retry_decorator(self):
        """Test creating a retry decorator."""
        config = RetryConfig(
            max_retries=TEST_RETRY_MAX_RETRIES,
            base_delay=CUSTOM_BASE_DELAY,
            max_delay=DEFAULT_MAX_DELAY,
            backoff_factor=DEFAULT_BACKOFF_FACTOR,
            jitter=True,
        )
        retry_decorator = config.create_retry_decorator(service_name="test_service")
        assert callable(retry_decorator)

    def test_create_simple_retry_decorator(self):
        """Test creating a simple retry decorator."""
        config = RetryConfig(
            max_retries=TEST_RETRY_MAX_RETRIES,
            base_delay=CUSTOM_BASE_DELAY,
            max_delay=DEFAULT_MAX_DELAY,
            backoff_factor=DEFAULT_BACKOFF_FACTOR,
            jitter=True,
        )
        simple_retry = config.create_simple_retry_decorator(service_name="test_service")
        assert callable(simple_retry)

    def test_create_connection_retry_decorator(self):
        """Test creating a connection retry decorator."""
        config = RetryConfig(
            max_retries=TEST_RETRY_MAX_RETRIES,
            base_delay=DEFAULT_BASE_DELAY,
            max_delay=DEFAULT_MAX_DELAY,
            backoff_factor=DEFAULT_BACKOFF_FACTOR,
            jitter=True,
        )
        connection_retry = config.create_connection_retry_decorator(
            service_name="test_service",
        )
        assert callable(connection_retry)


class TestServiceConfig(unittest.TestCase):
    """Tests for the ServiceConfig class."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        config = ServiceConfig(service_name="test_service", timeout=DEFAULT_TIMEOUT)
        assert config.service_name == "test_service"
        assert config.timeout == DEFAULT_TIMEOUT
        assert isinstance(config.circuit_breaker, CircuitBreakerConfig)
        assert isinstance(config.retry, RetryConfig)

    def test_custom_values(self):
        """Test that custom values are set correctly."""
        config = ServiceConfig(
            service_name="test_service",
            timeout=CUSTOM_TIMEOUT,
            circuit_breaker=CircuitBreakerConfig(
                enabled=False,
                failure_threshold=CUSTOM_FAILURE_THRESHOLD,
                reset_timeout=CUSTOM_RESET_TIMEOUT,
            ),
            retry=RetryConfig(
                max_retries=CUSTOM_MAX_RETRIES,
                base_delay=CUSTOM_BASE_DELAY,
                max_delay=CUSTOM_MAX_DELAY,
                backoff_factor=CUSTOM_BACKOFF_FACTOR,
                jitter=False,
            ),
        )
        assert config.service_name == "test_service"
        assert config.timeout == CUSTOM_TIMEOUT
        assert not config.circuit_breaker.enabled
        assert config.circuit_breaker.failure_threshold == CUSTOM_FAILURE_THRESHOLD
        assert config.circuit_breaker.reset_timeout == CUSTOM_RESET_TIMEOUT
        assert config.retry.max_retries == CUSTOM_MAX_RETRIES
        assert config.retry.base_delay == CUSTOM_BASE_DELAY
        assert config.retry.max_delay == CUSTOM_MAX_DELAY
        assert config.retry.backoff_factor == CUSTOM_BACKOFF_FACTOR
        assert not config.retry.jitter

    def test_create_circuit_breaker(self):
        """Test creating a CircuitBreaker instance."""
        config = ServiceConfig(
            service_name="test_service",
            timeout=DEFAULT_TIMEOUT,
            circuit_breaker=CircuitBreakerConfig(
                enabled=True,
                failure_threshold=CB_FAILURE_THRESHOLD,
                reset_timeout=CB_RESET_TIMEOUT,
            ),
        )
        circuit_breaker = config.create_circuit_breaker()
        # Check that circuit_breaker is not None before accessing attributes
        assert circuit_breaker is not None
        if circuit_breaker:  # Add this check to satisfy the linter
            assert isinstance(circuit_breaker, CircuitBreaker)
            assert circuit_breaker.failure_threshold == CB_FAILURE_THRESHOLD
            assert circuit_breaker.reset_timeout == CB_RESET_TIMEOUT
            assert circuit_breaker.service_name == "test_service"

    def test_create_retry_decorator(self):
        """Test creating a retry decorator."""
        config = ServiceConfig(
            service_name="test_service",
            timeout=DEFAULT_TIMEOUT,
            retry=RetryConfig(
                max_retries=TEST_RETRY_MAX_RETRIES,
                base_delay=CUSTOM_BASE_DELAY,
                max_delay=DEFAULT_MAX_DELAY,
                backoff_factor=DEFAULT_BACKOFF_FACTOR,
                jitter=True,
            ),
        )
        retry_decorator = config.create_retry_decorator()
        assert callable(retry_decorator)

    def test_create_simple_retry_decorator(self):
        """Test creating a simple retry decorator."""
        config = ServiceConfig(
            service_name="test_service",
            timeout=DEFAULT_TIMEOUT,
            retry=RetryConfig(
                max_retries=TEST_RETRY_MAX_RETRIES,
                base_delay=CUSTOM_BASE_DELAY,
                max_delay=DEFAULT_MAX_DELAY,
                backoff_factor=DEFAULT_BACKOFF_FACTOR,
                jitter=True,
            ),
        )
        simple_retry = config.create_simple_retry_decorator()
        assert callable(simple_retry)

    def test_create_connection_retry_decorator(self):
        """Test creating a connection retry decorator."""
        config = ServiceConfig(
            service_name="test_service",
            timeout=DEFAULT_TIMEOUT,
            retry=RetryConfig(
                max_retries=TEST_RETRY_MAX_RETRIES,
                base_delay=DEFAULT_BASE_DELAY,
                max_delay=DEFAULT_MAX_DELAY,
                backoff_factor=DEFAULT_BACKOFF_FACTOR,
                jitter=True,
            ),
        )
        connection_retry = config.create_connection_retry_decorator()
        assert callable(connection_retry)


@pytest.mark.asyncio
async def test_retry_decorator_functionality():
    """Test that the retry decorator actually retries."""
    config = RetryConfig(
        max_retries=TEST_RETRY_MAX_RETRIES,
        base_delay=SHORT_BASE_DELAY,  # Short delay for testing
        max_delay=DEFAULT_MAX_DELAY,
        backoff_factor=DEFAULT_BACKOFF_FACTOR,
        jitter=False,  # Disable jitter for predictable testing
    )
    retry_decorator = config.create_retry_decorator(service_name="test_service")

    # Counter to track number of attempts
    attempts = 0
    max_failures = TEST_RETRY_MAX_RETRIES

    # Function that fails twice then succeeds
    @retry_decorator
    async def flaky_function():
        nonlocal attempts
        attempts += 1
        if attempts <= max_failures:
            error_message = "Simulated connection error"
            raise ConnectionError(error_message)
        return "success"

    # Should succeed after 3 attempts (initial + 2 retries)
    result = await flaky_function()
    assert result == "success"
    expected_attempts = DEFAULT_MAX_RETRIES
    assert attempts == expected_attempts


@pytest.mark.asyncio
async def test_circuit_breaker_functionality():
    """Test that the circuit breaker opens after failures."""
    failure_threshold = TEST_FAILURE_THRESHOLD
    reset_timeout = TEST_RESET_TIMEOUT

    config = CircuitBreakerConfig(
        enabled=True,
        failure_threshold=failure_threshold,  # Open after 2 failures
        reset_timeout=reset_timeout,  # Short timeout for testing (must be an integer)
    )
    circuit_breaker = config.create_circuit_breaker(service_name="test_service")

    # Ensure circuit_breaker is not None before proceeding
    assert (
        circuit_breaker is not None
    ), "Circuit breaker should not be None when enabled"

    # Counter to track number of attempts
    attempts = 0

    # Function that always fails
    async def failing_function():
        nonlocal attempts
        attempts += 1
        error_message = "Simulated error"
        raise ValueError(error_message)

    # Should fail and open the circuit after 2 attempts
    for _ in range(failure_threshold):
        with suppress(ValueError):
            await circuit_breaker.execute(failing_function)

    # Circuit should be open now
    from src.core.services.utils import CircuitBreakerOpenError

    with pytest.raises(CircuitBreakerOpenError):
        await circuit_breaker.execute(failing_function)

    # Wait for reset timeout
    await asyncio.sleep(
        reset_timeout
        + RESET_TIMEOUT_BUFFER,  # Wait slightly longer than the reset timeout
    )

    # Circuit should be closed and allow another attempt
    with suppress(ValueError):
        await circuit_breaker.execute(failing_function)

    expected_attempts = DEFAULT_MAX_RETRIES  # Initial 2 failures + 1 after reset
    assert attempts == expected_attempts


if __name__ == "__main__":
    unittest.main()
