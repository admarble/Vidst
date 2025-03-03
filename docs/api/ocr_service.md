# OCR Service Interface

## Overview

The OCR (Optical Character Recognition) service interface provides a standardized way to extract text from images and video frames. It abstracts away the details of specific OCR implementations, allowing for easy switching between different providers like Google Document AI or other OCR engines.

## Key Components

### BaseOCRService

The `BaseOCRService` class provides a standardized interface for OCR operations:

- **extract_text**: Extract text from a single image
- **batch_extract_text**: Extract text from multiple images
- **detect_tables**: Detect and extract tables from images
- **initialize**: Initialize the OCR service
- **shutdown**: Release resources used by the OCR service

### DocumentAIService

The `DocumentAIService` class implements the `BaseOCRService` interface using Google Document AI:

- **Google Cloud Integration**: Handles communication with Google Document AI
- **Error Handling**: Provides detailed error messages for API-specific errors
- **Confidence Scoring**: Provides confidence scores for extracted text
- **Layout Analysis**: Extracts text with position and layout information

### OCRServiceFactory

The `OCRServiceFactory` class provides a factory for creating OCR service instances:

- **Service Creation**: Creates OCR service instances based on configuration
- **Dynamic Selection**: Allows for dynamic selection of OCR service implementations
- **Configuration Validation**: Validates service configuration

## Configuration

### DocumentAIConfig

The `DocumentAIConfig` class provides configuration options for the Google Document AI OCR service:

```python
class DocumentAIConfig(ServiceConfig):
    """Configuration for Google Document AI OCR service."""
    project_id: str
    processor_id: str
    location: str = "us-central1"
    confidence_threshold: float = 0.7
    timeout: float = 30.0
    max_batch_size: int = 10
```

## Usage Examples

### Basic Usage

```python
from src.video_understanding.ai.ocr.document_ai import DocumentAIService, DocumentAIConfig
import numpy as np
import cv2

# Create configuration
config = DocumentAIConfig(
    service_name="document_ai",
    project_id="your-gcp-project-id",
    processor_id="your-processor-id",
    confidence_threshold=0.8,
)

# Create service instance
ocr_service = DocumentAIService(config)

# Initialize service
await ocr_service.initialize()

# Extract text from an image file
image = cv2.imread("path/to/image.jpg")
result = ocr_service.extract_text(image)

# Process result
print(f"Extracted text: {result['text']}")
for block in result['blocks']:
    print(f"Block: {block['text']} at {block['bounding_box']}")

# Shut down service
await ocr_service.shutdown()
```

### Batch Processing

```python
import cv2
import numpy as np
from src.video_understanding.ai.ocr.document_ai import DocumentAIService, DocumentAIConfig

# Create configuration
config = DocumentAIConfig(
    service_name="document_ai",
    project_id="your-gcp-project-id",
    processor_id="your-processor-id",
    max_batch_size=5,
)

# Create service instance
ocr_service = DocumentAIService(config)

# Initialize service
await ocr_service.initialize()

# Load multiple images
images = [
    cv2.imread("path/to/image1.jpg"),
    cv2.imread("path/to/image2.jpg"),
    cv2.imread("path/to/image3.jpg"),
]

# Extract text from multiple images
results = ocr_service.batch_extract_text(images)

# Process results
for i, result in enumerate(results):
    print(f"Image {i+1} text: {result['text']}")

# Shut down service
await ocr_service.shutdown()
```

### Factory-based Usage

```python
from src.video_understanding.ai.ocr.factory import create_ocr_service
from src.video_understanding.services.factory import ServiceFactory
from src.video_understanding.ai.ocr.base import BaseOCRService
from src.video_understanding.ai.ocr.document_ai import DocumentAIConfig

# Create service using factory helper function
ocr_service = create_ocr_service(
    project_id="your-gcp-project-id",
    processor_id="your-processor-id",
    confidence_threshold=0.8,
)

# Initialize service
await ocr_service.initialize()

# Use service
# ...

# Shut down service
await ocr_service.shutdown()

# Alternatively, use the ServiceFactory directly
factory = ServiceFactory[ServiceConfig, BaseService]()
factory.register("document_ai", DocumentAIService)

config = DocumentAIConfig(
    service_name="document_ai",
    project_id="your-gcp-project-id",
    processor_id="your-processor-id",
)

ocr_service = factory.create("document_ai", config)
```

## Error Handling

```python
from src.video_understanding.ai.ocr.document_ai import OCRError

try:
    result = ocr_service.extract_text(image)
except OCRError as e:
    print(f"OCR error: {e}")
    # Handle the error
```

## Implementation Details

### Extracting Text

The `extract_text` method extracts text from an image:

```python
def extract_text(
    self,
    image: np.ndarray,
    detect_language: bool = False,
    confidence_threshold: float = 0.7,
) -> Dict[str, Any]:
    """Extract text from an image.

    Args:
        image: Numpy array of image data
        detect_language: Whether to detect language
        confidence_threshold: Minimum confidence for returned results

    Returns:
        Dictionary containing:
            text: Extracted text
            blocks: List of text blocks with positions
            confidence: Overall confidence score
            language: Detected language (if detect_language=True)

    Raises:
        OCRError: If there's an error during text extraction
    """
```

### Result Data Structure

The result of text extraction contains the following information:

```python
{
    "text": "The extracted text content",
    "blocks": [
        {
            "text": "Block of text",
            "bounding_box": {
                "x": 10,
                "y": 20,
                "width": 100,
                "height": 30
            },
            "confidence": 0.95
        },
        # More blocks...
    ],
    "confidence": 0.92,
    "language": "en"  # Only if detect_language=True
}
```

### Detecting Tables

The `detect_tables` method detects and extracts tables from an image:

```python
def detect_tables(
    self,
    image: np.ndarray,
    confidence_threshold: float = 0.7,
) -> Dict[str, Any]:
    """Detect tables in an image.

    Args:
        image: Numpy array of image data
        confidence_threshold: Minimum confidence for returned results

    Returns:
        Dictionary containing:
            tables: List of detected tables with positions and content
            confidence: Overall confidence score

    Raises:
        OCRError: If there's an error during table detection
    """
```

## Best Practices

1. **Initialize Before Use**: Always call `initialize()` before using the service.
2. **Proper Shutdown**: Always call `shutdown()` when done to release resources.
3. **Batch Processing**: Use batch processing for better performance when processing multiple images.
4. **Error Handling**: Use try-except blocks to handle potential errors.
5. **Confidence Thresholds**: Adjust confidence thresholds based on your specific needs.
6. **Image Preprocessing**: Consider preprocessing images (resizing, enhancing contrast) for better OCR results.
7. **Language Detection**: Enable language detection only when needed, as it may increase processing time.
8. **Resource Management**: Be mindful of API quotas and rate limits when using cloud-based OCR services.
9. **Caching Results**: Consider caching OCR results for frequently processed images.
