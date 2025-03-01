# Vidst Refactoring - Enhanced Workflow Commands

## When to apply
@semantics Applies when the user uses specific commands or phrases related to the workflow, such as implementing components, backing up code, or creating tests.
@userMessages ".*let['']s back this up.*" ".*add docstring.*" ".*create test.*" ".*implement this component.*" ".*refactor this.*" ".*implement API integration.*" ".*create documentation.*" ".*validate against requirements.*"

## Workflow Command Responses

This rule enhances the existing workflow commands with additional refactoring-specific commands for the Vidst project.

## Backup Commands

### "Let's back this up"

When the user says "let's back this up" or similar, create a backup of the current code in the `refactor/07_backup/` directory with appropriate naming.

Example implementation:

```python
def backup_file(file_path):
    """Create a backup of the specified file in the backup directory.
    
    Args:
        file_path: Path to the file to back up
        
    Returns:
        Path to the backup file
    """
    import os
    import shutil
    from datetime import datetime
    
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get filename
    filename = os.path.basename(file_path)
    base_name, ext = os.path.splitext(filename)
    
    # Create backup filename with timestamp
    backup_filename = f"{base_name}_{timestamp}{ext}.bak"
    
    # Create backup directory if it doesn't exist
    backup_dir = "refactor/07_backup/"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create backup path
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Copy the file
    shutil.copy2(file_path, backup_path)
    
    return backup_path
```

## API Integration Commands

### "Implement API integration for [component]"

When the user asks to implement API integration for a specific component, generate the appropriate API integration code following the Vidst architecture:

For Twelve Labs integration:

```python
from video_understanding.ai.scene.base import BaseSceneDetector
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import aiohttp
import asyncio
import logging

class TwelveLabsConfig(BaseModel):
    """Configuration for Twelve Labs API."""
    api_key: str
    api_url: str = "https://api.twelvelabs.io/v1"
    timeout: float = Field(default=30.0, ge=1.0, le=120.0)
    retries: int = Field(default=3, ge=0, le=10)

class TwelveLabsSceneDetector(BaseSceneDetector):
    """Scene detection implementation using Twelve Labs API."""
    
    def __init__(self, config: TwelveLabsConfig):
        """Initialize Twelve Labs scene detector.
        
        Args:
            config: Twelve Labs configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    async def _call_api(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Call Twelve Labs API with error handling and retry logic.
        
        Args:
            endpoint: API endpoint
            method: HTTP method (GET, POST, etc.)
            data: Request data
            
        Returns:
            API response
            
        Raises:
            APIError: If API call fails
        """
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.config.api_url}/{endpoint}"
        
        for attempt in range(self.config.retries + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=data,
                        timeout=self.config.timeout
                    ) as response:
                        if response.status < 400:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            raise APIError(f"API error: {response.status} - {error_text}")
            except Exception as e:
                self.logger.warning(f"API call failed (attempt {attempt + 1}/{self.config.retries + 1}): {str(e)}")
                if attempt < self.config.retries:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise APIError(f"API call failed after {self.config.retries + 1} attempts: {str(e)}")
    
    async def detect_scenes(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect scenes in a video using Twelve Labs API.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of detected scenes with timestamps and metadata
            
        Raises:
            SceneDetectionError: If scene detection fails
        """
        try:
            # Step 1: Upload video for analysis
            # Implementation details for Twelve Labs API
            
            # Step 2: Poll for results
            # Implementation details for Twelve Labs API
            
            # Step 3: Process and return results
            # Implementation details for Twelve Labs API
            
            return scenes
        except Exception as e:
            raise SceneDetectionError(f"Twelve Labs scene detection failed: {str(e)}")
```

For Pinecone integration:

```python
from video_understanding.storage.vector.base import BaseVectorStorage
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import pinecone
import numpy as np
import logging

class PineconeConfig(BaseModel):
    """Configuration for Pinecone vector database."""
    api_key: str
    environment: str
    index_name: str
    namespace: Optional[str] = None
    dimension: int = 1536
    metric: str = "cosine"
    
class PineconeVectorStorage(BaseVectorStorage):
    """Vector storage implementation using Pinecone."""
    
    def __init__(self, config: PineconeConfig):
        """Initialize Pinecone vector storage.
        
        Args:
            config: Pinecone configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._initialize()
        
    def _initialize(self):
        """Initialize Pinecone client and index."""
        try:
            pinecone.init(
                api_key=self.config.api_key,
                environment=self.config.environment
            )
            
            # Check if index exists
            if self.config.index_name not in pinecone.list_indexes():
                # Create index if it doesn't exist
                pinecone.create_index(
                    name=self.config.index_name,
                    dimension=self.config.dimension,
                    metric=self.config.metric
                )
                
            self.index = pinecone.Index(self.config.index_name)
            self.logger.info(f"Initialized Pinecone index: {self.config.index_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise VectorStorageError(f"Pinecone initialization failed: {str(e)}")
    
    async def add_vectors(self, vectors: List[np.ndarray], ids: List[str], metadata: Optional[List[Dict]] = None) -> bool:
        """Add vectors to Pinecone.
        
        Args:
            vectors: List of vectors to add
            ids: List of IDs for the vectors
            metadata: Optional metadata for each vector
            
        Returns:
            True if successful
            
        Raises:
            VectorStorageError: If operation fails
        """
        try:
            # Implementation for Pinecone upsert
            return True
        except Exception as e:
            raise VectorStorageError(f"Pinecone add_vectors failed: {str(e)}")
```

