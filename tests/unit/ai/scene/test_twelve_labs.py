"""Unit tests for Twelve Labs scene detection."""

# mypy: ignore-errors

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

# Import the SceneDetectionError from the implementation file
from video_understanding.ai.scene.twelve_labs import (
    TwelveLabsSceneDetection,
    SceneDetectionError,
)
from video_understanding.ai.models.twelve_labs.model import TwelveLabsModel
from video_understanding.ai.models.twelve_labs.types import TaskType

# Sample test data
SAMPLE_VIDEO_PATH = "path/to/test_video.mp4"
MOCK_API_RESPONSE = {
    "data": {
        "scenes": [
            {"start_time": 0.0, "end_time": 5.0, "confidence": 0.9},
            {"start_time": 5.0, "end_time": 10.0, "confidence": 0.8},
            {"start_time": 10.0, "end_time": 15.0, "confidence": 0.7},
            {"start_time": 15.0, "end_time": 16.0, "confidence": 0.6},  # Short scene
        ]
    }
}


@pytest.fixture
def mock_model():
    """Create a mock TwelveLabsModel."""
    model = MagicMock(spec=TwelveLabsModel)
    model.process = AsyncMock(return_value=MOCK_API_RESPONSE)
    model.close = AsyncMock()
    return model


@pytest_asyncio.fixture
async def scene_detector(mock_model):
    """Create a TwelveLabsSceneDetection instance with a mock model."""
    detector = TwelveLabsSceneDetection(model=mock_model)
    yield detector
    await detector.close()


@pytest.mark.asyncio
async def test_initialization_with_api_key():
    """Test initialization with API key."""
    with patch(
        "video_understanding.ai.scene.twelve_labs.TwelveLabsModel"
    ) as mock_model_class:
        mock_model_instance = MagicMock()
        mock_model_class.return_value = mock_model_instance

        detector = TwelveLabsSceneDetection(api_key="test_api_key")

        mock_model_class.assert_called_once_with(
            api_key="test_api_key",
            base_url="https://api.twelvelabs.io/v1.1",
        )
        assert detector.model == mock_model_instance


@pytest.mark.asyncio
async def test_initialization_with_config():
    """Test initialization with configuration options."""
    config = {
        "confidence_threshold": 0.8,
        "min_scene_duration": 2.0,
        "max_scenes": 50,
    }

    with patch("video_understanding.ai.scene.twelve_labs.TwelveLabsModel"):
        detector = TwelveLabsSceneDetection(api_key="test_api_key", config=config)

        assert detector.confidence_threshold == 0.8
        assert detector.min_scene_duration == 2.0
        assert detector.max_scenes == 50


@pytest.mark.asyncio
async def test_initialization_with_credentials():
    """Test initialization with credentials from environment."""
    with patch(
        "video_understanding.ai.scene.twelve_labs.credentials"
    ) as mock_credentials:
        mock_credentials.get_twelve_labs_credentials.return_value = {
            "api_key": "env_api_key"
        }

        with patch("video_understanding.ai.scene.twelve_labs.TwelveLabsModel"):
            # Create detector and verify credentials were used
            TwelveLabsSceneDetection()
            assert mock_credentials.get_twelve_labs_credentials.called


@pytest.mark.asyncio
async def test_scene_detection(scene_detector, mock_model):
    """Test basic scene detection functionality."""
    # Mock the file existence check
    with patch("pathlib.Path.exists", return_value=True):
        scenes = await scene_detector.detect_scenes(SAMPLE_VIDEO_PATH)

        # Verify the model was called correctly
        mock_model.process.assert_called_once_with(
            {
                "video_path": SAMPLE_VIDEO_PATH,
                "task": TaskType.SCENE_DETECTION,
                "options": {
                    "confidence_threshold": 0.5,
                    "min_scene_duration": 1.0,
                    "max_scenes": 100,
                },
            }
        )

        # Verify the scenes were extracted correctly (should be 3, as one is too short)
        assert len(scenes) == 3

        # Verify the structure of the scenes
        first_scene = scenes[0]  # type: ignore
        assert first_scene["scene_id"] == 1
        assert first_scene["start_time"] == 0.0
        assert first_scene["end_time"] == 5.0
        assert first_scene["duration"] == 5.0
        assert first_scene["confidence"] == 0.9


@pytest.mark.asyncio
async def test_minimum_duration_filtering(scene_detector):
    """Test filtering scenes by minimum duration."""
    # Set a higher minimum duration
    scene_detector.min_scene_duration = 6.0

    # Mock the file existence check
    with patch("pathlib.Path.exists", return_value=True):
        scenes = await scene_detector.detect_scenes(SAMPLE_VIDEO_PATH)

        # Only one scene should be long enough
        assert len(scenes) == 1
        long_scene = scenes[0]  # type: ignore
        assert long_scene["start_time"] == 10.0
        assert long_scene["end_time"] == 15.0


@pytest.mark.asyncio
async def test_accuracy_validation(scene_detector):
    """Test validation of minimum accuracy."""
    # Create scenes with high confidence (above 90% threshold)
    high_confidence_scenes = [
        {"scene_id": 1, "confidence": 0.95},
        {"scene_id": 2, "confidence": 0.92},
        {"scene_id": 3, "confidence": 0.91},
    ]

    # Create scenes with lower confidence (below 90% threshold)
    low_confidence_scenes = [
        {"scene_id": 1, "confidence": 0.85},
        {"scene_id": 2, "confidence": 0.82},
        {"scene_id": 3, "confidence": 0.81},
    ]

    # Verify high confidence scenes pass validation
    assert scene_detector._validate_minimum_accuracy(high_confidence_scenes)

    # Verify low confidence scenes fail validation
    assert not scene_detector._validate_minimum_accuracy(low_confidence_scenes)


@pytest.mark.asyncio
async def test_max_scenes_limit():
    """Test limiting the number of scenes."""
    # Create a detector with a low max_scenes limit
    config = {"max_scenes": 2}
    detector = TwelveLabsSceneDetection(config=config)

    # Create a mock model that returns many scenes
    mock_model = MagicMock(spec=TwelveLabsModel)
    mock_model.process = AsyncMock(return_value=MOCK_API_RESPONSE)
    detector.model = mock_model

    # Mock the file existence check
    with patch("pathlib.Path.exists", return_value=True):
        scenes = await detector.detect_scenes(SAMPLE_VIDEO_PATH)

        # Should only return the first 2 scenes
        assert len(scenes) == 2
        assert scenes[0]["scene_id"] == 1
        assert scenes[1]["scene_id"] == 2


@pytest.mark.asyncio
async def test_error_handling(scene_detector, mock_model):
    """Test error handling during scene detection."""
    # Make the model raise an exception
    mock_model.process.side_effect = Exception("API error")

    # Mock the file existence check
    with patch("pathlib.Path.exists", return_value=True):
        with pytest.raises(SceneDetectionError):
            await scene_detector.detect_scenes(SAMPLE_VIDEO_PATH)


@pytest.mark.asyncio
async def test_file_not_found(scene_detector):
    """Test handling of non-existent video file."""
    # Mock the file existence check to return False
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(SceneDetectionError):
            await scene_detector.detect_scenes("nonexistent.mp4")


@pytest.mark.asyncio
async def test_close(scene_detector, mock_model):
    """Test resource cleanup."""
    await scene_detector.close()
    mock_model.close.assert_called_once()
