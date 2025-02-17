# Error Handling Documentation

## Overview

The error handling system provides a comprehensive hierarchy of custom exceptions for managing and debugging errors in the video processing pipeline. It ensures proper error propagation, clear error messages, and consistent error handling across the application.

## Exception Hierarchy

```
VideoProcessingError
├── FileValidationError
├── ProcessingError
├── StorageError
├── ModelError
└── ConfigurationError
```

### Base Exception

```python
class VideoProcessingError(Exception):
    """Base exception for all video processing errors"""
```

All custom exceptions inherit from this base class, allowing for catch-all error handling when needed.

### Specific Exceptions

#### FileValidationError

```python
class FileValidationError(VideoProcessingError):
    """Exception raised when file validation fails"""
```

Raised when:
- File does not exist
- File is empty
- Invalid file format
- File size exceeds limits
- File permissions issues

#### ProcessingError

```python
class ProcessingError(VideoProcessingError):
    """Exception raised when video processing fails"""
```

Raised when:
- Video processing pipeline fails
- Frame extraction fails
- Video corruption detected
- Resource limits exceeded
- Processing timeout occurs

#### StorageError

```python
class StorageError(VideoProcessingError):
    """Exception raised when storage operations fail"""
```

Raised when:
- Vector storage operations fail
- Invalid vector dimensions
- Invalid data types
- Storage capacity exceeded
- Metadata validation fails

#### ModelError

```python
class ModelError(VideoProcessingError):
    """Exception raised when AI model operations fail"""
```

Raised when:
- Model initialization fails
- Invalid model input
- API errors occur
- Model timeout
- Resource constraints hit

#### ConfigurationError

```python
class ConfigurationError(VideoProcessingError):
    """Exception raised when configuration is invalid"""
```

Raised when:
- Missing required configuration
- Invalid configuration values
- Environment setup fails
- API key validation fails
- Resource configuration invalid

## Usage Examples

### Basic Error Handling

```python
from src.core.exceptions import VideoProcessingError, FileValidationError
from src.video.upload import VideoUploader

try:
    uploader = VideoUploader(config)
    uploader.validate_file("video.mp4")
except FileValidationError as e:
    print(f"File validation failed: {e}")
except VideoProcessingError as e:
    print(f"Processing error: {e}")
```

### Handling Multiple Error Types

```python
from src.core.exceptions import (
    FileValidationError,
    ProcessingError,
    ModelError,
    ConfigurationError
)
from src.ai.pipeline import VideoPipeline

try:
    pipeline = VideoPipeline(config)
    result = pipeline.process({
        "video_path": "video.mp4",
        "start_time": 0,
        "end_time": 10
    })
except FileValidationError as e:
    print(f"Invalid file: {e}")
except ProcessingError as e:
    print(f"Processing failed: {e}")
except ModelError as e:
    print(f"Model error: {e}")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except VideoProcessingError as e:
    print(f"Other error: {e}")
```

### Resource Cleanup

```python
from src.core.exceptions import VideoProcessingError
from src.ai.pipeline import VideoPipeline

pipeline = VideoPipeline(config)
try:
    result = pipeline.process({"video_path": "video.mp4"})
except VideoProcessingError as e:
    print(f"Error: {e}")
finally:
    # Cleanup code here
    pipeline.cleanup()
```

## Testing Error Handling

The system includes comprehensive test coverage for error scenarios:

```python
def test_file_validation_errors():
    config = VideoConfig()
    uploader = VideoUploader(config)

    # Test non-existent file
    with pytest.raises(FileValidationError, match="File does not exist"):
        uploader.validate_file("nonexistent.mp4")

    # Test empty file
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tf:
        with pytest.raises(FileValidationError, match="File is empty"):
            uploader.validate_file(tf.name)
```

## Best Practices

1. **Exception Hierarchy**:
   - Use the most specific exception type
   - Maintain the exception hierarchy
   - Add new exceptions as needed

2. **Error Messages**:
   - Include descriptive error messages
   - Add relevant context
   - Include troubleshooting hints

3. **Resource Management**:
   - Use context managers
   - Implement proper cleanup
   - Handle nested exceptions

4. **Testing**:
   - Test all error scenarios
   - Verify error messages
   - Check resource cleanup

## Common Error Scenarios

### File Validation

```python
try:
    uploader.validate_file(file_path)
except FileValidationError as e:
    if "does not exist" in str(e):
        print("Please check the file path")
    elif "empty" in str(e):
        print("The file appears to be corrupted")
    elif "format" in str(e):
        print("Supported formats: MP4, AVI, MOV")
```

### Processing Pipeline

```python
try:
    pipeline.process(input_data)
except ProcessingError as e:
    if "timeout" in str(e):
        print("Processing took too long")
    elif "memory" in str(e):
        print("Not enough memory")
    elif "corrupted" in str(e):
        print("Video file is corrupted")
```

### Configuration

```python
try:
    config.validate()
except ConfigurationError as e:
    if "API key" in str(e):
        print("Please check your API keys")
    elif "directory" in str(e):
        print("Check directory permissions")
    elif "value" in str(e):
        print("Invalid configuration value")
```

## Error Recovery Strategies

1. **Retry Logic**:
   ```python
   from tenacity import retry, stop_after_attempt
   
   @retry(stop=stop_after_attempt(3))
   def process_with_retry(data):
       try:
           return pipeline.process(data)
       except ProcessingError as e:
           if "timeout" in str(e):
               raise  # Retry on timeout
           else:
               return None  # Don't retry other errors
   ```

2. **Graceful Degradation**:
   ```python
   try:
       result = pipeline.process(data)
   except ModelError:
       # Fall back to simpler model
       result = fallback_pipeline.process(data)
   ```

3. **Resource Cleanup**:
   ```python
   try:
       pipeline.process(data)
   except VideoProcessingError:
       pipeline.cleanup()
       raise
   ``` 