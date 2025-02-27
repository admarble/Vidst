"""Video processing pipeline implementation.

This module provides the core video processing pipeline that orchestrates
multiple processing stages including:
- Scene detection
- Audio transcription
- Text extraction
- Content analysis
- Metadata generation
"""

import asyncio
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any

from video_understanding.ai.exceptions import ModelError, ValidationError
from video_understanding.ai.models import load_model
from video_understanding.ai.models.config import get_model_config
from video_understanding.core.exceptions import PipelineError


class ProcessingPipeline:
    """Video processing pipeline.

    This class manages the complete video processing workflow by:
    - Coordinating multiple processing stages
    - Managing dependencies between stages
    - Handling errors and retries
    - Collecting and combining results
    - Managing system resources

    Attributes:
        MAX_CONCURRENT_TASKS: Maximum number of concurrent processing tasks
        DEFAULT_TIMEOUT: Default timeout for each processing stage
    """

    MAX_CONCURRENT_TASKS = 3
    DEFAULT_TIMEOUT = 300  # seconds

    def __init__(self) -> None:
        """Initialize the processing pipeline."""
        self._models = {}
        self._active_tasks = set()
        self._semaphore = asyncio.Semaphore(self.MAX_CONCURRENT_TASKS)

    async def process_video(
        self,
        video_path: Path,
        stages: list[str] | None = None,
        options: dict[str, Any] | None = None,
        progress_callback: Callable[[str, float], None] | None = None,
    ) -> dict[str, Any]:
        """Process a video through multiple stages.

        Args:
            video_path: Path to video file
            stages: List of processing stages to run
            options: Processing options for each stage
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary containing combined results from all stages

        Raises:
            PipelineError: If processing fails
            ValidationError: If input is invalid
        """
        if not video_path.exists():
            raise ValidationError(f"Video file not found: {video_path}")

        if stages is None:
            stages = ["scene_detection", "transcription", "text_extraction"]

        if options is None:
            options = {}

        try:
            results = {}
            total_stages = len(stages)

            for i, stage in enumerate(stages):
                if progress_callback:
                    progress_callback(stage, i / total_stages)

                result = await self._process_stage(
                    stage, video_path, options.get(stage, {})
                )
                results[stage] = result

                if progress_callback:
                    progress_callback(stage, (i + 1) / total_stages)

            return self._combine_results(results)

        except ModelError as e:
            raise PipelineError(f"Model error in pipeline: {e!s}") from e
        except Exception as e:
            raise PipelineError(f"Pipeline processing failed: {e!s}") from e

    async def _process_stage(
        self, stage: str, video_path: Path, options: dict[str, Any]
    ) -> dict[str, Any]:
        """Process a single pipeline stage.

        Args:
            stage: Name of the processing stage
            video_path: Path to video file
            options: Stage-specific processing options

        Returns:
            Stage processing results

        Raises:
            PipelineError: If stage processing fails
        """
        try:
            async with self._semaphore:
                model = await self._get_model(stage)
                task_id = f"{stage}_{video_path.name}"
                self._active_tasks.add(task_id)

                try:
                    result = await asyncio.wait_for(
                        model.process({"video_path": str(video_path), **options}),
                        timeout=self.DEFAULT_TIMEOUT,
                    )
                    return result
                finally:
                    self._active_tasks.remove(task_id)

        except asyncio.TimeoutError:
            raise PipelineError(
                f"Stage {stage} timed out after {self.DEFAULT_TIMEOUT}s"
            )
        except ModelError as e:
            raise PipelineError(f"Model error in stage {stage}: {e!s}") from e
        except Exception as e:
            raise PipelineError(f"Stage {stage} failed: {e!s}") from e

    async def _get_model(self, stage: str) -> Any:
        """Get or initialize model for processing stage.

        Args:
            stage: Processing stage name

        Returns:
            Initialized model instance

        Raises:
            PipelineError: If model initialization fails
        """
        if stage not in self._models:
            try:
                config = get_model_config(stage)
                self._models[stage] = load_model(stage, config)
            except ModelError as e:
                raise PipelineError(
                    f"Failed to initialize model for {stage}: {e!s}"
                ) from e
            except Exception as e:
                raise PipelineError(
                    f"Failed to initialize model for {stage}: {e!s}"
                ) from e

        return self._models[stage]

    def _combine_results(self, results: dict[str, Any]) -> dict[str, Any]:
        """Combine results from multiple processing stages.

        Args:
            results: Dictionary of stage results

        Returns:
            Combined processing results
        """
        combined = {
            "metadata": {},
            "scenes": [],
            "transcription": None,
            "text_segments": [],
            "analysis": {},
        }

        # Combine metadata
        for stage_results in results.values():
            if "metadata" in stage_results:
                combined["metadata"].update(stage_results["metadata"])

        # Extract scenes
        if "scene_detection" in results:
            combined["scenes"] = (
                results["scene_detection"].get("data", {}).get("scenes", [])
            )

        # Extract transcription
        if "transcription" in results:
            combined["transcription"] = results["transcription"].get("data", {})

        # Extract text segments
        if "text_extraction" in results:
            combined["text_segments"] = (
                results["text_extraction"].get("data", {}).get("segments", [])
            )

        return combined

    async def close(self) -> None:
        """Clean up pipeline resources.

        This method ensures proper cleanup of all models and resources
        when the pipeline is no longer needed.
        """
        for model in self._models.values():
            await model.close()
        self._models.clear()
        self._active_tasks.clear()


