# Vidst Refactoring - Testing Strategy Rules

## When to apply
@semantics Applies when creating or modifying tests, especially when following the TDD approach for the refactoring project.
@files tests/**/*.py
@userMessages ".*create test.*" ".*test this.*" ".*write test.*" ".*TDD.*" ".*unit test.*" ".*mock.*API.*"

## Testing Strategy Overview

This rule provides guidance for implementing the Test-Driven Development (TDD) approach in the Vidst refactoring project, with a focus on API integrations.

## TDD Approach

Follow these steps when implementing new components or refactoring existing ones:

1. **Write the test first**: Define the expected behavior before implementation
2. **Run the test and watch it fail**: Verify that the test fails correctly
3. **Implement the minimum code to pass**: Focus on the simplest implementation
4. **Run the test and see it pass**: Verify that the implementation works
5. **Refactor**: Clean up the code while maintaining test coverage

## Test Structure

Organize tests according to this structure:

```
tests/
├── unit/
│   ├── ai/
│   │   ├── scene/
│   │   │   ├── test_base.py
│   │   │   ├── test_opencv.py
│   │   │   └── test_twelve_labs.py
│   │   ├── ocr/
│   │   └── object/
│   ├── storage/
│   │   ├── vector/
│   │   └── file/
│   └── processor/
├── integration/
│   ├── test_scene_detection.py
│   ├── test_vector_storage.py
│   └── test_ocr.py
├── api/
│   ├── test_twelve_labs_api.py
│   ├── test_pinecone_api.py
│   └── test_document_ai_api.py
└── fixtures/
    ├── video_fixtures.py
    ├── vector_fixtures.py
    └── ocr_fixtures.py
```

## Unit Testing Guidelines

### Test Class Structure

```python
import pytest
from unittest.mock import MagicMock, patch
from video_understanding.component import Component

class TestComponent:
    """Tests for Component class."""
    
    @pytest.fixture
    def component(self):
        """Create a component for testing."""
        config = {"param1": "value1", "param2": 42}
        return Component(config)
    
    def test_initialization(self, component):
        """Test component initialization."""
        assert component.config["param1"] == "value1"
        assert component.config["param2"] == 42
    
    def test_method_success(self, component):
        """Test method success case."""
        # Arrange
        input_data = {"key": "value"}
        expected = {"result": "success"}
        
        # Act
        result = component.method(input_data)
        
        # Assert
        assert result == expected
    
    def test_method_failure(self, component):
        """Test method failure case."""
        # Arrange
        input_data = {"invalid": "data"}
        
        # Act & Assert
        with pytest.raises(ValueError):
            component.method(input_data)
    
    @patch("video_understanding.component.dependency")
    def test_method_with_mock(self, mock_dependency, component):
        """Test method with mocked dependency."""
        # Arrange
        mock_dependency.return_value = "mocked_result"
        
        # Act
        result = component.method_with_dependency()
        
        # Assert
        assert "mocked_result" in result
        mock_dependency.assert_called_once()
```

### API Test Structure

```python
import pytest
import responses
from video_understanding.api import APIClient

class TestAPIClient:
    """Tests for API client."""
    
    @pytest.fixture
    def client(self):
        """Create an API client for testing."""
        config = {
            "api_key": "test_key",
            "api_url": "https://api.example.com"
        }
        return APIClient(config)
    
    @responses.activate
    def test_api_call_success(self, client):
        """Test successful API call."""
        # Arrange - Mock API response
        responses.add(
            responses.GET,
            "https://api.example.com/endpoint",
            json={"status": "success", "data": {"key": "value"}},
            status=200
        )
        
        # Act
        result = client.call_api("endpoint")
        
        # Assert
        assert result["status"] == "success"
        assert result["data"]["key"] == "value"
    
    @responses.activate
    def test_api_call_error(self, client):
        """Test API call error handling."""
        # Arrange - Mock API error response
        responses.add(
            responses.GET,
            "https://api.example.com/endpoint",
            json={"status": "error", "message": "Invalid request"},
            status=400
        )
        
        # Act & Assert
        with pytest.raises(APIError):
            client.call_api("endpoint")
    
    @responses.activate
    def test_api_call_retry(self, client):
        """Test API call retry logic."""
        # Arrange - Mock API responses
        # First request fails
        responses.add(
            responses.GET,
            "https://api.example.com/endpoint",
            json={"status": "error"},
            status=500
        )
        
        # Second request succeeds
        responses.add(
            responses.GET,
            "https://api.example.com/endpoint",
            json={"status": "success", "data": {"key": "value"}},
            status=200
        )
        
        # Act
        result = client.call_api("endpoint")
        
        # Assert
        assert result["status"] == "success"
        assert len(responses.calls) == 2
```

