"""Test stability of video processing pipeline."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

import pytest

from ..utils.base_test import BasePerformanceTest
from ..utils.mocks import MockProcessingConfig, MockTwelveLabsModel, MockVideoPipeline

logger = logging.getLogger(__name__)


class TestPipelineStability(BasePerformanceTest):
    """Test suite for pipeline stability."""

    def setup_method(self):
        """Set up test environment."""
        self.config = MockProcessingConfig()
        self.model = MockTwelveLabsModel(api_key="test_key")
        self.pipeline = MockVideoPipeline(config=self.config, models=[self.model])

        # Track processed videos for cleanup
        self.processed_videos: list[Path] = []

    @pytest.fixture(autouse=True)
    def setup_pipeline(self, mock_cv2, mock_twelve_labs, mock_process_metrics):
        """Set up video processing pipeline for testing."""
        yield

        # Cleanup processed videos
        with self.cleanup_context() as cleanup_errors:
            for video_path in self.processed_videos:
                try:
                    video_path.unlink()
                except Exception as e:
                    cleanup_errors.append(f"Failed to delete {video_path}: {e!s}")

    async def process_video(self, video_path: Path, expected_duration: int) -> dict:
        """Process a single video and measure performance.

        Args:
            video_path: Path to the video file
            expected_duration: Expected processing duration in seconds

        Returns:
            Processing results
        """
        self.expected_duration = expected_duration

        with self.assert_performance("video_processing"):
            result = await self.pipeline.process(
                {"video_path": str(video_path), "task": "scene_detection"}
            )

            if result["status"] != "completed":
                self.record_error(
                    "ProcessingIncomplete",
                    f"Processing status: {result['status']}",
                    {"video_path": str(video_path)},
                )

            return result

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "duration_seconds",
        [
            pytest.param(3600, id="1hour", marks=pytest.mark.slow),
            pytest.param(300, id="5min", marks=pytest.mark.quick),
        ],
    )
    async def test_long_running_stability(
        self, duration_seconds: int, create_test_video, caplog
    ):
        """Test system stability over extended periods.

        Args:
            duration_seconds: Test duration in seconds
            create_test_video: Fixture for creating test videos
            caplog: Pytest logging capture fixture
        """
        caplog.set_level(logging.INFO)
        start_time = datetime.now()
        processed_count = 0
        consecutive_errors = 0

        logger.info(f"Starting stability test for {duration_seconds} seconds")

        while (datetime.now() - start_time).total_seconds() < duration_seconds:
            # Create test video
            try:
                video_size = self.config.video.sizes_mb["medium"]  # 100MB
                video_duration = self.config.video.durations_seconds[
                    "medium"
                ]  # 5 minutes
                video_path = create_test_video(video_size, video_duration)
                self.processed_videos.append(video_path)

                logger.info(f"Created test video: {video_path}")
            except Exception as e:
                self.record_error("VideoCreationError", str(e))
                consecutive_errors += 1
                if consecutive_errors >= self.config.errors.max_consecutive_errors:
                    pytest.fail(
                        f"Failed to create videos {consecutive_errors} times in a row"
                    )
                continue

            # Process the video
            try:
                result = await self.process_video(video_path, video_duration)
                if result["status"] == "completed":
                    processed_count += 1
                    consecutive_errors = 0
                    logger.info(f"Successfully processed video {processed_count}")
            except Exception as e:
                self.record_error(
                    "ProcessingError", str(e), {"video_path": str(video_path)}
                )
                consecutive_errors += 1
                if consecutive_errors >= self.config.errors.max_consecutive_errors:
                    pytest.fail(
                        f"Processing failed {consecutive_errors} times in a row"
                    )
                continue

            # Brief pause to prevent overwhelming the system
            await asyncio.sleep(1)

        # Calculate and verify metrics
        total_duration = (datetime.now() - start_time).total_seconds()
        videos_per_hour = (processed_count / total_duration) * 3600

        if videos_per_hour < self.config.processing.min_videos_per_hour:
            self.record_error(
                "ThroughputError",
                f"Processing rate ({videos_per_hour:.1f} videos/hour) below minimum "
                f"({self.config.processing.min_videos_per_hour} videos/hour)",
            )

        self.assert_no_errors()

    @pytest.mark.asyncio
    async def test_memory_stability(self, create_test_video):
        """Test memory stability under continuous processing."""
        video_paths = []

        # Create a set of test videos
        for size, duration in [
            ("small", "short"),
            ("medium", "medium"),
            ("large", "long"),
        ]:
            video_path = create_test_video(
                self.config.video.sizes_mb[size],
                self.config.video.durations_seconds[duration],
            )
            video_paths.append(video_path)
            self.processed_videos.append(video_path)

        # Process each video multiple times to check for memory leaks
        for _ in range(3):  # 3 iterations
            for video_path in video_paths:
                await self.process_video(
                    video_path, self.config.video.durations_seconds["medium"]
                )

        # Memory growth should be within limits
        self.assert_no_errors()

    @pytest.mark.asyncio
    async def test_error_recovery(self, create_test_video, mocker):
        """Test system recovery from various error conditions."""
        video_path = create_test_video(
            self.config.video.sizes_mb["medium"],
            self.config.video.durations_seconds["medium"],
        )
        self.processed_videos.append(video_path)

        # Test recovery from API errors
        mocker.patch(
            "src.ai.models.twelve_labs.TwelveLabsModel._upload_video",
            side_effect=[Exception("API Error"), "test_video_id"],
        )

        with self.assert_performance("error_recovery"):
            # First attempt should fail
            try:
                await self.process_video(
                    video_path, self.config.video.durations_seconds["medium"]
                )
            except Exception:
                pass

            # Second attempt should succeed
            result = await self.process_video(
                video_path, self.config.video.durations_seconds["medium"]
            )
            assert result["status"] == "completed"

        self.assert_no_errors()

    @pytest.mark.asyncio
    async def test_concurrent_stability(self, create_test_video):
        """Test stability with concurrent video processing."""
        video_paths = []

        # Create test videos
        for i in range(4):  # Create 4 test videos
            video_path = create_test_video(
                self.config.video.sizes_mb["medium"],
                self.config.video.durations_seconds["medium"],
            )
            video_paths.append(video_path)
            self.processed_videos.append(video_path)

        # Process videos concurrently
        with self.assert_performance("concurrent_processing"):
            tasks = [
                self.process_video(
                    video_path, self.config.video.durations_seconds["medium"]
                )
                for video_path in video_paths
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.record_error(
                    "ConcurrentProcessingError",
                    str(result),
                    {"video_path": str(video_paths[i])},
                )

        self.assert_no_errors()
