import os
import shutil
from pathlib import Path
from typing import Tuple

from ..core.config import VideoConfig
from ..core.exceptions import FileValidationError
from ..models.video import Video


class VideoUploader:
    def __init__(self, config: VideoConfig):
        self.config = config
        self.upload_dir = Path(config.UPLOAD_DIRECTORY)
        self.upload_dir.mkdir(exist_ok=True)

    def validate_file(self, file_path: str) -> Tuple[int, str]:
        """
        Validate file size and format
        Returns: (file_size, format)
        """
        if not os.path.exists(file_path):
            raise FileValidationError("File does not exist")

        file_size = os.path.getsize(file_path)
        max_size = self.config.MAX_FILE_SIZE
        if file_size > max_size:
            msg = f"File size exceeds maximum limit of {max_size} bytes"
            raise FileValidationError(msg)

        file_format = Path(file_path).suffix[1:].upper()
        supported = self.config.SUPPORTED_FORMATS
        if file_format not in supported:
            msg = f"Unsupported format. Supported formats: {supported}"
            raise FileValidationError(msg)

        return file_size, file_format

    def upload(self, file_path: str) -> Video:
        """
        Handle file upload and create Video object
        """
        file_size, file_format = self.validate_file(file_path)

        video = Video(
            filename=os.path.basename(file_path),
            file_size=file_size,
            format=file_format
        )

        # Create upload directory with video ID
        video_dir = self.upload_dir / str(video.id)
        video_dir.mkdir(exist_ok=True)

        # Copy file to upload directory
        dest_path = video_dir / video.filename
        shutil.copy2(file_path, dest_path)

        return video
