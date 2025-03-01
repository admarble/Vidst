"""Tests for TwelveLabsModel task management."""

import pytest

from video_understanding.ai.exceptions.twelve_labs import ResourceError as TwelveLabsError


@pytest.mark.asyncio
async def test_track_task_status(model, mock_client):
    """Test task status tracking."""
    # First response - pending
    mock_client.wait_for_task.return_value = {"data": "test_result"}

    result = await model._client.wait_for_task("task_123")
    assert result == {"data": "test_result"}


@pytest.mark.asyncio
async def test_track_task_status_failure(model, mock_client):
    """Test task status tracking with failure."""
    mock_client.wait_for_task.side_effect = TwelveLabsError("Processing failed")

    with pytest.raises(TwelveLabsError, match="Processing failed"):
        await model._client.wait_for_task("task_123")


@pytest.mark.asyncio
async def test_search_success(model, mock_client):
    """Test successful semantic search."""
    expected_result = {
        "data": [
            {
                "video_id": "test_video_id",
                "start": 10.5,
                "end": 15.2,
                "score": 0.95,
                "text": "Person explaining code on screen",
                "metadata": {"confidence": 0.92, "source": "visual"},
            }
        ]
    }
    mock_client.search.return_value = expected_result

    result = await model.search("person explaining code")
    assert result == expected_result


@pytest.mark.asyncio
async def test_generate_text_success(model, mock_client):
    """Test successful text generation."""
    expected_result = {
        "summary": "A technical tutorial showing code examples",
        "chapters": [
            {"title": "Introduction", "start": 0, "end": 30},
            {"title": "Code Walkthrough", "start": 30, "end": 120},
        ],
        "topics": ["programming", "tutorial", "code examples"],
        "hashtags": ["#coding", "#tutorial", "#programming"],
    }
    mock_client.generate_text.return_value = expected_result

    result = await model.generate_text(
        "test_video_id", "Generate a summary and chapters"
    )
    assert result == expected_result
