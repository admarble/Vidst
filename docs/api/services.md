# Service Interfaces Documentation

## Overview

The service interfaces provide a standardized way to interact with external APIs and services in the Vidst project. They ensure consistent configuration, error handling, and lifecycle management across all service implementations.

## Key Components

### Base Service Interface

The `BaseService` class provides a standardized interface for all services:

- **Lifecycle Methods**: `initialize()` and `shutdown()` for consistent resource management
- **Health Checking**: `ping()` method for service availability checks
- **Configuration Validation**: Built-in validation with Pydantic and custom validation hooks

### Configuration Management

The `ServiceConfig` class provides a standardized way to configure services using Pydantic models:

- **Common Configuration**: Timeout, retry settings, and service identification
- **Type Safety**: Configuration types are validated at runtime
- **Extensibility**: Service-specific configurations inherit from the base class

### Error Handling

The exception hierarchy provides a standardized way to handle errors:

- **ServiceError**: Base class for all service-related errors
- **Specialized Errors**: ConfigurationError, ConnectionError, AuthenticationError, etc.
- **Context Information**: Errors include service name, status code, and additional details

### Service Factory

The `ServiceFactory` class provides a way to create service instances dynamically:

- **Service Registration**: Register service implementations by type
- **Dynamic Creation**: Create service instances based on configuration
- **Type Safety**: Generic typing ensures correct configuration types

### Retry Utilities

The `retry_async` function provides a way to retry operations that may fail due to transient errors:

- **Exponential Backoff**: Increasing delay between retries
- **Jitter**: Random variation in retry delays to prevent thundering herd
- **Configurable**: Customizable retry count, delay, and exceptions to retry

## Usage Examples

### Direct Service Usage

```python
# Create service configuration
config = ExampleServiceConfig(
    service_name="example_service",
    api_key="key_12345",
    base_url="https://api.example.com",
    max_results=5,
)

# Create service instance
service = ExampleService(config)

# Initialize service
await service.initialize()

# Use service
result = await service.get_data("test query")

# Shut down service
await service.shutdown()
```

### Factory-based Service Usage

```python
# Create service factory
factory = ServiceFactory[ServiceConfig, BaseService]()

# Register service implementations
factory.register("example", ExampleService)

# Create service configuration
config = ExampleServiceConfig(
    service_name="example_service",
    api_key="key_12345",
)

# Create service instance
service = factory.create("example", config)

# Initialize service
await service.initialize()

# Use service
if isinstance(service, ExampleService):
    result = await service.get_data("test query")

# Shut down service
await service.shutdown()
```

### Using Retry Utilities

```python
# Retry a function with default settings
result = await retry_async(
    service.operation,
    arg1, arg2,
)

# Retry with custom settings
result = await retry_async(
    service.operation,
    arg1, arg2,
    retry_count=5,
    initial_delay=0.5,
    max_delay=30.0,
    backoff_factor=1.5,
    jitter=True,
    exceptions_to_retry=[ConnectionError, TimeoutError],
)
```

## Error Handling Patterns

### Basic Error Handling

```python
try:
    result = await service.operation()
except ServiceError as e:
    print(f"Service error: {e}")
    # Handle the error
```

### Specific Error Handling

```python
try:
    result = await service.operation()
except ConnectionError as e:
    print(f"Connection error: {e}")
    # Handle connection issues
except TimeoutError as e:
    print(f"Timeout error: {e}")
    # Handle timeout issues
except AuthenticationError as e:
    print(f"Authentication error: {e}")
    # Handle authentication issues
except ServiceError as e:
    print(f"Other service error: {e}")
    # Handle other service errors
```

### Error Context Information

```python
try:
    result = await service.operation()
except ServiceError as e:
    print(f"Error message: {e.message}")
    print(f"Service name: {e.service_name}")
    print(f"Status code: {e.status_code}")
    print(f"Error details: {e.details}")
    # Handle the error based on context
```

## Configuration Examples

### Basic Configuration

```python
from video_understanding.services.config import ServiceConfig

# Basic configuration
config = ServiceConfig(
    service_name="example_service",
    timeout=30.0,
    max_retries=3,
    retry_delay=1.0,
)
```

### Service-Specific Configuration

```python
from pydantic import Field
from video_understanding.services.config import ServiceConfig

class ExampleServiceConfig(ServiceConfig):
    """Example service configuration."""

    api_key: str = Field(..., description="API key for authentication")
    base_url: str = Field(
        "https://api.example.com", description="Base URL for API requests"
    )
    max_results: int = Field(10, description="Maximum number of results to return")
```

### Configuration Validation

```python
from video_understanding.services.base import BaseService

class ExampleService(BaseService[ExampleServiceConfig]):
    """Example service implementation."""

    config_class = ExampleServiceConfig

    def validate_config(self) -> None:
        """Validate service configuration."""
        super().validate_config()

        # Custom validation
        if not self.config.api_key.startswith("key_"):
            raise ValueError("API key must start with 'key_'")
```

## Implementing a New Service

To implement a new service:

1. Create a service-specific configuration class that inherits from `ServiceConfig`
2. Create a service class that inherits from `BaseService`
3. Implement the required methods: `initialize()`, `shutdown()`, and service-specific methods
4. Use the retry utilities for operations that may fail due to transient errors
5. Use the standardized error hierarchy for error handling

### Example Implementation

```python
from pydantic import Field
from typing import Dict, Any

from video_understanding.services.base import BaseService
from video_understanding.services.config import ServiceConfig
from video_understanding.services.exceptions import ServiceError
from video_understanding.utils.retry import retry_async

class MyServiceConfig(ServiceConfig):
    """My service configuration."""

    api_key: str = Field(..., description="API key for authentication")
    base_url: str = Field(
        "https://api.myservice.com", description="Base URL for API requests"
    )

class MyService(BaseService[MyServiceConfig]):
    """My service implementation."""

    config_class = MyServiceConfig

    def __init__(self, config: MyServiceConfig):
        super().__init__(config)
        self.client = None

    async def initialize(self) -> None:
        """Initialize the service."""
        # Initialize resources
        self.client = {"initialized": True}

    async def shutdown(self) -> None:
        """Shut down the service."""
        # Clean up resources
        self.client = None

    async def get_data(self, query: str) -> Dict[str, Any]:
        """Get data from the service."""
        try:
            return await retry_async(
                self._get_data_internal,
                query,
                retry_count=self.config.max_retries,
                initial_delay=self.config.retry_delay,
            )
        except Exception as e:
            raise ServiceError(
                f"Failed to get data: {str(e)}",
                service_name=self.config.service_name,
            ) from e

    async def _get_data_internal(self, query: str) -> Dict[str, Any]:
        """Internal method for getting data."""
        # Make API request
        return {"query": query, "results": []}
```

## Best Practices

1. **Use the Factory Pattern**: Use the `ServiceFactory` to create service instances for better testability and flexibility.
2. **Proper Resource Management**: Always call `initialize()` before using a service and `shutdown()` when done.
3. **Error Handling**: Use the standardized error hierarchy for consistent error handling.
4. **Retry Transient Errors**: Use the retry utilities for operations that may fail due to transient errors.
5. **Configuration Validation**: Validate service configuration to catch issues early.
6. **Type Safety**: Use type annotations for better IDE support and error detection.
7. **Documentation**: Document service interfaces and implementations for better maintainability.
