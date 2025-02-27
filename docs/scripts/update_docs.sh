#!/bin/bash

# Script to update and validate documentation

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'  # No Color

echo -e "${YELLOW}Starting documentation update process...${NC}\n"

# Step 1: Generate documentation structure
echo -e "${YELLOW}Generating documentation structure...${NC}"
python3 scripts/generate_docs_structure.py
echo -e "${GREEN}✓ Documentation structure updated${NC}\n"

# Step 2: Check and fix cross-references
echo -e "${YELLOW}Checking cross-references...${NC}"
python3 scripts/fix_cross_references.py
echo -e "${GREEN}✓ Cross-references checked${NC}\n"

# Step 3: Validate documentation
echo -e "${YELLOW}Validating documentation...${NC}"
python3 scripts/validate_docs.py
echo -e "${GREEN}✓ Documentation validated${NC}\n"

# Step 4: Build documentation
echo -e "${YELLOW}Building documentation...${NC}"
make clean
make html SPHINXOPTS="-W --keep-going -n"

# Check if build was successful
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Documentation built successfully!${NC}"
    echo -e "\nDocumentation is now available in _build/html/"
else
    echo -e "\n${RED}✗ Documentation build failed. Please check the errors above.${NC}"
    exit 1
fi
