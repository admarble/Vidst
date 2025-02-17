"""Video processing pipeline implementation."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

from src.core.config import VideoConfig
from src.core.exceptions import ProcessingError

from .models.base import BaseModel


class VideoPipeline:
    """Orchestrates the video processing pipeline."""

    def __init__(self, config: VideoConfig, models: Optional[List[BaseModel]] = None):
        """Initialize the pipeline.

        Args:
            config: Video configuration
            models: Optional list of AI models
        """
        self.config = config
        self.models = models or []

    def add_model(self, model: BaseModel) -> None:
        """Add a model to the pipeline.

        Args:
            model: AI model instance
        """
        self.models.append(model)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process video through all models in the pipeline.

        Args:
            input_data: Dictionary containing input data
                If a string or Path is provided, it will be treated as the video path

        Returns:
            Dictionary containing combined results

        Raises:
            ProcessingError: If processing fails
        """
        # Handle string or Path input
        if isinstance(input_data, (str, Path)):
            input_data = {"video_path": str(input_data)}

        if not input_data or "video_path" not in input_data:
            raise ProcessingError("Missing required video_path in input data")

        video_path = Path(input_data["video_path"])
        if not video_path.exists():
            raise ProcessingError(f"Video file not found: {video_path}")

        if video_path.stat().st_size == 0:
            raise ProcessingError("Video file is empty")

        try:
            import cv2

            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                raise ProcessingError(
                    "Failed to open video file - file may be corrupted"
                )

            # Get basic video info
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0

            cap.release()
        except Exception as e:
            raise ProcessingError(f"Failed to process video: {str(e)}")

        results = {
            "status": "processing",
            "metadata": {
                "duration": duration,
                "frame_count": frame_count,
                "resolution": (width, height),
                "fps": fps,
            },
        }

        model_results = {}
        for model in self.models:
            try:
                if model.validate(input_data):
                    model_output = model.process(input_data)
                    model_results.update(model_output)
            except Exception as e:
                raise ProcessingError(f"Model processing failed: {str(e)}")

        # Ensure required fields are present
        results.update(model_results)
        if "scene_description" not in results:
            if frame_count == 0:  # No visual content
                results["scene_description"] = "No visual content detected"
            elif duration < 0.2:  # Very short video
                results["scene_description"] = "Video too short for analysis"
            else:
                results["scene_description"] = "No content analysis available"

        results["status"] = "completed"
        return results

    def detect_scenes(self, video_path: Path) -> List[Dict[str, Any]]:
        """Detect scenes in a video.

        Args:
            video_path: Path to video file

        Returns:
            List of scene information dictionaries
        """
        return self.process(
            {"task": "scene_detection", "video_path": str(video_path)}
        ).get("scenes", [])

    def transcribe_audio(self, video_path: Path) -> Dict[str, Any]:
        """Transcribe audio from a video.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary containing transcription results
        """
        return self.process(
            {"task": "transcription", "video_path": str(video_path)}
        ).get("transcription", {})

    def extract_text(self, video_path: Path) -> List[Dict[str, Any]]:
        """Extract text from video frames.

        Args:
            video_path: Path to video file

        Returns:
            List of text extraction results
        """
        return self.process(
            {"task": "text_extraction", "video_path": str(video_path)}
        ).get("text_segments", [])

    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics.

        Returns:
            Dictionary containing memory usage information
        """
        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            "rss": memory_info.rss / 1024 / 1024,  # MB
            "vms": memory_info.vms / 1024 / 1024,  # MB
            "percent": process.memory_percent(),
        }
