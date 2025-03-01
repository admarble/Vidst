# GPT-4 Vision Model API Reference

## Overview

The GPT-4 Vision model implementation for processing visual content using OpenAI's GPT-4V API.

## Classes

### GPT4VModel

```python
class GPT4VModel:
    """
    GPT-4 Vision model for processing visual content.

    This class provides an interface to OpenAI's GPT-4V API for analyzing
    images and extracting information from visual content.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize GPT-4V model.

        Args:
            config: Model configuration dictionary with the following keys:
                - api_key: OpenAI API key (required)
                - api_base: API base URL (optional)
                - model: Model name (default: "gpt-4-vision-preview")
                - max_tokens: Maximum tokens for response (default: 300)
                - temperature: Temperature for sampling (default: 0.7)

        Raises:
            ConfigurationError: If configuration is invalid
        """

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an image using GPT-4V.

        Args:
            input_data: Dictionary containing:
                - image_url: URL or path to image
                - prompt: Text prompt for the model
                - max_tokens: Optional override for max tokens

        Returns:
            Dictionary containing:
                - analysis: Model's response
                - model: Model name used
                - usage: Token usage statistics

        Raises:
            ValidationError: If input data is invalid
            APIError: If API request fails
        """

    async def close(self):
        """
        Close the model and release resources.

        This method should be called when the model is no longer needed
        to ensure proper cleanup of resources.
        """
```

### GPT4VConfig

```python
class GPT4VConfig:
    """
    Configuration class for GPT-4V model.

    Attributes:
        api_key: OpenAI API key
        api_base: API base URL
        model: Model name
        max_tokens: Maximum tokens for response
        temperature: Temperature for sampling
    """
```

## Usage Example

```python
from video_understanding.ai.models.gpt4v import GPT4VModel

# Initialize model
model = GPT4VModel({
    "api_key": "your-openai-api-key",
    "model": "gpt-4-vision-preview",
    "max_tokens": 300
})

# Process an image
result = await model.process({
    "image_url": "path/to/image.jpg",
    "prompt": "Describe what's in this image."
})

print(result["analysis"])

# Clean up
await model.close()
```
