# Vidst Refactoring - API Integration Testing

## When to apply
@semantics Applies when writing tests for API integrations, such as Twelve Labs, Pinecone, and Document AI.
@files tests/api/**/*.py tests/integration/**/*.py tests/**/test_*api*.py
@userMessages ".*test API.*" ".*API integration test.*" ".*mock API.*" ".*twelve labs test.*" ".*pinecone test.*"

## API Testing Guidelines

This rule provides patterns for testing API integrations in the Vidst refactoring project.

## Using responses Library

```python
import pytest
import responses
from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetector

class TestTwelveLabsAPI:
    @pytest.fixture
    def detector(self):
        """Create a detector for testing."""
        config = {
            "api_key": "test_key",
            "api_url": "https://api.twelvelabs.io/v1"
        }
        return TwelveLabsSceneDetector(config)
    
    @responses.activate
    async def test_detect_scenes(self, detector):
        """Test scene detection with mocked API."""
        # Setup mock responses
        responses.add(
            responses.POST,
            "https://api.twelvelabs.io/v1/upload",
            json={"task_id": "test_task"},
            status=200
        )
        
        responses.add(
            responses.GET,
            "https://api.twelvelabs.io/v1/tasks/test_task",
            json={"status": "completed"},
            status=200
        )
        
        # Act
        result = await detector.detect_scenes("test_video.mp4")
        
        # Assert
        assert len(responses.calls) == 2
        assert result is not None
```

## Testing API Error Handling

```python
@responses.activate
async def test_api_error_handling(self, detector):
    """Test API error handling."""
    # Setup mock error response
    responses.add(
        responses.POST,
        "https://api.twelvelabs.io/v1/upload",
        json={"error": "Invalid API key"},
        status=401
    )
    
    # Act & Assert
    with pytest.raises(APIError) as exc_info:
        await detector.detect_scenes("test_video.mp4")
    
    assert "Invalid API key" in str(exc_info.value)
```

## Testing Retry Logic

```python
@responses.activate
async def test_retry_logic(self, detector):
    """Test API retry logic."""
    # First attempt fails
    responses.add(
        responses.POST,
        "https://api.twelvelabs.io/v1/upload",
        json={"error": "Server error"},
        status=500
    )
    
    # Second attempt succeeds
    responses.add(
        responses.POST,
        "https://api.twelvelabs.io/v1/upload",
        json={"task_id": "test_task"},
        status=200
    )
    
    # Successful task response
    responses.add(
        responses.GET,
        "https://api.twelvelabs.io/v1/tasks/test_task",
        json={"status": "completed"},
        status=200
    )
    
    # Act
    await detector.detect_scenes("test_video.mp4")
    
    # Assert - should have called the upload endpoint twice
    assert len([c for c in responses.calls if c.request.url.endswith("/upload")]) == 2
```

## Testing Circuit Breaker

```python
import pytest
from unittest.mock import MagicMock
from video_understanding.utils.circuit_breaker import CircuitBreaker

class TestCircuitBreaker:
    @pytest.fixture
    def circuit_breaker(self):
        """Create a circuit breaker for testing."""
        return CircuitBreaker(failure_threshold=2, reset_timeout=0.1)
    
    async def test_circuit_opens_after_failures(self, circuit_breaker):
        """Test circuit opens after threshold failures."""
        # Setup mock function that always fails
        mock_func = MagicMock(side_effect=Exception("test error"))
        
        # First failure
        with pytest.raises(Exception):
            await circuit_breaker.execute(mock_func)
        
        assert not circuit_breaker.is_open
        
        # Second failure - should open circuit
        with pytest.raises(Exception):
            await circuit_breaker.execute(mock_func)
        
        assert circuit_breaker.is_open
        
        # Third call - should fail with CircuitBreakerOpenError
        with pytest.raises(CircuitBreakerOpenError):
            await circuit_breaker.execute(mock_func)
```

## Mocking Third-Party Libraries

### Twelve Labs

```python
@pytest.fixture
def mock_twelve_labs(monkeypatch):
    """Mock Twelve Labs client."""
    mock_client = MagicMock()
    mock_client.upload_video.return_value = {"task_id": "test_task"}
    mock_client.get_task_status.return_value = {"status": "completed"}
    mock_client.get_results.return_value = {
        "scenes": [
            {"start": 0.0, "end": 10.5, "confidence": 0.95},
            {"start": 10.5, "end": 15.2, "confidence": 0.92}
        ]
    }
    
    # Patch the client initialization
    monkeypatch.setattr(
        "video_understanding.ai.scene.twelve_labs.TwelveLabsClient",
        lambda api_key, api_url: mock_client
    )
    
    return mock_client
```

