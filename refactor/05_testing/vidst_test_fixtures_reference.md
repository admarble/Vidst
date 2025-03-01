# Vidst Test Fixtures Reference

## Document Status

| Version | Date | Author | Status |
|---------|------|--------|--------|
| 1.0 | February 26, 2025 | Vidst Team | Draft |

**Related Documents:**
- [Vidst TDD Testing Strategy](./vidst_tdd_testing_strategy.md)
- [Vidst TDD Implementation Guide](./vidst_tdd_implementation_guide.md)
- [Vidst Refactoring Master Plan](../vidst_refactoring_master_plan.md)

## 1. Introduction

This document provides a comprehensive reference for the test fixtures, mock responses, and test data used in the Vidst refactoring project. It serves as a catalog and guide for creating, maintaining, and using test fixtures across the test suite.

### Purpose

Test fixtures are essential for effective testing, particularly when integrating with external APIs. This reference aims to:

- Document all available test fixtures and their purposes
- Provide sample mock responses for external APIs
- Establish conventions for creating and organizing test fixtures
- Guide developers in creating new fixtures when needed

## 2. Test Fixture Directory Structure

Test fixtures are organized in the following directory structure:

```
tests/
├── fixtures/                      # Root fixtures directory
│   ├── video_samples/             # Test video files
│   │   ├── valid/                 # Valid video files for testing
│   │   └── invalid/               # Invalid video files for testing
│   ├── text_samples/              # Test images with text for OCR
│   │   ├── english/               # English text samples
│   │   └── multilingual/          # Multilingual text samples
│   ├── audio_samples/             # Test audio files
│   │   ├── clean/                 # Clean audio samples
│   │   └── noisy/                 # Audio with background noise
│   └── mock_responses/            # Mock API responses
│       ├── twelve_labs/           # Twelve Labs API mock responses
│       ├── pinecone/              # Pinecone API mock responses
│       └── document_ai/           # Google Document AI mock responses
└── utils/                         # Test utilities
    ├── mock_factory.py            # Factory for creating mock responses
    └── fixture_helpers.py         # Helper functions for fixtures
```

## 3. Video Test Fixtures

### 3.1 Sample Video Files

The project includes several sample video files for testing:

| Filename | Duration | Resolution | Features | Purpose |
|----------|----------|------------|----------|---------|
| short_test_video.mp4 | 30 sec | 720p | Multiple scenes, spoken content | General testing |
| long_test_video.mp4 | 5 min | 1080p | Complex scenes, dialog | Performance testing |
| text_heavy_video.mp4 | 1 min | 720p | On-screen text | OCR testing |
| no_audio_video.mp4 | 45 sec | 720p | No audio track | Audio fallback testing |
| multi_speaker_video.mp4 | 2 min | 720p | Multiple speakers | Speaker diarization |

### 3.2 Scene Detection Ground Truth

For testing scene detection accuracy, ground truth scene boundaries are provided in JSON format:

```json
// tests/fixtures/video_samples/ground_truth/short_test_video_scenes.json
{
  "video": "short_test_video.mp4",
  "scenes": [
    {"start": 0.0, "end": 5.32, "description": "Introduction title card"},
    {"start": 5.32, "end": 12.18, "description": "Person speaking to camera"},
    {"start": 12.18, "end": 18.75, "description": "Product demonstration"},
    {"start": 18.75, "end": 25.2, "description": "Charts and diagrams"},
    {"start": 25.2, "end": 30.0, "description": "Closing scene"}
  ]
}
```

### 3.3 Usage Examples

To use video fixtures in tests:

```python
# In test files
import pytest
from pathlib import Path

@pytest.fixture
def test_video_path():
    """Path to a short test video file."""
    return Path("tests/fixtures/video_samples/valid/short_test_video.mp4")

def test_video_processing(test_video_path):
    """Test video processing with sample video."""
    # Use test_video_path in the test
    assert test_video_path.exists()
```

