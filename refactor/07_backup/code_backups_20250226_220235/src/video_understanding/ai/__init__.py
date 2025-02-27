"""AI module for video understanding and processing.
This module contains model implementations and pipeline orchestration.
"""

__version__ = "0.1.0"

from .exceptions import ModelError, ValidationError, APIError, RateLimitError
from .models import BaseModel, GPT4VModel, GeminiModel, WhisperModel, TwelveLabsModel
from .pipeline import ModelPipeline

__all__ = [
    # Exceptions
    "ModelError",
    "ValidationError",
    "APIError",
    "RateLimitError",
    # Models
    "BaseModel",
    "GPT4VModel",
    "GeminiModel",
    "WhisperModel",
    "TwelveLabsModel",
    # Pipeline
    "ModelPipeline",
]
