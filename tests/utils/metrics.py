"""Utilities for collecting and analyzing performance metrics."""

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np
import psutil


@dataclass
class Measurement:
    """Individual performance measurement."""

    label: str
    timestamp: datetime
    time_elapsed: float
    memory_used: float
    cpu_percent: float
    context: dict = field(default_factory=dict)


@dataclass
class OperationMetrics:
    """Metrics for a specific operation type."""

    name: str
    measurements: list[Measurement] = field(default_factory=list)

    @property
    def total_time(self) -> float:
        """Calculate total time taken for all measurements."""
        if not self.measurements:
            return 0.0
        return self.measurements[-1].time_elapsed - self.measurements[0].time_elapsed

    @property
    def average_time(self) -> float:
        """Calculate average time per measurement."""
        if not self.measurements:
            return 0.0
        return self.total_time / len(self.measurements)

    @property
    def time_variance(self) -> float:
        """Calculate variance in measurement times."""
        if len(self.measurements) < 2:
            return 0.0
        times = [m.time_elapsed for m in self.measurements]
        return float(np.var(times))

    @property
    def peak_memory(self) -> float:
        """Get peak memory usage across measurements."""
        if not self.measurements:
            return 0.0
        return max(m.memory_used for m in self.measurements)

    @property
    def average_memory(self) -> float:
        """Calculate average memory usage."""
        if not self.measurements:
            return 0.0
        return sum(m.memory_used for m in self.measurements) / len(self.measurements)

    @property
    def memory_growth(self) -> float:
        """Calculate memory growth rate in MB/hour."""
        if len(self.measurements) < 2:
            return 0.0
        first, last = self.measurements[0], self.measurements[-1]
        time_diff = (last.timestamp - first.timestamp).total_seconds() / 3600
        if time_diff == 0:
            return 0.0
        return (last.memory_used - first.memory_used) / time_diff


class PerformanceMetrics:
    """Collector for performance metrics during testing."""

    def __init__(self):
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
        self.operations: dict[str, OperationMetrics] = {}

    def measure(self, label: str, context: dict | None = None) -> None:
        """Record a measurement with the given label."""
        current_time = time.time()
        current_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB

        measurement = Measurement(
            label=label,
            timestamp=datetime.now(),
            time_elapsed=current_time - self.start_time,
            memory_used=current_memory - self.start_memory,
            cpu_percent=psutil.cpu_percent(),
            context=context or {},
        )

        operation_name = label.split("_")[0]  # e.g., 'upload' from 'upload_start'
        if operation_name not in self.operations:
            self.operations[operation_name] = OperationMetrics(name=operation_name)
        self.operations[operation_name].measurements.append(measurement)

    @contextmanager
    def measure_operation(self, operation: str, context: dict | None = None):
        """Context manager for measuring an operation's duration."""
        try:
            self.measure(f"{operation}_start", context)
            yield
        finally:
            self.measure(f"{operation}_end", context)

    def get_operation_metrics(self, operation: str) -> OperationMetrics | None:
        """Get metrics for a specific operation."""
        return self.operations.get(operation)

    def get_summary(self) -> dict:
        """Get summary of all metrics."""
        return {
            "total_duration": time.time() - self.start_time,
            "peak_memory": max(
                op.peak_memory for op in self.operations.values() if op.measurements
            ),
            "operations": {
                name: {
                    "total_time": op.total_time,
                    "average_time": op.average_time,
                    "time_variance": op.time_variance,
                    "peak_memory": op.peak_memory,
                    "average_memory": op.average_memory,
                    "memory_growth": op.memory_growth,
                }
                for name, op in self.operations.items()
            },
        }

    def print_summary(self) -> None:
        """Print a human-readable summary of metrics."""
        summary = self.get_summary()

        print("\nPerformance Test Summary")
        print("=" * 50)
        print(f"Total Duration: {summary['total_duration']:.2f} seconds")
        print(f"Peak Memory: {summary['peak_memory']:.1f} MB")
        print("\nOperation Details:")

        for op_name, op_metrics in summary["operations"].items():
            print(f"\n{op_name}:")
            print(f"  Total Time: {op_metrics['total_time']:.2f}s")
            print(f"  Average Time: {op_metrics['average_time']:.2f}s")
            print(f"  Time Variance: {op_metrics['time_variance']:.2f}")
            print(f"  Peak Memory: {op_metrics['peak_memory']:.1f} MB")
            print(f"  Memory Growth: {op_metrics['memory_growth']:.1f} MB/hour")
