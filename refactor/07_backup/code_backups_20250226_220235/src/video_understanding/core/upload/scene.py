"""Scene detection module for video processing.

This module provides scene change detection functionality.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any
import logging
from pathlib import Path

import cv2
import numpy as np
from video_understanding.core.exceptions import FileValidationError

logger = logging.getLogger(__name__)

class SceneChangeType(Enum):
    """Types of scene changes."""

    CUT = "cut"  # Abrupt scene change
    FADE = "fade"  # Gradual fade transition
    DISSOLVE = "dissolve"  # Gradual dissolve transition


@dataclass
class SceneChange:
    """Represents a detected scene change.

    Attributes:
        frame_number: Frame number where change occurred
        timestamp: Timestamp of the change in seconds
        confidence: Detection confidence score
        type: Type of scene change
    """

    frame_number: int
    timestamp: float
    confidence: float
    type: SceneChangeType


class SceneDetector:
    """Detects scene changes in videos."""

    def __init__(self):
        """Initialize scene detector."""
        self.min_scene_duration = 2.0  # seconds
        self.max_scenes = 500
        self.threshold = 30.0  # threshold for scene change detection

    async def detect(self, file_path: Path) -> List[Dict[str, Any]]:
        """Detect scenes in video file.

        Args:
            file_path: Path to video file

        Returns:
            List of scene information dictionaries

        Raises:
            FileValidationError: If the video file does not exist or cannot be opened
        """
        if not file_path.exists():
            raise FileValidationError(f"Video file not found: {file_path}")

        scenes = []
        cap = cv2.VideoCapture(str(file_path))

        if not cap.isOpened():
            cap.release()
            raise FileValidationError(f"Failed to open video file: {file_path}")

        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            min_frames = int(self.min_scene_duration * fps)

            prev_frame = None
            frame_count = 0
            scene_start = 0

            while cap.isOpened() and frame_count < total_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                if prev_frame is not None:
                    # Calculate frame difference
                    diff = self._calculate_frame_diff(prev_frame, frame)

                    # Check for scene change
                    if diff > self.threshold and (frame_count - scene_start) >= min_frames:
                        scenes.append({
                            "start_frame": scene_start,
                            "end_frame": frame_count,
                            "start_time": scene_start / fps,
                            "end_time": frame_count / fps,
                            "duration": (frame_count - scene_start) / fps
                        })
                        scene_start = frame_count

                        # Check max scenes limit
                        if len(scenes) >= self.max_scenes:
                            break

                prev_frame = frame.copy()
                frame_count += 1

            # Add final scene if needed
            if scene_start < frame_count:
                scenes.append({
                    "start_frame": scene_start,
                    "end_frame": frame_count,
                    "start_time": scene_start / fps,
                    "end_time": frame_count / fps,
                    "duration": (frame_count - scene_start) / fps
                })

        finally:
            cap.release()

        return scenes

    def _calculate_frame_diff(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """Calculate difference between two frames.

        Args:
            frame1: First frame
            frame2: Second frame

        Returns:
            Difference score between frames
        """
        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # Calculate absolute difference
        diff = cv2.absdiff(gray1, gray2)

        # Calculate mean difference (convert to float array first)
        return float(np.mean(diff.astype(np.float32)))

    def set_min_scene_duration(self, duration: float) -> None:
        """Set minimum scene duration.

        Args:
            duration: Minimum duration in seconds
        """
        self.min_scene_duration = max(0.1, duration)

    def set_max_scenes(self, max_scenes: int) -> None:
        """Set maximum number of scenes.

        Args:
            max_scenes: Maximum number of scenes to detect
        """
        self.max_scenes = max(1, max_scenes)

    def set_threshold(self, threshold: float) -> None:
        """Set scene change detection threshold.

        Args:
            threshold: Detection threshold
        """
        self.threshold = max(0.0, threshold)

    def detect_change(
        self,
        frame: np.ndarray,
        frame_number: int,
        timestamp: float,
    ) -> Optional[SceneChange]:
        """Detect if current frame represents a scene change.

        Args:
            frame: Current frame as numpy array
            frame_number: Frame number in sequence
            timestamp: Frame timestamp in seconds

        Returns:
            SceneChange object if change detected, None otherwise
        """
        if not hasattr(self, '_prev_frame'):
            self._prev_frame = frame.copy()
            return None

        # Calculate frame difference
        diff = self._calculate_frame_diff(self._prev_frame, frame)

        # Update previous frame
        self._prev_frame = frame.copy()

        # Check if difference exceeds threshold
        if diff > self.threshold:
            return SceneChange(
                frame_number=frame_number,
                timestamp=timestamp,
                confidence=min(100.0, diff / self.threshold * 100),
                type=SceneChangeType.CUT if diff > self.threshold * 2 else SceneChangeType.DISSOLVE
            )

        return None
