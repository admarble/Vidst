"""Test Gemini model functionality."""

import base64
from unittest.mock import mock_open, patch

import pytest
from aiohttp import ClientSession

from video_understanding.ai.exceptions import ModelError
from video_understanding.ai.models.gemini import GeminiModel


@pytest.fixture
async def model() -> GeminiModel:
    """Create a test model instance."""
    return GeminiModel(api_key="test_key")


@pytest.fixture
def test_image(tmp_path):
    """Create a test image file."""
    image_path = tmp_path / "test_image.jpg"
    image_path.write_bytes(b"test image data")
    return image_path


async def test_initialization(model: GeminiModel) -> None:
    """Test model initialization."""
    assert model._api_key == "test_key"
    assert model._session is None


async def test_session_management(model: GeminiModel) -> None:
    """Test session management."""
    session = await model._ensure_session()
    assert isinstance(session, ClientSession)
    assert model._session is session

    # Test session reuse
    session2 = await model._ensure_session()
    assert session2 is session


async def test_image_encoding(model: GeminiModel) -> None:
    """Test image encoding functionality."""
    # Mock open to return test data
    test_data = b"test image data"
    encoded_data = base64.b64encode(test_data).decode("utf-8")

    mock_open_obj = mock_open(read_data=test_data)
    with patch("builtins.open", mock_open_obj):
        result = await model._encode_image("test.jpg")
        assert result == encoded_data


async def test_cleanup(model: GeminiModel) -> None:
    """Test cleanup functionality."""
    # Create a session and verify it's active
    session = await model._ensure_session()
    assert not session.closed

    # Clean up and verify session is closed
    await model.cleanup()
    assert session.closed
    assert model._session is None


async def test_error_handling(model: GeminiModel) -> None:
    """Test error handling."""
    with pytest.raises(ValueError):
        await model._ensure_session()  # Should fail with empty API key

    with pytest.raises(FileNotFoundError):
        await model._encode_image("nonexistent.jpg")


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
    """Test processing an image with Gemini."""
    # Test implementation


def test_analyze_frame(ai_test_image):
    """Test analyzing a video frame with Gemini."""
    # Test implementation
