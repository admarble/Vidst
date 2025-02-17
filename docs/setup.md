# Project Setup Guide

## Overview

This document provides detailed instructions for setting up the Video Understanding AI project for both development and production environments. The project uses Python 3.10+ and includes separate dependency configurations for development, testing, and production.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Git
- Virtual environment tool (venv or conda)
- FFmpeg (for video processing)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/your-org/video-understanding-ai
cd video-understanding-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install development dependencies (optional):
```bash
pip install -e .
```

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Dependency Management

### Production Dependencies (`requirements.txt`)

Core dependencies for running the application in production:

#### Web Framework
- fastapi==0.109.2 - Modern web framework for building APIs
- uvicorn==0.27.1 - ASGI server implementation

#### Database
- sqlalchemy==2.0.25 - SQL toolkit and ORM
- alembic==1.13.1 - Database migration tool
- python-dotenv==1.0.1 - Environment variable management

#### Security
- python-jose[cryptography]==3.3.0 - JWT token handling
- passlib[bcrypt]==1.7.4 - Password hashing

#### Data Validation
- pydantic==2.6.1 - Data validation using Python type annotations

### Development Dependencies (`setup.py`)

Additional tools for development:

```python
install_requires=[
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "isort>=5.0.0",
    "coverage-badge>=1.1.0",
]
```

### Testing Dependencies (`requirements-test.txt`)

Comprehensive testing suite dependencies:

#### Test Framework
- pytest==8.0.0 - Testing framework
- pytest-cov==4.1.0 - Coverage reporting
- pytest-xdist==3.5.0 - Parallel test execution
- pytest-timeout==2.2.0 - Test timeout management
- pytest-benchmark==4.0.0 - Performance benchmarking

#### Mock and Fixtures
- pytest-mock==3.12.0
- pytest-fixture-config==1.7.0
- pytest-env==1.1.3

#### Video Processing
- opencv-python==4.9.0.80
- moviepy==1.0.3
- ffmpeg-python==0.2.0

#### AI Models (Test Versions)
- openai==1.12.0
- google-ai-generativelanguage==0.4.0
- twelve-labs-python==0.3.0

#### Vector Storage
- numpy==1.26.3
- faiss-cpu==1.7.4

## Development Environment Setup

### IDE Configuration

#### VSCode Settings
Create `.vscode/settings.json`:
```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.rulers": [88],
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.nosetestsEnabled": false,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
```

### Code Style

The project uses:
- Black for code formatting (line length: 88 characters)
- isort for import sorting
- flake8 for linting

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

## Testing Setup

Run tests:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run parallel tests
pytest -n auto

# Run performance tests
pytest tests/performance/
```

## Environment Variables

Required environment variables:

```bash
# API Keys
OPENAI_API_KEY=your_key_here
GOOGLE_AI_API_KEY=your_key_here
TWELVE_LABS_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Security
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Storage
VECTOR_STORE_PATH=/path/to/vector/store
CACHE_DIR=/path/to/cache
```

## Troubleshooting

### Common Issues

1. FFmpeg not found:
```bash
# On Ubuntu/Debian
sudo apt-get install ffmpeg

# On macOS
brew install ffmpeg
```

2. Database migration errors:
```bash
# Reset migrations
alembic revision --autogenerate -m "reset"
alembic upgrade head
```

3. Memory issues with large videos:
- Increase Python's memory limit
- Use chunked processing
- Enable garbage collection

### Getting Help

- Check the [FAQ](./FAQ.md)
- Open an issue on GitHub
- Contact the development team

## Next Steps

- Review the [API Documentation](./api/README.md)
- Set up your first video processing pipeline
- Run the test suite
- Start contributing to the project 