## Component Replacement Commands

### "Replace component [component]"

When asked to replace a component with API alternative, follow the architecture transition plan:

1. Implement the API client
2. Update the factory to support both implementations
3. Add configuration for the API
4. Implement tests for the new implementation
5. Update documentation

Example response:

```
I'll help you replace the Vector Storage component with Pinecone API as per the component evaluation matrix. Here's the implementation plan:

1. First, let's create the Pinecone implementation
2. Then, update the factory to support both FAISS and Pinecone
3. Add Pinecone configuration
4. Implement tests for Pinecone
5. Update documentation

Let's start with the Pinecone implementation:
```

## Component Creation Commands

### "Create component [component]"

When asked to create a new component, follow the component structure:

1. Create the base interface
2. Implement concrete class
3. Add to factory
4. Create tests
5. Add documentation

Example:

```python
# Base interface
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseVectorStorage(ABC):
    """Base interface for vector storage implementations."""
    
    @abstractmethod
    async def add_vectors(self, vectors, ids, metadata=None):
        """Add vectors to storage."""
        pass
    
    @abstractmethod
    async def search_vectors(self, query_vector, limit=10):
        """Search for similar vectors."""
        pass
    
    @abstractmethod
    async def delete_vectors(self, ids):
        """Delete vectors by ID."""
        pass
    
    @abstractmethod
    async def get_vector(self, id):
        """Get vector by ID."""
        pass
    
    @abstractmethod
    async def clear(self):
        """Clear all vectors."""
        pass
```

## Testing-related Commands

### "Create test for API component"

When asked to create tests for API components, generate tests with mocked API responses:

```python
import pytest
import responses
from unittest.mock import patch, MagicMock
from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetector, TwelveLabsConfig

class TestTwelveLabsSceneDetector:
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return TwelveLabsConfig(
            api_key="test_key",
            api_url="https://api.example.com"
        )
    
    @pytest.fixture
    def detector(self, config):
        """Create test detector."""
        return TwelveLabsSceneDetector(config)
    
    @responses.activate
    async def test_detect_scenes(self, detector):
        """Test scene detection."""
        # Mock API responses
        responses.add(
            responses.POST,
            "https://api.example.com/analyze",
            json={"task_id": "test_task"},
            status=200
        )
        
        responses.add(
            responses.GET,
            "https://api.example.com/tasks/test_task",
            json={"status": "completed", "data": {"scenes": [{"start": 0, "end": 10}]}},
            status=200
        )
        
        # Call method
        result = await detector.detect_scenes("test_video.mp4")
        
        # Assertions
        assert len(result) == 1
        assert result[0]["start"] == 0
        assert result[0]["end"] == 10
```

## Validation Commands

### "Validate against requirements"

When asked to validate a component against requirements, use the Component Evaluation Matrix as reference:

Example:

```
I'll validate the Scene Detection implementation against the requirements from the Component Evaluation Matrix:

Requirements for Scene Detection:
- 94.2% accuracy target (vs. 90% requirement)
- API Alternative: Twelve Labs Marengo/Pegasus
- POC Importance: 5/5
- Implementation Status: 3/5
- Complexity Burden: 4/5
- API Viability: 5/5
- Accuracy Requirements: 4/5

Validation Results:
1. Accuracy: The implementation achieves X% accuracy (target: 94.2%)
2. Integration: The implementation correctly integrates with Twelve Labs API
3. Error Handling: The implementation includes proper error handling and retries
4. Tests: Test coverage is complete with mocked API responses
5. Documentation: Docstrings and API documentation are complete

Areas for Improvement:
1. [List any gaps identified]
2. [Suggestions for improvements]
```

## Documentation Commands

### "Create API documentation for [component]"

When asked to create API documentation, generate markdown documentation:

```markdown
# Twelve Labs Scene Detection API

## Overview

The Twelve Labs Scene Detection API provides high-accuracy scene boundary detection for video content. This integration allows for automatic identification of scene changes in video files.

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | str | Required | Twelve Labs API key |
| `api_url` | str | "https://api.twelvelabs.io/v1" | API endpoint URL |
| `timeout` | float | 30.0 | API request timeout in seconds |
| `retries` | int | 3 | Number of retry attempts |

## Usage

```python
from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetector, TwelveLabsConfig

# Initialize configuration
config = TwelveLabsConfig(api_key="your_api_key")

# Create detector
detector = TwelveLabsSceneDetector(config)

# Detect scenes
scenes = await detector.detect_scenes("video.mp4")

# Process scenes
for scene in scenes:
    print(f"Scene: {scene['start']} - {scene['end']}")
```

## Response Format

The API returns scene boundaries with the following structure:

```json
[
  {
    "start": 0.0,
    "end": 10.5,
    "confidence": 0.95,
    "metadata": {
      "scene_type": "dialog"
    }
  },
  {
    "start": 10.5,
    "end": 15.2,
    "confidence": 0.92,
    "metadata": {
      "scene_type": "transition"
    }
  }
]
```

## Error Handling

The implementation includes comprehensive error handling with retry logic for API calls. Errors are categorized as:

1. `APIError`: For issues with the API communication
2. `SceneDetectionError`: For errors in the scene detection process

## Performance Considerations

- API calls are asynchronous for better performance
- Batch processing is supported for multiple videos
- Circuit breaker pattern prevents cascading failures
```