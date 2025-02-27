# Vidst - Video Understanding AI

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

### Guides

- `guides/models/gpt4v.md` - GPT-4V Model Usage Guide
- `guides/` - User guides and tutorials
- `development/` - Development documentation

### Technical Documentation

- `error_handling.md` - Error Handling and Recovery
- `cache.md` - Two-Level Cache System
- `video_upload.md` - Video Upload and Validation
- `setup.md` - Project Setup and Configuration

### API Reference

- `api/ai/models/gpt4v.html` - GPT-4V Model API Reference
- `api/` - Complete API documentation

## New API Integrations

The project now includes integrations with the following external APIs:

### Twelve Labs

[Twelve Labs](https://twelvelabs.io/) provides a state-of-the-art video understanding API that enhances our capabilities for:

- Scene detection and segmentation
- Visual content analysis
- Natural language video search

### Pinecone Vector Database

[Pinecone](https://www.pinecone.io/) is a vector database that replaces our local FAISS implementation, providing:

- Cloud-hosted vector storage
- Fast similarity search
- Scalable storage for embedding vectors

### Google Document AI

[Google Document AI](https://cloud.google.com/document-ai) enhances our text extraction capabilities with:

- Improved OCR accuracy
- Structured document parsing
- Code block extraction

### OpenAI Whisper

[OpenAI Whisper](https://github.com/openai/whisper) provides state-of-the-art speech recognition with:

- Multilingual support
- Robust noise handling
- Speaker diarization

## Configuration

Configuration templates for the new API integrations are located in:

```
src/video_understanding/core/config/templates/
```

To use these APIs, you'll need to:

1. Copy the template files to your local configuration
2. Add your API keys to your environment variables
3. Update your configuration files with your specific settings

For detailed setup instructions, see the [API Integration Guide](docs/api_integration_guide.md).

## Dependency Information

We've updated our dependencies to ensure better compatibility and reliability. Key changes include:

1. Updated Whisper package:
   - Now using `whisper>=20230918` instead of `openai-whisper`
   - Requires Python 3.8-3.11 (3.11 recommended)
   - Requires PyTorch dependencies: `torch>=2.0.0` and `torchaudio>=2.0.0`

2. Corrected Twelve Labs package:
   - Now using `twelvelabs>=0.2.0` (correct package name)

3. Updated Pinecone package:
   - Now using `pinecone>=2.2.4` instead of `pinecone-client`

4. Updated Google Document AI package:
   - Now using `google-cloud-documentai>=2.24.0`

For detailed compatibility information and usage examples, see [Package Compatibility](docs/package_compatibility.md).
