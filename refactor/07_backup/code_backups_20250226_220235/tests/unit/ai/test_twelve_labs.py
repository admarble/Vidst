"""Unit tests for the Twelve Labs AI model integration."""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock, call
from datetime import datetime

from video_understanding.ai.models.twelve_labs import (
    TwelveLabsModel,
    TwelveLabsConfig,
    TwelveLabsClient,
    TwelveLabsError,
    TwelveLabsAuthError,
    TwelveLabsRateLimitError,
)


@pytest.fixture
def twelve_labs_config():
    """Create a TwelveLabsConfig for testing."""
    return TwelveLabsConfig(
        api_key="test_api_key",
        api_url="https://api.twelvelabs.io/v1",
        index_id="test_index_id",
        model_id="test_model_id",
    )


@pytest.fixture
def mock_client():
    """Mock the TwelveLabsClient."""
    with patch("video_understanding.ai.models.twelve_labs.TwelveLabsClient") as mock:
        client_instance = MagicMock()
        mock.return_value = client_instance
        yield client_instance


class TestTwelveLabsConfig:
    """Tests for TwelveLabsConfig."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        config = TwelveLabsConfig(
            api_key="test_api_key",
            index_id="test_index_id",
        )

        assert config.api_key == "test_api_key"
        assert config.index_id == "test_index_id"
        assert config.api_url == "https://api.twelvelabs.io/v1"
        assert config.model_id is None

    def test_init_with_all_params(self):
        """Test initialization with all parameters."""
        config = TwelveLabsConfig(
            api_key="test_api_key",
            index_id="test_index_id",
            api_url="https://custom-api.example.com",
            model_id="custom_model_id",
        )

        assert config.api_key == "test_api_key"
        assert config.index_id == "test_index_id"
        assert config.api_url == "https://custom-api.example.com"
        assert config.model_id == "custom_model_id"

    def test_validation(self):
        """Test configuration validation."""
        # Missing required fields
        with pytest.raises(ValueError):
            TwelveLabsConfig(api_key="", index_id="test_index_id")

        with pytest.raises(ValueError):
            TwelveLabsConfig(api_key="test_api_key", index_id="")

        # Invalid API URL
        with pytest.raises(ValueError):
            TwelveLabsConfig(
                api_key="test_api_key",
                index_id="test_index_id",
                api_url="not-a-url",
            )


class TestTwelveLabsClient:
    """Tests for TwelveLabsClient."""

    @pytest.fixture
    def client(self, twelve_labs_config):
        """Create a TwelveLabsClient instance for testing."""
        return TwelveLabsClient(config=twelve_labs_config)

    def test_init(self, twelve_labs_config):
        """Test client initialization."""
        client = TwelveLabsClient(config=twelve_labs_config)

        assert client.api_key == twelve_labs_config.api_key
        assert client.api_url == twelve_labs_config.api_url
        assert client.index_id == twelve_labs_config.index_id
        assert client.model_id == twelve_labs_config.model_id

    @patch("requests.get")
    def test_get_request(self, mock_get, client):
        """Test GET request method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test_data"}
        mock_get.return_value = mock_response

        # Call method
        endpoint = "test_endpoint"
        params = {"param1": "value1"}
        response = client._get_request(endpoint, params=params)

        # Verify
        assert response == {"data": "test_data"}
        mock_get.assert_called_once_with(
            f"{client.api_url}/test_endpoint",
            headers={"x-api-key": client.api_key},
            params=params,
        )

    @patch("requests.post")
    def test_post_request(self, mock_post, client):
        """Test POST request method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test_data"}
        mock_post.return_value = mock_response

        # Call method
        endpoint = "test_endpoint"
        payload = {"key": "value"}
        response = client._post_request(endpoint, payload=payload)

        # Verify
        assert response == {"data": "test_data"}
        mock_post.assert_called_once_with(
            f"{client.api_url}/test_endpoint",
            headers={"x-api-key": client.api_key},
            json=payload,
        )

    @patch("requests.put")
    def test_put_request(self, mock_put, client):
        """Test PUT request method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test_data"}
        mock_put.return_value = mock_response

        # Call method
        endpoint = "test_endpoint"
        payload = {"key": "value"}
        response = client._put_request(endpoint, payload=payload)

        # Verify
        assert response == {"data": "test_data"}
        mock_put.assert_called_once_with(
            f"{client.api_url}/test_endpoint",
            headers={"x-api-key": client.api_key},
            json=payload,
        )

    @patch("requests.delete")
    def test_delete_request(self, mock_delete, client):
        """Test DELETE request method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test_data"}
        mock_delete.return_value = mock_response

        # Call method
        endpoint = "test_endpoint"
        response = client._delete_request(endpoint)

        # Verify
        assert response == {"data": "test_data"}
        mock_delete.assert_called_once_with(
            f"{client.api_url}/test_endpoint",
            headers={"x-api-key": client.api_key},
        )

    @patch("requests.post")
    def test_error_handling(self, mock_post, client):
        """Test error handling in requests."""
        # Test 401 Unauthorized
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Unauthorized"}
        mock_post.return_value = mock_response

        with pytest.raises(TwelveLabsAuthError):
            client._post_request("test_endpoint", {})

        # Test 429 Rate Limit
        mock_response.status_code = 429
        mock_response.json.return_value = {"message": "Rate limit exceeded"}

        with pytest.raises(TwelveLabsRateLimitError):
            client._post_request("test_endpoint", {})

        # Test other errors
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Server error"}

        with pytest.raises(TwelveLabsError):
            client._post_request("test_endpoint", {})

    @patch("requests.post")
    def test_upload_video(self, mock_post, client):
        """Test video upload functionality."""
        # Mock file and response
        mock_file = MagicMock()
        mock_file.name = "test_video.mp4"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "_id": "video_id_123",
            "status": "processing",
        }
        mock_post.return_value = mock_response

        # Call method
        video_id = client.upload_video(mock_file, "test_video")

        # Verify
        assert video_id == "video_id_123"
        mock_post.assert_called_once()

        # The first positional arg should be the correct URL
        args, kwargs = mock_post.call_args
        assert args[0] == f"{client.api_url}/indexes/{client.index_id}/videos"

        # Files and data should be in the kwargs
        assert "files" in kwargs
        assert "data" in kwargs
        assert kwargs["data"]["title"] == "test_video"

    @patch("requests.get")
    def test_get_video_status(self, mock_get, client):
        """Test getting video status."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "_id": "video_id_123",
            "status": "ready",
        }
        mock_get.return_value = mock_response

        # Call method
        video_id = "video_id_123"
        status = client.get_video_status(video_id)

        # Verify
        assert status == "ready"
        mock_get.assert_called_once_with(
            f"{client.api_url}/indexes/{client.index_id}/videos/{video_id}",
            headers={"x-api-key": client.api_key},
            params=None,
        )

    @patch("requests.post")
    def test_search_video(self, mock_post, client):
        """Test video search functionality."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "video_id": "video_id_123",
                    "score": 0.95,
                    "timestamps": [{"start": 10.5, "end": 20.5}],
                }
            ]
        }
        mock_post.return_value = mock_response

        # Call method
        query = "people walking on the street"
        search_params = {
            "search_options": ["visual", "conversation", "text_in_video"],
            "group_by": "video",
            "threshold": 0.6,
        }
        results = client.search_video(query, search_params)

        # Verify
        assert len(results) == 1
        assert results[0]["video_id"] == "video_id_123"
        assert results[0]["score"] == 0.95
        mock_post.assert_called_once()

        # Verify call parameters
        args, kwargs = mock_post.call_args
        assert args[0] == f"{client.api_url}/search"
        assert kwargs["json"]["index_id"] == client.index_id
        assert kwargs["json"]["query"] == query


class TestTwelveLabsModel:
    """Tests for TwelveLabsModel."""

    @pytest.fixture
    def model(self, twelve_labs_config, mock_client):
        """Create a TwelveLabsModel instance for testing."""
        return TwelveLabsModel(config=twelve_labs_config)

    def test_init(self, twelve_labs_config, mock_client):
        """Test model initialization."""
        model = TwelveLabsModel(config=twelve_labs_config)

        assert model.client is not None
        assert model.config == twelve_labs_config

    @patch("video_understanding.ai.models.twelve_labs.TwelveLabsClient")
    def test_process_video(self, mock_client_class, twelve_labs_config):
        """Test video processing."""
        # Setup mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.upload_video.return_value = "video_id_123"

        # Mock video file
        mock_file = MagicMock()
        mock_file.name = "test_video.mp4"

        # Create model and call process_video
        model = TwelveLabsModel(config=twelve_labs_config)
        video_id = model.process_video(mock_file, "test_video")

        # Verify
        assert video_id == "video_id_123"
        mock_client.upload_video.assert_called_once_with(mock_file, "test_video")

    @patch("video_understanding.ai.models.twelve_labs.TwelveLabsClient")
    def test_get_video_status(self, mock_client_class, twelve_labs_config):
        """Test getting video status."""
        # Setup mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_video_status.return_value = "ready"

        # Create model and call get_video_status
        model = TwelveLabsModel(config=twelve_labs_config)
        status = model.get_video_status("video_id_123")

        # Verify
        assert status == "ready"
        mock_client.get_video_status.assert_called_once_with("video_id_123")

    @patch("video_understanding.ai.models.twelve_labs.TwelveLabsClient")
    def test_search_video(self, mock_client_class, twelve_labs_config):
        """Test video search."""
        # Setup mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_results = [
            {
                "video_id": "video_id_123",
                "score": 0.95,
                "timestamps": [{"start": 10.5, "end": 20.5}],
            }
        ]
        mock_client.search_video.return_value = mock_results

        # Create model and call search_video
        model = TwelveLabsModel(config=twelve_labs_config)
        query = "people walking on the street"
        results = model.search_video(query)

        # Verify
        assert results == mock_results
        mock_client.search_video.assert_called_once()

        # Check that default search options are provided
        args, kwargs = mock_client.search_video.call_args
        assert args[0] == query
        assert "search_options" in kwargs.get("search_params", {})

    @patch("video_understanding.ai.models.twelve_labs.TwelveLabsClient")
    def test_search_by_text(self, mock_client_class, twelve_labs_config):
        """Test search by text."""
        # Setup mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_results = [
            {
                "video_id": "video_id_123",
                "score": 0.95,
                "timestamps": [{"start": 10.5, "end": 20.5}],
            }
        ]
        mock_client.search_video.return_value = mock_results

        # Create model and call search_by_text
        model = TwelveLabsModel(config=twelve_labs_config)
        query = "people walking on the street"
        results = model.search_by_text(query)

        # Verify
        assert results == mock_results
        mock_client.search_video.assert_called_once()

        # Check that only conversation search option is provided
        args, kwargs = mock_client.search_video.call_args
        assert args[0] == query
        assert kwargs.get("search_params", {}).get("search_options") == ["conversation"]

    @patch("video_understanding.ai.models.twelve_labs.TwelveLabsClient")
    def test_search_by_visual(self, mock_client_class, twelve_labs_config):
        """Test search by visual."""
        # Setup mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_results = [
            {
                "video_id": "video_id_123",
                "score": 0.95,
                "timestamps": [{"start": 10.5, "end": 20.5}],
            }
        ]
        mock_client.search_video.return_value = mock_results

        # Create model and call search_by_visual
        model = TwelveLabsModel(config=twelve_labs_config)
        query = "a person wearing red shirt"
        results = model.search_by_visual(query)

        # Verify
        assert results == mock_results
        mock_client.search_video.assert_called_once()

        # Check that only visual search option is provided
        args, kwargs = mock_client.search_video.call_args
        assert args[0] == query
        assert kwargs.get("search_params", {}).get("search_options") == ["visual"]

    @patch("video_understanding.ai.models.twelve_labs.TwelveLabsClient")
    def test_search_by_text_in_video(self, mock_client_class, twelve_labs_config):
        """Test search by text in video."""
        # Setup mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_results = [
            {
                "video_id": "video_id_123",
                "score": 0.95,
                "timestamps": [{"start": 10.5, "end": 20.5}],
            }
        ]
        mock_client.search_video.return_value = mock_results

        # Create model and call search_by_text_in_video
        model = TwelveLabsModel(config=twelve_labs_config)
        query = "matplotlib"
        results = model.search_by_text_in_video(query)

        # Verify
        assert results == mock_results
        mock_client.search_video.assert_called_once()

        # Check that only text_in_video search option is provided
        args, kwargs = mock_client.search_video.call_args
        assert args[0] == query
        assert kwargs.get("search_params", {}).get("search_options") == [
            "text_in_video"
        ]

    @patch("video_understanding.ai.models.twelve_labs.TwelveLabsClient")
    def test_get_video_tasks(self, mock_client_class, twelve_labs_config):
        """Test getting video tasks."""
        # Setup mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client._get_request.return_value = {
            "data": [
                {
                    "type": "scene_detection",
                    "status": "completed",
                },
                {
                    "type": "transcription",
                    "status": "completed",
                },
            ]
        }

        # Create model and call get_video_tasks
        model = TwelveLabsModel(config=twelve_labs_config)
        tasks = model.get_video_tasks("video_id_123")

        # Verify
        assert len(tasks) == 2
        assert tasks[0]["type"] == "scene_detection"
        assert tasks[1]["type"] == "transcription"
        mock_client._get_request.assert_called_once_with(
            f"indexes/{twelve_labs_config.index_id}/videos/video_id_123/tasks",
            params=None,
        )

    @patch("video_understanding.ai.models.twelve_labs.TwelveLabsClient")
    def test_get_scenes(self, mock_client_class, twelve_labs_config):
        """Test getting video scenes."""
        # Setup mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client._get_request.return_value = {
            "data": [
                {
                    "scene_id": "scene_1",
                    "start": 0.0,
                    "end": 10.5,
                },
                {
                    "scene_id": "scene_2",
                    "start": 10.5,
                    "end": 20.0,
                },
            ]
        }

        # Create model and call get_scenes
        model = TwelveLabsModel(config=twelve_labs_config)
        scenes = model.get_scenes("video_id_123")

        # Verify
        assert len(scenes) == 2
        assert scenes[0]["scene_id"] == "scene_1"
        assert scenes[0]["start"] == 0.0
        assert scenes[0]["end"] == 10.5
        mock_client._get_request.assert_called_once_with(
            f"indexes/{twelve_labs_config.index_id}/videos/video_id_123/scenes",
            params=None,
        )

    @patch("video_understanding.ai.models.twelve_labs.TwelveLabsClient")
    def test_get_transcription(self, mock_client_class, twelve_labs_config):
        """Test getting video transcription."""
        # Setup mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client._get_request.return_value = {
            "data": [
                {
                    "text": "Hello world",
                    "start": 0.0,
                    "end": 2.5,
                },
                {
                    "text": "This is a test",
                    "start": 2.5,
                    "end": 5.0,
                },
            ]
        }

        # Create model and call get_transcription
        model = TwelveLabsModel(config=twelve_labs_config)
        transcription = model.get_transcription("video_id_123")

        # Verify
        assert len(transcription) == 2
        assert transcription[0]["text"] == "Hello world"
        assert transcription[0]["start"] == 0.0
        assert transcription[0]["end"] == 2.5
        mock_client._get_request.assert_called_once_with(
            f"indexes/{twelve_labs_config.index_id}/videos/video_id_123/transcription",
            params=None,
        )

    @patch("video_understanding.ai.models.twelve_labs.TwelveLabsClient")
    def test_get_text_in_video(self, mock_client_class, twelve_labs_config):
        """Test getting text in video."""
        # Setup mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client._get_request.return_value = {
            "data": [
                {
                    "text": "Title",
                    "start": 0.0,
                    "end": 2.5,
                },
                {
                    "text": "Subtitle",
                    "start": 2.5,
                    "end": 5.0,
                },
            ]
        }

        # Create model and call get_text_in_video
        model = TwelveLabsModel(config=twelve_labs_config)
        text_in_video = model.get_text_in_video("video_id_123")

        # Verify
        assert len(text_in_video) == 2
        assert text_in_video[0]["text"] == "Title"
        assert text_in_video[0]["start"] == 0.0
        assert text_in_video[0]["end"] == 2.5
        mock_client._get_request.assert_called_once_with(
            f"indexes/{twelve_labs_config.index_id}/videos/video_id_123/text_in_video",
            params=None,
        )

    @patch("video_understanding.ai.models.twelve_labs.TwelveLabsClient")
    def test_delete_video(self, mock_client_class, twelve_labs_config):
        """Test deleting a video."""
        # Setup mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client._delete_request.return_value = {"message": "Video deleted"}

        # Create model and call delete_video
        model = TwelveLabsModel(config=twelve_labs_config)
        result = model.delete_video("video_id_123")

        # Verify
        assert result == {"message": "Video deleted"}
        mock_client._delete_request.assert_called_once_with(
            f"indexes/{twelve_labs_config.index_id}/videos/video_id_123"
        )
