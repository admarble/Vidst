====================
API Integration Guide
====================

This guide covers the setup and integration of external APIs used in the Vidst system.

Overview
========

Vidst now integrates with several cloud API services to enhance video understanding capabilities:

- **Twelve Labs**: Advanced video understanding API for scene detection and content analysis
- **Pinecone**: Vector database for efficient storage and retrieval of embeddings
- **Google Document AI**: Document processing and OCR capabilities
- **OpenAI Whisper**: State-of-the-art speech recognition

Prerequisites
============

Before integrating these APIs, ensure you have:

1. Active accounts with each service provider
2. API keys or credentials for each service
3. Appropriate permissions to create and manage resources

Installation
===========

The required dependencies are included in the main ``requirements.txt`` file:

.. code-block:: bash

    pip install -r requirements.txt

This will install the following packages:

- ``twelvelabs-client>=1.0.0``: Client library for Twelve Labs API
- ``pinecone-client>=2.2.1``: Client library for Pinecone vector database
- ``google-cloud-documentai>=2.16.0``: Client library for Google Document AI
- ``google-cloud-storage>=2.8.0``: Google Cloud Storage client
- ``openai-whisper>=20230314``: OpenAI Whisper for speech recognition

Configuration
============

Configuration templates are provided in ``src/video_understanding/core/config/templates/``:

1. Copy the template files to your local configuration directory
2. Update the configuration files with your API keys and settings

