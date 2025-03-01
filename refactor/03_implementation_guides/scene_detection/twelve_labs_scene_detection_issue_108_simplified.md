# Simplified Implementation Instructions for Issue #108: Twelve Labs Scene Detection

## Background

We're replacing our custom OpenCV-based scene detection with the Twelve Labs API to simplify our architecture and improve accuracy (from ~90% to ~94%). This document provides streamlined implementation instructions focused on the core requirements.

## Core Requirements

1. Implement Twelve Labs API client for scene detection
2. Ensure scene detection achieves >90% accuracy
3. Implement error handling for API failures
4. Add unit tests to verify API interaction

## Implementation Steps

### 1. Understand the Basics (30 minutes)

Review these key files:
- `src/video_understanding/ai/models/twelve_labs/model.py` - Main Twelve Labs API wrapper
- `src/video_understanding/ai/models/twelve_labs/types.py` - Data type definitions including `TaskType.SCENE_DETECTION`
- `src/video_understanding/ai/scene/base.py` - Scene detection interface

### 2. Implement Core Functionality (1-2 hours)

Create `src/video_understanding/ai/scene/twelve_labs.py` with this basic implementation:

```python
"""Scene detection using Twelve Labs API."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from video_understanding.ai.exceptions import SceneDetectionError
from video_understanding.ai.models.twelve_labs.model import TwelveLabsModel
from video_understanding.ai.models.twelve_labs.types import TaskType
from video_understanding.ai.scene.base import BaseSceneDetector
from video_understanding.utils.credentials import get_twelve_labs_credentials

logger = logging.getLogger(__name__)

class TwelveLabsSceneDetection(BaseSceneDetector):
    """Scene detection using Twelve Labs API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize scene detection.
        
        Args:
            api_key: Optional API key (if not provided, loaded from environment)
        """
        try:
            # Get API key from credentials if not provided
            if api_key is None:
                credentials = get_twelve_labs_credentials()
                api_key = credentials["api_key"]
                
            # Initialize the Twelve Labs model
            self.model = TwelveLabsModel(api_key=api_key)
            logger.info("Initialized Twelve Labs scene detection")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twelve Labs scene detection: {e}")
            raise SceneDetectionError(f"Initialization failed: {e}")
    
    async def detect_scenes(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect scenes in a video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of detected scenes with timing information
            
        Raises:
            SceneDetectionError: If detection fails
        """
        try:
            # Validate video path
            video_path_obj = Path(video_path)
            if not video_path_obj.exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Process video with Twelve Labs
            logger.info(f"Detecting scenes in video: {video_path}")
            result = await self.model.process({
                "video_path": str(video_path_obj),
                "task": TaskType.SCENE_DETECTION,
                "options": {
                    "confidence_threshold": 0.5  # Adjust if needed
                }
            })
            
            # Extract scenes from result
            scenes = []
            raw_scenes = result.get("data", {}).get("scenes", [])
            
            for i, scene in enumerate(raw_scenes):
                scenes.append({
                    "scene_id": i + 1,
                    "start_time": scene.get("start_time", 0),
                    "end_time": scene.get("end_time", 0),
                    "duration": scene.get("end_time", 0) - scene.get("start_time", 0),
                    "confidence": scene.get("confidence", 0),
                })
            
            logger.info(f"Detected {len(scenes)} scenes")
            return scenes
            
        except Exception as e:
            logger.error(f"Scene detection failed: {e}")
            raise SceneDetectionError(f"Detection failed: {e}")
    
    async def close(self) -> None:
        """Clean up resources."""
        if hasattr(self, 'model'):
            await self.model.close()
```

### 3. Add Essential Unit Tests (1 hour)

Create a basic test file at `tests/video_understanding/ai/scene/test_twelve_labs.py`:

