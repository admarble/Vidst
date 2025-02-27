"""Base class for performance tests with common functionality."""

import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Any

import pytest

from tests.config.test_config import PerformanceConfig
from tests.utils.metrics import PerformanceMetrics

logger = logging.getLogger(__name__)


class BasePerformanceTest:
    """Base class for all performance tests providing common functionality."""

    @pytest.fixture(autouse=True)
    def setup_test(self, caplog):
        """Setup test environment and logging."""
        self.config = PerformanceConfig()
        self.metrics = PerformanceMetrics()
        self.errors: list[dict[str, Any]] = []
        self.expected_duration: float | None = None

        # Configure logging
        caplog.set_level(logging.INFO)

        yield

        # Print test summary
        self.metrics.print_summary()
        if self.errors:
            logger.error("Test encountered errors:")
            for error in self.errors:
                logger.error(f"  {error['type']}: {error['message']}")

    def record_error(
        self, error_type: str, message: str, context: dict | None = None
    ) -> None:
        """Record an error that occurred during testing."""
        error = {
            "type": error_type,
            "message": message,
            "timestamp": datetime.now(),
            "context": context or {},
        }
        self.errors.append(error)
        logger.error(f"{error_type}: {message}")

    @contextmanager
    def assert_performance(self, operation: str):
        """Context manager to assert performance metrics for an operation."""
        with self.metrics.measure_operation(operation) as metrics:
            yield metrics

            # Get operation metrics
            op_metrics = self.metrics.get_operation_metrics(operation)
            if not op_metrics:
                return

            # Memory assertions
            if op_metrics.peak_memory >= self.config.memory.max_memory_mb:
                self.record_error(
                    "MemoryError",
                    f"Peak memory ({op_metrics.peak_memory:.1f}MB) exceeded limit "
                    f"({self.config.memory.max_memory_mb}MB)",
                    {"operation": operation, "peak_memory": op_metrics.peak_memory},
                )

            if (
                op_metrics.memory_growth
                >= self.config.memory.max_memory_growth_mb_per_hour
            ):
                self.record_error(
                    "MemoryGrowthError",
                    f"Memory growth ({op_metrics.memory_growth:.1f}MB/hour) exceeded limit "
                    f"({self.config.memory.max_memory_growth_mb_per_hour}MB/hour)",
                    {"operation": operation, "growth_rate": op_metrics.memory_growth},
                )

            # Processing time assertions
            if (
                hasattr(self, "expected_duration")
                and self.expected_duration is not None
            ):
                max_time = (
                    self.expected_duration
                    * self.config.processing.max_processing_time_multiplier
                )
                if op_metrics.total_time > max_time:
                    self.record_error(
                        "ProcessingTimeError",
                        f"Processing time ({op_metrics.total_time:.1f}s) exceeded limit "
                        f"({max_time:.1f}s)",
                        {"operation": operation, "total_time": op_metrics.total_time},
                    )

            # Processing variance assertions
            if (
                op_metrics.time_variance
                > self.config.processing.max_processing_variance
            ):
                self.record_error(
                    "ProcessingVarianceError",
                    f"Processing time variance ({op_metrics.time_variance:.2f}) exceeded limit "
                    f"({self.config.processing.max_processing_variance})",
                    {"operation": operation, "variance": op_metrics.time_variance},
                )

    def assert_no_errors(self) -> None:
        """Assert that no errors were recorded during the test."""
        if self.errors:
            error_messages = "\n".join(
                f"  {error['type']}: {error['message']}" for error in self.errors
            )
            pytest.fail(f"Test encountered errors:\n{error_messages}")

    @contextmanager
    def cleanup_context(self):
        """Context manager for test cleanup operations."""
        cleanup_errors = []
        try:
            yield cleanup_errors
        finally:
            if cleanup_errors:
                self.record_error(
                    "CleanupError",
                    f"Failed to cleanup {len(cleanup_errors)} resources",
                    {"errors": cleanup_errors},
                )
                if len(cleanup_errors) > self.config.errors.max_cleanup_errors:
                    pytest.fail(
                        f"Too many cleanup errors: {len(cleanup_errors)} > "
                        f"{self.config.errors.max_cleanup_errors}"
                    )

    def setup_method(self):
        """Set up test resources."""
        pass

    def teardown_method(self):
        """Clean up test resources."""
        pass
