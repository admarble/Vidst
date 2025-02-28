# Vidst Refactoring - Workflow Commands

## When to apply
@semantics Applies when the user uses specific commands or phrases related to the workflow, such as backing up code, generating test, implementing components, or creating documentation.
@userMessages ".*let['']s back this up.*" ".*add docstring.*" ".*create test.*" ".*implement this component.*" ".*refactor this.*"

## Workflow Command Responses

This rule provides guidance on how to respond to specific workflow commands from the user during the Vidst refactoring project.

## Backup Commands

### "Let's back this up"

When the user says "let's back this up" or similar, it means they want to create a backup of the current code before making changes. Follow these steps:

1. Determine the file being edited
2. Create a backup in the appropriate location in the `refactor/07_backup/` directory
3. Inform the user of the backup location

Example response:

```
I'll back up the current version of this file before we make changes.

Creating backup at: refactor/07_backup/vector_storage.py.bak

The backup has been created. We can now proceed with the changes.
```

Implementation example:

```python
# Create a backup
import os
import shutil

def backup_file(file_path):
    # Get just the filename
    filename = os.path.basename(file_path)
    
    # Create backup directory if it doesn't exist
    backup_dir = "refactor/07_backup/"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create backup path
    backup_path = os.path.join(backup_dir, f"{filename}.bak")
    
    # Copy the file
    shutil.copy2(file_path, backup_path)
    
    return backup_path
```

## Documentation Commands

### "Add docstring to this"

When the user asks to add a docstring to a function, class, or module, generate a comprehensive docstring following the project's standards:

For functions:

```python
def example_function(param1: str, param2: int) -> bool:
    """Short description of what the function does.
    
    More detailed explanation if needed.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When exception is raised
    """
```

For classes:

```python
class ExampleClass:
    """Short description of what the class does.
    
    More detailed explanation if needed.
    
    Attributes:
        attr1: Description of attribute 1
        attr2: Description of attribute 2
        
    Example:
        ```python
        instance = ExampleClass()
        result = instance.method()
        ```
    """
```

## Testing Commands

### "Create test for this"

When the user asks to create a test for a component, generate a pytest-compatible test file following the project's test structure:

```python
import pytest
from module.path import ComponentToTest

class TestComponent:
    @pytest.fixture
    def component(self):
        # Setup code
        component = ComponentToTest()
        yield component
        # Teardown code if needed
    
    def test_functionality(self, component):
        # Test functionality
        result = component.method()
        assert result == expected_value
    
    def test_error_handling(self, component):
        # Test error handling
        with pytest.raises(ExpectedException):
            component.method_with_invalid_input()
```

For API components, include mocked responses:

```python
import pytest
import responses
from unittest.mock import patch, MagicMock

class TestAPIComponent:
    @pytest.fixture
    def api_client(self):
        config = APIConfig(api_key="test_key")
        return APIComponent(config)
    
    @responses.activate
    def test_api_call(self, api_client):
        # Mock API response
        responses.add(
            responses.POST,
            "https://api.example.com/endpoint",
            json={"status": "success", "data": {}},
            status=200
        )
        
        # Test API call
        result = api_client.method()
        assert result is not None
```

## Implementation Commands

### "Implement this component"

When the user asks to implement a component, create a structured implementation based on the architecture guidelines:

For base interfaces:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseComponent(ABC):
    """Base interface for component implementation."""
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Processed results
            
        Raises:
            ComponentError: If processing fails
        """
        pass
    
    @abstractmethod
    def validate(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            ValidationError: If validation fails
        """
        pass
```

For concrete implementations:

```python
from video_understanding.component.base import BaseComponent
from video_understanding.exceptions import ComponentError, ValidationError
from typing import Dict, Any

class ConcreteComponent(BaseComponent):
    """Concrete implementation of component."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize component.
        
        Args:
            config: Component configuration
        """
        self.config = config
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results.
        
        Args:
            input_data: Input data to process
            
        Returns:
            Processed results
            
        Raises:
            ComponentError: If processing fails
        """
        try:
            # Validate input
            if not self.validate(input_data):
                raise ValidationError("Invalid input data")
                
            # Process data
            # ...
            
            # Return results
            return {
                "status": "success",
                "results": {}
            }
        except Exception as e:
            raise ComponentError(f"Processing failed: {str(e)}")
    
    def validate(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            ValidationError: If validation fails
        """
        # Check required fields
        required_fields = ["field1", "field2"]
        for field in required_fields:
            if field not in input_data:
                return False
                
        # Check field types
        if not isinstance(input_data["field1"], str):
            return False
            
        return True
```

For API integrations, include circuit breaker and retry patterns:

```python
from video_understanding.component.base import BaseComponent
from video_understanding.utils.circuit_breaker import CircuitBreaker
from video_understanding.utils.retry import retry_with_backoff
from typing import Dict, Any

