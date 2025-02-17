# Configuration System Documentation

## Overview

The configuration system provides a flexible and type-safe way to manage settings for video processing, system resources, and API integrations. It includes validation, environment variable support, and proper error handling.

## Configuration Classes

### VideoConfig

The `VideoConfig` class manages video processing settings with built-in validation.

```python
from src.core.config import VideoConfig
from pathlib import Path

# Default configuration
config = VideoConfig()

# Custom upload directory
config = VideoConfig(upload_directory=Path("/custom/path"))
```

#### Attributes

- `MAX_FILE_SIZE`: Maximum file size (2GB)
- `SUPPORTED_FORMATS`: Supported video formats (MP4, AVI, MOV)
- `UPLOAD_DIRECTORY`: Video storage location
- `MIN_SCENE_LENGTH`: Minimum scene duration (2 seconds)
- `MAX_SCENES_PER_VIDEO`: Maximum scenes per video (500)

#### Methods

```python
def validate(self) -> None:
    """Validate configuration settings"""
```

Validates:
- Upload directory existence and permissions
- Positive value constraints
- Format support

### ProcessingConfig

The `ProcessingConfig` dataclass manages system resource settings.

```python
@dataclass(frozen=True)
class ProcessingConfig:
    MAX_CONCURRENT_JOBS: int = 3
    MEMORY_LIMIT_PER_JOB: int = 4 * 1024 * 1024 * 1024  # 4GB
    CACHE_TTL: int = 24 * 60 * 60  # 24 hours
    VECTOR_CACHE_SIZE: int = 1024 * 1024 * 1024  # 1GB
```

## Environment Configuration

### Loading Configuration

```python
from src.core.config import load_config

config = load_config()
```

### Required Environment Variables

```bash
# Required API Keys
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
TWELVE_LABS_API_KEY=your_key_here

# Optional Settings
ENVIRONMENT=development  # or production
DEBUG=false
UPLOAD_DIRECTORY=uploads
MAX_CONCURRENT_JOBS=3
CACHE_TTL=86400
```

### Configuration Validation

The system validates:
- Required API keys
- Directory permissions
- Value constraints
- Format support

```python
from src.core.config import validate_api_keys

# Validates API key presence
validate_api_keys(config_dict)
```

## Error Handling

Configuration errors are handled through the `ConfigurationError` exception:

```python
from src.core.exceptions import ConfigurationError

try:
    config = VideoConfig()
    config.validate()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

Common error cases:
- Missing API keys
- Invalid directory permissions
- Invalid value constraints
- Unsupported formats

## Best Practices

1. **Environment Variables**:
   - Use `.env` files for local development
   - Never commit API keys
   - Use secure secrets management in production

2. **Validation**:
   - Always validate configuration before use
   - Handle configuration errors appropriately
   - Log configuration changes

3. **Custom Settings**:
   - Use environment variables for deployment-specific settings
   - Override defaults through constructor parameters
   - Document custom configurations

## Example Usage

### Basic Configuration

```python
from src.core.config import VideoConfig, load_config

# Load environment configuration
env_config = load_config()

# Initialize video configuration
video_config = VideoConfig()
video_config.validate()
```

### Custom Upload Directory

```python
from pathlib import Path
from src.core.config import VideoConfig

# Custom upload location
config = VideoConfig(upload_directory=Path("/data/videos"))
config.validate()
```

### Processing Configuration

```python
from src.core.config import ProcessingConfig

# Use default processing settings
proc_config = ProcessingConfig()

# Access settings
max_jobs = proc_config.MAX_CONCURRENT_JOBS
memory_limit = proc_config.MEMORY_LIMIT_PER_JOB
``` 