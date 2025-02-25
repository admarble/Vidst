"""Quarantine management for suspicious files.

This module provides functionality for handling files that fail security
validation or are otherwise suspicious.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import magic

from video_understanding.utils.constants import QUARANTINE_FILE_MODE
from video_understanding.utils.exceptions import QuarantineError
from video_understanding.core.upload.directory import DirectoryManager

logger = logging.getLogger(__name__)


class QuarantineManager:
    """Manages quarantined files and their metadata.

    This class handles the quarantine process for suspicious files, including:
    1. Moving files to quarantine
    2. Recording quarantine metadata
    3. Managing quarantine history
    4. Cleaning up quarantined files

    Example:
        >>> manager = QuarantineManager(DirectoryManager(Path("/uploads")))
        >>> try:
        ...     manager.quarantine_file(Path("suspicious.mp4"), "Failed security check")
        ...     print("File quarantined successfully")
        ... except QuarantineError as e:
        ...     print(f"Quarantine failed: {e}")
    """

    def __init__(
        self,
        directory_manager: DirectoryManager,
        test_mode: bool = False,
    ) -> None:
        """Initialize the quarantine manager.

        Args:
            directory_manager: DirectoryManager instance for path operations
            test_mode: Whether to run in test mode (skip actual operations)
        """
        self.directory_manager = directory_manager
        self.test_mode = test_mode
        self._ensure_quarantine_dir()

    def _ensure_quarantine_dir(self) -> None:
        """Ensure quarantine directory exists with proper permissions.

        Raises:
            QuarantineError: If directory setup fails
        """
        if self.test_mode:
            return

        try:
            self.directory_manager.ensure_directory_exists("quarantine")
        except Exception as e:
            raise QuarantineError(f"Failed to setup quarantine directory: {e}")

    def quarantine_file(
        self,
        file_path: Path,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Move a file to quarantine and record metadata.

        Args:
            file_path: Path to the file to quarantine
            reason: Reason for quarantining the file
            metadata: Additional metadata about the file

        Returns:
            Path to the quarantined file

        Raises:
            QuarantineError: If quarantine operation fails
        """
        if self.test_mode:
            return self.directory_manager.get_path(
                "quarantine", f"test_{file_path.name}"
            )

        try:
            # Create timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            quarantine_name = f"{timestamp}_{file_path.name}"

            # Move file to quarantine
            quarantine_path = self.directory_manager.move_file(
                file_path, "quarantine", quarantine_name
            )

            # Set restrictive permissions
            quarantine_path.chmod(QUARANTINE_FILE_MODE)

            # Record metadata
            self._record_metadata(
                quarantine_path,
                reason,
                metadata or {},
            )

            logger.warning(
                f"File quarantined: {file_path} -> {quarantine_path}\n"
                f"Reason: {reason}"
            )

            return quarantine_path

        except Exception as e:
            raise QuarantineError(f"Failed to quarantine file: {e}")

    def _record_metadata(
        self,
        quarantine_path: Path,
        reason: str,
        metadata: Dict[str, Any],
    ) -> None:
        """Record metadata for a quarantined file.

        Args:
            quarantine_path: Path to the quarantined file
            reason: Reason for quarantining
            metadata: Additional metadata

        Raises:
            QuarantineError: If metadata recording fails
        """
        try:
            # Create metadata file path
            meta_path = quarantine_path.with_suffix(".meta")

            # Gather file information
            file_info = {
                "original_path": str(quarantine_path),
                "quarantine_time": datetime.now().isoformat(),
                "reason": reason,
                "file_info": {
                    "size": quarantine_path.stat().st_size,
                    "mime_type": magic.from_file(str(quarantine_path), mime=True),
                    "mode": oct(quarantine_path.stat().st_mode & 0o777),
                },
                **metadata,
            }

            # Write metadata file
            with open(meta_path, "w") as f:
                json.dump(file_info, f, indent=2)

            # Set restrictive permissions on metadata file
            meta_path.chmod(QUARANTINE_FILE_MODE)

            logger.debug(f"Recorded metadata for quarantined file: {meta_path}")

        except Exception as e:
            raise QuarantineError(f"Failed to record metadata: {e}")

    def get_quarantine_info(self, file_path: Path) -> Dict[str, Any]:
        """Get information about a quarantined file.

        Args:
            file_path: Path to the quarantined file

        Returns:
            Dictionary containing quarantine information

        Raises:
            QuarantineError: If information cannot be retrieved
        """
        try:
            meta_path = file_path.with_suffix(".meta")
            if not meta_path.exists():
                raise QuarantineError(f"No metadata found for {file_path}")

            with open(meta_path) as f:
                return json.load(f)

        except Exception as e:
            raise QuarantineError(f"Failed to get quarantine info: {e}")

    def list_quarantined_files(
        self,
        include_metadata: bool = False,
    ) -> Dict[str, Any]:
        """List all quarantined files.

        Args:
            include_metadata: Whether to include full metadata

        Returns:
            Dictionary mapping filenames to quarantine information

        Raises:
            QuarantineError: If listing fails
        """
        try:
            quarantine_dir = self.directory_manager.get_path("quarantine")
            if not quarantine_dir.exists():
                return {}

            quarantined = {}
            for meta_file in quarantine_dir.glob("*.meta"):
                try:
                    with open(meta_file) as f:
                        info = json.load(f)
                        if include_metadata:
                            quarantined[meta_file.stem] = info
                        else:
                            quarantined[meta_file.stem] = {
                                "quarantine_time": info["quarantine_time"],
                                "reason": info["reason"],
                            }
                except Exception as e:
                    logger.warning(f"Failed to read metadata {meta_file}: {e}")

            return quarantined

        except Exception as e:
            raise QuarantineError(f"Failed to list quarantined files: {e}")

    def cleanup_quarantine(self, max_age_days: int = 30) -> None:
        """Clean up old quarantined files.

        Args:
            max_age_days: Maximum age of files to keep

        Raises:
            QuarantineError: If cleanup fails
        """
        if self.test_mode:
            return

        try:
            quarantine_dir = self.directory_manager.get_path("quarantine")
            if not quarantine_dir.exists():
                return

            now = datetime.now()
            for meta_file in quarantine_dir.glob("*.meta"):
                try:
                    # Read metadata
                    with open(meta_file) as f:
                        info = json.load(f)

                    # Check age
                    quarantine_time = datetime.fromisoformat(
                        info["quarantine_time"]
                    )
                    age_days = (now - quarantine_time).days

                    if age_days > max_age_days:
                        # Remove quarantined file
                        quarantine_file = Path(info["original_path"])
                        if quarantine_file.exists():
                            quarantine_file.unlink()

                        # Remove metadata file
                        meta_file.unlink()

                        logger.info(
                            f"Removed quarantined file: {quarantine_file} "
                            f"(age: {age_days} days)"
                        )

                except Exception as e:
                    logger.warning(
                        f"Failed to cleanup {meta_file}: {e}"
                    )

        except Exception as e:
            raise QuarantineError(f"Failed to cleanup quarantine: {e}")

    def restore_file(
        self,
        quarantine_path: Path,
        destination: Path,
    ) -> Path:
        """Restore a quarantined file.

        Args:
            quarantine_path: Path to the quarantined file
            destination: Where to restore the file

        Returns:
            Path to the restored file

        Raises:
            QuarantineError: If restoration fails
        """
        if self.test_mode:
            return destination

        try:
            # Verify file is quarantined
            if not str(quarantine_path.resolve()).startswith(
                str(self.directory_manager.get_path("quarantine").resolve())
            ):
                raise QuarantineError(
                    f"File is not in quarantine: {quarantine_path}"
                )

            # Move file to destination
            restored_path = self.directory_manager.move_file(
                quarantine_path,
                str(destination.parent),
                destination.name,
            )

            # Remove metadata file
            meta_path = quarantine_path.with_suffix(".meta")
            if meta_path.exists():
                meta_path.unlink()

            logger.info(
                f"Restored quarantined file: {quarantine_path} -> {restored_path}"
            )

            return restored_path

        except Exception as e:
            raise QuarantineError(f"Failed to restore file: {e}")
