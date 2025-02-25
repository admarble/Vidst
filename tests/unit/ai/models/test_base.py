"""Tests for base model functionality."""

from typing import Any
from unittest.mock import MagicMock

import pytest
from aiohttp import ClientSession

from video_understanding.ai.models.base import BaseModel
from video_understanding.core.exceptions import ModelError


class TestModel(BaseModel):
    """Test implementation of BaseModel."""

    def __init__(self):
        """Initialize test model."""
        self._session: ClientSession | None = None
        self._cleanup_called = False

    def validate(self, input_data: dict[str, Any]) -> bool:
        """Test implementation of validate."""
        if not isinstance(input_data, dict):
            raise ModelError("Input must be a dictionary")
        if "test" not in input_data:
            raise ModelError("Missing 'test' key in input")
        return True

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Test implementation of process."""
        self.validate(input_data)
        return {"result": "processed"}

    async def close(self) -> None:
        """Test implementation of close."""
        self._cleanup_called = True
        if self._session is not None:
            await self._session.close()
            self._session = None


@pytest.mark.asyncio
async def test_base_model_initialization():
    """Test base model initialization."""
    model = TestModel()
    assert isinstance(model, BaseModel)


@pytest.mark.asyncio
async def test_validate_input_success():
    """Test successful input validation."""
    model = TestModel()
    input_data = {"test": "data"}
    assert await model.process(input_data) == {"result": "processed"}


@pytest.mark.asyncio
async def test_validate_input_failure():
    """Test input validation failure."""
    model = TestModel()
    with pytest.raises(ModelError):
        await model.process({"invalid": "data"})


@pytest.mark.asyncio
async def test_process_success():
    """Test successful processing."""
    model = TestModel()
    result = await model.process({"test": "data"})
    assert result == {"result": "processed"}


@pytest.mark.asyncio
async def test_process_validation_failure():
    """Test processing with invalid input."""
    model = TestModel()
    with pytest.raises(ModelError):
        await model.process({"invalid": "data"})


@pytest.mark.asyncio
async def test_retry_with_backoff_success():
    """Test successful retry with backoff."""
    model = TestModel()
    mock_func = MagicMock(return_value={"success": True})
    result = model.retry_with_backoff(mock_func)
    assert result == {"success": True}
    assert mock_func.call_count == 1


@pytest.mark.asyncio
async def test_retry_with_backoff_failure():
    """Test retry with backoff failure."""
    model = TestModel()
    mock_func = MagicMock(side_effect=Exception("Test error"))
    with pytest.raises(ModelError):
        model.retry_with_backoff(mock_func)
    assert mock_func.call_count == 3  # Default max retries


@pytest.mark.asyncio
async def test_process_with_cleanup():
    """Test process with cleanup."""
    model = TestModel()
    mock_func = MagicMock(return_value={"success": True})
    result = model.process_with_cleanup(mock_func)
    assert result == {"success": True}
    assert mock_func.call_count == 1


@pytest.mark.asyncio
async def test_process_with_cleanup_error():
    """Test process with cleanup when error occurs."""
    model = TestModel()
    mock_func = MagicMock(side_effect=Exception("Test error"))
    with pytest.raises(Exception):
        model.process_with_cleanup(mock_func)
    assert mock_func.call_count == 1


@pytest.mark.asyncio
async def test_validate_input_none():
    """Test validate_input with None."""
    model = TestModel()
    with pytest.raises(ValueError, match="Input cannot be None or empty"):
        model.validate_input(None)


@pytest.mark.asyncio
async def test_validate_input_empty_string():
    """Test validate_input with empty string."""
    model = TestModel()
    with pytest.raises(ValueError, match="Input must be a dictionary"):
        model.validate_input("")


@pytest.mark.asyncio
async def test_validate_input_valid():
    """Test validate_input with valid input."""
    model = TestModel()
    input_data = {"test": "data"}
    model.validate_input(input_data)  # Should not raise


@pytest.mark.asyncio
async def test_cleanup():
    """Test cleanup functionality."""
    model = TestModel()
    await model.close()
    # pylint: disable=protected-access
    assert model._cleanup_called is True
