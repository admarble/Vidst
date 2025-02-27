from pathlib import Path

class ProcessingConfig:
    max_video_size: int
    supported_formats: list[str]
    min_scene_length: float
    max_scenes: int
    concurrent_jobs: int
    memory_limit: int

    def __init__(self) -> None: ...
    def validate(self) -> None: ...

class VideoConfig:
    upload_directory: Path
    max_file_size: int
    supported_formats: set[str]
    min_scene_length: float
    max_scenes: int
    max_concurrent_jobs: int
    memory_limit: int
    cache_ttl: int
    vector_cache_size: int

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
    ) -> None: ...
    def validate(self) -> None: ...
    def is_format_supported(self, format_: str) -> bool: ...
    def is_file_size_valid(self, size: int) -> bool: ...