class APIComponent(BaseComponent):
    """API integration component."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize component.
        
        Args:
            config: Component configuration
        """
        self.config = config
        self.client = self._initialize_client()
        self.circuit_breaker = CircuitBreaker()
        
    def _initialize_client(self):
        """Initialize API client."""
        # API client initialization
        pass
    
    @retry_with_backoff(max_tries=3)
    async def _call_api(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Call API with retry logic.
        
        Args:
            request: API request
            
        Returns:
            API response
            
        Raises:
            APIError: If API call fails
        """
        # API call implementation
        pass
    
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
            # Validate input
            if not self.validate(input_data):
                raise ValidationError("Invalid input data")
                
            # Prepare API request
            request = self._prepare_request(input_data)
            
            # Call API with circuit breaker
            response = await self.circuit_breaker.execute(
                self._call_api, request
            )
            
            # Process response
            results = self._process_response(response)
            
            # Return results
            return {
                "status": "success",
                "results": results
            }
        except Exception as e:
            raise ComponentError(f"Processing failed: {str(e)}")
```

## Refactoring Commands

### "Refactor this"

When the user asks to refactor code, apply the following steps:

1. Identify the current implementation patterns
2. Apply proper abstraction layers
3. Implement interfaces and factories
4. Add proper error handling
5. Ensure docstrings are complete
6. Add type hints

Example refactoring from procedural to object-oriented:

Before:
```python
def process_video(file_path):
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    # Load video
    video = cv2.VideoCapture(file_path)
    
    # Process frames
    frames = []
    while True:
        ret, frame = video.read()
        if not ret:
            break
        frames.append(frame)
        
    # Detect scenes
    scenes = []
    for i in range(1, len(frames)):
        diff = compute_frame_diff(frames[i-1], frames[i])
        if diff > THRESHOLD:
            scenes.append(i)
            
    return scenes
```

After:
```python
class VideoProcessor:
    """Video processing component for scene detection."""
    
    def __init__(self, threshold=30.0):
        """Initialize video processor.
        
        Args:
            threshold: Threshold for scene change detection
        """
        self.threshold = threshold
        
    def process(self, file_path):
        """Process video file and detect scenes.
        
        Args:
            file_path: Path to video file
            
        Returns:
            List of detected scene indices
            
        Raises:
            FileNotFoundError: If file not found
            VideoProcessingError: If processing fails
        """
        try:
            # Validate file
            self._validate_file(file_path)
            
            # Load video
            frames = self._load_frames(file_path)
            
            # Detect scenes
            scenes = self._detect_scenes(frames)
            
            return scenes
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                raise
            raise VideoProcessingError(f"Processing failed: {str(e)}")
            
    def _validate_file(self, file_path):
        """Validate video file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
    def _load_frames(self, file_path):
        """Load video frames."""
        frames = []
        video = cv2.VideoCapture(file_path)
        while True:
            ret, frame = video.read()
            if not ret:
                break
            frames.append(frame)
        return frames
        
    def _detect_scenes(self, frames):
        """Detect scenes from frames."""
        scenes = []
        for i in range(1, len(frames)):
            diff = self._compute_frame_diff(frames[i-1], frames[i])
            if diff > self.threshold:
                scenes.append(i)
        return scenes
        
    def _compute_frame_diff(self, frame1, frame2):
        """Compute difference between frames."""
        # Compute frame difference
        pass
```

## Factory Pattern Implementation

When refactoring to use factory patterns:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseComponent(ABC):
    """Base component interface."""
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data."""
        pass

class ConcreteComponentA(BaseComponent):
    """Concrete implementation A."""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data."""
        # Implementation A
        pass

class ConcreteComponentB(BaseComponent):
    """Concrete implementation B."""
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data."""
        # Implementation B
        pass

class ComponentFactory:
    """Factory for creating components."""
    
    @staticmethod
    def create(component_type: str, config: Dict[str, Any] = None) -> BaseComponent:
        """Create component instance.
        
        Args:
            component_type: Type of component to create
            config: Component configuration
            
        Returns:
            Component instance
            
        Raises:
            ValueError: If component type is unknown
        """
        if component_type == "A":
            return ConcreteComponentA()
        elif component_type == "B":
            return ConcreteComponentB()
        else:
            raise ValueError(f"Unknown component type: {component_type}")
```

## API Factory Implementation

For API component factories:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAPIClient(ABC):
    """Base API client interface."""
    
    @abstractmethod
    async def call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Call API."""
        pass

class APIClientA(BaseAPIClient):
    """API client implementation A."""
    
    def __init__(self, api_key: str):
        """Initialize API client.
        
        Args:
            api_key: API key
        """
        self.api_key = api_key
        
    async def call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Call API."""
        # Implementation A
        pass

class APIClientB(BaseAPIClient):
    """API client implementation B."""
    
    def __init__(self, api_key: str, endpoint: str):
        """Initialize API client.
        
        Args:
            api_key: API key
            endpoint: API endpoint
        """
        self.api_key = api_key
        self.endpoint = endpoint
        
    async def call(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Call API."""
        # Implementation B
        pass

class APIClientFactory:
    """Factory for creating API clients."""
    
    @staticmethod
    def create(client_type: str, config: Dict[str, Any]) -> BaseAPIClient:
        """Create API client instance.
        
        Args:
            client_type: Type of API client to create
            config: API client configuration
            
        Returns:
            API client instance
            
        Raises:
            ValueError: If client type is unknown
        """
        if client_type == "A":
            return APIClientA(api_key=config["api_key"])
        elif client_type == "B":
            return APIClientB(api_key=config["api_key"], endpoint=config["endpoint"])
        else:
            raise ValueError(f"Unknown API client type: {client_type}")
```
