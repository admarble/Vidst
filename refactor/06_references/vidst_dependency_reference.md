# Vidst: Comprehensive Package Dependency Reference

This document provides a detailed reference for all dependencies used in the Vidst project, including their purpose, version requirements, and usage context.

## Dependency Management Strategy

The Vidst project uses a multi-tiered approach to dependency management:

1. **Core requirements** (`requirements.txt`): Essential dependencies needed for the basic functioning of the system
2. **Development requirements** (`requirements-dev.txt`): Additional dependencies needed for development
3. **Testing requirements** (`requirements-test.txt`): Dependencies specifically for testing

For production deployments, use `requirements.txt`. For development environments, install all three requirement sets.

```bash
# Production installation
pip install -r requirements.txt

# Development installation
pip install -r requirements.txt -r requirements-dev.txt -r requirements-test.txt
```

## Environment Compatibility

The dependency sets have been tested for compatibility on:
- Linux (Ubuntu 20.04+, CentOS 8+)
- macOS (Monterey 12.0+)
- Windows 10/11

Python version compatibility: 3.10 and higher (3.11 recommended for optimal performance)

## Core Dependencies

| Package | Version | Purpose | Essential | Notes |
|---------|---------|---------|-----------|-------|
| numpy | ≥1.24.0 | Numerical operations and data manipulation | ✅ | Required for array processing and mathematical operations |
| faiss-cpu | ≥1.7.4 | Vector storage and similarity search for embeddings | ✅ | For `faiss-gpu`, see performance optimization section |
| python-dotenv | ≥1.0.0 | Environment variable management for configuration | ✅ | Used for secure storage of API keys and configuration |
| pydantic | ≥2.0.0 | Data validation, settings management, and schema definition | ✅ | Core validation library; not compatible with older versions |
| loguru | ≥0.7.0 | Structured logging with improved formatting | ✅ | Replaces standard logging for better error traceability |

## AI/ML Dependencies

| Package | Version | Purpose | Essential | Notes |
|---------|---------|---------|-----------|-------|
| torch | ≥2.0.0 | Deep learning framework for AI model operations | ✅ | CUDA compatibility recommended for GPU acceleration |
| transformers | ≥4.30.0 | Transformer models for NLP tasks | ✅ | Used for text and multimodal processing |
| sentence-transformers | ≥2.2.0 | Text embeddings for similarity search | ✅ | Built on transformers; provides optimized text embeddings |
| ultralytics | ≥8.1.0 | Object detection using YOLOv8 | ✅ | Core vision detection functionality |
| google-generativeai | 0.4.0 | Client for Google's Gemini models | ❓ | Required only if using Gemini models |
| twelvelabs | 0.4.4 | Client for Twelve Labs video understanding API | ❓ | Required only if using Twelve Labs API |

## Video Processing

| Package | Version | Purpose | Essential | Notes |
|---------|---------|---------|-----------|-------|
| opencv-python | ≥4.8.0 | Video frame processing and computer vision operations | ✅ | Core video processing; use `opencv-python-headless` for servers |
| moviepy | ≥1.0.3 | High-level video editing and manipulation | ✅ | Used for video segmentation and transformation |
| ffmpeg-python | 0.2.0 | Python bindings for FFmpeg (video processing) | ✅ | Requires FFmpeg binary installation on the system |
| pytesseract | ≥0.3.10 | Optical Character Recognition (OCR) | ✅ | Requires Tesseract binary installation on the system |
| easyocr | ≥1.7.1 | Multilingual Optical Character Recognition | ❓ | Alternative to pytesseract with better multilingual support |

## Audio Processing

| Package | Version | Purpose | Essential | Notes |
|---------|---------|---------|-----------|-------|
| whisper | ≥1.1.10 | Speech recognition and transcription | ✅ | OpenAI's Whisper model for audio transcription |
| librosa | ≥0.10.0 | Audio analysis and processing | ✅ | Used for audio feature extraction and preprocessing |

## Storage and Database

