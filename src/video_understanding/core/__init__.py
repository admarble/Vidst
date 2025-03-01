"""Core module for video understanding system.
Contains base configurations, utilities and exceptions.
"""

__version__ = "0.1.0"

# Core package imports
from .config import ProcessingConfig, VideoConfig
from .exceptions import *
from .input import *
from .logging_config import setup_logging
from .metrics import (
    MetricMeasurement,
    MetricsTracker,
    MetricThreshold,
    MetricType,
    PerformanceTimer,
    SuccessCriteria,
)
from .output import *
from .processing import *
from .scene import *
from .upload import *

# Define public API
__all__ = [
    # Config
    "ProcessingConfig",
    "VideoConfig",
    # Exceptions
    "CoreError",
    "ConfigError",
    "ProcessingError",
    "ValidationError",
    # Input
    "InputProcessor",
    "InputValidator",
    # Output
    "OutputFormatter",
    "OutputValidator",
    # Processing
    "VideoProcessor",
    "ProcessingPipeline",
    # Scene
    "SceneDetector",
    "SceneAnalyzer",
    # Upload
    "VideoUploader",
    "UploadManager",
    # Metrics
    "MetricType",
    "MetricThreshold",
    "MetricMeasurement",
    "SuccessCriteria",
    "MetricsTracker",
    "PerformanceTimer",
    "setup_logging",
]

"""
Core package for video processing functionality.
"""

from .exceptions import (
    VideoProcessingError,
    VideoFormatError,
    ResourceExceededError,
    ConcurrencyLimitError,
)

"""Core functionality for video processing and analysis."""

from .config import ProcessingConfig, VideoConfig
from .exceptions import VideoUnderstandingError
from .processing import VideoProcessor
from .upload import VideoUploader

__all__ = [
    "ProcessingConfig",
    "VideoConfig",
    "VideoProcessor",
    "VideoUnderstandingError",
    "VideoUploader",
]
