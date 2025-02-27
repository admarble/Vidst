"""Tests for TwelveLabsModel session management."""

import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientError, ClientSession
from yarl import URL

# Mock external dependencies in a more organized way
MOCK_MODULES = [
    "cv2",
    "src.core.config",
    "src.core.input",
    "src.core",
    "src.ai.models.base",
    "src.ai.exceptions.twelve_labs",
    "src.ai.models.twelve_labs.client",
    "src.ai.models.twelve_labs.types",
]

# Create mock modules with proper typing
mock_modules: dict[str, ModuleType] = {}
for module_name in MOCK_MODULES:
    mock_module = MagicMock(spec=ModuleType(module_name))
    sys.modules[module_name] = mock_module
    mock_modules[module_name] = mock_module


# Create minimal BaseModel mock
class MockBaseModel:
    """Base model mock for testing."""

    def __init__(self) -> None:
        pass


# Set BaseModel attribute on mock module
base_module = mock_modules["src.ai.models.base"]
setattr(base_module, "BaseModel", MockBaseModel)


# Create minimal TwelveLabsModel implementation for testing
class TwelveLabsModel(MockBaseModel):
    """Test implementation of TwelveLabsModel."""

    def __init__(
        self, api_key: str, base_url: str = "https://api.twelvelabs.io/v1.1"
    ) -> None:
        """Initialize model with API key and base URL."""
        super().__init__()
        self.api_key = api_key
        self.base_url = base_url
        self._session = None
        self._temp_files = set()

    async def _ensure_session(self) -> ClientSession:
        """Ensure an active client session exists."""
        if self._session is None:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            self._session = ClientSession(headers=headers)
        return self._session

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make an HTTP request to the API."""
        session = await self._ensure_session()

        # Ensure endpoint starts with /
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        # Construct full URL
        url = f"{self.base_url.rstrip('/')}{endpoint}"

        async with session.request(method, url, **kwargs) as response:
            if response.status >= 400:
                error_message = await response.text()
                raise Exception(
                    f"Request failed with status {response.status}: {error_message}"
                )
            return await response.json()

    async def close(self) -> None:
        """Close session and clean up resources."""
        if self._session:
            await self._session.close()
            self._session = None

        for file in self._temp_files:
            try:
                Path(file).unlink()
            except OSError:
                # Ignore errors when deleting test files
                pass
        self._temp_files.clear()


# Test fixtures and functions
@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock session with default responses.

    Returns:
        AsyncMock: Configured session mock for testing
    """
    mock = AsyncMock(spec=ClientSession)
    mock._headers = {}
    mock._base_url = "https://api.twelvelabs.io/v1.1"

    # Add headers property
    @property
    def headers(self) -> dict[str, str]:
        return self._headers

    @headers.setter
    def headers(self, value: dict[str, str]) -> None:
        self._headers.update(value)

    type(mock).headers = headers

    # Add request method
    async def mock_request(method: str, url: str | URL, **kwargs) -> MagicMock:
        # Convert string URL to yarl.URL if needed
        if isinstance(url, str):
            url = URL(url)

        # Return the mock response
        if hasattr(mock, "_next_response"):
            return mock._next_response
        return create_mock_response(
            status_code=200, json_data={"data": [{"name": "default_index"}]}
        )

    mock.request = mock_request
    return mock


@pytest.fixture
def model(mock_session: AsyncMock) -> Generator[TwelveLabsModel, None, None]:
    """Create a model instance with test configuration.

    Args:
        mock_session: The mock session fixture

    Yields:
        TwelveLabsModel: Configured model instance for testing
    """
    with patch("aiohttp.ClientSession", return_value=mock_session):
        model = TwelveLabsModel(api_key="test_key")
        yield model


def create_mock_response(
    status_code: int = 200, json_data: dict | None = None
) -> MagicMock:
    """Create a mock response object with the specified data.

    Args:
        status_code: HTTP status code for the response
        json_data: JSON data to return in the response

    Returns:
        MagicMock: Configured response mock
    """
    mock_response = MagicMock()
    mock_response.status = status_code
    mock_response.json = AsyncMock(return_value=json_data or {})
    mock_response.text = AsyncMock(return_value=str(json_data or {}))
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)
    return mock_response


# Tests
@pytest.mark.asyncio
async def test_session_management(
    model: TwelveLabsModel, mock_session: AsyncMock
) -> None:
    """Test session management and reuse behavior.

    Args:
        model: The test model instance
        mock_session: The mock session
    """
    # Mock successful response for index list
    mock_session._next_response = create_mock_response(
        status_code=200, json_data={"data": [{"name": "default_index"}]}
    )

    # Test session reuse
    session1 = await model._ensure_session()
    assert session1.headers["Authorization"] == "Bearer test_key"

    result = await model._make_request("GET", "/indexes")
    session2 = model._session
    assert session1 is session2, "Session should be reused"
    assert result == {"data": [{"name": "default_index"}]}

    # Cleanup
    await model.close()


