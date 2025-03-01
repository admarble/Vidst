# Vidst Docstring Implementation Guide

## Overview

This guide provides practical instructions for implementing docstrings in the Vidst project. Consistent docstrings improve code readability, facilitate onboarding, and enable automatic documentation generation.

## Key Principles

For the Vidst POC phase, follow these docstring principles:

1. **Essential Only**: Document what's necessary, not everything possible
2. **User-Focused**: Write for the developers who will use your code
3. **Practical Examples**: Include examples for non-obvious functionality
4. **Keep It Current**: Update docstrings when you change functionality

## Quick Reference

| Code Element | When to Document | Priority Elements |
|--------------|------------------|-------------------|
| **Modules** | All public modules | Purpose, key components, example |
| **Classes** | All public classes | Purpose, important attributes, usage example |
| **Methods** | Public methods, complex private methods | Purpose, parameters, return values, exceptions |
| **Properties** | Public properties | Purpose, return value |
| **Constants** | Module-level constants | Purpose, units, constraints |

## Implementation Strategy

### 1. For New Code

Always include appropriate docstrings when writing new code, using the templates provided in `docstring_templates.py`.

### 2. For Existing Code

Follow this prioritization when adding docstrings to existing code:

1. Core user-facing components
2. Public APIs
3. Complex algorithms or non-obvious functionality
4. Supporting functionality

### 3. During Refactoring

When refactoring, update docstrings to reflect changes and add missing documentation.

## Using the Templates

The project provides templates in `docstring_templates.py`. Here's how to use them effectively:

### Module Docstrings

Place at the top of the file:

```python
"""Video processing core for scene detection and analysis.

This module provides the core functionality for processing video files,
detecting scene changes, and extracting relevant metadata.

Primary classes:
    * VideoProcessor: Main entry point for video processing
    * SceneDetector: Handles scene boundary detection

Example:
    ```python
    processor = VideoProcessor(config)
    with processor.process("video.mp4") as ctx:
        scenes = processor.detect_scenes(ctx)
    ```
"""
```

Keep module docstrings focused on the module's purpose and main components.

### Class Docstrings

```python
class SceneDetector:
    """Handles video scene detection and analysis.
    
    Analyzes video frame-by-frame to detect scene changes.
    
    Attributes:
        min_scene_length (float): Minimum scene length in seconds
        max_scenes (int): Maximum number of scenes to detect
    
    Example:
        ```python
        detector = SceneDetector(min_scene_length=2.0)
        scenes = detector.detect_scenes(video)
        ```
    """
```

Focus on what the class does and how to use it, not implementation details.

### Method Docstrings

```python
def detect_scenes(self, video: Video) -> list[Scene]:
    """Detect scenes in a video.
    
    Args:
        video (Video): Video object to process
        
    Returns:
        list[Scene]: Detected scene objects
        
    Raises:
        ValueError: If video file is not found
    """
```

For methods, always document parameters, return values, and exceptions.

### Property Docstrings

```python
@property
def scene_count(self) -> int:
    """Number of detected scenes.
    
    Returns:
        int: Scene count
    """
```

Keep property docstrings brief and focused on what they represent.

### Constants Docstrings

```python
DEFAULT_THRESHOLD = 30.0
"""Default threshold for scene change detection.

Units: Absolute pixel difference (0-255 scale)
"""
```

Include units or constraints for numerical constants.

## Common Mistakes to Avoid

1. **Describing Implementation**: Focus on behavior, not how it's implemented
2. **Missing Updates**: Not updating docstrings when code changes
3. **Excessive Detail**: Including unnecessary information in POC phase
4. **Incomplete Args**: Not documenting all parameters
5. **Unclear Examples**: Providing examples that don't clearly demonstrate usage

## Practical Examples

### Basic Function Example

```python
def extract_keyframe(self, video_path: Path, timestamp: float) -> np.ndarray:
    """Extract a keyframe from the video at the specified timestamp.
    
    Args:
        video_path: Path to the video file
        timestamp: Time in seconds to extract frame from
        
    Returns:
        Extracted frame as numpy array
        
    Raises:
        ValueError: If frame cannot be extracted
    """
```

### Class with Complete Documentation

```python
class TextExtractor:
    """Extracts and analyzes text from video frames.
    
    Performs OCR on video frames to identify and extract visible text.
    
    Attributes:
        languages (list[str]): Supported languages for OCR
        confidence_threshold (float): Minimum confidence score (0-1)
        
    Example:
        ```python
        extractor = TextExtractor(languages=["en"])
        text_regions = extractor.extract_text(frame)
        for region in text_regions:
            print(f"Found text: {region.text}")
        ```
    """
    
    def __init__(self, languages: list[str] = ["en"], confidence_threshold: float = 0.7):
        """Initialize text extractor.
        
        Args:
            languages: List of language codes to detect
            confidence_threshold: Minimum confidence score (0-1)
        """
        self.languages = languages
        self.confidence_threshold = confidence_threshold
```

## Integration with Tools

These docstrings are compatible with:

- **VS Code** and **PyCharm** docstring preview
- **Sphinx** documentation generation
- **mkdocstrings** for MkDocs integration

## Conclusion

Following this implementation guide will ensure consistent, useful docstrings throughout the Vidst codebase while maintaining focus on the POC goals. Remember that documentation should be concise yet complete, prioritizing what developers need to effectively use the code.
