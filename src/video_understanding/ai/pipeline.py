"""Video processing pipeline implementation."""

from enum import Enum
from pathlib import Path
from typing import Any

import cv2
import psutil

from video_understanding.core.config import ProcessingConfig
from video_understanding.core.exceptions import ProcessingError

from .models.base import BaseModel
from .models.twelve_labs import (
    APITimeoutError,
    TwelveLabsError,
)
from .models.twelve_labs import (
    TwelveLabsRateLimitError as RateLimitError,
)


class PipelineStage(Enum):
    """Enumeration of pipeline processing stages."""

    INITIALIZATION = "initialization"
    SCENE_DETECTION = "scene_detection"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    TEXT_EXTRACTION = "text_extraction"
    CONTENT_ANALYSIS = "content_analysis"
    POST_PROCESSING = "post_processing"


class ModelPipeline:
    """Manages a sequence of AI models for processing."""

    def __init__(self, stages: list[PipelineStage] | None = None):
        """Initialize the model pipeline.

        Args:
            stages: Optional list of pipeline stages to execute
        """
        self.stages = stages or list(PipelineStage)
        self.models: dict[PipelineStage, list[BaseModel]] = {
            stage: [] for stage in PipelineStage
        }

    def add_model(self, model: BaseModel, stage: PipelineStage) -> None:
        """Add a model to a specific pipeline stage.

        Args:
            model: AI model instance
            stage: Pipeline stage to add the model to
        """
        self.models[stage].append(model)

    async def process_stage(
        self, stage: PipelineStage, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process input through all models in a stage.

        Args:
            stage: Pipeline stage to process
            input_data: Input data for models

        Returns:
            Combined results from all models in the stage

        Raises:
            ProcessingError: If stage processing fails
        """
        results = {}
        for model in self.models[stage]:
            try:
                if model.validate(input_data):
                    model_output = await model.process(input_data)
                    if isinstance(model_output, dict):
                        results.update(model_output)
                    else:
                        raise ProcessingError(
                            f"Model returned invalid output type: {type(model_output)}"
                        )
            except Exception as e:
                raise ProcessingError(
                    f"Failed to process stage {stage.value}: {e!s}"
                ) from e
        return results

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process input through all pipeline stages.

        Args:
            input_data: Input data for processing

        Returns:
            Combined results from all stages

        Raises:
            ProcessingError: If pipeline processing fails
        """
        results = {"status": "processing"}

        try:
            for stage in self.stages:
                stage_results = await self.process_stage(stage, input_data)
                results.update(stage_results)

            results["status"] = "completed"
            return results
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            return results


def create_pipeline(config: ProcessingConfig) -> ModelPipeline:
    """Create and configure a model pipeline.

    Args:
        config: Processing configuration

    Returns:
        Configured model pipeline instance
    """
    pipeline = ModelPipeline()

    # TODO: Add models based on configuration

    return pipeline


async def execute_pipeline(
    pipeline: ModelPipeline, input_data: dict[str, Any]
) -> dict[str, Any]:
    """Execute a model pipeline on input data.

    Args:
        pipeline: Model pipeline instance
        input_data: Input data for processing

    Returns:
        Processing results

    Raises:
        ProcessingError: If pipeline execution fails
    """
    try:
        return await pipeline.process(input_data)
    except Exception as e:
        raise ProcessingError(f"Pipeline execution failed: {e!s}") from e


def validate_pipeline(pipeline: ModelPipeline) -> bool:
    """Validate a model pipeline configuration.

    Args:
        pipeline: Model pipeline instance

    Returns:
        True if pipeline is valid, False otherwise
    """
    try:
        # Check if required stages have models
        required_stages = {
            PipelineStage.SCENE_DETECTION,
            PipelineStage.AUDIO_TRANSCRIPTION,
            PipelineStage.TEXT_EXTRACTION,
        }

        for stage in required_stages:
            if not pipeline.models[stage]:
                return False

        return True
    except Exception:
        return False


class VideoPipeline:
    """Orchestrates the video processing pipeline."""

    def __init__(self, config: ProcessingConfig, models: list[BaseModel] | None = None):
        """Initialize the pipeline.

        Args:
            config: Video processing configuration
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

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
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

        # Check file format
        if video_path.suffix.lower() not in [
            f".{fmt}" for fmt in self.config.supported_formats
        ]:
            raise ProcessingError(f"Unsupported video format: {video_path.suffix}")

        if video_path.stat().st_size == 0:
            raise ProcessingError("Video file is empty")

        try:
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                raise ProcessingError(
                    "Failed to open video file - file may be corrupted"
                )

            # Get basic video info
            fps = float(cap.get(cv2.CAP_PROP_FPS))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0

            cap.release()
        except Exception as e:
            raise ProcessingError(f"Failed to process video: {e!s}") from e

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
                    model_output = await model.process(input_data)
                    if isinstance(model_output, dict):
                        model_results.update(model_output)
                    else:
                        raise ProcessingError(
                            f"Model returned invalid output type: {type(model_output)}"
                        )
            except RateLimitError as e:
                results["status"] = "error"
                results["error"] = f"Rate limit exceeded: {e!s}"
                return results
            except APITimeoutError as e:
                results["status"] = "error"
                results["error"] = f"API timeout: {e!s}"
                return results
            except TwelveLabsError as e:
                results["status"] = "error"
                results["error"] = f"Model error: {e!s}"
                return results
            except Exception as e:
                raise ProcessingError(f"Model processing failed: {e!s}") from e

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

    async def detect_scenes(self, video_path: Path) -> list[dict[str, Any]]:
        """Detect scenes in a video.

        Args:
            video_path: Path to video file

        Returns:
            List of scene information dictionaries
        """
        result = await self.process(
            {"task": "scene_detection", "video_path": str(video_path)}
        )
        return result.get("scenes", [])

    async def transcribe_audio(self, video_path: Path) -> dict[str, Any]:
        """Transcribe audio from a video.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary containing transcription results
        """
        result = await self.process(
            {"task": "transcription", "video_path": str(video_path)}
        )
        return result.get("transcription", {})

    async def extract_text(self, video_path: Path) -> list[dict[str, Any]]:
        """Extract text from video frames.

        Args:
            video_path: Path to video file

        Returns:
            List of text extraction results
        """
        result = await self.process(
            {"task": "text_extraction", "video_path": str(video_path)}
        )
        return result.get("text_segments", [])

    def get_memory_usage(self) -> dict[str, float]:
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
