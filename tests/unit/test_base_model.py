"""Unit tests for base AI model."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from video_understanding.ai.exceptions import ModelError
from video_understanding.ai.models.base import BaseModel


class TestModel(BaseModel):
    """Test implementation of BaseModel."""

    cleanup_called = False

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process input data."""
        return {"result": "processed"}

    def validate(self, input_data: dict[str, Any]) -> bool:
        """Validate input data."""
        return True

    def _cleanup_resources(self) -> None:
        """Clean up resources."""
        self.cleanup_called = True

    async def close(self) -> None:
        """Clean up model resources."""
        self._cleanup_resources()


@pytest.fixture
def test_model():  # pylint: disable=redefined-outer-name
    """Fixture to create a fresh TestModel instance."""
    model = TestModel()
    model.cleanup_called = False
    return model


def test_validate_input(test_model):  # pylint: disable=redefined-outer-name
    """Test input validation."""
    # Test None input
    with pytest.raises(ValueError, match="Input cannot be None or empty"):
        test_model.validate_input(None)

    # Test empty string
    with pytest.raises(ValueError, match="Input cannot be None or empty"):
        test_model.validate_input("")

    # Test valid input
    test_model.validate_input("valid input")
    test_model.validate_input(123)
    test_model.validate_input({"key": "value"})


def test_retry_with_backoff_success(test_model):  # pylint: disable=redefined-outer-name
    """Test successful retry with backoff."""
    mock_func = MagicMock(return_value="success")

    result = test_model.retry_with_backoff(mock_func)
    assert result == "success"
    assert mock_func.call_count == 1


def test_retry_with_backoff_retry_success(
    test_model,
):  # pylint: disable=redefined-outer-name
    """Test retry succeeds after failures."""
    mock_func = MagicMock(
        side_effect=[ValueError("fail"), ValueError("fail"), "success"]
    )

    with patch("time.sleep") as mock_sleep:
        result = test_model.retry_with_backoff(mock_func)
        assert result == "success"
        assert mock_func.call_count == 3
        assert mock_sleep.call_count == 2


def test_retry_with_backoff_max_retries(
    test_model,
):  # pylint: disable=redefined-outer-name
    """Test max retries exceeded."""
    mock_func = MagicMock(side_effect=ValueError("fail"))

    with (
        patch("time.sleep"),
        pytest.raises(ModelError, match="Failed after 3 attempts"),
    ):
        test_model.retry_with_backoff(mock_func)
        assert mock_func.call_count == 3


def test_retry_with_backoff_custom_params(
    test_model,
):  # pylint: disable=redefined-outer-name
    """Test retry with custom parameters."""
    mock_func = MagicMock(side_effect=[ValueError("fail"), "success"])

    with patch("time.sleep") as mock_sleep:
        result = test_model.retry_with_backoff(
            mock_func, max_retries=5, initial_delay=0.5
        )
        assert result == "success"
        assert mock_func.call_count == 2
        mock_sleep.assert_called_once_with(0.5)


def test_process_with_cleanup_success(
    test_model,
):  # pylint: disable=redefined-outer-name
    """Test successful processing with cleanup."""
    mock_func = MagicMock(return_value="success")

    result = test_model.process_with_cleanup(mock_func)
    assert result == "success"
    assert test_model.cleanup_called
    assert mock_func.call_count == 1


def test_process_with_cleanup_error(test_model):  # pylint: disable=redefined-outer-name
    """Test cleanup on error."""
    mock_func = MagicMock(side_effect=ValueError("error"))

    with pytest.raises(ValueError, match="error"):
        test_model.process_with_cleanup(mock_func)
    assert test_model.cleanup_called
    assert mock_func.call_count == 1


def test_abstract_methods():
    """Test abstract method enforcement."""
    # Test that BaseModel is properly marked as abstract
    assert hasattr(BaseModel, "__abstractmethods__")
    abstract_methods = BaseModel.__abstractmethods__
    assert "process" in abstract_methods
    assert "validate" in abstract_methods

    # Test concrete implementation works
    model = TestModel()
    assert model.process({"test": "data"}) == {"result": "processed"}
    assert model.validate({"test": "data"}) is True
