"""
Configuration classes for video processing and system settings.

This module contains dataclass configurations for:
- Video processing parameters (file size limits, formats)
- System processing settings (concurrent jobs, memory limits)
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from dotenv import load_dotenv

from .exceptions import ConfigurationError


class VideoConfig:
    """Configuration for video processing."""

    def __init__(
        self,
        upload_directory: Path = None,
        supported_formats: Optional[List[str]] = None,
        max_file_size: Optional[int] = None,
        min_scene_length: Optional[int] = None,
        max_scenes_per_video: Optional[int] = None,
    ):
        """Initialize configuration.

        Args:
            upload_directory: Optional custom upload directory
            supported_formats: List of supported video formats
            max_file_size: Maximum file size in bytes
            min_scene_length: Minimum scene length in seconds
            max_scenes_per_video: Maximum number of scenes per video
        """
        self.UPLOAD_DIRECTORY = upload_directory or Path("uploads")
        self.SUPPORTED_FORMATS: Set[str] = {
            fmt.upper() for fmt in (supported_formats or ["MP4", "AVI", "MOV"])
        }
        self.MAX_FILE_SIZE = max_file_size or 2 * 1024 * 1024 * 1024  # 2GB
        self.MIN_SCENE_LENGTH = min_scene_length or 2  # seconds
        self.MAX_SCENES_PER_VIDEO = max_scenes_per_video or 500

        # Create upload directory
        self.UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not self.UPLOAD_DIRECTORY.exists():
            raise ConfigurationError("Upload directory does not exist")

        if not self.UPLOAD_DIRECTORY.is_dir():
            raise ConfigurationError("Upload directory path is not a directory")

        if self.MAX_FILE_SIZE <= 0:
            raise ConfigurationError("MAX_FILE_SIZE must be positive")

        if self.MIN_SCENE_LENGTH <= 0:
            raise ConfigurationError("MIN_SCENE_LENGTH must be positive")

        if self.MAX_SCENES_PER_VIDEO <= 0:
            raise ConfigurationError("MAX_SCENES_PER_VIDEO must be positive")

        if not self.SUPPORTED_FORMATS:
            raise ConfigurationError("No supported formats specified")


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
        "openai_api_key": "OpenAI",
        "gemini_api_key": "Google Gemini",
        "twelve_labs_api_key": "Twelve Labs",
    }

    missing_keys: List[str] = []
    invalid_keys: List[str] = []

    for key, service in required_keys.items():
        api_key = config.get(key)
        if not api_key:
            missing_keys.append(service)
        elif (
            not isinstance(api_key, str) or len(api_key.strip()) < 10
        ):  # Basic validation
            invalid_keys.append(service)

    errors = []
    if missing_keys:
        errors.append(f"Missing API keys for: {', '.join(missing_keys)}")
    if invalid_keys:
        errors.append(f"Invalid API keys for: {', '.join(invalid_keys)}")

    if errors:
        raise ConfigurationError("\n".join(errors))


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables.

    Returns:
        Dictionary containing configuration values

    Raises:
        ConfigurationError: If required configuration is missing or invalid
    """
    # Load environment variables from .env file
    load_dotenv()

    config = {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        "twelve_labs_api_key": os.getenv("TWELVE_LABS_API_KEY"),
        "upload_directory": Path(os.getenv("UPLOAD_DIRECTORY", "uploads")),
        "max_concurrent_jobs": int(os.getenv("MAX_CONCURRENT_JOBS", "3")),
        "cache_ttl": int(os.getenv("CACHE_TTL", "86400")),  # 24 hours
    }

    try:
        validate_api_keys(config)
    except ConfigurationError as e:
        if config["environment"] == "development":
            print(f"\nConfiguration Error: {e}")
            print(
                "Please check your .env file and ensure all required API keys are set correctly."
            )
            print("Required Environment Variables:")
            print("  OPENAI_API_KEY=<your-openai-api-key>")
            print("  GEMINI_API_KEY=<your-gemini-api-key>")
            print("  TWELVE_LABS_API_KEY=<your-twelve-labs-api-key>")
        raise

    return config
