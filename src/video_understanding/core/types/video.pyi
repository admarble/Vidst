from typing import Literal
from uuid import UUID

class VideoFile:
    filename: str
    file_path: str
    format: str
    file_size: int
    def __init__(
        self, filename: str, file_path: str, format: str, file_size: int
    ) -> None: ...

class VideoProcessingStatus:
    status: Literal["pending", "processing", "completed", "failed"]
    def __init__(
        self, status: Literal["pending", "processing", "completed", "failed"]
    ) -> None: ...

class Video:
    id: UUID
    file_info: VideoFile
    processing: VideoProcessingStatus
    def __init__(
        self, id: UUID, file_info: VideoFile, processing: VideoProcessingStatus
    ) -> None: ...