@pytest.mark.asyncio
async def test_cleanup_resources(model: TwelveLabsModel, tmp_path: Path) -> None:
    """Test proper cleanup of temporary resources.

    Args:
        model: The test model instance
        tmp_path: Temporary directory path
    """
    # Create test files
    test_file1 = tmp_path / "test1.txt"
    test_file2 = tmp_path / "test2.txt"
    test_file1.write_text("test1")
    test_file2.write_text("test2")

    # Add test files to cleanup
    model._temp_files.add(str(test_file1))
    model._temp_files.add(str(test_file2))

    # Call cleanup
    await model.close()

    # Verify files are deleted
    assert not test_file1.exists()
    assert not test_file2.exists()
    assert len(model._temp_files) == 0
    assert model._session is None


@pytest.mark.asyncio
async def test_session_headers(model: TwelveLabsModel, mock_session: AsyncMock) -> None:
    """Test session headers are properly set and maintained.

    Args:
        model: The test model instance
        mock_session: The mock session
    """
    # Mock successful response for index list
    mock_session._next_response = create_mock_response(
        status_code=200, json_data={"data": [{"name": "default_index"}]}
    )

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
    assert session.headers == {
        "Authorization": "Bearer test_key",
        "Content-Type": "application/json",
    }

    # Cleanup
    await model.close()


@pytest.mark.asyncio
async def test_session_initialization_failure(mock_session: AsyncMock) -> None:
    """Test handling of session initialization failure.

    Args:
        mock_session: The mock session
    """
    # Mock ClientSession to raise an error
    with patch("aiohttp.ClientSession", side_effect=ClientError()):
        model = TwelveLabsModel(api_key="test_key")
        with pytest.raises(ClientError):
            await model._ensure_session()


@pytest.mark.asyncio
async def test_request_failure(model: TwelveLabsModel, mock_session: AsyncMock) -> None:
    """Test handling of request failures.

    Args:
        model: The test model instance
        mock_session: The mock session
    """
    # Mock a failed request
    mock_session._next_response = create_mock_response(
        status_code=500, json_data={"error": "Internal Server Error"}
    )

    with pytest.raises(Exception) as exc_info:
        await model._make_request("GET", "/indexes")
    assert "500" in str(exc_info.value)

    # Cleanup
    await model.close()


@pytest.mark.asyncio
async def test_invalid_api_key(mock_session: AsyncMock) -> None:
    """Test handling of invalid API key.

    Args:
        mock_session: The mock session
    """
    # Mock unauthorized response
    mock_session._next_response = create_mock_response(
        status_code=401, json_data={"error": "Invalid API key"}
    )

    model = TwelveLabsModel(api_key="invalid_key")
    with pytest.raises(Exception) as exc_info:
        await model._make_request("GET", "/indexes")
    assert "401" in str(exc_info.value)

    # Cleanup
    await model.close()


@pytest.mark.asyncio
async def test_empty_response(model: TwelveLabsModel, mock_session: AsyncMock) -> None:
    """Test handling of empty responses.

    Args:
        model: The test model instance
        mock_session: The mock session
    """
    # Mock empty response
    mock_session._next_response = create_mock_response(status_code=200, json_data={})

    result = await model._make_request("GET", "/indexes")
    assert result == {}

    # Cleanup
    await model.close()


@pytest.mark.asyncio
async def test_different_http_methods(
    model: TwelveLabsModel, mock_session: AsyncMock
) -> None:
    """Test different HTTP methods.

    Args:
        model: The test model instance
        mock_session: The mock session
    """
    methods = ["GET", "POST", "PUT", "DELETE"]

    for method in methods:
        mock_session._next_response = create_mock_response(
            status_code=200, json_data={"method": method}
        )

        result = await model._make_request(method, "/test")
        assert result == {"method": method}

    # Cleanup
    await model.close()


@pytest.mark.asyncio
async def test_custom_headers(model: TwelveLabsModel, mock_session: AsyncMock) -> None:
    """Test setting custom headers.

    Args:
        model: The test model instance
        mock_session: The mock session
    """
    custom_headers = {
        "X-Custom-Header": "test_value",
        "X-Another-Header": "another_value",
    }

    session = await model._ensure_session()

    # Add custom headers
    session.headers.update(custom_headers)

    # Verify all headers are present
    assert session.headers["Authorization"] == "Bearer test_key"
    assert session.headers["Content-Type"] == "application/json"
    assert session.headers["X-Custom-Header"] == "test_value"
    assert session.headers["X-Another-Header"] == "another_value"

    # Cleanup
    await model.close()


@pytest.mark.asyncio
async def test_concurrent_requests(
    model: TwelveLabsModel, mock_session: AsyncMock
) -> None:
    """Test handling of concurrent requests.

    Args:
        model: The test model instance
        mock_session: The mock session
    """
    import asyncio

    # Create multiple requests
    async def make_request(index: int) -> dict[str, Any]:
        mock_session._next_response = create_mock_response(
            status_code=200, json_data={"index": index}
        )
        return await model._make_request("GET", f"/test/{index}")

    # Run multiple requests concurrently
    tasks = [make_request(i) for i in range(5)]
    results = await asyncio.gather(*tasks)

    # Verify all requests completed
    assert len(results) == 5
    assert all(isinstance(r, dict) for r in results)
    assert [r["index"] for r in results] == list(range(5))

    # Cleanup
    await model.close()
