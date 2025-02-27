"""Context management for upload operations.

This module provides context managers for handling file operations and cleanup
during video upload processing.
"""

import logging
import shutil
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, Generator, List, Optional, Any, TypeVar, Union
import tempfile

from video_understanding.utils.exceptions import ProcessingError
from video_understanding.models.video import Video, ProcessingStatus
from video_understanding.core.upload.progress import ProgressTracker

logger = logging.getLogger(__name__)

T = TypeVar('T')  # Generic type for resources


class UploadContext:
    """Manages context for video upload processing."""

    def __init__(self, video: Union[Video, Path], progress_tracker: Optional[ProgressTracker] = None):
        """Initialize upload context.

        Args:
            video: Video object or path to uploaded video file
            progress_tracker: Optional progress tracking
        """
        self.video = video if isinstance(video, Video) else None
        self.file_path = video.file_info.file_path if isinstance(video, Video) else video
        self.progress_tracker = progress_tracker
        self.start_time = datetime.now()
        self.scenes: List[Dict[str, Any]] = []
        self.text_content: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {
            "filename": video.file_info.filename if isinstance(video, Video) else self.file_path.name,
            "size_bytes": video.file_info.file_size if isinstance(video, Video) else self.file_path.stat().st_size,
            "upload_time": self.start_time.isoformat()
        }
        self.temp_files: List[Path] = []
        self.temp_dirs: List[Path] = []
        self._resources: Dict[str, Any] = {}

    def add_scenes(self, scenes: List[Dict[str, Any]]) -> None:
        """Add detected scenes to context.

        Args:
            scenes: List of scene information dictionaries
        """
        self.scenes.extend(scenes)
        self.metadata["scene_count"] = len(self.scenes)

    def add_text(self, text_content: List[Dict[str, Any]]) -> None:
        """Add extracted text to context.

        Args:
            text_content: List of text extraction results
        """
        self.text_content.extend(text_content)
        self.metadata["text_blocks"] = len(self.text_content)

    def get_results(self) -> Dict[str, Any]:
        """Get processing results.

        Returns:
            Dictionary containing all processing results
        """
        end_time = datetime.now()
        processing_time = (end_time - self.start_time).total_seconds()

        return {
            "metadata": self.metadata,
            "scenes": self.scenes,
            "text_content": self.text_content,
            "processing_time": processing_time
        }

    def __enter__(self) -> 'UploadContext':
        """Enter the context.

        Returns:
            Self for use in with statement
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context and clean up resources.

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred
        """
        try:
            self.cleanup()
        except Exception as e:
            logger.error(f"Failed to cleanup upload context: {e}")

        if exc_type is not None and self.progress_tracker and self.video:
            # Log error and update progress on exception
            self.progress_tracker.mark_stage_error(
                self.video.processing.status,
                str(exc_val),
                error_type=exc_type.__name__,
            )

    def track_temp_file(self, file_path: Path) -> None:
        """Track a temporary file for cleanup.

        Args:
            file_path: Path to temporary file
        """
        self.temp_files.append(file_path)
        logger.debug(f"Tracking temporary file: {file_path}")

    def track_temp_dir(self, dir_path: Path) -> None:
        """Track a temporary directory for cleanup.

        Args:
            dir_path: Path to temporary directory
        """
        self.temp_dirs.append(dir_path)
        logger.debug(f"Tracking temporary directory: {dir_path}")

    def cleanup(self) -> None:
        """Clean up all temporary files and directories."""
        # Clean up temporary files
        for file_path in self.temp_files:
            try:
                if file_path.exists():
                    file_path.unlink()
                    logger.debug(f"Removed temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {file_path}: {e}")

        # Clean up temporary directories
        for dir_path in reversed(self.temp_dirs):  # Reverse to handle nested dirs
            try:
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                    logger.debug(f"Removed temporary directory: {dir_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary directory {dir_path}: {e}")

        # Clear tracking lists
        self.temp_files.clear()
        self.temp_dirs.clear()

    def create_temp_file(self, suffix: str = "") -> Path:
        """Create a temporary file.

        Args:
            suffix: Optional file suffix

        Returns:
            Path to temporary file
        """
        temp_file = Path(tempfile.mktemp(suffix=suffix))
        self.temp_files.append(temp_file)
        self.track_temp_file(temp_file)
        return temp_file

    def create_temp_dir(self) -> Path:
        """Create a temporary directory.

        Returns:
            Path to temporary directory
        """
        temp_dir = Path(tempfile.mkdtemp())
        self.temp_dirs.append(temp_dir)
        self.track_temp_dir(temp_dir)
        return temp_dir

    @contextmanager
    def temp_file(self, name: str, content: bytes = b"") -> Generator[Path, None, None]:
        """Context manager for temporary file.

        Args:
            name: Name for the temporary file
            content: Optional initial content

        Yields:
            Path to the temporary file

        Example:
            >>> with context.temp_file("data.txt", b"content") as temp:
            ...     process_file(temp)
            >>> # File is automatically cleaned up
        """
        temp_path = None
        try:
            temp_path = self.create_temp_file(name)
            yield temp_path
        finally:
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file {temp_path}: {e}")

    @contextmanager
    def temp_dir(self, name: str) -> Generator[Path, None, None]:
        """Context manager for temporary directory.

        Args:
            name: Name for the temporary directory

        Yields:
            Path to the temporary directory

        Example:
            >>> with context.temp_dir("workspace") as temp:
            ...     process_files(temp)
            >>> # Directory is automatically cleaned up
        """
        temp_dir = None
        try:
            temp_dir = self.create_temp_dir()
            yield temp_dir
        finally:
            if temp_dir and temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f"Failed to remove temporary directory {temp_dir}: {e}")

    def add_resource(self, key: str, resource: T) -> None:
        """Track an arbitrary resource.

        Args:
            key: Identifier for the resource
            resource: Resource to track
        """
        self._resources[key] = resource

    def get_resource(self, key: str) -> Optional[T]:
        """Get a tracked resource.

        Args:
            key: Resource identifier

        Returns:
            Resource if found, None otherwise
        """
        return self._resources.get(key)

    def remove_resource(self, key: str) -> None:
        """Remove a tracked resource.

        Args:
            key: Resource identifier
        """
        self._resources.pop(key, None)

    @property
    def elapsed_time(self) -> float:
        """Get elapsed processing time in seconds.

        Returns:
            Elapsed time in seconds
        """
        return (datetime.now() - self.start_time).total_seconds()
