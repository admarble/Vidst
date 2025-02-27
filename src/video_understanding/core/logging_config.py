"""Logging configuration for the Video Understanding AI system."""

import json
import logging
import logging.config
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


# Extend LogRecord to include extra field
class ExtendedLogRecord(logging.LogRecord):
    """Extended LogRecord class that includes an extra field for additional context."""

    extra: dict[str, Any]


class StructuredJsonFormatter(logging.Formatter):
    """Custom formatter that outputs logs in JSON format with additional context."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON string.

        Args:
            record: The log record to format

        Returns:
            JSON formatted string containing the log record
        """
        # Base log data
        output: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            output["exception"] = self.formatException(record.exc_info)

        # Add extra fields from the record
        if hasattr(record, "extra"):
            output["extra"] = getattr(record, "extra", {})

        # Add any additional attributes set in record.__dict__
        for key, value in record.__dict__.items():
            if (
                key
                not in ["timestamp", "level", "logger", "message", "exception", "extra"]
                and not key.startswith("_")
                and isinstance(value, (str, int, float, bool, list, dict))
            ):
                output[key] = str(value)

        return json.dumps(output)


def setup_logging(
    log_level: str = "INFO", log_file: str = "video_understanding.log"
) -> None:
    """Set up logging configuration for the application.

    Args:
        log_level: The minimum log level to record
        log_file: Path to the log file
    """
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"structured_json": {"()": StructuredJsonFormatter}},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "structured_json",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "structured_json",
                "filename": str(log_path),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": True,
            },
            "src.core.metrics": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging system initialized",
        extra={"log_level": log_level, "log_file": str(log_path)},
    )
