"""Unit tests for the OpenAI model."""

import pytest
import io
import os
import json
import base64
from unittest.mock import patch, MagicMock, call

from video_understanding.ai.models.openai_model import (
    OpenAIConfig,
    OpenAIClient,
    OpenAIModel,
    OpenAIError,
    convert_image_to_base64,
)


class TestOpenAIConfig:
    """Test suite for OpenAIConfig class."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        config = OpenAIConfig()

        assert config.api_key == ""
        assert config.model == "gpt-4-vision-preview"
        assert config.api_base == "https://api.openai.com/v1"
        assert config.timeout == 60
        assert config.max_tokens == 300

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        config = OpenAIConfig(
            api_key="test-key",
            model="gpt-4-turbo",
            api_base="https://custom-api.openai.com/v1",
            timeout=120,
            max_tokens=500,
        )

        assert config.api_key == "test-key"
        assert config.model == "gpt-4-turbo"
        assert config.api_base == "https://custom-api.openai.com/v1"
        assert config.timeout == 120
        assert config.max_tokens == 500

    def test_validation(self):
        """Test validation rules."""
        # Invalid API key
        with pytest.raises(ValueError, match="API key cannot be None"):
            OpenAIConfig(api_key=None)

        # Invalid model
        with pytest.raises(ValueError, match="Model cannot be empty"):
            OpenAIConfig(model="")

        # Invalid API base
        with pytest.raises(ValueError, match="API base URL cannot be empty"):
            OpenAIConfig(api_base="")

        # Invalid timeout
        with pytest.raises(ValueError, match="Timeout must be positive"):
            OpenAIConfig(timeout=0)

        # Invalid max tokens
        with pytest.raises(ValueError, match="Max tokens must be positive"):
            OpenAIConfig(max_tokens=0)

    def test_from_dict(self):
        """Test creation from dictionary."""
        config_dict = {
            "api_key": "test-key",
            "model": "gpt-4-turbo",
            "api_base": "https://custom-api.openai.com/v1",
            "timeout": 120,
            "max_tokens": 500,
        }

        config = OpenAIConfig.from_dict(config_dict)

        assert config.api_key == "test-key"
        assert config.model == "gpt-4-turbo"
        assert config.api_base == "https://custom-api.openai.com/v1"
        assert config.timeout == 120
        assert config.max_tokens == 500

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = OpenAIConfig(
            api_key="test-key",
            model="gpt-4-turbo",
            api_base="https://custom-api.openai.com/v1",
            timeout=120,
            max_tokens=500,
        )

        config_dict = config.to_dict()

        assert config_dict["api_key"] == "test-key"
        assert config_dict["model"] == "gpt-4-turbo"
        assert config_dict["api_base"] == "https://custom-api.openai.com/v1"
        assert config_dict["timeout"] == 120
        assert config_dict["max_tokens"] == 500


class TestOpenAIClient:
    """Test suite for OpenAIClient class."""

    def setup_method(self):
        """Set up test environment."""
        self.config = OpenAIConfig(api_key="test-key")
        self.client = OpenAIClient(self.config)

    @patch("requests.post")
    def test_chat_completion(self, mock_post):
        """Test chat completion."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "This is a test response."}}]
        }
        mock_post.return_value = mock_response

        # Test parameters
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"},
        ]

        # Call the method
        response = self.client.chat_completion(messages)

        # Verify response
        assert response == "This is a test response."

        # Verify request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.openai.com/v1/chat/completions"
        assert kwargs["headers"]["Authorization"] == "Bearer test-key"
        assert kwargs["json"]["model"] == "gpt-4-vision-preview"
        assert kwargs["json"]["messages"] == messages
        assert kwargs["json"]["max_tokens"] == 300
        assert kwargs["timeout"] == 60

    @patch("requests.post")
    def test_chat_completion_with_error(self, mock_post):
        """Test chat completion with error response."""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Invalid API key"}}
        mock_post.return_value = mock_response

        # Test parameters
        messages = [{"role": "user", "content": "What is the capital of France?"}]

        # Call the method and expect exception
        with pytest.raises(OpenAIError, match="OpenAI API Error: Invalid API key"):
            self.client.chat_completion(messages)

    @patch("requests.post")
    def test_chat_completion_with_network_error(self, mock_post):
        """Test chat completion with network error."""
        # Mock network error
        mock_post.side_effect = Exception("Connection error")

        # Test parameters
        messages = [{"role": "user", "content": "What is the capital of France?"}]

        # Call the method and expect exception
        with pytest.raises(
            OpenAIError, match="OpenAI API Request Failed: Connection error"
        ):
            self.client.chat_completion(messages)

    @patch("requests.post")
    def test_chat_completion_with_unexpected_response(self, mock_post):
        """Test chat completion with unexpected response format."""
        # Mock response with unexpected format
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"unexpected_field": "value"}
        mock_post.return_value = mock_response

        # Test parameters
        messages = [{"role": "user", "content": "What is the capital of France?"}]

        # Call the method and expect exception
        with pytest.raises(OpenAIError, match="Unexpected response format"):
            self.client.chat_completion(messages)

    @patch("requests.post")
    def test_image_analysis(self, mock_post):
        """Test image analysis."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "The image shows a beautiful landscape."}}
            ]
        }
        mock_post.return_value = mock_response

        # Test parameters
        image_base64 = "base64encodedimage"
        prompt = "Describe this image"

        # Call the method
        response = self.client.image_analysis(image_base64, prompt)

        # Verify response
        assert response == "The image shows a beautiful landscape."

        # Verify request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.openai.com/v1/chat/completions"
        assert kwargs["headers"]["Authorization"] == "Bearer test-key"
        assert kwargs["json"]["model"] == "gpt-4-vision-preview"
        assert kwargs["json"]["messages"][0]["role"] == "user"
        assert len(kwargs["json"]["messages"][0]["content"]) == 2
        assert kwargs["json"]["messages"][0]["content"][0]["type"] == "text"
        assert kwargs["json"]["messages"][0]["content"][0]["text"] == prompt
        assert kwargs["json"]["messages"][0]["content"][1]["type"] == "image_url"
        assert (
            kwargs["json"]["messages"][0]["content"][1]["image_url"]["url"]
            == f"data:image/jpeg;base64,{image_base64}"
        )

    @patch("requests.post")
    def test_image_analysis_with_multiple_images(self, mock_post):
        """Test image analysis with multiple images."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Comparison of images: both show landscapes."}}
            ]
        }
        mock_post.return_value = mock_response

        # Test parameters
        image_base64_list = ["base64encodedimage1", "base64encodedimage2"]
        prompt = "Compare these images"

        # Call the method
        response = self.client.image_analysis(image_base64_list, prompt)

        # Verify response
        assert response == "Comparison of images: both show landscapes."

        # Verify request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.openai.com/v1/chat/completions"
        assert kwargs["json"]["messages"][0]["role"] == "user"
        assert len(kwargs["json"]["messages"][0]["content"]) == 3  # Text + 2 images
        assert kwargs["json"]["messages"][0]["content"][0]["type"] == "text"
        assert kwargs["json"]["messages"][0]["content"][1]["type"] == "image_url"
        assert (
            kwargs["json"]["messages"][0]["content"][1]["image_url"]["url"]
            == f"data:image/jpeg;base64,{image_base64_list[0]}"
        )
        assert kwargs["json"]["messages"][0]["content"][2]["type"] == "image_url"
        assert (
            kwargs["json"]["messages"][0]["content"][2]["image_url"]["url"]
            == f"data:image/jpeg;base64,{image_base64_list[1]}"
        )


