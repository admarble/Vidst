# Package Compatibility Matrix

This document outlines the recommended package versions and compatibility information for the Vidst project.

## Core Packages

| Package | Recommended Version | Python Compatibility | Notes |
|---------|--------------------|--------------------|-------|
| whisper | 20230918 or newer | Python 3.8-3.11 | Python 3.11 recommended for best performance |
| torch | 2.0.0 or newer | Python 3.8+ | Required for Whisper |
| torchaudio | 2.0.0 or newer | Python 3.8+ | Required for audio processing with Whisper |
| twelvelabs | 0.2.0 or newer | Python 3.7+ | For video understanding API integration |
| pinecone | 2.2.4 or newer | Python 3.6+ | For vector database storage |
| google-cloud-documentai | 2.24.0 or newer | Python 3.8+ | For document AI integration |

## GPU Support

Using GPU acceleration requires:

- NVIDIA GPU with CUDA support
- Appropriate CUDA toolkit installed
- Compatible PyTorch version

## Package Usage Examples

### Whisper

```python
import whisper

# Load model
model = whisper.load_model("base")  # Options: tiny, base, small, medium, large

# Transcribe audio
result = model.transcribe("path/to/audio.mp3")
print(result["text"])
```

### Twelve Labs

```python
from twelvelabs import TwelveLabs

# Initialize client
client = TwelveLabs(api_key="YOUR_API_KEY")

# Index operations
indexes = client.indexes.list()

# Search operations (example)
search_results = client.search.query(
    index_id="your_index_id",
    query_text="people discussing AI concepts"
)
```

### Pinecone

```python
import pinecone

# Initialize
pinecone.init(api_key="YOUR_API_KEY", environment="YOUR_ENVIRONMENT")

# Create or connect to index
index = pinecone.Index("index-name")

# Upsert vectors
index.upsert(vectors=[("id1", [0.1, 0.2, 0.3], {"metadata": "value"})])

# Query vectors
results = index.query(vector=[0.1, 0.2, 0.3], top_k=10)
```

### Google Document AI

```python
from google.api_core.client_options import ClientOptions
from google.cloud import documentai

# Setup client
location = "us-central1"
opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
client = documentai.DocumentProcessorServiceClient(client_options=opts)

# Create document processor
project_id = "your-project-id"
processor_id = "your-processor-id"
parent = client.common_location_path(project_id, location)
processor_name = f"{parent}/processors/{processor_id}"
processor = client.get_processor(name=processor_name)

# Process document
with open("document.pdf", "rb") as file:
    content = file.read()
document = {"content": content, "mime_type": "application/pdf"}
request = {"name": processor_name, "document": document}
result = client.process_document(request=request)
```

## Troubleshooting Common Issues

### Whisper Installation Issues

If you encounter issues with Whisper installation:

1. Ensure you have the correct PyTorch version installed:

   ```bash
   pip install torch>=2.0.0 torchaudio>=2.0.0
   ```

2. Make sure ffmpeg is installed:

   ```bash
   # On Ubuntu/Debian
   sudo apt-get install ffmpeg

   # On macOS with Homebrew
   brew install ffmpeg

   # On Windows with Chocolatey
   choco install ffmpeg
   ```

### Pinecone Connection Issues

If you encounter issues connecting to Pinecone:

1. Check your API key and environment are correct
2. Ensure you're using the newest client version
3. Check if you're hitting rate limits
4. Verify your network can reach Pinecone servers

### GPU Acceleration Issues

If GPU acceleration is not working:

1. Verify NVIDIA drivers are installed: `nvidia-smi`
2. Check PyTorch can see your GPU: `python -c "import torch; print(torch.cuda.is_available())"`
3. Ensure CUDA versions are compatible with PyTorch version
