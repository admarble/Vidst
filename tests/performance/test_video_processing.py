"""Test video processing performance."""

import asyncio
import logging
from pathlib import Path

import pytest

from ..utils.base_test import BasePerformanceTest
from ..utils.mocks import MockProcessingConfig, MockTwelveLabsModel, MockVideoPipeline

logger = logging.getLogger(__name__)


class TestVideoProcessing(BasePerformanceTest):
    """Test suite for video processing performance."""

    def setup_method(self):
        """Set up test environment."""
        self.config = MockProcessingConfig()
        self.model = MockTwelveLabsModel(api_key="test_key")
        self.pipeline = MockVideoPipeline(config=self.config, models=[self.model])

        # Track videos for cleanup
        self.test_videos: list[Path] = []

    @pytest.fixture(autouse=True)
    def setup_pipeline(self, mock_cv2, mock_twelve_labs, mock_process_metrics):
        """Set up video processing pipeline for testing."""
        # Use mock implementations
        self.processing_config = MockProcessingConfig()
        self.model = MockTwelveLabsModel(api_key="test_key")
        self.pipeline = MockVideoPipeline(self.processing_config, models=[self.model])

        yield

        # Cleanup test videos
        with self.cleanup_context() as cleanup_errors:
            for video_path in self.test_videos:
                try:
                    video_path.unlink()
                except Exception as e:
                    cleanup_errors.append(f"Failed to delete {video_path}: {e!s}")

    async def process_video_with_metrics(
        self, video_path: Path, task: str, operation_name: str
    ) -> dict:
        """Process a video and collect performance metrics.

        Args:
            video_path: Path to the video file
            task: Processing task to perform
            operation_name: Name for the performance metrics

        Returns:
            Processing results
        """
        with self.assert_performance(operation_name):
            result = await self.pipeline.process(
                {"video_path": str(video_path), "task": task}
            )

            if result["status"] != "completed":
                self.record_error(
                    "ProcessingError",
                    f"Processing failed with status: {result['status']}",
                    {"video_path": str(video_path), "task": task},
                )

            return result

    @pytest.mark.asyncio
    @pytest.mark.parametrize("video_size", ["small", "medium", "large"])
    async def test_processing_by_size(self, video_size: str, create_test_video):
        """Test processing performance for different video sizes."""
        # Create test video
        video_path = create_test_video(
            self.config.video.sizes_mb[video_size],
            self.config.video.durations_seconds[
                "medium"
            ],  # Use medium duration for all sizes
        )
        self.test_videos.append(video_path)

        # Process video and measure performance
        await self.process_video_with_metrics(
            video_path, "scene_detection", f"process_{video_size}"
        )

        self.assert_no_errors()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("video_duration", ["short", "medium", "long"])
    async def test_processing_by_duration(self, video_duration: str, create_test_video):
        """Test processing performance for different video durations."""
        # Create test video
        video_path = create_test_video(
            self.config.video.sizes_mb["medium"],  # Use medium size for all durations
            self.config.video.durations_seconds[video_duration],
        )
        self.test_videos.append(video_path)

        # Set expected duration for performance assertions
        self.expected_duration = self.config.video.durations_seconds[video_duration]

        # Process video and measure performance
        await self.process_video_with_metrics(
            video_path, "scene_detection", f"process_{video_duration}"
        )

        self.assert_no_errors()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "task", ["scene_detection", "object_detection", "action_recognition"]
    )
    async def test_processing_by_task(self, task: str, create_test_video):
        """Test processing performance for different tasks."""
        # Create test video
        video_path = create_test_video(
            self.config.video.sizes_mb["medium"],
            self.config.video.durations_seconds["medium"],
        )
        self.test_videos.append(video_path)

        # Process video and measure performance
        await self.process_video_with_metrics(video_path, task, f"process_{task}")

        self.assert_no_errors()

    @pytest.mark.asyncio
    async def test_batch_processing(self, create_test_video):
        """Test performance of batch video processing."""
        video_paths = []

        # Create a batch of videos
        for i in range(5):  # Process 5 videos in batch
            video_path = create_test_video(
                self.config.video.sizes_mb["medium"],
                self.config.video.durations_seconds["medium"],
            )
            video_paths.append(video_path)
            self.test_videos.append(video_path)

        # Process videos in batch
        with self.assert_performance("batch_processing"):
            tasks = [
                self.pipeline.process(
                    {"video_path": str(video_path), "task": "scene_detection"}
                )
                for video_path in video_paths
            ]
            results = await asyncio.gather(*tasks)

        # Verify all videos processed successfully
        for i, result in enumerate(results):
            if result["status"] != "completed":
                self.record_error(
                    "BatchProcessingError",
                    f"Video {i} failed with status: {result['status']}",
                    {"video_path": str(video_paths[i])},
                )

        self.assert_no_errors()

    @pytest.mark.asyncio
    async def test_processing_with_options(self, create_test_video):
        """Test performance impact of different processing options."""
        video_path = create_test_video(
            self.config.video.sizes_mb["medium"],
            self.config.video.durations_seconds["medium"],
        )
        self.test_videos.append(video_path)

        # Test different processing options
        options = [
            ("default", {}),
            ("high_quality", {"quality": "high", "frame_sample_rate": 1}),
            ("fast", {"quality": "low", "frame_sample_rate": 5}),
        ]

        for option_name, settings in options:
            with self.assert_performance(f"process_{option_name}"):
                result = await self.pipeline.process(
                    {
                        "video_path": str(video_path),
                        "task": "scene_detection",
                        **settings,
                    }
                )

                if result["status"] != "completed":
                    self.record_error(
                        "ProcessingError",
                        f"Processing with {option_name} options failed",
                        {"options": settings},
                    )

        self.assert_no_errors()

    @pytest.mark.asyncio
    async def test_processing_resume(self, create_test_video, mocker):
        """Test performance of resuming interrupted processing."""
        video_path = create_test_video(
            self.config.video.sizes_mb["medium"],
            self.config.video.durations_seconds["medium"],
        )
        self.test_videos.append(video_path)

        # Mock interruption and resume
        process_calls = 0
        original_process = self.pipeline.process

        async def mock_process(*args, **kwargs):
            nonlocal process_calls
            process_calls += 1
            if process_calls == 1:
                raise Exception("Simulated interruption")
            return await original_process(*args, **kwargs)

        mocker.patch.object(self.pipeline, "process", side_effect=mock_process)

        with self.assert_performance("process_resume"):
            # First attempt should fail
            try:
                await self.process_video_with_metrics(
                    video_path, "scene_detection", "process_interrupted"
                )
            except Exception:
                pass

            # Resume should succeed
            await self.process_video_with_metrics(
                video_path, "scene_detection", "process_resumed"
            )

        self.assert_no_errors()
