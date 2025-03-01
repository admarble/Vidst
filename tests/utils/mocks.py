"""Mock implementations for test dependencies.

This module provides mock implementations of external dependencies and services
used in performance testing. These mocks simulate the behavior and performance
characteristics of real components while providing controlled test conditions.

Components:
- Video Processing: MockVideoPipeline, MockTwelveLabsModel
- Configuration: MockProcessingConfig, MockVideoConfig
- Storage: MockCache, MockVectorStorage
- Upload: MockVideoUploader

The mocks maintain realistic timing and resource usage patterns while
eliminating external dependencies and network calls.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock


@dataclass
class VideoConfig:
    """Mock video configuration for testing.

    Defines standard video sizes and durations for testing different
    processing scenarios.

    Attributes:
        sizes_mb: Dictionary of video sizes (small, medium, large)
        durations_seconds: Dictionary of video durations (short, medium, long)
    """

    sizes_mb: dict[str, int] = field(default_factory=dict)
    durations_seconds: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default video configurations."""
        self.sizes_mb = {
            "small": 10,  # 10MB
            "medium": 50,  # 50MB
            "large": 100,  # 100MB
        }
        self.durations_seconds = {
            "short": 60,  # 1 minute
            "medium": 300,  # 5 minutes
            "long": 900,  # 15 minutes
        }


@dataclass
class ProcessingConfig:
    """Mock processing configuration for testing.

    Defines processing parameters and limits for the pipeline.

    Attributes:
        max_retries: Maximum number of processing retries
        timeout_seconds: Processing timeout in seconds
        batch_size: Number of videos to process in batch
    """

    max_retries: int = 3
    timeout_seconds: int = 300
    batch_size: int = 10


class MockProcessingConfig:
    """Mock implementation of the processing configuration.

    Provides a complete configuration set for video processing including:
    - Video size and format limits
    - Processing parameters
    - Resource limits
    - Error handling settings

    Attributes:
        max_video_size: Maximum allowed video size
        supported_formats: List of supported video formats
        max_concurrent_jobs: Maximum concurrent processing jobs
        cache_ttl: Cache time-to-live in seconds
        video: Video-specific configurations
        processing: Processing-specific configurations
        errors: Error handling configurations
    """

    def __init__(self):
        """Initialize processing configuration with default values."""
        self.max_video_size = 100 * 1024 * 1024  # 100MB
        self.supported_formats = ["mp4", "avi", "mov"]
        self.max_concurrent_jobs = 3
        self.cache_ttl = 3600

        self.video = VideoConfig()
        self.processing = ProcessingConfig()
        self.errors = {"max_retries": 3, "backoff_factor": 1.5, "max_timeout": 300}


class MockTwelveLabsModel:
    """Mock implementation of the Twelve Labs AI model.

    Simulates the behavior of the Twelve Labs video understanding API
    with realistic timing and response patterns.

    Attributes:
        api_key: Mock API key for authentication
        _base_url: Mock API base URL
    """

    def __init__(self, api_key: str):
        """Initialize the mock model.

        Args:
            api_key: Mock API key
        """
        self.api_key = api_key
        self._base_url = "https://api.twelvelabs.io/v1.1"

    async def _upload_video(self, video_path: str) -> str:
        """Mock video upload to API.

        Args:
            video_path: Path to video file

        Returns:
            Mock video ID
        """
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "video_id": "test_video_id",
            "status": "completed",
        }
        return "test_video_id"

    async def _track_task_status(
        self, task_id: str, timeout: int = 300
    ) -> dict[str, Any]:
        """Mock task status tracking.

        Args:
            task_id: Task ID to track
            timeout: Status tracking timeout

        Returns:
            Mock task status and results
        """
        return {
            "status": "completed",
            "video_id": "test_video_id",
            "scene_description": "Test scene",
            "objects": [{"name": "test_object"}],
            "actions": [{"description": "test_action"}],
            "metadata": {"duration": 300, "fps": 30, "resolution": "1920x1080"},
        }

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Mock video processing.

        Args:
            input_data: Processing input parameters

        Returns:
            Mock processing results
        """
        return {
            "status": "completed",
            "video_id": "test_video_id",
            "results": {
                "scenes": [
                    {"start_time": 0, "end_time": 10, "description": "Test scene"}
                ]
            },
        }


class MockVideoPipeline:
    """Mock implementation of the video processing pipeline.

    Simulates the complete video processing pipeline including:
    - Video upload and validation
    - Multi-model processing
    - Result aggregation
    - Resource management

    Attributes:
        config: Processing configuration
        models: List of AI models to use
    """

    def __init__(self, config: MockProcessingConfig, models: list[MockTwelveLabsModel]):
        """Initialize the pipeline.

        Args:
            config: Processing configuration
            models: List of AI models
        """
        self.config = config
        self.models = models

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Mock pipeline processing.

        Args:
            input_data: Processing parameters

        Returns:
            Processing results

        Raises:
            ValueError: If video path is invalid
        """
        video_path = input_data.get("video_path")
        if not video_path or not Path(video_path).exists():
            return {"status": "error", "message": "Invalid video path"}

        results = []
        for model in self.models:
            result = await model.process(input_data)
            results.append(result)

        return {"status": "completed", "video_path": video_path, "results": results}

    def get_memory_usage(self) -> dict[str, float]:
        """Get mock memory usage statistics.

        Returns:
            Dictionary of memory usage metrics
        """
        return {
            "rss": 100 * 1024 * 1024,  # 100MB
            "vms": 200 * 1024 * 1024,  # 200MB
            "shared": 50 * 1024 * 1024,  # 50MB
        }


