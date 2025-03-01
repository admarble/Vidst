"""Configuration management for performance tests."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class MemoryThresholds:
    """Memory usage thresholds for performance testing."""

    max_memory_mb: int = 1024
    warning_memory_mb: float = 3.5 * 1024  # 3.5GB
    max_memory_growth_mb_per_hour: float = 100.0
    max_memory_spikes: int = 3


@dataclass
class ProcessingThresholds:
    """Processing time and throughput thresholds."""

    max_processing_time_s: float = 300.0
    max_processing_variance: float = 0.2
    min_videos_per_hour: int = 6  # Minimum videos processed per hour
    max_concurrent_tasks: int = 3
    max_processing_time_multiplier: float = 2.0  # Maximum multiplier for expected processing time


@dataclass
class ErrorThresholds:
    """Error rate and stability thresholds."""

    max_error_rate: float = 0.05
    max_consecutive_errors: int = 3
    max_cleanup_errors: int = 2
    error_window_s: float = 3600.0


@dataclass
class CacheConfig:
    """Configuration for cache performance testing."""

    cache_dir: Path = Path("/tmp/test_cache")
    ttl_s: float = 3600.0
    max_memory_items: int = 1000
    max_size_mb: int = 512
    cleanup_interval_s: float = 300.0


@dataclass
class TestVideoConfig:
    """Configuration for test video generation."""

    sizes_mb: dict[str, int] = field(
        default_factory=lambda: {
            "small": 10,
            "medium": 50,
            "large": 100,
        }
    )
    durations_s: dict[str, float] = field(
        default_factory=lambda: {
            "short": 30.0,
            "medium": 300.0,
            "long": 3600.0,
        }
    )
    supported_formats: list[str] = field(default_factory=lambda: ["mp4", "avi", "mov"])
    output_dir: Path = Path("temp_videos")


@dataclass
class PerformanceConfig:
    """Main configuration for performance testing."""

    memory: MemoryThresholds = field(default_factory=MemoryThresholds)
    processing: ProcessingThresholds = field(default_factory=ProcessingThresholds)
    errors: ErrorThresholds = field(default_factory=ErrorThresholds)
    cache: CacheConfig = field(default_factory=CacheConfig)
    video: TestVideoConfig = field(default_factory=TestVideoConfig)

    @classmethod
    def from_env(cls) -> "PerformanceConfig":
        """Create configuration from environment variables."""
        return cls(
            memory=MemoryThresholds(
                max_memory_mb=int(os.getenv("TEST_MAX_MEMORY_MB", 1024)),
                warning_memory_mb=float(
                    os.getenv("TEST_WARNING_MEMORY_MB", 3.5 * 1024)
                ),
                max_memory_growth_mb_per_hour=float(
                    os.getenv("TEST_MAX_MEMORY_GROWTH", 100.0)
                ),
                max_memory_spikes=int(os.getenv("TEST_MAX_MEMORY_SPIKES", 3)),
            ),
            processing=ProcessingThresholds(
                max_processing_time_s=float(
                    os.getenv("TEST_MAX_PROCESSING_TIME", 300.0)
                ),
                max_processing_variance=float(
                    os.getenv("TEST_MAX_PROCESSING_VARIANCE", 0.2)
                ),
                min_videos_per_hour=int(os.getenv("TEST_MIN_VIDEOS_PER_HOUR", 6)),
                max_concurrent_tasks=int(os.getenv("TEST_MAX_CONCURRENT_TASKS", 3)),
            ),
            errors=ErrorThresholds(
                max_error_rate=float(os.getenv("TEST_MAX_ERROR_RATE", 0.05)),
                max_consecutive_errors=int(os.getenv("TEST_MAX_CONSECUTIVE_ERRORS", 3)),
                max_cleanup_errors=int(os.getenv("TEST_MAX_CLEANUP_ERRORS", 2)),
                error_window_s=float(os.getenv("TEST_ERROR_WINDOW", 3600.0)),
            ),
        )

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "PerformanceConfig":
        """Create configuration from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            PerformanceConfig instance
        """
        return cls(
            memory=MemoryThresholds(**config_dict.get("memory", {})),
            processing=ProcessingThresholds(**config_dict.get("processing", {})),
            errors=ErrorThresholds(**config_dict.get("errors", {})),
            cache=CacheConfig(**config_dict.get("cache", {})),
            video=TestVideoConfig(**config_dict.get("video", {})),
        )

    def validate(self) -> list[str]:
        """Validate configuration values and return list of validation errors."""
        errors = []

        # Memory validations
        if self.memory.max_memory_mb <= 0:
            errors.append("max_memory_mb must be positive")
        if self.memory.warning_memory_mb >= self.memory.max_memory_mb:
            errors.append("warning_memory_mb must be less than max_memory_mb")

        # Processing validations
        if self.processing.max_processing_time_s <= 0:
            errors.append("max_processing_time_s must be positive")
        if self.processing.max_processing_variance <= 0:
            errors.append("max_processing_variance must be positive")
        if self.processing.min_videos_per_hour <= 0:
            errors.append("min_videos_per_hour must be positive")

        # Error threshold validations
        if not 0 <= self.errors.max_error_rate <= 1:
            errors.append("max_error_rate must be between 0 and 1")
        if self.errors.max_consecutive_errors <= 0:
            errors.append("max_consecutive_errors must be positive")

        return errors
