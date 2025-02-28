"""Integration tests for Twelve Labs scene detection."""

import os
import pytest
from pathlib import Path

from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetection

# Skip these tests if API credentials are not available
pytestmark = pytest.mark.skipif(
    "TWELVE_LABS_API_KEY" not in os.environ,
    reason="Twelve Labs API credentials not available",
)

# Test videos - ensure these exist in your environment
TEST_VIDEOS = {
    "short": "tests/data/sample_short.mp4",
}


@pytest.fixture
async def scene_detector():
    """Create a real TwelveLabsSceneDetection instance with API credentials."""
    detector = TwelveLabsSceneDetection()
    yield detector
    # Clean up resources
    await detector.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_scene_detection(scene_detector):
    """Test scene detection with a real video and API calls."""
    video_path = TEST_VIDEOS["short"]

    # Skip if test video doesn't exist
    if not Path(video_path).exists():
        pytest.skip(f"Test video not found: {video_path}")

    scenes = await scene_detector.detect_scenes(video_path)

    # Verify we got scenes back
    assert len(scenes) > 0

    # Verify scene structure
    assert "scene_id" in scenes[0]
    assert "start_time" in scenes[0]
    assert "end_time" in scenes[0]
    assert "confidence" in scenes[0]

    # Verify confidence meets our threshold
    avg_confidence = sum(scene["confidence"] for scene in scenes) / len(scenes)
    assert avg_confidence >= 0.9, "Average confidence below 90% threshold"
