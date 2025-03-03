# API Documentation

This page provides an overview of the Vidst API components and their functionality.

## Core Components

The system is built around several core components:

### Technical Success Criteria

- **Metrics** - Comprehensive metrics tracking and validation
- **Logging** - Structured JSON logging system

### AI Integration

- **AI Models** - AI model implementations
- **Pipeline** - Model orchestration

### Storage and Caching

- **Vector Storage** - Vector storage for embeddings
- **Metadata** - Metadata management
- **Cache** - Caching layer

### Configuration and Processing

- **Config** - System configuration
- **Input** - Input handling
- **Output** - Output formatting
- **Processing** - Processing pipeline
- **Exceptions** - Error handling

## API Structure

The API is organized into the following modules:

```
vidst/
├── core/
│   ├── config.py       # Configuration management
│   ├── input.py        # Input handling
│   ├── output.py       # Output formatting
│   ├── processing.py   # Processing pipeline
│   └── exceptions.py   # Error handling
├── ai/
│   ├── models/         # AI model implementations
│   │   ├── base.py     # Base model interface
│   │   ├── gpt4v.py    # GPT-4V implementation
│   │   └── twelve_labs.py # Twelve Labs implementation
│   └── pipeline.py     # Model orchestration
└── storage/
    ├── vector.py       # Vector storage
    ├── metadata.py     # Metadata management
    └── cache.py        # Caching layer
```

## Key Interfaces

### Video Processing

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

### AI Models

```python
from vidst.ai.models.gpt4v import GPT4VisionModel

# Initialize the model
model = GPT4VisionModel(api_key="your_api_key")

# Process a frame
result = model.analyze_frame("path/to/frame.jpg", prompt="Describe this scene")
```

### Vector Storage

```python
from vidst.storage.vector import VectorStorage

# Initialize the storage
storage = VectorStorage()

# Store an embedding
storage.store_embedding("video_id", embedding, metadata={"timestamp": 10.5})

# Search for similar embeddings
results = storage.search_similar(query_embedding, limit=5)
```

## Note on API Stability

**Status**: 🔄 In Progress

The API is still under development and may change in future releases. For the POC, focus on the core functionality demonstrated in the examples above.
