#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 Running PR Checks..."
echo

# Initialize error flag
errors=0

# Function to check command status
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1 passed${NC}"
    else
        echo -e "${RED}✗ $1 failed${NC}"
        errors=1
    fi
    echo
}

# 1. Code Formatting
echo "📝 Checking code formatting..."
black --check src tests
check_status "Black formatting"

isort --check-only src tests
check_status "Import sorting"

# 2. Run Tests with Coverage
echo "🧪 Running tests with coverage..."

# Clean previous coverage data
coverage erase

# Run unit tests
echo "Running unit tests..."
pytest tests/unit/ --cov=src --cov-report=xml --cov-report=term-missing:skip-covered
check_status "Unit tests"

# Run integration tests
echo "Running integration tests..."
pytest tests/integration/ --cov=src --cov-append --cov-report=xml --cov-report=term-missing:skip-covered
check_status "Integration tests"

# 3. Check Coverage Threshold
echo "📊 Checking coverage threshold..."
coverage report --fail-under=85
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Coverage threshold met${NC}"
else
    echo -e "${RED}✗ Coverage below 85% threshold${NC}"
    errors=1
fi
echo

# 4. Generate Coverage Badge
echo "🏷️  Generating coverage badge..."
coverage-badge -o coverage.svg -f
check_status "Coverage badge generation"

# Final Status
echo "🏁 Final Check Status:"
if [ $errors -eq 0 ]; then
    echo -e "${GREEN}All checks passed! Ready to create PR.${NC}"
    exit 0
else
    echo -e "${RED}Some checks failed. Please fix the issues above.${NC}"
    exit 1
fi 