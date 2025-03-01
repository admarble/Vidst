# Setup Guide

## Overview

This guide covers the setup and configuration of the Video Understanding AI system.

## Prerequisites

- Python 3.10+
- Git LFS
- CUDA-compatible GPU (optional)
- API keys for:
  - OpenAI GPT-4V
  - Google Gemini Pro Vision
  - Twelve Labs
  - Whisper v3

## Installation

### Basic Setup

```bash
# Clone repository
git clone https://github.com/admarble/Vidst.git
cd Vidst

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### Environment Setup

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your API keys and configuration:

   ```
   # API Keys
   OPENAI_API_KEY=your_openai_api_key
   TWELVE_LABS_API_KEY=your_twelve_labs_api_key
   GEMINI_API_KEY=your_gemini_api_key

   # Storage Configuration
   VECTOR_STORAGE_PATH=./storage/vectors
   METADATA_STORAGE_PATH=./storage/metadata
   CACHE_STORAGE_PATH=./storage/cache

   # Processing Configuration
   MAX_VIDEO_LENGTH=600  # in seconds
   DEFAULT_CHUNK_SIZE=60  # in seconds
   ```

### Configuration File

For more advanced configuration, you can create a YAML configuration file:

```yaml
# config.yaml
storage:
  vector_path: ./storage/vectors
  metadata_path: ./storage/metadata
  cache_path: ./storage/cache

processing:
  max_video_length: 600
  default_chunk_size: 60

models:
  gpt4v:
    enabled: true
    api_key: ${OPENAI_API_KEY}
  twelve_labs:
    enabled: true
    api_key: ${TWELVE_LABS_API_KEY}
```

Load the configuration in your code:

```python
from vidst.core.config import load_config

config = load_config("config.yaml")
```

## Verification

To verify your installation:

```bash
# Run the verification script
python -m vidst.verify

# Run tests
pytest tests/
```

## Next Steps

After completing the setup:

1. Follow the [Quick Start Guide](./quickstart.md) to process your first video
2. Explore the [Component Documentation](../components/status_dashboard.md) to understand available features
3. Check the [API Reference](../api/index.md) for detailed API information
