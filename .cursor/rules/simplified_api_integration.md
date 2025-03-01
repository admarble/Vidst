# Vidst Refactoring - Simplified API Integration Guide

## When to apply
@semantics Applies to API integration related tasks, especially when working with Twelve Labs, Pinecone, Document AI, or any external API service.
@files src/video_understanding/ai/**/*.py src/video_understanding/storage/vector/*.py

## API Integration Simplified Guide

This rule provides simple guidance for implementing API integrations for the Vidst refactoring project, focusing on the minimum viable implementation for the POC.

## Core Principles

1. **Keep It Simple**
   - Focus on making it work, not making it perfect
   - Stick to the simplest implementation that meets requirements
   - Avoid complex patterns unless absolutely necessary

2. **Refer to Minimum Viable Component Definitions**
   - Always check the [Minimum Viable Component Definitions](/Users/tony/Documents/Vidst/refactor/02_planning/vidst_minimum_viable_components.md) document
   - Implement only what's defined as "Minimum Viable Implementation"
   - Skip anything listed as "Out of Scope for POC"

## Basic API Structure

```python
# Simple API client for Twelve Labs integration
class TwelveLabsClient:
    def __init__(self, api_key):
        """Initialize with API key."""
        self.api_key = api_key
        self.api_url = "https://api.twelvelabs.io/v1"
        
    async def detect_scenes(self, video_path):
        """Detect scenes in a video using Twelve Labs API."""
        try:
            # Basic implementation
            import twelvelabs
            client = twelvelabs.Client(api_key=self.api_key)
            
            # Process video and get results
            result = await client.analyze_video(video_path)
            
            # Return scenes in simple format
            return result.get("scenes", [])
            
        except Exception as e:
            # Simple error handling
            print(f"Error detecting scenes: {str(e)}")
            return []
```

## Simple Error Handling

```python
# Simple retry function - avoid complex retry patterns
def simple_retry(func, max_retries=3):
    """Simple retry function for API calls."""
    async def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                print(f"Retry {attempt + 1}/{max_retries} after error: {str(e)}")
                await asyncio.sleep(1)  # Simple delay between retries
    return wrapper

# Usage
@simple_retry(max_retries=3)
async def call_api(client, request):
    return await client.execute(request)
```

## Simple Configuration

```python
# Simple configuration without Pydantic
class SimpleConfig:
    """Simple configuration class."""
    def __init__(self, **kwargs):
        """Initialize with keyword arguments."""
        for key, value in kwargs.items():
            setattr(self, key, value)
```

## Pinecone Integration Example

```python
# Simple Pinecone integration
class PineconeStorage:
    """Simple Pinecone vector storage."""
    
    def __init__(self, api_key, environment, index_name):
        """Initialize Pinecone storage."""
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self._initialize()
        
    def _initialize(self):
        """Initialize Pinecone."""
        import pinecone
        pinecone.init(api_key=self.api_key, environment=self.environment)
        
        # Get or create index
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(name=self.index_name, dimension=1536)
            
        self.index = pinecone.Index(self.index_name)
        
    def add_vectors(self, vectors, ids, metadata=None):
        """Add vectors to Pinecone."""
        try:
            # Prepare vectors
            items = []
            for i, (vector, id_) in enumerate(zip(vectors, ids)):
                item = (id_, vector.tolist())
                if metadata and i < len(metadata):
                    item += (metadata[i],)
                items.append(item)
                
            # Add vectors to Pinecone
            self.index.upsert(vectors=items)
            return True
        except Exception as e:
            print(f"Error adding vectors: {str(e)}")
            return False
            
    def search(self, query_vector, top_k=10):
        """Search vectors in Pinecone."""
        try:
            return self.index.query(vector=query_vector.tolist(), top_k=top_k)
        except Exception as e:
            print(f"Error searching vectors: {str(e)}")
            return []
```

## Simple Service Selection

```python
# Simple service selection instead of factories
def get_ocr_service(service_type, config):
    """Get OCR service based on type."""
    if service_type == "document_ai":
        from video_understanding.ai.ocr.document_ai import DocumentAIService
        return DocumentAIService(config)
    elif service_type == "easyocr":
        from video_understanding.ai.ocr.easyocr import EasyOCRService
        return EasyOCRService(config)
    else:
        raise ValueError(f"Unknown OCR service type: {service_type}")
```

## Testing Approach

```python
# Simple test for API
def test_twelve_labs_api():
    """Simple test for Twelve Labs API."""
    import os
    client = TwelveLabsClient(api_key=os.environ.get("TWELVE_LABS_API_KEY"))
    
    # Mock data for testing
    class MockResponse:
        def json(self):
            return {"scenes": [{"start_time": 0, "end_time": 10}]}
            
    # Mock the API call
    with unittest.mock.patch("requests.post", return_value=MockResponse()):
        result = client.detect_scenes("test_video.mp4")
        
    assert len(result) > 0
```

## Keeping Focus on POC Requirements

Remember these guidelines when implementing:

1. **Focus on End-to-End Functionality** - Get the complete flow working first, then improve
2. **Skip Advanced Features** - If it's listed as "Out of Scope for POC", don't implement it
3. **Use Simple Error Handling** - Skip complex circuit breakers; basic try/except is sufficient
4. **Prioritize Accuracy and Performance** - Focus on meeting the defined accuracy targets
5. **Document Limitations** - Note limitations rather than trying to solve every edge case
