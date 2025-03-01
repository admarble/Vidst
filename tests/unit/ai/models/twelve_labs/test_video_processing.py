"""Tests for TwelveLabsModel video processing functionality."""

import tempfile

import pytest

from video_understanding.ai.models.twelve_labs.exceptions import TwelveLabsError

from .conftest import create_mock_response


@pytest.mark.asyncio
async def test_process_success(model, test_video, mock_session):
    """Test successful video processing."""
    responses = [
        create_mock_response(
            status_code=200, json_data={"data": [{"name": "default_index"}]}
        ),
        create_mock_response(
            status_code=200,
            json_data={
                "task_id": "upload_task_id",
                "status": "completed",
                "result": {"video_id": "test_video_id"},
            },
        ),
        create_mock_response(status_code=200),  # chunk upload
        create_mock_response(
            status_code=200,
            json_data={"status": "completed", "result": {"video_id": "test_video_id"}},
        ),
        create_mock_response(
            status_code=200,
            json_data={
                "task_id": "analysis_task_id",
                "status": "completed",
                "result": {"data": "test"},
            },
        ),
        create_mock_response(
            status_code=200,
            json_data={"status": "completed", "result": {"data": "test"}},
        ),
    ]
    mock_session.request.side_effect = responses

    input_data = {"video_path": str(test_video), "task": "scene_detection"}

    result = await model.process(input_data)
    assert result["data"] == "test"
    assert result["metadata"]["video_id"] == "test_video_id"
    assert result["metadata"]["index_name"] == model.DEFAULT_INDEX


@pytest.mark.asyncio
async def test_process_analysis_failure(model, test_video, mock_session):
    """Test video processing with analysis failure."""
    responses = [
        create_mock_response(
            status_code=200, json_data={"data": [{"name": "default_index"}]}
        ),
        create_mock_response(
            status_code=200,
            json_data={
                "task_id": "upload_task_id",
                "status": "completed",
                "result": {"video_id": "test_video_id"},
            },
        ),
        create_mock_response(status_code=200),  # chunk upload
        create_mock_response(
            status_code=200,
            json_data={"status": "completed", "result": {"video_id": "test_video_id"}},
        ),
        create_mock_response(
            status_code=200,
            json_data={
                "task_id": "analysis_task_id",
                "status": "completed",
                "result": {"video_id": "test_video_id"},
            },
        ),
        create_mock_response(
            status_code=200, json_data={"status": "failed", "error": "Task failed"}
        ),
    ]
    mock_session.request.side_effect = responses

    input_data = {"video_path": str(test_video), "task": "scene_detection"}

    with pytest.raises(TwelveLabsError, match="Task failed: Task failed"):
        await model.process(input_data)


@pytest.mark.asyncio
async def test_chunked_upload(model, test_video, mock_session):
    """Test chunked upload functionality."""
    # Mock upload task creation
    task_response = create_mock_response(
        status_code=200, json_data={"task_id": "upload_123"}
    )

    # Mock chunk uploads
    chunk_response = create_mock_response(status_code=200)

    # Mock task completion
    complete_response = create_mock_response(
        status_code=200,
        json_data={"status": "completed", "result": {"video_id": "video_123"}},
    )

    mock_session.request.side_effect = [
        task_response,
        chunk_response,
        complete_response,
    ]

    result = await model._upload_video(str(test_video))
    assert result == "video_123"


@pytest.mark.asyncio
async def test_process_video(model, mock_session):
    """Test video processing."""

    def create_responses():
        yield create_mock_response(  # Index check
            status_code=200, json_data={"data": [{"name": "default_index"}]}
        )
        yield create_mock_response(  # Upload task creation
            status_code=200,
            json_data={"data": {"task_id": "upload_123", "status": "pending"}},
        )
        # Multiple chunk uploads
        for _ in range(5):  # Simulate 5 chunks
            yield create_mock_response(status_code=200)

        # Upload task status checks - first pending, then completed
        yield create_mock_response(  # First status check - pending
            status_code=200,
            json_data={"data": {"task_id": "upload_123", "status": "pending"}},
        )
        yield create_mock_response(  # Second status check - completed
            status_code=200,
            json_data={
                "data": {
                    "task_id": "upload_123",
                    "status": "completed",
                    "result": {"video_id": "video_123"},
                }
            },
        )
        yield create_mock_response(  # Analysis task creation
            status_code=200,
            json_data={"data": {"task_id": "analysis_123", "status": "pending"}},
        )
        # Analysis task status checks - first pending, then completed
        yield create_mock_response(  # First status check - pending
            status_code=200,
            json_data={"data": {"task_id": "analysis_123", "status": "pending"}},
        )
        yield create_mock_response(  # Second status check - completed
            status_code=200,
            json_data={
                "data": {
                    "task_id": "analysis_123",
                    "status": "completed",
                    "result": {
                        "transcription": "Test transcription",
                        "confidence": 0.95,
                    },
                }
            },
        )

    mock_session.request.side_effect = create_responses()

    with tempfile.NamedTemporaryFile(suffix=".mp4") as test_video:
        # Write some test data to ensure multiple chunks
        test_video.write(b"test video content" * 1000)
        test_video.flush()

        result = await model.process(
            {
                "video_path": test_video.name,
                "task": "transcription",
                "options": {"language": "en", "confidence_threshold": 0.8},
            }
        )

        assert result["data"]["transcription"] == "Test transcription"
        assert result["data"]["confidence"] == 0.95
        assert result["metadata"]["video_id"] == "video_123"
        assert result["metadata"]["index_name"] == model.DEFAULT_INDEX


@pytest.mark.asyncio
async def test_progress_callback(model, test_video, mock_session):
    """Test progress callback functionality during video processing."""
    progress_updates = []

    def progress_callback(current, total):
        progress_updates.append((current, total))

    responses = [
        create_mock_response(
            status_code=200, json_data={"data": [{"name": "default_index"}]}
        ),
        create_mock_response(
            status_code=200,
            json_data={
                "task_id": "upload_task_id",
                "status": "completed",
                "result": {"video_id": "test_video_id"},
            },
        ),
        create_mock_response(status_code=200),  # chunk upload
        create_mock_response(
            status_code=200,
            json_data={"status": "completed", "result": {"video_id": "test_video_id"}},
        ),
        create_mock_response(
            status_code=200,
            json_data={
                "task_id": "analysis_task_id",
                "status": "completed",
                "result": {"data": "test"},
            },
        ),
        create_mock_response(
            status_code=200,
            json_data={"status": "completed", "result": {"data": "test"}},
        ),
    ]
    mock_session.request.side_effect = responses

    input_data = {
        "video_path": str(test_video),
        "task": "scene_detection",
        "progress_callback": progress_callback,
    }

    result = await model.process(input_data)
    assert result["data"] == "test"
    assert result["metadata"]["video_id"] == "test_video_id"
    assert result["metadata"]["index_name"] == model.DEFAULT_INDEX
    assert len(progress_updates) > 0
    assert all(
        isinstance(update, tuple) and len(update) == 2 for update in progress_updates
    )
    assert all(0 <= current <= total for current, total in progress_updates)
    assert (
        progress_updates[-1][0] == progress_updates[-1][1]
    )  # Final update should be complete
