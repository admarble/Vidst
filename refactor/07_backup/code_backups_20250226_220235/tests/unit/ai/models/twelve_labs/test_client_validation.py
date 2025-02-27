"""Tests for TwelveLabsClient validation."""

from pathlib import Path

import pytest

from video_understanding.ai.exceptions.twelve_labs import ValidationError


@pytest.mark.asyncio
async def test_make_request_validation(mock_client):
    """Test _make_request validation."""
    # Test valid request
    result = await mock_client._make_request("GET", "/test")
    assert result == {"status": "success"}

    # Test missing index_name in upload task
    with pytest.raises(ValidationError, match="Missing index_name"):
        await mock_client._make_request("POST", "/tasks/upload", json={})

    # Test missing data in upload chunk
    with pytest.raises(ValidationError, match="Missing upload data"):
        await mock_client._make_request("PUT", "/tasks/test_task_id")


@pytest.mark.asyncio
async def test_upload_video_validation(mock_client):
    """Test upload_video validation."""
    # Test invalid path type
    with pytest.raises(ValidationError, match="Invalid video path type"):
        await mock_client.upload_video("not/a/path/object")

    # Test nonexistent file
    with pytest.raises(ValidationError, match="Video file not found"):
        await mock_client.upload_video(Path("nonexistent.mp4"))


@pytest.mark.asyncio
async def test_create_task_validation(mock_client):
    """Test create_task validation."""
    # Test missing task type
    with pytest.raises(ValidationError, match="Missing task type"):
        await mock_client.create_task("", "test_video_id")

    # Test missing video ID
    with pytest.raises(ValidationError, match="Missing video ID"):
        await mock_client.create_task("test_task", "")


@pytest.mark.asyncio
async def test_task_management_validation(mock_client):
    """Test task management validation."""
    # Test get_task_status with missing task ID
    with pytest.raises(ValidationError, match="Missing task ID"):
        await mock_client.get_task_status("")

    # Test cancel_task with missing task ID
    with pytest.raises(ValidationError, match="Missing task ID"):
        await mock_client.cancel_task("")


@pytest.mark.asyncio
async def test_successful_validation(mock_client, test_video):
    """Test successful validation cases."""
    # Test successful video upload
    video_id = await mock_client.upload_video(Path(test_video))
    assert video_id == "test_video_id"

    # Test successful task creation
    task_id = await mock_client.create_task("test_task", video_id)
    assert task_id == "test_task_id"

    # Test successful task status check
    status = await mock_client.get_task_status("test_task_id")
    assert status == {"status": "completed"}
