"""Credentials utility functions for Video Understanding AI."""

from typing import Dict
from ..core.config.credentials import get_service_credentials


def get_twelve_labs_credentials() -> Dict[str, str]:
    """Get Twelve Labs API credentials.

    Returns:
        Dict[str, str]: Dictionary containing API key

    Raises:
        CredentialError: If credentials are missing
    """
    credentials = get_service_credentials("twelve_labs")
    return {"api_key": credentials["TWELVE_LABS_API_KEY"]}
