"""Twelve Labs scene detection implementation."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import ModelError from core exceptions
from video_understanding.core.exceptions import ModelError
from video_understanding.ai.models.twelve_labs.model import TwelveLabsModel
from video_understanding.ai.models.twelve_labs.types import TaskType
from video_understanding.ai.scene.base import BaseSceneDetector

logger = logging.getLogger(__name__)


# Define SceneDetectionError locally
class SceneDetectionError(ModelError):
    """Exception raised when scene detection fails."""

    pass


class TwelveLabsSceneDetection(BaseSceneDetector):
    """Scene detection using Twelve Labs API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        model: Optional[TwelveLabsModel] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the scene detector.

        Args:
            api_key: The Twelve Labs API key
            api_url: The Twelve Labs API URL (base URL)
            model: An existing TwelveLabsModel instance to use
            config: Configuration options for scene detection with settings like:
                - confidence_threshold: Minimum confidence score (0-1, default: 0.5)
                - min_scene_duration: Minimum scene duration in seconds (default: 1.0)
                - max_scenes: Maximum number of scenes to detect (default: 100)

        Raises:
            SceneDetectionError: If initialization fails
        """
        self.config = config or {}

        # Configuration options with defaults
        self.confidence_threshold = self.config.get("confidence_threshold", 0.5)
        self.min_scene_duration = self.config.get("min_scene_duration", 1.0)  # seconds
        self.max_scenes = self.config.get("max_scenes", 100)

        try:
            if model:
                self.model = model
            else:
                if api_key is None:
                    # Use the credentials utility if api_key not provided
                    try:
                        # Import credentials utility
                        from video_understanding.utils import credentials

                        credentials_data = credentials.get_twelve_labs_credentials()
                        api_key = credentials_data["api_key"]
                    except (ImportError, KeyError) as e:
                        raise ValueError(
                            "API key is required when model is not provided"
                        ) from e

                self.model = TwelveLabsModel(
                    api_key=api_key,
                    base_url=api_url or "https://api.twelvelabs.io/v1.1",
                )
            logger.debug("Twelve Labs scene detection initialized")
        except Exception as e:
            raise SceneDetectionError(
                f"Failed to initialize Twelve Labs scene detection: {e}"
            ) from e

    async def detect_scenes(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect scenes in a video.

        Args:
            video_path: Path to the video file

        Returns:
            List of detected scenes with:
                - scene_id: Unique scene identifier
                - start_time: Scene start time in seconds
                - end_time: Scene end time in seconds
                - duration: Scene duration in seconds
                - confidence: Detection confidence score (0-1)

        Raises:
            SceneDetectionError: If scene detection fails
        """
        logger.debug(f"Detecting scenes in {video_path}")

        try:
            # Validate the video path
            if not Path(video_path).exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")

            # Process the video with Twelve Labs API with expanded options
            task_options = {
                "confidence_threshold": self.confidence_threshold,
                "min_scene_duration": self.min_scene_duration,
                "max_scenes": self.max_scenes,
            }

            result = await self.model.process(
                {
                    "video_path": video_path,
                    "task": TaskType.SCENE_DETECTION,
                    "options": task_options,
                }
            )

            # Extract and validate scenes
            scenes = self._extract_scenes(result)

            # Validate minimum accuracy
            if not self._validate_minimum_accuracy(scenes):
                logger.warning("Scene detection accuracy below threshold")
                # In a production system with more time, we might implement a fallback
                # to OpenCV-based detection here, but for this POC we'll
                # use the API results

            logger.debug(f"Detected {len(scenes)} scenes")
            return scenes

        except Exception as e:
            logger.error(f"Scene detection failed: {e}")
            raise SceneDetectionError(f"Failed to detect scenes: {e}") from e

    def _extract_scenes(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract scenes from the API result.

        Args:
            result: The API result containing scene data

        Returns:
            List of scene dictionaries
        """
        scenes = []

        # Extract scenes from the result
        scene_data = result.get("data", {}).get("scenes", [])

        for i, scene in enumerate(scene_data):
            start_time = scene.get("start_time", 0)
            end_time = scene.get("end_time", 0)
            confidence = scene.get("confidence", 0)

            # Filter scenes by minimum duration if configured
            duration = end_time - start_time
            if duration < self.min_scene_duration:
                # Split long log message to avoid line length issues
                msg = f"Skipping scene with duration {duration}s "
                msg += f"(below minimum {self.min_scene_duration}s)"
                logger.debug(msg)
                continue

            scenes.append(
                {
                    "scene_id": i + 1,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "confidence": confidence,
                }
            )

            # Limit the number of scenes if configured
            if len(scenes) >= self.max_scenes:
                logger.debug(f"Reached maximum number of scenes ({self.max_scenes})")
                break

        return scenes

    def _validate_minimum_accuracy(self, scenes: List[Dict[str, Any]]) -> bool:
        """Validate that the average confidence meets the minimum threshold.

        Args:
            scenes: List of detected scenes

        Returns:
            bool: True if the average confidence is above the threshold
        """
        if not scenes:
            return False

        # Calculate average confidence as a proxy for accuracy
        total_confidence = sum(scene.get("confidence", 0.0) for scene in scenes)
        avg_confidence = total_confidence / len(scenes)

        # Log the accuracy metrics
        logger.info(f"Scene detection average confidence: {avg_confidence:.2f}")

        # Check if it meets our 90% accuracy threshold
        return bool(avg_confidence >= 0.9)

    async def close(self) -> None:
        """Close the model and release resources."""
        if hasattr(self, "model"):
            await self.model.close()
