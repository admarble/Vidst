# Scene Detection Service Interface

## Overview

The Scene Detection service interface provides a standardized way to detect and analyze scenes in videos. It abstracts away the details of specific scene detection implementations, allowing for easy switching between different providers like Twelve Labs or OpenCV-based detection.

## Key Components

### BaseSceneDetector

The `BaseSceneDetector` class provides a standardized interface for scene detection operations:

- **detect_scenes**: Detect scenes in a video with timestamps and metadata
- **close**: Close resources used by the scene detector

### TwelveLabsSceneDetection

The `TwelveLabsSceneDetection` class implements the `BaseSceneDetector` interface using the Twelve Labs API:

- **API Integration**: Handles communication with the Twelve Labs API
- **Error Handling**: Provides detailed error messages for API-specific errors
- **Scene Validation**: Validates scenes based on duration and confidence thresholds

### SceneDetectionService

The `SceneDetectionService` class provides a factory-like functionality to create and manage scene detectors:

- **Detector Creation**: Creates scene detectors of different types
- **Detector Caching**: Caches detector instances for reuse
- **Simplified API**: Provides a simplified API for scene detection

## Configuration

### TwelveLabsConfig

The `TwelveLabsConfig` class provides configuration options for the Twelve Labs scene detection:

```python
class TwelveLabsConfig(ServiceConfig):
    """Configuration for Twelve Labs scene detection."""
    api_key: str
    api_url: str = "https://api.twelvelabs.io/v1.1"
    confidence_threshold: float = 0.5
    min_scene_duration: float = 1.0
    max_scenes: int = 100
```

## Usage Examples

### Basic Usage

```python
from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetection

# Create scene detector
detector = TwelveLabsSceneDetection(
    api_key="your-twelve-labs-key",
    config={
        "confidence_threshold": 0.7,
        "min_scene_duration": 2.0,
        "max_scenes": 50,
    }
)

# Detect scenes
scenes = await detector.detect_scenes("path/to/video.mp4")

# Process scenes
for scene in scenes:
    print(f"Scene {scene['scene_id']}: {scene['start_time']}s to {scene['end_time']}s")

# Close detector
await detector.close()
```

### Service-based Usage

```python
from video_understanding.ai.scene.service import SceneDetectionService

# Create service
service = SceneDetectionService(detector_type="twelve_labs")

# Detect scenes
scenes = await service.detect_scenes("path/to/video.mp4")

# Process scenes
for scene in scenes:
    print(f"Scene {scene['scene_id']}: {scene['start_time']}s to {scene['end_time']}s")
```

### Factory-based Usage

```python
from video_understanding.services.factory import ServiceFactory
from video_understanding.ai.scene.base import BaseSceneDetector
from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetection, TwelveLabsConfig

# Create service factory
factory = ServiceFactory[ServiceConfig, BaseService]()

# Register scene detector implementations
factory.register("twelve_labs", TwelveLabsSceneDetection)

# Create configuration
config = TwelveLabsConfig(
    service_name="twelve_labs_scene_detection",
    api_key="your-twelve-labs-key",
    confidence_threshold=0.7,
    min_scene_duration=2.0,
)

# Create service instance
scene_detector = factory.create("twelve_labs", config)

# Use as before
await scene_detector.initialize()
scenes = await scene_detector.detect_scenes("path/to/video.mp4")
await scene_detector.shutdown()
```

## Error Handling

```python
from video_understanding.ai.scene.twelve_labs import SceneDetectionError

try:
    scenes = await detector.detect_scenes("path/to/video.mp4")
except SceneDetectionError as e:
    print(f"Scene detection error: {e}")
    # Handle the error
```

## Implementation Details

### Detecting Scenes

The `detect_scenes` method detects scenes in a video:

```python
async def detect_scenes(self, video_path: str) -> List[Dict[str, Any]]:
    """Detect scenes in a video.

    Args:
        video_path: Path to the video file

    Returns:
        List of detected scenes with:
            - scene_id: Unique scene identifier
            - start_time: Scene start time in seconds
            - end_time: Scene end time in seconds
            - duration: Scene duration in seconds
            - confidence: Detection confidence score (0-1)

    Raises:
        SceneDetectionError: If scene detection fails
    """
```

### Scene Data Structure

Each scene returned by the `detect_scenes` method contains the following information:

```python
{
    "scene_id": 1,              # Unique identifier for the scene
    "start_time": 10.5,         # Start time in seconds
    "end_time": 25.2,           # End time in seconds
    "duration": 14.7,           # Duration in seconds
    "confidence": 0.95,         # Confidence score (0-1)
    "description": "A person presenting slides"  # Optional description
}
```

### Closing Resources

The `close` method closes resources used by the scene detector:

```python
async def close(self) -> None:
    """Close resources used by the scene detection.

    This method should be called when the detector is no longer needed
    to release any resources used by the detector.
    """
```

## Best Practices

1. **Close Resources**: Always call `close()` when done to release resources.
2. **Error Handling**: Use try-except blocks to handle potential errors.
3. **Configuration Tuning**: Adjust confidence threshold and minimum scene duration based on your specific needs.
4. **Service Usage**: Use the `SceneDetectionService` for simplified scene detection.
5. **Video Validation**: Ensure the video file exists and is in a supported format before passing it to the scene detector.
6. **Scene Processing**: Process scenes in batches for better performance with large videos.
7. **Fallback Strategy**: Implement a fallback strategy for when the primary scene detection method fails.
8. **Caching Results**: Consider caching scene detection results for frequently accessed videos.
9. **Parallel Processing**: For multiple videos, process them in parallel for better throughput.
