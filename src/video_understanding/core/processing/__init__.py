"""Video processing module.

This module provides the core video processing functionality including:
- Video pipeline management
- Scene analysis
- Resource management
- Error handling
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray

from ...models.scene import Scene
from ...models.video import Video, VideoFile
from ...types.cv2 import (
    CAP_PROP_FOURCC,
    CAP_PROP_FPS,
    CAP_PROP_FRAME_COUNT,
    CAP_PROP_FRAME_HEIGHT,
    CAP_PROP_FRAME_WIDTH,
    CAP_PROP_POS_FRAMES,
    COLOR_BGR2GRAY,
    VideoCapture,
    create_video_capture,
)
from ..config import ProcessingConfig
from ..exceptions import ProcessingError, VideoProcessingError
from .pipeline import ProcessingPipeline, analyze_scene


@dataclass
class TextDetection:
    """Results from text detection in a frame or scene."""

    text: str
    confidence: float
    bounding_box: tuple[int, int, int, int]  # (x, y, width, height)
    frame_number: int | None = None
    timestamp: float | None = None
    language: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "text": self.text,
            "confidence": self.confidence,
            "bounding_box": self.bounding_box,
            "frame_number": self.frame_number,
            "timestamp": self.timestamp,
            "language": self.language,
        }


@dataclass
class TranscriptionResult:
    """Results from audio transcription."""

    text: str
    start_time: float
    end_time: float
    speaker: str | None = None
    confidence: float = 0.0
    language: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "text": self.text,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "speaker": self.speaker,
            "confidence": self.confidence,
            "language": self.language,
        }


@dataclass
class SceneResults:
    """Results from scene processing."""

    metadata: dict[str, Any]  # Scene metadata dictionary
    extracted_text: list[TextDetection] = field(default_factory=list)
    detected_objects: list[str] = field(default_factory=list)
    transcription: list[TranscriptionResult] = field(default_factory=list)
    speakers: list[str] = field(default_factory=list)
    error: str | None = None
    processing_time: float = 0.0
    confidence_score: float = 0.0
    custom_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "metadata": self.metadata,
            "extracted_text": [text.to_dict() for text in self.extracted_text],
            "detected_objects": self.detected_objects,
            "transcription": [trans.to_dict() for trans in self.transcription],
            "speakers": self.speakers,
            "error": self.error,
            "processing_time": self.processing_time,
            "confidence_score": self.confidence_score,
            "custom_data": self.custom_data,
        }


@dataclass
class VideoResults:
    """Results from video processing."""

    metadata: VideoFile
    scenes: list[dict[str, Any]]  # List of scene metadata dictionaries
    extracted_text: list[TextDetection] = field(default_factory=list)
    detected_objects: list[str] = field(default_factory=list)
    transcription: list[TranscriptionResult] = field(default_factory=list)
    speakers: list[str] = field(default_factory=list)
    error: str | None = None
    processing_time: float = 0.0
    confidence_score: float = 0.0
    custom_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "metadata": {
                "filename": self.metadata.filename,
                "file_path": self.metadata.file_path,
                "format": self.metadata.format,
                "file_size": self.metadata.file_size,
                "duration": self.metadata.duration,
                "width": self.metadata.width,
                "height": self.metadata.height,
                "fps": self.metadata.fps,
                "total_frames": self.metadata.total_frames,
                "codec": self.metadata.codec,
                "bitrate": self.metadata.bitrate,
            },
            "scenes": self.scenes,
            "extracted_text": [text.to_dict() for text in self.extracted_text],
            "detected_objects": self.detected_objects,
            "transcription": [trans.to_dict() for trans in self.transcription],
            "speakers": self.speakers,
            "error": self.error,
            "processing_time": self.processing_time,
            "confidence_score": self.confidence_score,
            "custom_data": self.custom_data,
        }


def process_video(video: Video, output_dir: Path | None = None) -> dict[str, Any]:
    """Process a video file and return analysis results.

    Args:
        video: Video object containing file information
        output_dir: Optional directory for storing intermediate files

    Returns:
        Dictionary containing processing results including scenes, transcription,
        extracted text, and metadata

    Raises:
        ProcessingError: If video processing fails
    """
    try:
        processor = VideoProcessor()
        results = processor.process(str(video.file_info.file_path))

        return results.to_dict()

    except Exception as e:
        raise ProcessingError(f"Failed to process video: {e!s}")


def extract_frames(video: Video, output_dir: Path) -> list[Path]:
    """Extract frames from video at regular intervals.

    Args:
        video: Video object containing file information
        output_dir: Directory to save extracted frames

    Returns:
        List of paths to extracted frame images

    Raises:
        ProcessingError: If frame extraction fails
    """
    try:
        cap = cv2.VideoCapture(str(video.file_info.file_path))
        if not cap.isOpened():
            raise ProcessingError(
                f"Could not open video file: {video.file_info.file_path}"
            )

        frame_paths: list[Path] = []
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Save every 30th frame (adjust as needed)
            if frame_count % 30 == 0:
                frame_path = output_dir / f"frame_{frame_count:06d}.jpg"
                cv2.imwrite(str(frame_path), frame)
                frame_paths.append(frame_path)

            frame_count += 1

        return frame_paths

    except Exception as e:
        raise ProcessingError(f"Failed to extract frames: {e!s}")

    finally:
        if "cap" in locals():
            cap.release()


def detect_text(frame_path: Path) -> list[TextDetection]:
    """Detect and extract text from an image frame.

    Args:
        frame_path: Path to the image frame

    Returns:
        List of TextDetection objects containing detected text and metadata

    Raises:
        ProcessingError: If text detection fails
    """
    try:
        # Load image
        image = cv2.imread(str(frame_path))
        if image is None:
            return []

        # TODO: Implement actual text detection using OCR
        # For now, return dummy data
        return [
            TextDetection(
                text="Sample Text", confidence=0.95, bounding_box=(100, 100, 200, 50)
            )
        ]

    except Exception as e:
        raise ProcessingError(f"Failed to detect text: {e!s}")


def transcribe_audio(video: Video) -> list[TranscriptionResult]:
    """Transcribe audio from video file.

    Args:
        video: Video object containing file information

    Returns:
        List of TranscriptionResult objects containing transcribed text and metadata

    Raises:
        ProcessingError: If audio transcription fails
    """
    try:
        # TODO: Implement actual audio transcription
        # For now, return dummy data
        return [
            TranscriptionResult(
                text="Sample transcription",
                start_time=0.0,
                end_time=5.0,
                speaker="Speaker 1",
                confidence=0.9,
            )
        ]

    except Exception as e:
        raise ProcessingError(f"Failed to transcribe audio: {e!s}")


class VideoProcessor:
    """Main class for processing video content."""

    def __init__(self, config: ProcessingConfig | None = None):
        self.config = config or ProcessingConfig()
        self._validate_config()

    def process(self, video_path: str) -> VideoResults:
        """Process a video file and return its results."""
        start_time = datetime.now()
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise VideoProcessingError(f"Could not open video file: {video_path}")

            # Extract basic video properties
            metadata = self._extract_metadata(cap, video_path)

            # Process video content
            scenes = self._detect_scenes(cap)

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            return VideoResults(
                metadata=metadata,
                scenes=scenes,
                processing_time=processing_time,
                confidence_score=1.0,  # Default confidence
            )

        except Exception as e:
            error_msg = str(e)
            return VideoResults(
                metadata=VideoFile(
                    filename=os.path.basename(video_path),
                    file_path=video_path,
                    format="unknown",
                    file_size=0,
                    duration=0.0,
                    width=0,
                    height=0,
                    fps=0.0,
                    total_frames=0,
                    codec="",
                    bitrate=0,
                ),
                scenes=[],
                error=error_msg,
                processing_time=(datetime.now() - start_time).total_seconds(),
                confidence_score=0.0,
            )
        finally:
            if "cap" in locals():
                cap.release()

    def _validate_config(self) -> None:
        """Validate processing configuration."""
        if not self.config.supported_formats:
            raise ValueError("No supported video formats specified")
        if self.config.min_scene_length <= 0:
            raise ValueError("Minimum scene length must be positive")
        if self.config.max_scenes <= 0:
            raise ValueError("Maximum number of scenes must be positive")

    def _extract_metadata(self, cap: cv2.VideoCapture, video_path: str) -> VideoFile:
        """Extract basic metadata from video file."""
        width = int(cap.get(CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(CAP_PROP_FPS)
        frame_count = int(cap.get(CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0

        # Get video codec
        fourcc = int(cap.get(CAP_PROP_FOURCC))
        codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])

        return VideoFile(
            filename=os.path.basename(video_path),
            file_path=video_path,
            format=os.path.splitext(video_path)[1][1:].lower(),
            file_size=os.path.getsize(video_path),
            duration=duration,
            width=width,
            height=height,
            fps=fps,
            total_frames=frame_count,
            codec=codec,
            bitrate=0,  # TODO: Calculate actual bitrate
        )

    def _detect_scenes(self, cap: cv2.VideoCapture) -> list[dict[str, Any]]:
        """Detect scenes in video using content-based detection."""
        scenes: list[dict[str, Any]] = []
        prev_frame = None
        frame_count = 0
        scene_start = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if prev_frame is not None:
                # Calculate frame difference
                diff = cv2.absdiff(
                    cv2.cvtColor(frame, COLOR_BGR2GRAY),
                    cv2.cvtColor(prev_frame, COLOR_BGR2GRAY),
                )

                # Convert cv2 matrix to numpy array and calculate mean
                diff_array: NDArray[np.float64] = np.array(diff, dtype=np.float64)

                # If difference is significant, mark as scene boundary
                if (
                    np.mean(diff_array) > 30  # Arbitrary threshold
                    and frame_count - scene_start >= self.config.min_scene_length * cap.get(
                        CAP_PROP_FPS
                    )
                ):

                    scenes.append(
                        {
                            "start_time": scene_start / cap.get(CAP_PROP_FPS),
                            "end_time": frame_count / cap.get(CAP_PROP_FPS),
                            "frame_start": scene_start,
                            "frame_end": frame_count,
                        }
                    )

                    scene_start = frame_count

                    # Check if we've exceeded max scenes
                    if len(scenes) >= self.config.max_scenes:
                        break

            prev_frame = frame.copy()
            frame_count += 1

        # Add final scene if needed
        if scene_start < frame_count - 1:
            scenes.append(
                {
                    "start_time": scene_start / cap.get(CAP_PROP_FPS),
                    "end_time": frame_count / cap.get(CAP_PROP_FPS),
                    "frame_start": scene_start,
                    "frame_end": frame_count,
                }
            )

        return scenes


__all__ = [
    "ProcessingPipeline",
    "SceneResults",
    "TextDetection",
    "TranscriptionResult",
    "VideoProcessor",
    "VideoResults",
    "analyze_scene",
    "detect_text",
    "extract_frames",
    "process_video",
    "transcribe_audio",
    "Scene",
    "CAP_PROP_POS_FRAMES",
    "VideoCapture",
    "create_video_capture",
]
