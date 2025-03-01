# Audio Transcription

**Status**: 🔄 In Progress

## Overview

The Audio Transcription component extracts speech from videos and converts it to text using a combination of Whisper and Twelve Labs APIs.

## Implementation

- Uses OpenAI Whisper for primary transcription
- Twelve Labs API as a fallback option
- Supports multiple languages
- Includes speaker diarization (experimental)

## Usage

```python
from vidst.components import AudioTranscriber

# Initialize the transcriber with your API key
transcriber = AudioTranscriber(api_key="your_whisper_api_key")

# Transcribe audio from a video
transcript = transcriber.transcribe("path/to/video.mp4")

# Process transcript segments
for segment in transcript.segments:
    print(f"[{segment.start_time} - {segment.end_time}] {segment.text}")

# Get full transcript text
full_text = transcript.text
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| api_key | string | None | Whisper API key |
| language | string | "en" | Language code for transcription |
| enable_diarization | bool | False | Enable speaker diarization |
| fallback_to_twelve_labs | bool | True | Use Twelve Labs as fallback |

## Performance Metrics

| Metric | Target | Current Status |
|--------|--------|----------------|
| Accuracy | >85% | 82% |
| Processing Time | <0.5x video length | 0.7x video length |

## Known Limitations

- Speaker diarization is experimental and may not be accurate
- Performance degrades with background noise
- Some accents may not be recognized correctly

## Future Plans

- Improve accuracy with custom fine-tuning
- Optimize processing time
- Enhance speaker diarization
