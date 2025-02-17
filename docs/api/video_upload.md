# Video Upload Documentation

## Overview

The video upload system provides a secure and validated way to handle video file uploads. It ensures file integrity, enforces size limits, validates formats, and manages the storage of uploaded files.

## Features

- File validation (size, format, integrity)
- Secure file storage
- Automatic directory management
- UUID-based file organization
- Format validation
- Error handling

## Basic Usage

```python
from pathlib import Path
from src.core.config import VideoConfig
from src.video.upload import VideoUploader

# Initialize uploader
config = VideoConfig()
uploader = VideoUploader(config)

# Upload a video
try:
    video = uploader.upload("path/to/video.mp4")
    print(f"Uploaded video ID: {video.id}")
except FileValidationError as e:
    print(f"Upload failed: {e}")
```

## API Reference

### VideoUploader

```python
class VideoUploader:
    def __init__(self, config: VideoConfig):
        """Initialize uploader with configuration."""
```

#### Constructor Parameters

- `config`: VideoConfig instance containing:
  - `MAX_FILE_SIZE`: Maximum allowed file size
  - `SUPPORTED_FORMATS`: Set of allowed video formats
  - `UPLOAD_DIRECTORY`: Base directory for uploads

### Methods

#### validate_file()

```python
def validate_file(self, file_path: str) -> bool
```

Validate a video file before upload.

**Parameters**:
- `file_path`: Path to video file

**Returns**:
- `True` if file is valid

**Raises**:
- `FileValidationError`: If file validation fails

**Validation Checks**:
- File existence
- File format
- File size
- File integrity

**Example**:
```python
try:
    uploader.validate_file("video.mp4")
    print("File is valid")
except FileValidationError as e:
    print(f"Validation failed: {e}")
```

#### upload()

```python
def upload(self, file_path: str) -> Video
```

Upload a video file and create a Video model instance.

**Parameters**:
- `file_path`: Path to video file

**Returns**:
- `Video`: Video model instance

**Raises**:
- `FileValidationError`: If file validation fails

**Example**:
```python
try:
    video = uploader.upload("video.mp4")
    print(f"Video uploaded: {video.id}")
    print(f"Format: {video.format}")
    print(f"Size: {video.file_size} bytes")
except FileValidationError as e:
    print(f"Upload failed: {e}")
```

## Storage Structure

```
uploads/
├── 123e4567-e89b-12d3-a456-426614174000/
│   └── video1.mp4
├── 987fcdeb-51a2-3b4c-9d8e-765432109876/
│   └── video2.avi
└── ...
```

Each uploaded video is stored in its own directory named with a UUID.

## Examples

### Basic Upload

```python
from src.video.upload import VideoUploader
from src.core.config import VideoConfig

config = VideoConfig()
uploader = VideoUploader(config)

# Upload video
video = uploader.upload("lecture.mp4")
print(f"Uploaded to: {video.path}")
```

### Format Validation

```python
try:
    uploader.validate_file("document.pdf")
except FileValidationError as e:
    print(f"Invalid format: {e}")  # Will print supported formats
```

### Size Validation

```python
from src.core.config import VideoConfig
from src.video.upload import VideoUploader

# Custom configuration
config = VideoConfig()
config.MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB limit
uploader = VideoUploader(config)

try:
    uploader.validate_file("large_video.mp4")
except FileValidationError as e:
    print(f"Size validation failed: {e}")
```

### Error Handling

```python
from src.core.exceptions import FileValidationError

def safe_upload(file_path: str) -> Optional[Video]:
    try:
        uploader = VideoUploader(VideoConfig())
        return uploader.upload(file_path)
    except FileValidationError as e:
        if "does not exist" in str(e):
            print("Please check the file path")
        elif "format" in str(e):
            print("Unsupported video format")
        elif "size" in str(e):
            print("File is too large")
        return None
```

## Best Practices

1. **File Validation**:
   - Always validate before upload
   - Check file integrity
   - Verify file format
   - Enforce size limits

2. **Error Handling**:
   - Handle validation errors gracefully
   - Provide clear error messages
   - Clean up on failure

3. **Storage Management**:
   - Monitor storage usage
   - Clean up temporary files
   - Use appropriate permissions

4. **Security**:
   - Validate file types
   - Scan for malware
   - Use secure file operations

## Performance Considerations

1. **File Size**:
   - Use appropriate size limits
   - Consider streaming for large files
   - Monitor memory usage

2. **Storage Space**:
   - Monitor available space
   - Implement cleanup policies
   - Use efficient storage methods

3. **Concurrent Uploads**:
   - Handle multiple uploads safely
   - Use appropriate locking
   - Monitor system resources

## Common Issues

### 1. Permission Errors

```python
try:
    video = uploader.upload("video.mp4")
except FileValidationError as e:
    if "permission" in str(e).lower():
        print("Check file and directory permissions")
```

### 2. Space Issues

```python
def check_storage_space(path: Path) -> bool:
    """Check if enough storage space is available."""
    free_space = shutil.disk_usage(path).free
    return free_space > VideoConfig.MAX_FILE_SIZE
```

### 3. Format Issues

```python
def is_supported_format(file_path: str) -> bool:
    """Check if file format is supported."""
    return Path(file_path).suffix.lower()[1:] in {
        fmt.lower() for fmt in VideoConfig.SUPPORTED_FORMATS
    }
``` 