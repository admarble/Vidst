import time
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from src.ai.models.base import BaseModel
from src.core.exceptions import ModelError


class TestModel(BaseModel):
    """Concrete implementation of BaseModel for testing."""

    def __init__(self):
        self.cleanup_called = False

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"processed": input_data}

    def validate(self, input_data: Dict[str, Any]) -> bool:
        return bool(input_data)

    def _cleanup_resources(self) -> None:
        self.cleanup_called = True


@pytest.fixture
def model():
    return TestModel()


def test_validate_input_valid(model):
    # Test valid inputs
    model.validate_input("valid input")
    model.validate_input(123)
    model.validate_input({"key": "value"})
    model.validate_input([1, 2, 3])


def test_validate_input_invalid(model):
    # Test None input
    with pytest.raises(ValueError, match="Input cannot be None or empty"):
        model.validate_input(None)

    # Test empty string
    with pytest.raises(ValueError, match="Input cannot be None or empty"):
        model.validate_input("")


def test_retry_with_backoff_success(model):
    mock_func = Mock(return_value="success")
    result = model.retry_with_backoff(mock_func)

    assert result == "success"
    assert mock_func.call_count == 1


def test_retry_with_backoff_eventual_success(model):
    # Function that fails twice then succeeds
    mock_func = Mock(side_effect=[ValueError("fail"), ValueError("fail"), "success"])

    result = model.retry_with_backoff(mock_func, max_retries=3, initial_delay=0.1)

    assert result == "success"
    assert mock_func.call_count == 3


def test_retry_with_backoff_failure(model):
    # Function that always fails
    mock_func = Mock(side_effect=ValueError("persistent failure"))

    with pytest.raises(ModelError, match="Failed after 3 attempts"):
        model.retry_with_backoff(mock_func, max_retries=3, initial_delay=0.1)

    assert mock_func.call_count == 3


@patch("time.sleep")
def test_retry_with_backoff_delay(mock_sleep, model):
    # Function that fails max_retries times
    mock_func = Mock(side_effect=ValueError("fail"))
    initial_delay = 0.1

    with pytest.raises(ModelError):
        model.retry_with_backoff(mock_func, max_retries=3, initial_delay=initial_delay)

    # Check that sleep was called with exponential backoff
    assert mock_sleep.call_count == 2  # Called twice (not called on last retry)
    mock_sleep.assert_has_calls(
        [
            call(initial_delay),  # First retry
            call(initial_delay * 2),  # Second retry
        ]
    )


def test_process_with_cleanup_success(model):
    mock_func = Mock(return_value="success")

    result = model.process_with_cleanup(mock_func)

    assert result == "success"
    assert model.cleanup_called  # Verify cleanup was called
    assert mock_func.call_count == 1


def test_process_with_cleanup_failure(model):
    mock_func = Mock(side_effect=ValueError("failure"))

    with pytest.raises(ValueError):
        model.process_with_cleanup(mock_func)

    assert model.cleanup_called  # Verify cleanup was called even on failure
    assert mock_func.call_count == 1


def test_abstract_methods():
    # Verify that BaseModel cannot be instantiated without implementing abstract methods
    with pytest.raises(TypeError):
        BaseModel()


def test_process_implementation(model):
    input_data = {"test": "data"}
    result = model.process(input_data)
    assert result == {"processed": input_data}


def test_validate_implementation(model):
    assert model.validate({"test": "data"}) is True
    assert model.validate({}) is False
