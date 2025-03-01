# Vidst TDD Testing Strategy

## Document Status

| Version | Date | Author | Status |
|---------|------|--------|--------|
| 1.0 | February 26, 2025 | Vidst Team | Draft |

**Related Documents:**
- [Vidst Refactoring Master Plan](./vidst_refactoring_master_plan.md)
- [Vidst API Integration Strategy](./vidst_api_integration_strategy.md)
- [Vidst Architecture Transition](./vidst_architecture_transition.md)
- [Vidst Twelve Labs Integration Strategy](./vidst_twelve_labs_integration_strategy.md)
- [Vidst Vector DB API Integration](./vidst_vector_db_api_integration.md)

## 1. Executive Summary

This document outlines a comprehensive Test-Driven Development (TDD) strategy for the Vidst refactoring project. The strategy focuses on ensuring that the migration from custom implementations to API-based services maintains or improves functionality while reducing complexity. By adopting a test-first approach, we can verify that each component meets its requirements while providing confidence in the refactored system's capabilities.

### Primary Objectives

1. **Maintain Functional Equivalence**: Ensure refactored components deliver the same or improved functionality
2. **Validate Performance Metrics**: Verify all performance targets are met or exceeded
3. **Ensure Robust Error Handling**: Confirm system gracefully handles API failures
4. **Support Incremental Refactoring**: Enable phased implementation through isolated testing
5. **Provide Clear Implementation Path**: Create actionable test examples for developers

By following this TDD strategy, the project can achieve a ~60% reduction in implementation complexity while maintaining or enhancing all core functionality, within the 6-week POC timeline.

## 2. TDD Principles and Methodology

### 2.1 Core TDD Principles

The Vidst refactoring project will follow these core TDD principles:

1. **Write Tests First**: Create tests before implementing functionality
2. **Start with Interfaces**: Define clear interfaces that components must satisfy
3. **Minimal Implementation**: Write the minimum code necessary to pass tests
4. **Refactor with Confidence**: Improve code while ensuring tests remain green
5. **Progressive Integration**: Start with unit tests, then add integration tests

### 2.2 Adapted TDD Workflow for API Integration

For integrating external APIs, we adapt the standard TDD cycle:

1. **Define Interface Tests**: Write tests for the component interface
2. **Create Mock Tests**: Write unit tests with mocked API responses
3. **Implement Component**: Develop the API integration to pass tests
4. **Create Integration Tests**: Test against actual APIs with test accounts
5. **Verify Performance**: Validate performance meets or exceeds targets

### 2.3 Test Categories

Our testing strategy employs four test categories:

| Category | Purpose | Focus | Execution Frequency |
|----------|---------|-------|---------------------|
| Unit Tests | Test components in isolation | Component correctness with mocked dependencies | Every PR, CI/CD pipeline |
| Integration Tests | Test component interactions | Cross-component functionality, real API (limited scale) | Daily in development, weekly in CI/CD |
| End-to-End Tests | Test complete workflows | Full system functionality | Weekly, manual validation |
| Performance Tests | Verify metrics | Speed, accuracy, resource usage | Major milestones |

## 3. Component-Specific Testing Strategies

Based on the Component Evaluation Matrix, we prioritize our testing efforts as follows:

### 3.1 High Priority Components

#### 3.1.1 Scene Detection (Twelve Labs API)

**Current Implementation**: Custom OpenCV-based implementation  
**Target API**: Twelve Labs Marengo/Pegasus  
**Success Metric**: >90% accuracy (Twelve Labs achieves ~94.2%)

**TDD Strategy:**

1. **Interface Tests**:
   ```python
   def test_scene_detection_interface(model):
       """Test interface contract for scene detection."""
       assert hasattr(model, 'detect_scenes')
       # Verify method signature and return type
   ```

2. **Mock-Based Unit Tests**:
   ```python
   @pytest.mark.asyncio
   async def test_detect_scenes_with_mock(model, mock_client):
       """Test scene detection with mocked response."""
       # Setup mock scene detection response
       mock_response = {
           "groups": [
               {"start_time": 0, "end_time": 10.5, "confidence": 0.93},
               {"start_time": 10.5, "end_time": 25.2, "confidence": 0.87}
           ]
       }
       mock_client.search.query.return_value = mock_response
       
       # Call method
       scenes = await model.detect_scenes("test_index_123")
       
       # Verify results match expected format
       assert len(scenes) == 2
       assert scenes[0]["start_time"] == 0
       assert scenes[0]["end_time"] == 10.5
   ```

