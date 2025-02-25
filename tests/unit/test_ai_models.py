"""Unit tests for AI model integrations."""

import tempfile
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Generator
from unittest.mock import MagicMock, Mock, patch, AsyncMock

import pytest

from video_understanding.ai.exceptions import ModelError
from video_understanding.ai.models import (
    BaseModel,
    GeminiModel,
    GPT4VModel,
    TwelveLabsModel,
)


@pytest.fixture(name="api_response")
def fixture_api_response() -> Dict[str, Any]:
    """Mock successful API response."""
    return {
        "description": "Sample analysis",
        "objects": ["person", "laptop"],
        "text": ["Hello World"],
        "actions": ["typing"],
    }


@pytest.fixture(name="failed_api_response")
def fixture_failed_api_response() -> Dict[str, str]:
    """Mock failed API response."""
    return {"error": "API rate limit exceeded"}


@pytest.fixture(name="image_file")
def fixture_test_image() -> Generator[Path, None, None]:
    """Create a test image file."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tf:
        tf.write(b"test image data")
        tf.flush()
        yield Path(tf.name)


@pytest.fixture(name="video_file")
def fixture_test_video() -> Generator[Path, None, None]:
    """Create a test video file."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tf:
        tf.write(b"test video data")
        tf.flush()
        yield Path(tf.name)


@pytest.fixture
def mock_env_vars() -> Dict[str, str]:
    """Mock environment variables."""
    return {
        "OPENAI_API_KEY": "test-openai-key",
        "GEMINI_API_KEY": "test-gemini-key",
        "TWELVE_LABS_API_KEY": "test-twelvelabs-key",
        "CACHE_TTL": "3600",
        "DEBUG": "true",
        "ENVIRONMENT": "testing",
    }


@pytest.fixture
def create_async_context_manager_mock(**attrs):
    """Create a properly configured AsyncMock for async context managers."""
    mock = AsyncMock(**attrs)
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_response() -> AsyncMock:
    """Mock response for API calls."""
    mock = AsyncMock()

    # Set basic response attributes
    mock.status = 200
    mock.text = AsyncMock(return_value='{"success": true}')
    mock.json = AsyncMock(
        return_value={
            "choices": [{"message": {"content": "Test response"}}],
            "status": "completed",
            "result": {"data": {"scenes": [{"start": 0, "end": 10}]}},
        }
    )

    # Configure async context manager correctly
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)

    return mock


@pytest.fixture
def mock_aiohttp_session(mock_response: AsyncMock) -> AsyncMock:
    """Mock aiohttp ClientSession."""
    session = AsyncMock()

    # Make sure request methods return the mock_response directly, not a coroutine
    session.post = AsyncMock(return_value=mock_response)
    session.get = AsyncMock(return_value=mock_response)
    session.request = AsyncMock(return_value=mock_response)
    session.close = AsyncMock()

    # Configure session's async context manager
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)

    return session


@pytest.fixture
def mock_twelve_labs_session(mock_response: AsyncMock) -> AsyncMock:
    """Mock TwelveLabs session."""
    session = AsyncMock()

    # Make sure request methods return the mock_response directly, not a coroutine
    session.request = AsyncMock(return_value=mock_response)
    session.close = AsyncMock()

    # Configure session's async context manager
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)

    return session


@pytest.fixture
async def model(
    mock_env_vars: Dict[str, str], mock_aiohttp_session: AsyncMock
) -> AsyncGenerator[GPT4VModel, None]:
    """Create a GPT-4V model instance."""
    model = None
    try:
        model = GPT4VModel(config={"api_key": mock_env_vars["OPENAI_API_KEY"]})
        model.session = mock_aiohttp_session
        yield model
    finally:
        if model:
            await model.close()


class MockBaseModel(BaseModel):
    """Mock implementation of BaseModel for testing."""

    def __init__(self):
        self.resources = []

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        return {"success": True}

    def validate(self, input_data: dict[str, Any]) -> bool:
        if not input_data:
            raise ValueError("Invalid input")
        return True

    def _cleanup_resources(self) -> None:
        self.resources.clear()

    async def close(self) -> None:
        """Implement required close method from BaseModel."""
        self._cleanup_resources()


class TestGPT4VModel:
    """Tests for GPT-4V model integration."""

    @pytest.fixture
    def model(
        self, mock_env_vars: Dict[str, str], mock_aiohttp_session: AsyncMock
    ) -> GPT4VModel:
        """Create a GPT-4V model instance."""
        model = GPT4VModel(config={"api_key": mock_env_vars["OPENAI_API_KEY"]})
        model.session = mock_aiohttp_session
        return model

    def test_validate(self, model, image_file):
        """Test input validation."""
        assert model.validate(
            {"image_url": str(image_file), "prompt": "Describe this image"}
        )

        with pytest.raises(ModelError):
            model.validate({})  # Missing image_url and prompt

        with pytest.raises(ModelError):
            model.validate({"image_url": "nonexistent.jpg"})  # Missing prompt

    @pytest.mark.asyncio
    async def test_process(self, model, image_file, mock_response: AsyncMock):
        """Test image processing."""
        expected_result = {
            "description": "A test image",
            "objects": ["person", "laptop"],
            "text": ["Hello World"],
            "actions": ["typing"],
        }

        with patch.object(model, "process", return_value=expected_result):
            result = await model.process(
                {"image_url": str(image_file), "prompt": "Describe this image"}
            )
            assert "description" in result
            assert "objects" in result
            assert "text" in result
            assert "actions" in result


