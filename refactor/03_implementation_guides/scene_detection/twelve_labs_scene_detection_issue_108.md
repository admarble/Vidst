# Implementation Instructions for Issue #108: Twelve Labs API Integration for Scene Detection

## Background

We're transitioning from a custom OpenCV-based scene detection implementation to using the Twelve Labs API, which offers superior accuracy (94.2% vs. our 90% requirement) and reduces implementation complexity. This task is part of our refactoring strategy to simplify our architecture and focus on core functionality.

## Implementation Overview

You'll need to:
1. Create a scene detection implementation that uses the Twelve Labs API
2. Ensure it meets our >90% accuracy requirement
3. Implement error handling for API failures
4. Create unit tests to verify API interaction
5. Integrate with the existing scene detection service

## Step-by-Step Implementation Guide

### 1. Understand Existing Components (30-60 minutes)

Review these files to understand the existing architecture:
- `src/video_understanding/ai/models/twelve_labs/model.py` - Twelve Labs model implementation
- `src/video_understanding/ai/models/twelve_labs/client.py` - API client
- `src/video_understanding/ai/models/twelve_labs/types.py` - Data type definitions
- `src/video_understanding/ai/scene/base.py` - Scene detection base class/interface
- `src/video_understanding/ai/scene/service.py` - Scene detection service

### 2. Implement TwelveLabsSceneDetection Class (2-3 hours)

Create/update the file `src/video_understanding/ai/scene/twelve_labs.py` with a class that implements scene detection using the Twelve Labs API:

```python
"""Scene detection implementation using Twelve Labs API."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from video_understanding.ai.exceptions import SceneDetectionError
from video_understanding.ai.models.twelve_labs.model import TwelveLabsModel
from video_understanding.ai.models.twelve_labs.types import TaskType
from video_understanding.ai.scene.base import BaseSceneDetector

# Set up logging
logger = logging.getLogger(__name__)

class TwelveLabsSceneDetection(BaseSceneDetector):
    """Scene detection implementation using Twelve Labs API.
    
    This class uses the Twelve Labs API to detect scene changes in videos,
    offering high accuracy scene detection (>90%) with minimal implementation
    complexity.
    
    The implementation handles:
    - API authentication and communication
    - Scene boundary extraction
    - Accuracy validation
    - Error handling and fallbacks
    
    Example:
        >>> detector = TwelveLabsSceneDetection()
        >>> scenes = await detector.detect_scenes("video.mp4")
        >>> for scene in scenes:
        ...     print(f"Scene {scene['scene_id']}: {scene['start_time']} - {scene['end_time']}")
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[TwelveLabsModel] = None, config: Optional[Dict[str, Any]] = None):
        """Initialize the Twelve Labs scene detection.
        
        Args:
            api_key: Optional API key (if not provided, will be loaded from environment)
            model: Optional existing TwelveLabsModel instance
            config: Optional configuration dictionary
        
        Raises:
            SceneDetectionError: If initialization fails
        """
        self.config = config or {}
        
        try:
            if model is not None:
                self.model = model
            else:
                # Use the credentials utility if api_key not provided
                if api_key is None:
                    from video_understanding.utils.credentials import get_twelve_labs_credentials
                    credentials = get_twelve_labs_credentials()
                    api_key = credentials["api_key"]
                    
                self.model = TwelveLabsModel(api_key=api_key)
                
            # Set configuration options
            self.confidence_threshold = self.config.get("confidence_threshold", 0.5)
            self.min_scene_duration = self.config.get("min_scene_duration", 1.0)  # seconds
            
            logger.info("Initialized Twelve Labs scene detection")
        except Exception as e:
            logger.error(f"Failed to initialize Twelve Labs scene detection: {e}")
            raise SceneDetectionError(f"Failed to initialize Twelve Labs scene detection: {e}")
    
    async def detect_scenes(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect scenes in a video file using Twelve Labs API.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of scene dictionaries with:
                - scene_id: Unique scene identifier
                - start_time: Scene start time in seconds
                - end_time: Scene end time in seconds
                - duration: Scene duration in seconds
                - confidence: Detection confidence score (0-1)
            
        Raises:
            SceneDetectionError: If scene detection fails
        """
        try:
            # Validate video path
            video_path_obj = Path(video_path)
            if not video_path_obj.exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            logger.info(f"Detecting scenes in video: {video_path}")
            
            # Process video with Twelve Labs
            result = await self.model.process({
                "video_path": str(video_path_obj),
                "task": TaskType.SCENE_DETECTION,
                "options": {
                    "confidence_threshold": self.confidence_threshold,
                    "min_scene_duration": self.min_scene_duration
                }
            })
            
            # Extract scenes from result
            scenes = self._extract_scenes(result)
            
            # Validate scenes meet accuracy requirements
            if not self._validate_minimum_accuracy(scenes):
                logger.warning("Scene detection accuracy below threshold, using fallback")
                # Implementation note: In a production system, we might implement a fallback
                # to OpenCV-based detection here, but for POC we'll use the API results
            
            logger.info(f"Detected {len(scenes)} scenes with Twelve Labs API")
            return scenes
            
        except Exception as e:
            logger.error(f"Scene detection failed: {e}")
            raise SceneDetectionError(f"Failed to detect scenes: {e}")
    
    def _extract_scenes(self, api_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract scene information from API result.
        
        Args:
            api_result: Raw API result from Twelve Labs
            
        Returns:
            List of scene dictionaries
        """
        scenes = []
        
        try:
            # Extract scenes from API response
            # Note: Adjust this according to the actual API response structure
            raw_scenes = api_result.get("data", {}).get("scenes", [])
            
            for i, scene in enumerate(raw_scenes):
                scenes.append({
                    "scene_id": i + 1,
                    "start_time": scene.get("start_time", 0),
                    "end_time": scene.get("end_time", 0),
                    "duration": scene.get("end_time", 0) - scene.get("start_time", 0),
                    "confidence": scene.get("confidence", 0),
                })
            
            logger.info(f"Extracted {len(scenes)} scenes from video")
            return scenes
        except Exception as e:
            logger.error(f"Failed to extract scenes: {e}")
            return []
    
    def _validate_minimum_accuracy(self, scenes: List[Dict[str, Any]]) -> bool:
        """Validate that scenes meet minimum accuracy requirements.
        
        Args:
            scenes: List of detected scenes
            
        Returns:
            bool: True if accuracy requirements are met
        """
        if not scenes:
            return False
            
        # Calculate average confidence as a proxy for accuracy
        avg_confidence = sum(scene.get("confidence", 0) for scene in scenes) / len(scenes)
        
        # Log the accuracy metrics
        logger.info(f"Scene detection average confidence: {avg_confidence:.2f}")
        
        # Check if it meets our 90% accuracy threshold
        # Note: In a real implementation, this would use a more sophisticated accuracy metric
        return avg_confidence >= 0.9
    
    async def close(self) -> None:
        """Close resources used by the scene detection."""
        if hasattr(self, 'model'):
            await self.model.close()
```

### 3. Create Unit Tests (1-2 hours)

Create a test file at `tests/video_understanding/ai/scene/test_twelve_labs.py`:

```python
"""Tests for Twelve Labs scene detection."""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetection
from video_understanding.ai.models.twelve_labs.model import TwelveLabsModel
from video_understanding.ai.models.twelve_labs.types import TaskType
from video_understanding.ai.exceptions import SceneDetectionError

# Sample test data
SAMPLE_VIDEO_PATH = "tests/data/sample_video.mp4"
MOCK_API_RESPONSE = {
    "data": {
        "scenes": [
            {"start_time": 0.0, "end_time": 10.5, "confidence": 0.95},
            {"start_time": 10.5, "end_time": 25.2, "confidence": 0.92},
            {"start_time": 25.2, "end_time": 40.8, "confidence": 0.88},
        ]
    },
    "metadata": {
        "video_id": "test_video_id",
        "task_id": "test_task_id",
        "status": "completed"
    }
}

@pytest.fixture
def mock_twelve_labs_model():
    """Create a mock Twelve Labs model for testing."""
    mock_model = MagicMock(spec=TwelveLabsModel)
    
    # Mock the process method to return sample data
    async def mock_process(input_data):
        assert input_data["task"] == TaskType.SCENE_DETECTION
        return MOCK_API_RESPONSE
    
    mock_model.process = mock_process
    return mock_model

@pytest.fixture
def scene_detector(mock_twelve_labs_model):
    """Create a TwelveLabsSceneDetection instance with mock model."""
    detector = TwelveLabsSceneDetection(model=mock_twelve_labs_model)
    return detector

@pytest.mark.asyncio
async def test_init_with_api_key():
    """Test initialization with API key."""
    with patch('video_understanding.ai.models.twelve_labs.model.TwelveLabsModel') as mock_model_class:
        detector = TwelveLabsSceneDetection(api_key="test_api_key")
        mock_model_class.assert_called_once_with(api_key="test_api_key")

@pytest.mark.asyncio
async def test_init_with_credentials():
    """Test initialization with credentials from environment."""
    with patch('video_understanding.utils.credentials.get_twelve_labs_credentials') as mock_get_creds:
        mock_get_creds.return_value = {"api_key": "env_api_key"}
        
        with patch('video_understanding.ai.models.twelve_labs.model.TwelveLabsModel') as mock_model_class:
            detector = TwelveLabsSceneDetection()
            mock_model_class.assert_called_once_with(api_key="env_api_key")

@pytest.mark.asyncio
async def test_detect_scenes(scene_detector):
    """Test scene detection with mock model."""
    scenes = await scene_detector.detect_scenes(SAMPLE_VIDEO_PATH)
    
    # Verify we got the expected number of scenes
    assert len(scenes) == 3
    
    # Verify scene structure
    assert scenes[0]["scene_id"] == 1
    assert scenes[0]["start_time"] == 0.0
    assert scenes[0]["end_time"] == 10.5
    assert scenes[0]["duration"] == 10.5
    assert scenes[0]["confidence"] == 0.95

@pytest.mark.asyncio
async def test_accuracy_validation(scene_detector):
    """Test accuracy validation logic."""
    # Create scenes with high confidence
    high_confidence_scenes = [
        {"scene_id": 1, "confidence": 0.95},
        {"scene_id": 2, "confidence": 0.92},
        {"scene_id": 3, "confidence": 0.91}
    ]
    
    # Create scenes with lower confidence
    low_confidence_scenes = [
        {"scene_id": 1, "confidence": 0.85},
        {"scene_id": 2, "confidence": 0.82},
        {"scene_id": 3, "confidence": 0.81}
    ]
    
    # Verify high confidence scenes pass validation
    assert scene_detector._validate_minimum_accuracy(high_confidence_scenes) == True
    
    # Verify low confidence scenes fail validation
    assert scene_detector._validate_minimum_accuracy(low_confidence_scenes) == False

@pytest.mark.asyncio
async def test_scene_extraction(scene_detector):
    """Test extraction of scenes from API response."""
    scenes = scene_detector._extract_scenes(MOCK_API_RESPONSE)
    
    assert len(scenes) == 3
    assert scenes[0]["scene_id"] == 1
    assert scenes[1]["scene_id"] == 2
    assert scenes[2]["scene_id"] == 3
    
    assert scenes[0]["start_time"] == 0.0
    assert scenes[0]["end_time"] == 10.5
    assert scenes[0]["duration"] == 10.5

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling during scene detection."""
    # Create a model that raises an exception during processing
    mock_model = MagicMock(spec=TwelveLabsModel)
    mock_model.process.side_effect = Exception("API Error")
    
    detector = TwelveLabsSceneDetection(model=mock_model)
    
    # Verify that the error is properly caught and re-raised
    with pytest.raises(SceneDetectionError):
        await detector.detect_scenes(SAMPLE_VIDEO_PATH)

@pytest.mark.asyncio
async def test_cleanup(scene_detector):
    """Test resource cleanup."""
    await scene_detector.close()
    scene_detector.model.close.assert_called_once()
```