3. **Integration Tests**:
   ```python
   @pytest.mark.asyncio
   async def test_detect_scenes_real_api(model, test_video):
       """Test scene detection with real API."""
       # Process video through API
       result = await model.analyze_video(test_video)
       index_id = result["index_id"]
       
       # Call scene detection
       scenes = await model.detect_scenes(index_id)
       
       # Verify results structure
       assert len(scenes) > 0
       for scene in scenes:
           assert "scene_id" in scene
           assert "start_time" in scene
           assert "end_time" in scene
   ```

4. **Accuracy Tests**:
   ```python
   @pytest.mark.performance
   def test_scene_detection_accuracy(model, ground_truth_video):
       """Test scene detection accuracy against ground truth."""
       # Compare detected scenes with ground truth
       # Verify meets 94.2% accuracy target
   ```

#### 3.1.2 Vector Storage (Pinecone API)

**Current Implementation**: Self-hosted FAISS  
**Target API**: Pinecone API  
**Success Metric**: Query response time <2 seconds

**TDD Strategy:**

1. **Interface Tests**:
   ```python
   def test_vector_storage_interface(storage):
       """Test vector storage interface compliance."""
       assert hasattr(storage, 'store')
       assert hasattr(storage, 'search')
       assert hasattr(storage, 'delete')
   ```

2. **Unit Tests**:
   ```python
   @pytest.mark.asyncio
   async def test_store_vectors(storage, mock_pinecone):
       """Test storing vectors in Pinecone."""
       # Setup test vectors
       vectors = [
           {"id": "vec1", "vector": [0.1, 0.2, ...], "metadata": {"text": "test"}},
           {"id": "vec2", "vector": [0.3, 0.4, ...], "metadata": {"text": "test2"}}
       ]
       
       # Setup mock
       mock_index = MagicMock()
       mock_pinecone.Index.return_value = mock_index
       mock_index.upsert.return_value = {"upserted_count": 2}
       
       # Call method
       result = await storage.store(vectors)
       
       # Verify results
       assert result["upserted_count"] == 2
   ```

3. **Migration Tests**:
   ```python
   @pytest.mark.asyncio
   async def test_faiss_to_pinecone_migration(faiss_storage, pinecone_storage):
       """Test migration from FAISS to Pinecone."""
       # Load test vectors from FAISS
       # Migrate to Pinecone
       # Verify all vectors were transferred correctly
   ```

4. **Performance Tests**:
   ```python
   @pytest.mark.performance
   async def test_query_performance(storage, test_vectors):
       """Test vector search performance."""
       # Measure query response time
       # Verify <2 seconds response time
   ```

#### 3.1.3 OCR/Text Extraction (Google Document AI)

**Current Implementation**: pytesseract/easyocr  
**Target API**: Google Document AI  
**Success Metric**: >95% accuracy

**TDD Strategy:**
- Interface tests for text extraction contract
- Unit tests with mocked Document AI responses
- Integration tests with sample images
- Accuracy tests against ground truth datasets

#### 3.1.4 Natural Language Querying (Twelve Labs)

**Current Implementation**: Backend exists, interface missing  
**Target API**: Twelve Labs Semantic Search  
**Success Metric**: >85% query relevance

**TDD Strategy:**
- Interface tests for query/response contract
- Unit tests for semantic search with mocks
- Integration tests for end-to-end query flow
- Relevance tests against benchmark queries

#### 3.1.5 Audio Transcription (Hybrid)

**Current Implementation**: Whisper (placeholder)  
**Target Solution**: Hybrid (Whisper + Twelve Labs)  
**Success Metric**: >95% transcription accuracy

**TDD Strategy:**
- Interface tests for transcription contract
- Unit tests for both implementations
- Comparative tests to determine optimal approach
- Fallback tests to ensure reliability

### 3.2 Medium and Lower Priority Components

For medium and lower priority components, we will implement a simplified testing strategy that focuses on interface stability and basic functionality. Detailed testing will be addressed in later phases.

## 4. Testing Infrastructure

### 4.1 Mock Framework

We will extend the existing mock_factory.py to support the new API integrations:

```python
# tests/utils/mock_factory.py (extensions)

class TwelveLabsMocks:
    @staticmethod
    def get_analyze_video_response(success=True):
        if success:
            return {
                "index_id": "mock-index-123",
                "status": "ready",
                "task_id": "mock-task-123"
            }
        else:
            return {"error": "Failed to process video", "code": 500}
    
    @staticmethod
    def get_scene_detection_response():
        return {
            "groups": [
                {"start_time": 0, "end_time": 10.5, "confidence": 0.93},
                {"start_time": 10.5, "end_time": 25.2, "confidence": 0.87}
            ]
        }
```

### 4.2 Test Fixtures

We will organize test fixtures by component:

```
tests/fixtures/
├── video_samples/           # Test videos of various types
├── text_samples/            # Images with text for OCR testing
├── audio_samples/           # Audio files for transcription testing
└── mock_responses/          # Recorded API responses
    ├── twelve_labs/         # Mock Twelve Labs responses 
    ├── pinecone/            # Mock Pinecone responses
    └── document_ai/         # Mock Document AI responses
```

### 4.3 Test Configuration

We will create a central test configuration file:

```python
# tests/test_config.py

import os
from pathlib import Path

# API credentials for testing
TWELVE_LABS_API_KEY = os.environ.get("TWELVE_LABS_API_KEY", "")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY", "")
DOCUMENT_AI_API_KEY = os.environ.get("DOCUMENT_AI_API_KEY", "")

# Test directories
TEST_DATA_DIR = Path("tests/fixtures")
TEST_VIDEOS_DIR = TEST_DATA_DIR / "video_samples"
TEST_IMAGES_DIR = TEST_DATA_DIR / "text_samples"
TEST_AUDIO_DIR = TEST_DATA_DIR / "audio_samples"

# Helper functions
def skip_if_no_api_key(key_name):
    """Create a pytest skip decorator if the API key is not available."""
    import pytest
    return pytest.mark.skipif(
        globals().get(key_name, "") == "",
        reason=f"{key_name} environment variable not set"
    )
```

### 4.4 CI/CD Integration

To support CI/CD pipelines, we will:

1. **Use VCR.py or similar**: Record real API responses and replay them in CI/CD
2. **Implement test tagging**: Separate fast unit tests from slower integration tests
3. **Environment-based testing**: Use environment variables to control test execution

## 5. Docstring Standards

Proper documentation is essential for maintainable tests. We will follow these docstring standards:

### 5.1 Test Method Docstrings

Every test method should include a clear docstring:

```python
def test_analyze_video_success(self, model, mock_client):
    """
    Test successful video analysis with Twelve Labs API.
    
    This test verifies that:
    1. The analyze_video method correctly processes the video file
    2. The method properly handles the API response 
    3. The returned object contains the expected fields
    
    Args:
        model: The TwelveLabsEnhancedModel fixture
        mock_client: A mock of the Twelve Labs client
    """
```

### 5.2 Test Class Docstrings

Test classes should document their overall purpose:

```python
class TestTwelveLabsSceneDetection:
    """
    Test suite for Twelve Labs scene detection functionality.
    
    These tests verify the TwelveLabsEnhancedModel's ability to:
    - Process and analyze videos
    - Detect scene boundaries
    - Generate scene metadata
    - Handle API errors appropriately
    """
```

### 5.3 Implementation Docstrings

Implementation code should include comprehensive docstrings:

```python
async def analyze_video(self, video_path: str, index_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze a video file using Twelve Labs API.
    
    This method uploads and indexes a video for further analysis.
    
    Args:
        video_path: Path to the video file
        index_name: Optional name for the index (generated if not provided)
        
    Returns:
        Dictionary containing:
            - index_id: The ID of the indexed video
            - status: Status of the indexing operation
            - task_id: ID of the task for tracking progress
        
    Raises:
        AIServiceError: If there's an error with the API service
        ModelProcessingError: If there's an error processing the video
    """
```

## 6. Implementation Plan

The TDD implementation will follow the same phased approach outlined in the Refactoring Master Plan:

### 6.1 Phase 1: Core API Integration (Weeks 1-2)

1. Create interface tests for Scene Detection and Vector Storage
2. Implement unit tests with mocks for these components
3. Develop the API integrations
4. Create integration tests for core functionality

### 6.2 Phase 2: Enhanced Capabilities (Weeks 3-4)

