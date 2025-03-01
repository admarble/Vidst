#!/bin/bash
# Vidst File Structure Implementation Script
# This script creates the directory structure for the Vidst refactoring project

# Exit immediately if a command exits with a non-zero status
set -e

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}Vidst File Structure Implementation Script${NC}"
echo "This script will create the directory structure for the Vidst refactoring project."
echo

# Ask for confirmation
read -p "This will create new directories and files in your project. Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo -e "${RED}Operation cancelled.${NC}"
    exit 1
fi

# Create a backup of the current structure
echo -e "${YELLOW}Creating backup of current structure...${NC}"
mkdir -p ~/vidst_backup/src
cp -r src/* ~/vidst_backup/src/
echo -e "${GREEN}Backup created at ~/vidst_backup/src/${NC}"

# Create new directories
echo -e "${YELLOW}Creating new directories...${NC}"

# AI module directories
mkdir -p src/video_understanding/ai/ocr
mkdir -p src/video_understanding/ai/transcription
mkdir -p src/video_understanding/ai/scene

# Config directories
mkdir -p src/video_understanding/core/config

# Vector storage directories
mkdir -p src/video_understanding/storage/vector

# Utils directories
mkdir -p src/video_understanding/utils

# Scripts directory
mkdir -p src/scripts

echo -e "${GREEN}Directory structure created.${NC}"

# Create base interface files
echo -e "${YELLOW}Creating base interface files...${NC}"

# OCR service files
touch src/video_understanding/ai/ocr/__init__.py
touch src/video_understanding/ai/ocr/base.py
touch src/video_understanding/ai/ocr/document_ai.py
touch src/video_understanding/ai/ocr/service.py

# Transcription service files
touch src/video_understanding/ai/transcription/__init__.py
touch src/video_understanding/ai/transcription/base.py
touch src/video_understanding/ai/transcription/service.py
touch src/video_understanding/ai/transcription/hybrid.py

# Scene detection files
touch src/video_understanding/ai/scene/__init__.py
touch src/video_understanding/ai/scene/base.py
touch src/video_understanding/ai/scene/twelve_labs.py
touch src/video_understanding/ai/scene/service.py

# Vector storage files
touch src/video_understanding/storage/vector/base.py
touch src/video_understanding/storage/vector/pinecone.py

# Model files
touch src/video_understanding/ai/models/document_ai.py

echo -e "${GREEN}Base interface files created.${NC}"

# Create factory pattern files
echo -e "${YELLOW}Creating factory pattern files...${NC}"

# AI factory
touch src/video_understanding/ai/factory.py

# Vector storage factory
touch src/video_understanding/storage/vector/factory.py

# Configuration factory
touch src/video_understanding/core/config/api.py
touch src/video_understanding/core/config/factory.py

echo -e "${GREEN}Factory pattern files created.${NC}"

# Create utility classes
echo -e "${YELLOW}Creating utility classes...${NC}"

# Retry mechanism
touch src/video_understanding/utils/retry.py

# Circuit breaker
touch src/video_understanding/utils/circuit_breaker.py

# Migration and benchmark scripts
touch src/scripts/migrate_vectors.py
touch src/scripts/benchmark_apis.py

echo -e "${GREEN}Utility classes created.${NC}"

# Add empty init files
echo -e "${YELLOW}Adding empty __init__.py files...${NC}"

# Find directories missing __init__.py files
find src -type d -not -path "*/\.*" | while read dir; do
  if [ ! -f "$dir/__init__.py" ]; then
    touch "$dir/__init__.py"
    echo "Created __init__.py in $dir"
  fi
done

echo -e "${GREEN}All __init__.py files added.${NC}"

# Validate the structure
echo -e "${YELLOW}Validating directory structure...${NC}"

# Create a file showing the current structure
find src -type f -name "*.py" | sort > current_structure.txt

# Count new Python files
NEW_FILES=$(find src -type f -name "*.py" -newer ~/vidst_backup/src | wc -l)
echo "Created $NEW_FILES new Python files"

# Check if key interface files exist
echo -e "${YELLOW}Checking key interface files...${NC}"
for file in src/video_understanding/ai/ocr/base.py \
            src/video_understanding/storage/vector/base.py \
            src/video_understanding/utils/circuit_breaker.py; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file exists${NC}"
    else
        echo -e "${RED}✗ $file is missing${NC}"
    fi
done

echo -e "${GREEN}File structure creation complete!${NC}"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Add content to the interface files"
echo "2. Implement the factory classes"
echo "3. Begin with the high-priority components (Twelve Labs, Pinecone, Document AI)"
echo
echo -e "${GREEN}Good luck with your implementation!${NC}"