.. code-block:: bash

    # Create your configuration directory if it doesn't exist
    mkdir -p config/local

    # Copy template files
    cp src/video_understanding/core/config/templates/*.yaml config/local/

Twelve Labs Setup
================

1. Sign up for an account at `Twelve Labs <https://twelvelabs.io/>`_
2. Create an API key in the developer dashboard
3. Set your API key in the environment:

.. code-block:: bash

    export TWELVE_LABS_API_KEY=your_api_key_here

4. Configure the Twelve Labs client in your application:

.. code-block:: python

    from twelvelabs import TwelveLabsClient

    # Initialize with API key from environment variable
    client = TwelveLabsClient()

    # Or initialize with explicit API key
    client = TwelveLabsClient(api_key="your_api_key_here")

    # Create an index
    index = client.create_index(
        name="vidst_index",
        engine_id="marengo2.5",
        index_options=["visual", "conversation", "text_in_video"]
    )

For more detailed usage examples, see the `Twelve Labs API <https://docs.twelvelabs.io/docs>`_ documentation.

Pinecone Setup
=============

1. Sign up for a Pinecone account at `Pinecone <https://www.pinecone.io/>`_
2. Create an API key and environment in the console
3. Set your API credentials in the environment:

.. code-block:: bash

    export PINECONE_API_KEY=your_api_key_here
    export PINECONE_ENVIRONMENT=your_environment_here

4. Configure the Pinecone client in your application:

.. code-block:: python

    import pinecone

    # Initialize with API key from environment variable
    pinecone.init()

    # Create an index if it doesn't exist
    if "vidst_embeddings" not in pinecone.list_indexes():
        pinecone.create_index(
            name="vidst_embeddings",
            dimension=1536,
            metric="cosine"
        )

    # Connect to the index
    index = pinecone.Index("vidst_embeddings")

For more detailed usage examples, see the `Pinecone documentation <https://docs.pinecone.io/>`_.

Google Document AI Setup
=======================

1. Create a Google Cloud account if you don't have one
2. Enable the Document AI API in your Google Cloud Console
3. Create a service account and download the JSON key file
4. Set the environment variable to point to your service account key:

.. code-block:: bash

    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
    export GOOGLE_CLOUD_PROJECT_ID="your-project-id"

5. Configure Document AI in your application:

.. code-block:: python

    from google.cloud import documentai

    # Initialize Document AI client
    client = documentai.DocumentProcessorServiceClient()

    # Format the resource name
    parent = f"projects/{project_id}/locations/{location}"

    # Get the processor name
    processor_name = f"{parent}/processors/{processor_id}"

    # Process a document
    with open(document_path, "rb") as document:
        document_content = document.read()

    # Configure the process request
    request = documentai.ProcessRequest(
        name=processor_name,
        raw_document=documentai.RawDocument(
            content=document_content,
            mime_type="application/pdf"
        )
    )

    # Process the document
    result = client.process_document(request=request)
    document = result.document

For more detailed usage examples, see the `Google Document AI documentation <https://cloud.google.com/document-ai/docs>`_.

OpenAI Whisper Setup
===================

OpenAI Whisper is a locally run model that doesn't require API keys. However, you'll need sufficient hardware resources for the larger models.

1. Install the required dependencies:

.. code-block:: bash

    pip install openai-whisper torch ffmpeg-python

2. Use Whisper in your application:

.. code-block:: python

    import whisper

    # Load the model
    model = whisper.load_model("large-v3")

    # Transcribe audio
    result = model.transcribe("path/to/audio.mp3")

    # Get the transcription text
    transcription = result["text"]

    # Get segments with timestamps
    segments = result["segments"]
    for segment in segments:
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"]
        print(f"{start_time:.2f} - {end_time:.2f}: {text}")

For more detailed usage examples, see the `OpenAI Whisper GitHub repository <https://github.com/openai/whisper>`_.

Environment Variables
===================

Here's a summary of all the environment variables needed for the API integrations:

.. code-block:: bash

    # Twelve Labs
    TWELVE_LABS_API_KEY=your_api_key_here

    # Pinecone
    PINECONE_API_KEY=your_api_key_here
    PINECONE_ENVIRONMENT=your_environment_here

    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
    GOOGLE_CLOUD_PROJECT_ID=your-project-id
    DOCUMENT_AI_OCR_PROCESSOR_ID=your-ocr-processor-id
    DOCUMENT_AI_FORM_PROCESSOR_ID=your-form-processor-id
    DOCUMENT_AI_CODE_PROCESSOR_ID=your-code-processor-id
    GCS_BUCKET_NAME=your-gcs-bucket-name

Testing Your Configuration
=========================

To verify your API configurations:

.. code-block:: python

    # tests/test_api_integrations.py

    import os
    import unittest

    class TestAPIIntegrations(unittest.TestCase):
        def test_twelve_labs_connectivity(self):
            from twelvelabs import TwelveLabsClient
            client = TwelveLabsClient()
            response = client.get_indexes()
            self.assertIsNotNone(response)

        def test_pinecone_connectivity(self):
            import pinecone
            pinecone.init()
            indexes = pinecone.list_indexes()
            self.assertIsInstance(indexes, list)

        def test_document_ai_connectivity(self):
            from google.cloud import documentai
            client = documentai.DocumentProcessorServiceClient()
            parent = f"projects/{os.environ['GOOGLE_CLOUD_PROJECT_ID']}/locations/us-central1"
            processors = client.list_processors(parent=parent)
            self.assertIsNotNone(processors)

        def test_whisper_model(self):
            import whisper
            model = whisper.load_model("base")
            self.assertIsNotNone(model)

Run the tests with:

.. code-block:: bash

    python -m unittest tests/test_api_integrations.py

Troubleshooting
==============

Common Issues
------------

**API Rate Limiting**

- Implement exponential backoff with the `backoff` package
- Use caching to reduce API calls

**Authentication Errors**

- Verify API keys are correct and have not expired
- Check environment variables are correctly set
- Ensure proper permissions are assigned to service accounts

**Compatibility Issues**

- Check version compatibility between client libraries and APIs
- Update to the latest stable versions when possible

Getting Help
-----------

If you encounter issues with the API integrations:

1. Check the API provider's documentation and status pages
2. Look for error messages in the logs
3. Check issue tracker for similar problems
4. Post a question on the project's discussion forum

Conclusion
=========

These API integrations significantly enhance Vidst's video understanding capabilities. By leveraging these external services, we reduce the need for custom implementations while improving accuracy and performance.

For further assistance, contact the project maintainers or refer to the individual API documentation.
