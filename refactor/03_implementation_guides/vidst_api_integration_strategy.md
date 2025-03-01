# Vidst API Integration Strategy

## Document Status

| Version | Date | Author | Status |
|---------|------|--------|--------|
| 1.1 | February 27, 2025 | Vidst Team | Draft |

**Related Documents:**
- [Vidst Refactoring Master Plan](./vidst_refactoring_master_plan.md)
- [Vidst Architecture Transition](./vidst_architecture_transition.md)
- [Vidst Implementation Timeline](./vidst_implementation_timeline.md)
- [Vidst Twelve Labs Integration Strategy](./vidst_twelve_labs_integration_strategy.md)
- [Vidst Vector DB API Integration](./vidst_vector_db_api_integration.md)

## 1. Introduction

This document outlines the strategic approach for integrating managed API services to replace complex custom implementations in the Vidst project. It focuses on the integration patterns, data flows, and coordination between multiple API services, rather than duplicating the detailed implementation guidance provided in service-specific documents.

## 2. API Ecosystem Overview

The refactored Vidst architecture will leverage a coordinated ecosystem of API services:

### 2.1 Primary API Services

1. **Twelve Labs Video Understanding API**
   - Primary service for video understanding and analysis
   - Provides scene detection, video indexing, and semantic search
   - Detailed implementation in [Vidst Twelve Labs Integration Strategy](./vidst_twelve_labs_integration_strategy.md)

2. **Pinecone Vector Database API**
   - Managed vector database for similarity search
   - Replaces self-hosted FAISS implementation
   - Detailed implementation in [Vidst Vector DB API Integration](./vidst_vector_db_api_integration.md)

3. **Google Document AI**
   - OCR and document understanding for text extraction
   - Replaces pytesseract/easyocr implementations

### 2.2 API Integration Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    Vidst Application Layer                        │
└───────────────┬────────────────────┬────────────────┬────────────┘
                │                    │                │
                ▼                    ▼                ▼
┌───────────────────┐    ┌────────────────────┐    ┌───────────────┐
│   Twelve Labs     │    │     Pinecone       │    │  Google       │
│   Video API       │    │     Vector DB      │    │  Document AI  │
└─────────┬─────────┘    └──────────┬─────────┘    └───────┬───────┘
          │                         │                      │
          │                         │                      │
          ▼                         ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    Retained Local Components                    │
│     (Whisper Transcription, Redis Caching, ffmpeg Pipeline)     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 3. API Integration Patterns

### 3.1 Simplified API Client Architecture

The refactoring will implement a minimal API client architecture with the following components:

1. **Basic Service Interfaces**: Minimal interfaces defining core functionality
2. **Direct API Implementations**: Straightforward implementations with minimal abstraction
3. **Simple Configuration**: Basic configuration for API credentials
4. **Essential Error Handling**: Focused on critical errors and basic retries

### 3.2 Data Flow Patterns

The system will implement these primary data flow patterns:

#### 3.2.1 Video Processing Flow

```
┌─────────┐     ┌───────────┐     ┌──────────────┐     ┌──────────────┐
│  Video  │────▶│  Extract  │────▶│ Twelve Labs  │────▶│   Pinecone   │
│  Input  │     │  Frames   │     │  Processing  │     │  Indexing    │
└─────────┘     └───────────┘     └──────────────┘     └──────────────┘
                      │                   │                   │
                      ▼                   │                   │
              ┌───────────────┐           │                   │
              │ Document AI   │           │                   │
              │  (OCR)        │           │                   │
              └───────┬───────┘           │                   │
                      │                   │                   │
                      ▼                   ▼                   ▼
              ┌──────────────────────────────────────────────────┐
              │                                                  │
              │           Metadata & Vector Database             │
              │                                                  │
              └─────────────────────────┬────────────────────────┘
                                        │
                                        ▼
                              ┌───────────────────┐
                              │  Query Interface  │
                              └───────────────────┘
```

