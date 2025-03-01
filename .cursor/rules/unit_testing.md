# Vidst Refactoring - Unit Testing

## When to apply
@semantics Applies when writing unit tests for components, focusing on testing individual units in isolation.
@files tests/unit/**/*.py tests/**/test_*.py
@userMessages ".*unit test.*" ".*test component.*" ".*write test for.*" ".*create test.*" ".*component test.*"

## Unit Testing Guidelines

This rule provides patterns for implementing unit tests for Vidst components, focusing on isolated testing of classes and functions.

## Basic Test Structure

```python
import pytest
from unittest.mock import MagicMock, patch
from video_understanding.component import Component

class TestComponent:
    """Tests for Component class."""
    
    @pytest.fixture
    def component(self):
        """Create a component for testing."""
        config = {"param1": "value1", "param2": 42}
        return Component(config)
    
    def test_initialization(self, component):
        """Test component initialization."""
        assert component.config["param1"] == "value1"
        assert component.config["param2"] == 42
    
    def test_method_success(self, component):
        """Test method success case."""
        # Arrange
        input_data = {"key": "value"}
        expected = {"result": "success"}
        
        # Act
        result = component.method(input_data)
        
        # Assert
        assert result == expected
```

## Test Naming Conventions

Follow these naming conventions:

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<method_name>_<scenario>`

Examples:
- `test_initialization`
- `test_process_valid_input`
- `test_detect_scenes_empty_video`

## Fixture Pattern

Use fixtures for test setup:

```python
@pytest.fixture
def mock_service():
    """Create a mock service."""
    service = MagicMock()
    service.process.return_value = {"status": "success"}
    return service

@pytest.fixture
def component(mock_service):
    """Create a component with mock dependencies."""
    return Component(service=mock_service)
```

## Mocking Dependencies

Mock external dependencies:

```python
@patch("video_understanding.component.service.ServiceClient")
def test_process_calls_service(mock_service_client, component):
    """Test process method calls service client."""
    # Arrange
    mock_instance = mock_service_client.return_value
    mock_instance.call.return_value = {"result": "data"}
    
    # Act
    result = component.process({"input": "data"})
    
    # Assert
    mock_instance.call.assert_called_once_with({"input": "data"})
    assert result == {"result": "data"}
```

## Testing Exceptions

Test error handling:

```python
def test_process_handles_error(component):
    """Test process method handles errors."""
    # Arrange
    component.service.process.side_effect = ValueError("Test error")
    
    # Act & Assert
    with pytest.raises(ComponentError) as exc_info:
        component.process({"input": "data"})
    
    assert "Test error" in str(exc_info.value)
```

## Example: Testing Base Component

```python
import pytest
from video_understanding.component.base import BaseComponent
from video_understanding.component.concrete import ConcreteComponent

class TestConcreteComponent:
    """Tests for ConcreteComponent class."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "param1": "test",
            "param2": 42
        }
    
    @pytest.fixture
    def component(self, config):
        """Create a component instance."""
        return ConcreteComponent(config)
    
    def test_initialization(self, component, config):
        """Test component initialization."""
        assert component.config["param1"] == config["param1"]
        assert component.config["param2"] == config["param2"]
        assert isinstance(component, BaseComponent)
    
    def test_process_success(self, component):
        """Test process method success case."""
        # Arrange
        input_data = {"key": "value"}
        
        # Act
        result = component.process(input_data)
        
        # Assert
        assert result["status"] == "success"
        assert "results" in result
```

## Example: Testing API Client

```python
import pytest
from unittest.mock import patch, MagicMock
from video_understanding.utils.api import APIClient, APIError

class TestAPIClient:
    """Tests for APIClient class."""
    
    @pytest.fixture
    def config(self):
        """Create API configuration."""
        return {
            "api_key": "test_key",
            "api_url": "https://api.example.com",
            "timeout": 10.0,
            "retries": 2
        }
    
    @pytest.fixture
    def client(self, config):
        """Create an API client."""
        return APIClient(config)
    
    @patch("aiohttp.ClientSession.request")
    async def test_call_api_success(self, mock_request, client):
        """Test successful API call."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json.return_value = {"result": "success"}
        mock_request.return_value.__aenter__.return_value = mock_response
        
        # Act
        result = await client.call_api("endpoint")
        
        # Assert
        assert result == {"result": "success"}
        mock_request.assert_called_once()
```

## Table-Driven Tests

Use table-driven tests for multiple scenarios:

```python
import pytest
from video_understanding.utils.validation import validate_input

@pytest.mark.parametrize("input_data,expected_result", [
    ({"name": "Test", "age": 30}, True),
    ({"name": "Test"}, False),
    ({"age": 30}, False),
    ({}, False),
])
def test_validate_input(input_data, expected_result):
    """Test input validation with multiple scenarios."""
    result = validate_input(input_data)
    assert result == expected_result
```

## Testing Asynchronous Code

Use pytest-asyncio for async tests:

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test an asynchronous function."""
    # Arrange
    expected = "result"
    
    # Act
    result = await async_function()
    
    # Assert
    assert result == expected
```

## Marking Tests

Use pytest marks for categorization:

```python
@pytest.mark.slow
def test_slow_operation():
    """Test that takes a long time to run."""
    # Test implementation
    
@pytest.mark.integration
def test_with_database():
    """Test that requires database integration."""
    # Test implementation
```

## Test Coverage Guidelines

Aim for high test coverage:

1. ✓ Test all public methods and functions
2. ✓ Test edge cases and error handling
3. ✓ Test initialization and configuration
4. ✓ Use parameterized tests for multiple scenarios
5. ✓ Mock external dependencies

## Unit Test Checklist

When writing unit tests:

1. ✓ Follow naming conventions
2. ✓ Create appropriate fixtures
3. ✓ Mock external dependencies
4. ✓ Test success cases
5. ✓ Test error cases
6. ✓ Use assertions effectively
7. ✓ Document test purpose with docstrings
