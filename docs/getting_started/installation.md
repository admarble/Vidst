# Installation

## Prerequisites

- Python 3.10+
- Git LFS
- CUDA-compatible GPU (optional)
- API keys for implemented services:
  - Twelve Labs

## Basic Setup

```bash
# Clone repository
git clone https://github.com/admarble/Vidst.git
cd Vidst

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
# Required keys for POC: TWELVE_LABS_API_KEY
```
