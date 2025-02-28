"""Core metrics tracking and validation system for Video Understanding AI.

This module provides classes and utilities for tracking, validating, and reporting
technical success criteria across all components of the system.
"""

import logging
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# Set up module logger
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics that can be tracked in the system.

    This enum defines the different categories of metrics that can be tracked
    and monitored throughout the video processing pipeline. Each type has specific
    thresholds and validation rules.

    Values:
        ACCURACY: Measurement of model or component accuracy (0-100%)
            Examples: Scene detection accuracy, OCR accuracy
        LATENCY: Time-based measurements in seconds
            Examples: Processing time, API response time
        THROUGHPUT: Processing rate measurements (units/time)
            Examples: Frames per second, videos per hour
        RESOURCE_USAGE: System resource utilization metrics
            Examples: Memory usage (MB), CPU utilization (%)

    Example:
        >>> from video_understanding.core.metrics import MetricType, MetricsTracker
        >>> tracker = MetricsTracker()
        >>> # Record scene detection accuracy
        >>> tracker.record_metric(
        ...     name="scene_detection_accuracy",
        ...     value=92.5,
        ...     metric_type=MetricType.ACCURACY
        ... )
        >>> # Record processing latency
        >>> tracker.record_metric(
        ...     name="video_processing_time",
        ...     value=45.2,
        ...     metric_type=MetricType.LATENCY
        ... )
    """

    ACCURACY = "accuracy"
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    RESOURCE_USAGE = "resource_usage"


@dataclass
class MetricThreshold:
    """Defines success criteria thresholds for a metric."""

    min_value: float | None = None
    max_value: float | None = None
    target_value: float | None = None
    unit: str = ""

    def validate(self, value: float) -> bool:
        """Check if a value meets the threshold criteria."""
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        """Convert threshold to dictionary for logging."""
        return {
            "min_value": self.min_value,
            "max_value": self.max_value,
            "target_value": self.target_value,
            "unit": self.unit,
        }


@dataclass
class MetricMeasurement:
    """Individual metric measurement with timestamp and context."""

    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert measurement to dictionary for logging."""
        return {
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
        }


class SuccessCriteria:
    """Defines and tracks success criteria for the system."""

    def __init__(self) -> None:
        """Initialize success criteria with predefined thresholds."""
        self.thresholds: dict[str, MetricThreshold] = {
            "scene_detection_accuracy": MetricThreshold(min_value=90.0, unit="percent"),
            "ocr_accuracy": MetricThreshold(min_value=95.0, unit="percent"),
            "speech_transcription_accuracy": MetricThreshold(
                min_value=95.0, unit="percent"
            ),
            "processing_speed_ratio": MetricThreshold(max_value=2.0, unit="x_realtime"),
            "query_response_time": MetricThreshold(max_value=2.0, unit="seconds"),
        }
        logger.info(
            "Initialized success criteria with thresholds",
            extra={"thresholds": {k: v.to_dict() for k, v in self.thresholds.items()}},
        )


