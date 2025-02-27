"""Scene detection module for video processing.

This module provides scene change detection functionality.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import cv2
import numpy as np


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
    """Scene change detector for video frames.

    This class detects scene changes in video frames using various methods:
    1. Frame difference analysis
    2. Histogram comparison
    3. Motion analysis

    Example:
        >>> detector = SceneDetector()
        >>> frame = cv2.imread("frame.jpg")
        >>> change = detector.detect_change(frame)
        >>> if change:
        ...     print(f"Scene change at {change.timestamp}s")
    """

    def __init__(
        self,
        diff_threshold: float = 0.35,
        hist_threshold: float = 0.6,
    ) -> None:
        """Initialize scene detector.

        Args:
            diff_threshold: Frame difference threshold
            hist_threshold: Histogram difference threshold
        """
        self.diff_threshold = diff_threshold
        self.hist_threshold = hist_threshold
        self._prev_frame = None
        self._prev_hist = None

    def detect_change(
        self,
        frame: np.ndarray,
        frame_number: int,
        timestamp: float,
    ) -> Optional[SceneChange]:
        """Detect scene changes between consecutive frames.

        Args:
            frame: Current frame as numpy array
            frame_number: Frame number in sequence
            timestamp: Frame timestamp in seconds

        Returns:
            SceneChange object if change detected, None otherwise
        """
        if self._prev_frame is None:
            self._prev_frame = frame
            self._prev_hist = self._compute_histogram(frame)
            return None

        # Compute frame difference
        diff_score = self._compute_frame_diff(frame)
        hist_score = self._compute_hist_diff(frame)

        # Detect scene change
        if diff_score > self.diff_threshold or hist_score > self.hist_threshold:
            change_type = (
                SceneChangeType.CUT
                if diff_score > self.diff_threshold
                else SceneChangeType.DISSOLVE
            )
            confidence = max(diff_score, hist_score)

            # Update previous frame
            self._prev_frame = frame
            self._prev_hist = self._compute_histogram(frame)

            return SceneChange(
                frame_number=frame_number,
                timestamp=timestamp,
                confidence=confidence,
                type=change_type,
            )

        # Update previous frame
        self._prev_frame = frame
        self._prev_hist = self._compute_histogram(frame)
        return None

    def _compute_frame_diff(self, frame: np.ndarray) -> float:
        """Compute normalized frame difference.

        Args:
            frame: Current frame

        Returns:
            Normalized difference score
        """
        # Convert to grayscale
        curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        prev_gray = cv2.cvtColor(self._prev_frame, cv2.COLOR_BGR2GRAY)

        # Compute absolute difference
        diff = cv2.absdiff(curr_gray, prev_gray)
        return diff.mean() / 255.0

    def _compute_histogram(self, frame: np.ndarray) -> np.ndarray:
        """Compute color histogram for frame.

        Args:
            frame: Input frame

        Returns:
            Normalized histogram array
        """
        hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        cv2.normalize(hist, hist)
        return hist

    def _compute_hist_diff(self, frame: np.ndarray) -> float:
        """Compute histogram difference between frames.

        Args:
            frame: Current frame

        Returns:
            Normalized difference score
        """
        curr_hist = self._compute_histogram(frame)
        diff = cv2.compareHist(self._prev_hist, curr_hist, cv2.HISTCMP_CHISQR)
        return min(diff / 1000.0, 1.0)  # Normalize to [0, 1]
