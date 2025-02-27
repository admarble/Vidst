from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import ClientError, ClientSession
from multidict import CIMultiDict


class TwelveLabsModel:
    """Mock TwelveLabsModel class for testing."""

    def __init__(self, api_key):
        self.api_key = api_key
        self._session = None
        self._base_url = "https://api.twelvelabs.io/v1.1"

    async def _ensure_session(self):
        """Ensure session is initialized."""
        if self._session is None:
            self._session = ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
        return self._session

    async def _make_request(self, method, endpoint, **kwargs):
        """Make HTTP request."""
        session = await self._ensure_session()
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        url = self._base_url + endpoint
        async with session.request(method, url, **kwargs) as response:
            return await response.json()


class MockClientResponse:
    def __init__(self, status, json_data):
        self.status = status
        self._json_data = json_data
        self.headers = CIMultiDict()

    async def json(self):
        return self._json_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def mock_session():
    """Create a mock session."""
    mock = AsyncMock(spec=ClientSession)
    mock.closed = False
    mock.headers = CIMultiDict(
        {"Authorization": "Bearer test_key", "Content-Type": "application/json"}
    )

    async def mock_request(method, url, **kwargs):
        # Create a mock response based on the request
        return MockClientResponse(200, {"data": "test"})

    mock.request = mock_request
    return mock


@pytest.fixture
def model(mock_session):
    """Create a model instance with mock session."""
    with patch("aiohttp.ClientSession", return_value=mock_session):
        model = TwelveLabsModel(api_key="test_key")
        return model


def create_mock_response(status_code=200, json_data=None):
    """Create a mock response with specified status code and JSON data."""
    return MockClientResponse(status_code, json_data or {})


@pytest.mark.asyncio
async def test_session_management(model, mock_session):
    """Test basic session management."""
    session = await model._ensure_session()
    assert session == mock_session


@pytest.mark.asyncio
async def test_session_headers(model, mock_session):
    """Test session headers are properly set."""
    # Mock successful response for index list
    response = create_mock_response(
        status_code=200, json_data={"data": [{"name": "default_index"}]}
    )
    mock_session.request = AsyncMock(return_value=response)

    # Initialize session and make a request
    session = await model._ensure_session()

    # Test headers are set correctly
    assert session.headers == {
        "Authorization": "Bearer test_key",
        "Content-Type": "application/json",
    }

    # Verify headers persist after request
    result = await model._make_request("GET", "/indexes")
    assert result == {"data": [{"name": "default_index"}]}


@pytest.mark.asyncio
async def test_session_initialization_failure():
    """Test handling of session initialization failure."""
    # Mock ClientSession to raise an error
    with patch("aiohttp.ClientSession", side_effect=ClientError()):
        model = TwelveLabsModel(api_key="test_key")
        with pytest.raises(ClientError):
            await model._ensure_session()


@pytest.mark.asyncio
async def test_request_failure(model, mock_session):
    """Test handling of request failures."""
    # Mock a failed request
    error_response = create_mock_response(
        status_code=500, json_data={"error": "Internal Server Error"}
    )
    mock_session.request = AsyncMock(return_value=error_response)

    result = await model._make_request("GET", "/indexes")
    assert result == {"error": "Internal Server Error"}


@pytest.mark.asyncio
async def test_invalid_api_key(mock_session):
    """Test handling of invalid API key."""
    # Mock unauthorized response
    error_response = create_mock_response(
        status_code=401, json_data={"error": "Invalid API key"}
    )
    mock_session.request = AsyncMock(return_value=error_response)

    model = TwelveLabsModel(api_key="invalid_key")
    result = await model._make_request("GET", "/indexes")
    assert result == {"error": "Invalid API key"}


@pytest.mark.asyncio
async def test_empty_response(model, mock_session):
    """Test handling of empty responses."""
    # Mock empty response
    empty_response = create_mock_response(status_code=200, json_data={})
    mock_session.request = AsyncMock(return_value=empty_response)

    result = await model._make_request("GET", "/indexes")
    assert result == {}


@pytest.mark.asyncio
async def test_different_http_methods(model, mock_session):
    """Test different HTTP methods."""
    methods = ["GET", "POST", "PUT", "DELETE"]

    for method in methods:
        response = create_mock_response(status_code=200, json_data={"method": method})
        mock_session.request = AsyncMock(return_value=response)

        result = await model._make_request(method, "/test")
        assert result == {"method": method}


@pytest.mark.asyncio
async def test_concurrent_requests(model, mock_session):
    """Test handling of concurrent requests."""
    import asyncio

    # Create multiple requests
    async def make_request(index):
        response = create_mock_response(status_code=200, json_data={"index": index})
        mock_session.request = AsyncMock(return_value=response)
        return await model._make_request("GET", f"/test/{index}")

    # Run multiple requests concurrently
    tasks = [make_request(i) for i in range(5)]
    results = await asyncio.gather(*tasks)

    # Verify results
    for i, result in enumerate(results):
        assert result == {"index": i}