## Mocking External Dependencies

### Mocking API Calls

```python
import pytest
import responses
from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetector

class TestTwelveLabsSceneDetector:
    @pytest.fixture
    def detector(self):
        """Create a detector with test config."""
        config = {
            "api_key": "test_key",
            "api_url": "https://api.twelvelabs.io/v1"
        }
        return TwelveLabsSceneDetector(config)
    
    @responses.activate
    async def test_detect_scenes(self, detector):
        """Test scene detection with mocked API."""
        # Mock video upload response
        responses.add(
            responses.POST,
            "https://api.twelvelabs.io/v1/upload",
            json={"task_id": "test_task"},
            status=200
        )
        
        # Mock task status response
        responses.add(
            responses.GET,
            "https://api.twelvelabs.io/v1/tasks/test_task",
            json={"status": "completed"},
            status=200
        )
        
        # Mock results response
        responses.add(
            responses.GET,
            "https://api.twelvelabs.io/v1/results/test_task",
            json={
                "scenes": [
                    {
                        "start": 0.0,
                        "end": 10.5,
                        "confidence": 0.95
                    },
                    {
                        "start": 10.5,
                        "end": 15.2,
                        "confidence": 0.92
                    }
                ]
            },
            status=200
        )
        
        # Act
        scenes = await detector.detect_scenes("test_video.mp4")
        
        # Assert
        assert len(scenes) == 2
        assert scenes[0]["start"] == 0.0
        assert scenes[0]["end"] == 10.5
        assert scenes[0]["confidence"] == 0.95
```

### Mocking File Operations

```python
import pytest
from unittest.mock import mock_open, patch
from video_understanding.processor import VideoProcessor

class TestVideoProcessor:
    @pytest.fixture
    def processor(self):
        """Create a video processor for testing."""
        return VideoProcessor()
    
    @patch("builtins.open", new_callable=mock_open, read_data=b"test_data")
    @patch("cv2.VideoCapture")
    def test_process_video(self, mock_video_capture, mock_file, processor):
        """Test video processing with mocked file operations."""
        # Arrange
        mock_video = mock_video_capture.return_value
        mock_video.read.side_effect = [
            (True, "frame1"),
            (True, "frame2"),
            (False, None)
        ]
        
        # Act
        result = processor.process("test_video.mp4")
        
        # Assert
        assert len(result) == 2
        mock_file.assert_called_once_with("test_video.mp4", "rb")
        mock_video_capture.assert_called_once()
```

## Testing Asynchronous Code

```python
import pytest
import asyncio
from video_understanding.ai.scene import SceneDetector

class TestSceneDetector:
    @pytest.fixture
    def detector(self):
        """Create a scene detector for testing."""
        return SceneDetector()
    
    @pytest.mark.asyncio
    async def test_detect_scenes(self, detector):
        """Test asynchronous scene detection."""
        # Act
        result = await detector.detect_scenes("test_video.mp4")
        
        # Assert
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_detect_scenes_with_timeout(self, detector):
        """Test asynchronous scene detection with timeout."""
        # Act & Assert
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(detector.detect_scenes("large_video.mp4"), timeout=0.001)
```

## Integration Testing

```python
import pytest
from video_understanding.ai.scene import SceneDetectorFactory
from video_understanding.storage.vector import VectorStorageFactory

class TestSceneToVectorIntegration:
    @pytest.fixture
    def scene_detector(self):
        """Create a scene detector."""
        config = {"type": "mock"}
        return SceneDetectorFactory.create(config)
    
    @pytest.fixture
    def vector_storage(self):
        """Create a vector storage."""
        config = {"type": "mock"}
        return VectorStorageFactory.create(config)
    
    async def test_scene_to_vector_flow(self, scene_detector, vector_storage):
        """Test the flow from scene detection to vector storage."""
        # Detect scenes
        scenes = await scene_detector.detect_scenes("test_video.mp4")
        
        # Convert scenes to vectors
        vectors = [scene["embedding"] for scene in scenes]
        ids = [f"scene_{i}" for i in range(len(scenes))]
        
        # Store vectors
        result = await vector_storage.add_vectors(vectors, ids)
        
        # Verify storage
        assert result is True
        
        # Search for similar scenes
        query_vector = vectors[0]
        similar_scenes = await vector_storage.search_vectors(query_vector)
        
        # Verify search results
        assert len(similar_scenes) > 0
        assert similar_scenes[0]["id"] == ids[0]
```