class TestConvertImageToBase64:
    """Test suite for convert_image_to_base64 function."""

    def test_convert_image_to_base64_from_path(self, tmp_path):
        """Test converting image to base64 from file path."""
        # Create a test image file
        image_path = tmp_path / "test_image.jpg"
        with open(image_path, "wb") as f:
            f.write(b"test image content")

        # Call the function
        with patch("builtins.open", new_callable=MagicMock) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = (
                b"test image content"
            )
            result = convert_image_to_base64(image_path)

        # Verify result
        expected = base64.b64encode(b"test image content").decode("utf-8")
        assert result == expected

    def test_convert_image_to_base64_from_bytes_io(self):
        """Test converting image to base64 from BytesIO."""
        # Create a BytesIO object
        image_bytes = io.BytesIO(b"test image content")

        # Call the function
        result = convert_image_to_base64(image_bytes)

        # Verify result
        expected = base64.b64encode(b"test image content").decode("utf-8")
        assert result == expected

    def test_convert_image_to_base64_from_bytes(self):
        """Test converting image to base64 from bytes."""
        # Create bytes
        image_bytes = b"test image content"

        # Call the function
        result = convert_image_to_base64(image_bytes)

        # Verify result
        expected = base64.b64encode(b"test image content").decode("utf-8")
        assert result == expected

    def test_convert_image_to_base64_invalid_input(self):
        """Test converting image to base64 with invalid input."""
        # Call the function with invalid input
        with pytest.raises(TypeError, match="Unsupported image type"):
            convert_image_to_base64(123)  # Integer is not a valid image type


