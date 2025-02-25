"""Video integrity checking functionality.

This module provides functionality for validating video file integrity,
including format validation, frame validation, and codec compatibility checks.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

import cv2
import magic

from video_understanding.utils.constants import (
    VALID_VIDEO_FORMATS,
    MIN_SCENE_LENGTH,
    MAX_SCENES_PER_VIDEO,
)
from video_understanding.utils.exceptions import VideoIntegrityError, VideoFormatError
from video_understanding.models.video import VideoMetadata

logger = logging.getLogger(__name__)


class VideoIntegrityChecker:
    """Checks video file integrity and extracts metadata.

    This class provides comprehensive validation of video files, including:
    1. Format validation using MIME type detection
    2. Frame validation and sampling
    3. Codec compatibility verification
    4. Metadata extraction

    Example:
        >>> checker = VideoIntegrityChecker()
        >>> try:
        ...     metadata = checker.check_video("video.mp4")
        ...     print(f"Valid video: {metadata.duration}s, {metadata.width}x{metadata.height}")
        ... except VideoIntegrityError as e:
        ...     print(f"Invalid video: {e}")
    """

    def __init__(self, test_mode: bool = False):
        """Initialize the integrity checker.

        Args:
            test_mode: Whether to run in test mode (skip actual validation)
        """
        self.test_mode = test_mode

    def check_video(self, file_path: Path) -> VideoMetadata:
        """Perform comprehensive video integrity check.

        Args:
            file_path: Path to the video file to check

        Returns:
            VideoMetadata containing extracted video information

        Raises:
            VideoFormatError: If video format is invalid
            VideoIntegrityError: If video fails integrity checks
        """
        if self.test_mode:
            # Return dummy metadata in test mode
            return VideoMetadata(
                duration=10.0,
                width=1920,
                height=1080,
                fps=30.0,
                codec="h264",
                total_frames=300,
            )

        try:
            # Check format first
            self._validate_format(file_path)

            # Extract metadata and validate frames
            metadata = self._extract_metadata(file_path)

            # Validate extracted metadata
            self._validate_metadata(metadata)

            return metadata

        except (VideoFormatError, VideoIntegrityError):
            raise
        except Exception as e:
            raise VideoIntegrityError(f"Failed to validate video: {e}")

    def _validate_format(self, file_path: Path) -> None:
        """Validate video format using MIME type detection.

        Args:
            file_path: Path to the video file

        Raises:
            VideoFormatError: If format is invalid or unsupported
        """
        try:
            mime_type = magic.from_file(str(file_path), mime=True)
            if mime_type not in VALID_VIDEO_FORMATS:
                raise VideoFormatError(
                    f"Invalid video format: {mime_type}. "
                    f"Supported formats: {', '.join(VALID_VIDEO_FORMATS.values())}"
                )

            # Check if extension matches MIME type
            expected_ext = VALID_VIDEO_FORMATS[mime_type]
            actual_ext = file_path.suffix.lower()
            if actual_ext != expected_ext:
                raise VideoFormatError(
                    f"File extension {actual_ext} does not match format {mime_type}"
                )

        except magic.MagicException as e:
            raise VideoFormatError(f"Failed to detect file format: {e}")
        except Exception as e:
            raise VideoFormatError(f"Format validation failed: {e}")

    def _extract_metadata(self, file_path: Path) -> VideoMetadata:
        """Extract metadata from video file.

        Args:
            file_path: Path to the video file

        Returns:
            VideoMetadata containing extracted information

        Raises:
            VideoIntegrityError: If metadata extraction fails
        """
        try:
            cap = cv2.VideoCapture(str(file_path))
            if not cap.isOpened():
                raise VideoIntegrityError("Failed to open video file")

            try:
                # Extract basic properties
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                codec_int = int(cap.get(cv2.CAP_PROP_FOURCC))

                # Convert codec to string
                codec = "".join([
                    chr((codec_int >> 8 * i) & 0xFF)
                    for i in range(4)
                ]).strip()

                # Calculate duration
                duration = frame_count / fps if fps > 0 else 0.0

                return VideoMetadata(
                    duration=duration,
                    width=width,
                    height=height,
                    fps=fps,
                    codec=codec,
                    total_frames=frame_count,
                )

            finally:
                cap.release()

        except cv2.error as e:
            raise VideoIntegrityError(f"OpenCV error: {e}")
        except Exception as e:
            raise VideoIntegrityError(f"Failed to extract metadata: {e}")

    def _validate_metadata(self, metadata: VideoMetadata) -> None:
        """Validate extracted metadata against requirements.

        Args:
            metadata: Extracted video metadata

        Raises:
            VideoIntegrityError: If metadata fails validation
        """
        try:
            # Check basic properties
            if metadata.duration <= 0:
                raise VideoIntegrityError("Invalid video duration")
            if metadata.width <= 0 or metadata.height <= 0:
                raise VideoIntegrityError("Invalid video dimensions")
            if metadata.fps <= 0:
                raise VideoIntegrityError("Invalid frame rate")
            if metadata.total_frames <= 0:
                raise VideoIntegrityError("Invalid frame count")
            if not metadata.codec:
                raise VideoIntegrityError("Invalid or unsupported codec")

            # Check scene requirements
            if metadata.duration < MIN_SCENE_LENGTH:
                raise VideoIntegrityError(
                    f"Video duration {metadata.duration:.1f}s below minimum "
                    f"of {MIN_SCENE_LENGTH}s"
                )

            estimated_scenes = metadata.duration / MIN_SCENE_LENGTH
            if estimated_scenes > MAX_SCENES_PER_VIDEO:
                raise VideoIntegrityError(
                    f"Estimated {estimated_scenes:.0f} scenes exceeds maximum "
                    f"of {MAX_SCENES_PER_VIDEO}"
                )

        except VideoIntegrityError:
            raise
        except Exception as e:
            raise VideoIntegrityError(f"Metadata validation failed: {e}")

    def validate_frames(
        self,
        file_path: Path,
        sample_count: int = 5,
    ) -> None:
        """Validate video frames by sampling throughout the video.

        Args:
            file_path: Path to the video file
            sample_count: Number of frames to sample

        Raises:
            VideoIntegrityError: If frame validation fails
        """
        if self.test_mode:
            return

        try:
            cap = cv2.VideoCapture(str(file_path))
            if not cap.isOpened():
                raise VideoIntegrityError("Failed to open video file")

            try:
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                if frame_count <= 0:
                    raise VideoIntegrityError("Cannot determine frame count")

                # Calculate sample positions
                sample_positions = [
                    int(i * frame_count / (sample_count - 1))
                    for i in range(sample_count)
                ]

                # Check dimensions of first frame
                ret, frame = cap.read()
                if not ret or frame is None:
                    raise VideoIntegrityError("Failed to read first frame")

                height, width = frame.shape[:2]

                # Sample frames throughout video
                for pos in sample_positions[1:]:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
                    ret, frame = cap.read()

                    if not ret or frame is None:
                        raise VideoIntegrityError(f"Failed to read frame at position {pos}")

                    # Check frame dimensions
                    if frame.shape[0] != height or frame.shape[1] != width:
                        raise VideoIntegrityError(
                            f"Inconsistent frame dimensions at position {pos}"
                        )

            finally:
                cap.release()

        except cv2.error as e:
            raise VideoIntegrityError(f"OpenCV error during frame validation: {e}")
        except Exception as e:
            raise VideoIntegrityError(f"Frame validation failed: {e}")

    def estimate_bitrate(self, file_path: Path) -> int:
        """Estimate video bitrate from file size and duration.

        Args:
            file_path: Path to the video file

        Returns:
            Estimated bitrate in bits per second

        Raises:
            VideoIntegrityError: If bitrate cannot be estimated
        """
        if self.test_mode:
            return 5_000_000  # Return 5 Mbps in test mode

        try:
            # Get file size in bits
            size_bits = file_path.stat().st_size * 8

            # Get duration
            metadata = self._extract_metadata(file_path)
            if metadata.duration <= 0:
                raise VideoIntegrityError("Invalid duration for bitrate calculation")

            # Calculate bitrate
            return int(size_bits / metadata.duration)

        except Exception as e:
            raise VideoIntegrityError(f"Failed to estimate bitrate: {e}")
