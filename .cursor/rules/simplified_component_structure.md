# Vidst Refactoring - Simplified Component Structure

## When to apply
@semantics Applies when creating or implementing components for the Vidst POC.
@files src/video_understanding/**/*.py
@userMessages ".*create component.*" ".*implement.*component.*" ".*component structure.*"

## Simple Component Structure

This rule provides straightforward guidance for structuring components in the Vidst POC refactoring project.

## Basic Component Pattern

All components should follow this simple structure:

```python
# Simple component implementation
class SceneDetector:
    """Component for detecting scenes in videos."""
    
    def __init__(self, config=None):
        """Initialize with optional configuration."""
        self.config = config or {}
        
    async def detect_scenes(self, video_path):
        """Detect scenes in a video.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of detected scenes
        """
        try:
            # Implementation goes here
            pass
        except Exception as e:
            print(f"Error detecting scenes: {str(e)}")
            return []
```

## Basic Component Types

For the POC, focus on these basic component types:

1. **API Clients** - Connect to external services like Twelve Labs
2. **Storage Components** - Handle data storage like Pinecone
3. **Processing Components** - Process data (OCR, transcription)
4. **Integration Components** - Connect different services together

## Simple Error Handling

```python
# Simple error handling
try:
    # Call API or process data
    result = api.call_endpoint()
    
    # Check for empty or invalid results
    if not result:
        print("Warning: Empty result received")
        return []
        
    return result
    
except Exception as e:
    # Log error and return empty result
    print(f"Error: {str(e)}")
    return []
```

## Simple Service Selection

Instead of complex factories, use simple if-else service selection:

```python
def get_scene_detector(detector_type="twelve_labs"):
    """Get scene detector based on type."""
    if detector_type == "twelve_labs":
        return TwelveLabsSceneDetector()
    elif detector_type == "opencv":
        return OpenCVSceneDetector()
    else:
        # Default to Twelve Labs
        return TwelveLabsSceneDetector()
```

## Configuration Simplification

```python
# Simple configuration using dictionaries
def create_config(api_key=None, **kwargs):
    """Create a simple configuration dictionary."""
    config = {
        "api_key": api_key or os.environ.get("API_KEY"),
        "timeout": 30,
        "retries": 3
    }
    
    # Update with any additional parameters
    config.update(kwargs)
    
    return config
```

## Component Implementation Checklist

When implementing components for the POC, ensure:

1. ✓ Component performs the core functionality required
2. ✓ Error handling is in place, but kept simple
3. ✓ Configuration is straightforward and documented
4. ✓ Functions have clear docstrings explaining parameters
5. ✓ Component meets the minimum viable requirements

## Example: Simplified Scene Detector

```python
class TwelveLabsSceneDetector:
    """Scene detector using Twelve Labs API."""
    
    def __init__(self, api_key=None):
        """Initialize with API key."""
        self.api_key = api_key or os.environ.get("TWELVE_LABS_API_KEY")
        if not self.api_key:
            raise ValueError("Twelve Labs API key not provided")
            
        # Initialize client
        self.client = self._create_client()
        
    def _create_client(self):
        """Create Twelve Labs client."""
        import twelvelabs
        return twelvelabs.Client(api_key=self.api_key)
        
    async def detect_scenes(self, video_path):
        """Detect scenes in a video.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of scenes with timestamps
        """
        try:
            # Upload video
            task = await self.client.upload_video(video_path)
            
            # Wait for processing
            result = await self.client.wait_for_task(task["task_id"])
            
            # Extract scenes
            scenes = result.get("scenes", [])
            
            # Format scene information
            formatted_scenes = []
            for scene in scenes:
                formatted_scenes.append({
                    "start_time": scene.get("start_time"),
                    "end_time": scene.get("end_time"),
                    "description": scene.get("description", "")
                })
                
            return formatted_scenes
            
        except Exception as e:
            print(f"Error detecting scenes: {str(e)}")
            return []
```
