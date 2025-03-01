"""Unit tests for the credentials module."""

import os
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock

import pytest

from video_understanding.core.config.credentials import (
    CredentialError,
    find_env_file,
    load_credentials,
    validate_credentials,
    get_service_credentials,
    get_all_credentials,
)


class TestCredentials:
    """Tests for credentials module."""

    @patch("video_understanding.core.config.credentials.Path")
    def test_find_env_file_found(self, mock_path):
        """Test find_env_file when file exists."""
        # Setup mock
        mock_file = Mock()
        mock_file.exists.return_value = True
        mock_cwd = MagicMock()
        mock_cwd.__truediv__.return_value = mock_file  # Mock the / operator
        mock_path.cwd.return_value = mock_cwd

        # Call function
        result = find_env_file()

        # Assert
        assert result == mock_file
        mock_file.exists.assert_called_once()

    @patch("video_understanding.core.config.credentials.Path")
    def test_find_env_file_not_found(self, mock_path):
        """Test find_env_file when file does not exist."""
        # Setup mocks
        mock_file = Mock()
        mock_file.exists.return_value = False

        # Mock cwd path
        mock_cwd = MagicMock()
        mock_cwd.__truediv__.return_value = mock_file
        mock_path.cwd.return_value = mock_cwd

        # Mock project root path
        mock_project_root = MagicMock()
        mock_project_root.__truediv__.return_value = mock_file
        mock_file_attr = MagicMock()
        mock_file_attr.parents = {4: mock_project_root}
        mock_path.__file__ = mock_file_attr

        # Mock home path
        mock_home = MagicMock()
        mock_vidst_dir = MagicMock()
        mock_vidst_dir.__truediv__.return_value = mock_file
        mock_home.__truediv__.return_value = mock_vidst_dir
        mock_path.home.return_value = mock_home

        # Call function & assert
        with pytest.raises(CredentialError) as excinfo:
            find_env_file()

        assert ".env file not found" in str(excinfo.value)

    @patch("video_understanding.core.config.credentials.find_env_file")
    @patch("video_understanding.core.config.credentials.load_dotenv")
    def test_load_credentials(self, mock_load_dotenv, mock_find_env_file):
        """Test loading credentials from environment."""
        # Setup mocks
        mock_find_env_file.return_value = Path("/fake/.env")
        mock_env = {
            "OPENAI_API_KEY": "test-openai-key",
            "GEMINI_API_KEY": "test-gemini-key",
            "TWELVE_LABS_API_KEY": "test-12labs-key",
            "PINECONE_API_KEY": "test-pinecone-key",
            "PINECONE_ENVIRONMENT": "test-pinecone-env",
            "OTHER_ENV_VAR": "should-not-be-included",
        }

        with patch.dict(os.environ, mock_env, clear=True):
            # Call function
            result = load_credentials()

        # Verify
        assert "OPENAI_API_KEY" in result
        assert result["OPENAI_API_KEY"] == "test-openai-key"
        assert "PINECONE_ENVIRONMENT" in result
        assert "OTHER_ENV_VAR" not in result
        mock_load_dotenv.assert_called_once_with(mock_find_env_file.return_value)

    def test_validate_credentials_all_present(self):
        """Test validation when all credentials are present."""
        # Setup test data
        credentials = {
            "OPENAI_API_KEY": "test-key",
            "GEMINI_API_KEY": "test-key",
            "TWELVE_LABS_API_KEY": "test-key",
            "PINECONE_API_KEY": "test-key",
            "PINECONE_ENVIRONMENT": "test-env",
            "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/creds.json",
            "GOOGLE_CLOUD_PROJECT_ID": "test-project",
            "DOCUMENT_AI_OCR_PROCESSOR_ID": "test-processor",
        }

        # Call function - should not raise
        validate_credentials(credentials)

    def test_validate_credentials_missing(self):
        """Test validation when credentials are missing."""
        # Setup test data - missing required keys
        credentials = {
            "OPENAI_API_KEY": "test-key",
            # Missing GEMINI_API_KEY
            "TWELVE_LABS_API_KEY": "test-key",
            "PINECONE_API_KEY": "test-key",
            # Missing PINECONE_ENVIRONMENT
        }

        # Call function & assert
        with pytest.raises(CredentialError) as excinfo:
            validate_credentials(credentials)

        # Verify error message contains missing keys
        error_msg = str(excinfo.value)
        assert "Gemini: GEMINI_API_KEY" in error_msg
        assert "Pinecone: PINECONE_ENVIRONMENT" in error_msg

    @patch("video_understanding.core.config.credentials.load_credentials")
    def test_get_service_credentials(self, mock_load_credentials):
        """Test getting credentials for a specific service."""
        # Setup mock
        mock_load_credentials.return_value = {
            "OPENAI_API_KEY": "test-openai-key",
            "GEMINI_API_KEY": "test-gemini-key",
        }

        # Call function
        result = get_service_credentials("openai")

        # Verify
        assert "OPENAI_API_KEY" in result
        assert result["OPENAI_API_KEY"] == "test-openai-key"
        assert len(result) == 1  # Only contains OpenAI key

    @patch("video_understanding.core.config.credentials.load_credentials")
    def test_get_service_credentials_missing(self, mock_load_credentials):
        """Test getting credentials when a required key is missing."""
        # Setup mock - missing required key
        mock_load_credentials.return_value = {
            "OPENAI_API_KEY": "test-openai-key",
            # PINECONE_ENVIRONMENT is missing
            "PINECONE_API_KEY": "test-pinecone-key",
        }

        # Call function & assert
        with pytest.raises(CredentialError) as excinfo:
            get_service_credentials("pinecone")

        assert "PINECONE_ENVIRONMENT" in str(excinfo.value)

    @patch("video_understanding.core.config.credentials.load_credentials")
    def test_get_service_credentials_unknown_service(self, mock_load_credentials):
        """Test getting credentials for an unknown service."""
        # Setup mock
        mock_load_credentials.return_value = {}

        # Call function & assert
        with pytest.raises(CredentialError) as excinfo:
            get_service_credentials("unknown-service")

        assert "Unknown service" in str(excinfo.value)

    @patch("video_understanding.core.config.credentials.load_credentials")
    def test_get_all_credentials(self, mock_load_credentials):
        """Test getting all credentials organized by service."""
        # Setup mock
        mock_load_credentials.return_value = {
            "OPENAI_API_KEY": "test-openai-key",
            "GEMINI_API_KEY": "test-gemini-key",
            "TWELVE_LABS_API_KEY": "test-12labs-key",
            "PINECONE_API_KEY": "test-pinecone-key",
            "PINECONE_ENVIRONMENT": "test-pinecone-env",
        }

        # Call function
        result = get_all_credentials()

        # Verify
        assert "openai" in result
        assert result["openai"]["OPENAI_API_KEY"] == "test-openai-key"
        assert "gemini" in result
        assert "twelve_labs" in result
        assert "pinecone" in result
        assert len(result["pinecone"]) == 2  # Contains both Pinecone keys
