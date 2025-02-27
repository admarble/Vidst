"""Security validation for video uploads.

This module provides security validation functionality for video uploads,
including path traversal prevention, permission checks, and malicious
content detection.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from video_understanding.utils.constants import (
    UPLOAD_DIR_MODE,
    UPLOAD_FILE_MODE,
)
from video_understanding.utils.exceptions import SecurityError
from video_understanding.core.upload.directory import DirectoryManager

logger = logging.getLogger(__name__)


class SecurityValidator:
    """Validates security aspects of video uploads.

    This class handles security validation for video uploads, including:
    1. Path traversal prevention
    2. File permission checks
    3. Ownership validation
    4. Basic malicious content detection

    Example:
        >>> validator = SecurityValidator(DirectoryManager(Path("/uploads")))
        >>> try:
        ...     validator.validate_file(Path("video.mp4"))
        ...     print("File passed security checks")
        ... except SecurityError as e:
        ...     print(f"Security check failed: {e}")
    """

    def __init__(
        self,
        directory_manager: DirectoryManager,
        test_mode: bool = False,
    ) -> None:
        """Initialize the security validator.

        Args:
            directory_manager: DirectoryManager instance for path operations
            test_mode: Whether to run in test mode (skip actual validation)
        """
        self.directory_manager = directory_manager
        self.test_mode = test_mode

    def validate_file(self, file_path: Path) -> None:
        """Perform comprehensive security validation on a file.

        Args:
            file_path: Path to the file to validate

        Raises:
            SecurityError: If security validation fails
        """
        if self.test_mode:
            return

        try:
            # Check file existence and basic access
            self._validate_file_access(file_path)

            # Check file permissions
            self._validate_permissions(file_path)

            # Check file ownership
            self._validate_ownership(file_path)

            # Check for path traversal
            self._validate_path(file_path)

            # Check for suspicious content
            self._check_suspicious_content(file_path)

            logger.debug(f"Security validation passed for {file_path}")

        except SecurityError:
            raise
        except Exception as e:
            raise SecurityError(f"Security validation failed: {e}")

    def _validate_file_access(self, file_path: Path) -> None:
        """Validate basic file access.

        Args:
            file_path: Path to the file

        Raises:
            SecurityError: If file access validation fails
        """
        try:
            if not file_path.exists():
                raise SecurityError(f"File does not exist: {file_path}")

            if not file_path.is_file():
                raise SecurityError(f"Path is not a regular file: {file_path}")

            if not os.access(str(file_path), os.R_OK):
                raise SecurityError(f"File is not readable: {file_path}")

        except SecurityError:
            raise
        except Exception as e:
            raise SecurityError(f"File access validation failed: {e}")

    def _validate_permissions(self, file_path: Path) -> None:
        """Validate file permissions.

        Args:
            file_path: Path to the file

        Raises:
            SecurityError: If permission validation fails
        """
        try:
            # Get file permissions
            file_stat = file_path.stat()
            file_mode = file_stat.st_mode & 0o777

            # Check if file is world-writable
            if file_mode & 0o002:
                raise SecurityError(
                    f"File has unsafe permissions (world-writable): {file_path}"
                )

            # Check parent directory permissions
            parent_stat = file_path.parent.stat()
            parent_mode = parent_stat.st_mode & 0o777

            # Check if parent directory is world-writable
            if parent_mode & 0o002:
                raise SecurityError(
                    f"Parent directory has unsafe permissions: {file_path.parent}"
                )

            logger.debug(
                f"Permission validation passed for {file_path} "
                f"(mode: {oct(file_mode)})"
            )

        except SecurityError:
            raise
        except Exception as e:
            raise SecurityError(f"Permission validation failed: {e}")

    def _validate_ownership(self, file_path: Path) -> None:
        """Validate file ownership.

        Args:
            file_path: Path to the file

        Raises:
            SecurityError: If ownership validation fails
        """
        try:
            # Get file ownership
            file_stat = file_path.stat()
            file_uid = file_stat.st_uid
            file_gid = file_stat.st_gid

            # Get current process ownership
            current_uid = os.getuid()
            current_gid = os.getgid()

            # Check if file is owned by current user or group
            if file_uid != current_uid and file_gid != current_gid:
                raise SecurityError(
                    f"File has invalid ownership: uid={file_uid}, gid={file_gid}"
                )

            logger.debug(
                f"Ownership validation passed for {file_path} "
                f"(uid: {file_uid}, gid: {file_gid})"
            )

        except SecurityError:
            raise
        except Exception as e:
            raise SecurityError(f"Ownership validation failed: {e}")

    def _validate_path(self, file_path: Path) -> None:
        """Validate file path for traversal attempts.

        Args:
            file_path: Path to the file

        Raises:
            SecurityError: If path validation fails
        """
        try:
            # Resolve the real path
            real_path = file_path.resolve()

            # Check if path is within base directory
            if not str(real_path).startswith(
                str(self.directory_manager.base_dir.resolve())
            ):
                raise SecurityError(
                    f"File path {file_path} resolves outside base directory"
                )

            # Check for suspicious path components
            path_str = str(real_path)
            suspicious_patterns = ["../", "..\\", "~", "$"]
            for pattern in suspicious_patterns:
                if pattern in path_str:
                    raise SecurityError(
                        f"Suspicious path pattern detected: {pattern}"
                    )

            logger.debug(f"Path validation passed for {file_path}")

        except SecurityError:
            raise
        except Exception as e:
            raise SecurityError(f"Path validation failed: {e}")

    def _check_suspicious_content(self, file_path: Path) -> None:
        """Check for suspicious content patterns.

        Args:
            file_path: Path to the file

        Raises:
            SecurityError: If suspicious content is detected
        """
        try:
            # TODO: Implement more thorough malicious content detection
            # For now, just check basic file properties

            # Check file size
            if file_path.stat().st_size == 0:
                raise SecurityError("Empty file detected")

            # Check if file is a symlink
            if file_path.is_symlink():
                raise SecurityError("Symbolic links are not allowed")

            logger.debug(f"Content validation passed for {file_path}")

        except SecurityError:
            raise
        except Exception as e:
            raise SecurityError(f"Content validation failed: {e}")

    def secure_file(self, file_path: Path) -> None:
        """Apply secure permissions to a file.

        Args:
            file_path: Path to the file

        Raises:
            SecurityError: If securing the file fails
        """
        if self.test_mode:
            return

        try:
            # Set secure file permissions
            os.chmod(str(file_path), UPLOAD_FILE_MODE)

            # Set secure directory permissions
            os.chmod(str(file_path.parent), UPLOAD_DIR_MODE)

            logger.debug(f"Applied secure permissions to {file_path}")

        except Exception as e:
            raise SecurityError(f"Failed to secure file: {e}")

    def validate_and_secure(self, file_path: Path) -> None:
        """Validate and secure a file in one operation.

        Args:
            file_path: Path to the file

        Raises:
            SecurityError: If validation or securing fails
        """
        self.validate_file(file_path)
        self.secure_file(file_path)