## 4. Twelve Labs API Mock Responses

### 4.1 Video Analysis Response

Sample response for the `analyze_video` method:

```json
// tests/fixtures/mock_responses/twelve_labs/analyze_video_response.json
{
  "index_id": "mock-index-123456",
  "status": "ready",
  "task_id": "mock-task-789012",
  "metadata": {
    "video_size": 15482789,
    "video_duration": 30.5,
    "created_at": "2025-02-26T14:30:00Z"
  }
}
```

### 4.2 Scene Detection Response

Sample response for the `detect_scenes` method:

```json
// tests/fixtures/mock_responses/twelve_labs/scene_detection_response.json
{
  "groups": [
    {
      "start_time": 0.0,
      "end_time": 5.32,
      "confidence": 0.94,
      "thumbnail_url": "https://example.com/thumb1.jpg"
    },
    {
      "start_time": 5.32,
      "end_time": 12.18,
      "confidence": 0.91,
      "thumbnail_url": "https://example.com/thumb2.jpg"
    },
    {
      "start_time": 12.18,
      "end_time": 18.75,
      "confidence": 0.89,
      "thumbnail_url": "https://example.com/thumb3.jpg"
    },
    {
      "start_time": 18.75,
      "end_time": 25.2,
      "confidence": 0.92,
      "thumbnail_url": "https://example.com/thumb4.jpg"
    },
    {
      "start_time": 25.2,
      "end_time": 30.0,
      "confidence": 0.95,
      "thumbnail_url": "https://example.com/thumb5.jpg"
    }
  ]
}
```

### 4.3 Video Search Response

Sample response for the `search_video` method:

```json
// tests/fixtures/mock_responses/twelve_labs/search_video_response.json
{
  "data": [
    {
      "start_time": 5.32,
      "end_time": 12.18,
      "score": 0.87,
      "text": "person speaking to camera about the product features",
      "thumbnail_url": "https://example.com/thumb2.jpg"
    },
    {
      "start_time": 12.18,
      "end_time": 18.75,
      "score": 0.82,
      "text": "demonstration of the product in use",
      "thumbnail_url": "https://example.com/thumb3.jpg"
    }
  ]
}
```

###.4.4 Summary Generation Response

Sample response for the `generate_summary` method:

```json
// tests/fixtures/mock_responses/twelve_labs/summary_response.json
{
  "data": {
    "text": "The video presents a product demonstration starting with an introduction title card. A presenter explains the key features of the product, followed by a hands-on demonstration showing how it works. Charts and diagrams illustrate the product's performance advantages. The video concludes with a call to action and contact information."
  }
}
```

### 4.5 Error Response Examples

Sample error responses for different error conditions:

```json
// tests/fixtures/mock_responses/twelve_labs/error_unauthorized.json
{
  "error": {
    "code": 401,
    "message": "Unauthorized access. Invalid API key provided."
  }
}

// tests/fixtures/mock_responses/twelve_labs/error_video_processing.json
{
  "error": {
    "code": 422,
    "message": "Could not process video. Invalid format or corrupted file."
  }
}

// tests/fixtures/mock_responses/twelve_labs/error_rate_limit.json
{
  "error": {
    "code": 429,
    "message": "Rate limit exceeded. Please try again later."
  }
}
```

### 4.6 Using Twelve Labs Mocks

Example of using mock responses in tests:

```python
# tests/utils/mock_factory.py
import json
from pathlib import Path

class TwelveLabsMocks:
    """Factory for Twelve Labs mock responses."""
    
    @staticmethod
    def load_response(filename):
        """Load a mock response from a JSON file."""
        path = Path("tests/fixtures/mock_responses/twelve_labs") / filename
        with open(path, "r") as f:
            return json.load(f)
    
    @staticmethod
    def analyze_video_response(success=True):
        """Get mock analyze_video response."""
        if success:
            return TwelveLabsMocks.load_response("analyze_video_response.json")
        else:
            return TwelveLabsMocks.load_response("error_video_processing.json")
    
    @staticmethod
    def scene_detection_response():
        """Get mock scene detection response."""
        return TwelveLabsMocks.load_response("scene_detection_response.json")
    
    @staticmethod
    def search_video_response(query="product"):
        """Get mock search response for a query."""
        return TwelveLabsMocks.load_response("search_video_response.json")
    
    @staticmethod
    def summary_response():
        """Get mock summary generation response."""
        return TwelveLabsMocks.load_response("summary_response.json")
```

Using in tests:

```python
from tests.utils.mock_factory import TwelveLabsMocks
from unittest.mock import patch, MagicMock

def test_analyze_video_with_mock():
    """Test analyze_video with mock response."""
    mock_response = TwelveLabsMocks.analyze_video_response()
    
    # Use mock response in test
    with patch("twelvelabs.Client") as mock_client:
        client_instance = MagicMock()
        mock_client.return_value = client_instance
        
        # Configure mock task
        task = MagicMock()
        task.index_id = mock_response["index_id"]
        task.status = mock_response["status"]
        task.id = mock_response["task_id"]
        
        client_instance.index.create.return_value = task
        
        # Test implementation
```

## 5. Pinecone API Mock Responses

### 5.1 Vector Storage Responses

Sample responses for vector operations:

```json
// tests/fixtures/mock_responses/pinecone/upsert_response.json
{
  "upserted_count": 5
}

// tests/fixtures/mock_responses/pinecone/query_response.json
{
  "matches": [
    {
      "id": "vec1",
      "score": 0.92,
      "metadata": {
        "text": "person speaking to camera",
        "start_time": 5.32,
        "end_time": 12.18
      }
    },
    {
      "id": "vec2",
      "score": 0.85,
      "metadata": {
        "text": "product demonstration",
        "start_time": 12.18,
        "end_time": 18.75
      }
    },
    {
      "id": "vec3",
      "score": 0.78,
      "metadata": {
        "text": "charts and diagrams",
        "start_time": 18.75,
        "end_time": 25.2
      }
    }
  ],
  "namespace": "default"
}

// tests/fixtures/mock_responses/pinecone/delete_response.json
{
  "deleted_count": 3
}
```

### 5.2 Pinecone Mock Factory

Example mock factory for Pinecone:

```python
# tests/utils/mock_factory.py
class PineconeMocks:
    """Factory for Pinecone mock responses."""
    
    @staticmethod
    def load_response(filename):
        """Load a mock response from a JSON file."""
        path = Path("tests/fixtures/mock_responses/pinecone") / filename
        with open(path, "r") as f:
            return json.load(f)
    
    @staticmethod
    def upsert_response(count=5):
        """Get mock upsert response."""
        response = PineconeMocks.load_response("upsert_response.json")
        response["upserted_count"] = count
        return response
    
    @staticmethod
    def query_response(top_k=3):
        """Get mock query response."""
        response = PineconeMocks.load_response("query_response.json")
        response["matches"] = response["matches"][:top_k]
        return response
    
    @staticmethod
    def delete_response(count=3):
        """Get mock delete response."""
        response = PineconeMocks.load_response("delete_response.json")
        response["deleted_count"] = count
        return response
```

## 6. Document AI Mock Responses

### 6.1 Text Extraction Responses

Sample responses for OCR operations:

