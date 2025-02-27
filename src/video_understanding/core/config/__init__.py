"""Configuration management for video processing."""

from dataclasses import dataclass, field
from pathlib import Path

from ..exceptions import ConfigurationError
from .credentials import (
    CredentialError,
    find_env_file,
    load_credentials,
    validate_credentials,
    get_service_credentials,
    get_all_credentials,
)


@dataclass
class ProcessingConfig:
    """Configuration for video processing."""

    max_video_size: int = 2 * 1024 * 1024 * 1024  # 2GB
    supported_formats: list[str] = field(default_factory=lambda: ["mp4", "avi", "mov"])
    min_scene_length: float = 2.0  # seconds
    max_scenes: int = 500
    concurrent_jobs: int = 3
    memory_limit: int = 4 * 1024 * 1024 * 1024  # 4GB
    cache_ttl: int = 86400  # 24 hours
    vector_cache_size: int = 1024 * 1024 * 1024  # 1GB


class VideoConfig:
    """Configuration settings for video processing."""

    def __init__(
        self,
        upload_directory: Path | None = None,
        supported_formats: list[str] | None = None,
        max_file_size: int | None = None,
        min_scene_length: float | None = None,
        max_scenes: int | None = None,
        max_concurrent_jobs: int | None = None,
        memory_limit: int | None = None,
        cache_ttl: int | None = None,
        vector_cache_size: int | None = None,
    ):
        """Initialize video configuration with default values.

        Args:
            upload_directory: Directory for uploaded files
            supported_formats: List of supported video formats
            max_file_size: Maximum file size in bytes
            min_scene_length: Minimum scene length in seconds
            max_scenes: Maximum number of scenes per video
            max_concurrent_jobs: Maximum number of concurrent jobs
            memory_limit: Memory limit per job in bytes
            cache_ttl: Cache time-to-live in seconds
            vector_cache_size: Vector cache size in bytes
        """
        self.upload_directory: Path = upload_directory or Path("uploads")
        self.max_file_size: int = max_file_size or 2 * 1024 * 1024 * 1024  # 2GB
        self.min_scene_length: float = min_scene_length or 2.0  # seconds
        self.max_scenes: int = max_scenes or 500
        self.supported_formats: set[str] = set(
            supported_formats or ["MP4", "AVI", "MOV"]
        )
        self.max_concurrent_jobs: int = max_concurrent_jobs or 3
        self.memory_limit: int = memory_limit or 4 * 1024 * 1024 * 1024  # 4GB
        self.cache_ttl: int = cache_ttl or 24 * 60 * 60  # 24 hours
        self.vector_cache_size: int = vector_cache_size or 1024 * 1024 * 1024  # 1GB

    def validate(self) -> None:
        """Validate configuration settings.

        Raises:
            ConfigurationError: If any settings are invalid
        """
        if self.max_file_size <= 0:
            raise ConfigurationError("max_file_size must be positive")
        if not self.supported_formats:
            raise ConfigurationError("supported_formats cannot be empty")
        if self.min_scene_length <= 0:
            raise ConfigurationError("min_scene_length must be positive")
        if self.max_scenes <= 0:
            raise ConfigurationError("max_scenes must be positive")
        if self.max_concurrent_jobs <= 0:
            raise ConfigurationError("max_concurrent_jobs must be positive")
        if self.memory_limit <= 0:
            raise ConfigurationError("memory_limit must be positive")
        if self.cache_ttl <= 0:
            raise ConfigurationError("cache_ttl must be positive")
        if self.vector_cache_size <= 0:
            raise ConfigurationError("vector_cache_size must be positive")

    def is_format_supported(self, format_: str) -> bool:
        """Check if a video format is supported."""
        return format_.upper() in {fmt.upper() for fmt in self.supported_formats}


__all__ = [
    "ProcessingConfig",
    "VideoConfig",
    "CredentialError",
    "find_env_file",
    "load_credentials",
    "validate_credentials",
    "get_service_credentials",
    "get_all_credentials",
]
