# Vidst Refactoring - General Rules

## When to apply
@semantics Applies to general refactoring tasks, architecture changes, and any file modifications within the src directory.
@files src/**/*.py

## Context

This rule provides guidance for the Vidst refactoring project, focusing on transitioning from a complex custom implementation to a streamlined API-centric approach.

## Architecture Overview

The refactored architecture consolidates around a smaller set of managed API services with clear abstraction layers:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  Video Upload   │─────▶│ Core Processing │─────▶│ API Gateway     │
│                 │      │                 │      │                 │
└─────────────────┘      └────────┬────────┘      └─────────────────┘
                                  │                        ▲
                                  ▼                        │
┌─────────────────┐      ┌───────┴───────┐      ┌─────────┴─────────┐
│                 │      │               │      │                   │
│  Twelve Labs    │◀────▶│ Integration   │─────▶│ Pinecone Vector   │
│  Video API      │      │ Layer         │      │ Database API      │
│                 │      │               │      │                   │
└─────────────────┘      └───────────────┘      └───────────────────┘
        ▲                        │                        ▲
        │                        ▼                        │
┌───────┴─────────┐      ┌───────────────┐      ┌────────┴──────────┐
│                 │      │               │      │                    │
│  Google         │      │ Query         │      │ Local              │
│  Document AI    │◀────▶│ Processor     │─────▶│ Components         │
│                 │      │               │      │ (Whisper, Redis)   │
└─────────────────┘      └───────────────┘      └────────────────────┘
```

## File Structure Guidelines

### Key Structure Changes

1. New abstraction directories for specific functionalities:
   - `ai/ocr/`
   - `ai/transcription/`
   - `ai/scene/`

2. New factory patterns for dynamic selection:
   - `ai/factory.py`
   - `storage/vector/factory.py`
   - `core/config/factory.py`

3. New API integration files:
   - `storage/vector/pinecone.py`
   - `ai/models/document_ai.py`

### Interface Pattern

All components should use interfaces and factories:

```python
# Base interface
class BaseVectorStorage:
    def add_vectors(self):
        raise NotImplementedError
        
    def search(self):
        raise NotImplementedError

# Factory
class VectorStorageFactory:
    @staticmethod
    def create(config):
        if isinstance(config, FAISSConfig):
            return FAISSVectorStorage(config)
        elif isinstance(config, PineconeConfig):
            return PineconeVectorStorage(config)
```

## Coding Standards

1. **Python Standards**
   - Python 3.10+
   - Type hints for all functions
   - Black formatter (88 char line length)
   - Docstrings for all public methods

2. **Error Handling**
   - Use custom exceptions
   - Implement circuit breakers for APIs
   - Implement retry patterns
   - Add comprehensive error logging

3. **Dependency Management**
   - Add new API dependencies:
     - `pinecone-client>=2.2.1`
     - `google-cloud-documentai>=2.20.0`
     - `twelvelabs>=0.5.0`
   - Remove deprecated dependencies:
     - `faiss-cpu>=1.7.4`
     - `pytesseract>=0.3.10`
     - `easyocr>=1.7.1`

## Refactoring Priorities

1. Replace higher priority components first:
   - Scene Detection (Twelve Labs)
   - Vector Storage (Pinecone)
   - OCR (Google Document AI)

2. Phase later or keep current:
   - Object Detection
   - File Storage
   - Caching
   - Video Processing

## Implementation Patterns

1. **Circuit Breaker Pattern**

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.is_open = False
        self.last_failure_time = 0
        
    async def execute(self, func, *args, **kwargs):
        # Circuit breaker implementation
        pass
```

2. **Service with Fallback**

```python
class OCRService:
    def __init__(self, primary_service, fallback_service=None):
        self.primary = primary_service
        self.fallback = fallback_service
        self.circuit_breaker = CircuitBreaker()
        
    async def extract_text(self, image):
        try:
            return await self.circuit_breaker.execute(
                self.primary.extract_text, image
            )
        except (OCRError, CircuitBreakerOpenError) as e:
            if self.fallback:
                return await self.fallback.extract_text(image)
            raise OCRError(f"OCR failed with no fallback: {str(e)}")
```

## Migration Steps

For each component migration:

1. Implement base interface
2. Create API integration
3. Create factory
4. Update core pipeline
5. Update tests
6. Run migrations for data

## Success Metrics

- Scene Detection Accuracy: >90%
- OCR Accuracy: >95%
- Speech Transcription Accuracy: >95%
- Processing Speed: Maximum 2x video duration
- Query Response Time: <2 seconds
