# Video Understanding AI

AI-powered video understanding and analysis system.

## Features

- Scene detection and analysis
- Audio transcription with speaker identification
- Text extraction from video frames
- Natural language querying of video content
- Multi-modal AI model integration

## Installation

```bash
pip install -e .
```

## Development

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e .
```

### Testing

```bash
# Run all checks
./scripts/check_pr.sh

# Run specific tests
pytest tests/unit/
pytest tests/integration/
```

## License

MIT License

## Documentation

- `error_handling.md` - Error Handling and Recovery
- `cache.md` - Two-Level Cache System
- `video_upload.md` - Video Upload and Validation
- `setup.md` - Project Setup and Configuration
- `guides/` - User guides and tutorials
- `development/` - Development documentation
