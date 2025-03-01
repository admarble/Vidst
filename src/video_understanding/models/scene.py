"""Scene model for representing video scenes."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4


@dataclass
class Scene:
    """Represents a detected scene in a video.

    A scene represents a continuous segment of video content between detected
    boundaries. Each scene has a start and end time, an optional keyframe image,
    and associated metadata. The class provides functionality to validate time
    boundaries and track scene information.

    Attributes:
        video_id (UUID): Unique identifier of the parent video
        start_time (float): Start time of the scene in seconds from video start
        end_time (float): End time of the scene in seconds from video start
        id (UUID): Unique identifier for this scene, auto-generated if not provided
        keyframe_path (Optional[Path]): Path to the extracted keyframe image file
        confidence_score (float): Scene boundary detection confidence (0.0 to 1.0)
        metadata (dict): Additional scene metadata like detected objects, text, etc.
        created_at (datetime): When this scene was detected/created

    Example:
        >>> from uuid import uuid4
        >>> from pathlib import Path
        >>> video_id = uuid4()
        >>> scene = Scene(
        ...     video_id=video_id,
        ...     start_time=10.5,
        ...     end_time=25.2,
        ...     keyframe_path=Path("keyframes/scene_001.jpg"),
        ...     confidence_score=0.95,
        ...     metadata={"detected_objects": ["person", "car"]}
        ... )
        >>> print(f"Scene duration: {scene.duration:.1f} seconds")
        Scene duration: 14.7 seconds
    """

    video_id: UUID
    start_time: float  # Start time in seconds
    end_time: float  # End time in seconds
    id: UUID = field(default_factory=uuid4)
    keyframe_path: Path | None = None
    confidence_score: float = 0.0
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate and process scene attributes after initialization.

        Ensures:
            - UUID fields are properly typed
            - Time values are valid (non-negative start, end > start)

        Raises:
            ValueError: If start_time is negative or end_time <= start_time
            TypeError: If UUID fields cannot be converted to UUID type
        """
        # Ensure UUID type
        if isinstance(self.id, str):
            self.id = UUID(self.id)
        if isinstance(self.video_id, str):
            self.video_id = UUID(self.video_id)

        # Validate time values
        if self.start_time < 0:
            raise ValueError("Start time cannot be negative")
        if self.end_time < self.start_time:
            raise ValueError("End time must be greater than start time")

    @property
    def duration(self) -> float:
        """Calculate the duration of the scene in seconds.

        Returns:
            float: Scene duration in seconds (end_time - start_time)
        """
        return self.end_time - self.start_time

    @property
    def has_keyframe(self) -> bool:
        """Check if the scene has a valid keyframe image.

        Returns:
            bool: True if keyframe_path exists and points to a valid file
        """
        return self.keyframe_path is not None and self.keyframe_path.exists()

    def to_dict(self) -> dict:
        """Convert scene to dictionary representation."""
        return {
            "id": str(self.id),
            "video_id": str(self.video_id),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "keyframe_path": str(self.keyframe_path) if self.keyframe_path else None,
            "confidence_score": self.confidence_score,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Scene":
        """Create scene instance from dictionary."""
        # Convert string paths to Path objects
        if data.get("keyframe_path"):
            data["keyframe_path"] = Path(data["keyframe_path"])

        # Convert ISO format string to datetime
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])

        return cls(**data)

    def validate(self) -> bool:
        """Validate scene properties."""
        try:
            # Check duration requirements (minimum 2 seconds)
            if self.duration < 2.0:
                return False

            # Check keyframe if path is set
            if self.keyframe_path and not self.has_keyframe:
                return False

            # Check confidence score range
            if not 0.0 <= self.confidence_score <= 1.0:
                return False

            return True
        except Exception:
            return False