### Pinecone

```python
@pytest.fixture
def mock_pinecone(monkeypatch):
    """Mock Pinecone client."""
    mock_index = MagicMock()
    mock_index.upsert.return_value = {"upserted_count": 3}
    mock_index.query.return_value = {
        "matches": [
            {"id": "test1", "score": 0.95},
            {"id": "test2", "score": 0.85}
        ]
    }
    
    mock_pinecone = MagicMock()
    mock_pinecone.list_indexes.return_value = ["test-index"]
    mock_pinecone.Index.return_value = mock_index
    
    # Patch the module
    monkeypatch.setattr(
        "video_understanding.storage.vector.pinecone.pinecone",
        mock_pinecone
    )
    
    return {"pinecone": mock_pinecone, "index": mock_index}
```

## Testing API Integration

Example for Twelve Labs scene detection:

```python
import pytest
import responses
from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetector

class TestTwelveLabsIntegration:
    @pytest.fixture
    def detector(self):
        """Create a detector for testing."""
        config = {
            "api_key": "test_key",
            "api_url": "https://api.twelvelabs.io/v1"
        }
        return TwelveLabsSceneDetector(config)
    
    @responses.activate
    async def test_scene_detection_flow(self, detector):
        """Test the complete scene detection flow."""
        # Mock file upload
        responses.add(
            responses.POST,
            "https://api.twelvelabs.io/v1/upload",
            json={"task_id": "test_task"},
            status=200
        )
        
        # Mock task status - processing
        responses.add(
            responses.GET,
            "https://api.twelvelabs.io/v1/tasks/test_task",
            json={"status": "processing"},
            status=200
        )
        
        # Mock task status - completed
        responses.add(
            responses.GET,
            "https://api.twelvelabs.io/v1/tasks/test_task",
            json={"status": "completed"},
            status=200
        )
        
        # Mock results
        responses.add(
            responses.GET,
            "https://api.twelvelabs.io/v1/results/test_task",
            json={
                "scenes": [
                    {"start": 0.0, "end": 10.5, "confidence": 0.95},
                    {"start": 10.5, "end": 15.2, "confidence": 0.92}
                ]
            },
            status=200
        )
        
        # Act
        scenes = await detector.detect_scenes("test_video.mp4")
        
        # Assert
        assert len(scenes) == 2
        assert scenes[0]["start"] == 0.0
        assert scenes[0]["confidence"] == 0.95
```

## Integration Test Structure

For tests that integrate multiple components:

```python
class TestSceneToVectorIntegration:
    @pytest.fixture
    def scene_detector(self, mock_twelve_labs):
        """Create a scene detector with mocked API."""
        config = {"api_key": "test_key"}
        return TwelveLabsSceneDetector(config)
    
    @pytest.fixture
    def vector_storage(self, mock_pinecone):
        """Create vector storage with mocked API."""
        config = {
            "api_key": "test_key",
            "environment": "test",
            "index_name": "test-index"
        }
        return PineconeVectorStorage(config)
    
    async def test_scene_to_vector_workflow(self, scene_detector, vector_storage):
        """Test the workflow from scene detection to vector storage."""
        # Detect scenes
        scenes = await scene_detector.detect_scenes("test.mp4")
        
        # Check scenes were detected
        assert len(scenes) > 0
        
        # Extract vectors (assume embeddings in scenes)
        vectors = [scene.get("embedding") for scene in scenes]
        ids = [f"scene_{i}" for i in range(len(scenes))]
        
        # Store vectors
        result = await vector_storage.add_vectors(vectors, ids)
        
        # Check storage succeeded
        assert result is True
        
        # Search for similar scene
        similar = await vector_storage.search_vectors(vectors[0], limit=1)
        
        # Check search returned results
        assert len(similar) > 0
        assert similar[0]["id"] == ids[0]
```

## API Testing Checklist

When testing API integrations:

1. ✓ Mock all external API calls
2. ✓ Test the complete API workflow
3. ✓ Test error handling for API errors
4. ✓ Test retry logic for transient errors
5. ✓ Verify correct API request parameters
6. ✓ Verify proper handling of API responses
7. ✓ Test circuit breaker functionality