#### 3.2.2 Query Processing Flow

```
┌─────────────┐     ┌────────────────┐     ┌───────────────┐
│  User       │────▶│  Query         │────▶│  Pinecone     │
│  Query      │     │  Processing    │     │  Semantic     │
└─────────────┘     └────────────────┘     │  Search       │
                            │              └───────┬───────┘
                            │                      │
                            ▼                      │
                    ┌───────────────┐              │
                    │ Twelve Labs   │              │
                    │ Semantic      │              │
                    │ Search        │              │
                    └───────┬───────┘              │
                            │                      │
                            │                      │
                            ▼                      ▼
                    ┌───────────────────────────────────┐
                    │                                   │
                    │   Federated Results Processing    │
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │ User Response │
                              └───────────────┘
```

### 3.3 Service Coordination

The API services will be coordinated through:

1. **Sequential Processing**: Video uploaded → Twelve Labs processing → Vector indexing
2. **Parallel Processing**: OCR processed in parallel with video indexing
3. **Federated Search**: Queries processed across both Twelve Labs and Pinecone
4. **Result Consolidation**: Combined results from multiple services

## 4. API Integration Approach

### 4.1 Common Integration Components

All API integrations will implement:

1. **Consistent Error Handling**
   - Standard error types and mapping
   - Basic retry mechanisms
   - Simple error logging and reporting

2. **Performance Monitoring**
   - Basic latency tracking for API calls
   - Usage tracking for cost management
   - Simple performance metrics

3. **Security Best Practices**
   - Secure credential management
   - Basic request/response validation

4. **Caching Strategies**
   - Response caching for frequent operations
   - Simple invalidation approach

### 4.2 API-Specific Integration Approach

#### 4.2.1 Twelve Labs Integration 

**Core Capabilities to Leverage:**
- Scene detection (94.2% accuracy, exceeding 90% target)
- Video indexing for search
- Semantic search (92.3% accuracy, exceeding 85% target)

**Integration Approach:**
- Replace custom scene detection with Twelve Labs API
- Use for natural language querying
- Detailed implementation in [Vidst Twelve Labs Integration Strategy](./vidst_twelve_labs_integration_strategy.md)

#### 4.2.2 Pinecone Integration

**Core Capabilities to Leverage:**
- Vector similarity search
- Metadata filtering capabilities
- Serverless infrastructure

**Integration Approach:**
- Replace self-hosted FAISS with Pinecone API
- Integrate with Twelve Labs embeddings
- Detailed implementation in [Vidst Vector DB API Integration](./vidst_vector_db_api_integration.md)

#### 4.2.3 Google Document AI Integration

**Core Capabilities to Leverage:**
- High-accuracy OCR (expected >95% accuracy)
- Structured document understanding
- Multilingual support

**Integration Approach:**
- Replace pytesseract/easyocr with Document AI
- Process key frames for text extraction
- Store extracted text as searchable metadata

## 5. Fallback Strategies

To ensure system reliability, each API integration will implement fallback mechanisms:

### 5.1 Service-Level Fallbacks

1. **Twelve Labs**
   - Primary: Twelve Labs Marengo/Pegasus
   - Fallback: Local OpenCV-based scene detection
   - Trigger: Service timeout or error after 3 retries

2. **Pinecone**
   - Primary: Pinecone serverless
   - Fallback: Local FAISS implementation
   - Trigger: Service unavailable or latency >500ms

3. **Document AI**
   - Primary: Google Document AI
   - Fallback: Local easyocr implementation
   - Trigger: Service error or quota exceeded

### 5.2 Simplified Fallback Implementation

```python
# Simpler fallback implementation pattern
class OCRService:
    def __init__(self, primary_service, fallback_service=None):
        self.primary = primary_service
        self.fallback = fallback_service
        
    async def extract_text(self, image):
        try:
            # Try primary service with basic retry
            return await retry(3, self.primary.extract_text, image)
        except ServiceError:
            if self.fallback:
                logger.warning("Falling back to secondary OCR service")
                return await self.fallback.extract_text(image)
            raise
```

