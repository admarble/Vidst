"""Tests for TwelveLabsModel request features."""

import asyncio
from threading import Lock

import pytest


@pytest.mark.asyncio
async def test_chunked_upload(model, mock_client, test_video):
    """Test chunked upload functionality."""
    mock_client.upload_video.return_value = "video_123"

    result = await model._client.upload_video(test_video)
    assert result == "video_123"


@pytest.mark.asyncio
async def test_process_with_progress(model, mock_client, test_video):
    """Test progress callback functionality during video processing."""
    progress_updates = []

    def progress_callback(current, total):
        progress_updates.append((current, total))

    mock_client.upload_video.return_value = "test_video_id"
    mock_client.create_task.return_value = "analysis_task_id"
    mock_client.wait_for_task.return_value = {
        "status": "completed",
        "result": {"data": "test"},
    }

    input_data = {
        "video_path": str(test_video),
        "task": "scene_detection",
        "progress_callback": progress_callback,
    }

    result = await model.process(input_data)
    assert result["data"] == "test"
    assert result["metadata"]["video_id"] == "test_video_id"
    assert result["metadata"]["index_name"] == model.DEFAULT_INDEX


@pytest.mark.asyncio
async def test_concurrent_requests(model, mock_client):
    """Test handling of concurrent API requests."""

    class RequestCounter:
        def __init__(self):
            self.value = 0
            self.lock = Lock()

        async def increment(self):
            with self.lock:
                self.value += 1

    counter = RequestCounter()

    async def mock_request(query: str, index_name: str | None = None, **kwargs):
        await counter.increment()
        return {
            "data": {"status": "success"},
            "metadata": {
                "index_name": index_name or model.DEFAULT_INDEX,
                "query": query,
            },
        }

    mock_client.search.side_effect = mock_request

    # Run concurrent searches
    tasks = [model.search("test query") for _ in range(5)]
    results = await asyncio.gather(*tasks)

    assert len(results) == 5
    assert counter.value == 5
    assert all(r["data"]["status"] == "success" for r in results)
    assert all(r["metadata"]["index_name"] == model.DEFAULT_INDEX for r in results)
    assert all(r["metadata"]["query"] == "test query" for r in results)


@pytest.mark.asyncio
async def test_cleanup(model, mock_client):
    """Test cleanup behavior."""
    mock_client.close.return_value = None

    await model.close()
    mock_client.close.assert_called_once()
