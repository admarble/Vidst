"""Configuration module for Video Understanding AI.

This module handles configuration settings for the project.
"""

# Standard library imports
from dataclasses import dataclass, field
from pathlib import Path

# Third-party imports
import yaml

# Local imports
from .exceptions import ConfigurationError


@dataclass
class ProcessingConfig:
    """Video processing configuration.

    Attributes:
        max_video_size: Maximum video file size in bytes
        supported_formats: List of supported video formats
        min_scene_length: Minimum scene length in seconds
        max_scenes: Maximum number of scenes per video
        concurrent_jobs: Maximum number of concurrent processing jobs
        memory_limit: Memory limit per job in bytes
    """

    max_video_size: int = 2 * 1024 * 1024 * 1024  # 2GB
    supported_formats: list[str] = field(default_factory=lambda: ["mp4", "avi", "mov"])
    min_scene_length: float = 2.0
    max_scenes: int = 500
    concurrent_jobs: int = 3
    memory_limit: int = 4 * 1024 * 1024 * 1024  # 4GB

    def validate(self) -> None:
        """Validate configuration settings.

        Raises:
            ConfigurationError: If settings are invalid
        """
        if self.max_video_size <= 0:
            raise ConfigurationError("max_video_size must be positive")
        if not self.supported_formats:
            raise ConfigurationError("supported_formats cannot be empty")
        if self.min_scene_length <= 0:
            raise ConfigurationError("min_scene_length must be positive")
        if self.max_scenes <= 0:
            raise ConfigurationError("max_scenes must be positive")
        if self.concurrent_jobs <= 0:
            raise ConfigurationError("concurrent_jobs must be positive")
        if self.memory_limit <= 0:
            raise ConfigurationError("memory_limit must be positive")


@dataclass
class StorageConfig:
    """Storage configuration.

    Attributes:
        cache_dir: Path to cache directory
        metadata_dir: Path to metadata directory
        vector_dir: Path to vector storage directory
        cache_ttl: Cache time-to-live in seconds
        cache_size: Maximum cache size in bytes
        vector_cache_size: Maximum vector cache size in bytes
    """

    cache_dir: Path = Path("/tmp/cache")
    metadata_dir: Path = Path("/tmp/metadata")
    vector_dir: Path = Path("/tmp/vectors")
    cache_ttl: int = 24 * 60 * 60  # 24 hours
    cache_size: int = 1024 * 1024 * 1024  # 1GB
    vector_cache_size: int = 1024 * 1024 * 1024  # 1GB

    def validate(self) -> None:
        """Validate configuration settings.

        Raises:
            ConfigurationError: If settings are invalid
        """
        if not isinstance(self.cache_dir, Path):
            raise ConfigurationError("cache_dir must be a Path")
        if not isinstance(self.metadata_dir, Path):
            raise ConfigurationError("metadata_dir must be a Path")
        if not isinstance(self.vector_dir, Path):
            raise ConfigurationError("vector_dir must be a Path")
        if self.cache_ttl <= 0:
            raise ConfigurationError("cache_ttl must be positive")
        if self.cache_size <= 0:
            raise ConfigurationError("cache_size must be positive")
        if self.vector_cache_size <= 0:
            raise ConfigurationError("vector_cache_size must be positive")


@dataclass
class Config:
    """Main configuration container.

    Attributes:
        processing: Video processing configuration
        storage: Storage configuration
        api_keys: API key dictionary
        debug: Debug mode flag
    """

    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    api_keys: dict[str, str] = field(default_factory=dict)
    debug: bool = False

    def validate(self) -> None:
        """Validate all configuration settings.

        Raises:
            ConfigurationError: If any settings are invalid
        """
        self.processing.validate()
        self.storage.validate()
        required_apis = {"openai", "gemini", "twelvelabs", "whisper"}
        missing_keys = required_apis - set(self.api_keys.keys())
        if missing_keys:
            raise ConfigurationError(f"Missing required API keys: {missing_keys}")


def load_config(config_path: Path) -> Config:
    """Load configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Loaded configuration object

    Raises:
        ConfigurationError: If loading fails or configuration is invalid
    """
    try:
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")

        with open(config_path, encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)

        if not isinstance(config_dict, dict):
            raise ConfigurationError("Invalid configuration format")

        config = Config(
            processing=ProcessingConfig(**config_dict.get("processing", {})),
            storage=StorageConfig(**config_dict.get("storage", {})),
            api_keys=config_dict.get("api_keys", {}),
            debug=config_dict.get("debug", False),
        )
        config.validate()
        return config

    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration: {e}") from e


def get_default_config() -> Config:
    """Get default configuration.

    Returns:
        Default configuration object
    """
    return Config()


def validate_config(config: Config) -> None:
    """Validate configuration object.

    Args:
        config: Configuration object to validate

    Raises:
        ConfigurationError: If configuration is invalid
    """
    if not isinstance(config, Config):
        raise ConfigurationError("Invalid configuration object")
    config.validate()
