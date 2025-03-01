"""
Video Understanding AI - Core package initialization.
"""

import logging
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("video_understanding")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

# Configure logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Import core components
from .core.config import ProcessingConfig, VideoConfig
from .core.exceptions import (
    VideoUnderstandingError,
    ProcessingError,
    ValidationError,
    StorageError,
    VideoFormatError,
    APIError,
    ModelError,
    PipelineError,
)
from .core.processing import VideoProcessor
from .core.processing.pipeline import ProcessingPipeline
from .core.scene import SceneDetector
from .core.upload.processor import UploadProcessor

# Import metrics
from .core.metrics import (
    MetricType,
    MetricThreshold,
    MetricMeasurement,
    SuccessCriteria,
    MetricsTracker,
    PerformanceTimer,
)

# Import AI models
from .ai.models.base import BaseModel
from .ai.models.gemini import GeminiModel
from .ai.models.gpt4v import GPT4VModel
from .ai.models.twelve_labs import TwelveLabsModel
from .ai.models.whisper import WhisperModel
from .ai.pipeline import VideoPipeline

# Import storage components
from .storage.metadata import MetadataStore
from .storage.cache import CacheStore
from .storage.vector import VectorStorage, VectorStorageConfig

# Define public API
__all__ = [
    # Core components
    "ProcessingConfig",
    "VideoConfig",
    "VideoUnderstandingError",
    "ProcessingError",
    "ValidationError",
    "StorageError",
    "VideoFormatError",
    "APIError",
    "ModelError",
    "PipelineError",
    "VideoProcessor",
    "ProcessingPipeline",
    "SceneDetector",
    "UploadProcessor",

    # Metrics
    "MetricType",
    "MetricThreshold",
    "MetricMeasurement",
    "SuccessCriteria",
    "MetricsTracker",
    "PerformanceTimer",

    # AI models
    "BaseModel",
    "GeminiModel",
    "GPT4VModel",
    "TwelveLabsModel",
    "WhisperModel",
    "VideoPipeline",

    # Storage
    "MetadataStore",
    "CacheStore",
    "VectorStorage",
    "VectorStorageConfig",
]
