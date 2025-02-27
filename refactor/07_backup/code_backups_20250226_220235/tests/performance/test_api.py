"""Performance tests for API interactions."""

import asyncio
import time
from pathlib import Path

import aiohttp
import pytest

from ..utils.base_test import BasePerformanceTest
from ..utils.mocks import MockTwelveLabsModel


class TestAPIPerformance(BasePerformanceTest):
    """Test suite for API performance and rate limiting."""

    @pytest.fixture(autouse=True)
    def setup_api(self, mock_twelve_labs):
        """Set up API client for testing."""
        self.model = MockTwelveLabsModel(api_key="test_key")
        self.test_videos: list[Path] = []

        yield

        # Cleanup test videos
        with self.cleanup_context() as cleanup_errors:
            for video_path in self.test_videos:
                try:
                    video_path.unlink()
                except Exception as e:
                    cleanup_errors.append(f"Failed to delete {video_path}: {e!s}")

    async def upload_video(self, video_path: Path) -> dict:
        """Upload a video and measure performance.

        Args:
            video_path: Path to the video file

        Returns:
            Upload response
        """
        with self.assert_performance("video_upload"):
            video_id = await self.model._upload_video(str(video_path))
            return {"video_id": video_id}

    async def track_task(self, task_id: str, timeout: int = 300) -> dict:
        """Track task status and measure performance.

        Args:
            task_id: Task ID to track
            timeout: Maximum time to wait in seconds

        Returns:
            Task status response
        """
        with self.assert_performance("task_tracking"):
            return await self.model._track_task_status(task_id, timeout)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("video_size", ["small", "medium", "large"])
    async def test_upload_performance(self, video_size: str, create_test_video):
        """Test upload performance for different video sizes."""
        # Create test video
        video_path = create_test_video(
            self.config.video.sizes_mb[video_size],
            self.config.video.durations_seconds["medium"],
        )
        self.test_videos.append(video_path)

        # Test upload performance
        result = await self.upload_video(video_path)
        assert "video_id" in result

        self.assert_no_errors()

    @pytest.mark.asyncio
    async def test_concurrent_uploads(self, create_test_video):
        """Test performance of concurrent video uploads."""
        video_paths = []

        # Create test videos
        for _ in range(3):  # Test with 3 concurrent uploads
            video_path = create_test_video(
                self.config.video.sizes_mb["medium"],
                self.config.video.durations_seconds["medium"],
            )
            video_paths.append(video_path)
            self.test_videos.append(video_path)

        # Perform concurrent uploads
        with self.assert_performance("concurrent_uploads"):
            tasks = [self.upload_video(path) for path in video_paths]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.record_error(
                    "UploadError", str(result), {"video_path": str(video_paths[i])}
                )
            else:
                assert "video_id" in result

        self.assert_no_errors()

    @pytest.mark.asyncio
    async def test_rate_limiting(self, create_test_video, mocker):
        """Test API rate limiting behavior."""
        video_path = create_test_video(
            self.config.video.sizes_mb["small"],
            self.config.video.durations_seconds["short"],
        )
        self.test_videos.append(video_path)

        # Mock rate limit response
        rate_limit_response = aiohttp.ClientResponse(
            "POST",
            aiohttp.RequestInfo(
                url=aiohttp.URL("https://api.twelvelabs.io/v1.1/upload"),
                method="POST",
                headers={},
                real_url=aiohttp.URL("https://api.twelvelabs.io/v1.1/upload"),
            ),
        )
        rate_limit_response.status = 429

        # Track rate limit recovery
        rate_limit_hits = 0
        last_rate_limit = 0

        async def mock_upload(*args, **kwargs):
            nonlocal rate_limit_hits, last_rate_limit
            current_time = time.time()

            # Simulate rate limit every other request
            if rate_limit_hits == 0 or (current_time - last_rate_limit) > 1:
                rate_limit_hits += 1
                last_rate_limit = current_time
                raise aiohttp.ClientResponseError(
                    request_info=rate_limit_response.request_info,
                    history=(),
                    status=429,
                )
            return "test_video_id"

        mocker.patch.object(self.model, "_upload_video", side_effect=mock_upload)

        with self.assert_performance("rate_limit_handling"):
            for _ in range(5):  # Make multiple requests
                try:
                    result = await self.upload_video(video_path)
                    assert "video_id" in result
                except Exception as e:
                    if (
                        not isinstance(e, aiohttp.ClientResponseError)
                        or e.status != 429
                    ):
                        self.record_error("APIError", str(e))
                # Brief pause between requests
                await asyncio.sleep(0.1)

        self.assert_no_errors()

    @pytest.mark.asyncio
    async def test_error_handling(self, create_test_video, mocker):
        """Test performance impact of error handling."""
        video_path = create_test_video(
            self.config.video.sizes_mb["medium"],
            self.config.video.durations_seconds["medium"],
        )
        self.test_videos.append(video_path)

        # Define error scenarios
        error_scenarios = [
            (500, "Internal Server Error"),
            (502, "Bad Gateway"),
            (504, "Gateway Timeout"),
        ]

        for status_code, error_message in error_scenarios:
            # Mock error response
            error_response = aiohttp.ClientResponse(
                "POST",
                aiohttp.RequestInfo(
                    url=aiohttp.URL("https://api.twelvelabs.io/v1.1/upload"),
                    method="POST",
                    headers={},
                    real_url=aiohttp.URL("https://api.twelvelabs.io/v1.1/upload"),
                ),
            )
            error_response.status = status_code

            async def mock_error(*args, **kwargs):
                raise aiohttp.ClientResponseError(
                    request_info=error_response.request_info,
                    history=(),
                    status=status_code,
                )

            mocker.patch.object(self.model, "_upload_video", side_effect=mock_error)

            with self.assert_performance(f"error_handling_{status_code}"):
                try:
                    await self.upload_video(video_path)
                except aiohttp.ClientResponseError as e:
                    assert e.status == status_code
                except Exception as e:
                    self.record_error(
                        "UnexpectedError", str(e), {"status_code": status_code}
                    )

        self.assert_no_errors()

    @pytest.mark.asyncio
    async def test_retry_performance(self, create_test_video, mocker):
        """Test performance of retry mechanism."""
        video_path = create_test_video(
            self.config.video.sizes_mb["medium"],
            self.config.video.durations_seconds["medium"],
        )
        self.test_videos.append(video_path)

        # Mock retryable failures
        attempt_count = 0

        async def mock_with_retries(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1

            if attempt_count < 3:  # Fail twice before succeeding
                raise aiohttp.ClientError("Temporary network error")
            return "test_video_id"

        mocker.patch.object(self.model, "_upload_video", side_effect=mock_with_retries)

        with self.assert_performance("retry_handling"):
            result = await self.upload_video(video_path)
            assert "video_id" in result
            assert attempt_count == 3  # Verify retry count

        self.assert_no_errors()
