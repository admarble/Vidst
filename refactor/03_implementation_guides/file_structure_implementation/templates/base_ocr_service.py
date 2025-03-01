from typing import Dict, List, Union, Any
from pathlib import Path
import numpy as np


class BaseOCRService:
    """Base interface for OCR services."""
    
    async def extract_text(self, image: Union[str, Path, np.ndarray]) -> Dict[str, Any]:
        """Extract text from an image.
        
        Args:
            image: Image path or numpy array
            
        Returns:
            Dictionary containing extracted text and metadata
            
        Raises:
            OCRError: If there's an error during text extraction
        """
        raise NotImplementedError("Subclasses must implement extract_text")
        
    async def extract_text_batch(self, images: List[Union[str, Path, np.ndarray]]) -> List[Dict[str, Any]]:
        """Extract text from multiple images.
        
        Args:
            images: List of image paths or numpy arrays
            
        Returns:
            List of dictionaries containing extracted text and metadata
            
        Raises:
            OCRError: If there's an error during batch text extraction
        """
        # Default implementation, subclasses can optimize
        results = []
        for image in images:
            result = await self.extract_text(image)
            results.append(result)
        return results
