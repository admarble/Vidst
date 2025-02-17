"""Unit tests for AI model integrations."""

import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from src.ai.models.base import BaseModel
from src.ai.models.gemini import GeminiModel
from src.ai.models.gpt4v import GPT4VisionModel
from src.ai.models.twelve_labs import TwelveLabsModel
from src.core.exceptions import ModelError


@pytest.fixture
def mock_api_response():
    """Mock successful API response."""
    return {
        "description": "Sample analysis",
        "objects": ["person", "laptop"],
        "text": ["Hello World"],
        "actions": ["typing"],
    }


@pytest.fixture
def mock_failed_api_response():
    """Mock failed API response."""
    return {"error": "API rate limit exceeded"}


@pytest.fixture
def test_image():
    """Create a test image file."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tf:
        tf.write(b"test image data")
        tf.flush()
        return Path(tf.name)


@pytest.fixture
def test_video():
    """Create a test video file."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tf:
        tf.write(b"test video data")
        tf.flush()
        return Path(tf.name)


class MockBaseModel(BaseModel):
    """Mock implementation of BaseModel for testing."""

    def __init__(self):
        self.resources = []

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True}

    def validate(self, input_data: Dict[str, Any]) -> bool:
        if not input_data:
            raise ValueError("Invalid input")
        return True

    def _cleanup_resources(self) -> None:
        self.resources.clear()


class TestGPT4VisionModel:
    """Tests for GPT-4V model integration."""

    @pytest.fixture
    def model(self, mock_env_vars):
        """Create a GPT-4V model instance."""
        return GPT4VisionModel(api_key=mock_env_vars["OPENAI_API_KEY"])

    def test_validate(self, model, test_image):
        """Test input validation."""
        assert model.validate({"image_path": str(test_image)})

        with pytest.raises(ModelError):
            model.validate({})  # Missing image_path

        with pytest.raises(ModelError):
            model.validate({"image_path": "nonexistent.jpg"})

    def test_process(self, model, test_image, mock_api_response):
        """Test image processing."""
        result = model.process({"image_path": str(test_image)})
        assert "description" in result
        assert "objects" in result
        assert "text" in result
        assert "actions" in result


class TestGeminiModel:
    """Tests for Google Gemini model integration."""

    @pytest.fixture
    def model(self, mock_env_vars):
        """Create a Gemini model instance."""
        return GeminiModel(api_key=mock_env_vars["GEMINI_API_KEY"])

    def test_validate(self, model, test_image):
        """Test input validation."""
        assert model.validate({"image_path": str(test_image)})

        with pytest.raises(ModelError):
            model.validate({})

    def test_process(self, model, test_image, mock_api_response):
        """Test content processing."""
        result = model.process({"image_path": str(test_image)})
        assert "description" in result


class TestTwelveLabsModel:
    """Tests for Twelve Labs model integration."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock requests session."""
        session = MagicMock()
        # Mock index check response
        session.request.side_effect = [
            # Index check response
            MagicMock(
                status_code=200, json=lambda: {"data": [{"name": "default_index"}]}
            ),
            # Upload task creation response
            MagicMock(status_code=200, json=lambda: {"task_id": "test_upload_task_id"}),
            # Upload chunk response
            MagicMock(status_code=204),
            # Upload status response
            MagicMock(
                status_code=200,
                json=lambda: {
                    "status": "completed",
                    "result": {"video_id": "test_video_id"},
                },
            ),
            # Analysis task creation response
            MagicMock(
                status_code=200, json=lambda: {"task_id": "test_analysis_task_id"}
            ),
            # Analysis status response
            MagicMock(
                status_code=200,
                json=lambda: {
                    "status": "completed",
                    "result": {
                        "scene_description": "Test scene",
                        "objects": [{"name": "person"}],
                        "actions": [{"description": "walking"}],
                        "metadata": {
                            "duration": 10,
                            "fps": 30,
                            "resolution": "1920x1080",
                        },
                    },
                },
            ),
        ]
        return session

    @pytest.fixture
    def model(self, mock_env_vars, mock_session):
        """Create a Twelve Labs model instance with mock session."""
        with patch("requests.Session", return_value=mock_session):
            return TwelveLabsModel(api_key=mock_env_vars["TWELVE_LABS_API_KEY"])

    def test_validate(self, model, test_video):
        """Test input validation."""
        input_data = {"video_path": str(test_video), "start_time": 0, "end_time": 10}
        assert model.validate(input_data)

        with pytest.raises(ModelError):
            model.validate({})

    def test_process(self, model, test_video, mock_api_response):
        """Test video processing."""
        input_data = {"video_path": str(test_video), "start_time": 0, "end_time": 10}
        result = model.process(input_data)
        assert "description" in result
        assert "objects" in result
        assert "actions" in result
        assert "metadata" in result


