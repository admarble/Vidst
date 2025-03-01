"""Model configuration management."""

import json
from pathlib import Path
from typing import Any

from ..exceptions import ModelError


def get_model_config(model_name: str) -> dict[str, Any]:
    """Get configuration for a specific model.

    This function loads the model's configuration from the config file.
    If no model-specific configuration exists, returns default values.

    Args:
        model_name: Name of the model

    Returns:
        Configuration dictionary for the model

    Raises:
        ModelError: If model_name is not found in registry
    """
    # Default configurations
    default_configs = {
        "twelve_labs": {"api_key": "", "max_retries": 3, "timeout": 300},
        "gpt4v": {"api_key": "", "model": "gpt-4-vision-preview", "max_tokens": 1000},
        "gemini": {"api_key": "", "model": "gemini-pro-vision", "temperature": 0.7},
        "whisper": {"api_key": "", "model": "whisper-v3", "language": "en"},
    }

    if model_name not in default_configs:
        raise ModelError(f"Model {model_name} not found in registry")

    config_path = Path(__file__).parent / "config" / f"{model_name}.json"

    try:
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load config for {model_name}: {e}")

    return default_configs.get(model_name, {})
