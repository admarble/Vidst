"""Scene detection service for Video Understanding AI."""

import logging
from typing import Optional

from video_understanding.ai.scene.base import BaseSceneDetector
from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetection

logger = logging.getLogger(__name__)


class SceneDetectionService:
    """Service for detecting scenes in videos."""

    def __init__(self, detector_type: str = "twelve_labs"):
        """Initialize the scene detection service.

        Args:
            detector_type: Type of scene detector to use
        """
        self.detector: Optional[BaseSceneDetector] = None
        self.detector_type = detector_type

    async def get_detector(self) -> BaseSceneDetector:
        """Get or create the scene detector.

        Returns:
            BaseSceneDetector: Scene detector instance
        """
        if self.detector is None:
            self.detector = self._create_detector(self.detector_type)
        return self.detector

    def _create_detector(self, detector_type: str) -> BaseSceneDetector:
        """Create a scene detector of the specified type.

        Args:
            detector_type: Type of scene detector to create

        Returns:
            BaseSceneDetector: Scene detector instance
        """
        if detector_type == "twelve_labs":
            logger.info("Creating Twelve Labs scene detector")
            return TwelveLabsSceneDetection()
        else:
            logger.warning(f"Unknown detector type: {detector_type}, using Twelve Labs")
            return TwelveLabsSceneDetection()

    async def detect_scenes(self, video_path: str):
        """Detect scenes in a video.

        Args:
            video_path: Path to the video file

        Returns:
            List of detected scenes
        """
        detector = await self.get_detector()
        return await detector.detect_scenes(video_path)

    async def close(self):
        """Close the service and release resources."""
        if self.detector is not None:
            await self.detector.close()
            self.detector = None


# Factory function for convenience
def get_scene_detector(detector_type: str = "twelve_labs") -> BaseSceneDetector:
    """Get a scene detector of the specified type.

    Args:
        detector_type: Type of scene detector to create

    Returns:
        BaseSceneDetector: Scene detector instance
    """
    if detector_type == "twelve_labs":
        return TwelveLabsSceneDetection()
    else:
        return TwelveLabsSceneDetection()
