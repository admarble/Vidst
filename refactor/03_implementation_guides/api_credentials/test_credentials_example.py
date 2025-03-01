"""Tests for the credentials utility module."""

import os
import unittest
from unittest.mock import patch

from src.vidst.utils.credentials import (
    CredentialError,
    load_credentials,
    get_twelve_labs_credentials,
    get_pinecone_credentials,
    get_document_ai_credentials,
    get_whisper_credentials,
)

class TestCredentials(unittest.TestCase):
    """Tests for the credentials utility functions."""

    @patch.dict(os.environ, {
        "TWELVE_LABS_API_KEY": "test-api-key",
        "TWELVE_LABS_API_URL": "https://test-api.twelvelabs.io",
        "PINECONE_API_KEY": "test-pinecone-key",
        "PINECONE_ENVIRONMENT": "test-env",
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json",
    })
    def test_load_credentials_success(self):
        """Test that credentials are loaded successfully when all required ones are present."""
        credentials = load_credentials()
        self.assertEqual(credentials["TWELVE_LABS_API_KEY"], "test-api-key")
        self.assertEqual(credentials["TWELVE_LABS_API_URL"], "https://test-api.twelvelabs.io")
        self.assertEqual(credentials["PINECONE_API_KEY"], "test-pinecone-key")
        self.assertEqual(credentials["PINECONE_ENVIRONMENT"], "test-env")
        self.assertEqual(credentials["GOOGLE_APPLICATION_CREDENTIALS"], "/path/to/credentials.json")

    @patch.dict(os.environ, {
        "TWELVE_LABS_API_KEY": "test-api-key",
        "TWELVE_LABS_API_URL": "https://test-api.twelvelabs.io",
        # Missing Pinecone credentials
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json",
    })
    def test_load_credentials_missing(self):
        """Test that an error is raised when required credentials are missing."""
        with self.assertRaises(CredentialError) as context:
            load_credentials()
        
        self.assertIn("Missing required credentials", str(context.exception))
        self.assertIn("PINECONE_API_KEY", str(context.exception))
        self.assertIn("PINECONE_ENVIRONMENT", str(context.exception))

    @patch.dict(os.environ, {
        "TWELVE_LABS_API_KEY": "test-api-key",
        "TWELVE_LABS_API_URL": "https://test-api.twelvelabs.io",
        "PINECONE_API_KEY": "test-pinecone-key",
        "PINECONE_ENVIRONMENT": "test-env",
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json",
    })
    def test_get_twelve_labs_credentials(self):
        """Test that Twelve Labs credentials are retrieved correctly."""
        credentials = get_twelve_labs_credentials()
        self.assertEqual(credentials["api_key"], "test-api-key")
        self.assertEqual(credentials["api_url"], "https://test-api.twelvelabs.io")

    @patch.dict(os.environ, {
        "TWELVE_LABS_API_KEY": "test-api-key",
        "TWELVE_LABS_API_URL": "https://test-api.twelvelabs.io",
        "PINECONE_API_KEY": "test-pinecone-key",
        "PINECONE_ENVIRONMENT": "test-env",
        "PINECONE_INDEX_NAME": "custom-index",
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json",
    })
    def test_get_pinecone_credentials_custom_index(self):
        """Test that Pinecone credentials with custom index are retrieved correctly."""
        credentials = get_pinecone_credentials()
        self.assertEqual(credentials["api_key"], "test-pinecone-key")
        self.assertEqual(credentials["environment"], "test-env")
        self.assertEqual(credentials["index_name"], "custom-index")

    @patch.dict(os.environ, {
        "TWELVE_LABS_API_KEY": "test-api-key",
        "TWELVE_LABS_API_URL": "https://test-api.twelvelabs.io",
        "PINECONE_API_KEY": "test-pinecone-key",
        "PINECONE_ENVIRONMENT": "test-env",
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json",
    })
    def test_get_pinecone_credentials_default_index(self):
        """Test that Pinecone credentials with default index are retrieved correctly."""
        credentials = get_pinecone_credentials()
        self.assertEqual(credentials["api_key"], "test-pinecone-key")
        self.assertEqual(credentials["environment"], "test-env")
        self.assertEqual(credentials["index_name"], "vidst-vectors")  # Default value

    @patch.dict(os.environ, {
        "TWELVE_LABS_API_KEY": "test-api-key",
        "TWELVE_LABS_API_URL": "https://test-api.twelvelabs.io",
        "PINECONE_API_KEY": "test-pinecone-key",
        "PINECONE_ENVIRONMENT": "test-env",
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json",
        "GOOGLE_DOCUMENT_AI_PROCESSOR_ID": "test-processor",
        "GOOGLE_DOCUMENT_AI_LOCATION": "eu",
    })
    def test_get_document_ai_credentials_custom(self):
        """Test that Document AI credentials with custom values are retrieved correctly."""
        credentials = get_document_ai_credentials()
        self.assertEqual(credentials["credentials_path"], "/path/to/credentials.json")
        self.assertEqual(credentials["processor_id"], "test-processor")
        self.assertEqual(credentials["location"], "eu")

    @patch.dict(os.environ, {
        "TWELVE_LABS_API_KEY": "test-api-key",
        "TWELVE_LABS_API_URL": "https://test-api.twelvelabs.io",
        "PINECONE_API_KEY": "test-pinecone-key",
        "PINECONE_ENVIRONMENT": "test-env",
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json",
    })
    def test_get_document_ai_credentials_default(self):
        """Test that Document AI credentials with default values are retrieved correctly."""
        credentials = get_document_ai_credentials()
        self.assertEqual(credentials["credentials_path"], "/path/to/credentials.json")
        self.assertEqual(credentials["processor_id"], "")  # Default empty value
        self.assertEqual(credentials["location"], "us")  # Default value

    @patch.dict(os.environ, {
        "TWELVE_LABS_API_KEY": "test-api-key",
        "TWELVE_LABS_API_URL": "https://test-api.twelvelabs.io",
        "PINECONE_API_KEY": "test-pinecone-key",
        "PINECONE_ENVIRONMENT": "test-env",
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json",
        "OPENAI_API_KEY": "test-openai-key",
    })
    def test_get_whisper_credentials_present(self):
        """Test that Whisper credentials are retrieved correctly when present."""
        credentials = get_whisper_credentials()
        self.assertIsNotNone(credentials)
        self.assertEqual(credentials["api_key"], "test-openai-key")

    @patch.dict(os.environ, {
        "TWELVE_LABS_API_KEY": "test-api-key",
        "TWELVE_LABS_API_URL": "https://test-api.twelvelabs.io",
        "PINECONE_API_KEY": "test-pinecone-key",
        "PINECONE_ENVIRONMENT": "test-env",
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json",
        # No OPENAI_API_KEY
    })
    def test_get_whisper_credentials_missing(self):
        """Test that None is returned when Whisper credentials are missing."""
        credentials = get_whisper_credentials()
        self.assertIsNone(credentials)

if __name__ == "__main__":
    unittest.main()