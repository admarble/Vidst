"""Tests for AI model image processing functionality."""

from unittest.mock import mock_open, patch


def test_process_image_encoding(model, ai_test_image):
    """Test image encoding during processing."""
    input_data = {"image_path": str(ai_test_image)}

    # Mock open to return test data
    test_data = b"test image data"
    mock_open_obj = mock_open(read_data=test_data)

    with patch("builtins.open", mock_open_obj):
        result = model.process(input_data)

        # Verify file was opened in binary mode
        mock_open_obj.assert_called_once_with(str(ai_test_image), "rb")

        # Verify the result contains expected fields
        assert isinstance(result, dict)
        assert "description" in result
        assert "objects" in result
        assert "text" in result
        assert "actions" in result
        assert isinstance(result["objects"], list)
        assert isinstance(result["text"], list)
        assert isinstance(result["actions"], list)
