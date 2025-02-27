"""Unit tests for GPT-4V model."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp
from typing import Dict, Any

from src.video_understanding.ai.models.gpt4v import GPT4VModel, GPT4VConfig
from src.video_understanding.ai.exceptions import ValidationError, APIError, ConfigurationError

@pytest.fixture
def model_config() -> Dict[str, Any]:
    """Test model configuration."""
    return {
        "api_key": "test-key",
        "api_base": "https://test.api/v1",
        "model": "gpt-4-vision-test",
        "max_tokens": 100,
        "temperature": 0.5
    }

@pytest.fixture
def valid_input() -> Dict[str, str]:
    """Valid model input data."""
    return {
        "image_url": "https://example.com/image.jpg",
        "prompt": "Describe this image"
    }

@pytest.fixture
def mock_response() -> Dict[str, Any]:
    """Mock API response."""
    return {
        "choices": [{
            "message": {
                "content": "A test description"
            }
        }],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 20
        }
    }

def test_config_initialization(model_config: Dict[str, Any]) -> None:
    """Test GPT4VConfig initialization."""
    config = GPT4VConfig(**model_config)
    assert config.api_key == model_config["api_key"]
    assert config.api_base == model_config["api_base"]
    assert config.model == model_config["model"]
    assert config.max_tokens == model_config["max_tokens"]
    assert config.temperature == model_config["temperature"]

def test_model_initialization_without_api_key() -> None:
    """Test model initialization without API key."""
    with pytest.raises(ConfigurationError, match="API key required"):
        GPT4VModel({})

def test_model_initialization_with_config(model_config: Dict[str, Any]) -> None:
    """Test model initialization with valid config."""
    model = GPT4VModel(model_config)
    assert isinstance(model.config, GPT4VConfig)
    assert model.config.api_key == model_config["api_key"]

def test_validate_invalid_input() -> None:
    """Test input validation with invalid data."""
    model = GPT4VModel({"api_key": "test"})

    with pytest.raises(ValidationError, match="Input must be dictionary"):
        model.validate("not a dict")

    with pytest.raises(ValidationError, match="image_url required"):
        model.validate({"prompt": "test"})

    with pytest.raises(ValidationError, match="prompt required"):
        model.validate({"image_url": "test"})

    with pytest.raises(ValidationError, match="prompt must be string"):
        model.validate({"image_url": "test", "prompt": 123})

def test_validate_valid_input(valid_input: Dict[str, str]) -> None:
    """Test input validation with valid data."""
    model = GPT4VModel({"api_key": "test"})
    assert model.validate(valid_input) is True

@pytest.mark.asyncio
async def test_process_success(
    model_config: Dict[str, Any],
    valid_input: Dict[str, str],
    mock_response: Dict[str, Any]
) -> None:
    """Test successful processing."""
    model = GPT4VModel(model_config)

    mock_session = AsyncMock()
    mock_response_obj = AsyncMock()
    mock_response_obj.status = 200
    mock_response_obj.json = AsyncMock(return_value=mock_response)
    mock_session.post = AsyncMock(return_value=mock_response_obj)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        result = await model.process(valid_input)

    assert result["analysis"] == "A test description"
    assert result["model"] == model_config["model"]
    assert "usage" in result

@pytest.mark.asyncio
async def test_process_api_error(
    model_config: Dict[str, Any],
    valid_input: Dict[str, str]
) -> None:
    """Test API error handling."""
    model = GPT4VModel(model_config)

    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_session.post = AsyncMock(return_value=mock_response)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        with pytest.raises(APIError, match="API request failed: 400"):
            await model.process(valid_input)

@pytest.mark.asyncio
async def test_process_network_error(
    model_config: Dict[str, Any],
    valid_input: Dict[str, str]
) -> None:
    """Test network error handling."""
    model = GPT4VModel(model_config)

    mock_session = AsyncMock()
    mock_session.post = AsyncMock(side_effect=aiohttp.ClientError())

    with patch("aiohttp.ClientSession", return_value=mock_session):
        with pytest.raises(APIError, match="API request failed"):
            await model.process(valid_input)

@pytest.mark.asyncio
async def test_close(model_config: Dict[str, Any]) -> None:
    """Test resource cleanup."""
    model = GPT4VModel(model_config)
    mock_session = AsyncMock()
    model.session = mock_session

    await model.close()
    mock_session.close.assert_called_once()
    assert model.session is None