```python
"""Tests for Twelve Labs scene detection."""

import pytest
from unittest.mock import MagicMock, patch

from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetection
from video_understanding.ai.models.twelve_labs.model import TwelveLabsModel
from video_understanding.ai.models.twelve_labs.types import TaskType
from video_understanding.ai.exceptions import SceneDetectionError

# Mock data
SAMPLE_VIDEO_PATH = "tests/data/sample_video.mp4"
MOCK_API_RESPONSE = {
    "data": {
        "scenes": [
            {"start_time": 0.0, "end_time": 10.5, "confidence": 0.95},
            {"start_time": 10.5, "end_time": 25.2, "confidence": 0.92},
        ]
    }
}

@pytest.fixture
def mock_model():
    """Create a mock Twelve Labs model."""
    mock = MagicMock(spec=TwelveLabsModel)
    
    async def mock_process(input_data):
        return MOCK_API_RESPONSE
    
    mock.process = mock_process
    return mock

@pytest.mark.asyncio
async def test_initialization():
    """Test initialization with credentials."""
    with patch('video_understanding.utils.credentials.get_twelve_labs_credentials') as mock_get_creds:
        mock_get_creds.return_value = {"api_key": "test_api_key"}
        
        with patch('video_understanding.ai.models.twelve_labs.model.TwelveLabsModel') as mock_model_class:
            detector = TwelveLabsSceneDetection()
            mock_model_class.assert_called_once_with(api_key="test_api_key")

@pytest.mark.asyncio
async def test_scene_detection():
    """Test basic scene detection."""
    # Create detector with mock model
    detector = TwelveLabsSceneDetection(api_key="test_api_key")
    detector.model = mock_model()
    
    # Mock Path.exists to return True
    with patch('pathlib.Path.exists', return_value=True):
        scenes = await detector.detect_scenes(SAMPLE_VIDEO_PATH)
    
    # Basic assertions
    assert len(scenes) == 2
    assert scenes[0]["start_time"] == 0.0
    assert scenes[0]["end_time"] == 10.5
    assert scenes[1]["start_time"] == 10.5
    assert scenes[1]["end_time"] == 25.2

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling."""
    # Create detector with mock model that raises exception
    detector = TwelveLabsSceneDetection(api_key="test_api_key")
    mock = MagicMock(spec=TwelveLabsModel)
    mock.process.side_effect = Exception("API Error")
    detector.model = mock
    
    # Mock Path.exists to return True
    with patch('pathlib.Path.exists', return_value=True):
        with pytest.raises(SceneDetectionError):
            await detector.detect_scenes(SAMPLE_VIDEO_PATH)
```

### 4. Update the Scene Detection Service (30 minutes)

Update the service to use your implementation:

```python
# In src/video_understanding/ai/scene/service.py

from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetection

# Update the factory method or service initialization
def get_scene_detector(detector_type="twelve_labs"):
    """Get appropriate scene detector."""
    if detector_type == "twelve_labs":
        return TwelveLabsSceneDetection()
    # Add fallback or other implementations if needed
```

## Testing

### Basic Tests (Required)
```
pytest tests/video_understanding/ai/scene/test_twelve_labs.py -v
```

### Manual Testing (Optional)
Create a simple script to verify actual detection results:

```python
# test_scene_detection.py
import asyncio
from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetection

async def main():
    detector = TwelveLabsSceneDetection()
    try:
        scenes = await detector.detect_scenes("path/to/test/video.mp4")
        print(f"Detected {len(scenes)} scenes:")
        for scene in scenes:
            print(f"Scene {scene['scene_id']}: {scene['start_time']} - {scene['end_time']} (confidence: {scene['confidence']})")
    finally:
        await detector.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Checklist

Before submitting, verify you've completed these core requirements:

- [ ] Twelve Labs API client integration is working
- [ ] Scene detection returns correct results
- [ ] Basic error handling is implemented
- [ ] Unit tests pass

## Resources

- [Twelve Labs API Documentation](https://docs.twelvelabs.io/)
- [Vidst Twelve Labs Integration Strategy](../vidst_twelve_labs_integration_strategy.md)

## Future Enhancements (Optional)

These items are not required for the initial implementation but can be added later:

1. Advanced accuracy validation
2. More comprehensive error handling with fallbacks
3. Additional unit tests with more edge cases
4. Integration tests with real API calls