## Test Fixtures

Create reusable fixtures for common test scenarios:

```python
# tests/fixtures/video_fixtures.py
import pytest
import numpy as np
import cv2
from pathlib import Path

@pytest.fixture
def sample_video_path():
    """Return path to a sample video file."""
    return Path(__file__).parent / "data" / "sample_video.mp4"

@pytest.fixture
def sample_frames():
    """Generate sample video frames."""
    frames = []
    for i in range(5):
        # Create a frame with a simple pattern
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add a rectangle with different position in each frame
        cv2.rectangle(frame, (i * 50, i * 30), (i * 50 + 100, i * 30 + 100), (0, 255, 0), -1)
        frames.append(frame)
    return frames

@pytest.fixture
def sample_scenes():
    """Generate sample scene data."""
    return [
        {
            "start": 0.0,
            "end": 10.5,
            "confidence": 0.95,
            "frames": [0, 1, 2, 3]
        },
        {
            "start": 10.5,
            "end": 15.2,
            "confidence": 0.92,
            "frames": [4]
        }
    ]
```

## Test Factories

Create factories for test objects:

```python
# tests/fixtures/factory_fixtures.py
import pytest
from unittest.mock import MagicMock

class MockSceneDetector:
    """Mock scene detector for testing."""
    
    def __init__(self, config):
        self.config = config
        
    async def detect_scenes(self, video_path):
        """Return mock scenes."""
        return [
            {
                "start": 0.0,
                "end": 10.5,
                "confidence": 0.95
            },
            {
                "start": 10.5,
                "end": 15.2,
                "confidence": 0.92
            }
        ]

class MockVectorStorage:
    """Mock vector storage for testing."""
    
    def __init__(self, config):
        self.config = config
        self.vectors = {}
        
    async def add_vectors(self, vectors, ids, metadata=None):
        """Store mock vectors."""
        for i, (vector, id_) in enumerate(zip(vectors, ids)):
            self.vectors[id_] = {
                "vector": vector,
                "metadata": metadata[i] if metadata else None
            }
        return True
        
    async def search_vectors(self, query_vector, limit=10):
        """Search mock vectors."""
        return [
            {
                "id": list(self.vectors.keys())[0],
                "score": 0.95
            }
        ]

@pytest.fixture
def mock_factories(monkeypatch):
    """Set up mock factories for testing."""
    scene_factory = MagicMock()
    scene_factory.create.return_value = MockSceneDetector({"type": "mock"})
    
    vector_factory = MagicMock()
    vector_factory.create.return_value = MockVectorStorage({"type": "mock"})
    
    monkeypatch.setattr("video_understanding.ai.scene.SceneDetectorFactory", scene_factory)
    monkeypatch.setattr("video_understanding.storage.vector.VectorStorageFactory", vector_factory)
    
    return {
        "scene_factory": scene_factory,
        "vector_factory": vector_factory
    }
```

## TDD Examples for Key Components

### Testing Twelve Labs Integration

```python
import pytest
import responses
from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetector, TwelveLabsConfig

class TestTwelveLabsIntegration:
    @pytest.fixture
    def detector(self):
        """Create a Twelve Labs scene detector."""
        config = TwelveLabsConfig(
            api_key="test_key",
            api_url="https://api.twelvelabs.io/v1"
        )
        return TwelveLabsSceneDetector(config)
    
    @responses.activate
    async def test_full_detection_flow(self, detector, sample_video_path):
        """Test the full scene detection flow."""
        # Mock video upload
        responses.add(
            responses.POST,
            "https://api.twelvelabs.io/v1/upload",
            json={"task_id": "test_task"},
            status=200
        )
        
        # Mock task status check - processing
        responses.add(
            responses.GET,
            "https://api.twelvelabs.io/v1/tasks/test_task",
            json={"status": "processing"},
            status=200
        )
        
        # Mock task status check - completed
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
                    {
                        "start": 0.0,
                        "end": 10.5,
                        "confidence": 0.95
                    },
                    {
                        "start": 10.5,
                        "end": 15.2,
                        "confidence": 0.92
                    }
                ]
            },
            status=200
        )
        
        # Act
        scenes = await detector.detect_scenes(str(sample_video_path))
        
        # Assert
        assert len(scenes) == 2
        assert scenes[0]["start"] == 0.0
        assert scenes[0]["end"] == 10.5
        assert scenes[0]["confidence"] == 0.95
        assert scenes[1]["start"] == 10.5
        assert scenes[1]["end"] == 15.2
        assert scenes[1]["confidence"] == 0.92
```