## 6. API Cost and Performance Optimization

### 6.1 Cost Management Strategy

| Service | Free Tier | Estimated POC Usage | Estimated POC Cost |
|---------|-----------|---------------------|-------------------|
| Twelve Labs | Limited free quota | 50 videos (5 mins avg) | $150-200 |
| Pinecone | 100K vectors | ~50K vectors | $0 (within free tier) |
| Document AI | 1K pages/month | ~5K frames | $20-30 |

**Cost Optimization Measures:**
- Batch processing to reduce API calls
- Caching to prevent redundant processing
- Selective processing of keyframes
- Rate limiting to prevent accidental overages

### 6.2 Performance Optimization

**Latency Management:**
- Parallel processing where possible
- Response caching for repeated operations

**Throughput Management:**
- Request batching for bulk operations
- Simple rate limiting to prevent throttling

## 7. API Integration Testing Strategy

### 7.1 Integration Test Approach

Each API integration will include focused testing:

1. **Integration Testing**: Testing with real API endpoints
2. **Basic Performance Testing**: Simple latency measurements
3. **Fallback Testing**: Verify fallback mechanisms work
4. **End-to-End Testing**: Testing complete workflows

### 7.2 Testing Framework

```python
# Example integration test framework
@pytest.mark.integration
async def test_document_ai_ocr_integration():
    # Setup
    config = DocumentAIConfig(
        project_id=os.environ["DOCUMENT_AI_PROJECT_ID"],
        location="us",
        processor_id=os.environ["DOCUMENT_AI_PROCESSOR_ID"]
    )
    service = DocumentAIService(config)
    
    # Test with reference image
    image_path = "tests/fixtures/text_sample.jpg"
    result = await service.extract_text(image_path)
    
    # Verify against ground truth
    ground_truth = load_ground_truth("tests/fixtures/text_sample.txt")
    accuracy = calculate_text_accuracy(result, ground_truth)
    assert accuracy >= 0.95, f"OCR accuracy below target: {accuracy}"
```

## 8. API Exploration Spikes

Before committing to full implementations, conduct quick proof-of-concept explorations:

1. **Twelve Labs Spike (1-2 days)**
   - Test basic API functionality
   - Verify scene detection accuracy
   - Evaluate integration complexity

2. **Pinecone Spike (1 day)**
   - Test vector storage performance
   - Verify search functionality
   - Evaluate migration complexity

3. **Document AI Spike (1 day)**
   - Test OCR accuracy with sample frames
   - Verify API constraints
   - Evaluate processing requirements

These spikes will validate assumptions and identify potential challenges before detailed implementation.

## 9. Implementation Sequencing

The API integrations will be implemented in the following sequence:

1. **Twelve Labs (Week 1)**
   - Initialize with basic video understanding
   - Setup scene detection capabilities
   
2. **Pinecone (Week 2)**
   - Setup vector database
   - Integrate with Twelve Labs embeddings
   
3. **Google Document AI (Week 3)**
   - Implement OCR integration
   - Connect to video frame processing

4. **Integration & Optimization (Week 4)**
   - Implement coordinated workflows
   - Add fallback mechanisms
   - Optimize performance
   
## 10. Conclusion

This API integration strategy provides a focused approach to replacing complex custom implementations with managed API services. By leveraging best-in-class API services for their respective domains, the Vidst project can focus on demonstrating its core value proposition while reducing implementation complexity.

The strategy emphasizes simplicity through minimal abstractions, reliability through basic fallback mechanisms, and focused testing that validates core functionality. By following this strategy, the project can achieve the refactoring goals outlined in the master plan while maintaining all performance targets.

For detailed implementation guidance on specific API integrations, refer to the service-specific documents listed at the beginning of this document.