1. Extend testing to OCR and Natural Language Querying
2. Implement hybrid approach tests for Audio Transcription
3. Create comparative tests to validate implementation choices

### 6.3 Phase 3: System Integration (Weeks 5-6)

1. Develop end-to-end tests for complete workflows
2. Implement performance benchmarking
3. Validate all success metrics

## 7. Getting Started

To begin implementing this TDD strategy:

### 7.1 Setup Test Environment

1. Create necessary directory structure:
   ```bash
   # Create initial test files
   mkdir -p tests/unit/ai/models
   mkdir -p tests/unit/storage/vector
   mkdir -p tests/integration/ai/models
   mkdir -p tests/integration/storage/vector
   ```

2. Create test template files:
   ```bash
   # Create unit test files
   touch tests/unit/ai/models/test_twelve_labs_enhanced.py
   touch tests/unit/storage/vector/test_pinecone_storage.py
   
   # Create integration test files
   touch tests/integration/ai/models/test_twelve_labs_integration.py
   touch tests/integration/storage/vector/test_pinecone_integration.py
   ```

3. Set up test configuration:
   - Create tests/test_config.py with API credentials and helper functions
   - Update pytest.ini for test categorization

### 7.2 Create Initial Interface Tests

Start with interface tests for the highest priority components:

```python
# tests/unit/ai/models/test_twelve_labs_enhanced.py

import pytest
from video_understanding.ai.models.twelve_labs_enhanced import TwelveLabsEnhancedModel

def test_model_interface():
    """Test that the model implements all required methods."""
    model = TwelveLabsEnhancedModel(api_key="test")
    
    # Scene detection methods
    assert hasattr(model, "analyze_video")
    assert hasattr(model, "detect_scenes")
    
    # Search methods
    assert hasattr(model, "search_video")
    
    # Summary methods
    assert hasattr(model, "generate_summary")
```

### 7.3 Implement Mock Factory Extensions

Extend the mock factory to support API testing:

```python
# tests/utils/mock_factory.py (extensions)

class ApiMocks:
    """Factory for API mock responses."""
    
    @staticmethod
    def twelve_labs_analyze_response():
        """Mock for Twelve Labs analyze_video response."""
        return {
            "index_id": "test-index-123",
            "status": "ready",
            "task_id": "test-task-123"
        }
    
    @staticmethod
    def twelve_labs_scenes_response():
        """Mock for Twelve Labs scene detection response."""
        return {
            "groups": [
                {"start_time": 0, "end_time": 10.5, "confidence": 0.93},
                {"start_time": 10.5, "end_time": 25.2, "confidence": 0.87}
            ]
        }
```

## 8. Success Metrics

The testing strategy will be evaluated based on:

1. **Test Coverage**: >90% coverage for all new or refactored components
2. **Functional Equivalence**: All tests pass, demonstrating equal or improved functionality
3. **Performance Validation**: All performance targets are met or exceeded
4. **Development Velocity**: Testing supports rather than hinders development pace
5. **Defect Reduction**: Fewer defects in refactored components

## 9. Common Challenges and Mitigations

| Challenge | Mitigation |
|-----------|------------|
| API limits during testing | Record API responses for replay in CI/CD |
| Slow integration tests | Categorize tests, run unit tests more frequently |
| Mock fidelity issues | Regularly update mocks based on real API interactions |
| Test data management | Create standardized test fixtures with version control |
| API authentication in CI/CD | Use environment variables and secure storage for API keys |

## 10. Conclusion

This TDD testing strategy provides a comprehensive approach for ensuring the successful refactoring of the Vidst video understanding system. By following this test-first approach, we can verify that each component meets its requirements while simplifying the overall architecture.

The strategy emphasizes interface stability, component isolation, and progressive integration, allowing the team to confidently replace complex custom implementations with API-based alternatives while maintaining or improving functionality.

## References

1. [Pytest Documentation](https://docs.pytest.org/)
2. [Twelve Labs API Documentation](https://docs.twelvelabs.io/)
3. [Pinecone API Documentation](https://docs.pinecone.io/)
4. [Google Document AI Documentation](https://cloud.google.com/document-ai/docs)
5. [Test-Driven Development by Example (Kent Beck)](https://www.oreilly.com/library/view/test-driven-development/0321146530/)
6. [Python Testing with pytest (Brian Okken)](https://pragprog.com/titles/bopytest2/python-testing-with-pytest-second-edition/)