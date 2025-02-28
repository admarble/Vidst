# Vidst File Structure Implementation Guide for Junior Developers

## Introduction

This guide will help you implement the new file structure for the Vidst refactoring project. By following these steps, you will create the directory structure and placeholder files needed to transition to the API-centric architecture outlined in our refactoring plan.

**Goal**: Set up the foundational file structure to enable smooth implementation of the API-centric architecture.

## Prerequisites

Before starting, ensure you have:

- Access to the Vidst project repository
- Proper permissions to create and modify files
- Basic familiarity with command line operations
- Git installed and configured
- A terminal or command prompt open in the project's root directory

## Implementation Steps

### Phase 1: Setup and Backup

Before making any changes, let's create a backup of the current structure.

1. **Create a new branch for the refactoring**

```bash
# Create and checkout a new branch
git checkout -b refactor/file-structure
```

2. **Create a backup of the current source code**

```bash
# Create a backup directory
mkdir -p ~/vidst_backup/src
# Copy current source code to backup
cp -r src/* ~/vidst_backup/src/
```

3. **Verify your backup**

```bash
# List the backup directory to confirm files are there
ls -la ~/vidst_backup/src/
```

> **Note**: This backup is an extra precaution. The git branch will also protect your changes, but a local backup provides additional security.

### Phase 2: Create New Directories

Now we'll create the new directory structure according to the refactoring plan.

1. **Create the new directories**

```bash
# Create new directories in the AI module
mkdir -p src/video_understanding/ai/ocr
mkdir -p src/video_understanding/ai/transcription
mkdir -p src/video_understanding/ai/scene

# Create config directories
mkdir -p src/video_understanding/core/config

# Create vector storage directories
mkdir -p src/video_understanding/storage/vector

# Create utils directories
mkdir -p src/video_understanding/utils

# Create scripts directory
mkdir -p src/scripts
```

2. **Verify the new directory structure**

```bash
# Show the directory structure
find src/video_understanding -type d | sort
find src/scripts -type d | sort
```

### Phase 3: Create Base Interface Files

Now we'll create the base interface files that will define the abstractions for our API-centric approach.

1. **Create OCR service interface files**

```bash
touch src/video_understanding/ai/ocr/__init__.py
touch src/video_understanding/ai/ocr/base.py
touch src/video_understanding/ai/ocr/document_ai.py
touch src/video_understanding/ai/ocr/service.py
```

2. **Create transcription service interface files**

```bash
touch src/video_understanding/ai/transcription/__init__.py
touch src/video_understanding/ai/transcription/base.py
touch src/video_understanding/ai/transcription/service.py
touch src/video_understanding/ai/transcription/hybrid.py
```

3. **Create scene detection interface files**

```bash
touch src/video_understanding/ai/scene/__init__.py
touch src/video_understanding/ai/scene/base.py
touch src/video_understanding/ai/scene/twelve_labs.py
touch src/video_understanding/ai/scene/service.py
```

4. **Create vector storage interface files**

```bash
touch src/video_understanding/storage/vector/base.py
touch src/video_understanding/storage/vector/pinecone.py
```

5. **Create model files**

```bash
touch src/video_understanding/ai/models/document_ai.py
# Note: twelve_labs.py and whisper.py already exist and will be updated later
```

### Phase 4: Setup Factory Pattern Files

Next, we'll create the factory pattern files that will enable dynamic provider selection.

1. **Create AI factory file**

```bash
touch src/video_understanding/ai/factory.py
```

2. **Create vector storage factory file**

```bash
touch src/video_understanding/storage/vector/factory.py
```

3. **Create configuration factory file**

```bash
touch src/video_understanding/core/config/api.py
touch src/video_understanding/core/config/factory.py
```

### Phase 5: Add Utility Classes

Now we'll create the utility classes for resiliency patterns.

1. **Create retry mechanism file**

```bash
touch src/video_understanding/utils/retry.py
```

2. **Create circuit breaker implementation file**

