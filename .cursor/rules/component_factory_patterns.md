# Vidst Refactoring - Factory Patterns

## When to apply
@semantics Applies when implementing factory patterns for component creation and dependency management.
@files src/video_understanding/**/*factory*.py src/video_understanding/**/factory/*.py
@userMessages ".*factory pattern.*" ".*component factory.*" ".*create factory.*" ".*dependency injection.*"

## Factory Pattern Guidelines

This rule provides guidance for implementing factory patterns to enable dynamic component creation and dependency injection.

## Basic Factory Pattern

```python
from typing import Dict, Any, Type
from video_understanding.component.base import BaseComponent

class ComponentFactory:
    """Factory for creating component instances."""
    
    _registry = {}  # Component registry
    
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
        """
        if name not in cls._registry:
            raise ValueError(f"Component not registered: {name}")
            
        return cls._registry[name](config)
```

## Factory with Configuration Handling

```python
from typing import Dict, Any, Type
import importlib

class SceneDetectorFactory:
    """Factory for creating scene detector instances."""
    
    _registry = {
        "opencv": "video_understanding.ai.scene.opencv.OpenCVSceneDetector",
        "twelve_labs": "video_understanding.ai.scene.twelve_labs.TwelveLabsSceneDetector"
    }
    
    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> Any:
        """Create a scene detector instance."""
        if name not in cls._registry:
            raise ValueError(f"Scene detector not registered: {name}")
            
        # Get the component class path
        class_path = cls._registry[name]
        
        # Split module and class name
        module_path, class_name = class_path.rsplit('.', 1)
        
        # Import the module
        module = importlib.import_module(module_path)
        
        # Get the class
        component_class = getattr(module, class_name)
        
        # Get the config class if available
        config_class_name = f"{class_name}Config"
        if hasattr(module, config_class_name):
            config_class = getattr(module, config_class_name)
            config_obj = config_class(**config)
        else:
            config_obj = config
            
        # Create and return the component
        return component_class(config_obj)
```

## Component Registration Example

```python
# Register components
from video_understanding.ai.scene.opencv import OpenCVSceneDetector
from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetector

# Manual registration
SceneDetectorFactory.register("opencv", OpenCVSceneDetector)
SceneDetectorFactory.register("twelve_labs", TwelveLabsSceneDetector)

# Auto-registration decorator
def register_component(name):
    """Decorator to register a component with a factory."""
    def decorator(cls):
        ComponentFactory.register(name, cls)
        return cls
    return decorator

@register_component("custom_detector")
class CustomSceneDetector(BaseSceneDetector):
    """Custom scene detector implementation."""
    # Implementation...
```

## Service Locator Pattern

For more complex dependency management:

```python
class ServiceLocator:
    """Service locator for dependency management."""
    
    _services = {}
    
    @classmethod
    def register(cls, name: str, service: Any) -> None:
        """Register a service instance."""
        cls._services[name] = service
    
    @classmethod
    def get(cls, name: str) -> Any:
        """Get a service instance."""
        if name not in cls._services:
            raise ValueError(f"Service not registered: {name}")
        return cls._services[name]
    
    @classmethod
    def has(cls, name: str) -> bool:
        """Check if a service is registered."""
        return name in cls._services
```

## Component Factory Implementation Example

```python
# Scene detector factory implementation
class SceneDetectorFactory:
    """Factory for creating scene detector instances."""
    
    _registry = {
        "opencv": OpenCVSceneDetector,
        "twelve_labs": TwelveLabsSceneDetector
    }
    
    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> BaseSceneDetector:
        """Create a scene detector instance."""
        if name not in cls._registry:
            raise ValueError(f"Scene detector not registered: {name}")
            
        detector_class = cls._registry[name]
        
        # Handle config mapping
        if name == "twelve_labs":
            config_obj = TwelveLabsConfig(**config)
        else:
            config_obj = config
            
        return detector_class(config_obj)
```

## Factory Method Pattern

For objects that need to create other objects:

```python
class ProcessorFactory:
    """Base factory for creating processors."""
    
    @abstractmethod
    def create_processor(self) -> BaseProcessor:
        """Create a processor instance."""
        pass

class VideoProcessorFactory(ProcessorFactory):
    """Factory for creating video processors."""
    
    def create_processor(self) -> BaseProcessor:
        """Create a video processor instance."""
        return VideoProcessor()
```

## Factory Best Practices

1. ✓ Use descriptive names for factory methods
2. ✓ Handle configuration mapping within factories
3. ✓ Provide clear error messages for missing components
4. ✓ Use factory registration patterns for extensibility
5. ✓ Keep factories focused on a single component type
6. ✓ Use dependency injection to manage component dependencies

## Component Integration with Factories

```python
# Application setup with factories
def setup_application():
    """Set up the application with factories."""
    # Create configuration
    config = load_configuration()
    
    # Create repositories
    user_repo = RepositoryFactory.create("user", config["database"])
    
    # Create services with dependencies
    user_service = ServiceFactory.create("user", {
        "repository": user_repo,
        "config": config["user_service"]
    })
    
    # Create API components
    scene_detector = SceneDetectorFactory.create(
        "twelve_labs", 
        config["scene_detection"]
    )
    
    # Return components
    return {
        "user_service": user_service,
        "scene_detector": scene_detector
    }
```