### Testing Pinecone Integration

```python
import pytest
from unittest.mock import patch, MagicMock
import numpy as np
from video_understanding.storage.vector.pinecone import PineconeVectorStorage, PineconeConfig

class TestPineconeIntegration:
    @pytest.fixture
    def config(self):
        """Create Pinecone configuration."""
        return PineconeConfig(
            api_key="test_key",
            environment="test-env",
            index_name="test-index"
        )
    
    @pytest.fixture
    def mock_pinecone(self, monkeypatch):
        """Create mock Pinecone client."""
        mock_index = MagicMock()
        mock_pinecone = MagicMock()
        mock_pinecone.list_indexes.return_value = ["test-index"]
        mock_pinecone.Index.return_value = mock_index
        
        monkeypatch.setattr("video_understanding.storage.vector.pinecone.pinecone", mock_pinecone)
        
        return {
            "pinecone": mock_pinecone,
            "index": mock_index
        }
    
    def test_initialization(self, config, mock_pinecone):
        """Test Pinecone initialization."""
        # Act
        storage = PineconeVectorStorage(config)
        
        # Assert
        mock_pinecone["pinecone"].init.assert_called_once_with(
            api_key="test_key",
            environment="test-env"
        )
        mock_pinecone["pinecone"].Index.assert_called_once_with("test-index")
        assert storage.index == mock_pinecone["index"]
    
    def test_add_vectors(self, config, mock_pinecone):
        """Test adding vectors to Pinecone."""
        # Arrange
        storage = PineconeVectorStorage(config)
        vectors = [np.random.rand(1536) for _ in range(3)]
        ids = ["id1", "id2", "id3"]
        metadata = [{"key": "value1"}, {"key": "value2"}, {"key": "value3"}]
        
        # Act
        result = storage.add_vectors(vectors, ids, metadata)
        
        # Assert
        assert result is True
        mock_pinecone["index"].upsert.assert_called_once()
    
    def test_search_vectors(self, config, mock_pinecone):
        """Test searching vectors in Pinecone."""
        # Arrange
        storage = PineconeVectorStorage(config)
        query_vector = np.random.rand(1536)
        
        # Mock query response
        mock_response = {
            "matches": [
                {"id": "id1", "score": 0.95, "metadata": {"key": "value1"}},
                {"id": "id2", "score": 0.85, "metadata": {"key": "value2"}}
            ]
        }
        mock_pinecone["index"].query.return_value = mock_response
        
        # Act
        results = storage.search_vectors(query_vector, limit=2)
        
        # Assert
        assert len(results) == 2
        assert results[0]["id"] == "id1"
        assert results[0]["score"] == 0.95
        assert results[0]["metadata"]["key"] == "value1"
        
        mock_pinecone["index"].query.assert_called_once_with(
            vector=query_vector.tolist(),
            top_k=2,
            namespace=None,
            include_metadata=True
        )
```

## Common Test Scenarios

### Test API Error Handling

```python
import pytest
import responses
from video_understanding.ai.scene.twelve_labs import TwelveLabsSceneDetector, TwelveLabsConfig, APIError

class TestAPIErrorHandling:
    @pytest.fixture
    def detector(self):
        """Create a Twelve Labs scene detector."""
        config = TwelveLabsConfig(
            api_key="test_key",
            api_url="https://api.twelvelabs.io/v1",
            retries=1
        )
        return TwelveLabsSceneDetector(config)
    
    @responses.activate
    async def test_api_error_handling(self, detector):
        """Test API error handling."""
        # Mock API error
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
    
    @responses.activate
    async def test_retry_logic(self, detector):
        """Test retry logic for transient errors."""
        # Mock first attempt - server error
        responses.add(
            responses.POST,
            "https://api.twelvelabs.io/v1/upload",
            json={"error": "Server error"},
            status=500
        )
        
        # Mock second attempt - success
        responses.add(
            responses.POST,
            "https://api.twelvelabs.io/v1/upload",
            json={"task_id": "test_task"},
            status=200
        )
        
        # Mock remaining API calls for success path
        responses.add(
            responses.GET,
            "https://api.twelvelabs.io/v1/tasks/test_task",
            json={"status": "completed"},
            status=200
        )
        
        responses.add(
            responses.GET,
            "https://api.twelvelabs.io/v1/results/test_task",
            json={"scenes": []},
            status=200
        )
        
        # Act
        await detector.detect_scenes("test_video.mp4")
        
        # Assert
        assert len(responses.calls) >= 3  # Upload (x2) + task status + results
```

