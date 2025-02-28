from typing import Dict, List, Optional, Any, Tuple
import numpy as np


class BaseVectorStorage:
    """Base interface for vector storage implementations."""
    
    def add_vectors(self, vectors: np.ndarray, ids: List[str], metadata: Optional[List[Dict[str, Any]]] = None) -> None:
        """Add vectors to the storage.
        
        Args:
            vectors: Numpy array of vectors to add
            ids: List of IDs corresponding to vectors
            metadata: Optional list of metadata dictionaries
            
        Raises:
            VectorStorageError: If there's an error adding vectors
        """
        raise NotImplementedError("Subclasses must implement add_vectors")
        
    def search(self, query_vector: np.ndarray, top_k: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[Tuple[str, float, Optional[Dict[str, Any]]]]:
        """Search for similar vectors.
        
        Args:
            query_vector: Query vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of tuples (id, score, metadata)
            
        Raises:
            VectorStorageError: If there's an error during search
        """
        raise NotImplementedError("Subclasses must implement search")
        
    def delete_vectors(self, ids: List[str]) -> None:
        """Delete vectors from the storage.
        
        Args:
            ids: List of vector IDs to delete
            
        Raises:
            VectorStorageError: If there's an error deleting vectors
        """
        raise NotImplementedError("Subclasses must implement delete_vectors")
        
    def get_vector_count(self) -> int:
        """Get the number of vectors in the storage.
        
        Returns:
            Number of vectors
            
        Raises:
            VectorStorageError: If there's an error getting vector count
        """
        raise NotImplementedError("Subclasses must implement get_vector_count")
        
    def clear(self) -> None:
        """Clear all vectors from the storage.
        
        Raises:
            VectorStorageError: If there's an error clearing vectors
        """
        raise NotImplementedError("Subclasses must implement clear")