| Package | Version | Purpose | Essential | Notes |
|---------|---------|---------|-----------|-------|
| redis | ≥5.0.0 | In-memory data structure store for caching | ✅ | Requires Redis server; use `redis-py` as fallback |
| sqlalchemy | ≥2.0.0 | SQL toolkit and Object-Relational Mapping | ✅ | Core database functionality; significant API changes from 1.x |
| alembic | 1.13.1 | Database migration tool for SQLAlchemy | ✅ | Used for schema migrations and version control |

## API and Web

| Package | Version | Purpose | Essential | Notes |
|---------|---------|---------|-----------|-------|
| fastapi | 0.110.0 | Modern, fast web framework for building APIs | ❓ | Required only if exposing API endpoints |
| uvicorn | 0.28.0 | ASGI server implementation | ❓ | Web server for FastAPI; required for API hosting |
| httpx | ≥0.24.0 | HTTP client with async support | ✅ | Used for all external API calls |

## Testing Dependencies

| Package | Version | Purpose | Essential for Development | Notes |
|---------|---------|---------|--------------------------|-------|
| pytest | 8.0.0 | Testing framework | ✅ | Core testing framework |
| pytest-cov | 4.1.0 | Test coverage reporting | ✅ | Generates coverage reports |
| pytest-asyncio | 0.23.5 | Async test support | ✅ | Required for testing async code |
| pytest-mock | 3.12.0 | Mock object testing | ✅ | Simplifies mocking |
| pytest-xdist | 3.5.0 | Parallel test execution | ❓ | Optional for performance improvement |
| pytest-timeout | 2.2.0 | Test timeout enforcement | ❓ | Prevents hanging tests |
| pytest-benchmark | 4.0.0 | Performance benchmarking | ❓ | Used for performance tests |
| pytest-fixture-config | 1.7.0 | Fixture configuration | ❓ | Advanced fixture management |
| pytest-env | 1.1.3 | Environment variable setting | ❓ | Controls test environments |
| coverage | 7.4.1 | Code coverage measurement | ✅ | Used by pytest-cov |
| hypothesis | 6.98.0 | Property-based testing | ❓ | For advanced test case generation |
| freezegun | 1.4.0 | Time-based testing | ❓ | For testing time-dependent code |
| requests-mock | 1.11.0 | Mock for requests library | ✅ | Essential for testing API clients |
| responses | 0.24.1 | Mock for HTTP requests | ❓ | Alternative to requests-mock |

## Documentation Dependencies

| Package | Version | Purpose | Essential for Development | Notes |
|---------|---------|---------|--------------------------|-------|
| sphinx | 7.2.6 | Documentation generator | ✅ | Core documentation tool |
| sphinx-rtd-theme | 2.0.0 | ReadTheDocs theme for Sphinx | ✅ | Improved documentation UI |
| sphinx-autodoc-typehints | 1.25.2 | Type hints support for Sphinx | ✅ | Enhances API docs with type information |
| myst-parser | 2.0.0 | Markdown support for Sphinx | ✅ | Allows writing docs in Markdown |
| mkdocs | 1.5.3 | Project documentation with Markdown | ❓ | Alternative to Sphinx for user guides |
| mkdocs-material | 9.5.9 | Material theme for MkDocs | ❓ | Required if using MkDocs |
| docstring-parser | 0.15 | Parse Python docstrings | ✅ | Enhances API documentation |
| pdoc | 14.4.0 | API documentation generator | ❓ | Alternative to Sphinx for simple API docs |

## Development Tools

| Package | Version | Purpose | Essential for Development | Notes |
|---------|---------|---------|--------------------------|-------|
| black | ≥23.7.0 | Code formatter | ✅ | Enforces consistent code style |
| isort | ≥5.12.0 | Import sorter | ✅ | Works in conjunction with Black |
| mypy | ≥1.4.0 | Static type checker | ✅ | Ensures type safety |
| pylint | ≥2.17.0 | Code analyzer | ✅ | Advanced code quality checks |
| flake8 | 7.0.0 | Code linter | ❓ | Partially replaced by ruff |
| ruff | N/A | Fast Python linter | ✅ | Configured in pyproject.toml |

## Utilities

