"""AI model initialization and management."""

from typing import Any

from .base import BaseModel
from .config import get_model_config
from .gemini import GeminiModel
from .gpt4v import GPT4VisionModel
from .twelve_labs import TwelveLabsModel
from .whisper import WhisperModel

# Model registry
MODEL_REGISTRY: dict[str, type[BaseModel]] = {
    "twelve_labs": TwelveLabsModel,
    "gpt4v": GPT4VisionModel,
    "gemini": GeminiModel,
    "whisper": WhisperModel,
}


def initialize_models() -> dict[str, BaseModel]:
    """Initialize all registered models.

    Returns:
        Dict[str, BaseModel]: Dictionary of initialized model instances
    """
    return {name: model_cls() for name, model_cls in MODEL_REGISTRY.items()}


def load_model(model_name: str, config: dict[str, Any] | None = None) -> BaseModel:
    """Load a specific model with optional configuration.

    This function loads a model from the registry and initializes it
    with the provided configuration. If no configuration is provided,
    it will use the default configuration from get_model_config().

    Args:
        model_name: Name of the model to load
        config: Optional configuration dictionary

    Returns:
        Initialized model instance

    Raises:
        ValueError: If model_name is not found in registry
        ConfigurationError: If configuration is invalid
    """
    if model_name not in MODEL_REGISTRY:
        raise ValueError(f"Model {model_name} not found in registry")

    if config is None:
        config = get_model_config(model_name)

    model_cls = MODEL_REGISTRY[model_name]
    return model_cls(**config)


def get_model_config(model_name: str) -> dict[str, Any]:
    """Get configuration for a specific model.

    This function loads the model's configuration from the config file.
    If no model-specific configuration exists, returns default values.

    Args:
        model_name: Name of the model

    Returns:
        Configuration dictionary for the model

    Raises:
        ValueError: If model_name is not found in registry
    """
    if model_name not in MODEL_REGISTRY:
        raise ValueError(f"Model {model_name} not found in registry")

    config_path = Path(__file__).parent / "config" / f"{model_name}.json"

    # Default configurations
    default_configs = {
        "twelve_labs": {"api_key": "", "max_retries": 3, "timeout": 300},
        "gpt4v": {"api_key": "", "model": "gpt-4-vision-preview", "max_tokens": 1000},
        "gemini": {"api_key": "", "model": "gemini-pro-vision", "temperature": 0.7},
        "whisper": {"api_key": "", "model": "whisper-v3", "language": "en"},
    }

    try:
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load config for {model_name}: {e}")

    return default_configs.get(model_name, {})
