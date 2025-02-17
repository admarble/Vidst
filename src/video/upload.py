"""Video upload functionality."""

import os
import shutil
from pathlib import Path
from uuid import uuid4

from src.core.config import VideoConfig
from src.core.exceptions import FileValidationError
from src.models.video import Video


class VideoUploader:
    """Handles video file uploads and validation."""

    def __init__(self, config: VideoConfig):
        """Initialize uploader with configuration."""
        self.config = config

    def validate_file(self, file_path: str) -> bool:
        """Validate video file.

        Args:
            file_path: Path to video file

        Returns:
            True if file is valid

        Raises:
            FileValidationError: If file is invalid
        """
        path = Path(file_path)

        if not path.exists():
            raise FileValidationError("File does not exist")

        if path.suffix.lower()[1:] not in {
            fmt.lower() for fmt in self.config.SUPPORTED_FORMATS
        }:
            raise FileValidationError("Unsupported format")

        if path.stat().st_size == 0:
            raise FileValidationError("File is empty")

        if path.stat().st_size > self.config.MAX_FILE_SIZE:
            raise FileValidationError("File exceeds maximum size")

        return True

    def upload(self, file_path: str) -> Video:
        """Upload video file.

        Args:
            file_path: Path to video file

        Returns:
            Video: Video model instance
        """
        self.validate_file(file_path)
        path = Path(file_path)

        # Generate unique ID and create directory
        video_id = uuid4()
        upload_dir = self.config.UPLOAD_DIRECTORY / str(video_id)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Copy file to upload directory
        dest_path = upload_dir / path.name
        shutil.copy2(path, dest_path)

        return Video.from_path(dest_path, video_id)
