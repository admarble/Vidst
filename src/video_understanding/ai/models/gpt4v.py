"""GPT-4V model implementation for image analysis."""

import asyncio
from typing import Any, Dict, Optional
import aiohttp

from .base import BaseModel
from ..exceptions import ValidationError, APIError, ConfigurationError

class GPT4VConfig:
    """Configuration for GPT-4V model."""

    def __init__(
        self,
        api_key: str,
        api_base: str = "https://api.openai.com/v1",
        model: str = "gpt-4-vision-preview",
        max_tokens: int = 300,
        temperature: float = 0.7,
    ):
        """Initialize GPT-4V configuration.

        Args:
            api_key: OpenAI API key
            api_base: Base URL for API
            model: Model identifier
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
        """
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

class GPT4VModel(BaseModel):
    """GPT-4V model for image analysis."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize GPT-4V model.

        Args:
            config: Model configuration

        Raises:
            ConfigurationError: If configuration is invalid
        """
        super().__init__(config)
        if not config or "api_key" not in config:
            raise ConfigurationError("API key required")

        self.config = GPT4VConfig(**config)
        self.session: Optional[aiohttp.ClientSession] = None

    def validate(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data.

        Args:
            input_data: Dictionary containing:
                - image_url: URL or base64 image
                - prompt: Analysis prompt

        Returns:
            bool: True if valid

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(input_data, dict):
            raise ValidationError("Input must be dictionary")

        if "image_url" not in input_data:
            raise ValidationError("image_url required")

        if "prompt" not in input_data:
            raise ValidationError("prompt required")

        if not isinstance(input_data["prompt"], str):
            raise ValidationError("prompt must be string")

        return True

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process image through GPT-4V.

        Args:
            input_data: Dictionary containing image and prompt

        Returns:
            Dictionary containing analysis results

        Raises:
            APIError: If API request fails
        """
        self.validate(input_data)

        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.config.api_key}"}
            )

        try:
            async with self.session.post(
                f"{self.config.api_base}/chat/completions",
                json={
                    "model": self.config.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": input_data["prompt"]
                                },
                                {
                                    "type": "image_url",
                                    "image_url": input_data["image_url"]
                                }
                            ]
                        }
                    ],
                    "max_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature
                }
            ) as response:
                if response.status != 200:
                    raise APIError(f"API request failed: {response.status}")

                result = await response.json()
                return {
                    "analysis": result["choices"][0]["message"]["content"],
                    "model": self.config.model,
                    "usage": result.get("usage", {})
                }

        except aiohttp.ClientError as e:
            raise APIError(f"API request failed: {str(e)}")

    async def close(self) -> None:
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None
