# Vidst: Video Understanding AI System Documentation

## Project Overview

Vidst is an AI-powered video understanding and analysis system designed to extract, analyze, and make accessible the content of videos through a combination of advanced AI techniques. The system processes videos to identify scenes, transcribe audio, extract text from frames, detect objects, and enable natural language querying of video content.

## System Architecture

### Architecture Diagram

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  Video Upload   │─────▶│ Core Processing │─────▶│ Storage Layer   │
│                 │      │                 │      │                 │
└─────────────────┘      └────────┬────────┘      └─────────────────┘
                                  │                        ▲
                                  ▼                        │
┌─────────────────┐      ┌─────────────────┐      ┌───────┴─────────┐
│                 │      │                 │      │                 │
│  AI Models      │◀────▶│ Video Analysis  │─────▶│ Metadata Index  │
│  Integration    │      │ Pipeline        │      │                 │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        ▲                                                 │
        │                                                 ▼
┌───────┴─────────┐                              ┌─────────────────┐
│  External AI    │                              │                 │
│  Services       │                              │ Query Interface │
│  - GPT-4V       │                              │                 │
│  - Gemini       │◀─────────────────────────────┤ (API/Web)       │
│  - Twelve Labs  │                              │                 │
│  - Whisper      │                              │                 │
└─────────────────┘                              └─────────────────┘
```

### Data Flow

1. **Video Ingestion**: Videos are uploaded, validated for format/security, and preprocessed
2. **Processing Pipeline**: Videos are processed through a series of analysis steps:
   - Frame extraction and scene detection
   - Visual analysis (object detection, scene classification)
   - Audio extraction and transcription
   - Text extraction via OCR
3. **AI Analysis**: Multiple AI models process the extracted data:
   - Visual content analyzed by GPT-4V and Gemini
   - Video understanding enhanced by Twelve Labs API
   - Audio transcribed by Whisper
4. **Metadata Storage**: Analysis results stored in structured database and vector storage
5. **Querying**: Natural language queries processed against metadata and vector indexes

### System Components

The Vidst system is organized into the following key components:

1. **AI Models Integration**
   - Integration with multiple AI providers for different analysis tasks
   - Model-specific error handling and configuration
   - API client implementations with retry mechanisms
   - Rate limiting and quota management

2. **Core Processing**
   - Video processing pipeline
   - Scene detection and analysis
   - Input/output handling
   - Configuration management
   - Task scheduling and monitoring

3. **Storage**
   - Metadata storage (SQL database via SQLAlchemy)
   - Vector storage for similarity search (FAISS)
   - Caching mechanisms (Redis)
   - File storage for video assets

4. **Video Processing**
   - Frame extraction and analysis
   - Metadata generation
   - Upload handling and validation
   - Format conversion and optimization

5. **Utilities**
   - Common helper functions
   - Exception handling
   - Logging and monitoring
   - Security utilities

## Project Structure

```
src/
├── video_understanding/
│   ├── ai/
│   │   ├── models/              # AI model integrations
│   │   │   ├── base.py          # Base model interface
│   │   │   ├── gemini.py        # Google Gemini implementation
│   │   │   ├── gpt4v.py         # OpenAI GPT-4V implementation
│   │   │   ├── twelve_labs.py   # Twelve Labs implementation
│   │   │   └── whisper.py       # Whisper implementation
│   │   ├── exceptions/          # Model-specific error handling
│   │   └── pipeline.py          # AI processing pipeline
│   ├── core/
│   │   ├── config/              # Configuration management
│   │   ├── processing/          # Core processing logic
│   │   │   ├── pipeline.py      # Processing pipeline
│   │   │   └── video.py         # Video processing
│   │   ├── upload/              # Upload handling
│   │   │   ├── security.py      # Security validation
│   │   │   ├── integrity.py     # File integrity
│   │   │   └── processor.py     # Upload processing
│   │   └── scene.py             # Scene detection and management
│   ├── models/                  # Data models for scenes and videos
│   │   ├── scene.py             # Scene data models
│   │   └── video.py             # Video data models
│   ├── storage/
│   │   ├── cache/               # Caching mechanisms
│   │   ├── metadata/            # Metadata storage
│   │   └── vector/              # Vector storage for similarity search
│   │       ├── storage.py       # FAISS implementation
│   │       └── utils.py         # Vector utilities
│   ├── utils/                   # Utility functions
│   │   ├── constants.py         # System constants
│   │   └── exceptions.py        # Exception handling
│   └── video/                   # Video processing
│       ├── metadata.py          # Video metadata extraction
│       ├── processor.py         # Video processing
│       ├── status.py            # Processing status tracking
│       ├── upload.py            # Upload handling
│       └── validator.py         # Video validation
```

## System Requirements

### Hardware Requirements

- **CPU**: 4+ cores recommended for parallel processing
- **RAM**: Minimum 8GB, 16GB+ recommended for processing larger videos
- **Storage**: SSD recommended for better I/O performance
- **GPU**: Optional but recommended for faster AI model inference
- **Network**: High-speed internet connection for external AI API calls

### Software Requirements

- **Operating System**: Linux (recommended), macOS, or Windows
- **Python Version**: 3.10 or higher
- **Additional Software**:
  - FFmpeg for video processing
  - Redis server for caching
  - PostgreSQL or similar for database storage

## Technical Stack

### Build System and Configuration

The project uses the following build system and configuration tools:

- **Python Version**: 3.10 or higher
- **Build System**: Hatchling (modern Python build backend)
- **Dependency Management**: pip with requirements.txt
- **Environment Management**: Python virtual environments

### Development Tools

The project employs the following development tools to ensure code quality:

- **Code Formatting**:
  - Black (line length: 88)
  - isort (profile: black)

- **Linting and Static Analysis**:
  - Ruff (comprehensive Python linter)
  - Mypy (static type checking)
  - Pylint (code analysis)

- **Testing**:
  - pytest (test framework)
  - pytest-cov (coverage reporting)
  - pytest-asyncio (for async tests)
  - pytest-benchmark (for performance testing)

- **Documentation**:
  - Sphinx (API documentation)
  - MkDocs with Material theme (user guides)
  - docstring-parser, pdoc (API generation)

## Error Handling and Recovery

The system implements multiple error handling strategies to ensure robustness:

1. **Graceful Degradation**
   - If one AI model fails, the system falls back to alternatives
   - Essential features continue to work even if enhanced features fail

2. **Retry Mechanisms**
   - API calls use exponential backoff via the backoff library
   - Failed processing tasks are automatically retried with configurable limits

3. **Comprehensive Logging**
   - All errors are logged with context using loguru
   - Error traceability across the processing pipeline

4. **Error Classification**
   - Transient errors (network, temporary API issues) handled differently from permanent errors
   - User errors (invalid formats, etc.) separated from system errors

5. **Recovery Processes**
   - Automatic recovery for interrupted video processing
   - Processing state persistence for resuming after system restarts

## Security Measures

The system implements several security measures:

1. **Upload Validation**
   - File type verification using python-magic
   - Size limits and format restrictions
   - Malware scanning capabilities

2. **Authentication and Authorization**
   - JWT-based authentication using python-jose
   - Role-based access controls
   - API key management for external services

3. **Data Protection**
   - Encryption of sensitive data
   - Secure storage of API credentials using environment variables
   - Option for encrypted storage of video content

4. **Input Validation**
   - All user inputs validated via Pydantic models
   - Query sanitization to prevent injection attacks
   - Strict type checking throughout the application

## Performance Optimization

The system is optimized for performance in several ways:

1. **Two-Level Caching**
   - In-memory caching for frequent operations
   - Redis-based distributed caching for shared resources
   - Cached results from expensive AI operations

2. **Parallel Processing**
   - Multi-threading for I/O-bound operations
   - Process pools for CPU-intensive tasks
   - Asynchronous programming for API calls

3. **Resource Management**
   - Configurable resource limits for system protection
   - Graceful handling of resource exhaustion
   - Memory-efficient processing of large videos

4. **Optimized Storage**
   - FAISS for high-performance vector similarity search
   - Database indexing strategies for fast querying
   - Efficient metadata storage design

## Key Features and Functionality

### 1. Scene Detection and Analysis

The system can analyze videos to:
- Detect scene changes using OpenCV
- Extract key frames that represent scene content
- Identify visual elements within scenes using YOLOv8
- Group related scenes based on visual similarity
- Generate scene summaries using AI models

### 2. Audio Transcription

The system processes audio in videos to:
- Transcribe speech to text using Whisper
- Identify different speakers through voice patterns
- Link transcriptions to specific timestamps
- Extract keywords and topics from spoken content
- Support multiple languages for transcription

### 3. Text Extraction from Frames

The system can:
- Detect text within video frames using OpenCV
- Extract and process the text using OCR (pytesseract/easyocr)
- Make text content searchable via vector embeddings
- Support multiple languages for text recognition
- Correlate text with visual elements and scenes

### 4. Natural Language Querying

Users can:
- Ask questions about video content in natural language
- Search for specific moments or information
- Get summaries of video content at different levels of detail
- Filter and sort results based on relevance
- Get contextual snippets around matched content

### 5. Multi-Modal AI Integration

The system leverages multiple AI models:
- GPT-4V for visual understanding and natural language reasoning
- Gemini for multimodal analysis combining text and visuals
- Twelve Labs for specialized video understanding
- Whisper for speech recognition and transcription
- YOLOv8 for object detection and classification

## Deployment Options

The system supports multiple deployment configurations:

1. **Development Setup**
   - Local installation for development and testing
   - Docker containers for isolated development
   - Mock services for offline development

2. **Single-Server Deployment**
   - All components on a single server for simple deployments
   - Suitable for moderate workloads
   - Simplified configuration and management

3. **Distributed Deployment**
   - Separate services for processing, storage, and API
   - Horizontal scaling for high-demand components
   - Load balancing across multiple instances

4. **Cloud Integration**
   - Integration with cloud storage services
   - Serverless functions for scaling specific components
   - Managed databases for simplified operations

## Development Workflow

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

## Limitations and Future Work

### Current Limitations

- Processing very large videos (>1 hour) may require significant resources
- English language processing is more advanced than other languages
- Relies on external API services that may have usage quotas
- Complex visual scenes with multiple activities can be challenging to analyze
- Real-time processing is not currently supported

### Planned Enhancements

- Real-time video analysis capabilities
- Enhanced multilingual support
- On-premise AI model options to reduce API dependencies
- Improved handling of long-form video content
- Advanced search and filtering capabilities
- User feedback integration to improve model performance
- Additional visualization options for analysis results

## Conclusion

Vidst provides a comprehensive system for video understanding and analysis, combining multiple AI models and technologies to extract insights from video content. The project is built with best practices in mind, including strong typing, extensive testing, and comprehensive documentation.

The modular architecture allows for easy extension and maintenance, while the use of modern libraries ensures high performance and reliability. The system is designed to handle various aspects of video analysis, from scene detection to natural language querying, making it a powerful tool for video content analysis and understanding.

*For detailed information about the project dependencies, refer to the [Dependency Reference](vidst_dependency_reference.md) document.*
