# Vidst Refactoring - Component Implementation Rules

## When to apply
@semantics Applies when implementing or refactoring components, especially those listed in the Component Evaluation Matrix.
@files src/video_understanding/**/*.py
@userMessages ".*implement.*component.*" ".*refactor.*component.*" ".*replace.*component.*" ".*API.*integration.*"

## Component Implementation Guidelines

This rule provides guidance for implementing components based on the Vidst Component Evaluation Matrix and architecture standards.

## Component Architecture

All components in Vidst should follow this architecture:

1. **Base Interface**: Abstract base class defining the component interface
2. **Concrete Implementations**: Classes implementing the base interface
3. **Factory**: Factory class for creating component instances
4. **Configuration**: Pydantic models for component configuration
5. **Exceptions**: Custom exception classes

## Implementation Patterns

### Base Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseComponent(ABC):
    """Base interface for component implementation."""
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Processed results
            
        Raises:
            ComponentError: If processing fails
        """
        pass
```

### Concrete Implementation

```python
from video_understanding.component.base import BaseComponent
from video_understanding.exceptions import ComponentError
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

class ComponentConfig(BaseModel):
    """Configuration for component."""
    param1: str
    param2: int = 42
    param3: Optional[str] = None

class ConcreteComponent(BaseComponent):
    """Concrete implementation of component."""
    
    def __init__(self, config: ComponentConfig):
        """Initialize component.
        
        Args:
            config: Component configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Processed results
            
        Raises:
            ComponentError: If processing fails
        """
        try:
            # Implementation details
            return {
                "status": "success",
                "results": {}
            }
        except Exception as e:
            self.logger.error(f"Processing failed: {str(e)}")
            raise ComponentError(f"Processing failed: {str(e)}")
```

### Factory Pattern

```python
from typing import Dict, Any, Type
from video_understanding.component.base import BaseComponent
from video_understanding.component.concrete import ConcreteComponent, ComponentConfig
from video_understanding.component.api import APIComponent, APIConfig

class ComponentFactory:
    """Factory for creating component instances."""
    
    _registry = {
        "concrete": ConcreteComponent,
        "api": APIComponent
    }
    
    @classmethod
    def register(cls, name: str, component_class: Type[BaseComponent]) -> None:
        """Register a component class.
        
        Args:
            name: Component name
            component_class: Component class
        """
        cls._registry[name] = component_class
    
    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> BaseComponent:
        """Create a component instance.
        
        Args:
            name: Component name
            config: Component configuration
            
        Returns:
            Component instance
            
        Raises:
            ValueError: If component is not registered
        """
        if name not in cls._registry:
            raise ValueError(f"Component not registered: {name}")
            
        component_class = cls._registry[name]
        
        # Convert dict config to appropriate config class
        if name == "concrete":
            config_obj = ComponentConfig(**config)
        elif name == "api":
            config_obj = APIConfig(**config)
        else:
            config_obj = config
            
        return component_class(config_obj)
```

## API Integration Patterns

For API integrations, follow these patterns:

### API Configuration

```python
from pydantic import BaseModel, Field
from typing import Optional

class APIConfig(BaseModel):
    """Configuration for API integration."""
    api_key: str
    api_url: str
    timeout: float = Field(default=30.0, ge=1.0, le=120.0)
    retries: int = Field(default=3, ge=0, le=10)
    proxy: Optional[str] = None
```

### API Error Handling

```python
class APIError(Exception):
    """Base error for API integrations."""
    pass

class APIRequestError(APIError):
    """Error for API request issues."""
    
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API request failed: {status_code} - {message}")

class APIResponseError(APIError):
    """Error for API response issues."""
    
    def __init__(self, message: str, response_data: Dict[str, Any] = None):
        self.message = message
        self.response_data = response_data or {}
        super().__init__(f"API response error: {message}")
```

### API Client Pattern

```python
import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional

class APIClient:
    """Base client for API integrations."""
    
    def __init__(self, config: APIConfig):
        """Initialize API client.
        
        Args:
            config: API configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    async def _call_api(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        """Call API with retry logic.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            data: Request data
            headers: Request headers
            
        Returns:
            API response
            
        Raises:
            APIRequestError: If request fails
            APIResponseError: If response is invalid
        """
        default_headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        # Merge headers
        merged_headers = {**default_headers, **(headers or {})}
        
        # Construct URL
        url = f"{self.config.api_url}/{endpoint.lstrip('/')}"
        
        # Retry logic
        for attempt in range(self.config.retries + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method=method,
                        url=url,
                        json=data,
                        headers=merged_headers,
                        timeout=self.config.timeout,
                        proxy=self.config.proxy
                    ) as response:
                        response_data = await response.json()
                        
                        if response.status < 400:
                            return response_data
                        else:
                            raise APIRequestError(response.status, response_data.get("error", "Unknown error"))
            except aiohttp.ClientError as e:
                self.logger.warning(f"API request failed (attempt {attempt + 1}/{self.config.retries + 1}): {str(e)}")
                if attempt < self.config.retries:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise APIRequestError(0, f"API request failed after {self.config.retries + 1} attempts: {str(e)}")
```

## Component-Specific Implementations

### Scene Detection (Twelve Labs)

```python
from video_understanding.ai.scene.base import BaseSceneDetector
from video_understanding.exceptions import SceneDetectionError
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

class TwelveLabsConfig(BaseModel):
    """Configuration for Twelve Labs API."""
    api_key: str
    api_url: str = "https://api.twelvelabs.io/v1"
    timeout: float = 30.0
    retries: int = 3

class TwelveLabsSceneDetector(BaseSceneDetector):
    """Scene detection implementation using Twelve Labs API."""
    
    def __init__(self, config: TwelveLabsConfig):
        """Initialize Twelve Labs scene detector.
        
        Args:
            config: Twelve Labs configuration
        """
        self.config = config
        self.client = APIClient(config)
        self.logger = logging.getLogger(__name__)
        
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
            # Implementation details for Twelve Labs
            return scenes
        except Exception as e:
            self.logger.error(f"Scene detection failed: {str(e)}")
            raise SceneDetectionError(f"Scene detection failed: {str(e)}")
```

### Vector Storage (Pinecone)

```python
from video_understanding.storage.vector.base import BaseVectorStorage
from video_understanding.exceptions import VectorStorageError
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
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
        pinecone.init(
            api_key=self.config.api_key,
            environment=self.config.environment
        )
        
        # Implementation details for Pinecone
```

## Component Quality Standards

All components should adhere to these quality standards:

1. **Type Hinting**: All methods should include proper type hints
2. **Docstrings**: All classes and methods should have docstrings
3. **Error Handling**: All components should have proper error handling
4. **Logging**: All components should include logging
5. **Configuration**: All components should use Pydantic for configuration
6. **Tests**: All components should have unit tests and integration tests

## Implementation Checklist

When implementing a new component or refactoring an existing one, follow this checklist:

1. [ ] Define base interface with abstract methods
2. [ ] Implement configuration model using Pydantic
3. [ ] Create concrete implementation class
4. [ ] Implement error handling with custom exceptions
5. [ ] Add comprehensive logging
6. [ ] Include type hints for all methods
7. [ ] Write unit tests with proper mocking
8. [ ] Create integration tests for API components
9. [ ] Add to component factory
10. [ ] Update documentation

## Dependency Approach

For handling dependencies, prefer:

1. **Dependency Injection**: Pass dependencies to constructors
2. **Factory Pattern**: Use factories to create components
3. **Configuration Objects**: Use Pydantic models for configuration

Avoid:
1. Global state
2. Singletons
3. Direct imports of concrete implementations

## Component Integration Approach

For integrating components, follow these approaches:

1. **Composite Pattern**: For complex components that contain multiple sub-components
2. **Strategy Pattern**: For components with multiple algorithms
3. **Adapter Pattern**: For integrating with third-party APIs
4. **Facade Pattern**: For simplifying complex subsystems

## Implementation Examples for Key Components

### Scene Detection Implementation

```python
# Base interface
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseSceneDetector(ABC):
    """Base interface for scene detection."""
    
    @abstractmethod
    async def detect_scenes(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect scenes in a video.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of detected scenes
            
        Raises:
            SceneDetectionError: If scene detection fails
        """
        pass

# Twelve Labs implementation
from video_understanding.ai.scene.base import BaseSceneDetector
from video_understanding.exceptions import SceneDetectionError
from video_understanding.utils.api import APIClient
from pydantic import BaseModel
from typing import Dict, Any, List
import logging

class TwelveLabsConfig(BaseModel):
    """Configuration for Twelve Labs API."""
    api_key: str
    api_url: str = "https://api.twelvelabs.io/v1"
    timeout: float = 30.0
    retries: int = 3

class TwelveLabsSceneDetector(BaseSceneDetector):
    """Scene detection implementation using Twelve Labs API."""
    
    def __init__(self, config: TwelveLabsConfig):
        """Initialize Twelve Labs scene detector.
        
        Args:
            config: Twelve Labs configuration
        """
        self.config = config
        self.client = APIClient(config)
        self.logger = logging.getLogger(__name__)
        
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
            # Implementation details
            return scenes
        except Exception as e:
            self.logger.error(f"Scene detection failed: {str(e)}")
            raise SceneDetectionError(f"Scene detection failed: {str(e)}")

# Factory
from typing import Dict, Any, Type
from video_understanding.ai.scene.base import BaseSceneDetector
from video_understanding.ai.scene.opencv import OpenCVSceneDetector
from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetector, TwelveLabsConfig

class SceneDetectorFactory:
    """Factory for creating scene detector instances."""
    
    _registry = {
        "opencv": OpenCVSceneDetector,
        "twelve_labs": TwelveLabsSceneDetector
    }
    
    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> BaseSceneDetector:
        """Create a scene detector instance.
        
        Args:
            name: Scene detector name
            config: Scene detector configuration
            
        Returns:
            Scene detector instance
        """
        if name not in cls._registry:
            raise ValueError(f"Scene detector not registered: {name}")
            
        detector_class = cls._registry[name]
        
        # Convert dict config to appropriate config class
        if name == "twelve_labs":
            config_obj = TwelveLabsConfig(**config)
        else:
            config_obj = config
            
        return detector_class(config_obj)
```