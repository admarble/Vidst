# Vidst Refactoring - Component Base Patterns

## When to apply
@semantics Applies when creating or implementing core component structures following the base architecture patterns.
@files src/video_understanding/**/base.py src/video_understanding/**/*.py
@userMessages ".*create base component.*" ".*component interface.*" ".*base class.*" ".*abstract.*interface.*"

## Component Base Architecture

All components in Vidst should follow this core architecture:

1. **Base Interface**: Abstract base class defining the component interface
2. **Concrete Implementations**: Classes implementing the base interface
3. **Factory**: Factory class for creating component instances

## Base Interface Pattern

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseComponent(ABC):
    """Base interface for component implementation.
    
    All components should inherit from this base class.
    """
    
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

## Configuration Pattern

Use Pydantic models for component configuration:

```python
from pydantic import BaseModel, Field
from typing import Optional

class ComponentConfig(BaseModel):
    """Configuration for component."""
    name: str
    version: str = "1.0.0"
    # Add component-specific settings
    settings: Optional[Dict[str, Any]] = None
```

## Error Handling Pattern

Create custom exception classes for components:

```python
class ComponentError(Exception):
    """Base error for component operations."""
    pass

class ConfigurationError(ComponentError):
    """Error with component configuration."""
    pass

class ProcessingError(ComponentError):
    """Error during component processing."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.details = details or {}
        super().__init__(message)
```

## Component Factory Pattern

```python
from typing import Dict, Any, Type

class ComponentFactory:
    """Factory for creating component instances."""
    
    _registry = {}  # Component registry
    
    @classmethod
    def register(cls, name: str, component_class: Type) -> None:
        """Register a component class.
        
        Args:
            name: Component name
            component_class: Component class
        """
        cls._registry[name] = component_class
    
    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> Any:
        """Create a component instance.
        
        Args:
            name: Component name
            config: Component configuration
            
        Returns:
            Component instance
            
        Raises:
            ValueError: If component not registered
        """
        if name not in cls._registry:
            raise ValueError(f"Component not registered: {name}")
            
        component_class = cls._registry[name]
        return component_class(config)
```

## Component Quality Checklist

When creating base components, ensure:

1. ✓ Clear and descriptive docstrings
2. ✓ Proper type hints for all methods 
3. ✓ Well-defined interfaces with minimal methods
4. ✓ Appropriate error classes
5. ✓ Use of Pydantic for configuration validation

## Example: Scene Detector Base

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseSceneDetector(ABC):
    """Base interface for scene detection components."""
    
    @abstractmethod
    async def detect_scenes(self, video_path: str) -> List[Dict[str, Any]]:
        """Detect scenes in a video.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of detected scenes with timing information
            
        Raises:
            SceneDetectionError: If detection fails
        """
        pass
```