class TestOpenAIModel:
    """Test suite for OpenAIModel class."""

    def setup_method(self):
        """Set up test environment."""
        self.config = OpenAIConfig(api_key="test-key")
        self.client = OpenAIClient(self.config)
        self.model = OpenAIModel(self.config)

    @patch.object(OpenAIClient, "chat_completion")
    def test_generate_text(self, mock_chat_completion):
        """Test generating text."""
        # Mock response
        mock_chat_completion.return_value = "This is a test response."

        # Call the method
        response = self.model.generate_text("What is the capital of France?")

        # Verify response
        assert response == "This is a test response."

        # Verify client call
        mock_chat_completion.assert_called_once()
        args, kwargs = mock_chat_completion.call_args
        assert args[0][0]["role"] == "user"
        assert args[0][0]["content"] == "What is the capital of France?"

    @patch.object(OpenAIClient, "chat_completion")
    def test_generate_text_with_system_prompt(self, mock_chat_completion):
        """Test generating text with system prompt."""
        # Mock response
        mock_chat_completion.return_value = "This is a test response."

        # Call the method
        response = self.model.generate_text(
            "What is the capital of France?",
            system_prompt="You are a geography expert.",
        )

        # Verify response
        assert response == "This is a test response."

        # Verify client call
        mock_chat_completion.assert_called_once()
        args, kwargs = mock_chat_completion.call_args
        assert len(args[0]) == 2
        assert args[0][0]["role"] == "system"
        assert args[0][0]["content"] == "You are a geography expert."
        assert args[0][1]["role"] == "user"
        assert args[0][1]["content"] == "What is the capital of France?"

    @patch.object(OpenAIClient, "image_analysis")
    @patch("video_understanding.ai.models.openai_model.convert_image_to_base64")
    def test_analyze_image(self, mock_convert, mock_image_analysis):
        """Test analyzing image."""
        # Mock responses
        mock_convert.return_value = "base64encodedimage"
        mock_image_analysis.return_value = "The image shows a beautiful landscape."

        # Test parameters
        image_path = "/path/to/image.jpg"
        prompt = "Describe this image"

        # Call the method
        response = self.model.analyze_image(image_path, prompt)

        # Verify response
        assert response == "The image shows a beautiful landscape."

        # Verify calls
        mock_convert.assert_called_once_with(image_path)
        mock_image_analysis.assert_called_once_with("base64encodedimage", prompt)

    @patch.object(OpenAIClient, "image_analysis")
    @patch("video_understanding.ai.models.openai_model.convert_image_to_base64")
    def test_analyze_images(self, mock_convert, mock_image_analysis):
        """Test analyzing multiple images."""
        # Mock responses
        mock_convert.side_effect = ["base64encodedimage1", "base64encodedimage2"]
        mock_image_analysis.return_value = "Comparison of images: both show landscapes."

        # Test parameters
        image_paths = ["/path/to/image1.jpg", "/path/to/image2.jpg"]
        prompt = "Compare these images"

        # Call the method
        response = self.model.analyze_images(image_paths, prompt)

        # Verify response
        assert response == "Comparison of images: both show landscapes."

        # Verify calls
        assert mock_convert.call_count == 2
        mock_convert.assert_has_calls([call(image_paths[0]), call(image_paths[1])])
        mock_image_analysis.assert_called_once_with(
            ["base64encodedimage1", "base64encodedimage2"], prompt
        )

    @patch.object(OpenAIClient, "chat_completion")
    def test_extract_text_from_image(self, mock_chat_completion):
        """Test extracting text from image."""
        # Mock response
        mock_chat_completion.return_value = "Text: Hello World"

        # Call the method with mocked image analysis
        with patch.object(
            OpenAIModel, "analyze_image", return_value="Text: Hello World"
        ):
            text = self.model.extract_text_from_image("/path/to/image.jpg")

        # Verify response
        assert text == "Text: Hello World"

    @patch.object(OpenAIClient, "chat_completion")
    def test_describe_scene(self, mock_chat_completion):
        """Test describing scene."""
        # Mock response
        mock_chat_completion.return_value = (
            "A beautiful mountain landscape with a lake."
        )

        # Call the method with mocked image analysis
        with patch.object(
            OpenAIModel,
            "analyze_image",
            return_value="A beautiful mountain landscape with a lake.",
        ):
            description = self.model.describe_scene("/path/to/image.jpg")

        # Verify response
        assert description == "A beautiful mountain landscape with a lake."

    @patch.object(OpenAIClient, "chat_completion")
    def test_detect_objects(self, mock_chat_completion):
        """Test detecting objects."""
        # Mock response
        mock_chat_completion.return_value = json.dumps(
            {"objects": ["mountain", "lake", "tree", "sky"]}
        )

        # Call the method with mocked image analysis
        with patch.object(
            OpenAIModel,
            "analyze_image",
            return_value=json.dumps({"objects": ["mountain", "lake", "tree", "sky"]}),
        ):
            objects = self.model.detect_objects("/path/to/image.jpg")

        # Verify response
        assert objects == ["mountain", "lake", "tree", "sky"]
