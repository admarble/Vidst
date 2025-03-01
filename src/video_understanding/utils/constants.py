"""Constants for video understanding system.

This module contains shared constants used across the video understanding system,
particularly for video upload and processing functionality.
"""

from pathlib import Path
from typing import Dict, Final

# File format constants
VALID_VIDEO_FORMATS: Final[Dict[str, str]] = {
    "video/mp4": ".mp4",
    "video/x-msvideo": ".avi",
    "video/quicktime": ".mov",
}

# Size limits
MAX_FILE_SIZE: Final[int] = 2 * 1024 * 1024 * 1024  # 2GB

# Directory structure
UPLOAD_SUBDIRS: Final[tuple[str, ...]] = (
    "temp",        # Temporary storage for uploads in progress
    "processing",  # Storage for files being processed
    "completed",   # Storage for successfully processed files
    "failed",      # Storage for failed uploads and processing
    "quarantine",  # Storage for suspicious files
    "logs",        # Upload and processing logs
)

# File permissions
UPLOAD_DIR_MODE: Final[int] = 0o750    # rwxr-x---
UPLOAD_FILE_MODE: Final[int] = 0o640   # rw-r-----
QUARANTINE_FILE_MODE: Final[int] = 0o440  # r--r-----

# Processing constants
MAX_CONCURRENT_JOBS: Final[int] = 3
MEMORY_LIMIT_PER_JOB: Final[int] = 4 * 1024 * 1024 * 1024  # 4GB
CACHE_TTL: Final[int] = 24 * 60 * 60  # 24 hours in seconds

# Video processing constants
MIN_SCENE_LENGTH: Final[float] = 2.0  # seconds
MAX_SCENES_PER_VIDEO: Final[int] = 500
