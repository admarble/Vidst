# Transcription Service Interface

## Overview

The Transcription Service Interface provides a standardized way to extract text from audio in videos. It abstracts the complexities of different transcription providers, allowing the application to switch between different transcription services without changing the core application code. This service is essential for making video content searchable and accessible.

## Key Components

### BaseTranscriptionService

An abstract base class that defines the interface for all transcription services. It includes methods for:

- **Transcribing audio**: Extract text from audio files with timestamps
- **Batch processing**: Process multiple audio files efficiently
- **Speaker diarization**: Identify different speakers in the audio
- **Language detection**: Automatically detect or specify the language
- **Initialization and shutdown**: Manage resources properly

### WhisperTranscriptionService

An implementation of the `BaseTranscriptionService` using OpenAI's Whisper model:

- **Integration**: Connects to the Whisper API for high-quality transcription
- **Error handling**: Manages API errors and retries with exponential backoff
- **Confidence scoring**: Provides confidence levels for transcribed segments
- **Multi-language support**: Handles multiple languages automatically

### TranscriptionServiceFactory

A factory class for creating transcription service instances:

- **Dynamic service creation**: Creates the appropriate service based on configuration
- **Service registration**: Allows registering new service implementations
- **Configuration validation**: Ensures the configuration is valid before creating a service

## Configuration

The `WhisperConfig` class provides configuration options for the Whisper transcription service:

```python
class WhisperConfig(ServiceConfig):
    """Configuration for the Whisper transcription service."""

    api_key: str
    model_size: str = "large-v3"
    language: Optional[str] = None
    detect_speakers: bool = True
    max_speakers: int = 10
    word_timestamps: bool = True
    confidence_threshold: float = 0.5
    timeout: int = 300
    max_retries: int = 3
```

## Usage Examples

### Basic Usage

```python
from video_understanding.ai.transcription import WhisperTranscriptionService, WhisperConfig

# Create configuration
config = WhisperConfig(
    api_key="your-api-key",
    model_size="large-v3",
    detect_speakers=True
)

# Create service
transcription_service = WhisperTranscriptionService(config)

# Initialize service
await transcription_service.initialize()

try:
    # Transcribe audio
    result = await transcription_service.transcribe_audio("path/to/audio.mp3")

    # Process results
    for segment in result:
        print(f"[{segment.start_time:.2f} - {segment.end_time:.2f}] {segment.speaker}: {segment.text}")
finally:
    # Clean up resources
    await transcription_service.shutdown()
```

### Factory-based Usage

```python
from video_understanding.ai.transcription import TranscriptionServiceFactory, WhisperConfig

# Create configuration
config = WhisperConfig(
    api_key="your-api-key",
    model_size="large-v3"
)

# Create service using factory
factory = TranscriptionServiceFactory()
transcription_service = factory.create_service("whisper", config)

# Use service
await transcription_service.initialize()
try:
    result = await transcription_service.transcribe_audio("path/to/audio.mp3")
    # Process results...
finally:
    await transcription_service.shutdown()
```

## Error Handling

```python
from video_understanding.services.exceptions import ServiceError, TranscriptionError

try:
    result = await transcription_service.transcribe_audio("path/to/audio.mp3")
except TranscriptionError as e:
    print(f"Transcription failed: {e}")
    print(f"Context: {e.context}")  # Additional error context
except ServiceError as e:
    print(f"Service error: {e}")
```

## Implementation Details

### TranscriptionResult

The `transcribe_audio` method returns a list of `TranscriptionResult` objects:

```python
@dataclass
class TranscriptionResult:
    """Results from audio transcription."""

    text: str
    start_time: float
    end_time: float
    speaker: str | None = None
    confidence: float = 0.0
    language: str | None = None
```

### Batch Processing

For processing multiple audio files efficiently:

```python
results = await transcription_service.batch_transcribe([
    "path/to/audio1.mp3",
    "path/to/audio2.mp3",
    "path/to/audio3.mp3"
])
```

## Best Practices

1. **Always initialize the service** before use and shut it down when finished
2. **Use the factory pattern** for service creation to allow for easy switching between providers
3. **Handle errors appropriately** by catching specific exception types
4. **Use batch processing** for multiple files to improve efficiency
5. **Set appropriate confidence thresholds** for your use case
6. **Properly manage resources** by using async context managers or try/finally blocks
7. **Consider language settings** for better accuracy with non-English content
8. **Monitor performance metrics** to optimize configuration