| Package | Version | Purpose | Essential | Notes |
|---------|---------|---------|-----------|-------|
| python-magic | ≥0.4.27 | File type detection | ✅ | Used for upload validation |
| python-jose | 3.3.0 | JavaScript Object Signing and Encryption | ❓ | Required for JWT authentication |
| passlib | 1.7.4 | Password hashing | ❓ | Required for authentication |
| psutil | 5.9.8 | System resource monitoring | ❓ | Used for performance monitoring |
| backoff | ≥2.2.1 | Function retry decorator | ✅ | Essential for reliable API calls |
| aiohttp | ≥3.8.0 | Async HTTP client/server | ❓ | Alternative to httpx for specific use cases |
| requests | ≥2.31.0 | HTTP library | ✅ | Used for synchronous HTTP requests |
| typing-extensions | ≥4.5.0 | Backported typing features | ✅ | Enhances type hints in older Python versions |
| tenacity | 8.2.3 | Retrying operations | ❓ | Alternative to backoff with different features |

## Package Dependencies by Environment

### Minimal Installation (Basic Functionality)

For basic functionality with minimal dependencies, install:

```
numpy>=1.24.0
pydantic>=2.0.0
python-dotenv>=1.0.0
loguru>=0.7.0
httpx>=0.24.0
backoff>=2.2.1
typing-extensions>=4.5.0
```

### Production Installation

For production environments, install all essential packages:

```
# Core
numpy>=1.24.0
faiss-cpu>=1.7.4
python-dotenv>=1.0.0
pydantic>=2.0.0
loguru>=0.7.0

# AI/ML
torch>=2.0.0
transformers>=4.30.0
sentence-transformers>=2.2.0
ultralytics>=8.1.0

# Video Processing
opencv-python-headless>=4.8.0
moviepy>=1.0.3
ffmpeg-python==0.2.0
pytesseract>=0.3.10

# Audio Processing
whisper>=1.1.10
librosa>=0.10.0

# Storage
redis>=5.0.0
sqlalchemy>=2.0.0
alembic==1.13.1

# Utilities
httpx>=0.24.0
backoff>=2.2.1
python-magic>=0.4.27
requests>=2.31.0
typing-extensions>=4.5.0
```

### Development Installation

For development environments, install all packages including testing and documentation tools.

## AI Models Integration Details

The project integrates with several external AI model providers. Here are implementation details for each:

### 1. Google Generative AI (Gemini)

**Implementation File:** `src/video_understanding/ai/models/gemini.py`

**API Pattern:**
```python
from google import generativeai as genai
from PIL import Image

# Initialize API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro-vision')

# Process video frame
def analyze_video_frame(frame_image):
    response = model.generate_content([
        "Analyze this video frame and describe the key elements:",
        Image.fromarray(frame_image)
    ])
    return response.text
```

**Usage Context:**
- Scene content analysis
- Visual question answering
- Multi-modal reasoning tasks

### 2. OpenAI's GPT-4V

**Implementation File:** `src/video_understanding/ai/models/gpt4v.py`

**API Pattern:**
```python
import base64
import httpx
from io import BytesIO
from PIL import Image

# Process video frame with GPT-4V
async def analyze_frame_with_gpt4v(image, prompt):
    # Convert image to base64
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    # Construct API request
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                ]
            }
        ],
        "max_tokens": 300
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            timeout=30.0
        )
        return response.json()["choices"][0]["message"]["content"]
```

**Usage Context:**
- Detailed visual analysis
- Content description and summarization
- Visual reasoning tasks

### 3. Twelve Labs

**Implementation File:** `src/video_understanding/ai/models/twelve_labs.py`

**API Pattern:**
```python
from twelvelabs import Client

# Initialize client
client = Client(api_key=TWELVE_LABS_API_KEY)

# Index a video
def index_video(video_path):
    with open(video_path, "rb") as f:
        task = client.index.create(
            video=f,
            index_name="my_index",
            title="Video Title"
        )
    return task.id

# Search video by text
def search_video_by_text(index_id, query):
    results = client.search.query(
        index_id=index_id,
        search_options={"query": query, "search_type": "semantic"}
    )
    return results
```

**Usage Context:**
- Video indexing and search
- Temporal scene understanding
- Action recognition

### 4. Whisper

**Implementation File:** `src/video_understanding/ai/models/whisper.py`

