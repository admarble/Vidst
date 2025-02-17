# AI Pipeline Documentation

## Overview

The `VideoPipeline` class orchestrates the video processing pipeline, managing multiple AI models and processing stages for video analysis. It provides a flexible and extensible architecture for video content understanding.

## Installation

```bash
pip install -r requirements.txt
```

## Basic Usage

```python
from pathlib import Path
from src.ai.pipeline import VideoPipeline
from src.core.config import VideoConfig

# Initialize pipeline
config = VideoConfig()
pipeline = VideoPipeline(config)

# Process a video
# You can provide either a path string or Path object
results = pipeline.process("path/to/video.mp4")
# Or use a dictionary with additional parameters
results = pipeline.process({
    "video_path": "path/to/video.mp4",
    "task": "scene_detection"
})
```

## Features

- **Modular AI Model Integration**: Add and combine multiple AI models
- **Multi-stage Processing**: Scene detection, audio transcription, and text extraction
- **Resource Monitoring**: Built-in memory usage tracking
- **Flexible Input Handling**: Supports both path strings and structured input
- **Robust Error Handling**: Comprehensive validation and error reporting

## API Reference

### Constructor

```python
def __init__(self, config: VideoConfig, models: Optional[List[BaseModel]] = None)
```

- `config`: Video configuration instance
- `models`: Optional list of AI model instances

### Core Methods

#### process()

```python
def process(self, input_data: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]
```

Process a video through all configured models.

**Input**:
- String or Path: Direct video path
- Dictionary: Structured input with parameters
  - Required: `video_path`
  - Optional: `task` and model-specific parameters

**Returns**:
Dictionary containing:
- `status`: Processing status ("processing" or "completed")
- `metadata`: Video information (duration, frame count, resolution, fps)
- Model-specific results
- `scene_description`: Scene analysis results

**Raises**:
- `ProcessingError`: If processing fails

#### add_model()

```python
def add_model(self, model: BaseModel) -> None
```

Add an AI model to the pipeline.

### Specialized Methods

#### detect_scenes()

```python
def detect_scenes(self, video_path: Path) -> List[Dict[str, Any]]
```

Detect and analyze scenes in a video.

#### transcribe_audio()

```python
def transcribe_audio(self, video_path: Path) -> Dict[str, Any]
```

Transcribe audio content from a video.

#### extract_text()

```python
def extract_text(self, video_path: Path) -> List[Dict[str, Any]]
```

Extract and analyze text from video frames.

#### get_memory_usage()

```python
def get_memory_usage(self) -> Dict[str, float]
```

Get current memory usage statistics.

## Error Handling

The pipeline implements comprehensive error handling:
- Input validation
- File existence and format checks
- Model processing error handling
- Resource monitoring

## Examples

### Basic Scene Detection

```python
from src.ai.pipeline import VideoPipeline
from src.core.config import VideoConfig

pipeline = VideoPipeline(VideoConfig())
scenes = pipeline.detect_scenes("lecture.mp4")
print(f"Found {len(scenes)} scenes")
```

### Full Processing with Multiple Models

```python
from src.ai.models import SceneDetector, TextExtractor, AudioTranscriber

pipeline = VideoPipeline(VideoConfig())
pipeline.add_model(SceneDetector())
pipeline.add_model(TextExtractor())
pipeline.add_model(AudioTranscriber())

results = pipeline.process({
    "video_path": "tutorial.mp4",
    "task": "full_analysis"
})

print(f"Processing completed: {results['status']}")
print(f"Duration: {results['metadata']['duration']}s")
print(f"Detected text segments: {len(results.get('text_segments', []))}")
```

## Performance Considerations

- Memory usage is monitored through `get_memory_usage()`
- Large videos are processed in chunks
- Multiple models can run concurrently
- Resource limits are configurable through `VideoConfig`

## Best Practices

1. **Model Management**:
   - Add models before processing
   - Use appropriate models for the task
   - Monitor memory usage for large videos

2. **Error Handling**:
   - Always handle `ProcessingError` exceptions
   - Validate input before processing
   - Check results status

3. **Resource Management**:
   - Monitor memory usage for long-running tasks
   - Release resources after processing
   - Use appropriate batch sizes for large videos 