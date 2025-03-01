"""Base interface for scene detection components."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseSceneDetector(ABC):
    """Base interface for scene detection."""

    @abstractmethod
    async def detect_scenes(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect scenes in a video.

        Args:
            video_path: Path to the video file

        Returns:
            List of detected scenes

        Raises:
            SceneDetectionError: If scene detection fails
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close resources used by the scene detection."""
        pass
