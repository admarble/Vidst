"""
Configuration classes for video processing and system settings.

This module contains dataclass configurations for:
- Video processing parameters (file size limits, formats)
- System processing settings (concurrent jobs, memory limits)
"""

import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Set, Optional, List


class ConfigurationError(Exception):
    """Raised when configuration validation fails."""
    pass


class VideoConfig:
    """Configuration settings for video processing.
    
    Attributes:
        MAX_FILE_SIZE: Maximum allowed file size in bytes (2GB)
        SUPPORTED_FORMATS: Set of allowed video file formats
        UPLOAD_DIRECTORY: Path where uploaded videos are stored
        MIN_SCENE_LENGTH: Minimum duration of a scene in seconds
        MAX_SCENES_PER_VIDEO: Maximum number of scenes allowed per video
    """

    # File size limits (2GB in bytes)
    MAX_FILE_SIZE: int = 2 * 1024 * 1024 * 1024

    # Supported video formats
    SUPPORTED_FORMATS: Set[str] = {'MP4', 'AVI', 'MOV'}

    # Upload directory - using a 'uploads' directory in the project root
    UPLOAD_DIRECTORY: Path = Path('uploads')

    # Processing settings
    MIN_SCENE_LENGTH: float = 2.0  # seconds
    MAX_SCENES_PER_VIDEO: int = 500

    def __init__(self) -> None:
        """Initialize configuration and create necessary directories."""
        self._setup_logging()
        self._create_upload_directory()

    def _setup_logging(self) -> None:
        """Set up logging for the configuration module."""
        self.logger = logging.getLogger(__name__)

    def _create_upload_directory(self) -> None:
        """Create the upload directory if it doesn't exist."""
        try:
            self.UPLOAD_DIRECTORY.mkdir(exist_ok=True)
            self.logger.info(f"Upload directory created at {self.UPLOAD_DIRECTORY}")
        except Exception as e:
            self.logger.error(f"Failed to create upload directory: {e}")
            raise ConfigurationError(f"Failed to create upload directory: {e}")


@dataclass(frozen=True)
class ProcessingConfig:
    """Configuration settings for system processing resources.
    
    Attributes:
        MAX_CONCURRENT_JOBS: Maximum number of videos that can be processed simultaneously
        MEMORY_LIMIT_PER_JOB: Maximum memory allocation per job in bytes (4GB)
    """

    MAX_CONCURRENT_JOBS: int = 3
    MEMORY_LIMIT_PER_JOB: int = 4 * 1024 * 1024 * 1024  # 4GB

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.MAX_CONCURRENT_JOBS < 1:
            raise ConfigurationError("MAX_CONCURRENT_JOBS must be at least 1")
        if self.MEMORY_LIMIT_PER_JOB < 1024 * 1024 * 1024:  # 1GB
            raise ConfigurationError("MEMORY_LIMIT_PER_JOB must be at least 1GB")


def validate_api_keys(config: Dict[str, Any]) -> None:
    """Validate that all required API keys are present and non-empty.
    
    Args:
        config: Configuration dictionary containing API keys
        
    Raises:
        ConfigurationError: If any required API key is missing or empty
    """
    required_keys = {
        'openai_api_key': 'OpenAI',
        'gemini_api_key': 'Google Gemini',
        'twelve_labs_api_key': 'Twelve Labs'
    }
    
    missing_keys: List[str] = []
    
    for key, service in required_keys.items():
        if not config.get(key):
            missing_keys.append(service)
    
    if missing_keys:
        raise ConfigurationError(
            f"Missing API keys for the following services: {', '.join(missing_keys)}"
        )


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables.
    
    Returns:
        Dict[str, Any]: Configuration dictionary containing API keys and environment settings
        
    Raises:
        ConfigurationError: If required environment variables are missing
        
    Note:
        Required environment variables:
        - OPENAI_API_KEY
        - GEMINI_API_KEY
        - TWELVE_LABS_API_KEY
        
        Optional environment variables:
        - ENVIRONMENT (defaults to 'development')
        - DEBUG (defaults to 'false')
    """
    config = {
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'gemini_api_key': os.getenv('GEMINI_API_KEY'),
        'twelve_labs_api_key': os.getenv('TWELVE_LABS_API_KEY'),
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'debug': os.getenv('DEBUG', 'false').lower() == 'true'
    }
    
    # Validate API keys
    validate_api_keys(config)
    
    return config