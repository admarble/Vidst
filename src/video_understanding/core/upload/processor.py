"""Video upload processing orchestration.

This module provides the main upload processing functionality, orchestrating
the various components involved in video upload handling.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
import asyncio

import cv2
import numpy as np

from video_understanding.utils.exceptions import (
    ProcessingError,
    SecurityError,
    VideoIntegrityError,
)
from video_understanding.models.video import (
    Video,
    VideoFile,
    VideoProcessingInfo,
    ProcessingStatus,
    VideoMetadata,
)
from video_understanding.core.upload.directory import DirectoryManager
from video_understanding.core.upload.integrity import VideoIntegrityChecker as FileIntegrityChecker
from video_understanding.core.upload.security import SecurityValidator as SecurityScanner
from video_understanding.core.upload.quarantine import QuarantineManager
from video_understanding.core.upload.config import ProcessorConfig
from video_understanding.core.upload.context import UploadContext
from video_understanding.core.upload.progress import ProgressTracker
from video_understanding.core.upload.scene import SceneDetector, SceneChange
from video_understanding.core.upload.detection import ObjectDetector
from video_understanding.core.upload.ocr import TextExtractor
from video_understanding.core.upload.config import UploadConfig
from video_understanding.core.upload.ocr import OCRProcessor
from video_understanding.exceptions import VideoUnderstandingError

logger = logging.getLogger(__name__)


class UploadProcessor:
    """Orchestrates the video upload processing pipeline.

    This class manages the complete upload process, including:
    1. File validation and security checks
    2. Video integrity verification
    3. Metadata extraction
    4. Progress tracking
    5. Error handling and quarantine

    Example:
        >>> processor = UploadProcessor(Path("/uploads"))
        >>> try:
        ...     video = processor.process_upload("video.mp4")
        ...     print(f"Processed video: {video.id}")
        ... except ProcessingError as e:
        ...     print(f"Processing failed: {e}")
    """

    def __init__(
        self,
        upload_dir: Path,
        test_mode: bool = False,
    ) -> None:
        """Initialize the upload processor.

        Args:
            upload_dir: Base directory for uploads
            test_mode: Whether to run in test mode
        """
        self.directory_manager = DirectoryManager(upload_dir, test_mode)
        self.integrity_checker = FileIntegrityChecker(test_mode)
        self.security_validator = SecurityScanner(self.directory_manager, test_mode)
        self.quarantine_manager = QuarantineManager(self.directory_manager, test_mode)
        self.test_mode = test_mode

    def process_upload(
        self,
        file_path: Path,
        video_id: Optional[UUID] = None,
    ) -> Video:
        """Process a video upload through the complete pipeline.

        Args:
            file_path: Path to the uploaded file
            video_id: Optional UUID for the video

        Returns:
            Video object with processing results

        Raises:
            ProcessingError: If processing fails
            SecurityError: If security validation fails
            VideoIntegrityError: If video validation fails
        """
        try:
            # Initialize video object
            video = self._create_video(file_path, video_id)
            self._update_status(video, ProcessingStatus.UPLOADING)

            # Move to temp directory for processing
            temp_path = self._move_to_temp(file_path)

            try:
                # Validate security
                self._update_status(video, ProcessingStatus.VALIDATING)
                self._validate_security(temp_path)

                # Check video integrity
                metadata = self._validate_integrity(temp_path)
                video.metadata = metadata

                # Move to processing directory
                self._update_status(video, ProcessingStatus.PROCESSING)
                processing_path = self._move_to_processing(temp_path)

                # Process video (placeholder for future processing)
                processed_path = self._process_video(processing_path)

                # Move to completed directory
                final_path = self._move_to_completed(processed_path, video.id)

                # Update video information
                video.file_info.file_path = final_path
                self._update_status(video, ProcessingStatus.COMPLETED)

                return video

            except (SecurityError, VideoIntegrityError) as e:
                # Quarantine file on validation failure
                self._handle_validation_failure(temp_path, str(e), video)
                raise

            except Exception as e:
                # Move to failed directory on processing failure
                self._handle_processing_failure(temp_path, str(e), video)
                raise ProcessingError(f"Upload processing failed: {e}")

        except Exception as e:
            if not isinstance(e, (ProcessingError, SecurityError, VideoIntegrityError)):
                raise ProcessingError(f"Upload processing failed: {e}")
            raise

    def _create_video(self, file_path: Path, video_id: Optional[UUID] = None) -> Video:
        """Create initial Video object for upload.

        Args:
            file_path: Path to the uploaded file
            video_id: Optional UUID for the video

        Returns:
            Initial Video object
        """
        file_info = VideoFile(
            filename=file_path.name,
            file_path=file_path,
            format=file_path.suffix[1:].upper(),
            file_size=file_path.stat().st_size,
        )
        processing = VideoProcessingInfo(
            status=ProcessingStatus.PENDING,
            start_time=datetime.now(),
        )
        return Video(
            id=video_id or uuid4(),
            file_info=file_info,
            processing=processing,
        )

    def _update_status(
        self,
        video: Video,
        status: ProcessingStatus,
        progress: float = 0.0,
        error: Optional[str] = None,
    ) -> None:
        """Update video processing status.

        Args:
            video: Video object to update
            status: New processing status
            progress: Processing progress (0-100)
            error: Optional error message
        """
        video.processing.status = status
        video.processing.progress = progress
        if error:
            video.processing.error = error
            video.processing.end_time = datetime.now()
        elif status == ProcessingStatus.COMPLETED:
            video.processing.progress = 100.0
            video.processing.end_time = datetime.now()

        logger.info(
            f"Video {video.id} status updated: {status} "
            f"(progress: {progress:.1f}%)"
        )

    def _move_to_temp(self, file_path: Path) -> Path:
        """Move uploaded file to temporary directory.

        Args:
            file_path: Path to the uploaded file

        Returns:
            Path in temporary directory

        Raises:
            ProcessingError: If move fails
        """
        try:
            return self.directory_manager.move_file(file_path, "temp")
        except Exception as e:
            raise ProcessingError(f"Failed to move file to temp directory: {e}")

    def _validate_security(self, file_path: Path) -> None:
        """Perform security validation.

        Args:
            file_path: Path to the file to validate

        Raises:
            SecurityError: If validation fails
        """
        self.security_validator.validate_and_secure(file_path)

    def _validate_integrity(self, file_path: Path) -> VideoMetadata:
        """Validate video integrity and extract metadata.

        Args:
            file_path: Path to the file to validate

        Returns:
            Extracted video metadata

        Raises:
            VideoIntegrityError: If validation fails
        """
        # Check basic integrity
        metadata = self.integrity_checker.check_video(file_path)

        # Validate frames
        self.integrity_checker.validate_frames(file_path)

        return metadata

    def _move_to_processing(self, file_path: Path) -> Path:
        """Move file to processing directory.

        Args:
            file_path: Path to the file to move

        Returns:
            Path in processing directory

        Raises:
            ProcessingError: If move fails
        """
        try:
            return self.directory_manager.move_file(file_path, "processing")
        except Exception as e:
            raise ProcessingError(f"Failed to move file to processing: {e}")

    def _process_video(self, file_path: Path) -> Path:
        """Process the video file.

        This is a placeholder for future video processing implementation.

        Args:
            file_path: Path to the file to process

        Returns:
            Path to the processed file

        Raises:
            ProcessingError: If processing fails
        """
        # TODO: Implement actual video processing
        return file_path

    def _move_to_completed(self, file_path: Path, video_id: UUID) -> Path:
        """Move processed file to completed directory.

        Args:
            file_path: Path to the file to move
            video_id: Video UUID for directory structure

        Returns:
            Path in completed directory

        Raises:
            ProcessingError: If move fails
        """
        try:
            # Create video-specific directory
            completed_dir = self.directory_manager.ensure_directory_exists(
                f"completed/{video_id}"
            )
            return self.directory_manager.move_file(
                file_path,
                f"completed/{video_id}",
            )
        except Exception as e:
            raise ProcessingError(f"Failed to move file to completed: {e}")

    def _handle_validation_failure(
        self,
        file_path: Path,
        error: str,
        video: Video,
    ) -> None:
        """Handle validation failure by quarantining the file.

        Args:
            file_path: Path to the failed file
            error: Error message
            video: Video object to update
        """
        try:
            self.quarantine_manager.quarantine_file(
                file_path,
                f"Validation failed: {error}",
                {
                    "video_id": str(video.id),
                    "filename": video.filename,
                    "failure_time": datetime.now().isoformat(),
                },
            )
            self._update_status(
                video,
                ProcessingStatus.QUARANTINED,
                error=error,
            )
        except Exception as e:
            logger.error(f"Failed to quarantine file: {e}")
            self._handle_processing_failure(file_path, str(e), video)

    def _handle_processing_failure(
        self,
        file_path: Path,
        error: str,
        video: Video,
    ) -> None:
        """Handle processing failure by moving file to failed directory.

        Args:
            file_path: Path to the failed file
            error: Error message
            video: Video object to update
        """
        try:
            self.directory_manager.move_file(file_path, "failed")
            self._update_status(
                video,
                ProcessingStatus.FAILED,
                error=error,
            )
        except Exception as e:
            logger.error(f"Failed to move file to failed directory: {e}")

    def get_upload_progress(self, video_id: UUID) -> dict:
        """Get current upload progress for a video.

        Args:
            video_id: Video UUID to check

        Returns:
            Dictionary containing progress information
        """
        # TODO: Implement progress tracking
        return {
            "status": "not_implemented",
            "progress": 0.0,
        }


class VideoProcessor:
    """Handles video processing operations.

    This class implements the video processing pipeline, including:
    1. Frame extraction and analysis
    2. Metadata generation
    3. Progress tracking
    4. Resource management

    The processing pipeline follows these stages:
    1. Pre-processing setup
    2. Frame extraction
    3. Frame analysis
    4. Metadata compilation
    5. Result generation

    Example:
        >>> processor = VideoProcessor(config)
        >>> with processor.process(video) as context:
        ...     result = processor.analyze_frames(context)
        ...     print(f"Processed {result['frame_count']} frames")
    """

    def __init__(self, config: ProcessorConfig) -> None:
        """Initialize video processor.

        Args:
            config: Processing configuration

        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Validate configuration
        config.validate()

        self.config = config
        self._progress = ProgressTracker(video_id=None)
        self._current_frame = 0
        self.scene_detector = SceneDetector()
        self.object_detector = ObjectDetector(
            confidence_threshold=config.detection_confidence,
            model_path=config.object_detection_model,
        )
        self.text_extractor = TextExtractor(
            languages=config.ocr_languages,
            confidence_threshold=config.ocr_confidence,
            gpu=config.ocr_gpu,
        )

    def process(self, video: Video) -> UploadContext:
        """Process a video file.

        This method creates a processing context and initializes the
        processing pipeline for a video.

        Args:
            video: Video to process

        Returns:
            Processing context for use in with statement

        Example:
            >>> with processor.process(video) as context:
            ...     metadata = processor.extract_metadata(context)
        """
        # Set up processing state
        self._current_video = video
        self._progress = ProgressTracker(video.id)

        # Add progress callbacks
        for callback in self.config.progress_callbacks:
            self._progress.add_callback(callback)

        # Create and return context
        return UploadContext(video, self._progress)

    def extract_metadata(self, context: UploadContext) -> Dict[str, Any]:
        """Extract metadata from video file.

        Args:
            context: Processing context

        Returns:
            Dictionary containing video metadata:
            - dimensions: (width, height)
            - duration: Duration in seconds
            - fps: Frames per second
            - frame_count: Total frame count
            - codec: Video codec information

        Raises:
            ProcessingError: If metadata extraction fails
        """
        try:
            # Update progress
            if self._progress:
                self._progress.update_progress(
                    ProcessingStatus.PROCESSING,
                    progress=0.0,
                    current_stage="metadata",
                )

            # Open video file
            cap = cv2.VideoCapture(str(context.video.file_info.file_path))
            if not cap.isOpened():
                raise ProcessingError("Failed to open video file")

            try:
                # Extract basic properties
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                codec = int(cap.get(cv2.CAP_PROP_FOURCC))

                # Calculate duration
                duration = frame_count / fps if fps > 0 else 0.0

                # Create metadata dictionary
                metadata = {
                    "dimensions": (width, height),
                    "duration": duration,
                    "fps": fps,
                    "frame_count": frame_count,
                    "codec": codec,
                }

                # Update progress
                if self._progress:
                    self._progress.update_progress(
                        ProcessingStatus.PROCESSING,
                        progress=100.0,
                        current_stage="metadata",
                        metadata=metadata,
                    )

                return metadata

            finally:
                cap.release()

        except Exception as e:
            raise ProcessingError(f"Failed to extract metadata: {e}")

    def analyze_frames(
        self,
        context: UploadContext,
        sample_rate: int = 1,
    ) -> Dict[str, Any]:
        """Analyze video frames.

        This method processes frames from the video, performing analysis
        such as scene detection, object detection, or text extraction.

        Args:
            context: Processing context
            sample_rate: Number of frames to skip between samples

        Returns:
            Dictionary containing analysis results:
            - frame_count: Number of frames analyzed
            - scenes: List of scene transitions
            - objects: Detected objects
            - text: Extracted text

        Raises:
            ProcessingError: If frame analysis fails
        """
        try:
            # Update progress
            if self._progress:
                self._progress.update_progress(
                    ProcessingStatus.PROCESSING,
                    progress=0.0,
                    current_stage="analysis",
                )

            # Open video file
            cap = cv2.VideoCapture(str(context.video.file_info.file_path))
            if not cap.isOpened():
                raise ProcessingError("Failed to open video file")

            try:
                # Get video properties
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                processed_frames = 0
                results = {
                    "frame_count": 0,
                    "scenes": [],
                    "objects": [],
                    "text": [],
                }

                # Process frames
                while True:
                    # Read frame
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # Skip frames based on sample rate
                    if processed_frames % sample_rate != 0:
                        processed_frames += 1
                        continue

                    # Process frame
                    frame_result = self._process_frame(frame, processed_frames)
                    self._update_results(results, frame_result)

                    # Update progress
                    if self._progress:
                        progress = (processed_frames / frame_count) * 100
                        self._progress.update_progress(
                            ProcessingStatus.PROCESSING,
                            progress=progress,
                            current_stage="analysis",
                            frames_processed=processed_frames,
                        )

                    processed_frames += 1

                # Update final progress
                if self._progress:
                    self._progress.update_progress(
                        ProcessingStatus.PROCESSING,
                        progress=100.0,
                        current_stage="analysis",
                        results=results,
                    )

                return results

            finally:
                cap.release()

        except Exception as e:
            raise ProcessingError(f"Failed to analyze frames: {e}")

    def _process_frame(
        self,
        frame: np.ndarray,
        frame_number: int,
    ) -> Dict[str, Any]:
        """Process a single video frame.

        Args:
            frame: Input frame as numpy array
            frame_number: Frame number in sequence

        Returns:
            Dictionary containing frame analysis results
        """
        result = {
            "frame_number": frame_number,
            "timestamp": frame_number / self._get_fps(),
        }

        # Run object detection if enabled
        if self.object_detector is not None:
            try:
                detections = self.object_detector(frame, frame_number)
                result["objects"] = [obj.to_dict() for obj in detections]
            except Exception as e:
                logger.warning(f"Object detection failed for frame {frame_number}: {e}")
                result["objects"] = []

        # Run text extraction if enabled
        if self.text_extractor is not None:
            try:
                texts = self.text_extractor.extract_text(frame)
                result["text"] = [text.to_dict() for text in texts]
            except Exception as e:
                logger.warning(f"Text extraction failed for frame {frame_number}: {e}")
                result["text"] = []

        # Add other frame processing results
        result.update(self._analyze_frame_content(frame))

        return result

    def _analyze_frame_content(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze frame content for various features.

        Args:
            frame: Input frame as numpy array

        Returns:
            Dictionary containing analysis results
        """
        result = {
            "text": [],  # Placeholder for text extraction
            "scene_change": None,
        }

        # Detect scene changes
        scene_change = self.scene_detector.detect_change(
            frame,
            frame_number=self._current_frame,
            timestamp=self._current_frame / self._get_fps(),
        )
        if scene_change:
            result["scene_change"] = {
                "confidence": scene_change.confidence,
                "type": scene_change.type,
            }

        # Run processing hooks
        self._run_frame_hooks(frame, result)

        return result

    def _update_results(
        self,
        results: Dict[str, Any],
        frame_result: Dict[str, Any],
    ) -> None:
        """Update overall results with frame results.

        Args:
            results: Overall results dictionary to update
            frame_result: Results from single frame
        """
        results["frame_count"] += 1

        # Update scene list if scene change detected
        if frame_result.get("scene_change"):
            results["scenes"].append({
                "frame": frame_result["frame_number"],
                "timestamp": frame_result["timestamp"],
                "type": frame_result["scene_change"]["type"],
                "confidence": frame_result["scene_change"]["confidence"],
            })

        # Add detected objects
        results["objects"].extend(frame_result["objects"])

        # Add extracted text
        results["text"].extend(frame_result["text"])

    def _run_frame_hooks(
        self,
        frame: np.ndarray,
        result: Dict[str, Any],
    ) -> None:
        """Run processing hooks for a frame.

        Args:
            frame: Frame data
            result: Frame result dictionary to update
        """
        if ProcessingStatus.PROCESSING in self.config.processing_hooks:
            for hook in self.config.processing_hooks[ProcessingStatus.PROCESSING]:
                try:
                    hook(frame, result)
                except Exception as e:
                    logger.error(f"Frame processing hook failed: {e}")

    def _is_scene_change(self, frame_result: Dict[str, Any]) -> bool:
        """Detect if a frame represents a scene change.

        Args:
            frame_result: Frame analysis results

        Returns:
            True if frame is a scene change
        """
        return bool(frame_result.get("scene_change"))

    def _get_fps(self) -> float:
        """Get current video FPS.

        Returns:
            Frames per second or 30.0 if unknown
        """
        if not self._current_video:
            return 30.0

        try:
            cap = cv2.VideoCapture(str(self._current_video.file_info.file_path))
            if not cap.isOpened():
                return 30.0

            try:
                return cap.get(cv2.CAP_PROP_FPS) or 30.0
            finally:
                cap.release()
        except Exception:
            return 30.0


class VideoUploader:
    """Handles video upload processing and validation."""

    def __init__(self, config: Optional[UploadConfig] = None):
        """Initialize the uploader with optional config."""
        self.config = config or UploadConfig()
        self.integrity_checker = FileIntegrityChecker()
        self.security_scanner = SecurityScanner()
        self.scene_detector = SceneDetector()
        self.ocr_processor = OCRProcessor()

    async def process_upload(self, file_path: Path) -> Dict[str, Any]:
        """Process an uploaded video file.

        Args:
            file_path: Path to the uploaded video file

        Returns:
            Dict containing processing results

        Raises:
            VideoUnderstandingError: If processing fails
        """
        try:
            # Create processing context
            context = UploadContext(file_path)

            # Run integrity checks
            await self.integrity_checker.check(file_path)

            # Scan for security issues
            await self.security_scanner.scan(file_path)

            # Detect scenes
            scenes = await self.scene_detector.detect(file_path)
            context.add_scenes(scenes)

            # Extract text with OCR
            text = await self.ocr_processor.process(file_path)
            context.add_text(text)

            return context.get_results()

        except Exception as e:
            logger.error(f"Error processing upload {file_path}: {str(e)}")
            raise VideoUnderstandingError(f"Upload processing failed: {str(e)}")

    async def process_batch(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """Process multiple uploaded files concurrently.

        Args:
            file_paths: List of paths to uploaded files

        Returns:
            List of processing results for each file
        """
        tasks = [self.process_upload(path) for path in file_paths]
        return await asyncio.gather(*tasks, return_exceptions=True)
