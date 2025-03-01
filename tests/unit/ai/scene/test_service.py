"""Tests for scene detection service."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from video_understanding.ai.scene.service import (
    SceneDetectionService,
    get_scene_detector,
)


@pytest.mark.asyncio
async def test_service_initialization():
    """Test service initialization."""
    service = SceneDetectionService()
    assert service.detector is None
    assert service.detector_type == "twelve_labs"


@pytest.mark.asyncio
async def test_get_detector():
    """Test get_detector method."""
    service = SceneDetectionService()

    # Mock the _create_detector method
    mock_detector = MagicMock()
    service._create_detector = MagicMock(return_value=mock_detector)

    # Get detector
    detector = await service.get_detector()

    # Verify
    assert detector == mock_detector
    service._create_detector.assert_called_once_with("twelve_labs")

    # Second call should return the same detector
    detector2 = await service.get_detector()
    assert detector2 == mock_detector
    assert service._create_detector.call_count == 1  # Should not be called again


@pytest.mark.asyncio
async def test_create_detector():
    """Test _create_detector method."""
    service = SceneDetectionService()

    with patch(
        "video_understanding.ai.scene.service.TwelveLabsSceneDetection"
    ) as mock_cls:
        # Create detector with twelve_labs type
        service._create_detector("twelve_labs")
        mock_cls.assert_called_once()

        # Reset mock
        mock_cls.reset_mock()

        # Create detector with unknown type
        service._create_detector("unknown_type")
        mock_cls.assert_called_once()  # Should still create TwelveLabsSceneDetection


@pytest.mark.asyncio
async def test_detect_scenes():
    """Test detect_scenes method."""
    service = SceneDetectionService()

    # Mock the get_detector method
    mock_detector = AsyncMock()
    mock_scenes = [{"scene_id": 1, "start_time": 0.0, "end_time": 10.0}]
    mock_detector.detect_scenes.return_value = mock_scenes

    # Use AsyncMock for get_detector
    async_mock = AsyncMock(return_value=mock_detector)
    service.get_detector = async_mock

    # Detect scenes
    scenes = await service.detect_scenes("test_video.mp4")

    # Verify
    assert scenes == mock_scenes
    service.get_detector.assert_called_once()
    mock_detector.detect_scenes.assert_called_once_with("test_video.mp4")


@pytest.mark.asyncio
async def test_close():
    """Test close method."""
    service = SceneDetectionService()

    # Mock detector with AsyncMock
    mock_detector = AsyncMock()
    service.detector = mock_detector

    # Close service
    await service.close()

    # Verify
    mock_detector.close.assert_called_once()
    assert service.detector is None


@pytest.mark.asyncio
async def test_factory_function():
    """Test get_scene_detector factory function."""
    with patch(
        "video_understanding.ai.scene.service.TwelveLabsSceneDetection"
    ) as mock_cls:
        # Get detector with twelve_labs type
        get_scene_detector("twelve_labs")
        mock_cls.assert_called_once()

        # Reset mock
        mock_cls.reset_mock()

        # Get detector with unknown type
        get_scene_detector("unknown_type")
        mock_cls.assert_called_once()  # Should still create TwelveLabsSceneDetection