### Test Circuit Breaker Pattern

```python
import pytest
from unittest.mock import patch, MagicMock
from video_understanding.utils.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError

class TestCircuitBreaker:
    @pytest.fixture
    def circuit_breaker(self):
        """Create a circuit breaker with low threshold for testing."""
        return CircuitBreaker(failure_threshold=2, reset_timeout=0.1)
    
    async def test_successful_execution(self, circuit_breaker):
        """Test successful function execution."""
        # Arrange
        mock_func = MagicMock()
        mock_func.return_value = "success"
        
        # Act
        result = await circuit_breaker.execute(mock_func, "arg1", kwarg1="value1")
        
        # Assert
        assert result == "success"
        mock_func.assert_called_once_with("arg1", kwarg1="value1")
        assert circuit_breaker.failure_count == 0
        assert not circuit_breaker.is_open
    
    async def test_circuit_opens_after_failures(self, circuit_breaker):
        """Test circuit opens after multiple failures."""
        # Arrange
        mock_func = MagicMock()
        mock_func.side_effect = Exception("Test error")
        
        # Act & Assert - First failure
        with pytest.raises(Exception):
            await circuit_breaker.execute(mock_func)
        
        assert circuit_breaker.failure_count == 1
        assert not circuit_breaker.is_open
        
        # Act & Assert - Second failure opens circuit
        with pytest.raises(Exception):
            await circuit_breaker.execute(mock_func)
        
        assert circuit_breaker.failure_count == 2
        assert circuit_breaker.is_open
        
        # Act & Assert - With circuit open
        with pytest.raises(CircuitBreakerOpenError):
            await circuit_breaker.execute(mock_func)
    
    async def test_circuit_resets_after_timeout(self, circuit_breaker):
        """Test circuit resets after timeout."""
        # Arrange
        mock_func = MagicMock()
        mock_func.side_effect = [Exception("Error"), "success"]
        
        # Open the circuit
        circuit_breaker.failure_count = 2
        circuit_breaker.is_open = True
        circuit_breaker.last_failure_time = 0  # Ensure timeout has passed
        
        # Act
        result = await circuit_breaker.execute(mock_func)
        
        # Assert
        assert result == "success"
        assert circuit_breaker.failure_count == 0
        assert not circuit_breaker.is_open
```

## End-to-End Testing

```python
import pytest
from video_understanding.processor import VideoProcessor
from video_understanding.ai.scene import SceneDetectorFactory
from video_understanding.storage.vector import VectorStorageFactory
from video_understanding.query import QueryEngine

class TestEndToEnd:
    @pytest.fixture
    def processor(self):
        """Create a video processor."""
        return VideoProcessor()
    
    @pytest.fixture
    def scene_detector(self):
        """Create a scene detector."""
        config = {"type": "twelve_labs", "api_key": "test_key"}
        return SceneDetectorFactory.create(config)
    
    @pytest.fixture
    def vector_storage(self):
        """Create a vector storage."""
        config = {"type": "pinecone", "api_key": "test_key", "environment": "test", "index_name": "test-index"}
        return VectorStorageFactory.create(config)
    
    @pytest.fixture
    def query_engine(self, vector_storage):
        """Create a query engine."""
        return QueryEngine(vector_storage)
    
    @pytest.mark.skip(reason="End-to-end test requires real APIs")
    async def test_full_video_processing_flow(self, processor, scene_detector, vector_storage, query_engine, sample_video_path):
        """Test the full video processing flow."""
        # Process video
        video_data = processor.process(str(sample_video_path))
        
        # Detect scenes
        scenes = await scene_detector.detect_scenes(str(sample_video_path))
        
        # Convert scenes to vectors and store
        vectors = [scene.get("embedding") for scene in scenes]
        ids = [f"scene_{i}" for i in range(len(scenes))]
        metadata = [{"start": scene["start"], "end": scene["end"]} for scene in scenes]
        
        await vector_storage.add_vectors(vectors, ids, metadata)
        
        # Query for a scene with natural language
        query = "Find scenes with people talking"
        results = await query_engine.search(query)
        
        # Assert
        assert len(results) > 0
        assert "start" in results[0]["metadata"]
        assert "end" in results[0]["metadata"]
```