"""Unit tests for base AI model."""

import time
from unittest.mock import MagicMock, patch

import pytest

from src.ai.models.base import BaseModel
from src.core.exceptions import ModelError


class TestModel(BaseModel):
    """Test implementation of BaseModel."""

    def __init__(self):
        self.cleanup_called = False

    def process(self, input_data):
        return {"result": "processed"}

    def validate(self, input_data):
        return True

    def _cleanup_resources(self):
        self.cleanup_called = True


def test_validate_input():
    """Test input validation."""
    model = TestModel()

    # Test None input
    with pytest.raises(ValueError, match="Input cannot be None or empty"):
        model.validate_input(None)

    # Test empty string
    with pytest.raises(ValueError, match="Input cannot be None or empty"):
        model.validate_input("")

    # Test valid input
    model.validate_input("valid input")
    model.validate_input(123)
    model.validate_input({"key": "value"})


def test_retry_with_backoff_success():
    """Test successful retry with backoff."""
    model = TestModel()
    mock_func = MagicMock(return_value="success")

    result = model.retry_with_backoff(mock_func)
    assert result == "success"
    assert mock_func.call_count == 1


def test_retry_with_backoff_retry_success():
    """Test retry succeeds after failures."""
    model = TestModel()
    mock_func = MagicMock(
        side_effect=[ValueError("fail"), ValueError("fail"), "success"]
    )

    with patch("time.sleep") as mock_sleep:
        result = model.retry_with_backoff(mock_func)
        assert result == "success"
        assert mock_func.call_count == 3
        assert mock_sleep.call_count == 2


def test_retry_with_backoff_max_retries():
    """Test max retries exceeded."""
    model = TestModel()
    mock_func = MagicMock(side_effect=ValueError("fail"))

    with (
        patch("time.sleep"),
        pytest.raises(ModelError, match="Failed after 3 attempts"),
    ):
        model.retry_with_backoff(mock_func)
        assert mock_func.call_count == 3


def test_retry_with_backoff_custom_params():
    """Test retry with custom parameters."""
    model = TestModel()
    mock_func = MagicMock(side_effect=[ValueError("fail"), "success"])

    with patch("time.sleep") as mock_sleep:
        result = model.retry_with_backoff(mock_func, max_retries=5, initial_delay=0.5)
        assert result == "success"
        assert mock_func.call_count == 2
        mock_sleep.assert_called_once_with(0.5)


def test_process_with_cleanup_success():
    """Test successful processing with cleanup."""
    model = TestModel()
    mock_func = MagicMock(return_value="success")

    result = model.process_with_cleanup(mock_func)
    assert result == "success"
    assert model.cleanup_called
    assert mock_func.call_count == 1


def test_process_with_cleanup_error():
    """Test cleanup on error."""
    model = TestModel()
    mock_func = MagicMock(side_effect=ValueError("error"))

    with pytest.raises(ValueError, match="error"):
        model.process_with_cleanup(mock_func)
    assert model.cleanup_called
    assert mock_func.call_count == 1


def test_abstract_methods():
    """Test abstract method enforcement."""
    # Attempt to instantiate abstract class
    with pytest.raises(TypeError):
        BaseModel()

    # Test concrete implementation
    model = TestModel()
    assert model.process({"test": "data"}) == {"result": "processed"}
    assert model.validate({"test": "data"}) is True
