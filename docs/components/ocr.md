# Optical Character Recognition (OCR)

**Status**: 📝 Planned

## Overview

The OCR component extracts text visible in video frames, enabling search and analysis of on-screen text.

## Implementation

This component is currently planned but not yet implemented. The planned implementation will:

- Use Google Document AI for primary OCR
- Include fallback to Tesseract OCR for offline processing
- Support multiple languages
- Include text position tracking

## Planned Usage

```python
from vidst.components import TextExtractor

# Initialize the extractor with your API key
extractor = TextExtractor(api_key="your_google_api_key")

# Extract text from a video
text_results = extractor.extract("path/to/video.mp4")

# Process extracted text
for result in text_results:
    print(f"Frame at {result.timestamp}: {result.text}")
    print(f"Position: {result.position}")
```

## Planned Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| api_key | string | None | Google Document AI API key |
| language | string | "en" | Language code for OCR |
| frame_interval | float | 1.0 | Seconds between processed frames |
| min_confidence | float | 0.7 | Minimum confidence score for text detection |

## Performance Targets

| Metric | Target |
|--------|--------|
| Accuracy | >80% |
| Processing Time | <1.5x video length |

## Integration Notes

When implemented, this component will integrate with:

- Scene Detection to provide context for extracted text
- Vector Storage to enable searching for videos containing specific text
- Natural Language Querying to allow questions about on-screen text

## Timeline

Implementation is planned for the next development phase, with an estimated completion time of 1 week.
