# Vidst Refactoring - API Integration Rules

## When to apply
@semantics Applies to API integration related tasks, especially when working with Twelve Labs, Pinecone, Document AI, or any external API service.
@files src/video_understanding/ai/**/*.py src/video_understanding/storage/vector/*.py

## API Integration Strategy

This rule provides guidance for implementing API integrations for the Vidst refactoring project, focusing on best practices, error handling, and resilience patterns.

## General API Guidelines

1. **Abstraction Layers**
   - Create base interfaces for each API service type
   - Implement concrete providers for each service
   - Use factories for dynamic provider selection
   - Enable fallback mechanisms where possible

2. **Error Handling**
   - Implement retry logic with exponential backoff
   - Use circuit breakers for API calls
   - Create specific exception classes
   - Log detailed error information

3. **Configuration**
   - Store API keys in environment variables
   - Use Pydantic for configuration validation
   - Support dynamic configuration changes
   - Create separate configuration classes per service

4. **Testing**
   - Mock all API calls in unit tests
   - Create integration test fixtures
   - Add dedicated API test modules
   - Test resilience mechanisms

## Twelve Labs Integration

### Configuration

```python
from pydantic import BaseModel, Field

class TwelveLabsConfig(BaseModel):
    """Configuration for Twelve Labs API."""
    api_key: str
    api_url: str = "https://api.twelvelabs.io/v1"
    timeout: float = Field(default=30.0, ge=1.0, le=120.0)
    retries: int = Field(default=3, ge=0, le=10)
```

### Implementation

```python
from video_understanding.ai.scene.base import BaseSceneDetector

class TwelveLabsSceneDetector(BaseSceneDetector):
    """Twelve Labs implementation for scene detection."""
    
    def __init__(self, config: TwelveLabsConfig):
        """Initialize the Twelve Labs scene detector.
        
        Args:
            config: Twelve Labs configuration
        """
        self.config = config
        self.client = self._initialize_client()
        
    def _initialize_client(self):
        """Initialize the Twelve Labs client."""
        import twelvelabs
        return twelvelabs.Client(api_key=self.config.api_key)
        
    async def detect_scenes(self, video_path: str) -> list:
        """Detect scenes using Twelve Labs API.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of detected scenes
            
        Raises:
            SceneDetectionError: If scene detection fails
        """
        try:
            # Implementation details for Twelve Labs API
            pass
        except Exception as e:
            raise SceneDetectionError(f"Twelve Labs API error: {str(e)}")
```

## Pinecone Integration

### Configuration

```python
from pydantic import BaseModel, Field
from typing import Optional

class PineconeConfig(BaseModel):
    """Configuration for Pinecone vector database."""
    api_key: str
    environment: str
    index_name: str
    namespace: Optional[str] = None
    dimension: int = 1536
    metric: str = "cosine"
    timeout: float = Field(default=30.0, ge=1.0, le=120.0)
```

### Implementation

```python
from video_understanding.storage.vector.base import BaseVectorStorage
import pinecone

class PineconeVectorStorage(BaseVectorStorage):
    """Pinecone implementation for vector storage."""
    
    def __init__(self, config: PineconeConfig):
        """Initialize Pinecone vector storage.
        
        Args:
            config: Pinecone configuration
        """
        self.config = config
        self._initialize()
        
    def _initialize(self):
        """Initialize Pinecone client and index."""
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
        
    def add_vectors(self, vectors, ids, metadata=None):
        """Add vectors to Pinecone."""
        try:
            # Prepare items for upsert
            items = []
            for i, (vector, id_) in enumerate(zip(vectors, ids)):
                item = (id_, vector.tolist())
                if metadata:
                    item += (metadata[i],)
                items.append(item)
                
            # Upsert in batches of 100
            batch_size = 100
            for i in range(0, len(items), batch_size):
                batch = items[i:i+batch_size]
                self.index.upsert(
                    vectors=batch,
                    namespace=self.config.namespace
                )
                
            return True
        except Exception as e:
            raise VectorStorageError(f"Pinecone upsert error: {str(e)}")
```

## Document AI Integration

### Configuration

```python
from pydantic import BaseModel

class DocumentAIConfig(BaseModel):
    """Configuration for Google Document AI."""
    project_id: str
    location: str = "us-central1"
    processor_id: str
    timeout: float = 30.0
```

### Implementation

```python
from google.cloud import documentai
from video_understanding.ai.ocr.base import BaseOCRService

class DocumentAIService(BaseOCRService):
    """Google Document AI implementation for OCR."""
    
    def __init__(self, config: DocumentAIConfig):
        """Initialize the Document AI service.
        
        Args:
            config: Document AI configuration
        """
        self.config = config
        self.client = documentai.DocumentProcessorServiceClient()
        self.processor_name = f"projects/{config.project_id}/locations/{config.location}/processors/{config.processor_id}"
        
    async def extract_text(self, image):
        """Extract text from an image using Document AI."""
        try:
            # Convert image to bytes
            if isinstance(image, (str, Path)):
                with open(image, "rb") as f:
                    content = f.read()
            elif isinstance(image, np.ndarray):
                is_success, buffer = cv2.imencode(".jpg", image)
                if not is_success:
                    raise OCRError("Failed to encode image")
                content = buffer.tobytes()
            else:
                raise ValueError(f"Unsupported image type: {type(image)}")
                
            # Create and process document
            raw_document = documentai.RawDocument(
                content=content,
                mime_type="image/jpeg"
            )
            
            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=raw_document
            )
            
            response = self.client.process_document(request)
            document = response.document
            
            # Process and return results
            # ...
            
        except Exception as e:
            raise OCRError(f"Document AI error: {str(e)}")
```

## Resilience Patterns

### Retry Pattern

```python
import backoff
from typing import Callable, Any

def retry_with_backoff(max_tries=3, backoff_factor=1.5):
    """Decorator for API calls with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @backoff.on_exception(
            backoff.expo,
            (ConnectionError, TimeoutError),
            max_tries=max_tries,
            factor=backoff_factor
        )
        async def wrapper(*args, **kwargs) -> Any:
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@retry_with_backoff(max_tries=5)
async def call_external_api(client, request):
    return await client.execute(request)
```

### Circuit Breaker Implementation

```python
import time
import asyncio
from typing import Callable, Any

class CircuitBreakerOpenError(Exception):
    """Error raised when circuit breaker is open."""
    pass

class CircuitBreaker:
    """Circuit breaker for API resilience."""
    
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.is_open = False
        self.last_failure_time = 0
        
    async def execute(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.is_open:
            current_time = time.time()
            if current_time - self.last_failure_time >= self.reset_timeout:
                # Try to reset circuit
                self.is_open = False
                self.failure_count = 0
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker open. Try again in {self.reset_timeout - (current_time - self.last_failure_time):.2f}s"
                )
                
        try:
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
                
            # Successful call, reset failure count
            self.failure_count = 0
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.is_open = True
                
            # Re-raise the original exception
            raise
```

## Service with Fallback

```python
class ServiceWithFallback:
    """Base class for services with fallback capability."""
    
    def __init__(self, primary_service, fallback_service=None):
        self.primary = primary_service
        self.fallback = fallback_service
        self.circuit_breaker = CircuitBreaker()
        
    async def execute(self, method_name, *args, **kwargs):
        """Execute method with fallback capability."""
        try:
            # Get method from primary service
            method = getattr(self.primary, method_name)
            # Execute with circuit breaker
            return await self.circuit_breaker.execute(method, *args, **kwargs)
        except Exception as e:
            if self.fallback:
                # Try fallback service
                fallback_method = getattr(self.fallback, method_name)
                return await fallback_method(*args, **kwargs)
            # Re-raise if no fallback available
            raise
```

## API Integration Testing

```python
import pytest
import responses
from unittest.mock import patch

class TestTwelveLabsAPI:
    @pytest.fixture
    def api_client(self):
        config = TwelveLabsConfig(api_key="test_key")
        return TwelveLabsSceneDetector(config)
        
    @responses.activate
    def test_scene_detection(self, api_client):
        # Mock API response
        responses.add(
            responses.POST,
            "https://api.twelvelabs.io/v1/analyze",
            json={"task_id": "test_task_id", "status": "processing"},
            status=200
        )
        
        responses.add(
            responses.GET,
            "https://api.twelvelabs.io/v1/tasks/test_task_id",
            json={"status": "completed", "result": {"scenes": []}},
            status=200
        )
        
        # Test API call
        result = await api_client.detect_scenes("test_video.mp4")
        assert result is not None
```
