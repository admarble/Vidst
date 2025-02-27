"""Tests for TwelveLabsModel request handling."""

from unittest.mock import patch

import pytest

from video_understanding.ai.exceptions.twelve_labs import (
    APIError as APITimeoutError,
)
from video_understanding.ai.exceptions.twelve_labs import (
    RateLimitError,
    TwelveLabsError,
)

from .conftest import create_mock_response


@pytest.mark.asyncio
async def test_make_request_rate_limit(model, mock_session):
    """Test rate limit handling."""
    # First request hits rate limit
    rate_limit_response = create_mock_response(
        status_code=429, headers={"X-RateLimit-Reset": "30"}
    )

    mock_session.request.side_effect = RateLimitError(
        "Rate limit exceeded, reset in 30 seconds"
    )

    with pytest.raises(
        RateLimitError, match="Rate limit exceeded, reset in 30 seconds"
    ):
        await model._make_request("GET", "/test")


@pytest.mark.asyncio
async def test_make_request_timeout(model, mock_session):
    """Test timeout handling."""
    mock_session.request.side_effect = APITimeoutError("Request timed out")

    with pytest.raises(APITimeoutError, match="Request timed out"):
        await model._make_request("GET", "/test")


@pytest.mark.asyncio
async def test_make_request_unauthorized_error(model, mock_session):
    """Test unauthorized error handling."""
    mock_session.request.return_value = create_mock_response(
        status_code=401, json_data={"message": "Invalid API key"}
    )

    with pytest.raises(TwelveLabsError, match="Unauthorized: Invalid API key"):
        await model._make_request("GET", "/test")


@pytest.mark.asyncio
async def test_make_request_not_found_error(model, mock_session):
    """Test not found error handling."""
    mock_session.request.return_value = create_mock_response(
        status_code=404, json_data={"message": "Endpoint not found"}
    )

    with pytest.raises(TwelveLabsError, match="Not found: /test"):
        await model._make_request("GET", "/test")


@pytest.mark.asyncio
async def test_make_request_bad_request_error(model, mock_session):
    """Test handling of 400 Bad Request API responses."""
    mock_session.request.return_value = create_mock_response(
        status_code=400, json_data={"error": "Invalid request parameters"}
    )

    with pytest.raises(
        TwelveLabsError, match="Bad request: Invalid request parameters"
    ):
        await model._make_request("GET", "/test")


@pytest.mark.asyncio
async def test_make_request_forbidden(model, mock_session):
    """Test handling of 403 Forbidden API responses."""
    mock_session.request.side_effect = TwelveLabsError("Forbidden: Account suspended")

    with pytest.raises(TwelveLabsError, match="Forbidden: Account suspended"):
        await model._make_request("GET", "/test")


@pytest.mark.asyncio
async def test_make_request_server_error_response(model, mock_session):
    """Test handling of 500 Internal Server Error responses."""
    mock_session.request.return_value = create_mock_response(
        status_code=500, json_data={"message": "Internal server error"}
    )

    with pytest.raises(TwelveLabsError, match="Server error: Internal server error"):
        await model._make_request("GET", "/test")


@pytest.mark.asyncio
async def test_make_request_service_unavailable_error(model, mock_session):
    """Test handling of 503 Service Unavailable responses."""
    mock_session.request.return_value = create_mock_response(
        status_code=503, json_data={"message": "Service temporarily unavailable"}
    )

    with pytest.raises(
        TwelveLabsError, match="Server error: Service temporarily unavailable"
    ):
        await model._make_request("GET", "/test")


@pytest.mark.asyncio
async def test_retry_with_backoff(model, mock_session):
    """Test retry mechanism with exponential backoff."""
    # Create mock responses
    responses = [
        create_mock_response(
            status_code=429,
            headers={"X-RateLimit-Reset": "30"},
            json_data={"message": "Rate limit exceeded"},
        ),
        create_mock_response(
            status_code=429,
            headers={"X-RateLimit-Reset": "30"},
            json_data={"message": "Rate limit exceeded"},
        ),
        create_mock_response(status_code=200, json_data={"status": "success"}),
    ]
    mock_session.request.side_effect = responses

    with patch("asyncio.sleep") as mock_sleep:  # Mock sleep to avoid actual delays
        result = await model._make_request_with_retry("GET", "/test")
        assert result == {"status": "success"}
        assert mock_session.request.call_count == 3
        assert mock_sleep.call_count == 2
        # Verify exponential backoff delays
        assert mock_sleep.call_args_list[0][0][0] == 1.0  # First retry delay
        assert mock_sleep.call_args_list[1][0][0] == 2.0  # Second retry delay


@pytest.mark.asyncio
async def test_handle_rate_limit_headers(model, mock_session):
    """Test proper handling of rate limit headers from API responses."""
    response = create_mock_response(
        status_code=200,
        headers={"X-RateLimit-Remaining": "50", "X-RateLimit-Reset": "1500000000"},
        json_data={"status": "success"},
    )
    mock_session.request.side_effect = [response]

    result = await model._make_request("GET", "/test")
    assert result == {"status": "success"}
    assert mock_session.request.call_count == 1


@pytest.mark.asyncio
async def test_make_request_bad_request(model, mock_client):
    """Test handling of 400 Bad Request API responses."""
    mock_client.search.side_effect = TwelveLabsError("Invalid request parameters")

    with pytest.raises(TwelveLabsError, match="Invalid request parameters"):
        await model.search("test query")


@pytest.mark.asyncio
async def test_make_request_unauthorized(model, mock_client):
    """Test unauthorized error handling."""
    mock_client.search.side_effect = TwelveLabsError("Invalid API key")

    with pytest.raises(TwelveLabsError, match="Invalid API key"):
        await model.search("test query")


@pytest.mark.asyncio
async def test_make_request_not_found(model, mock_client):
    """Test not found error handling."""
    mock_client.search.side_effect = TwelveLabsError("Resource not found")

    with pytest.raises(TwelveLabsError, match="Resource not found"):
        await model.search("test query")


@pytest.mark.asyncio
async def test_make_request_server_error(model, mock_client):
    """Test handling of 500 Internal Server Error responses."""
    mock_client.search.side_effect = TwelveLabsError("Internal server error")

    with pytest.raises(TwelveLabsError, match="Internal server error"):
        await model.search("test query")


@pytest.mark.asyncio
async def test_make_request_service_unavailable(model, mock_client):
    """Test handling of 503 Service Unavailable responses."""
    mock_client.search.side_effect = TwelveLabsError("Service temporarily unavailable")

    with pytest.raises(TwelveLabsError, match="Service temporarily unavailable"):
        await model.search("test query")
