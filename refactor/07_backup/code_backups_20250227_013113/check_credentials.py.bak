#!/usr/bin/env python3
"""
Credential Validation Utility

This script checks if all required API credentials are configured correctly in the .env file.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# Import local modules
try:
    from video_understanding.core.config.credentials import (
        load_credentials,
        validate_credentials,
        get_all_credentials,
        CredentialError,
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(
        "Make sure you've activated your virtual environment and installed the package."
    )
    sys.exit(1)

# ANSI color codes for terminal output
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
BOLD = "\033[1m"
RESET = "\033[0m"


def check_credentials():
    """Check if all required credentials are configured correctly."""
    print(f"{BOLD}Checking API Credentials{RESET}")
    print("-" * 50)

    try:
        # Load all credentials from .env file
        credentials = load_credentials()
        print(f"{GREEN}✓ Successfully loaded .env file{RESET}")

        # Get credentials organized by service
        all_creds = get_all_credentials()

        # Check each service
        services = {
            "openai": "OpenAI (GPT-4V and Whisper)",
            "gemini": "Google Gemini",
            "twelve_labs": "Twelve Labs",
            "pinecone": "Pinecone Vector Database",
            "document_ai": "Google Document AI",
        }

        print("\n🔑 API Credentials Status:")
        for service_key, service_name in services.items():
            if service_key in all_creds:
                keys = list(all_creds[service_key].keys())
                print(f"{GREEN}✓ {service_name}:{RESET} {', '.join(keys)}")
            else:
                print(f"{YELLOW}⚠ {service_name}:{RESET} Missing credentials")

        # Validate required credentials
        try:
            validate_credentials(credentials)
            print(f"\n{GREEN}✓ All required credentials are configured.{RESET}")
        except CredentialError as e:
            print(f"\n{YELLOW}⚠ Some required credentials are missing:{RESET}")
            print(f"{str(e)}")

    except CredentialError as e:
        print(f"{RED}✗ Error: {str(e)}{RESET}")
        print(f"\nPlease copy .env.example to .env and fill in your credentials:")
        print("  cp .env.example .env")
        sys.exit(1)

    print(
        "\n💡 Tip: To update your credentials, edit the .env file in the project root."
    )


if __name__ == "__main__":
    check_credentials()
