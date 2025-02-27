"""Tests for TwelveLabsModel error handling."""

from unittest.mock import patch

import pytest

from video_understanding.ai.exceptions.twelve_labs import (
    RateLimitError,
    TwelveLabsError,
)

from .conftest import create_mock_response


@pytest.mark.asyncio
async def test_ensure_index_exists(model, mock_client):
    """Test ensuring index exists."""
    # Mock successful index list response
    mock_client.list_indexes.return_value = [{"name": "default_index"}]

    await model._ensure_index()
    mock_client.list_indexes.assert_called_once()


@pytest.mark.asyncio
async def test_retry_with_backoff(model, mock_client):
    """Test retry mechanism with exponential backoff."""
    # First attempt fails with rate limit
    mock_client.search.side_effect = [
        RateLimitError("Rate limit exceeded"),
        {"status": "success"},
    ]

    with patch("asyncio.sleep") as mock_sleep:  # Mock sleep to avoid actual delays
        result = await model.search("test query")
        assert result == {"status": "success"}
        assert mock_client.search.call_count == 2
        mock_sleep.assert_called_once()


@pytest.mark.asyncio
async def test_handle_rate_limit_headers(model, mock_client):
    """Test proper handling of rate limit headers."""
    mock_client.search.return_value = {"status": "success"}
    mock_client.get_rate_limit_info.return_value = {
        "remaining": 50,
        "reset": 1500000000,
    }

    result = await model.search("test query")
    assert result == {"status": "success"}
    assert mock_client.get_rate_limit_info.call_count == 1


@pytest.mark.asyncio
async def test_ensure_index_create(model, mock_session):
    """Test index creation."""
    # Mock empty index list and successful creation
    mock_session.request.side_effect = [
        create_mock_response(status_code=200, json_data={"data": []}),
        create_mock_response(status_code=200, json_data={"status": "success"}),
    ]

    await model._ensure_index()
    assert mock_session.request.call_count == 2

    # Verify create index call
    create_call = mock_session.request.call_args_list[1]
    assert create_call[0][0] == "POST"
    assert create_call[0][1].endswith("/indexes")
    assert "json" in create_call[1]
    assert create_call[1]["json"] == {
        "name": model.DEFAULT_INDEX,
        "engine": "marengo2.5",
    }


@pytest.mark.asyncio
async def test_track_task_status(model, mock_session):
    """Test task status tracking."""
    # First response - pending
    pending_response = create_mock_response(
        status_code=200,
        json_data={
            "task_id": "test_task_id",
            "status": "pending",
            "video_id": "test_video_id",
        },
    )

    # Second response - completed
    completed_response = create_mock_response(
        status_code=200,
        json_data={
            "task_id": "test_task_id",
            "status": "completed",
            "result": {"data": "test_result"},
            "video_id": "test_video_id",
            "error": None,
        },
    )

    mock_session.request.side_effect = [pending_response, completed_response]

    result = await model._track_task_status("task_123")
    assert result["task_id"] == "test_task_id"
    assert result["status"] == "completed"
    assert result["result"]["data"] == "test_result"
    assert result["video_id"] == "test_video_id"
    assert result["error"] is None


@pytest.mark.asyncio
async def test_track_task_status_failure(model, mock_session):
    """Test task status tracking with failure."""
    failed_response = create_mock_response(
        status_code=200,
        json_data={
            "task_id": "test_task_id",
            "status": "failed",
            "error": "Processing failed",
            "video_id": "test_video_id",
        },
    )

    mock_session.request.side_effect = [failed_response]

    with pytest.raises(TwelveLabsError, match="Task failed: Processing failed"):
        await model._track_task_status("task_123")
