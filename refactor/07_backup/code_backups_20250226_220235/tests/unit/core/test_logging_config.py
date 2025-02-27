"""Test module for logging_config.py.

This module contains tests for logging configuration and formatting functionality.
"""

import json
import logging
import sys
from unittest.mock import MagicMock, patch

import pytest

from video_understanding.core.logging_config import (
    StructuredJsonFormatter,
    setup_logging,
)


@pytest.fixture
def log_record():
    """Create a basic log record for testing."""
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    return record


@pytest.fixture
def log_record_with_extra(log_record):
    """Create a log record with extra fields."""
    record = log_record
    record.extra = {"context": "test", "user_id": "123"}
    return record


@pytest.fixture
def log_record_with_exception(log_record):
    """Create a log record with exception info."""
    try:
        raise ValueError("Test error")
    except ValueError:
        record = log_record
        record.exc_info = sys.exc_info()
        return record


class TestStructuredJsonFormatter:
    def test_format_basic_record(self, log_record):
        """Test formatting a basic log record."""
        formatter = StructuredJsonFormatter()
        result = json.loads(formatter.format(log_record))

        assert result["level"] == "INFO"
        assert result["logger"] == "test_logger"
        assert result["message"] == "Test message"
        assert "timestamp" in result

    def test_format_with_extra_fields(self, log_record_with_extra):
        """Test formatting a log record with extra fields."""
        formatter = StructuredJsonFormatter()
        result = json.loads(formatter.format(log_record_with_extra))

        assert result["extra"]["context"] == "test"
        assert result["extra"]["user_id"] == "123"

    def test_format_with_exception(self, log_record_with_exception):
        """Test formatting a log record with exception information."""
        formatter = StructuredJsonFormatter()
        result = json.loads(formatter.format(log_record_with_exception))

        assert "exception" in result
        assert "ValueError: Test error" in result["exception"]

    def test_format_with_custom_attributes(self, log_record):
        """Test formatting a log record with custom attributes."""
        log_record.custom_str = "test_str"
        log_record.custom_int = 42
        log_record.custom_float = 3.14
        log_record.custom_bool = True
        log_record.custom_list = ["a", "b"]
        log_record.custom_dict = {"key": "value"}
        log_record._private = "private"  # Should be excluded

        formatter = StructuredJsonFormatter()
        result = json.loads(formatter.format(log_record))

        assert result["custom_str"] == "test_str"
        assert result["custom_int"] == "42"
        assert result["custom_float"] == "3.14"
        assert result["custom_bool"] == "True"
        assert result["custom_list"] == "['a', 'b']"
        assert result["custom_dict"] == "{'key': 'value'}"
        assert "_private" not in result


class TestSetupLogging:
    def test_setup_logging_default_params(self, tmp_path):
        """Test setup_logging with default parameters."""
        log_file = tmp_path / "test.log"

        with patch("logging.config.dictConfig") as mock_dict_config:
            setup_logging(log_file=str(log_file))

            # Verify dictConfig was called
            mock_dict_config.assert_called_once()
            config = mock_dict_config.call_args[0][0]

            # Verify config structure
            assert config["version"] == 1
            assert not config["disable_existing_loggers"]
            assert "structured_json" in config["formatters"]
            assert "console" in config["handlers"]
            assert "file" in config["handlers"]
            assert "" in config["loggers"]  # Root logger
            assert "src.core.metrics" in config["loggers"]

    def test_setup_logging_custom_level(self, tmp_path):
        """Test setup_logging with custom log level."""
        log_file = tmp_path / "test.log"

        with patch("logging.config.dictConfig") as mock_dict_config:
            setup_logging(log_level="DEBUG", log_file=str(log_file))

            config = mock_dict_config.call_args[0][0]
            assert config["loggers"][""]["level"] == "DEBUG"
            assert config["loggers"]["src.core.metrics"]["level"] == "DEBUG"

    def test_setup_logging_creates_directory(self, tmp_path):
        """Test setup_logging creates log directory if it doesn't exist."""
        log_file = tmp_path / "logs" / "test.log"

        with patch("logging.config.dictConfig"):
            setup_logging(log_file=str(log_file))
            assert log_file.parent.exists()

    def test_setup_logging_rotating_file_handler(self, tmp_path):
        """Test setup_logging configures RotatingFileHandler correctly."""
        log_file = tmp_path / "test.log"

        with patch("logging.config.dictConfig") as mock_dict_config:
            setup_logging(log_file=str(log_file))

            config = mock_dict_config.call_args[0][0]
            file_handler = config["handlers"]["file"]
            assert file_handler["class"] == "logging.handlers.RotatingFileHandler"
            assert file_handler["maxBytes"] == 10485760  # 10MB
            assert file_handler["backupCount"] == 5

    def test_setup_logging_initialization_log(self, tmp_path):
        """Test setup_logging logs initialization message."""
        log_file = tmp_path / "test.log"

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            setup_logging(log_file=str(log_file))

            mock_logger.info.assert_called_once_with(
                "Logging system initialized",
                extra={"log_level": "INFO", "log_file": str(log_file)},
            )