**API Pattern:**
```python
import whisper

# Load model
model = whisper.load_model("medium")

# Transcribe audio
def transcribe_audio(audio_path):
    result = model.transcribe(audio_path)
    return result["text"]

# Transcribe with timestamp segments
def transcribe_with_timestamps(audio_path):
    result = model.transcribe(audio_path, word_timestamps=True)
    segments = result["segments"]
    return [
        {
            "text": segment["text"],
            "start": segment["start"],
            "end": segment["end"]
        }
        for segment in segments
    ]
```

**Usage Context:**
- Audio transcription
- Speech to text conversion
- Timestamp generation for video segments

### 5. YOLOv8 (via ultralytics)

**Implementation File:** `src/video_understanding/ai/models/object_detection.py`

**API Pattern:**
```python
from ultralytics import YOLO

# Load model
model = YOLO('yolov8n.pt')

# Detect objects in frame
def detect_objects(frame):
    results = model(frame)
    
    # Process results
    detections = []
    for result in results:
        for box in result.boxes:
            obj = {
                "class": model.names[int(box.cls)],
                "confidence": float(box.conf),
                "bbox": box.xyxy[0].tolist()
            }
            detections.append(obj)
    
    return detections
```

**Usage Context:**
- Object detection in video frames
- Scene classification based on detected objects
- Visual element tagging

## Performance Considerations

### CPU vs. GPU Dependencies

Some packages offer GPU acceleration for improved performance:

- **torch**: Use CUDA-enabled version for GPU acceleration
- **faiss-cpu** vs **faiss-gpu**: Choose based on hardware availability
- **ultralytics**: Automatically uses GPU if available
- **easyocr**: Benefits from GPU acceleration

### Memory Optimization

- For large video processing, consider:
  - Processing in smaller chunks
  - Using memory-mapped arrays with NumPy
  - Adjusting batch sizes for model inference

### Scaling Strategies

- Horizontal scaling for distributed processing
- Redis caching for shared results
- Load balancing for API endpoints
- Worker pools for parallel task processing

## Compatibility Notes

### Known Issues

- **opencv-python** and **opencv-python-headless** cannot be installed together
- **whisper** requires **ffmpeg** to be installed on the system
- **sentence-transformers** may have version conflicts with older **transformers** versions
- **pytesseract** requires the Tesseract OCR engine to be installed separately

### Version Conflicts

- **pydantic** v2.x has significant API changes from v1.x
- **sqlalchemy** v2.x has API changes from v1.x
- **transformers** may have compatibility issues with different torch versions

## References

- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/20/)
- [Twelve Labs API Reference](https://docs.twelvelabs.io/reference)
- [Ultralytics YOLOv8 Documentation](https://docs.ultralytics.com/)
- [Redis Documentation](https://redis.io/documentation)
- [Whisper GitHub Repository](https://github.com/openai/whisper)
- [Tesseract Documentation](https://tesseract-ocr.github.io/)
- [MoviePy Documentation](https://zulko.github.io/moviepy/)
- [FAISS Documentation](https://faiss.ai/index.html)

## Dependency Management Best Practices

### Security Considerations

- Regularly update dependencies to address security vulnerabilities
- Pin versions in production environments for stability
- Use tools like `pip-audit` to scan for security issues
- Consider using virtual environments with restricted permissions

### Optimization Strategies

- Use lightweight alternatives for resource-constrained environments:
  - **opencv-python-headless** instead of **opencv-python**
  - Smaller model variants (e.g., "tiny" or "base" for Whisper)
  - Consider CPU-only versions if GPU not available
- Profile memory usage during development

### Containerization

For containerized deployments:

- Include system dependencies in Dockerfile:
  ```dockerfile
  # Example Dockerfile snippet for system dependencies
  RUN apt-get update && apt-get install -y \
      ffmpeg \
      libsm6 \
      libxext6 \
      tesseract-ocr \
      && rm -rf /var/lib/apt/lists/*
  ```
- Consider multi-stage builds to reduce image size
- Use volume mounts for persistent data

## Conclusion

This document provides a comprehensive reference for the dependencies used in the Vidst project. By understanding the purpose, version requirements, and integration patterns for each package, developers can effectively work with and extend the system while maintaining compatibility and performance.

For further details on system architecture and implementation, refer to the [System Architecture Documentation](vidst_system_architecture.md).
