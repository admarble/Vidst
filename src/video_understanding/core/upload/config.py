"""Configuration for video upload processing.

This module provides configuration classes and utilities for customizing
the video upload processing pipeline.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

from video_understanding.core.exceptions import ConfigurationError
from video_understanding.models.video import ProcessingStatus


@dataclass
class ProcessorConfig:
    """Configuration for upload processor.

    Attributes:
        max_concurrent_uploads: Maximum number of concurrent uploads
        temp_file_timeout: Timeout for temporary files in seconds
        min_free_space_mb: Minimum required free disk space in MB
        processing_hooks: Custom processing hooks by stage
        custom_validators: Additional validation functions
        upload_chunk_size: Upload chunk size in bytes
        max_retries: Maximum number of retries for operations
        retry_delay: Delay between retries in seconds
        max_video_size: Maximum video file size in bytes
        supported_formats: List of supported video formats
        min_scene_length: Minimum scene length in seconds
        max_scenes: Maximum number of scenes per video
        concurrent_jobs: Maximum number of concurrent processing jobs
        memory_limit: Memory limit per job in bytes
        object_detection_model: Path to YOLOv8 model weights
        detection_confidence: Minimum confidence threshold for detections
        detection_enabled: Whether to enable object detection
        ocr_languages: List of languages for OCR
        ocr_confidence: Minimum confidence threshold for OCR
        ocr_enabled: Whether to enable OCR
        ocr_gpu: Whether to use GPU for OCR
    """
    # Resource limits
    max_concurrent_uploads: int = 3
    temp_file_timeout: int = 3600  # 1 hour
    min_free_space_mb: int = 1000
    upload_chunk_size: int = 8 * 1024 * 1024  # 8MB

    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0

    # Extension points
    processing_hooks: dict[ProcessingStatus, list[Callable]] = field(
        default_factory=dict
    )
    custom_validators: list[Callable[[Path], None]] = field(default_factory=list)
    progress_callbacks: list[Callable[[Any], None]] = field(default_factory=list)

    # Stage weights for progress calculation
    stage_weights: dict[ProcessingStatus, float] = field(
        default_factory=lambda: {
            ProcessingStatus.PENDING: 0.0,
            ProcessingStatus.UPLOADING: 0.2,
            ProcessingStatus.VALIDATING: 0.3,
            ProcessingStatus.PROCESSING: 0.4,
            ProcessingStatus.COMPLETED: 1.0,
            ProcessingStatus.FAILED: 1.0,
            ProcessingStatus.QUARANTINED: 1.0,
        }
    )

    # Video processing configuration
    max_video_size: int = 2 * 1024 * 1024 * 1024  # 2GB
    supported_formats: list[str] = field(default_factory=lambda: ["mp4", "avi", "mov"])
    min_scene_length: float = 2.0
    max_scenes: int = 500
    concurrent_jobs: int = 3
    memory_limit: int = 4 * 1024 * 1024 * 1024  # 4GB

    # Object detection configuration
    object_detection_model: str | None = None  # Uses default YOLOv8n if None
    detection_confidence: float = 0.5
    detection_enabled: bool = True

    # OCR configuration
    ocr_languages: list[str] = field(default_factory=lambda: ["en"])
    ocr_confidence: float = 0.5
    ocr_enabled: bool = True
    ocr_gpu: bool = False

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.max_concurrent_uploads < 1:
            raise ValueError("max_concurrent_uploads must be positive")
        if self.temp_file_timeout < 0:
            raise ValueError("temp_file_timeout must be non-negative")
        if self.min_free_space_mb < 0:
            raise ValueError("min_free_space_mb must be non-negative")
        if self.upload_chunk_size < 1:
            raise ValueError("upload_chunk_size must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.retry_delay < 0:
            raise ValueError("retry_delay must be non-negative")
        self.validate()

    def validate(self) -> None:  # noqa: C901
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
        if self.detection_confidence < 0 or self.detection_confidence > 1:
            raise ConfigurationError("detection_confidence must be between 0 and 1")
        if (
            self.object_detection_model
            and not Path(self.object_detection_model).exists()
        ):
            raise ConfigurationError("object_detection_model path does not exist")
        if self.ocr_confidence < 0 or self.ocr_confidence > 1:
            raise ConfigurationError("ocr_confidence must be between 0 and 1")
        if not self.ocr_languages:
            raise ConfigurationError("ocr_languages cannot be empty")

    def add_processing_hook(
        self,
        stage: ProcessingStatus,
        hook: Callable[[Path, Any], None],
    ) -> None:
        """Add a processing hook for a stage.

        Args:
            stage: Processing stage to add hook for
            hook: Function to call during processing
        """
        if stage not in self.processing_hooks:
            self.processing_hooks[stage] = []
        self.processing_hooks[stage].append(hook)

    def add_validator(
        self,
        validator: Callable[[Path], None],
    ) -> None:
        """Add a custom validator.

        Args:
            validator: Function to call for validation
        """
        self.custom_validators.append(validator)

    def add_progress_callback(
        self,
        callback: Callable[[Any], None],
    ) -> None:
        """Add a progress callback.

        Args:
            callback: Function to call with progress updates
        """
        self.progress_callbacks.append(callback)

    def get_stage_weight(
        self,
        stage: ProcessingStatus,
    ) -> float:
        """Get weight for a processing stage.

        Args:
            stage: Processing stage

        Returns:
            Weight between 0 and 1
        """
        return self.stage_weights.get(stage, 0.0)


@dataclass
class RetryConfig:
    """Configuration for retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts
        retry_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Exponential backoff multiplier
        retry_on: Exceptions to retry on
    """

    max_retries: int = 3
    retry_delay: float = 1.0
    max_delay: float = 30.0
    backoff_factor: float = 2.0
    retry_on: tuple = (IOError, OSError)

    def __post_init__(self) -> None:
        """Validate retry configuration."""
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.retry_delay < 0:
            raise ValueError("retry_delay must be non-negative")
        if self.max_delay < self.retry_delay:
            raise ValueError("max_delay must be >= retry_delay")
        if self.backoff_factor <= 1.0:
            raise ValueError("backoff_factor must be > 1.0")

    def get_retry_delay(self, attempt: int) -> float:
        """Calculate delay for a retry attempt.

        Args:
            attempt: Current attempt number (0-based)

        Returns:
            Delay in seconds
        """
        delay = self.retry_delay * (self.backoff_factor**attempt)
        return min(delay, self.max_delay)


@dataclass
class UploadConfig:
    """Configuration for video upload processing."""

    # File validation
    max_file_size_mb: int = 2048  # 2GB
    allowed_extensions: List[str] = field(default_factory=lambda: [".mp4", ".avi", ".mov"])

    # Processing
    detection_enabled: bool = True
    ocr_enabled: bool = True
    scene_detection_enabled: bool = True

    # OCR settings
    ocr_languages: List[str] = field(default_factory=lambda: ["eng"])
    ocr_confidence_threshold: float = 0.7

    # Scene detection
    min_scene_duration: float = 2.0  # seconds
    max_scenes: int = 500
    scene_threshold: float = 30.0  # threshold for scene change detection

    # Security
    virus_scan_enabled: bool = True
    content_validation_enabled: bool = True

    # Processing paths
    temp_dir: Optional[Path] = None
    output_dir: Optional[Path] = None

    def __post_init__(self):
        """Convert string paths to Path objects if needed."""
        if isinstance(self.temp_dir, str):
            self.temp_dir = Path(self.temp_dir)
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
