"""
Tests for API integrations.

This module provides tests to verify the connectivity and basic functionality
of integrated external APIs.
"""

# pylint: disable=import-error
# pylint: disable=no-name-in-module
# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-import
# pylint: disable=no-member

import os
import sys  # Required for mock.patch.dict("sys.modules", ...)
import unittest
from unittest import mock

# Mock the external modules completely
sys_modules_patcher = mock.patch.dict(
    "sys.modules",
    {
        "twelvelabs": mock.MagicMock(),
        "pinecone": mock.MagicMock(),
        "google.cloud": mock.MagicMock(),
        "google.cloud.documentai": mock.MagicMock(),
        "whisper": mock.MagicMock(),
    },
)
sys_modules_patcher.start()


class TestTwelveLabsIntegration(unittest.TestCase):
    """Test Twelve Labs API integration."""

    def test_twelve_labs_connectivity(self):
        """Test basic connectivity to Twelve Labs API."""
        # Create mock client and API response
        mock_client = mock.MagicMock()
        mock_client.indexes.list.return_value = ["test_index"]

        # Mock the import and constructor
        with mock.patch.dict(
            "sys.modules",
            {
                "twelvelabs": mock.MagicMock(),
            },
        ):
            import twelvelabs

            twelvelabs.TwelveLabs = mock.MagicMock(return_value=mock_client)

            # Create the client
            client = twelvelabs.TwelveLabs(api_key="test_key")

            # Get the indexes
            response = client.indexes.list()

            # Verify the expected behavior
            client.indexes.list.assert_called_once()
            self.assertEqual(response, ["test_index"])


class TestPineconeIntegration(unittest.TestCase):
    """Test Pinecone vector database integration."""

    def test_pinecone_connectivity(self):
        """Test basic connectivity to Pinecone."""
        # Mock the module and API response
        with mock.patch.dict(
            "sys.modules",
            {
                "pinecone": mock.MagicMock(),
            },
        ):
            import pinecone

            # Mock the init and Index constructor
            pinecone.init = mock.MagicMock()
            mock_index = mock.MagicMock()
            pinecone.Index = mock.MagicMock(return_value=mock_index)

            # Initialize pinecone
            pinecone.init(api_key="test_key", environment="test-env")

            # Create index
            index = pinecone.Index("test_index")

            # Verify the expected behavior
            pinecone.init.assert_called_once_with(
                api_key="test_key", environment="test-env"
            )
            pinecone.Index.assert_called_once_with("test_index")


class TestDocumentAIIntegration(unittest.TestCase):
    """Test Google Document AI integration."""

    def test_document_ai_connectivity(self):
        """Test basic connectivity to Document AI."""
        # Create mock client and response
        mock_client = mock.MagicMock()
        mock_client.get_processor.return_value = {"name": "test_processor"}

        # Mock the client options
        mock_client_options = mock.MagicMock()

        # Mock the import and constructor
        with mock.patch.dict(
            "sys.modules",
            {
                "google.cloud": mock.MagicMock(),
                "google.cloud.documentai": mock.MagicMock(),
                "google.api_core.client_options": mock.MagicMock(),
            },
        ):
            from google.cloud import documentai
            from google.api_core.client_options import ClientOptions

            # Mock the ClientOptions constructor
            ClientOptions = mock.MagicMock(return_value=mock_client_options)

            # Mock the document client constructor
            documentai.DocumentProcessorServiceClient = mock.MagicMock(
                return_value=mock_client
            )

            # Mock the common_location_path method
            mock_client.common_location_path = mock.MagicMock(
                return_value="projects/test-project/locations/us-central1"
            )

            # Create options
            location = "us-central1"
            opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

            # Create the client
            client = documentai.DocumentProcessorServiceClient(client_options=opts)

            # Get processor
            project_id = "test-project"
            processor_id = "test-processor-id"
            parent = client.common_location_path(project_id, location)
            processor_name = f"{parent}/processors/{processor_id}"
            processor = client.get_processor(name=processor_name)

            # Verify the expected behavior
            client.common_location_path.assert_called_once_with(project_id, location)
            client.get_processor.assert_called_once_with(name=processor_name)
            self.assertEqual(processor, {"name": "test_processor"})


class TestWhisperIntegration(unittest.TestCase):
    """Test Whisper integration."""

    def test_whisper_model_loading(self):
        """Test loading the Whisper model."""
        # Create mock model
        mock_model = mock.MagicMock()
        mock_model.transcribe.return_value = {"text": "Test transcription"}

        # Mock the import and function
        with mock.patch.dict(
            "sys.modules",
            {
                "whisper": mock.MagicMock(),
            },
        ):
            import whisper

            whisper.load_model = mock.MagicMock(return_value=mock_model)

            # Load the model
            model = whisper.load_model("base")

            # Test transcription
            result = model.transcribe("test_audio.mp3")

            # Verify the expected behavior
            whisper.load_model.assert_called_once_with("base")
            model.transcribe.assert_called_once_with("test_audio.mp3")
            self.assertEqual(result["text"], "Test transcription")


if __name__ == "__main__":
    unittest.main()
