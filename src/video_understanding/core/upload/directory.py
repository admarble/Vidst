"""Directory management for video upload system.

This module provides functionality for managing the directory structure and
permissions for the video upload system.
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Optional

from video_understanding.utils.constants import (
    UPLOAD_SUBDIRS,
    UPLOAD_DIR_MODE,
    UPLOAD_FILE_MODE,
)
from video_understanding.utils.exceptions import StorageError

logger = logging.getLogger(__name__)


class DirectoryManager:
    """Manages directory structure and permissions for video uploads.

    This class handles the creation and maintenance of the directory structure
    required for video upload processing, including setting appropriate
    permissions and handling cleanup operations.

    Attributes:
        base_dir: Base directory for all upload operations
        test_mode: Whether running in test mode (skips actual file operations)

    Example:
        >>> manager = DirectoryManager(Path("/uploads"))
        >>> manager.initialize_directories()
        >>> manager.ensure_directory_exists("processing")
    """

    def __init__(
        self,
        base_dir: Path,
        test_mode: bool = False,
    ) -> None:
        """Initialize the directory manager.

        Args:
            base_dir: Base directory for all upload operations
            test_mode: Whether to run in test mode (skip file operations)

        Raises:
            StorageError: If base directory is invalid or inaccessible
        """
        self.base_dir = base_dir
        self.test_mode = test_mode
        self._validate_base_dir()

    def _validate_base_dir(self) -> None:
        """Validate the base directory.

        Ensures the base directory is valid and accessible.

        Raises:
            StorageError: If directory is invalid or inaccessible
        """
        if self.test_mode:
            return

        try:
            if not self.base_dir.exists():
                self.base_dir.mkdir(parents=True)

            if not os.access(str(self.base_dir), os.W_OK):
                raise StorageError(f"Base directory {self.base_dir} is not writable")

            # Set secure permissions
            os.chmod(str(self.base_dir), UPLOAD_DIR_MODE)

        except OSError as e:
            raise StorageError(f"Failed to validate base directory: {e}")

    def initialize_directories(self) -> None:
        """Initialize the complete directory structure.

        Creates all necessary subdirectories with appropriate permissions.

        Raises:
            StorageError: If directory creation fails
        """
        if self.test_mode:
            return

        try:
            for subdir in UPLOAD_SUBDIRS:
                self.ensure_directory_exists(subdir)

            logger.info(f"Initialized directory structure at {self.base_dir}")

        except Exception as e:
            raise StorageError(f"Failed to initialize directory structure: {e}")

    def ensure_directory_exists(self, subdir: str) -> Path:
        """Ensure a subdirectory exists with correct permissions.

        Args:
            subdir: Name of the subdirectory to ensure exists

        Returns:
            Path to the ensured directory

        Raises:
            StorageError: If directory cannot be created or secured
        """
        if self.test_mode:
            return self.base_dir / subdir

        try:
            dir_path = self.base_dir / subdir
            dir_path.mkdir(exist_ok=True)
            os.chmod(str(dir_path), UPLOAD_DIR_MODE)

            logger.debug(f"Ensured directory exists: {dir_path}")
            return dir_path

        except OSError as e:
            raise StorageError(f"Failed to ensure directory exists: {e}")

    def get_path(self, subdir: str, filename: Optional[str] = None) -> Path:
        """Get path within the directory structure.

        Args:
            subdir: Subdirectory name
            filename: Optional filename to append to path

        Returns:
            Complete path including base directory

        Raises:
            StorageError: If path would be invalid
        """
        try:
            path = self.base_dir / subdir
            if filename:
                path = path / filename

            # Ensure path is within base directory (prevent path traversal)
            if not str(path.resolve()).startswith(str(self.base_dir.resolve())):
                raise StorageError(f"Invalid path: {path} outside base directory")

            return path

        except Exception as e:
            raise StorageError(f"Failed to get valid path: {e}")

    def move_file(
        self,
        source: Path,
        dest_subdir: str,
        filename: Optional[str] = None,
    ) -> Path:
        """Move a file to a subdirectory.

        Args:
            source: Source file path
            dest_subdir: Destination subdirectory
            filename: Optional new filename

        Returns:
            Path to the moved file

        Raises:
            StorageError: If file movement fails
        """
        if self.test_mode:
            return self.get_path(dest_subdir, filename or source.name)

        try:
            # Ensure source exists
            if not source.exists():
                raise StorageError(f"Source file does not exist: {source}")

            # Get destination path
            dest = self.get_path(dest_subdir, filename or source.name)
            dest.parent.mkdir(exist_ok=True)

            # Move file
            shutil.move(str(source), str(dest))
            os.chmod(str(dest), UPLOAD_FILE_MODE)

            logger.debug(f"Moved file: {source} -> {dest}")
            return dest

        except Exception as e:
            raise StorageError(f"Failed to move file: {e}")

    def cleanup_empty_dirs(self, subdir: str) -> None:
        """Remove empty directories within a subdirectory.

        Args:
            subdir: Subdirectory to clean up

        Raises:
            StorageError: If cleanup fails
        """
        if self.test_mode:
            return

        try:
            path = self.get_path(subdir)
            if not path.exists():
                return

            # Walk directory tree bottom-up
            for dirpath, dirnames, filenames in os.walk(str(path), topdown=False):
                if not dirnames and not filenames and dirpath != str(path):
                    try:
                        Path(dirpath).rmdir()
                        logger.debug(f"Removed empty directory: {dirpath}")
                    except OSError:
                        pass  # Directory might have contents now, skip it

        except Exception as e:
            raise StorageError(f"Failed to cleanup empty directories: {e}")

    def remove_file(self, subdir: str, filename: str) -> None:
        """Remove a file from a subdirectory.

        Args:
            subdir: Subdirectory containing the file
            filename: Name of file to remove

        Raises:
            StorageError: If file removal fails
        """
        if self.test_mode:
            return

        try:
            file_path = self.get_path(subdir, filename)
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Removed file: {file_path}")

        except Exception as e:
            raise StorageError(f"Failed to remove file: {e}")
