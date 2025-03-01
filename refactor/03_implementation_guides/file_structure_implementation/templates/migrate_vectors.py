#!/usr/bin/env python
"""
Vector Migration Script for Vidst

This script facilitates the migration of vector embeddings from the current FAISS implementation
to the new Pinecone vector database. It performs the migration in batches, with validation
checks to ensure data integrity.

Usage:
    python migrate_vectors.py [--batch-size BATCH_SIZE] [--dry-run]

Options:
    --batch-size BATCH_SIZE  Size of batches for migration (default: 1000)
    --dry-run                Perform a test run without actual migration
    --namespace NAMESPACE    Optional namespace for Pinecone vectors
    --help                   Show this help message and exit
"""

import argparse
import logging
import time
import sys
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

# Vidst imports
from video_understanding.storage.vector.storage import FAISSVectorStorage, FAISSConfig
from video_understanding.storage.vector.pinecone import PineconeVectorStorage, PineconeConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("vector_migration.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("vector_migration")


class VectorMigration:
    """Handles migration of vector embeddings from FAISS to Pinecone."""
    
    def __init__(
        self, 
        batch_size: int = 1000, 
        dry_run: bool = False,
        namespace: Optional[str] = None
    ):
        """Initialize vector migration.
        
        Args:
            batch_size: Number of vectors to migrate in each batch
            dry_run: If True, don't actually perform migration
            namespace: Optional namespace for Pinecone vectors
        """
        self.batch_size = batch_size
        self.dry_run = dry_run
        self.namespace = namespace
        
        logger.info(f"Initializing vector migration (dry_run={dry_run}, batch_size={batch_size})")
        
        # Source FAISS storage
        self.faiss_config = self._get_faiss_config()
        self.faiss_storage = FAISSVectorStorage(self.faiss_config)
        
        # Target Pinecone storage
        if not dry_run:
            self.pinecone_config = self._get_pinecone_config()
            self.pinecone_storage = PineconeVectorStorage(self.pinecone_config)
    
    def _get_faiss_config(self) -> FAISSConfig:
        """Get FAISS configuration from environment or config file."""
        # In actual implementation, this would read from config
        # For template purposes, using placeholder values
        return FAISSConfig(
            index_path="path/to/faiss/index",
            dimension=512,  # Example dimension
            metadata_path="path/to/metadata.json"
        )
    
    def _get_pinecone_config(self) -> PineconeConfig:
        """Get Pinecone configuration from environment or config file."""
        # In actual implementation, this would read from config
        # For template purposes, using placeholder values
        return PineconeConfig(
            api_key="your-api-key",
            environment="your-environment",
            index_name="vidst-vectors",
            dimension=512,  # Should match FAISS dimension
            namespace=self.namespace
        )
    
    def migrate(self) -> Dict[str, Any]:
        """Perform the migration from FAISS to Pinecone.
        
        Returns:
            Dictionary with migration statistics
        """
        start_time = time.time()
        
        # Get total vector count
        total_vectors = self.faiss_storage.get_vector_count()
        logger.info(f"Found {total_vectors} vectors to migrate")
        
        if self.dry_run:
            logger.info("DRY RUN: No actual migration will be performed")
            return {
                "status": "dry_run",
                "total_vectors": total_vectors,
                "duration_seconds": time.time() - start_time
            }
        
        # Initialize counters
        migrated_count = 0
        error_count = 0
        batch_count = 0
        
        # Get all vector IDs
        # In actual implementation, you'd need a method to get all IDs from FAISS
        # This is a simplified approach
        all_ids = self._get_all_vector_ids()
        
        # Process in batches
        for i in range(0, len(all_ids), self.batch_size):
            batch_count += 1
            batch_ids = all_ids[i:i + self.batch_size]
            
            try:
                # Get vectors and metadata from FAISS
                batch_vectors, batch_metadata = self._get_vectors_and_metadata(batch_ids)
                
                # Add vectors to Pinecone
                self.pinecone_storage.add_vectors(
                    vectors=batch_vectors,
                    ids=batch_ids,
                    metadata=batch_metadata
                )
                
                # Validate migration
                validation_errors = self._validate_batch(batch_ids, batch_vectors)
                
                if validation_errors:
                    logger.warning(f"Validation errors in batch {batch_count}: {validation_errors}")
                    error_count += len(validation_errors)
                
                migrated_count += len(batch_ids) - len(validation_errors)
                
                logger.info(f"Migrated batch {batch_count}: {len(batch_ids)} vectors")
                
            except Exception as e:
                logger.error(f"Error migrating batch {batch_count}: {str(e)}")
                error_count += len(batch_ids)
        
        duration = time.time() - start_time
        
        # Log summary
        logger.info(f"Migration complete:")
        logger.info(f"  Total vectors: {total_vectors}")
        logger.info(f"  Successfully migrated: {migrated_count}")
        logger.info(f"  Errors: {error_count}")
        logger.info(f"  Duration: {duration:.2f} seconds")
        
        return {
            "status": "completed",
            "total_vectors": total_vectors,
            "migrated_vectors": migrated_count,
            "error_count": error_count,
            "batch_count": batch_count,
            "duration_seconds": duration
        }
    
    def _get_all_vector_ids(self) -> List[str]:
        """Get all vector IDs from FAISS.
        
        Returns:
            List of vector IDs
        """
        # Placeholder - in actual implementation, you'd need to get this from FAISS
        # This would depend on how IDs are stored in your FAISS implementation
        return ["id_1", "id_2", "id_3"]  # Example IDs
    
    def _get_vectors_and_metadata(self, ids: List[str]) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """Get vectors and metadata for the given IDs from FAISS.
        
        Args:
            ids: List of vector IDs
            
        Returns:
            Tuple of (vectors array, metadata list)
        """
        # Placeholder - in actual implementation, you'd need to get this from FAISS
        # This would depend on how vectors and metadata are stored in your FAISS implementation
        vectors = np.random.rand(len(ids), 512)  # Example vectors
        metadata = [{"source": f"video_{i}"} for i in range(len(ids))]  # Example metadata
        
        return vectors, metadata
    
    def _validate_batch(self, ids: List[str], original_vectors: np.ndarray) -> List[str]:
        """Validate that vectors were correctly migrated to Pinecone.
        
        Args:
            ids: List of vector IDs
            original_vectors: Original vectors from FAISS
            
        Returns:
            List of IDs with validation errors
        """
        error_ids = []
        
        for i, vector_id in enumerate(ids):
            # Search for the vector in Pinecone
            # In actual implementation, you'd need a method to get vectors by ID from Pinecone
            # This is a simplified approach
            try:
                query_vector = original_vectors[i]
                results = self.pinecone_storage.search(query_vector, top_k=1)
                
                if not results or results[0][0] != vector_id:
                    error_ids.append(vector_id)
            
            except Exception as e:
                logger.error(f"Error validating vector {vector_id}: {str(e)}")
                error_ids.append(vector_id)
        
        return error_ids


def main():
    """Main function to run the vector migration."""
    parser = argparse.ArgumentParser(description="Migrate vectors from FAISS to Pinecone")
    parser.add_argument("--batch-size", type=int, default=1000, help="Size of batches for migration")
    parser.add_argument("--dry-run", action="store_true", help="Perform a test run without actual migration")
    parser.add_argument("--namespace", type=str, help="Optional namespace for Pinecone vectors")
    
    args = parser.parse_args()
    
    # Create and run migration
    migration = VectorMigration(
        batch_size=args.batch_size,
        dry_run=args.dry_run,
        namespace=args.namespace
    )
    
    results = migration.migrate()
    
    # Print summary
    print("\nMigration Summary:")
    for key, value in results.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
