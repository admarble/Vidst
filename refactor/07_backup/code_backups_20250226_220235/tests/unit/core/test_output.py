"""Test module for output.py.

This module contains tests for processing results and output formatting functionality.
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from video_understanding.core.exceptions import ValidationError
from video_understanding.core.output import (
    ProcessingResult,
    ProcessingStatus,
    Scene,
    format_result,
    format_scene,
    format_timestamp,
    load_result,
    parse_timestamp,
    save_result,
)


# Test data
@pytest.fixture
def sample_scene():
    """Create a sample Scene instance."""
    return Scene(
        scene_id="scene1",
        start_time=10.5,
        end_time=20.75,
        keyframe_path=Path("/test/keyframe.jpg"),
        transcript="Sample transcript",
        metadata={"confidence": 0.95},
    )


@pytest.fixture
def sample_result(sample_scene):
    """Create a sample ProcessingResult instance."""
    return ProcessingResult(
        video_id="video1",
        status=ProcessingStatus.COMPLETED,
        scenes=[sample_scene],
        transcript="Full video transcript",
        metadata={"duration": 120.0},
        created_at=datetime(2024, 1, 1, 12, 0),
        updated_at=datetime(2024, 1, 1, 12, 30),
    )


class TestProcessingStatus:
    def test_status_values(self):
        """Test ProcessingStatus enumeration values."""
        assert ProcessingStatus.PENDING.value == "pending"
        assert ProcessingStatus.PROCESSING.value == "processing"
        assert ProcessingStatus.COMPLETED.value == "completed"
        assert ProcessingStatus.FAILED.value == "failed"


class TestScene:
    def test_scene_creation(self, sample_scene):
        """Test Scene creation with all fields."""
        assert sample_scene.scene_id == "scene1"
        assert sample_scene.start_time == 10.5
        assert sample_scene.end_time == 20.75
        assert sample_scene.keyframe_path == Path("/test/keyframe.jpg")
        assert sample_scene.transcript == "Sample transcript"
        assert sample_scene.metadata == {"confidence": 0.95}

    def test_scene_optional_fields(self):
        """Test Scene creation with optional fields."""
        scene = Scene(
            scene_id="scene2",
            start_time=30.0,
            end_time=40.0,
            keyframe_path=None,
        )
        assert scene.transcript is None
        assert scene.metadata == {}


class TestProcessingResult:
    def test_result_creation(self, sample_result):
        """Test ProcessingResult creation with all fields."""
        assert sample_result.video_id == "video1"
        assert sample_result.status == ProcessingStatus.COMPLETED
        assert len(sample_result.scenes) == 1
        assert sample_result.transcript == "Full video transcript"
        assert sample_result.metadata == {"duration": 120.0}
        assert sample_result.created_at == datetime(2024, 1, 1, 12, 0)
        assert sample_result.updated_at == datetime(2024, 1, 1, 12, 30)
        assert sample_result.error is None

    def test_result_with_error(self):
        """Test ProcessingResult with error status."""
        result = ProcessingResult(
            video_id="video2",
            status=ProcessingStatus.FAILED,
            scenes=[],
            error="Processing failed",
        )
        assert result.status == ProcessingStatus.FAILED
        assert result.error == "Processing failed"
        assert len(result.scenes) == 0
        assert result.transcript is None
        assert result.metadata == {}


class TestFormatting:
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        assert format_timestamp(3661.123) == "01:01:01.123"  # 1h 1m 1.123s
        assert format_timestamp(70.5) == "00:01:10.500"  # 1m 10.5s
        assert format_timestamp(0.001) == "00:00:00.001"  # 0.001s
        assert format_timestamp(7200.0) == "02:00:00.000"  # 2h

    def test_format_scene(self, sample_scene):
        """Test scene formatting."""
        formatted = format_scene(sample_scene)
        assert formatted["id"] == "scene1"
        assert formatted["start_time"] == "00:00:10.500"
        assert formatted["end_time"] == "00:00:20.750"
        assert formatted["duration"] == 10.25
        assert formatted["keyframe"] == "/test/keyframe.jpg"
        assert formatted["transcript"] == "Sample transcript"
        assert formatted["metadata"] == {"confidence": 0.95}

    def test_format_scene_no_keyframe(self):
        """Test scene formatting without keyframe."""
        scene = Scene(
            scene_id="scene2",
            start_time=0.0,
            end_time=10.0,
            keyframe_path=None,
        )
        formatted = format_scene(scene)
        assert formatted["keyframe"] is None

    def test_format_result(self, sample_result):
        """Test result formatting."""
        formatted = format_result(sample_result)
        assert formatted["video_id"] == "video1"
        assert formatted["status"] == "completed"
        assert len(formatted["scenes"]) == 1
        assert formatted["transcript"] == "Full video transcript"
        assert formatted["metadata"] == {"duration": 120.0}
        assert formatted["created_at"] == "2024-01-01T12:00:00"
        assert formatted["updated_at"] == "2024-01-01T12:30:00"
        assert formatted["error"] is None


class TestFileOperations:
    def test_save_result(self, sample_result, tmp_path):
        """Test saving result to file."""
        output_path = tmp_path / "result.json"
        save_result(sample_result, output_path)

        # Verify file contents
        with open(output_path) as f:
            data = json.load(f)
            assert data["video_id"] == "video1"
            assert data["status"] == "completed"
            assert len(data["scenes"]) == 1

    def test_save_result_creates_directory(self, sample_result, tmp_path):
        """Test save_result creates output directory."""
        output_path = tmp_path / "subdir" / "result.json"
        save_result(sample_result, output_path)
        assert output_path.exists()

    def test_save_result_error(self, sample_result):
        """Test save_result with file error."""
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = OSError("Write error")
            with pytest.raises(ValidationError, match="Failed to save result"):
                save_result(sample_result, Path("/test/result.json"))

    def test_load_result(self, sample_result, tmp_path):
        """Test loading result from file."""
        # Save result first
        input_path = tmp_path / "result.json"
        save_result(sample_result, input_path)

        # Load and verify
        loaded = load_result(input_path)
        assert loaded.video_id == sample_result.video_id
        assert loaded.status == sample_result.status
        assert len(loaded.scenes) == len(sample_result.scenes)
        assert loaded.transcript == sample_result.transcript
        assert loaded.metadata == sample_result.metadata

    def test_load_result_error(self):
        """Test load_result with file error."""
        with pytest.raises(ValidationError, match="Failed to load result"):
            load_result(Path("/nonexistent/result.json"))

    def test_load_result_invalid_json(self, tmp_path):
        """Test load_result with invalid JSON."""
        input_path = tmp_path / "invalid.json"
        input_path.write_text("invalid json")
        with pytest.raises(ValidationError, match="Failed to load result"):
            load_result(input_path)


class TestTimestampParsing:
    def test_parse_timestamp_valid(self):
        """Test parsing valid timestamps."""
        assert parse_timestamp("01:01:01.123") == 3661.123  # 1h 1m 1.123s
        assert parse_timestamp("00:01:10.500") == 70.5  # 1m 10.5s
        assert parse_timestamp("00:00:00.001") == 0.001  # 0.001s
        assert parse_timestamp("02:00:00.000") == 7200.0  # 2h

    def test_parse_timestamp_invalid(self):
        """Test parsing invalid timestamps."""
        invalid_timestamps = [
            "01:01",  # Missing seconds
            "01:01:01:01",  # Too many components
            "aa:bb:cc",  # Non-numeric values
            "",  # Empty string
            "01:61:00",  # Invalid minutes
            "24:00:00",  # Invalid hours
            "01:01:60",  # Invalid seconds
            "not a timestamp",  # Invalid format
        ]
        for timestamp in invalid_timestamps:
            with pytest.raises(ValidationError, match="Invalid timestamp format"):
                parse_timestamp(timestamp)

    def test_parse_timestamp_negative(self):
        """Test parsing negative timestamps."""
        with pytest.raises(ValidationError, match="Invalid timestamp format"):
            parse_timestamp("-01:00:00")  # Negative time not allowed