@pytest.mark.parametrize(
    "model_class,input_data",
    [
        (GPT4VisionModel, {"image_path": "test.jpg"}),
        (GeminiModel, {"image_path": "test.jpg"}),
        (TwelveLabsModel, {"video_path": "test.mp4", "start_time": 0, "end_time": 10}),
    ],
)
def test_model_initialization(
    model_class, input_data, mock_env_vars, test_image, test_video, monkeypatch
):
    """Test initialization and basic functionality of all model types."""
    api_key_map = {
        GPT4VisionModel: mock_env_vars["OPENAI_API_KEY"],
        GeminiModel: mock_env_vars["GEMINI_API_KEY"],
        TwelveLabsModel: mock_env_vars["TWELVE_LABS_API_KEY"],
    }

    # Mock requests.Session for TwelveLabs model
    if model_class == TwelveLabsModel:
        mock_session = MagicMock()
        mock_session.request.side_effect = [
            # Index check response
            MagicMock(
                status_code=200, json=lambda: {"data": [{"name": "default_index"}]}
            ),
            # Upload task creation response
            MagicMock(status_code=200, json=lambda: {"task_id": "test_upload_task_id"}),
            # Upload chunk response
            MagicMock(status_code=204),
            # Upload status response
            MagicMock(
                status_code=200,
                json=lambda: {
                    "status": "completed",
                    "result": {"video_id": "test_video_id"},
                },
            ),
            # Analysis task creation response
            MagicMock(
                status_code=200, json=lambda: {"task_id": "test_analysis_task_id"}
            ),
            # Analysis status response
            MagicMock(
                status_code=200,
                json=lambda: {
                    "status": "completed",
                    "result": {
                        "scene_description": "Test scene",
                        "objects": [{"name": "person"}],
                        "actions": [{"description": "walking"}],
                        "metadata": {
                            "duration": 10,
                            "fps": 30,
                            "resolution": "1920x1080",
                        },
                    },
                },
            ),
        ]
        monkeypatch.setattr("requests.Session", lambda: mock_session)

    model = model_class(api_key=api_key_map[model_class])

    # Update paths to use actual test files
    if "image_path" in input_data:
        input_data["image_path"] = str(test_image)
    if "video_path" in input_data:
        input_data["video_path"] = str(test_video)

    # Test validation
    assert model.validate(input_data)

    # Test processing
    result = model.process(input_data)
    assert isinstance(result, dict)


def test_model_retry_mechanism():
    """Test retry mechanism for failed API calls."""
    model = MockBaseModel()
    mock_func = Mock(
        side_effect=[
            Exception("API Error"),
            Exception("API Error"),
            {"success": True},
        ]
    )

    result = model.retry_with_backoff(mock_func)
    assert result["success"]


def test_model_validation():
    """Test input validation for models."""
    model = MockBaseModel()

    with pytest.raises(ValueError):
        model.validate_input(None)

    with pytest.raises(ValueError):
        model.validate_input("")

    assert model.validate_input("valid input") is None


def test_model_resource_cleanup():
    """Test proper resource cleanup after model usage."""
    model = MockBaseModel()

    def test_func():
        model.resources.append("test")
        return True

    result = model.process_with_cleanup(test_func)
    assert result is True
    assert len(model.resources) == 0
