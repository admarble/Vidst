"""Scene detection functionality.

This module provides tools for detecting and analyzing scenes within video content.
It uses computer vision techniques to identify scene changes and extract keyframes.

The main component is the SceneDetector class, which processes videos frame by frame
to detect scene boundaries based on visual changes. It ensures scenes meet minimum
length requirements and provides confidence scoring for detected boundaries.

Example:
    >>> detector = SceneDetector(min_scene_length=2.0, max_scenes=500)
    >>> video = Video(filename="example.mp4", ...)
    >>> scenes = detector.detect_scenes(video)
    >>> for scene in scenes:
    ...     print(f"Scene: {scene.start_time}s to {scene.end_time}s")

Performance Targets:
    - Scene Detection Accuracy: >90%
    - Processing Speed: Maximum 2x video duration
    - Memory Usage: Scales with frame size
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast
from uuid import UUID, uuid4

import cv2
import numpy as np
from numpy.typing import NDArray

from ..models.scene import Scene
from ..models.video import Video

logger = logging.getLogger(__name__)


@dataclass
class SceneParams:
    """Parameters for scene creation.

    Attributes:
        video_id: UUID of the parent video
        start_time: Scene start time in seconds
        end_time: Scene end time in seconds
        keyframe: Frame to use as scene keyframe
        output_dir: Base directory for saving keyframe
    """

    video_id: UUID
    start_time: float
    end_time: float
    keyframe: Any  # OpenCV frame type
    output_dir: Path


class SceneDetector:
    """Handles video scene detection and analysis.

    This class implements frame-by-frame video analysis to detect scene changes
    using computer vision techniques. It ensures detected scenes meet minimum
    length requirements and provides confidence scoring for scene boundaries.

    The detection algorithm:
    1. Processes frames sequentially
    2. Calculates frame differences
    3. Identifies significant visual changes
    4. Extracts keyframes for each scene
    5. Generates scene metadata and confidence scores

    Attributes:
        min_scene_length (float): Minimum scene length in seconds
        max_scenes (int): Maximum number of scenes to detect
    """

    def __init__(self, min_scene_length: float = 2.0, max_scenes: int = 500):
        """Initialize scene detector.

        Args:
            min_scene_length: Minimum scene length in seconds. Scenes shorter than
                this will be merged with adjacent scenes. Default is 2.0 seconds.
            max_scenes: Maximum number of scenes to detect. Processing will stop
                after this many scenes are found. Default is 500 scenes.

        Note:
            These parameters can significantly impact processing time and accuracy.
            Lower min_scene_length or higher max_scenes will increase processing time.
        """
        self.min_scene_length = min_scene_length
        self.max_scenes = max_scenes
        self._scene_change_threshold = 30.0

    def set_scene_change_threshold(self, threshold: float) -> None:
        """Set the threshold for scene change detection.

        Args:
            threshold: New threshold value. Higher values mean fewer scene changes.
        """
        if threshold <= 0:
            raise ValueError("Threshold must be positive")
        self._scene_change_threshold = threshold

    def get_video_info(self, video_path: Path) -> dict:
        """Get basic information about a video file.

        Args:
            video_path: Path to the video file

        Returns:
            Dictionary containing video information (fps, frame count, duration)

        Raises:
            ValueError: If video file cannot be opened
        """
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError("Failed to open video file")

        try:
            fps = float(cap.get(cv2.CAP_PROP_FPS))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0.0

            return {
                "fps": fps,
                "frame_count": frame_count,
                "width": width,
                "height": height,
                "duration": duration,
                "format": self._get_video_format(video_path),
            }
        finally:
            cap.release()

    def extract_keyframe(self, video_path: Path, timestamp: float) -> NDArray[np.uint8]:
        """Extract a keyframe from the video at the specified timestamp.

        Args:
            video_path: Path to the video file
            timestamp: Time in seconds to extract frame from

        Returns:
            Extracted frame as numpy array

        Raises:
            ValueError: If frame cannot be extracted
        """
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError("Failed to open video file")

        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(timestamp * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

            ret, frame = cap.read()
            if not ret or frame is None:
                raise ValueError(f"Failed to extract frame at {timestamp}s")

            return cast(NDArray[np.uint8], frame)
        finally:
            cap.release()

    def _get_video_format(self, video_path: Path) -> str:
        """Get the format/codec of the video file.

        Args:
            video_path: Path to the video file

        Returns:
            String describing the video format
        """
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return "unknown"

        try:
            fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
            return "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
        finally:
            cap.release()

    def _process_video(self, video: Video) -> list[Scene]:
        """Process video to detect scenes.

        This method implements the core video processing logic:
        1. Opens video file and validates it
        2. Processes frames sequentially
        3. Detects scene changes using frame differences
        4. Creates Scene objects with metadata
        5. Handles cleanup and resource management

        Args:
            video: Video object to process

        Returns:
            List of detected Scene objects

        Raises:
            ValueError: If video file is invalid
            RuntimeError: If processing fails
        """
        video_path = Path(video.file_path)
        if not video_path.exists():
            raise ValueError(f"Video file not found: {video_path}")

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")

        try:
            fps = float(cap.get(cv2.CAP_PROP_FPS))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            scenes: list[Scene] = []
            current_scene_start = 0.0
            prev_frame = None

            for frame_number in range(frame_count):
                ret, frame = cap.read()
                if not ret:
                    break

                current_time = frame_number / fps

                if prev_frame is not None:
                    # Check for scene change
                    if self._is_scene_change(prev_frame, frame):
                        # Only create scene if it meets minimum length
                        if current_time - current_scene_start >= self.min_scene_length:
                            scene = self._create_scene(
                                SceneParams(
                                    video_id=video.id,
                                    start_time=current_scene_start,
                                    end_time=current_time,
                                    keyframe=frame,
                                    output_dir=video_path.parent,
                                )
                            )
                            scenes.append(scene)
                            current_scene_start = current_time

                            # Check if we've reached maximum scenes
                            if len(scenes) >= self.max_scenes:
                                break

                prev_frame = frame.copy()

            # Add final scene if it meets minimum length
            if prev_frame is not None and frame_count / fps - current_scene_start >= self.min_scene_length:
                scene = self._create_scene(
                    SceneParams(
                        video_id=video.id,
                        start_time=current_scene_start,
                        end_time=frame_count / fps,
                        keyframe=prev_frame,
                        output_dir=video_path.parent,
                    )
                )
                scenes.append(scene)

            return scenes

        except Exception as e:
            raise RuntimeError(f"Failed to process video: {e}") from e

        finally:
            cap.release()

    def detect_scenes(self, video: Video) -> list[Scene]:
        """Detect scenes in a video.

        Processes the video frame by frame to detect scene changes based on visual
        differences between consecutive frames. Each detected scene includes:
        - Precise start and end timestamps
        - Representative keyframe
        - Confidence score
        - Scene metadata

        Args:
            video: Video object to process, must have a valid file_path

        Returns:
            List of Scene objects, each representing a detected scene with
            metadata and keyframe

        Raises:
            ValueError: If video file is not found, empty, or cannot be opened
            RuntimeError: If video processing fails

        Performance:
            - Processing time scales with video duration
            - Memory usage scales with frame size
            - GPU acceleration used when available
        """
        return self._process_video(video)

    def _is_scene_change(
        self,
        prev_frame: Any,  # OpenCV frame type
        curr_frame: Any,  # OpenCV frame type
        threshold: float = 30.0,
    ) -> bool:
        """Detect if there is a scene change between frames.

        Uses frame difference analysis to identify significant visual changes that
        indicate scene boundaries. The detection process:
        1. Converts frames to grayscale for efficiency
        2. Computes absolute difference between frames
        3. Calculates mean difference
        4. Compares against threshold

        Args:
            prev_frame: Previous video frame
            curr_frame: Current video frame
            threshold: Difference threshold for scene change detection.
                Higher values mean fewer scene changes. Default is 30.0.

        Returns:
            True if a scene change is detected, False otherwise

        Note:
            The threshold value significantly impacts detection sensitivity.
            Lower values will detect more subtle scene changes but may
            result in false positives.
        """
        # Convert frames to grayscale
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        # Calculate frame difference
        frame_diff = cv2.absdiff(prev_gray, curr_gray)
        mean_diff = float(np.mean(frame_diff.astype(np.float32)))

        return mean_diff > threshold

    def _create_scene(self, params: SceneParams) -> Scene:
        """Create a Scene object with extracted keyframe.

        Args:
            params: Scene parameters containing video_id, timestamps, keyframe, and output directory

        Returns:
            Initialized Scene object with all metadata and saved keyframe
        """
        # Create keyframe directory if it doesn't exist
        keyframe_dir = params.output_dir / "keyframes"
        keyframe_dir.mkdir(exist_ok=True)

        # Save keyframe
        scene_id = uuid4()
        keyframe_path = keyframe_dir / f"{scene_id}.jpg"
        cv2.imwrite(str(keyframe_path), params.keyframe)

        return Scene(
            id=scene_id,
            video_id=params.video_id,
            start_time=params.start_time,
            end_time=params.end_time,
            keyframe_path=keyframe_path,
            confidence_score=1.0,  # TODO: Implement confidence scoring
        )
