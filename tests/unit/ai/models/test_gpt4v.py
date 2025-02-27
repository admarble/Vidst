"""Tests for GPT-4V model implementation."""

import base64
from unittest.mock import mock_open, patch

import pytest

from video_understanding.ai.exceptions import ModelError
from video_understanding.ai.models.gpt4v import GPT4VisionModel


@pytest.fixture
def model():
    """Create a test model instance."""
    return GPT4VisionModel(api_key="test_key")


@pytest.fixture
def test_image(tmp_path):
    """Create a test image file."""
    image_path = tmp_path / "test_image.jpg"
    image_path.write_bytes(b"test image data")
    return image_path


def test_model_initialization():
    """Test model initialization."""
    model = GPT4VisionModel(api_key="test_key")
    assert model.api_key == "test_key"


@pytest.mark.asyncio
async def test_validate_missing_image_path(model):
    """Test validation with missing image path."""
    input_data = {}
    with pytest.raises(ModelError, match="Missing image_path in input data"):
        model.validate(input_data)


@pytest.mark.asyncio
async def test_validate_nonexistent_image(model):
    """Test validation with nonexistent image."""
    input_data = {"image_path": "nonexistent.jpg"}
    with pytest.raises(ModelError, match="Image file not found"):
        model.validate(input_data)


@pytest.mark.asyncio
async def test_validate_success(model, test_image):
    """Test successful validation."""
    input_data = {"image_path": str(test_image)}
    assert model.validate(input_data) is True


@pytest.mark.asyncio
async def test_process_missing_image_path(model):
    """Test processing with missing image path."""
    input_data = {}
    with pytest.raises(ModelError, match="Missing image_path in input data"):
        await model.process(input_data)


@pytest.mark.asyncio
async def test_process_nonexistent_image(model):
    """Test processing with nonexistent image."""
    input_data = {"image_path": "nonexistent.jpg"}
    with pytest.raises(ModelError, match="Image file not found"):
        await model.process(input_data)


@pytest.mark.asyncio
async def test_process_file_read_error(model, test_image):
    """Test processing with file read error."""
    input_data = {"image_path": str(test_image)}

    # Mock open to raise an error
    mock_open_obj = mock_open()
    mock_open_obj.side_effect = OSError("Failed to read file")

    with patch("builtins.open", mock_open_obj):
        with pytest.raises(ModelError, match="Failed to process image"):
            await model.process(input_data)


@pytest.mark.asyncio
async def test_process_success(model, test_image):
    """Test successful processing."""
    input_data = {"image_path": str(test_image)}
    result = await model.process(input_data)
    assert isinstance(result, dict)
    assert "description" in result
    assert "objects" in result
    assert "text" in result
    assert "actions" in result


@pytest.mark.asyncio
async def test_process_image_encoding(model, test_image):
    """Test image encoding during processing."""
    input_data = {"image_path": str(test_image)}

    # Mock open to return test data
    test_data = b"test image data"
    expected_encoded = base64.b64encode(test_data).decode("utf-8")

    mock_open_obj = mock_open(read_data=test_data)

    with patch("builtins.open", mock_open_obj):
        await model.process(input_data)

        # Verify file was opened in binary mode
        mock_open_obj.assert_called_once_with(test_image, "rb")


def test_process_image(ai_test_image):
    """Test processing an image with GPT-4V."""
    # Test implementation


def test_analyze_frame(ai_test_image):
    """Test analyzing a video frame with GPT-4V."""
    # Test implementation


@pytest.mark.asyncio
async def test_cleanup(model):
    """Test cleanup functionality."""
    # Create a session
    session = await model._ensure_session()
    assert model._session is not None

    # Close and verify cleanup
    await model.close()
    assert model._session is None
