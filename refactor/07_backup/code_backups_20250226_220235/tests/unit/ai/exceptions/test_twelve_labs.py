"""Tests for Twelve Labs exceptions."""

import pytest
from video_understanding.ai.exceptions.twelve_labs import (
    TwelveLabsError,
    RateLimitError,
    TaskError,
    ValidationError,
    APIError,
    ResourceError,
)
from video_understanding.core.exceptions import ModelError

def test_twelve_labs_error_base():
    """Test the base TwelveLabsError."""
    error = TwelveLabsError("Base Twelve Labs error")
    assert str(error) == "Base Twelve Labs error"
    assert isinstance(error, ModelError)

def test_rate_limit_error():
    """Test RateLimitError class."""
    error = RateLimitError("Rate limit exceeded")
    assert str(error) == "Rate limit exceeded"
    assert isinstance(error, TwelveLabsError)
    assert isinstance(error, ModelError)

def test_task_error():
    """Test TaskError class."""
    error = TaskError("Task processing failed")
    assert str(error) == "Task processing failed"
    assert isinstance(error, TwelveLabsError)
    assert isinstance(error, ModelError)

def test_validation_error():
    """Test ValidationError class."""
    error = ValidationError("Invalid input")
    assert str(error) == "Invalid input"
    assert isinstance(error, TwelveLabsError)
    assert isinstance(error, ModelError)

def test_api_error():
    """Test APIError class."""
    error = APIError("API request failed")
    assert str(error) == "API request failed"
    assert isinstance(error, TwelveLabsError)
    assert isinstance(error, ModelError)

def test_resource_error():
    """Test ResourceError class."""
    error = ResourceError("Resource access failed")
    assert str(error) == "Resource access failed"
    assert isinstance(error, TwelveLabsError)
    assert isinstance(error, ModelError)

def test_error_hierarchy():
    """Test the exception hierarchy relationships."""
    # Test inheritance from TwelveLabsError
    assert issubclass(RateLimitError, TwelveLabsError)
    assert issubclass(TaskError, TwelveLabsError)
    assert issubclass(ValidationError, TwelveLabsError)
    assert issubclass(APIError, TwelveLabsError)
    assert issubclass(ResourceError, TwelveLabsError)

    # Test inheritance from ModelError
    assert issubclass(TwelveLabsError, ModelError)
    assert issubclass(RateLimitError, ModelError)
    assert issubclass(TaskError, ModelError)
    assert issubclass(ValidationError, ModelError)
    assert issubclass(APIError, ModelError)
    assert issubclass(ResourceError, ModelError)

def test_error_with_cause():
    """Test exceptions with a cause."""
    cause = ValueError("Original error")
    error = TwelveLabsError("Twelve Labs error", cause)
    assert str(error) == "Twelve Labs error"
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
        assert isinstance(e, TwelveLabsError)

def test_error_with_details():
    """Test exceptions with additional details."""
    details = {
        "status_code": 429,
        "retry_after": 60,
        "request_id": "12345"
    }
    error = RateLimitError("Rate limit exceeded", details=details)
    assert str(error) == "Rate limit exceeded"
    assert hasattr(error, "details")
    assert error.details == details
