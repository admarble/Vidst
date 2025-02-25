"""Tests for the mock client fixture."""

from pathlib import Path

import pytest


@pytest.mark.asyncio
async def test_mock_client_attributes(mock_client):
    """Test that mock client has all required attributes."""
    assert mock_client.API_BASE_URL == "https://api.twelvelabs.io/v1.3"
    assert mock_client.DEFAULT_INDEX == "default_index"
    assert mock_client.CHUNK_SIZE == 1024 * 1024
    assert mock_client.MAX_RETRIES == 3
    assert mock_client.INITIAL_BACKOFF == 1
    assert mock_client.MAX_BACKOFF == 30


@pytest.mark.asyncio
async def test_mock_client_session_management(mock_client):
    """Test session management methods."""
    session = await mock_client._get_session()
    assert session == mock_client._session
    assert mock_client._rate_limit_remaining == 50
    assert mock_client._rate_limit_reset == 1500000000


@pytest.mark.asyncio
async def test_mock_client_core_methods(mock_client, test_video):
    """Test core API methods."""
    # Test basic request
    result = await mock_client._make_request("GET", "/test")
    assert result == {"status": "success"}

    # Test video upload
    video_id = await mock_client.upload_video(Path(test_video))
    assert video_id == "test_video_id"

    # Test task creation
    task_id = await mock_client.create_task("test_task", video_id)
    assert task_id == "test_task_id"

    # Test task waiting
    task_result = await mock_client.wait_for_task(task_id)
    assert isinstance(task_result, dict)  # TaskResult is a TypedDict
    assert task_result["task_id"] == "test_task_id"
    assert task_result["status"] == "completed"
    assert task_result["result"] == {"data": "test_result"}
    assert task_result["video_id"] == "test_video_id"

    # Test search
    search_result = await mock_client.search("test query")
    assert search_result == {"data": "test_search_result"}

    # Test text generation
    text_result = await mock_client.generate_text("test prompt")
    assert text_result == {"data": "test_text"}

    # Test rate limit info
    rate_limit = await mock_client.get_rate_limit_info()
    assert rate_limit == {"remaining": 50, "reset": 1500000000}


@pytest.mark.asyncio
async def test_mock_client_index_management(mock_client):
    """Test index management methods."""
    # Test listing indexes
    indexes = await mock_client.list_indexes()
    assert indexes == [{"name": "default_index"}]

    # Test creating index
    new_index = await mock_client.create_index()
    assert new_index == {"name": "default_index"}

    # Test getting index
    index = await mock_client.get_index()
    assert index == {"name": "default_index"}

    # Test deleting index
    delete_result = await mock_client.delete_index()
    assert delete_result == {"status": "success"}


@pytest.mark.asyncio
async def test_mock_client_task_management(mock_client):
    """Test task management methods."""
    # Test getting task status
    status = await mock_client.get_task_status("test_task_id")
    assert status == {"status": "completed"}

    # Test canceling task
    cancel_result = await mock_client.cancel_task("test_task_id")
    assert cancel_result == {"status": "cancelled"}

    # Test listing tasks
    tasks = await mock_client.list_tasks()
    assert tasks == [{"task_id": "test_task_id"}]


@pytest.mark.asyncio
async def test_mock_client_cleanup(mock_client):
    """Test cleanup methods."""
    await mock_client.close()
    mock_client.close.assert_called_once()
