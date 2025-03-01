"""Credential management utilities for Vidst API integrations."""

import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv

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