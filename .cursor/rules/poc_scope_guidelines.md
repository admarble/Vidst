# Vidst Refactoring - POC Scope Guidelines

## When to apply
@semantics Applies to all code changes to ensure they stay within the defined POC scope.
@files src/video_understanding/**/*.py
@userMessages ".*scope.*" ".*feature.*" ".*implement.*" ".*enhance.*" ".*improve.*"

## POC Scope Guidelines

This rule provides guidance to ensure your implementation stays within the defined scope for the proof-of-concept (POC).

## Check Against Minimum Viable Definitions

Always check your implementation against the [Minimum Viable Component Definitions](/Users/tony/Documents/Vidst/refactor/02_planning/vidst_minimum_viable_components.md) document.

## Key POC Principles

1. **Focus on Proving Core Functionality** - The POC's purpose is to demonstrate the core value proposition, not to build a production-ready system

2. **Simplicity Over Elegance** - Choose simpler implementations over architecturally elegant solutions

3. **Prefer Working Over Perfect** - A working implementation with limitations is better than a perfect implementation that's incomplete

4. **Meet Accuracy Targets** - Focus on meeting the defined accuracy targets (e.g., 90% for scene detection)

## Scope Checking Questions

Before implementing a feature, ask yourself:

1. Is this feature explicitly listed in the Minimum Viable Implementation?
2. Is it necessary to demonstrate the core value proposition?
3. Will it take significant time that could be spent on more critical features?
4. Is it listed as "Out of Scope for POC"?

## In-Scope vs. Out-of-Scope Examples

### Scene Detection

✅ **In-Scope**:
- Basic scene boundary detection
- 90%+ accuracy for major scene changes
- Simple timestamp format

❌ **Out-of-Scope**:
- Advanced scene classification
- Shot composition analysis
- Complex metadata extraction

### Vector Storage

✅ **In-Scope**:
- Basic vector storage and retrieval
- Simple metadata filtering
- Basic search functionality

❌ **Out-of-Scope**:
- Complex query optimization
- Advanced filtering capabilities
- Hybrid search implementations
- Extensive performance tuning

## Scope Management in Code

### Add Comments for Scope Decisions

```python
# In-scope: Basic scene detection
def detect_basic_scenes(video_path):
    # Implementation...
    pass
    
# Out-of-scope for POC: Scene classification
# TODO: Implement in future phase if needed
# def classify_scenes(scenes):
#     pass
```

### Simplify Complex Features

```python
# Simplified implementation for POC
def extract_text(image):
    """Extract text from image for POC.
    
    Note: This is a simplified implementation for the POC.
    Future enhancements could include:
    - Text layout analysis
    - Multiple language support
    - Handwriting recognition
    """
    # Simple implementation for POC
    try:
        # Use Document AI for basic text extraction
        text = document_ai.extract_text(image)
        return text
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return ""
```

## Documenting Future Enhancements

If you identify potential enhancements that are out of scope:

1. Document them in code comments
2. Add them to the project's future enhancements list
3. Do not implement them in the current POC phase

```python
def search_videos(query, top_k=10):
    """Search videos based on query.
    
    Args:
        query: Text query
        top_k: Number of results to return
        
    Returns:
        List of matching video segments
        
    Future Enhancements:
    - Conversational search (out of scope for POC)
    - Query refinement (out of scope for POC)
    - Advanced relevance tuning (out of scope for POC)
    """
    # Simple implementation for POC
    # ...
```

## Getting Help with Scope Decisions

If you're unsure whether a feature is in scope:

1. Check the Minimum Viable Component Definitions document
2. Ask during daily standup
3. Add the `scope:creep` tag to the issue for team discussion

## Remember

- The goal is a working POC that demonstrates value, not a perfect implementation
- You can always add features later after the core functionality is proven
- Stay focused on the critical path to completion
