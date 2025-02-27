"""Unit tests for the core metrics module."""

from collections.abc import Generator
from datetime import datetime
from unittest.mock import ANY as mock_ANY
from unittest.mock import Mock, patch

import pytest

from video_understanding.core.metrics import (
    MetricMeasurement,
    MetricsTracker,
    MetricThreshold,
    MetricType,
    PerformanceTimer,
    SuccessCriteria,
)

# Test data
SAMPLE_METRICS = {
    "scene_detection_accuracy": 95.0,
    "ocr_accuracy": 97.5,
    "speech_transcription_accuracy": 96.0,
    "processing_speed_ratio": 1.5,
    "query_response_time": 1.8,
}


@pytest.fixture
def metrics_tracker() -> MetricsTracker:
    """Create a MetricsTracker instance."""
    return MetricsTracker()


@pytest.fixture
def logger_mock() -> Generator[Mock, None, None]:
    """Create a mock logger."""
    with patch("src.core.metrics.logger") as mock:
        yield mock


class TestMetricType:
    def test_metric_types(self) -> None:
        """Test metric type enumeration."""
        assert MetricType.ACCURACY.value == "accuracy"
        assert MetricType.LATENCY.value == "latency"
        assert MetricType.THROUGHPUT.value == "throughput"
        assert MetricType.RESOURCE_USAGE.value == "resource_usage"


class TestMetricThreshold:
    def test_threshold_creation(self) -> None:
        """Test threshold creation with different configurations."""
        threshold = MetricThreshold(min_value=90.0, max_value=100.0, unit="percent")
        assert threshold.min_value == 90.0
        assert threshold.max_value == 100.0
        assert threshold.unit == "percent"

    def test_threshold_validation(self) -> None:
        """Test threshold validation logic."""
        threshold = MetricThreshold(min_value=90.0, max_value=100.0)
        assert threshold.validate(95.0) is True
        assert threshold.validate(85.0) is False
        assert threshold.validate(105.0) is False

    def test_threshold_validation_partial_bounds(self) -> None:
        """Test threshold validation with partial bounds."""
        # Only min value
        min_threshold = MetricThreshold(min_value=90.0)
        assert min_threshold.validate(95.0) is True
        assert min_threshold.validate(85.0) is False
        assert min_threshold.validate(105.0) is True

        # Only max value
        max_threshold = MetricThreshold(max_value=100.0)
        assert max_threshold.validate(95.0) is True
        assert max_threshold.validate(85.0) is True
        assert max_threshold.validate(105.0) is False

        # No bounds
        no_bounds = MetricThreshold()
        assert no_bounds.validate(95.0) is True
        assert no_bounds.validate(-float("inf")) is True
        assert no_bounds.validate(float("inf")) is True

    def test_threshold_to_dict(self) -> None:
        """Test threshold conversion to dictionary."""
        threshold = MetricThreshold(
            min_value=90.0, max_value=100.0, target_value=95.0, unit="percent"
        )
        data = threshold.to_dict()
        assert data["min_value"] == 90.0
        assert data["max_value"] == 100.0
        assert data["target_value"] == 95.0
        assert data["unit"] == "percent"


class TestMetricMeasurement:
    def test_measurement_creation(self) -> None:
        """Test measurement creation with value and context."""
        measurement = MetricMeasurement(value=95.0, context={"source": "test"})
        assert measurement.value == 95.0
        assert measurement.context == {"source": "test"}
        assert isinstance(measurement.timestamp, datetime)

    def test_measurement_creation_defaults(self) -> None:
        """Test measurement creation with default values."""
        measurement = MetricMeasurement(value=95.0)
        assert measurement.value == 95.0
        assert measurement.context == {}
        assert isinstance(measurement.timestamp, datetime)

    def test_measurement_to_dict(self) -> None:
        """Test measurement conversion to dictionary."""
        measurement = MetricMeasurement(value=95.0, context={"source": "test"})
        data = measurement.to_dict()
        assert data["value"] == 95.0
        assert data["context"] == {"source": "test"}
        assert isinstance(data["timestamp"], str)


