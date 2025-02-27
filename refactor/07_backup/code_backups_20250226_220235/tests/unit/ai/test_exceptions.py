"""Tests for AI model exceptions."""

import pytest
from video_understanding.ai.exceptions import (
    ModelError,
    ValidationError,
    APIError,
    RateLimitError,
    ResourceError,
    TaskError,
    ProcessingError,
    ConfigurationError,
)

def test_model_error_base():
    """Test the base ModelError."""
    error = ModelError("Base model error")
    assert str(error) == "Base model error"
    assert isinstance(error, Exception)

def test_validation_error():
    """Test ValidationError class."""
    error = ValidationError("Invalid model input")
    assert str(error) == "Invalid model input"
    assert isinstance(error, ModelError)
    assert isinstance(error, Exception)

def test_api_error():
    """Test APIError class."""
    error = APIError("API request failed")
    assert str(error) == "API request failed"
    assert isinstance(error, ModelError)
    assert isinstance(error, Exception)

def test_rate_limit_error():
    """Test RateLimitError class."""
    error = RateLimitError("Rate limit exceeded")
    assert str(error) == "Rate limit exceeded"
    assert isinstance(error, APIError)
    assert isinstance(error, ModelError)
    assert isinstance(error, Exception)

def test_resource_error():
    """Test ResourceError class."""
    error = ResourceError("Resource access failed")
    assert str(error) == "Resource access failed"
    assert isinstance(error, ModelError)
    assert isinstance(error, Exception)

def test_task_error():
    """Test TaskError class."""
    error = TaskError("Task processing failed")
    assert str(error) == "Task processing failed"
    assert isinstance(error, ModelError)
    assert isinstance(error, Exception)

def test_processing_error():
    """Test ProcessingError class."""
    error = ProcessingError("Model processing failed")
    assert str(error) == "Model processing failed"
    assert isinstance(error, ModelError)
    assert isinstance(error, Exception)

def test_configuration_error():
    """Test ConfigurationError class."""
    error = ConfigurationError("Invalid configuration")
    assert str(error) == "Invalid configuration"
    assert isinstance(error, ModelError)
    assert isinstance(error, Exception)

def test_error_hierarchy():
    """Test the exception hierarchy relationships."""
    # Test direct inheritance from ModelError
    assert issubclass(ValidationError, ModelError)
    assert issubclass(APIError, ModelError)
    assert issubclass(ResourceError, ModelError)
    assert issubclass(TaskError, ModelError)
    assert issubclass(ProcessingError, ModelError)
    assert issubclass(ConfigurationError, ModelError)

    # Test nested inheritance
    assert issubclass(RateLimitError, APIError)
    assert issubclass(RateLimitError, ModelError)

def test_error_with_cause():
    """Test exceptions with a cause."""
    cause = ValueError("Original error")
    error = ModelError("Model error", cause)
    assert str(error) == "Model error"
    assert error.__cause__ == cause

    # Test with nested exceptions
    try:
        try:
            raise ValueError("Root cause")
        except ValueError as e:
            raise APIError("API error") from e
    except APIError as e:
        assert isinstance(e.__cause__, ValueError)
        assert str(e.__cause__) == "Root cause"
