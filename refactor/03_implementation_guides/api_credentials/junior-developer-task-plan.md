# Junior Developer Task Plan: Configure API Credentials in .env File

**GitHub Issue**: [#88 - enhancement(configuration): Configure API credentials in .env file](https://github.com/admarble/Vidst/issues/88)  
**Priority**: High  
**Estimated Time**: 1-2 days

## Overview

As part of our Vidst refactoring strategy, we're transitioning to using managed API services instead of custom implementations. Your task is to set up and document the API credentials required in the `.env` file for all the external services we'll be using.

This task aligns with our [Refactoring Master Plan](../../02_planning/vidst_refactoring_master_plan.md), where we're simplifying our architecture by replacing complex components with API services like Twelve Labs, Pinecone, and Google Document AI.

## Background Context

Our project is a 6-week proof-of-concept for video understanding and analysis. We're refactoring to simplify the architecture while ensuring all core functionality and performance targets are maintained. The Component Evaluation Matrix shows that several components will be replaced with API services:

1. **Scene Detection** → Twelve Labs API
2. **Vector Storage** → Pinecone API
3. **Natural Language Querying** → Twelve Labs Semantic Search
4. **OCR (Text Extraction)** → Google Document AI
5. **Audio Transcription** → Possibly Whisper API

## Step-by-Step Implementation Guide

### 1. Review Existing Environment Configuration (30 minutes)

- Check the current `.env` file structure in the project
- Note any existing patterns for credential storage
- Identify any existing credential validation logic

### 2. Create/Update `.env.example` Template (1 hour)

- Create or update the `.env.example` file in the project root
- Include placeholders for all required API credentials
- Add clear comments explaining each credential's purpose
- Example structure:

```
# Vidst API Credentials Configuration

# Twelve Labs - Used for Scene Detection and Semantic Search
TWELVE_LABS_API_KEY=your_api_key_here
TWELVE_LABS_API_URL=https://api.twelvelabs.io/v1

# Pinecone - Used for Vector Storage
PINECONE_API_KEY=your_api_key_here
PINECONE_ENVIRONMENT=your_environment_here
PINECONE_INDEX_NAME=vidst-vectors

# Google Document AI - Used for OCR/Text Extraction
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
GOOGLE_DOCUMENT_AI_PROCESSOR_ID=your_processor_id
GOOGLE_DOCUMENT_AI_LOCATION=your_location

# OpenAI Whisper API (if applicable) - Used for Audio Transcription
OPENAI_API_KEY=your_api_key_here
```

### 3. Add Documentation (1-2 hours)

- Create a new documentation file at `/docs/configuration.md`
- Explain each credential's purpose in detail
- Provide instructions on how to obtain these credentials
- Document any format requirements or restrictions
- Include troubleshooting tips for common credential issues

### 4. Implement Credential Loading (2-3 hours)

- Create or update a credentials module at `src/vidst/utils/credentials.py`
- Implement secure loading of credentials from the `.env` file
- Add validation to check for required credentials
- Include helpful error messages when credentials are missing or invalid

Example implementation:

```python
"""Credential management utilities for Vidst API integrations."""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Optional

class CredentialError(Exception):
    """Exception raised for credential-related errors."""
    pass

def load_credentials() -> Dict[str, str]:
    """
    Load API credentials from .env file.
    
    Returns:
        Dict[str, str]: Dictionary of credentials
        
    Raises:
        CredentialError: If required credentials are missing
    """
    # Load .env file from project root
    project_root = Path(__file__).parents[3]
    env_path = project_root / ".env"
    
    if not env_path.exists():
        raise CredentialError(
            ".env file not found. Create one based on .env.example template."
        )
    
    load_dotenv(env_path)
    
    # Define required credentials for each service
    required_credentials = {
        "TWELVE_LABS_API_KEY": "Twelve Labs API Key",
        "TWELVE_LABS_API_URL": "Twelve Labs API URL",
        "PINECONE_API_KEY": "Pinecone API Key",
        "PINECONE_ENVIRONMENT": "Pinecone Environment",
        "GOOGLE_APPLICATION_CREDENTIALS": "Google Application Credentials",
    }
    
    # Validate required credentials
    missing_credentials = []
    credentials = {}
    
    for key, description in required_credentials.items():
        value = os.environ.get(key)
        if not value:
            missing_credentials.append(f"{description} ({key})")
        else:
            credentials[key] = value
    
    if missing_credentials:
        raise CredentialError(
            f"Missing required credentials: {', '.join(missing_credentials)}. "
            f"Please update your .env file."
        )
    
    return credentials

def get_twelve_labs_credentials() -> Dict[str, str]:
    """Get Twelve Labs API credentials."""
    credentials = load_credentials()
    return {
        "api_key": credentials["TWELVE_LABS_API_KEY"],
        "api_url": credentials["TWELVE_LABS_API_URL"],
    }

def get_pinecone_credentials() -> Dict[str, str]:
    """Get Pinecone credentials."""
    credentials = load_credentials()
    return {
        "api_key": credentials["PINECONE_API_KEY"],
        "environment": credentials["PINECONE_ENVIRONMENT"],
        "index_name": os.environ.get("PINECONE_INDEX_NAME", "vidst-vectors"),
    }

def get_document_ai_credentials() -> Dict[str, str]:
    """Get Google Document AI credentials."""
    credentials = load_credentials()
    return {
        "credentials_path": credentials["GOOGLE_APPLICATION_CREDENTIALS"],
        "processor_id": os.environ.get("GOOGLE_DOCUMENT_AI_PROCESSOR_ID", ""),
        "location": os.environ.get("GOOGLE_DOCUMENT_AI_LOCATION", "us"),
    }

def get_whisper_credentials() -> Optional[Dict[str, str]]:
    """Get OpenAI Whisper API credentials if available."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    
    return {"api_key": api_key}
```

### 5. Add Simple Credential Tests (1-2 hours)

- Create a test file at `tests/utils/test_credentials.py`
- Write tests to verify credential loading and validation
- Use environment mocking to test missing credential scenarios

### 6. Integrate with API Service Modules (2-3 hours)

- Update the API service modules to use the new credential utilities
- Examples:
  - `src/vidst/services/twelve_labs.py`
  - `src/vidst/services/pinecone_db.py`
  - `src/vidst/services/document_ai.py`

### 7. Test End-to-End (1-2 hours)

- Create a simple test script that validates all API connections
- Verify that credentials are loaded correctly for each service
- Test error handling when credentials are missing or invalid

### 8. Update PR with Completion Evidence (30 minutes)

- Create a pull request for your changes
- Include screenshots or logs showing successful credential loading
- Update the GitHub issue with a summary of your changes

## Resources

- [Twelve Labs API Documentation](https://docs.twelvelabs.io/)
- [Pinecone API Documentation](https://docs.pinecone.io/)
- [Google Document AI Documentation](https://cloud.google.com/document-ai/docs)
- [Python dotenv Documentation](https://github.com/theskumar/python-dotenv)

## Important Notes

1. **Security**: Never commit actual API keys to the repository. The `.env` file should be in the `.gitignore`.
2. **Simplicity**: Keep the implementation simple and focused. We're in a POC stage.
3. **Documentation**: Ensure your code has clear docstrings and comments.
4. **Error Messages**: Make error messages helpful for future developers.

## Definition of Done

- All checklist items in the GitHub issue are completed
- `.env.example` template is created and documented
- Credential loading utility is implemented and tested
- Documentation is clear and comprehensive
- Pull request is submitted for review

If you have any questions or run into issues, please reach out to the senior developer on the team for guidance.