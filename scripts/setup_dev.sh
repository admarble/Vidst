#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🚀 Setting up development environment..."
echo

# Function to check command status
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1 failed${NC}"
        exit 1
    fi
    echo
}

# 1. Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$python_version 3.10" | awk '{print ($1 >= $2)}') )); then
    echo -e "${GREEN}✓ Python $python_version detected${NC}"
else
    echo -e "${RED}✗ Python 3.10+ required, but $python_version detected${NC}"
    exit 1
fi
echo

# 2. Create virtual environment
echo "🌟 Creating virtual environment..."
python3 -m venv venv
check_status "Virtual environment creation"

# 3. Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
check_status "Virtual environment activation"

# 4. Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
check_status "Core dependencies"

pip install -r requirements-test.txt
check_status "Test dependencies"

pip install -e .
check_status "Development mode installation"

# 5. Install pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
pre-commit install
check_status "Pre-commit hooks installation"

# 6. Create .env file if it doesn't exist
echo "⚙️  Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env with your configuration${NC}"
    check_status "Environment file creation"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
    echo
fi

# 7. Set up git hooks
echo "🎣 Setting up git hooks..."
chmod +x .git/hooks/pre-push
check_status "Git hooks setup"

# 8. Create necessary directories
echo "📁 Creating project directories..."
mkdir -p .cursor
check_status "Project directories creation"

# 9. Initial test run
echo "🧪 Running initial test suite..."
pytest tests/unit/ -v
check_status "Initial test run"

# Success message
echo -e "${GREEN}✅ Development environment setup complete!${NC}"
echo
echo "Next steps:"
echo "1. Edit .env with your API keys and configuration"
echo "2. Run './scripts/check_pr.sh' to verify everything is working"
echo "3. Start developing!"
