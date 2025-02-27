# GPT-4V Model Guide

## Overview

The GPT-4V model is a powerful vision-language model that enables analysis of visual content in videos. It leverages OpenAI's GPT-4V API to provide detailed descriptions, identify objects, extract text, and understand actions in video frames.

## Features

- Scene analysis and description
- Object detection and identification
- Text extraction from frames
- Action recognition
- Natural language querying of visual content

## Configuration

The model can be configured through the `GPT4VConfig` class:

```python
from video_understanding.ai.models.gpt4v import GPT4VModel, GPT4VConfig

config = {
    "api_key": "your-openai-api-key",
    "api_base": "https://api.openai.com/v1",  # Optional
    "model": "gpt-4-vision-preview",          # Optional
    "max_tokens": 300,                        # Optional
    "temperature": 0.7                        # Optional
}

model = GPT4VModel(config)
```

## Usage Examples

### Basic Frame Analysis

```python
# Analyze a single frame
result = await model.process({
    "image_url": "path/to/frame.jpg",
    "prompt": "Describe what is happening in this frame."
})

print(result["analysis"])  # Detailed description
print(result["model"])     # Model used
print(result["usage"])     # Token usage stats
```

### Object Detection

```python
# Detect objects in frame
result = await model.process({
    "image_url": "path/to/frame.jpg",
    "prompt": "List all visible objects in this frame."
})
```

### Text Extraction

```python
# Extract text from frame
result = await model.process({
    "image_url": "path/to/frame.jpg",
    "prompt": "Extract and list all visible text in this frame."
})
```

### Action Recognition

```python
# Identify actions
result = await model.process({
    "image_url": "path/to/frame.jpg",
    "prompt": "What actions are being performed in this frame?"
})
```

## Error Handling

The model implements robust error handling:

```python
from video_understanding.ai.exceptions import ValidationError, APIError

try:
    result = await model.process(input_data)
except ValidationError as e:
    print(f"Invalid input: {e}")
except APIError as e:
    print(f"API error: {e}")
finally:
    await model.close()  # Always clean up resources
```

## Best Practices

1. **Resource Management**
   - Always use the model in an async context manager or call `close()` when done
   - Process frames in batches when possible
   - Implement proper error handling and retries

2. **Input Validation**
   - Ensure image URLs are accessible
   - Keep prompts clear and specific
   - Validate input data before processing

3. **Performance Optimization**
   - Cache results when appropriate
   - Use appropriate batch sizes
   - Monitor token usage

4. **Error Handling**
   - Implement retries for transient failures
   - Handle rate limits appropriately
   - Log errors for debugging

## Integration Examples

### With Video Processing Pipeline

```python
async def process_video_frame(frame_path: str, model: GPT4VModel) -> dict:
    """Process a single video frame."""
    try:
        result = await model.process({
            "image_url": frame_path,
            "prompt": "Analyze this frame for key objects and actions."
        })
        return result
    except Exception as e:
        logger.error(f"Frame processing failed: {e}")
        raise
```

### With Batch Processing

```python
async def process_frame_batch(
    frame_paths: list[str],
    model: GPT4VModel
) -> list[dict]:
    """Process a batch of frames."""
    results = []
    for frame_path in frame_paths:
        result = await model.process({
            "image_url": frame_path,
            "prompt": "Analyze this frame."
        })
        results.append(result)
    return results
```

## Troubleshooting

Common issues and solutions:

1. **Rate Limiting**
   - Implement exponential backoff
   - Use the retry mechanism
   - Monitor API usage

2. **Memory Usage**
   - Process frames in smaller batches
   - Clean up resources promptly
   - Monitor memory consumption

3. **API Errors**
   - Check API key validity
   - Verify input data format
   - Monitor API status

## API Reference

For detailed API documentation, see the [GPT-4V API Reference](../api/ai/models/gpt4v.html).
