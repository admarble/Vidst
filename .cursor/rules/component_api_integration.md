# Vidst Refactoring - API Integration Patterns

## When to apply
@semantics Applies when implementing API integrations for components, especially when replacing local implementations with external APIs.
@files src/video_understanding/**/api/**/*.py src/video_understanding/ai/**/*.py
@userMessages ".*API integration.*" ".*implement API.*" ".*external API.*" ".*twelve labs.*" ".*pinecone.*" ".*document ai.*"

## API Integration Guidelines

This rule provides patterns for implementing external API integrations based on the Component Evaluation Matrix priorities.

## API Configuration Pattern

```python
from pydantic import BaseModel, Field
from typing import Optional

class APIConfig(BaseModel):
    """Configuration for API integration."""
    api_key: str
    api_url: str
    timeout: float = Field(default=30.0, ge=1.0, le=120.0)
    retries: int = Field(default=3, ge=0, le=10)
```

## API Client Pattern

```python
import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional

class APIClient:
    """Base client for API integrations."""
    
    def __init__(self, config: APIConfig):
        """Initialize API client."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    async def call_api(self, endpoint: str, method: str = "GET", 
                      data: Optional[Dict] = None) -> Dict[str, Any]:
        """Call API with retry logic.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
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
        
        # Implement retry logic with exponential backoff
        for attempt in range(self.config.retries + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method=method,
                        url=url,
                        json=data,
                        headers=headers,
                        timeout=self.config.timeout
                    ) as response:
                        if response.status < 400:
                            return await response.json()
                        else:
                            # Handle error response
                            error_text = await response.text()
                            raise APIError(f"API error: {response.status} - {error_text}")
            except Exception as e:
                # Log error and retry if attempts remain
                if attempt < self.config.retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise APIError(f"API call failed: {str(e)}")
```

## API Error Handling

```python
class APIError(Exception):
    """Base error for API integrations."""
    pass

class APIRequestError(APIError):
    """Error for API request issues."""
    pass

class APIResponseError(APIError):
    """Error for API response issues."""
    pass
```

## Example: Twelve Labs Integration

```python
from video_understanding.ai.scene.base import BaseSceneDetector
from pydantic import BaseModel
from typing import List, Dict, Any

class TwelveLabsConfig(BaseModel):
    """Configuration for Twelve Labs API."""
    api_key: str
    api_url: str = "https://api.twelvelabs.io/v1"
    timeout: float = 30.0
    retries: int = 3

class TwelveLabsSceneDetector(BaseSceneDetector):
    """Scene detection using Twelve Labs API."""
    
    def __init__(self, config: TwelveLabsConfig):
        """Initialize with Twelve Labs configuration."""
        self.config = config
        self.client = APIClient(config)
        self.logger = logging.getLogger(__name__)
    
    async def detect_scenes(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect scenes using Twelve Labs API.
        
        Implements scene detection using their Marengo/Pegasus API.
        """
        try:
            # Upload video or get video ID
            # Call API to analyze
            # Process response
            # Return scene data
            
            return scenes
        except Exception as e:
            self.logger.error(f"Scene detection failed: {str(e)}")
            raise SceneDetectionError(f"Twelve Labs scene detection failed: {str(e)}")
```

## Example: Pinecone Integration

```python
from video_understanding.storage.vector.base import BaseVectorStorage
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import numpy as np

class PineconeConfig(BaseModel):
    """Configuration for Pinecone API."""
    api_key: str
    environment: str
    index_name: str
    namespace: Optional[str] = None
    dimension: int = 1536

class PineconeVectorStorage(BaseVectorStorage):
    """Vector storage using Pinecone API."""
    
    def __init__(self, config: PineconeConfig):
        """Initialize with Pinecone configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._initialize()
    
    async def add_vectors(self, vectors: List[np.ndarray], 
                         ids: List[str], 
                         metadata: Optional[List[Dict]] = None) -> bool:
        """Add vectors to Pinecone."""
        try:
            # Prepare vectors for upsert
            # Call Pinecone API
            # Return success
            return True
        except Exception as e:
            self.logger.error(f"Failed to add vectors: {str(e)}")
            raise VectorStorageError(f"Pinecone add_vectors failed: {str(e)}")
```

## Circuit Breaker Pattern

For resilient API calls:

```python
class CircuitBreaker:
    """Circuit breaker for API resilience."""
    
    def __init__(self, failure_threshold=5, reset_timeout=60):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Failures before opening circuit
            reset_timeout: Seconds before resetting circuit
        """
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.is_open = False
        self.last_failure_time = 0
    
    async def execute(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        # Check if circuit is open
        # If closed, try to execute function
        # Track failures and open circuit if threshold exceeded
```

## API Integration Checklist

When implementing API integrations:

1. ✓ Use Pydantic models for configuration
2. ✓ Implement proper error handling
3. ✓ Add retry logic with exponential backoff
4. ✓ Use circuit breaker for resilience
5. ✓ Log API calls and errors appropriately
6. ✓ Handle rate limiting
7. ✓ Secure API keys through environment variables
