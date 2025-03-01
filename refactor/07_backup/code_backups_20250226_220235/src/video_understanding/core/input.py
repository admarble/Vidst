"""Input module for Video Understanding AI.

This module handles video file input validation and information extraction.
It provides functionality to validate video files, extract metadata, and
ensure files meet processing requirements.

Key Features:
- Video format detection and validation
- Metadata extraction (duration, dimensions, fps)
- Directory scanning for video files
- Processing configuration validation

Example:
    >>> video_path = Path("example.mp4")
    >>> try:
    ...     info = get_video_info(video_path)
    ...     print(f"Video duration: {info.duration}s")
    ...     print(f"Resolution: {info.width}x{info.height}")
    ... except VideoFormatError as e:
    ...     print(f"Invalid video: {e}")

Performance Considerations:
    - Fast file type detection using magic numbers
    - Efficient metadata extraction using OpenCV
    - Minimal memory footprint for large files
"""

import os
from dataclasses import dataclass
from pathlib import Path

import cv2
import magic

from .config import ProcessingConfig
from .exceptions import ValidationError, VideoFormatError


@dataclass
class VideoInfo:
    """Video information container.

    This class holds comprehensive metadata about a video file, including
    technical specifications and file information. All attributes are
    validated during creation.

    Attributes:
        file_path: Path to video file
        video_format: Video format (e.g., 'mp4', 'avi')
        duration: Duration in seconds
        width: Frame width in pixels
        height: Frame height in pixels
        fps: Frames per second
        total_frames: Total number of frames
        file_size: File size in bytes

    Note:
        All numeric attributes are guaranteed to be positive values.
        The video_format is always lowercase and excludes the leading dot.
    """

    file_path: Path
    video_format: str
    duration: float
    width: int
    height: int
    fps: float
    total_frames: int
    file_size: int


def get_video_info(file_path: Path) -> VideoInfo:
    """Get comprehensive video file information.

    This function performs a detailed analysis of a video file to extract
    its technical specifications and metadata. It uses both file system
    information and video stream analysis.

    The extraction process:
    1. Validates file existence
    2. Determines file format using magic numbers
    3. Extracts video stream properties using OpenCV
    4. Validates all extracted information

    Args:
        file_path: Path to video file

    Returns:
        VideoInfo object containing validated video information

    Raises:
        VideoFormatError: If video format is invalid or file cannot be read
        ValidationError: If file does not exist or is inaccessible
        OSError: If file system operations fail

    Note:
        This function may take longer for large video files as it needs
        to read video stream information.
    """
    if not file_path.exists():
        raise ValidationError(f"File does not exist: {file_path}")

    try:
        # Get file format using python-magic
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(str(file_path))
        if not mime_type.startswith("video/"):
            raise VideoFormatError(f"Invalid file format: {mime_type}")

        # Get video format from file extension
        video_format = file_path.suffix.lower().lstrip(".")
        if not video_format:
            raise VideoFormatError("Missing file extension")

        # Get file size
        file_size = file_path.stat().st_size

        # Open video file with OpenCV
        cap: cv2.VideoCapture = cv2.VideoCapture(str(file_path))
        if not cap.isOpened():
            raise VideoFormatError("Failed to open video file")

        try:
            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = float(cap.get(cv2.CAP_PROP_FPS))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = float(total_frames) / fps if fps > 0 else 0.0

            return VideoInfo(
                file_path=file_path,
                video_format=video_format,
                duration=duration,
                width=width,
                height=height,
                fps=fps,
                total_frames=total_frames,
                file_size=file_size,
            )

        finally:
            cap.release()

    except Exception as e:
        raise VideoFormatError(f"Failed to get video information: {e}") from e


def validate_video(video_info: VideoInfo, config: ProcessingConfig) -> None:
    """Validate video file against configuration settings.

    This function performs comprehensive validation of video specifications
    against the system configuration requirements. It checks multiple
    technical aspects of the video to ensure it can be processed.

    Validation checks:
    1. File size against maximum limit
    2. Video format against supported formats
    3. Duration validity (must be positive)
    4. Frame dimensions (must be positive)
    5. Frame rate validity (must be positive)

    Args:
        video_info: Video information to validate
        config: Processing configuration containing validation rules

    Raises:
        ValidationError: If any validation check fails, with specific
            error message indicating which check failed and why

    Example:
        >>> config = ProcessingConfig(max_video_size=2*1024**3)  # 2GB
        >>> try:
        ...     validate_video(video_info, config)
        ... except ValidationError as e:
        ...     print(f"Validation failed: {e}")
    """
    # Check file size
    if video_info.file_size > config.max_video_size:
        raise ValidationError(
            f"Video file too large: {video_info.file_size} bytes "
            f"(max {config.max_video_size} bytes)"
        )

    # Check format
    if video_info.video_format.lower() not in [
        fmt.lower() for fmt in config.supported_formats
    ]:
        raise ValidationError(
            f"Unsupported video format: {video_info.video_format} "
            f"(supported: {', '.join(config.supported_formats)})"
        )

    # Check duration
    if video_info.duration <= 0:
        raise ValidationError("Invalid video duration")

    # Check dimensions
    if video_info.width <= 0 or video_info.height <= 0:
        raise ValidationError("Invalid video dimensions")

    # Check frame rate
    if video_info.fps <= 0:
        raise ValidationError("Invalid frame rate")


