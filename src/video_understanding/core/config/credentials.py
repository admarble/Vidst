"""Credentials management module for Video Understanding AI.

This module provides functions for loading and validating API credentials from environment variables.
"""

# Standard library imports
import os
from pathlib import Path
from typing import Dict, List

# Third-party imports
from dotenv import load_dotenv

# Local imports
from ..exceptions import ConfigurationError


class CredentialError(ConfigurationError):
    """Exception raised for credential-related errors."""

    pass


def find_env_file() -> Path:
    """Find the .env file in the project structure.

    Returns:
        Path: Path to the .env file

    Raises:
        CredentialError: If .env file cannot be found
    """
    # Try different paths to find the .env file
    possible_paths = [
        Path.cwd() / ".env",  # Current working directory
        Path(__file__).parents[4]
        / ".env",  # Project root (assuming standard structure)
        Path.home() / ".vidst" / ".env",  # User home directory
    ]

    for path in possible_paths:
        if path.exists():
            return path

    raise CredentialError(
        ".env file not found. Please create one based on .env.example template."
    )


def load_credentials() -> Dict[str, str]:
    """Load API credentials from .env file.

    Returns:
        Dict[str, str]: Dictionary of credentials

    Raises:
        CredentialError: If required credentials are missing
    """
    # Find and load .env file
    env_path = find_env_file()
    load_dotenv(env_path)

    # Check if all required credentials are set
    credentials = {}

    # Get all credentials from environment (can be used for all services)
    for key, value in os.environ.items():
        if key.endswith("_API_KEY") or key in {
            "PINECONE_ENVIRONMENT",
            "GOOGLE_APPLICATION_CREDENTIALS",
            "GOOGLE_CLOUD_PROJECT_ID",
            "DOCUMENT_AI_OCR_PROCESSOR_ID",
            "DOCUMENT_AI_FORM_PROCESSOR_ID",
            "DOCUMENT_AI_CODE_PROCESSOR_ID",
            "GCS_BUCKET_NAME",
        }:
            credentials[key] = value

    return credentials


def validate_credentials(credentials: Dict[str, str]) -> None:
    """Validate that all required credentials are present.

    Args:
        credentials: Dictionary of credentials

    Raises:
        CredentialError: If required credentials are missing
    """
    # Define required credentials for each service
    required_credentials: Dict[str, List[str]] = {
        "openai": ["OPENAI_API_KEY"],
        "gemini": ["GEMINI_API_KEY"],
        "twelve_labs": ["TWELVE_LABS_API_KEY"],
        "pinecone": ["PINECONE_API_KEY", "PINECONE_ENVIRONMENT"],
        "document_ai": [
            "GOOGLE_APPLICATION_CREDENTIALS",
            "GOOGLE_CLOUD_PROJECT_ID",
            "DOCUMENT_AI_OCR_PROCESSOR_ID",
        ],
    }

    # Check for missing credentials
    missing_services: Dict[str, List[str]] = {}

    for service, keys in required_credentials.items():
        missing_keys = [
            key for key in keys if key not in credentials or not credentials[key]
        ]
        if missing_keys:
            missing_services[service] = missing_keys

    if missing_services:
        error_messages = []
        for service, keys in missing_services.items():
            error_messages.append(
                f"{service.replace('_', ' ').title()}: {', '.join(keys)}"
            )

        error_msg = "Missing required API credentials:\n- "
        error_msg += "\n- ".join(error_messages)
        error_msg += "\n\nPlease update your .env file with the required credentials."
        raise CredentialError(error_msg)


def get_service_credentials(service_name: str) -> Dict[str, str]:
    """Get credentials for a specific service.

    Args:
        service_name: Name of the service ('openai', 'gemini', 'twelve_labs', etc.)

    Returns:
        Dict[str, str]: Dictionary of credentials for the service

    Raises:
        CredentialError: If service credentials are missing
    """
    credentials = load_credentials()

    # Define the credentials needed for specific services
    service_credential_keys = {
        "openai": ["OPENAI_API_KEY"],
        "gemini": ["GEMINI_API_KEY"],
        "twelve_labs": ["TWELVE_LABS_API_KEY"],
        "pinecone": ["PINECONE_API_KEY", "PINECONE_ENVIRONMENT"],
        "document_ai": [
            "GOOGLE_APPLICATION_CREDENTIALS",
            "GOOGLE_CLOUD_PROJECT_ID",
            "DOCUMENT_AI_OCR_PROCESSOR_ID",
            "DOCUMENT_AI_FORM_PROCESSOR_ID",
            "DOCUMENT_AI_CODE_PROCESSOR_ID",
        ],
        "gcs": ["GCS_BUCKET_NAME"],
    }

    if service_name not in service_credential_keys:
        raise CredentialError(f"Unknown service: {service_name}")

    required_keys = service_credential_keys[service_name]
    service_credentials = {}

    for key in required_keys:
        if key not in credentials or not credentials[key]:
            raise CredentialError(
                f"Missing {key} for {service_name} service. "
                f"Please add it to your .env file."
            )
        service_credentials[key] = credentials[key]

    return service_credentials


def get_all_credentials() -> Dict[str, Dict[str, str]]:
    """Get all credentials organized by service.

    Returns:
        Dict[str, Dict[str, str]]: Dictionary of all credentials organized by service
    """
    credentials = load_credentials()

    # Define the credentials needed for specific services
    service_credential_keys = {
        "openai": ["OPENAI_API_KEY"],
        "gemini": ["GEMINI_API_KEY"],
        "twelve_labs": ["TWELVE_LABS_API_KEY"],
        "pinecone": ["PINECONE_API_KEY", "PINECONE_ENVIRONMENT"],
        "document_ai": [
            "GOOGLE_APPLICATION_CREDENTIALS",
            "GOOGLE_CLOUD_PROJECT_ID",
            "DOCUMENT_AI_OCR_PROCESSOR_ID",
            "DOCUMENT_AI_FORM_PROCESSOR_ID",
            "DOCUMENT_AI_CODE_PROCESSOR_ID",
        ],
        "gcs": ["GCS_BUCKET_NAME"],
    }

    all_credentials = {}

    for service, keys in service_credential_keys.items():
        service_creds = {}
        for key in keys:
            if key in credentials:
                service_creds[key] = credentials[key]
        if service_creds:
            all_credentials[service] = service_creds

    return all_credentials
