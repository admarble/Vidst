from typing import Dict, Union, Any, Protocol
from pathlib import Path
import numpy as np

# OpenCV is a C++ library with Python bindings, so type checkers often struggle with it
import cv2  # type: ignore
from pydantic import BaseModel

# NOTE: This is a template file for demonstration purposes.
# In a real implementation, you would need to install the required packages:
#   pip install google-cloud-documentai pydantic


# Define stub classes for type checking
class DocumentAIStubs:
    """Stub classes to support linting without the actual dependencies."""

    class TextSegment:
        start_index: int
        end_index: int

    class TextAnchor:
        text_segments: list["DocumentAIStubs.TextSegment"]

    class Vertex:
        x: float
        y: float

    class BoundingPoly:
        vertices: list["DocumentAIStubs.Vertex"]

    class Layout:
        text_anchor: "DocumentAIStubs.TextAnchor"
        confidence: float
        bounding_poly: "DocumentAIStubs.BoundingPoly"

    class Block:
        layout: "DocumentAIStubs.Layout"

    class Dimension:
        width: float
        height: float

    class Page:
        page_number: int
        dimension: "DocumentAIStubs.Dimension"
        blocks: list["DocumentAIStubs.Block"]

    class Document:
        text: str
        pages: list["DocumentAIStubs.Page"]

    class ProcessResponse:
        document: "DocumentAIStubs.Document"


# Try to import the real package if available, otherwise use stubs
try:
    # In an actual implementation, this would be installed
    from google.cloud import documentai  # type: ignore
except ImportError:
    # For type checking only - mock the DocumentAI classes
    class documentai:
        class DocumentProcessorServiceClient:
            def process_document(self, request: Any) -> DocumentAIStubs.ProcessResponse:
                """Process a document."""
                # This is a stub method that would be replaced in actual implementation
                raise NotImplementedError()

        class RawDocument:
            def __init__(self, content: bytes, mime_type: str):
                self.content = content
                self.mime_type = mime_type

        class ProcessRequest:
            def __init__(self, name: str, raw_document: "documentai.RawDocument"):
                self.name = name
                self.raw_document = raw_document


# Define interface for OCR Service - using Protocol for better linting support
class BaseOCRServiceProtocol(Protocol):
    """Protocol defining the interface for OCR services."""

    async def extract_text(self, image: Union[str, Path, np.ndarray]) -> Dict[str, Any]:
        """Extract text from an image."""
        ...


# In an actual implementation, this would be imported from the project structure
# Since this is a template, we define a base class to use
BaseOCRService = BaseOCRServiceProtocol  # type: ignore


class OCRError(Exception):
    """Exception raised for OCR-related errors."""

    pass


class DocumentAIConfig(BaseModel):
    """Configuration for Google Document AI."""

    project_id: str
    location: str = "us-central1"
    processor_id: str
    timeout: float = 30.0


class DocumentAIService:
    """Google Document AI implementation for OCR."""

    def __init__(self, config: DocumentAIConfig):
        """Initialize the Document AI service.

        Args:
            config: Document AI configuration
        """
        self.config = config
        self.client = documentai.DocumentProcessorServiceClient()
        self.processor_name = (
            f"projects/{config.project_id}/locations/{config.location}"
            f"/processors/{config.processor_id}"
        )

    async def extract_text(self, image: Union[str, Path, np.ndarray]) -> Dict[str, Any]:
        """Extract text from an image using Document AI.

        Args:
            image: Image path or numpy array

        Returns:
            Dictionary containing extracted text and metadata

        Raises:
            OCRError: If there's an error during text extraction
        """
        try:
            # Convert image to bytes
            if isinstance(image, (str, Path)):
                with open(image, "rb") as f:
                    content = f.read()
            elif isinstance(image, np.ndarray):
                # OpenCV's imencode function exists but may not be detected by linters
                # because it's part of a C++ extension. The function converts a numpy
                # array to compressed image bytes (e.g., JPG, PNG)
                # Syntax: retval, buffer = cv2.imencode(ext, img[, params])
                is_success, buffer = cv2.imencode(".jpg", image)  # type: ignore
                if not is_success:
                    raise OCRError("Failed to encode image")
                content = buffer.tobytes()
            else:
                raise ValueError(f"Unsupported image type: {type(image)}")

            # Create document for processing
            raw_document = documentai.RawDocument(
                content=content, mime_type="image/jpeg"
            )

            # Process document
            request = documentai.ProcessRequest(
                name=self.processor_name, raw_document=raw_document
            )

            response = self.client.process_document(request)
            document = response.document

            # Extract text and layout
            result = {"text": document.text, "pages": []}

            # Extract page information
            for page in document.pages:
                page_info = {
                    "page_number": page.page_number,
                    "width": page.dimension.width,
                    "height": page.dimension.height,
                    "blocks": [],
                }

                # Extract text blocks
                for block in page.blocks:
                    block_text = self._get_text_from_layout(document, block.layout)
                    block_info = {
                        "text": block_text,
                        "confidence": block.layout.confidence,
                        "bounding_box": [
                            (vertex.x, vertex.y)
                            for vertex in block.layout.bounding_poly.vertices
                        ],
                    }
                    page_info["blocks"].append(block_info)

                result["pages"].append(page_info)

            return result

        except Exception as e:
            raise OCRError(f"Document AI error: {str(e)}")

    def _get_text_from_layout(self, document: Any, layout: Any) -> str:
        """Extract text from a layout element.

        Args:
            document: Document object containing the text
            layout: Layout object with text segment information

        Returns:
            Extracted text from the specified segment
        """
        start_index = layout.text_anchor.text_segments[0].start_index
        end_index = layout.text_anchor.text_segments[0].end_index
        return document.text[start_index:end_index]
