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

from video_understanding.utils.exceptions import ProcessingError
from video_understanding.models.video import Video, ProcessingStatus
from video_understanding.core.upload.progress import ProgressTracker

logger = logging.getLogger(__name__)

T = TypeVar('T')  # Generic type for resources


class UploadContext:
    """Context manager for upload operations.

    This class manages the lifecycle of temporary files and resources during
    upload processing, ensuring proper cleanup in both success and failure cases.

    Example:
        >>> with UploadContext(video) as context:
        ...     temp_file = context.create_temp_file("video.mp4")
        ...     process_file(temp_file)
        >>> # All temporary files are cleaned up
    """

    def __init__(
        self,
        video: Video,
        progress_tracker: Optional[ProgressTracker] = None,
    ) -> None:
        """Initialize the upload context.

        Args:
            video: Video being processed
            progress_tracker: Optional progress tracker
        """
        self.video = video
        self.progress_tracker = progress_tracker
        self.temp_files: List[Path] = []
        self.temp_dirs: List[Path] = []
        self._start_time = datetime.now()
        self._resources: Dict[str, Any] = {}

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

        if exc_type is not None:
            # Log error and update progress on exception
            if self.progress_tracker:
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

    def create_temp_file(self, name: str, content: bytes = b"") -> Path:
        """Create a temporary file.

        Args:
            name: Name for the temporary file
            content: Optional initial content

        Returns:
            Path to the created temporary file

        Raises:
            ProcessingError: If file creation fails
        """
        try:
            # Create parent directories if needed
            temp_dir = Path("/tmp/video_upload")
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Create unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_path = temp_dir / f"{timestamp}_{name}"

            # Write content
            temp_path.write_bytes(content)
            self.track_temp_file(temp_path)

            return temp_path

        except Exception as e:
            raise ProcessingError(f"Failed to create temporary file: {e}")

    def create_temp_dir(self, name: str) -> Path:
        """Create a temporary directory.

        Args:
            name: Name for the temporary directory

        Returns:
            Path to the created temporary directory

        Raises:
            ProcessingError: If directory creation fails
        """
        try:
            # Create parent directories if needed
            temp_base = Path("/tmp/video_upload")
            temp_base.mkdir(parents=True, exist_ok=True)

            # Create unique directory name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = temp_base / f"{timestamp}_{name}"
            temp_dir.mkdir(parents=True)

            self.track_temp_dir(temp_dir)
            return temp_dir

        except Exception as e:
            raise ProcessingError(f"Failed to create temporary directory: {e}")

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
            temp_path = self.create_temp_file(name, content)
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
            temp_dir = self.create_temp_dir(name)
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
        return (datetime.now() - self._start_time).total_seconds()
