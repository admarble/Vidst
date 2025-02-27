"""Tests for TwelveLabsModel analysis functionality."""

from .conftest import create_mock_response


def test_analyze_video(model, mock_session, test_video):
    """Test video analysis with custom options."""
    # Mock successful index check
    mock_session.request.side_effect = [
        create_mock_response(
            status_code=200, json_data={"data": [{"name": "default_index"}]}
        ),
        # Mock successful upload task creation
        create_mock_response(status_code=200, json_data={"task_id": "upload_task_123"}),
        # Mock successful chunk upload
        create_mock_response(status_code=200),
        # Mock successful upload completion
        create_mock_response(
            status_code=200,
            json_data={"status": "completed", "result": {"video_id": "video_123"}},
        ),
        # Mock successful analysis task creation
        create_mock_response(
            status_code=200, json_data={"task_id": "analysis_task_123"}
        ),
        # Mock successful analysis completion
        create_mock_response(
            status_code=200,
            json_data={
                "status": "completed",
                "result": {"transcription": "Test transcription", "confidence": 0.95},
            },
        ),
    ]

    result = model.analyze_video(
        test_video, task_type="transcription", confidence_threshold=0.8, language="en"
    )
    assert "transcription" in result
    assert result["confidence"] > 0.9
    assert mock_session.request.call_count == 6


def test_search_success(model, mock_session):
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
    response = create_mock_response(status_code=200, json_data=expected_result)
    mock_session.request.return_value = response

    result = model.search("person explaining code")
    assert result == expected_result


def test_generate_text_success(model, mock_session):
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
    responses = [
        create_mock_response(status_code=200, json_data={"task_id": "text_gen_task"}),
        create_mock_response(
            status_code=200,
            json_data={"status": "completed", "result": expected_result},
        ),
    ]
    mock_session.request.side_effect = responses

    result = model.generate_text("test_video_id", "Generate a summary and chapters")
    assert result == expected_result