```json
// tests/fixtures/mock_responses/document_ai/process_document_response.json
{
  "document": {
    "text": "Vidst: Advanced Video Understanding\nTransform your video content with AI-powered analysis\nFeatures:\n- Scene detection\n- Content analysis\n- Natural language querying",
    "pages": [
      {
        "page_number": 1,
        "dimension": {
          "width": 1280,
          "height": 720
        },
        "blocks": [
          {
            "layout": {
              "text_anchor": {
                "text_segments": [
                  {
                    "start_index": 0,
                    "end_index": 36
                  }
                ]
              },
              "bounding_poly": {
                "vertices": [
                  {"x": 320, "y": 100},
                  {"x": 960, "y": 100},
                  {"x": 960, "y": 150},
                  {"x": 320, "y": 150}
                ]
              }
            },
            "text": "Vidst: Advanced Video Understanding"
          },
          {
            "layout": {
              "text_anchor": {
                "text_segments": [
                  {
                    "start_index": 37,
                    "end_index": 88
                  }
                ]
              },
              "bounding_poly": {
                "vertices": [
                  {"x": 320, "y": 170},
                  {"x": 960, "y": 170},
                  {"x": 960, "y": 220},
                  {"x": 320, "y": 220}
                ]
              }
            },
            "text": "Transform your video content with AI-powered analysis"
          }
        ]
      }
    ]
  }
}
```

### 6.2 Document AI Mock Factory

Example mock factory for Document AI:

```python
# tests/utils/mock_factory.py
class DocumentAIMocks:
    """Factory for Document AI mock responses."""
    
    @staticmethod
    def load_response(filename):
        """Load a mock response from a JSON file."""
        path = Path("tests/fixtures/mock_responses/document_ai") / filename
        with open(path, "r") as f:
            return json.load(f)
    
    @staticmethod
    def process_document_response():
        """Get mock process document response."""
        return DocumentAIMocks.load_response("process_document_response.json")
```

## 7. Test Audio Fixtures

### 7.1 Audio Samples

The project includes several audio samples for transcription testing:

| Filename | Duration | Features | Purpose |
|----------|----------|----------|---------|
| clean_speech.wav | 30 sec | Clear speech, single speaker | Basic transcription |
| noisy_speech.wav | 30 sec | Speech with background noise | Noise handling |
| multi_speaker.wav | 60 sec | Multiple speakers | Speaker diarization |
| music_speech.wav | 45 sec | Speech with music | Background separation |
| accented_speech.wav | 30 sec | Non-native English | Accent handling |

### 7.2 Transcription Ground Truth

For testing transcription accuracy, ground truth transcriptions are provided:

```json
// tests/fixtures/audio_samples/ground_truth/clean_speech_transcript.json
{
  "audio": "clean_speech.wav",
  "transcript": "Welcome to Vidst, the advanced video understanding platform. Our system combines multiple AI technologies to analyze and extract insights from your video content.",
  "segments": [
    {
      "start": 0.0,
      "end": 4.8,
      "text": "Welcome to Vidst, the advanced video understanding platform."
    },
    {
      "start": 4.8,
      "end": 13.2,
      "text": "Our system combines multiple AI technologies to analyze and extract insights from your video content."
    }
  ]
}
```

## 8. Mock Response Helpers

### 8.1 Mock Response Utility

To simplify working with mock responses, a utility class is provided:

```python
# tests/utils/mock_response.py
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union

class MockResponse:
    """Utility for managing mock API responses."""
    
    MOCK_DIR = Path("tests/fixtures/mock_responses")
    
    @staticmethod
    def load(service: str, response_type: str) -> Dict[str, Any]:
        """
        Load a mock response from a JSON file.
        
        Args:
            service: Service name (e.g., "twelve_labs", "pinecone")
            response_type: Type of response (e.g., "analyze_video_response")
            
        Returns:
            Dictionary containing the mock response
        """
        file_path = MockResponse.MOCK_DIR / service / f"{response_type}.json"
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Mock response not found: {file_path}")
    
    @staticmethod
    def modify(
        response: Dict[str, Any],
        path: str,
        value: Any
    ) -> Dict[str, Any]:
        """
        Modify a value in a mock response.
        
        Args:
            response: Original response dictionary
            path: Dot-separated path to the value (e.g., "matches.0.score")
            value: New value to set
            
        Returns:
            Modified response dictionary
        """
        result = response.copy()
        parts = path.split(".")
        
        # Navigate to the nested object
        current = result
        for i, part in enumerate(parts[:-1]):
            if part.isdigit():  # Handle array indices
                part = int(part)
            if i == len(parts) - 2:  # Last navigation step
                current[part] = value
            else:
                current = current[part]
        
        return result
    
    @staticmethod
    def create_error(
        service: str,
        code: int,
        message: str
    ) -> Dict[str, Any]:
        """
        Create a custom error response.
        
        Args:
            service: Service name
            code: Error code
            message: Error message
            
        Returns:
            Error response dictionary
        """
        if service == "twelve_labs":
            return {
                "error": {
                    "code": code,
                    "message": message
                }
            }
        elif service == "pinecone":
            return {
                "code": code,
                "message": message
            }
        elif service == "document_ai":
            return {
                "error": {
                    "code": code,
                    "message": message,
                    "status": "FAILED_PRECONDITION"
                }
            }
        else:
            return {
                "error": {
                    "code": code,
                    "message": message
                }
            }
```

### 8.2 Using the Mock Response Utility

Example of using the mock response utility in tests:

```python
from tests.utils.mock_response import MockResponse
from unittest.mock import patch, MagicMock

def test_search_with_mock():
    """Test video search with custom mock response."""
    # Load base response
    mock_response = MockResponse.load("twelve_labs", "search_video_response")
    
    # Modify a specific value
    mock_response = MockResponse.modify(mock_response, "data.0.score", 0.95)
    
    # Use in test
    with patch("twelvelabs.Client") as mock_client:
        client_instance = MagicMock()
        mock_client.return_value = client_instance
        client_instance.search.query.return_value = mock_response
        
        # Test implementation
```

## 9. Creating New Test Fixtures

This section provides guidelines for creating new test fixtures.

### 9.1 Video Fixtures

When adding new video fixtures:

1. Keep test videos short (preferably under 1 minute)
2. Use lower resolutions for faster processing (720p or lower)
3. Include a variety of content (scenes, text, speech)
4. Create corresponding ground truth data when applicable
5. Document the video's features and purpose

### 9.2 Mock Response Fixtures

When creating new mock responses:

1. Base them on actual API responses when possible
2. Use the following naming convention:
   - `<method_name>_response.json` for success responses
   - `error_<error_type>.json` for error responses
3. Include all relevant fields from the actual API response
4. Document any special handling required

### 9.3 Guidelines for Recording New API Responses

To record actual API responses for use as fixtures:

1. Create a simple recording script:
   ```python
   import json
   import asyncio
   from video_understanding.ai.models.twelve_labs_enhanced import TwelveLabsEnhancedModel
   
   async def record_response():
       """Record actual API responses for use as fixtures."""
       # Initialize with your API key
       model = TwelveLabsEnhancedModel(api_key="your_key_here")
       
       # Make the API call
       result = await model.analyze_video("tests/fixtures/video_samples/valid/short_test_video.mp4")
       
       # Save the response
       with open("analyze_video_response.json", "w") as f:
           json.dump(result, f, indent=2)
   
   if __name__ == "__main__":
       asyncio.run(record_response())
   ```

2. Run the script to record actual responses
3. Remove any sensitive information before committing
4. Place the recorded responses in the appropriate directory

## 10. Conclusion

This test fixtures reference provides a comprehensive catalog of the test fixtures, mock responses, and test data used in the Vidst refactoring project. By following the guidelines and using the provided utilities, developers can create consistent, effective tests that validate the refactored components.

For guidance on using these fixtures in tests, refer to the [Vidst TDD Implementation Guide](./vidst_tdd_implementation_guide.md).

When adding new fixtures or modifying existing ones, ensure they follow the conventions established in this document to maintain consistency across the test suite.