```bash
touch src/video_understanding/utils/circuit_breaker.py
```

3. **Create migration and benchmark script files**

```bash
touch src/scripts/migrate_vectors.py
touch src/scripts/benchmark_apis.py
```

These utility scripts serve important purposes in the refactoring process:

- **migrate_vectors.py**: Facilitates the migration of vector embeddings from the current FAISS implementation to the new Pinecone vector database. It performs the migration in batches, with validation checks to ensure data integrity.

- **benchmark_apis.py**: Benchmarks the performance of various API integrations (Twelve Labs, Pinecone, Document AI), measuring latency, throughput, error rates, and estimating costs under different load conditions.

### Phase 6: Add Empty Init Files

To ensure Python can properly import from all directories, add `__init__.py` files:

```bash
# Find directories missing __init__.py files
find src -type d -not -path "*/\.*" | while read dir; do
  if [ ! -f "$dir/__init__.py" ]; then
    touch "$dir/__init__.py"
    echo "Created __init__.py in $dir"
  fi
done
```

## Validation

Let's verify that you've successfully created the file structure.

1. **Verify the directory structure**

```bash
# Create a file showing the current structure
find src -type f -name "*.py" | sort > current_structure.txt

# View the structure
cat current_structure.txt
```

2. **Count the number of files created**

```bash
# Count new Python files
find src -type f -name "*.py" -newer ~/vidst_backup/src | wc -l
```

3. **Verify specific important files exist**

```bash
# Check if key interface files exist
ls -la src/video_understanding/ai/ocr/base.py
ls -la src/video_understanding/storage/vector/base.py
ls -la src/video_understanding/utils/circuit_breaker.py
```

## Adding Basic Content to Key Files

To help you get started, here's some basic template content for a few key files. Refer to the templates directory for more complete examples.

### 1. Vector Storage Base Interface (`src/video_understanding/storage/vector/base.py`)

Create this file with the following content:

```python
# src/video_understanding/storage/vector/base.py
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
```

### 2. Circuit Breaker Implementation (`src/video_understanding/utils/circuit_breaker.py`)

For circuit breaker implementation, please refer to the templates/circuit_breaker.py file.

## Commit Your Changes

Once you've completed and verified the file structure creation, commit your changes:

```bash
# Stage all new files
git add .

# Commit with a descriptive message
git commit -m "Implement new file structure for API-centric refactoring"
```

## Moving Forward

Now that you've set up the file structure, here's what comes next:

1. **Focus on implementing the high-priority components first**:
   - Scene Detection (Twelve Labs integration)
   - Vector Storage (Pinecone implementation)
   - OCR (Google Document AI)

2. **Follow the weekly plans in the implementation timeline**:
   - Week 1: Focus on Twelve Labs integration
   - Week 2: Implement Pinecone vector storage
   - Weeks 3-6: Complete remaining components

3. **Use the factory patterns** to allow switching between implementations, which will make testing easier and provide fallback options.

4. **Maintain the existing functionality** while gradually introducing the new API-based implementations.

## Troubleshooting

Here are solutions to common issues you might encounter:

### Permission Issues

If you encounter permission issues when creating files:

```bash
# Check your permissions in the directory
ls -la src/

# If needed, adjust permissions (be careful with this command)
chmod -R u+w src/
```

### Missing Directories

If a directory doesn't exist when you try to create a file:

```bash
# Ensure the directory exists before creating files
mkdir -p $(dirname path/to/file)
```

### Conflicts with Existing Files

If you try to create a file that already exists:

```bash
# Check if the file exists
ls -la path/to/file

# If needed, back up the existing file before overwriting
mv path/to/file path/to/file.bak
```

## Need Help?

If you encounter any issues during this process:
1. Consult the refactoring documentation in the refactor directory
2. Refer to the "Vidst Architecture Transition" document for detailed explanations
3. Ask for help from a senior developer if you're unsure about any step

Good luck with the implementation!
