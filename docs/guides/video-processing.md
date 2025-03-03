# Video Processing Guide

**Status**: 🔄 In Progress

This guide covers the video processing capabilities of Vidst, including scene detection, audio transcription, and text extraction.

## Basic Video Processing

The core functionality of Vidst is processing videos to extract meaningful information. Here's how to use the basic video processing pipeline:

```python
from vidst.core.processing import VideoProcessor

# Initialize the processor
processor = VideoProcessor()

# Process a video
result = processor.process("path/to/video.mp4")

# Access the results
for scene in result.scenes:
    print(f"Scene from {scene.start_time} to {scene.end_time}: {scene.description}")
```

## Scene Detection

Scene detection identifies distinct scenes within a video:

```python
from vidst.components import SceneDetector

# Initialize the detector
detector = SceneDetector(api_key="your_twelve_labs_api_key")

# Detect scenes
scenes = detector.detect("path/to/video.mp4")

# Process detected scenes
for scene in scenes:
    print(f"Scene starts at {scene.start_time} and ends at {scene.end_time}")
    print(f"Scene description: {scene.description}")
```

## Audio Transcription

Extract speech from videos:

```python
from vidst.components import AudioTranscriber

# Initialize the transcriber
transcriber = AudioTranscriber()

# Transcribe audio
transcript = transcriber.transcribe("path/to/video.mp4")

# Process transcript
for segment in transcript.segments:
    print(f"[{segment.start_time} - {segment.end_time}] {segment.text}")
```

## Text Extraction (OCR)

Extract text visible in video frames:

```python
from vidst.components import TextExtractor

# Initialize the extractor
extractor = TextExtractor()

# Extract text
text_results = extractor.extract("path/to/video.mp4")

# Process extracted text
for result in text_results:
    print(f"Frame at {result.timestamp}: {result.text}")
```

## Advanced Processing Options

### Processing Configuration

You can customize the processing with configuration options:

```python
from vidst.core.config import ProcessingConfig

# Create a custom configuration
config = ProcessingConfig(
    chunk_size=30,  # Process in 30-second chunks
    extract_audio=True,
    detect_scenes=True,
    extract_text=False,  # Skip OCR
    max_resolution=720  # Limit resolution for faster processing
)

# Initialize processor with custom config
processor = VideoProcessor(config=config)

# Process with custom configuration
result = processor.process("path/to/video.mp4")
```

### Processing Large Videos

For large videos, you can process in chunks:

```python
from vidst.core.processing import process_video_in_chunks

# Process a large video in 5-minute chunks
results = process_video_in_chunks("path/to/large_video.mp4", chunk_size=300)

# Combine results
all_scenes = []
for chunk_result in results:
    all_scenes.extend(chunk_result.scenes)
```

## Performance Considerations

- Processing time scales with video length and resolution
- OCR is the most computationally intensive component
- Consider using a GPU for faster processing
- Use caching to avoid reprocessing the same video

## Next Steps

- Explore the [Scene Detection](../components/scene_detection.md) component documentation
- Learn about Vector Storage for storing and searching video embeddings
- Check the [API Reference](../api/index.md) for detailed API information
