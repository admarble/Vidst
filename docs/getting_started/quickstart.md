# Quick Start Guide

This guide will help you get started with Vidst quickly for the POC demonstration.

## Basic Usage

After completing the [installation](installation.md), you can use Vidst to analyze videos:

```python
from vidst import VideoAnalyzer

# Initialize the analyzer
analyzer = VideoAnalyzer()

# Analyze a video file
results = analyzer.analyze("path/to/your/video.mp4")

# Access scene detection results
scenes = results.scenes
for scene in scenes:
    print(f"Scene from {scene.start_time}s to {scene.end_time}s")

# Access transcription results (if available)
if results.transcription:
    print(f"Transcription: {results.transcription}")
```

## Example Scripts

The repository includes example scripts to demonstrate key functionality:

```bash
# Run scene detection example
python examples/scene_detection_example.py --video path/to/video.mp4

# Run audio transcription example
python examples/transcription_example.py --video path/to/video.mp4
```

## Next Steps

- Check the [Component Status Dashboard](../components/status_dashboard.md) to see which features are available
- Explore the [Scene Detection](../components/scene_detection.md) documentation for more details
- Review the [Architecture Overview](../architecture/system_overview.md) to understand how Vidst works
