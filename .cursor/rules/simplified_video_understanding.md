# Simplified Video Understanding Guide for POC

## When to apply
@semantics Applies to all video understanding components and development for the POC phase.
@files src/video_understanding/**/*.py
@userMessages ".*video.*" ".*ai model.*" ".*understanding.*" ".*video analysis.*"

## Project Overview

This is a proof-of-concept (POC) system for analyzing educational and technical video content using AI services. The focus is on demonstrating core functionality, not building a production-ready system.

## Essential Guidelines

### Code Basics

- Python 3.10+
- List dependencies in `requirements.txt`
- Use type hints for clarity
- Add brief comments for complex logic

### Project Structure

```
src/
├── core/          # Core processing components
├── ai/            # AI model integration 
└── storage/       # Data persistence
```

### Component Development

- Keep components simple and focused
- Use clear method names
- Implement basic error handling with try/except
- Add docstrings for main functions

### Essential Testing

- Test core functionality (not 100% coverage)
- Focus on integration tests over unit tests
- Mock external API calls

### Performance Targets

- Process videos within 2x video duration
- Query response time < 2 seconds
- Memory use under 4GB per job

### API Integration

Support for these external services:
- Twelve Labs (for scene detection)
- Pinecone (for vector storage)
- Google Document AI (for OCR)
- Whisper (for transcription)

### Simple Error Handling

```python
# Simple error handling approach
try:
    # Process video
    result = process_video(video_path)
    return result
except Exception as e:
    # Log error and return failure
    print(f"Error processing video: {e}")
    return {"status": "error", "message": str(e)}
```

### Basic Documentation

Add simple docstrings that explain:
- What the function does
- Parameters and return values
- Basic example usage

```python
def process_video(file_path: str) -> dict:
    """Process a video file to extract scenes, text and transcription.
    
    Args:
        file_path: Path to the video file
        
    Returns:
        Dictionary with scenes, text and transcription data
    """
    # Implementation
```

### Success Metrics

Focus on these key metrics:
- Scene Detection Accuracy: >90%
- OCR Accuracy: >95%
- Speech Transcription Accuracy: >95%
- Processing Speed: Maximum 2x video duration
- Query Response Time: <2 seconds

### Git Basics

- Descriptive commit messages
- Push changes regularly
- Reference issue numbers if applicable

## POC Implementation Checklist

For each component, ensure:

1. **Basic Functionality**
   - Implements core requirements defined in Minimum Viable Components
   - Handles common error cases
   - Returns results in expected format

2. **API Integration**
   - Successfully connects to required external APIs
   - Handles authentication properly
   - Implements minimal retry logic for failures

3. **Testing**
   - Has basic integration tests
   - Validates accuracy requirements
   - Tests the "happy path" workflow

4. **Documentation**
   - Includes basic docstrings
   - Documents any configuration requirements
   - Notes any known limitations

## Out of Scope for POC

The following are **not** required for the POC:
- Comprehensive error handling for all edge cases
- Advanced monitoring and metrics
- CI/CD pipeline setup
- Extensive documentation
- Optimized performance beyond basic requirements
- Complex data management strategies
- Sophisticated logging systems

## Implementation Examples

### Scene Detection Client

```python
# Simple Twelve Labs client for scene detection
class TwelveLabsClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.twelvelabs.io/v1"
        
    async def detect_scenes(self, video_path):
        """Detect scenes in a video using Twelve Labs API."""
        try:
            # Initialize client
            import twelvelabs
            client = twelvelabs.Client(api_key=self.api_key)
            
            # Process video
            result = await client.analyze_video(video_path)
            
            # Return scenes in simple format
            return result.get("scenes", [])
            
        except Exception as e:
            print(f"Error detecting scenes: {str(e)}")
            return []
```

### Video Processor

```python
class VideoProcessor:
    """Simple processor for video content."""
    
    def __init__(self, scene_detector, ocr_service, transcription_service):
        self.scene_detector = scene_detector
        self.ocr_service = ocr_service
        self.transcription_service = transcription_service
        
    async def process_video(self, video_path):
        """Process a video file to extract information.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary with extracted information
        """
        try:
            # Detect scenes
            scenes = await self.scene_detector.detect_scenes(video_path)
            
            # Extract key frames
            frames = extract_key_frames(video_path, scenes)
            
            # Perform OCR on frames
            text_content = []
            for frame in frames:
                text = await self.ocr_service.extract_text(frame)
                if text:
                    text_content.append({
                        "timestamp": frame["timestamp"],
                        "text": text
                    })
            
            # Transcribe audio
            transcription = await self.transcription_service.transcribe(video_path)
            
            # Return combined results
            return {
                "scenes": scenes,
                "text_content": text_content,
                "transcription": transcription
            }
            
        except Exception as e:
            print(f"Error processing video: {str(e)}")
            return {"status": "error", "message": str(e)}
```

## Remember

The goal of the POC is to demonstrate core functionality and validate the approach, not to build a production-ready system. Focus on proving that the concept works with the target accuracy and performance metrics.