class TestSuccessCriteria:
    def test_criteria_initialization(self) -> None:
        """Test success criteria initialization."""
        criteria = SuccessCriteria()
        assert "scene_detection_accuracy" in criteria.thresholds
        assert "ocr_accuracy" in criteria.thresholds
        assert "speech_transcription_accuracy" in criteria.thresholds
        assert "processing_speed_ratio" in criteria.thresholds
        assert "query_response_time" in criteria.thresholds

    def test_threshold_values(self) -> None:
        """Test predefined threshold values."""
        criteria = SuccessCriteria()
        assert criteria.thresholds["scene_detection_accuracy"].min_value == 90.0
        assert criteria.thresholds["ocr_accuracy"].min_value == 95.0
        assert criteria.thresholds["speech_transcription_accuracy"].min_value == 95.0
        assert criteria.thresholds["processing_speed_ratio"].max_value == 2.0
        assert criteria.thresholds["query_response_time"].max_value == 2.0

    def test_threshold_units(self) -> None:
        """Test threshold units are correctly set."""
        criteria = SuccessCriteria()
        assert criteria.thresholds["scene_detection_accuracy"].unit == "percent"
        assert criteria.thresholds["processing_speed_ratio"].unit == "x_realtime"
        assert criteria.thresholds["query_response_time"].unit == "seconds"


class TestMetricsTracker:
    def test_record_metric(self, metrics_tracker: MetricsTracker) -> None:
        """Test recording a metric measurement."""
        metrics_tracker.record_metric("test_metric", 95.0, {"source": "test"})
        assert "test_metric" in metrics_tracker.measurements
        assert len(metrics_tracker.measurements["test_metric"]) == 1
        measurement = metrics_tracker.measurements["test_metric"][0]
        assert measurement.value == 95.0
        assert measurement.context == {"source": "test"}

    def test_record_metric_with_threshold(
        self, metrics_tracker: MetricsTracker, logger_mock: Mock
    ) -> None:
        """Test recording a metric with threshold validation."""
        # Test passing threshold
        metrics_tracker.record_metric("scene_detection_accuracy", 95.0)
        assert "scene_detection_accuracy" in metrics_tracker.measurements
        assert len(metrics_tracker.measurements["scene_detection_accuracy"]) == 1
        logger_mock.info.assert_called()

        # Test failing threshold
        metrics_tracker.record_metric("scene_detection_accuracy", 85.0)
        logger_mock.warning.assert_called_with(
            "Metric scene_detection_accuracy value 85.0 does not meet threshold criteria",
            extra=mock_ANY,
        )

    def test_record_metric_no_threshold(
        self, metrics_tracker: MetricsTracker, logger_mock: Mock
    ) -> None:
        """Test recording a metric without threshold."""
        metrics_tracker.record_metric("custom_metric", 95.0)
        logger_mock.info.assert_called_with(
            "Recorded metric custom_metric (no threshold defined)", extra=mock_ANY
        )

    def test_get_metric_stats(self, metrics_tracker: MetricsTracker) -> None:
        """Test getting statistical analysis of metrics."""
        values = [95.0, 96.0, 97.0, 94.0, 95.5]
        for value in values:
            metrics_tracker.record_metric("test_metric", value)

        stats = metrics_tracker.get_metric_stats("test_metric")
        assert "mean" in stats
        assert "median" in stats
        assert "min" in stats
        assert "max" in stats
        assert "stddev" in stats
        assert stats["mean"] == pytest.approx(95.5, 0.1)
        assert stats["min"] == 94.0
        assert stats["max"] == 97.0

    def test_get_metric_stats_single_value(
        self, metrics_tracker: MetricsTracker
    ) -> None:
        """Test getting stats for metric with single value."""
        metrics_tracker.record_metric("test_metric", 95.0)
        stats = metrics_tracker.get_metric_stats("test_metric")
        assert stats["mean"] == 95.0
        assert stats["median"] == 95.0
        assert stats["min"] == 95.0
        assert stats["max"] == 95.0
        assert stats["stddev"] == 0

    def test_get_metric_stats_empty(
        self, metrics_tracker: MetricsTracker, logger_mock: Mock
    ) -> None:
        """Test getting stats for non-existent metric."""
        stats = metrics_tracker.get_metric_stats("nonexistent")
        assert stats == {}
        logger_mock.warning.assert_called_with(
            "No measurements found for metric: nonexistent"
        )

    def test_validate_metric(self, metrics_tracker: MetricsTracker) -> None:
        """Test metric validation against thresholds."""
        # Test passing validation (single value)
        metrics_tracker.record_metric("scene_detection_accuracy", 95.0)
        assert metrics_tracker.validate_metric("scene_detection_accuracy") is True

        # Test failing validation (mean below threshold)
        metrics_tracker.record_metric("scene_detection_accuracy", 85.0)
        metrics_tracker.record_metric("scene_detection_accuracy", 80.0)
        metrics_tracker.record_metric("scene_detection_accuracy", 85.0)
        # Mean is (95 + 85 + 80 + 85) / 4 = 86.25, which is below 90.0 threshold
        assert metrics_tracker.validate_metric("scene_detection_accuracy") is False

    def test_validate_metric_no_criteria(self, metrics_tracker: MetricsTracker) -> None:
        """Test validation for metric without criteria."""
        metrics_tracker.record_metric("custom_metric", 95.0)
        with pytest.raises(ValueError):
            metrics_tracker.validate_metric("custom_metric")

    def test_validate_metric_no_data(
        self, metrics_tracker: MetricsTracker, logger_mock: Mock
    ) -> None:
        """Test validation for metric with no data."""
        result = metrics_tracker.validate_metric("scene_detection_accuracy")
        assert result is False
        logger_mock.warning.assert_called_with(
            "No data available to validate metric: scene_detection_accuracy"
        )

    def test_get_performance_report(self, metrics_tracker: MetricsTracker) -> None:
        """Test generating performance report."""
        for metric, value in SAMPLE_METRICS.items():
            metrics_tracker.record_metric(metric, value)

        report = metrics_tracker.get_performance_report()
        assert isinstance(report, dict)
        for metric in SAMPLE_METRICS:
            assert metric in report
            assert "statistics" in report[metric]
            assert "meets_criteria" in report[metric]
            assert "threshold" in report[metric]

    def test_get_performance_report_empty(
        self, metrics_tracker: MetricsTracker, logger_mock: Mock
    ) -> None:
        """Test generating performance report with no data."""
        report = metrics_tracker.get_performance_report()
        assert isinstance(report, dict)
        assert len(report) == 0
        logger_mock.info.assert_called_with(
            "Performance report generated", extra={"report": {}}
        )