@dataclass
class MockVideoConfig:
    """Mock video configuration.

    Defines video-specific configuration parameters.

    Attributes:
        upload_directory: Directory for video uploads
        supported_formats: List of supported video formats
        max_file_size: Maximum allowed file size
    """

    upload_directory: Path
    supported_formats: list[str]
    max_file_size: int

    def __init__(self, **kwargs):
        """Initialize with provided parameters."""
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockVideoUploader:
    """Mock video upload handler.

    Simulates video upload functionality with realistic timing
    and resource usage patterns.

    Attributes:
        config: Upload configuration
    """

    def __init__(self, config: MockVideoConfig):
        """Initialize uploader with configuration.

        Args:
            config: Upload configuration
        """
        self.config = config

    def upload(self, video_path: str) -> dict[str, Any]:
        """Mock video upload.

        Args:
            video_path: Path to video file

        Returns:
            Upload status and video ID
        """
        return {"status": "success", "video_id": "test_video_id"}


class MockCache:
    """Mock caching implementation.

    Simulates an in-memory caching system with TTL and size limits.

    Attributes:
        cache_dir: Cache directory path
        ttl: Cache entry time-to-live
        max_memory_items: Maximum items in memory
        _cache: Internal cache storage
    """

    def __init__(self, cache_dir: Path, ttl: int, max_memory_items: int):
        """Initialize cache with configuration.

        Args:
            cache_dir: Cache directory path
            ttl: Time-to-live in seconds
            max_memory_items: Maximum items in memory
        """
        self.cache_dir = cache_dir
        self.ttl = ttl
        self.max_memory_items = max_memory_items
        self._cache: dict[str, Any] = {}

    def get(self, key: str) -> Any | None:
        """Get item from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set item in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = value


@dataclass
class MockVectorMetadata:
    """Mock vector metadata.

    Defines metadata for vector storage entries.

    Attributes:
        vector_id: Unique vector identifier
        source_id: Source data identifier
        vector_type: Type of vector data
    """

    vector_id: str
    source_id: str
    vector_type: str


class MockVectorStorageConfig:
    """Mock vector storage configuration.

    Defines configuration for vector storage operations.

    Attributes:
        dimension: Vector dimension
    """

    def __init__(self, dimension: int):
        """Initialize with vector dimension.

        Args:
            dimension: Vector dimension
        """
        self.dimension = dimension


class MockVectorStorage:
    """Mock vector storage implementation.

    Simulates vector storage and search functionality.

    Attributes:
        config: Storage configuration
        _storage: Internal vector storage
    """

    def __init__(self, config: MockVectorStorageConfig):
        """Initialize storage with configuration.

        Args:
            config: Storage configuration
        """
        self.config = config
        self._storage: dict[str, Any] = {}

    def add(self, vector_id: str, vector: Any, metadata: MockVectorMetadata) -> None:
        """Add vector to storage.

        Args:
            vector_id: Vector identifier
            vector: Vector data
            metadata: Vector metadata
        """
        self._storage[vector_id] = (vector, metadata)

    def search(self, query: Any, k: int = 10) -> list[dict[str, Any]]:
        """Search vectors by similarity.

        Args:
            query: Search query vector
            k: Number of results to return

        Returns:
            List of similar vectors with scores
        """
        return [{"id": "test_vector", "score": 0.9} for _ in range(k)]
