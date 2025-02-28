# Vidst TDD Implementation Guide

## Document Status

| Version | Date | Author | Status |
|---------|------|--------|--------|
| 1.0 | February 26, 2025 | Vidst Team | Draft |

**Related Documents:**
- [Vidst TDD Testing Strategy](./vidst_tdd_testing_strategy.md)
- [Vidst Test Fixtures Reference](./vidst_test_fixtures_reference.md)
- [Vidst Refactoring Master Plan](../vidst_refactoring_master_plan.md)

## 1. Introduction

This guide provides practical, hands-on instructions for implementing Test-Driven Development (TDD) in the Vidst refactoring project. It offers step-by-step workflows, code examples, and best practices to help developers write effective tests and implement components using the TDD approach.

### Purpose and Audience

This document is intended for developers working on the Vidst refactoring project. It assumes familiarity with Python, pytest, and the basics of Vidst's architecture. The guide focuses on practical implementation rather than theoretical TDD concepts.

### How to Use This Guide

- **Getting Started**: Begin with Section 2 to set up your test environment
- **Component Testing**: Use Section 3 for step-by-step TDD workflows by component
- **Code Examples**: Find practical code examples in Section 4
- **Common Challenges**: Reference Section 5 for solutions to common testing challenges

## 2. Test Environment Setup

### 2.1 Development Environment

Before you begin writing tests, set up your development environment:

```bash
# Install development dependencies
pip install -r requirements.txt -r requirements-dev.txt -r requirements-test.txt

# Create test environment configuration
cp tests/test_config.example.py tests/test_config.py
```

Edit `tests/test_config.py` to configure your test environment settings.

### 2.2 API Keys for Testing

To run integration tests, you'll need API keys for the external services:

1. **Twelve Labs API**: Obtain a key from [Twelve Labs Developer Portal](https://docs.twelvelabs.io/)
2. **Pinecone API**: Get API key from [Pinecone Console](https://app.pinecone.io/)
3. **Google Document AI**: Get API key from [Google Cloud Console](https://console.cloud.google.com/)

Add these keys to your test environment:

```bash
# For local testing (add to .env)
TWELVE_LABS_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=your_environment
DOCUMENT_AI_API_KEY=your_key_here

# Alternative: set environment variables directly
export TWELVE_LABS_API_KEY=your_key_here
```

### 2.3 Test Data Setup

Create or download required test data:

```bash
# Create test data directories if they don't exist
mkdir -p tests/fixtures/video_samples/valid
mkdir -p tests/fixtures/text_samples
mkdir -p tests/fixtures/audio_samples

# Download sample test data (example)
python scripts/download_test_data.py
```

## 3. TDD Workflow by Component

This section provides step-by-step TDD workflows for each high-priority component.

### 3.1 Scene Detection (Twelve Labs) TDD Workflow

#### Step 1: Create Interface Tests

Create `tests/unit/ai/models/test_twelve_labs_enhanced.py` with interface tests:

```python
import pytest
from video_understanding.ai.models.twelve_labs_enhanced import TwelveLabsEnhancedModel

class TestTwelveLabsInterface:
    """Tests for the TwelveLabsEnhancedModel interface."""
    
    def test_has_required_methods(self):
        """Test that the model has all required methods."""
        model = TwelveLabsEnhancedModel(api_key="test")
        
        # Verify scene detection methods
        assert hasattr(model, "analyze_video")
        assert hasattr(model, "detect_scenes")
        
        # Verify method signatures
        import inspect
        sig = inspect.signature(model.analyze_video)
        assert "video_path" in sig.parameters
```

Run this test (it will fail initially):

```bash
pytest tests/unit/ai/models/test_twelve_labs_enhanced.py -v
```

#### Step 2: Create Initial Implementation

Create a minimal implementation to pass the interface test:

```python
# video_understanding/ai/models/twelve_labs_enhanced.py
from typing import Dict, List, Optional, Any
from video_understanding.ai.models.base import BaseAIModel

class TwelveLabsEnhancedModel(BaseAIModel):
    """Enhanced implementation of Twelve Labs video understanding model."""
    
    def __init__(self, api_key: str, engine: str = "marengo-2.6"):
        """Initialize the Twelve Labs model."""
        self.api_key = api_key
        self.engine = engine
        
    async def analyze_video(self, video_path: str, index_name: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a video file using Twelve Labs API."""
        raise NotImplementedError()
        
    async def detect_scenes(self, index_id: str) -> List[Dict[str, Any]]:
        """Detect scenes in an indexed video."""
        raise NotImplementedError()
```

#### Step 3: Create Behavioral Unit Tests

Add detailed unit tests with mocks:

```python
import pytest
from unittest.mock import patch, MagicMock
import json
from video_understanding.ai.models.twelve_labs_enhanced import TwelveLabsEnhancedModel

class TestTwelveLabsSceneDetection:
    @pytest.fixture
    def model(self):
        """Create a model instance for testing."""
        return TwelveLabsEnhancedModel(api_key="test_key")
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Twelve Labs client."""
        with patch('twelvelabs.Client') as mock:
            client = MagicMock()
            mock.return_value = client
            yield client
    
    @pytest.mark.asyncio
    async def test_analyze_video_success(self, model, mock_client):
        """Test successful video analysis with mocked response."""
        # Setup mock
        task = MagicMock()
        task.index_id = "test_index_123"
        task.status = "ready"
        task.id = "task_123"
        mock_client.index.create.return_value = task
        
        # Call method
        result = await model.analyze_video("test_video.mp4")
        
        # Verify results
        assert result["index_id"] == "test_index_123"
        assert result["status"] == "ready"
        assert "task_id" in result
        
        # Verify mock was called correctly
        mock_client.index.create.assert_called_once()
```

#### Step 4: Implement to Pass Unit Tests

Update the implementation to pass the unit tests:

```python
# video_understanding/ai/models/twelve_labs_enhanced.py
from typing import Dict, List, Optional, Any
import httpx
import backoff
from twelvelabs import Client

from video_understanding.ai.models.base import BaseAIModel
from video_understanding.utils.exceptions import AIServiceError

class TwelveLabsEnhancedModel(BaseAIModel):
    """Enhanced implementation of Twelve Labs video understanding model."""
    
    def __init__(self, api_key: str, engine: str = "marengo-2.6"):
        """Initialize the Twelve Labs model."""
        self.api_key = api_key
        self.engine = engine
        self.client = Client(api_key=api_key)
        
    @backoff.on_exception(
        backoff.expo,
        (httpx.HTTPError, httpx.TimeoutException),
        max_tries=3
    )
    async def analyze_video(self, video_path: str, index_name: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a video file using Twelve Labs API."""
        try:
            if not index_name:
                import uuid
                index_name = f"vidst-{uuid.uuid4()}"
                
            with open(video_path, "rb") as f:
                task = self.client.index.create(
                    video=f,
                    index_name=index_name,
                    title=f"Video Analysis {index_name}"
                )
            
            return {
                "index_id": task.index_id,
                "status": task.status,
                "task_id": task.id
            }
                
        except Exception as e:
            raise AIServiceError(f"Twelve Labs API error: {str(e)}")
```

#### Step 5: Create Integration Tests

Create integration tests that use the real API:

```python
# tests/integration/ai/models/test_twelve_labs_integration.py
import pytest
import os
from pathlib import Path
from video_understanding.ai.models.twelve_labs_enhanced import TwelveLabsEnhancedModel

# Skip if no API key is available
pytestmark = pytest.mark.skipif(
    os.environ.get("TWELVE_LABS_API_KEY") is None,
    reason="TWELVE_LABS_API_KEY environment variable not set"
)

class TestTwelveLabsIntegration:
    @pytest.fixture
    def model(self):
        """Create a model instance with real API key."""
        return TwelveLabsEnhancedModel(
            api_key=os.environ.get("TWELVE_LABS_API_KEY")
        )
    
    @pytest.fixture
    def test_video_path(self):
        """Get path to test video."""
        return Path("tests/fixtures/video_samples/valid/short_test_video.mp4")
    
    @pytest.mark.asyncio
    async def test_analyze_video_real_api(self, model, test_video_path):
        """Test video analysis with the real Twelve Labs API."""
        try:
            result = await model.analyze_video(str(test_video_path))
            
            # Verify structure of response
            assert "index_id" in result
            assert "status" in result
            
            # Store for other tests
            self.index_id = result["index_id"]
            
        except Exception as e:
            pytest.fail(f"Real API call failed: {str(e)}")
```

Run integration tests (skip if no API key):

```bash
pytest tests/integration/ai/models/test_twelve_labs_integration.py -v
```

#### Step 6: Implement Remaining Features and Tests

Continue the TDD cycle for remaining features:
1. Write tests for `detect_scenes` method
2. Implement the method to pass tests
3. Add integration tests for scene detection
4. Continue for other methods

### 3.2 Vector Storage (Pinecone) TDD Workflow

Follow similar steps as outlined above:

1. Create interface tests
2. Create minimal implementation
3. Add behavioral unit tests with mocks
4. Implement to pass unit tests
5. Create integration tests
6. Implement remaining features

## 4. Code Examples by Component

This section provides complete code examples for each component.

### 4.1 Twelve Labs Enhanced Model

#### Complete Test Suite

```python
# tests/unit/ai/models/test_twelve_labs_enhanced.py

import pytest
from unittest.mock import patch, MagicMock
from video_understanding.ai.models.twelve_labs_enhanced import TwelveLabsEnhancedModel

class TestTwelveLabsEnhancedModel:
    """Tests for the TwelveLabsEnhancedModel."""
    
    @pytest.fixture
    def model(self):
        """Create a model instance for testing."""
        return TwelveLabsEnhancedModel(api_key="test_key")
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock Twelve Labs client."""
        with patch('twelvelabs.Client') as mock:
            client = MagicMock()
            mock.return_value = client
            yield client
    
    # Interface tests
    def test_has_required_methods(self, model):
        """Test that the model has all required methods."""
        assert hasattr(model, "analyze_video")
        assert hasattr(model, "detect_scenes")
        assert hasattr(model, "search_video")
        assert hasattr(model, "generate_summary")
    
    # Analyze video tests
    @pytest.mark.asyncio
    async def test_analyze_video_success(self, model, mock_client):
        """Test successful video analysis with mocked response."""
        # Setup mock
        task = MagicMock()
        task.index_id = "test_index_123"
        task.status = "ready"
        task.id = "task_123"
        mock_client.index.create.return_value = task
        
        # Call method
        result = await model.analyze_video("test_video.mp4")
        
        # Verify results
        assert result["index_id"] == "test_index_123"
        assert result["status"] == "ready"
        assert "task_id" in result
    
    @pytest.mark.asyncio
    async def test_analyze_video_error(self, model, mock_client):
        """Test error handling in video analysis."""
        # Setup mock to raise exception
        mock_client.index.create.side_effect = Exception("API error")
        
        # Call method and verify exception
        with pytest.raises(AIServiceError):
            await model.analyze_video("test_video.mp4")
    
    # Scene detection tests
    @pytest.mark.asyncio
    async def test_detect_scenes_success(self, model, mock_client):
        """Test scene detection with mocked response."""
        # Setup mock
        mock_client.search.query.return_value = {
            "groups": [
                {"start_time": 0, "end_time": 10.5, "confidence": 0.93},
                {"start_time": 10.5, "end_time": 25.2, "confidence": 0.87}
            ]
        }
        
        # Call method
        scenes = await model.detect_scenes("test_index_123")
        
        # Verify results
        assert len(scenes) == 2
        assert scenes[0]["start_time"] == 0
        assert scenes[0]["end_time"] == 10.5
        assert scenes[0]["confidence"] == 0.93
        
        # Verify mock was called correctly
        mock_client.search.query.assert_called_with(
            index_id="test_index_123",
            search_options={
                "query": "scene change", 
                "search_type": "visual", 
                "group_by": "scene"
            }
        )
    
    # Additional tests for search_video and generate_summary...
```

#### Complete Implementation

```python
# video_understanding/ai/models/twelve_labs_enhanced.py

from typing import Dict, List, Optional, Any
import httpx
import backoff
from loguru import logger
from twelvelabs import Client

from video_understanding.ai.models.base import BaseAIModel
from video_understanding.utils.exceptions import AIServiceError, ModelProcessingError

class TwelveLabsEnhancedModel(BaseAIModel):
    """Enhanced implementation of Twelve Labs video understanding model."""
    
    def __init__(self, api_key: str, engine: str = "marengo-2.6"):
        """
        Initialize the Twelve Labs model.
        
        Args:
            api_key: API key for Twelve Labs
            engine: Engine version to use
        """
        self.api_key = api_key
        self.engine = engine
        self.client = Client(api_key=api_key)
        logger.info(f"Initialized Twelve Labs model with engine {engine}")
        
    @backoff.on_exception(
        backoff.expo,
        (httpx.HTTPError, httpx.TimeoutException),
        max_tries=3,
        giveup=lambda e: isinstance(e, httpx.HTTPStatusError) and e.response.status_code < 500,
    )
    async def analyze_video(self, video_path: str, index_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a video file using Twelve Labs API.
        
        Args:
            video_path: Path to the video file
            index_name: Optional name for the index
            
        Returns:
            Dictionary containing analysis results
            
        Raises:
            AIServiceError: If there's an error with the API service
            ModelProcessingError: If there's an error processing the video
        """
        try:
            # Create a unique index name if not provided
            if not index_name:
                import uuid
                index_name = f"vidst-{uuid.uuid4()}"
                
            # Index the video for analysis
            with open(video_path, "rb") as f:
                task = self.client.index.create(
                    video=f,
                    index_name=index_name,
                    title=f"Video Analysis {index_name}"
                )
            
            # Wait for indexing to complete
            task.wait()
            if task.status != "ready":
                raise ModelProcessingError(f"Video indexing failed: {task.status}")
                
            # Return the index ID for further operations
            return {
                "index_id": task.index_id,
                "status": task.status,
                "task_id": task.id
            }
                
        except Exception as e:
            if isinstance(e, ModelProcessingError):
                raise
            logger.error(f"Error in Twelve Labs API: {str(e)}")
            raise AIServiceError(f"Twelve Labs API error: {str(e)}")
            
    async def detect_scenes(self, index_id: str) -> List[Dict[str, Any]]:
        """
        Detect scenes in an indexed video.
        
        Args:
            index_id: The index ID of the processed video
            
        Returns:
            List of detected scenes with timestamps and metadata
            
        Raises:
            AIServiceError: If there's an error with the API service
        """
        try:
            # Query for scene changes
            results = self.client.search.query(
                index_id=index_id,
                search_options={
                    "query": "scene change", 
                    "search_type": "visual",
                    "group_by": "scene"
                }
            )
            
            # Process and format scene detections
            scenes = []
            for idx, group in enumerate(results.get("groups", [])):
                scenes.append({
                    "scene_id": idx + 1,
                    "start_time": group.get("start_time", 0),
                    "end_time": group.get("end_time", 0),
                    "duration": group.get("end_time", 0) - group.get("start_time", 0),
                    "confidence": group.get("confidence", 0)
                })
                
            return scenes
                
        except Exception as e:
            logger.error(f"Error in scene detection: {str(e)}")
            raise AIServiceError(f"Scene detection error: {str(e)}")
    
    # Implementation of search_video and generate_summary methods...
```

### 4.2 Pinecone Vector Storage

Similar format with complete test suite and implementation.

## 5. Common Testing Challenges and Solutions

This section addresses common challenges developers may encounter when implementing TDD for the Vidst refactoring project.

### 5.1 Testing Asynchronous Code

Challenge: Many of the API clients use async/await patterns, which require special testing approaches.

Solution:
- Use `pytest-asyncio` for testing async functions
- Mark async tests with `@pytest.mark.asyncio`
- Use async fixtures when needed

Example:
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await my_async_function()
    assert result is not None
```

### 5.2 Mocking Complex API Responses

Challenge: External APIs like Twelve Labs return complex nested JSON responses.

Solution:
- Create a mock factory with realistic responses
- Store example responses in JSON files
- Use fixture parameterization for different response scenarios

Example:
```python
# tests/utils/mock_factory.py
import json
from pathlib import Path

class ApiMocks:
    @staticmethod
    def load_mock_response(name):
        """Load a mock response from a JSON file."""
        file_path = Path("tests/fixtures/mock_responses") / f"{name}.json"
        with open(file_path, "r") as f:
            return json.load(f)
    
    @staticmethod
    def twelve_labs_analyze_response():
        """Get a mock Twelve Labs analyze response."""
        return ApiMocks.load_mock_response("twelve_labs_analyze")
```

### 5.3 Testing Error Handling and Fallbacks

Challenge: Testing error conditions and fallback mechanisms is crucial but can be complex.

Solution:
- Create specific tests for error cases
- Use mock side effects to simulate errors
- Test the complete error handling chain

Example:
```python
@pytest.mark.asyncio
async def test_error_handling_and_fallback(model, mock_client):
    # Configure primary method to fail
    mock_client.index.create.side_effect = Exception("API error")
    
    # Configure fallback to succeed
    mock_client.alternative_method.return_value = {"result": "fallback"}
    
    # Call method with fallback
    result = await model.analyze_video_with_fallback("test.mp4")
    
    # Verify fallback was used
    assert result["result"] == "fallback"
    assert mock_client.alternative_method.called
```

### 5.4 Managing Test API Credentials

Challenge: Integration tests need real API credentials, but these shouldn't be in the code.

Solution:
- Use environment variables for API credentials
- Skip integration tests if credentials aren't available
- Use a consistent pattern for credential checking

Example:
```python
import pytest
import os

# Skip this test if API key is not available
pytestmark = pytest.mark.skipif(
    os.environ.get("TWELVE_LABS_API_KEY") is None,
    reason="TWELVE_LABS_API_KEY environment variable not set"
)
```

### 5.5 Testing Performance Requirements

Challenge: Verifying performance metrics is difficult to do in standard unit tests.

Solution:
- Create dedicated performance test fixtures
- Use pytest-benchmark for consistent measurements
- Compare against known baselines

Example:
```python
def test_vector_search_performance(benchmark, storage, test_vectors):
    # Setup
    storage.store(test_vectors)
    query_vector = test_vectors[0]["vector"]
    
    # Benchmark the search operation
    result = benchmark(
        lambda: storage.search(query_vector, top_k=10)
    )
    
    # Verify performance meets requirements
    assert benchmark.stats.stats.mean < 0.1  # Less than 100ms
```

## 6. Test Fixture Management

Effective test fixtures are critical for TDD success. This section provides guidance on creating and managing test fixtures.

### 6.1 Test Video Fixtures

For testing video processing:

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def test_video_path():
    """Path to a short test video file."""
    return Path("tests/fixtures/video_samples/valid/short_test_video.mp4")

@pytest.fixture
def test_videos():
    """Dictionary of test videos for different scenarios."""
    base_path = Path("tests/fixtures/video_samples/valid")
    return {
        "short": base_path / "short_test_video.mp4",
        "long": base_path / "long_test_video.mp4",
        "no_audio": base_path / "no_audio_video.mp4",
        "text_heavy": base_path / "text_heavy_video.mp4"
    }
```

### 6.2 Mock Response Fixtures

For consistent mock responses:

```python
# tests/conftest.py
import pytest
import json
from pathlib import Path

@pytest.fixture
def twelve_labs_mock_responses():
    """Load Twelve Labs mock responses from JSON files."""
    base_path = Path("tests/fixtures/mock_responses/twelve_labs")
    return {
        name.stem: json.loads(name.read_text())
        for name in base_path.glob("*.json")
    }
```

### 6.3 API Client Fixtures

For testing with real APIs:

```python
# tests/conftest.py
import pytest
import os
from video_understanding.ai.models.twelve_labs_enhanced import TwelveLabsEnhancedModel

@pytest.fixture
def twelve_labs_client():
    """Create a real Twelve Labs client if API key is available."""
    api_key = os.environ.get("TWELVE_LABS_API_KEY")
    if not api_key:
        pytest.skip("TWELVE_LABS_API_KEY environment variable not set")
    
    return TwelveLabsEnhancedModel(api_key=api_key)
```

## 7. Testing Best Practices

This section provides general best practices for TDD in the Vidst refactoring project.

### 7.1 Docstring Standards

Use descriptive docstrings for all test functions:

```python
def test_detect_scenes_success(self, model, mock_client):
    """
    Test successful scene detection with the Twelve Labs API.
    
    This test verifies that:
    1. The detect_scenes method correctly processes the API response
    2. The returned scenes have the expected structure and data
    3. The API is called with the correct parameters
    
    Args:
        model: The TwelveLabsEnhancedModel instance
        mock_client: Mock of the Twelve Labs client
    """
    # Test implementation
```

### 7.2 Test Naming Conventions

Follow a consistent naming convention for test methods:

- `test_<function>_<scenario>`: Specific scenario tests
- `test_<function>_success`: Happy path tests
- `test_<function>_error`: Error handling tests

Examples:
- `test_analyze_video_success`
- `test_analyze_video_timeout_error`
- `test_detect_scenes_empty_video`

### 7.3 Test Organization

Organize tests into classes by functionality:

```python
class TestSceneDetection:
    """Tests for scene detection functionality."""
    # Scene detection tests

class TestVideoSearch:
    """Tests for video search functionality."""
    # Video search tests
```

### 7.4 Code Coverage

Aim for high test coverage, particularly for critical components:

- Use `pytest-cov` to measure coverage
- Run coverage reports regularly
- Focus on covering all code paths, not just line coverage

Example command:
```bash
pytest --cov=video_understanding tests/
```

## 8. Getting Started: First TDD Steps

To start implementing TDD for the Vidst refactoring project:

1. **Create test template files**:
   ```bash
   mkdir -p tests/unit/ai/models
   touch tests/unit/ai/models/test_twelve_labs_enhanced.py
   touch tests/unit/storage/vector/test_pinecone_storage.py
   ```

2. **Write your first interface test**:
   ```python
   # tests/unit/ai/models/test_twelve_labs_enhanced.py
   import pytest
   
   def test_twelve_labs_interface():
       """Test that TwelveLabsEnhancedModel has the required interface."""
       from video_understanding.ai.models.twelve_labs_enhanced import TwelveLabsEnhancedModel
       
       model = TwelveLabsEnhancedModel(api_key="test")
       assert hasattr(model, "analyze_video")
       assert hasattr(model, "detect_scenes")
   ```

3. **Create a minimal implementation**:
   ```python
   # video_understanding/ai/models/twelve_labs_enhanced.py
   from typing import Dict, Any, List
   
   class TwelveLabsEnhancedModel:
       def __init__(self, api_key: str, engine: str = "marengo-2.6"):
           self.api_key = api_key
           self.engine = engine
           
       async def analyze_video(self, video_path: str):
           """Placeholder implementation."""
           pass
           
       async def detect_scenes(self, index_id: str):
           """Placeholder implementation."""
           pass
   ```

4. **Run the test**:
   ```bash
   pytest tests/unit/ai/models/test_twelve_labs_enhanced.py -v
   ```

5. **Continue the TDD cycle**: Add more tests, implement functionality, refactor.

## 9. Conclusion

This implementation guide provides practical direction for applying TDD to the Vidst refactoring project. By following the workflows, code examples, and best practices in this guide, developers can effectively implement and test the refactored components.

Remember the core TDD cycle:
1. Write a test that defines the expected behavior
2. Run the test to verify that it fails
3. Write the minimum code needed to pass the test
4. Run the test to verify that it passes
5. Refactor the code while ensuring tests still pass

For reference implementations and mock response examples, see the [Vidst Test Fixtures Reference](./vidst_test_fixtures_reference.md).