class MetricsTracker:
    """Tracks and analyzes system metrics."""

    def __init__(self) -> None:
        """Initialize metrics tracker."""
        self.measurements: dict[str, list[MetricMeasurement]] = {}
        self.success_criteria = SuccessCriteria()
        self.active_processes = 0
        logger.info("Initialized metrics tracker")

    def get_active_count(self) -> int:
        """Get the current number of active processing operations.

        Returns:
            int: Number of active processes
        """
        return self.active_processes

    def increment_active_count(self) -> None:
        """Increment the count of active processing operations."""
        self.active_processes += 1
        logger.debug("Incremented active process count to %d", self.active_processes)

    def decrement_active_count(self) -> None:
        """Decrement the count of active processing operations."""
        if self.active_processes > 0:
            self.active_processes -= 1
        logger.debug("Decremented active process count to %d", self.active_processes)

    def record_metric(
        self, metric_name: str, value: float, context: dict[str, Any] | None = None
    ) -> None:
        """Record a new metric measurement.

        Args:
            metric_name: Name of the metric to record
            value: Measured value
            context: Optional context about the measurement
        """
        if metric_name not in self.measurements:
            self.measurements[metric_name] = []

        measurement = MetricMeasurement(value=value, context=context or {})
        self.measurements[metric_name].append(measurement)

        # Log the measurement
        log_context = {"metric_name": metric_name, "measurement": measurement.to_dict()}

        # Add threshold information if available
        if metric_name in self.success_criteria.thresholds:
            threshold = self.success_criteria.thresholds[metric_name]
            log_context["threshold"] = threshold.to_dict()

            # Log validation result
            if not threshold.validate(value):
                logger.warning(
                    "Metric %s value %s does not meet threshold criteria",
                    metric_name,
                    value,
                    extra=log_context,
                )
            else:
                logger.info("Recorded metric %s", metric_name, extra=log_context)
        else:
            logger.info(
                "Recorded metric %s (no threshold defined)",
                metric_name,
                extra=log_context,
            )

    def get_metric_stats(self, metric_name: str) -> dict[str, float]:
        """Get statistical analysis of a metric's measurements.

        Args:
            metric_name: Name of the metric to analyze

        Returns:
            Dictionary containing statistical measures
        """
        if metric_name not in self.measurements:
            logger.warning("No measurements found for metric: %s", metric_name)
            return {}

        values = [m.value for m in self.measurements[metric_name]]
        if not values:
            logger.warning("Empty measurements list for metric: %s", metric_name)
            return {}

        stats = {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "stddev": statistics.stdev(values) if len(values) > 1 else 0,
        }

        logger.debug(
            "Calculated statistics for %s",
            metric_name,
            extra={"metric_name": metric_name, "stats": stats},
        )
        return stats

    def validate_metric(self, metric_name: str) -> bool:
        """Check if a metric meets its success criteria.

        Args:
            metric_name: Name of the metric to validate

        Returns:
            True if metric meets criteria, False otherwise
        """
        if metric_name not in self.success_criteria.thresholds:
            logger.error("No success criteria defined for metric: %s", metric_name)
            raise ValueError(f"No success criteria defined for metric: {metric_name}")

        stats = self.get_metric_stats(metric_name)
        if not stats:
            logger.warning("No data available to validate metric: %s", metric_name)
            return False

        threshold = self.success_criteria.thresholds[metric_name]
        result = threshold.validate(stats["mean"])

        log_context = {
            "metric_name": metric_name,
            "stats": stats,
            "threshold": threshold.to_dict(),
            "meets_criteria": result,
        }

        if result:
            logger.info(
                "Metric %s meets success criteria", metric_name, extra=log_context
            )
        else:
            logger.warning(
                "Metric %s does not meet success criteria",
                metric_name,
                extra=log_context,
            )

        return result

    def get_performance_report(self) -> dict[str, dict[str, Any]]:
        """Generate a comprehensive performance report.

        Returns:
            Dictionary containing performance metrics and their analysis
        """
        logger.info("Generating performance report")
        report = {}
        for metric_name in self.measurements:
            stats = self.get_metric_stats(metric_name)
            meets_criteria = self.validate_metric(metric_name)
            threshold = self.success_criteria.thresholds.get(metric_name)

            report[metric_name] = {
                "statistics": stats,
                "meets_criteria": meets_criteria,
                "threshold": {
                    "min": threshold.min_value if threshold else None,
                    "max": threshold.max_value if threshold else None,
                    "target": threshold.target_value if threshold else None,
                    "unit": threshold.unit if threshold else None,
                },
            }

        logger.info("Performance report generated", extra={"report": report})
        return report


class PerformanceTimer:
    """Context manager for timing operations."""

    def __init__(self, metrics_tracker: MetricsTracker, metric_name: str) -> None:
        """Initialize timer.

        Args:
            metrics_tracker: MetricsTracker instance to record measurements
            metric_name: Name of the metric to record
        """
        self.metrics_tracker = metrics_tracker
        self.metric_name = metric_name
        self.start_time: float | None = None
        logger.debug("Initialized performance timer for %s", metric_name)

    def __enter__(self) -> "PerformanceTimer":
        """Start timing."""
        self.start_time = time.time()
        logger.debug(
            "Started timing %s",
            self.metric_name,
            extra={"metric_name": self.metric_name, "start_time": self.start_time},
        )
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_val: Exception | None,
        exc_tb: Any | None,
    ) -> None:
        """Stop timing and record measurement."""
        if self.start_time is not None:
            duration = time.time() - self.start_time
            context = {"error": str(exc_val) if exc_val else None}

            log_context = {
                "metric_name": self.metric_name,
                "duration": duration,
                "error": context["error"],
            }

            if exc_val:
                logger.warning(
                    "Operation %s failed", self.metric_name, extra=log_context
                )
            else:
                logger.debug(
                    "Operation %s completed", self.metric_name, extra=log_context
                )

            self.metrics_tracker.record_metric(
                self.metric_name, duration, context=context
            )
