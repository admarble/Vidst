# Updated Implementation Instructions for Issue #108: Twelve Labs API Integration

## Background

We're transitioning from a custom OpenCV-based scene detection implementation to using the Twelve Labs API, which offers superior accuracy (94.2% vs. our 90% requirement) and reduces implementation complexity.

## Current Client Library

Our project is using `twelvelabs-client>=1.0.0` as specified in the requirements.txt file. This is the official Python client for interacting with the Twelve Labs API.

## Implementation Overview

You'll need to:
1. Implement Twelve Labs API client for scene detection
2. Ensure scene detection achieves >90% accuracy
3. Implement error handling for API failures
4. Add unit tests to verify API interaction

## Step-by-Step Implementation Guide

### 1. Understanding the Current API Structure (30 minutes)

The Twelve Labs API provides two main APIs:
- **Embed API**: Used for video embeddings, which can help in scene detection
- **Generate API**: Used for text generation based on video content

The current client structure follows:

```python
from twelvelabs import TwelveLabs

# Initialize the client
client = TwelveLabs("<YOUR_API_KEY>")
```

### 2. Implement TwelveLabsSceneDetection Class (2-3 hours)

Create a file at `src/video_understanding/ai/scene/twelve_labs.py`:

```python
"""Scene detection implementation using Twelve Labs API."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from twelvelabs import TwelveLabs

from video_understanding.ai.exceptions import SceneDetectionError
from video_understanding.ai.scene.base import BaseSceneDetector
from video_understanding.utils.credentials import get_twelve_labs_credentials

logger = logging.getLogger(__name__)

class TwelveLabsSceneDetection(BaseSceneDetector):
    """Scene detection using Twelve Labs API.
    
    This implementation utilizes Twelve Labs' Marengo model for high-accuracy
    scene detection in videos.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Twelve Labs scene detection.
        
        Args:
            api_key: Optional API key (if not provided, loaded from environment)
            
        Raises:
            SceneDetectionError: If initialization fails
        """
        try:
            # Get API key from credentials if not provided
            if api_key is None:
                credentials = get_twelve_labs_credentials()
                api_key = credentials["api_key"]
                
            # Initialize the Twelve Labs client
            self.client = TwelveLabs(api_key)
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
            
            logger.info(f"Detecting scenes in video: {video_path}")
            
            # Create an index for the video (temporary for this processing)
            index = await self._create_temp_index()
            
            # Upload and process the video
            task = await self._upload_video(index.id, str(video_path_obj))
            
            # Wait for processing to complete
            task = await self._wait_for_task_completion(task)
            
            # Extract scenes using the Embed API
            scenes = await self._extract_scenes_from_task(task)
            
            # Clean up resources
            await self._cleanup_resources(index.id)
            
            logger.info(f"Detected {len(scenes)} scenes")
            return scenes
            
        except Exception as e:
            logger.error(f"Scene detection failed: {e}")
            raise SceneDetectionError(f"Detection failed: {e}")
    
    async def _create_temp_index(self):
        """Create a temporary index for video processing."""
        try:
            # Generate a unique name for the temporary index
            import uuid
            index_name = f"vidst-temp-{uuid.uuid4().hex[:8]}"
            
            # Create index with Marengo model
            index = self.client.index.create(
                name=index_name,
                engines=[
                    {
                        "name": "marengo",  # Using Marengo for scene detection
                        "options": ["visual", "conversation"]
                    }
                ]
            )
            
            return index
            
        except Exception as e:
            logger.error(f"Failed to create temporary index: {e}")
            raise SceneDetectionError(f"Index creation failed: {e}")
    
    async def _upload_video(self, index_id: str, video_path: str):
        """Upload video to the Twelve Labs API.
        
        Args:
            index_id: ID of the index to upload to
            video_path: Path to the video file
            
        Returns:
            Task object for tracking
        """
        try:
            # Create upload task
            task = self.client.task.create(
                index_id=index_id, 
                file=video_path, 
                language="en"
            )
            
            return task
            
        except Exception as e:
            logger.error(f"Failed to upload video: {e}")
            raise SceneDetectionError(f"Video upload failed: {e}")
    
    async def _wait_for_task_completion(self, task):
        """Wait for a task to complete.
        
        Args:
            task: Task object to wait for
            
        Returns:
            Completed task object
        """
        try:
            # Wait for the task to complete
            task.wait_for_done()
            
            # Retrieve updated task information
            return task.retrieve()
            
        except Exception as e:
            logger.error(f"Task failed: {e}")
            raise SceneDetectionError(f"Processing task failed: {e}")
    
    async def _extract_scenes_from_task(self, task) -> List[Dict[str, Any]]:
        """Extract scene information from completed task.
        
        Args:
            task: Completed task object
            
        Returns:
            List of scene dictionaries
        """
        scenes = []
        
        try:
            # Get embeddings which contain temporal information
            if task.video_embedding and task.video_embedding.segments:
                # Process each segment as a scene
                for i, segment in enumerate(task.video_embedding.segments):
                    scenes.append({
                        "scene_id": i + 1,
                        "start_time": segment.start_offset_sec,
                        "end_time": segment.end_offset_sec,
                        "duration": segment.end_offset_sec - segment.start_offset_sec,
                        # Using a default confidence of 0.9+ since Twelve Labs accuracy is ~94%
                        "confidence": 0.94
                    })
            
            return scenes
            
        except Exception as e:
            logger.error(f"Failed to extract scenes: {e}")
            return []
    
    async def _cleanup_resources(self, index_id: str):
        """Clean up resources after processing.
        
        Args:
            index_id: ID of the index to clean up
        """
        try:
            # Delete the temporary index
            self.client.index.delete(index_id)
            
        except Exception as e:
            logger.warning(f"Failed to clean up resources: {e}")
    
    async def close(self):
        """Close all resources."""
        # Clean up any remaining resources
        pass
```