class TestPerformanceTimer:
    def test_performance_timer(self, metrics_tracker: MetricsTracker) -> None:
        """Test performance timer context manager."""
        with patch("time.time") as mock_time:
            mock_time.side_effect = [0.0, 1.0]  # Start and end times
            with PerformanceTimer(metrics_tracker, "test_timing"):
                pass  # Simulate some work

            assert "test_timing" in metrics_tracker.measurements
            measurement = metrics_tracker.measurements["test_timing"][0]
            assert measurement.value == pytest.approx(1.0)

    def test_performance_timer_with_error(
        self, metrics_tracker: MetricsTracker
    ) -> None:
        """Test performance timer with error in context."""
        with patch("time.time") as mock_time:
            mock_time.side_effect = [0.0, 1.0]
            try:
                with PerformanceTimer(metrics_tracker, "test_timing"):
                    raise ValueError("Test error")
            except ValueError:
                pass

            assert "test_timing" in metrics_tracker.measurements
            measurement = metrics_tracker.measurements["test_timing"][0]
            assert measurement.value == pytest.approx(1.0)
            assert "error" in measurement.context
            assert measurement.context["error"] == "Test error"

    def test_performance_timer_zero_duration(
        self, metrics_tracker: MetricsTracker
    ) -> None:
        """Test performance timer with zero duration."""
        with patch("time.time") as mock_time:
            mock_time.side_effect = [1.0, 1.0]  # Same start and end time
            with PerformanceTimer(metrics_tracker, "test_timing"):
                pass

            assert "test_timing" in metrics_tracker.measurements
            measurement = metrics_tracker.measurements["test_timing"][0]
            assert measurement.value == 0.0
