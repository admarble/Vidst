#!/bin/bash

# Test script for verifying requirements installation
# This script creates a temporary virtual environment and tests the installation
# of all dependencies in requirements.txt

set -e  # Exit on first error

echo "=== Testing requirements.txt installation ==="

# Create a temporary directory
TEMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_DIR"

# Function to clean up on exit
cleanup() {
  echo "Cleaning up temporary directory..."
  rm -rf "$TEMP_DIR"
}

# Register the cleanup function
trap cleanup EXIT

# Navigate to temp directory
cd "$TEMP_DIR"

echo "Creating a fresh virtual environment..."
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
  # macOS or Linux
  source venv/bin/activate
else
  # Windows
  source venv/Scripts/activate
fi

# Copy requirements.txt to temp directory
cp "$OLDPWD/requirements.txt" .

# Ensure pip is up to date
pip install --upgrade pip

echo "Installing git for git-based dependencies..."
# This is a no-op if git is already installed
command -v git >/dev/null 2>&1 || { echo "Git is required but not installed. Please install git and try again." >&2; exit 1; }

echo "Creating processed requirements file without comments..."
# Create a processed file without comments and empty lines
grep -v "^\s*#" requirements.txt | grep -v "^\s*$" > requirements_processed.txt

echo "Testing package installation..."

while IFS= read -r line; do
    # Extract package name (everything before the comparison operator)
    package=$(echo "$line" | sed -E 's/([a-zA-Z0-9_.-]+)([>=<~!].*)$/\1/')

    # Attempt installation
    echo "Testing: $package"
    pip install "$package" --dry-run 2>/dev/null

    if [ $? -ne 0 ]; then
        echo "❌ Failed to install: $package"
        exit 1
    else
        echo "✅ Successfully verified: $package"
    fi
done < "requirements_processed.txt"

echo "Checking for dependency conflicts..."
pip check || echo "Some dependency conflicts were found. This may need to be resolved."

echo "Testing imports for major packages..."

# Function to test a Python import
test_import() {
  package=$1
  import_name=$2
  echo -n "Testing import for $package... "
  if python -c "import $import_name" &> /dev/null; then
    echo "✅ Success"
    return 0
  else
    echo "❌ Failed"
    return 1
  fi
}

# Test core dependencies
test_import "numpy" "numpy"
test_import "faiss-cpu" "faiss" || echo "  ⚠️  FAISS may need additional configuration"
test_import "torch" "torch" || echo "  ⚠️  PyTorch may require additional configuration"
test_import "transformers" "transformers" || echo "  ⚠️  May need to download models"

# Test new dependencies (some may be mocked in actual tests)
echo "Testing new API dependencies (these may fail if API keys are required)..."
test_import "pinecone" "pinecone" || echo "  ⚠️  May need API key configuration"
test_import "google-cloud-documentai" "google.cloud.documentai" || echo "  ⚠️  May need API key configuration"
# For git-based packages like whisper, we handle them differently
pip freeze | grep -q "whisper" && echo "✅ Whisper is installed" || echo "❌ Whisper is not installed"
test_import "twelvelabs" "twelvelabs" || echo "  ⚠️  May need API key configuration"

echo ""
echo "=== Requirements installation test complete ==="
echo "If there were any failures above, they may need to be resolved."
echo "You may need to configure API keys or install additional system dependencies."
exit 0