async def analyze_scene(
    video_path: Path,
    start_time: float,
    end_time: float,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Analyze a specific scene in a video.

    This function performs detailed analysis of a video segment including:
    - Visual content analysis
    - Audio transcription
    - Text extraction
    - Action recognition
    - Object detection

    Args:
        video_path: Path to video file
        start_time: Scene start time in seconds
        end_time: Scene end time in seconds
        options: Analysis options

    Returns:
        Dictionary containing:
            - visual_content: Visual analysis results
            - transcription: Audio transcription
            - text_content: Extracted text
            - actions: Detected actions
            - objects: Detected objects
            - metadata: Scene metadata

    Raises:
        PipelineError: If analysis fails
        ValidationError: If input is invalid
    """
    if not video_path.exists():
        raise ValidationError(f"Video file not found: {video_path}")

    if start_time < 0 or end_time <= start_time:
        raise ValidationError("Invalid time range")

    if options is None:
        options = {}

    try:
        # Initialize models
        gpt4v_model = load_model("gpt4v")
        whisper_model = load_model("whisper")
        twelve_labs_model = load_model("twelve_labs")

        # Process scene in parallel
        tasks: list[Coroutine[Any, Any, dict[str, Any]]] = [
            gpt4v_model.process(
                {
                    "video_path": str(video_path),
                    "start_time": start_time,
                    "end_time": end_time,
                    **options.get("visual", {}),
                }
            ),
            whisper_model.process(
                {
                    "video_path": str(video_path),
                    "start_time": start_time,
                    "end_time": end_time,
                    **options.get("audio", {}),
                }
            ),
            twelve_labs_model.process(
                {
                    "video_path": str(video_path),
                    "start_time": start_time,
                    "end_time": end_time,
                    **options.get("analysis", {}),
                }
            ),
        ]

        results = await asyncio.gather(*tasks)
        visual_result, audio_result, analysis_result = results

        return {
            "visual_content": visual_result.get("data", {}),
            "transcription": audio_result.get("data", {}),
            "analysis": analysis_result.get("data", {}),
            "metadata": {
                "start_time": start_time,
                "end_time": end_time,
                "duration": end_time - start_time,
                **analysis_result.get("metadata", {}),
            },
        }

    except Exception as e:
        raise PipelineError(f"Scene analysis failed: {e!s}") from e