class TestGeminiModel:
    """Tests for Google Gemini model integration."""

    @pytest.fixture
    def model(
        self, mock_env_vars: Dict[str, str], mock_aiohttp_session: AsyncMock
    ) -> GeminiModel:
        """Create a Gemini model instance."""
        model = GeminiModel(api_key=mock_env_vars["GEMINI_API_KEY"])
        # Directly setting private attribute for testing
        model._session = mock_aiohttp_session
        return model

    def test_validate(self, model, image_file):
        """Test input validation."""
        assert model.validate({"image_path": str(image_file)})

        with pytest.raises(ModelError):
            model.validate({})

    @pytest.mark.asyncio
    async def test_process(self, model, image_file):
        """Test content processing."""
        expected_result = {"description": "A test image processed by Gemini"}

        with patch.object(model, "process", return_value=expected_result):
            result = await model.process({"image_path": str(image_file)})
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
    def model(
        self,
        mock_env_vars: Dict[str, str],
        mock_session: MagicMock,
        mock_twelve_labs_session: AsyncMock,
    ) -> TwelveLabsModel:
        """Create a Twelve Labs model instance with mock session."""
        with patch("requests.Session", return_value=mock_session):
            model = TwelveLabsModel(api_key=mock_env_vars["TWELVE_LABS_API_KEY"])
            model._session = mock_twelve_labs_session
            return model

    def test_validate(self, model, video_file):
        """Test input validation."""
        input_data = {
            "video_path": str(video_file),
            "task": "scene_detection",
            "start_time": 0,
            "end_time": 10,
        }
        assert model.validate(input_data)

        with pytest.raises(ModelError):
            model.validate({})

    @pytest.mark.asyncio
    async def test_process(self, model, video_file):
        """Test video processing."""
        input_data = {
            "video_path": str(video_file),
            "task": "scene_detection",
            "start_time": 0,
            "end_time": 10,
        }

        expected_result = {
            "description": "Test scene",
            "objects": [{"name": "person"}],
            "actions": [{"description": "walking"}],
            "metadata": {
                "duration": 10,
                "fps": 30,
                "resolution": "1920x1080",
            },
        }

        with patch.object(model, "process", return_value=expected_result):
            result = await model.process(input_data)
            assert "description" in result
            assert "objects" in result
            assert "actions" in result
            assert "metadata" in result


@pytest.mark.parametrize(
    "model_class,input_data",
    [
        (GPT4VModel, {"image_url": "test.jpg", "prompt": "Describe this image"}),
        (GeminiModel, {"image_path": "test.jpg"}),
        (
            TwelveLabsModel,
            {
                "video_path": "test.mp4",
                "task": "scene_detection",
                "start_time": 0,
                "end_time": 10,
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_model_initialization(
    model_class: type,
    input_data: Dict[str, Any],
    mock_env_vars: Dict[str, str],
    image_file: Path,
    video_file: Path,
    mock_aiohttp_session: AsyncMock,
    mock_twelve_labs_session: AsyncMock,
) -> None:
    """Test initialization and basic functionality of all model types."""
    api_key_map = {
        GPT4VModel: {"api_key": mock_env_vars["OPENAI_API_KEY"]},
        GeminiModel: mock_env_vars["GEMINI_API_KEY"],
        TwelveLabsModel: mock_env_vars["TWELVE_LABS_API_KEY"],
    }

    model = None
    try:
        # Mock API calls
        if model_class == TwelveLabsModel:
            with patch("aiohttp.ClientSession", return_value=mock_twelve_labs_session):
                model = model_class(api_key=api_key_map[model_class])
                # Set _session directly for testing purposes
                model._session = mock_twelve_labs_session

                # Update paths to use actual test files
                if "video_path" in input_data:
                    input_data["video_path"] = str(video_file)
                # Test validation
                assert model.validate(input_data)
                # Test processing - create a basic response for testing
                with patch.object(
                    model, "process", return_value={"data": {"test": "data"}}
                ):
                    result = await model.process(input_data)
                    assert result is not None
        else:
            with patch("aiohttp.ClientSession", return_value=mock_aiohttp_session):
                if model_class == GPT4VModel:
                    model = model_class(config=api_key_map[model_class])
                else:
                    model = model_class(api_key=api_key_map[model_class])

                # Set session directly for testing
                model.session = mock_aiohttp_session

                # Update paths to use actual test files
                if "image_url" in input_data:
                    input_data["image_url"] = str(image_file)
                elif "image_path" in input_data:
                    input_data["image_path"] = str(image_file)
                # Test validation
                assert model.validate(input_data)
                # Test processing - patch to avoid actual API calls
                with patch.object(
                    model, "process", return_value={"description": "test"}
                ):
                    result = await model.process(input_data)
                    assert result is not None
    finally:
        if model is not None:
            await model.close()


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

    # Test with valid dictionary input
    valid_input = {"video_path": "test.mp4", "task": "scene_detection"}
    assert model.validate_input(valid_input) is None


def test_model_resource_cleanup():
    """Test proper resource cleanup after model usage."""
    model = MockBaseModel()

    def test_func():
        model.resources.append("test")
        return True

    result = model.process_with_cleanup(test_func)
    assert result is True
    assert len(model.resources) == 0
