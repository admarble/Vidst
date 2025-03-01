"""Progress tracking for video upload processing.

This module provides functionality for tracking progress of video uploads
and processing through various stages.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID

from video_understanding.models.video import ProcessingStatus

logger = logging.getLogger(__name__)


@dataclass
class ProgressInfo:
    """Information about processing stage progress.

    Attributes:
        stage: Current processing stage
        progress: Progress percentage (0-100)
        start_time: When this stage started
        details: Additional stage-specific details
        error: Error message if stage failed
    """
    stage: ProcessingStatus
    progress: float
    start_time: datetime
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate progress information."""
        if not isinstance(self.stage, ProcessingStatus):
            raise ValueError(f"Invalid stage: {self.stage}")
        self.progress = min(max(float(self.progress), 0.0), 100.0)


class ProgressTracker:
    """Tracks upload and processing progress.

    This class manages progress tracking through various processing stages,
    including:
    1. Stage transitions
    2. Progress updates
    3. Error tracking
    4. Progress callbacks

    Example:
        >>> tracker = ProgressTracker(video_id)
        >>> tracker.add_callback(lambda info: print(f"Progress: {info.progress}%"))
        >>> tracker.update_progress(ProcessingStatus.UPLOADING, 50.0)
    """

    def __init__(self, video_id: UUID) -> None:
        """Initialize the progress tracker.

        Args:
            video_id: UUID of the video being processed
        """
        self.video_id = video_id
        self.stages: Dict[ProcessingStatus, ProgressInfo] = {}
        self.callbacks: List[Callable[[ProgressInfo], None]] = []
        self.current_stage: Optional[ProcessingStatus] = None
        self._start_time = datetime.now()

    def update_progress(
        self,
        stage: ProcessingStatus,
        progress: float,
        **details: Any,
    ) -> None:
        """Update progress for a processing stage.

        Args:
            stage: Processing stage to update
            progress: Current progress (0-100)
            **details: Additional stage-specific details
        """
        try:
            # Create progress info
            info = ProgressInfo(
                stage=stage,
                progress=progress,
                start_time=self.stages[stage].start_time if stage in self.stages
                else datetime.now(),
                details=details,
            )

            # Update stage information
            self.stages[stage] = info
            self.current_stage = stage

            # Notify callbacks
            self._notify_callbacks(info)

            logger.debug(
                f"Progress updated for {self.video_id}: "
                f"{stage.value} - {progress:.1f}%"
            )

        except Exception as e:
            logger.error(f"Failed to update progress: {e}")

    def mark_stage_error(
        self,
        stage: ProcessingStatus,
        error: str,
        **details: Any,
    ) -> None:
        """Mark a stage as failed.

        Args:
            stage: Failed processing stage
            error: Error message
            **details: Additional error details
        """
        try:
            # Create error progress info
            info = ProgressInfo(
                stage=stage,
                progress=self.stages[stage].progress if stage in self.stages else 0.0,
                start_time=self.stages[stage].start_time if stage in self.stages
                else datetime.now(),
                details=details,
                error=error,
            )

            # Update stage information
            self.stages[stage] = info
            self.current_stage = stage

            # Notify callbacks
            self._notify_callbacks(info)

            logger.error(
                f"Stage failed for {self.video_id}: "
                f"{stage.value} - {error}"
            )

        except Exception as e:
            logger.error(f"Failed to mark stage error: {e}")

    def add_callback(
        self,
        callback: Callable[[ProgressInfo], None],
    ) -> None:
        """Add a progress callback.

        Args:
            callback: Function to call with progress updates
        """
        self.callbacks.append(callback)

    def remove_callback(
        self,
        callback: Callable[[ProgressInfo], None],
    ) -> None:
        """Remove a progress callback.

        Args:
            callback: Callback to remove
        """
        try:
            self.callbacks.remove(callback)
        except ValueError:
            pass

    def get_stage_progress(
        self,
        stage: ProcessingStatus,
    ) -> Optional[ProgressInfo]:
        """Get progress information for a stage.

        Args:
            stage: Processing stage to get progress for

        Returns:
            Progress information or None if stage not started
        """
        return self.stages.get(stage)

    def get_overall_progress(self) -> float:
        """Calculate overall processing progress.

        Returns:
            Overall progress percentage (0-100)
        """
        if not self.stages:
            return 0.0

        # Weight progress by stage order
        stage_weights = {
            ProcessingStatus.PENDING: 0.0,
            ProcessingStatus.UPLOADING: 0.2,
            ProcessingStatus.VALIDATING: 0.3,
            ProcessingStatus.PROCESSING: 0.4,
            ProcessingStatus.COMPLETED: 1.0,
            ProcessingStatus.FAILED: 1.0,
            ProcessingStatus.QUARANTINED: 1.0,
        }

        # Get highest stage reached
        current_stage = max(
            self.stages.keys(),
            key=lambda s: stage_weights[s],
        )
        current_weight = stage_weights[current_stage]
        current_progress = self.stages[current_stage].progress

        # Calculate overall progress
        return (
            current_weight * 100.0 +
            (current_progress * (1.0 - current_weight))
        )

    def _notify_callbacks(self, info: ProgressInfo) -> None:
        """Notify all callbacks of a progress update.

        Args:
            info: Progress information to send to callbacks
        """
        for callback in self.callbacks:
            try:
                callback(info)
            except Exception as e:
                logger.error(f"Progress callback failed: {e}")
                # Remove failed callback
                self.remove_callback(callback)
