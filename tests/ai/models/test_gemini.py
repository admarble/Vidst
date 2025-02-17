"""Unit tests for Gemini model implementation."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.ai.models.gemini import GeminiModel
from src.core.exceptions import ModelError


@pytest.fixture
def model():
    return GeminiModel(api_key="test_key")


@pytest.fixture
def mock_image_file(tmp_path):
    """Create a mock image file for testing."""
    image_path = tmp_path / "test.jpg"
    image_path.write_bytes(b"test image content")
    return str(image_path)


def test_model_initialization(model):
    """Test model initialization."""
    assert isinstance(model, GeminiModel)
    assert model.api_key == "test_key"


def test_validate_input_success(model, mock_image_file):
    """Test successful input validation."""
    input_data = {"image_path": mock_image_file}
    assert model.validate(input_data) is True


def test_validate_input_missing_image_path(model):
    """Test validation with missing image path."""
    with pytest.raises(ModelError, match="Missing image_path in input data"):
        model.validate({})


def test_validate_input_nonexistent_image(model, tmp_path):
    """Test validation with non-existent image."""
    nonexistent_path = tmp_path / "nonexistent.jpg"
    with pytest.raises(ModelError, match="Image file not found"):
        model.validate({"image_path": str(nonexistent_path)})


@patch("google.generativeai.GenerativeModel")
def test_process_success(mock_gemini, model, mock_image_file):
    """Test successful processing."""
    # Mock Gemini model response
    mock_model = Mock()
    mock_response = Mock()
    mock_response.text = "Scene description"
    mock_model.generate_content.return_value = mock_response
    mock_gemini.return_value = mock_model

    result = model.process({"image_path": mock_image_file})

    assert isinstance(result, dict)
    assert "description" in result
    assert isinstance(result["objects"], list)
    assert isinstance(result["text"], list)
    assert isinstance(result["actions"], list)


@patch("google.generativeai.GenerativeModel")
def test_process_api_error(mock_gemini, model, mock_image_file):
    """Test handling of API errors."""
    # Mock API error
    mock_model = Mock()
    mock_model.generate_content.side_effect = Exception("API Error")
    mock_gemini.return_value = mock_model

    with pytest.raises(ModelError) as exc_info:
        model.process({"image_path": mock_image_file})
    assert "Failed to process image" in str(exc_info.value)


def test_process_invalid_input(model):
    """Test processing with invalid input."""
    with pytest.raises(ModelError, match="Missing image_path in input data"):
        model.process({"invalid": "data"})


@patch("google.generativeai.configure")
def test_api_configuration(mock_configure):
    """Test API configuration during initialization."""
    api_key = "test-gemini-key-123456789"
    model = GeminiModel(api_key=api_key)
    mock_configure.assert_called_once_with(api_key=api_key)
    assert model.api_key == api_key
