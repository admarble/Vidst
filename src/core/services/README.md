# Simplified Service Interfaces

This document provides an overview of the simplified service interfaces for the POC.

## Overview

The simplified service interfaces provide a standardized way to implement services with consistent error handling, configuration management, and common patterns. The goal is to reduce boilerplate code and make it easier to implement new services.

## Key Components

### 1. Error Handling

The error handling system provides a standardized way to handle errors in services:

- **EnhancedServiceError**: An enhanced service error with additional metadata for better error classification, logging, and handling.
- **ErrorCategory**: Categories for classifying service errors (e.g., network, timeout, authentication).
- **ErrorSeverity**: Severity levels for service errors (e.g., debug, info, warning, error, critical).
- **handle_service_errors**: Decorator for handling service errors in a consistent way.
- **is_retryable_error**: Function to determine if an error is retryable.
- **classify_error**: Function to classify an exception into an error category.

### 2. Configuration Management

The configuration management system provides a standardized way to configure services:

- **SimpleServiceConfig**: A simplified configuration model for services with common configuration options.

### 3. Service Interface

The service interface provides a standardized way to implement services:

- **SimpleService**: A simplified base class for services with standardized error handling, configuration management, and common patterns.

## Usage

### Basic Usage

```python
from src.core.services import SimpleService, SimpleServiceConfig
from src.core.services.error_handling import EnhancedServiceError, ErrorCategory, ErrorSeverity

# Define a service configuration
class MyServiceConfig(SimpleServiceConfig):
    api_key: str
    api_url: str = "https://api.example.com"

# Implement a service
class MyService(SimpleService[MyServiceConfig]):
    config_class = MyServiceConfig

    async def _initialize_impl(self) -> None:
        # Implement service initialization
        pass

    async def _shutdown_impl(self) -> None:
        # Implement service shutdown
        pass

    async def my_operation(self, param1: str) -> str:
        # Use execute_with_retry for automatic retry and circuit breaking
        return await self.execute_with_retry(self._my_operation_impl, param1)

    async def _my_operation_impl(self, param1: str) -> str:
        # Implement operation
        if not self._connected:
            raise EnhancedServiceError(
                message="Service is not connected",
                service_name=self.config.service_name,
                category=ErrorCategory.SERVICE_UNAVAILABLE,
                severity=ErrorSeverity.ERROR,
                retry_allowed=True,
            )

        # Perform operation
        return f"Result for {param1}"
```

### Using the Service

```python
import asyncio

async def main():
    # Create a service configuration
    config = MyServiceConfig(
        service_name="my_service",
        api_key="key_12345",
        api_url="https://api.example.com",
    )

    # Create a service instance
    service = MyService(config)

    try:
        # Initialize the service
        await service.initialize()

        # Use the service
        result = await service.my_operation("test")
        print(f"Result: {result}")

    finally:
        # Shutdown the service
        await service.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## Best Practices

1. **Use the SimpleService base class** for all new services.
2. **Define a service-specific configuration class** that inherits from SimpleServiceConfig.
3. **Use the execute_with_retry method** for operations that may fail and should be retried.
4. **Implement the _initialize_impl and _shutdown_impl methods** to handle service-specific initialization and shutdown.
5. **Use EnhancedServiceError** for all service-specific errors, with appropriate categories and severity levels.
6. **Separate public methods from implementation methods** to allow for consistent error handling and retry logic.

## Error Categories

The following error categories are available:

- **NETWORK**: Network-related errors (e.g., connection errors).
- **TIMEOUT**: Timeout errors.
- **RESOURCE_EXHAUSTION**: Resource exhaustion errors (e.g., out of memory).
- **AUTHENTICATION**: Authentication errors.
- **AUTHORIZATION**: Authorization errors.
- **INVALID_INPUT**: Invalid input errors.
- **RESOURCE_NOT_FOUND**: Resource not found errors.
- **RATE_LIMIT**: Rate limit errors.
- **SERVICE_UNAVAILABLE**: Service unavailable errors.
- **INTERNAL_ERROR**: Internal service errors.
- **DATA_VALIDATION**: Data validation errors.
- **DATA_INTEGRITY**: Data integrity errors.
- **UNKNOWN**: Unknown errors.

## Error Severity Levels

The following error severity levels are available:

- **DEBUG**: Debug-level errors.
- **INFO**: Info-level errors.
- **WARNING**: Warning-level errors.
- **ERROR**: Error-level errors.
- **CRITICAL**: Critical-level errors.