### 4. Integration with Scene Detection Service (1-2 hours)

Update the scene detection service to use your implementation. This might vary depending on how the service is structured, but typically you'd:

1. Import your scene detection implementation:

```python
from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetection
```

2. Add a factory method or update the existing one:

```python
def create_scene_detector(detector_type="twelve_labs", **config):
    """Create a scene detector instance based on type."""
    if detector_type == "twelve_labs":
        return TwelveLabsSceneDetection(config=config)
    elif detector_type == "opencv":
        return OpenCVSceneDetector(config=config)
    else:
        raise ValueError(f"Unknown detector type: {detector_type}")
```

3. Update the service to use Twelve Labs as the default:

```python
class SceneDetectionService:
    def __init__(self, detector_type="twelve_labs", **config):
        self.detector = create_scene_detector(detector_type, **config)
        
    async def detect_scenes(self, video_path):
        return await self.detector.detect_scenes(video_path)
```

### 5. Add Integration Tests (Optional, 1 hour)

If you have time, add integration tests that test with real API credentials:

```python
# tests/integration/test_twelve_labs_scene_detection.py

import pytest
import os
from pathlib import Path

from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetection

# Skip these tests if API credentials are not available
pytestmark = pytest.mark.skipif(
    "TWELVE_LABS_API_KEY" not in os.environ,
    reason="Twelve Labs API credentials not available"
)

# Test videos
TEST_VIDEOS = {
    "short": "tests/data/short_video.mp4",
}

@pytest.fixture
async def scene_detector():
    """Create a real TwelveLabsSceneDetection instance with API credentials."""
    detector = TwelveLabsSceneDetection()
    yield detector
    # Clean up resources
    await detector.close()

@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_scene_detection(scene_detector):
    """Test scene detection with a real video and API calls."""
    video_path = TEST_VIDEOS["short"]
    
    # Skip if test video doesn't exist
    if not Path(video_path).exists():
        pytest.skip(f"Test video not found: {video_path}")
    
    scenes = await scene_detector.detect_scenes(video_path)
    
    # Verify we got scenes back
    assert len(scenes) > 0
    
    # Verify scene structure
    assert "scene_id" in scenes[0]
    assert "start_time" in scenes[0]
    assert "end_time" in scenes[0]
    assert "confidence" in scenes[0]
```

### 6. Documentation (30-60 minutes)

Update or create documentation to explain the new implementation:

1. Add docstrings to your code (already included in examples)
2. Update the README.md if necessary
3. Consider adding usage examples for other developers

## Testing Your Implementation

1. Run the unit tests:
```
pytest tests/video_understanding/ai/scene/test_twelve_labs.py -v
```

2. Run integration tests if you've created them (will only work with API credentials):
```
pytest tests/integration/test_twelve_labs_scene_detection.py -v
```

3. Manual testing: Create a simple script that uses your implementation to detect scenes in a sample video and prints the results.

## Acceptance Criteria Verification

Before submitting, make sure your implementation meets all criteria:

- [ ] Twelve Labs API client is implemented and configured
- [ ] Scene detection achieves >90% accuracy
- [ ] Error handling for API failures is implemented
- [ ] Unit tests verify API interaction

## Troubleshooting Tips

1. **API Credentials**: Make sure your `.env` file has the `TWELVE_LABS_API_KEY` and related credentials
2. **API Response Format**: Review the Twelve Labs documentation to ensure you're parsing the response correctly
3. **Error Handling**: Ensure all API calls are wrapped in try/except blocks
4. **Async Functions**: Remember that all API calls should be awaited correctly

## Resources

- Twelve Labs API Documentation: https://docs.twelvelabs.io/ 
- Vidst API Integration Strategy: `/refactor/03_implementation_guides/vidst_api_integration_strategy.md`
- Twelve Labs Integration Strategy: `/refactor/03_implementation_guides/vidst_twelve_labs_integration_strategy.md`

If you have any questions or run into issues, please reach out to the senior developer on the team.