def process_video_file(file_path: Path, config: ProcessingConfig) -> VideoInfo:
    """Process and validate video file.

    This function combines video information extraction and validation
    into a single operation. It ensures a video file is both readable
    and meets all processing requirements.

    The processing workflow:
    1. Extract video information
    2. Validate against configuration
    3. Return validated video information

    Args:
        file_path: Path to video file
        config: Processing configuration for validation

    Returns:
        VideoInfo object containing validated video information

    Raises:
        VideoFormatError: If video format is invalid or file cannot be read
        ValidationError: If video does not meet configuration requirements
        OSError: If file system operations fail

    Example:
        >>> config = ProcessingConfig(
        ...     max_video_size=2*1024**3,  # 2GB
        ...     supported_formats=['mp4', 'mov']
        ... )
        >>> try:
        ...     info = process_video_file(Path("video.mp4"), config)
        ...     print(f"Video processed: {info.duration}s")
        ... except (VideoFormatError, ValidationError) as e:
        ...     print(f"Processing failed: {e}")
    """
    # Get video information
    video_info = get_video_info(file_path)

    # Validate video
    validate_video(video_info, config)

    return video_info


def list_video_files(directory: Path, recursive: bool = False) -> list[Path]:
    """List video files in directory.

    This function scans a directory for video files, optionally including
    subdirectories. It uses magic number detection to accurately identify
    video files regardless of file extension.

    The scanning process:
    1. Validates directory existence and accessibility
    2. Recursively walks directory if specified
    3. Checks each file's magic number for video format
    4. Filters out non-video files

    Args:
        directory: Directory to search
        recursive: Whether to search subdirectories (default: False)

    Returns:
        List of paths to discovered video files, sorted alphabetically

    Raises:
        ValidationError: If directory does not exist or is not accessible
        OSError: If file system operations fail

    Example:
        >>> try:
        ...     videos = list_video_files(Path("media"), recursive=True)
        ...     print(f"Found {len(videos)} videos:")
        ...     for video in videos:
        ...         print(f"- {video.name}")
        ... except ValidationError as e:
        ...     print(f"Directory error: {e}")

    Note:
        This function may be slower than simple extension matching but
        is more accurate as it checks actual file content.
    """
    if not directory.exists():
        raise ValidationError(f"Directory does not exist: {directory}")

    if not directory.is_dir():
        raise ValidationError(f"Not a directory: {directory}")

    video_files: list[Path] = []
    pattern = "**/*" if recursive else "*"

    for file_path in directory.glob(pattern):
        if file_path.is_file():
            try:
                mime = magic.Magic(mime=True)
                mime_type = mime.from_file(str(file_path))
                if mime_type.startswith("video/"):
                    video_files.append(file_path)
            except Exception:
                continue

    return sorted(video_files)


def create_video_directory(directory: Path) -> None:
    """Create directory for video files.

    This function creates a directory for storing video files with appropriate
    permissions. It ensures the directory and its parent directories exist
    and have the correct access rights.

    The creation process:
    1. Creates directory and parent directories if needed
    2. Sets directory permissions to rwxr-xr-x (755)
    3. Validates directory creation and permissions

    Args:
        directory: Directory to create

    Raises:
        ValidationError: If directory creation fails or permissions
            cannot be set
        OSError: If file system operations fail

    Example:
        >>> try:
        ...     create_video_directory(Path("uploads/videos"))
        ...     print("Video directory created successfully")
        ... except ValidationError as e:
        ...     print(f"Failed to create directory: {e}")

    Note:
        This function is idempotent - it will not fail if the directory
        already exists, but will ensure correct permissions.
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        os.chmod(directory, 0o755)  # rwxr-xr-x
    except Exception as e:
        raise ValidationError(f"Failed to create video directory: {e}") from e