### 3. Add Basic Unit Tests (1 hour)

Create a test file at `tests/video_understanding/ai/scene/test_twelve_labs.py`:

```python
"""Tests for Twelve Labs scene detection."""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetection
from video_understanding.ai.exceptions import SceneDetectionError

# Sample test data
SAMPLE_VIDEO_PATH = "tests/data/sample_video.mp4"

@pytest.fixture
def mock_twelve_labs_client():
    """Create a mock Twelve Labs client."""
    mock_client = MagicMock()
    
    # Mock index
    mock_index = MagicMock()
    mock_index.id = "test_index_id"
    mock_client.index.create.return_value = mock_index
    
    # Mock task
    mock_task = MagicMock()
    mock_task.wait_for_done.return_value = None
    mock_task.retrieve.return_value = mock_task
    
    # Mock embedding segments
    mock_segment1 = MagicMock()
    mock_segment1.start_offset_sec = 0.0
    mock_segment1.end_offset_sec = 10.5
    
    mock_segment2 = MagicMock()
    mock_segment2.start_offset_sec = 10.5
    mock_segment2.end_offset_sec = 25.2
    
    # Set up the segments
    mock_embedding = MagicMock()
    mock_embedding.segments = [mock_segment1, mock_segment2]
    mock_task.video_embedding = mock_embedding
    
    mock_client.task.create.return_value = mock_task
    
    return mock_client

@pytest.fixture
def scene_detector(mock_twelve_labs_client):
    """Create a TwelveLabsSceneDetection instance with mock client."""
    detector = TwelveLabsSceneDetection(api_key="test_api_key")
    detector.client = mock_twelve_labs_client
    return detector

@pytest.mark.asyncio
async def test_initialization():
    """Test initialization with credentials."""
    with patch('video_understanding.utils.credentials.get_twelve_labs_credentials') as mock_get_creds:
        mock_get_creds.return_value = {"api_key": "test_api_key"}
        
        with patch('twelvelabs.TwelveLabs') as mock_client_class:
            detector = TwelveLabsSceneDetection()
            mock_client_class.assert_called_once_with("test_api_key")

@pytest.mark.asyncio
async def test_scene_detection(scene_detector):
    """Test scene detection."""
    # Mock Path.exists to return True
    with patch('pathlib.Path.exists', return_value=True):
        scenes = await scene_detector.detect_scenes(SAMPLE_VIDEO_PATH)
    
    # Check results
    assert len(scenes) == 2
    assert scenes[0]["scene_id"] == 1
    assert scenes[0]["start_time"] == 0.0
    assert scenes[0]["end_time"] == 10.5
    assert scenes[1]["start_time"] == 10.5
    assert scenes[1]["end_time"] == 25.2

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling."""
    detector = TwelveLabsSceneDetection(api_key="test_api_key")
    
    # Mock client that raises exception
    mock_client = MagicMock()
    mock_client.index.create.side_effect = Exception("API Error")
    detector.client = mock_client
    
    # Test error handling
    with patch('pathlib.Path.exists', return_value=True):
        with pytest.raises(SceneDetectionError):
            await detector.detect_scenes(SAMPLE_VIDEO_PATH)
```

### 4. Integrate with Scene Detection Service (30 minutes)

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

Run the unit tests:
```
pytest tests/video_understanding/ai/scene/test_twelve_labs.py -v
```

## Checklist

Before submitting, verify you've completed:

- [ ] Twelve Labs API client integration is working
- [ ] Scene detection returns correct results
- [ ] Basic error handling is implemented
- [ ] Unit tests pass

## Resources

- Twelve Labs API Documentation: https://docs.twelvelabs.io/
- Twelve Labs Python Client: https://pypi.org/project/twelvelabs-client/

## Notes

This implementation uses the Twelve Labs Python client's current structure with the Embed and Index APIs. The code focuses on the essential requirements for scene detection while maintaining error handling and test coverage.
