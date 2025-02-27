
Configuration Guide


























.. module:: src.core.config

.. index::

   single: configuration
   single: settings
   single: environment variables

Overview


























The Video Understanding AI system uses a flexible configuration system to manage settings for video processing, system resources, and API integrations. This guide explains how to effectively configure and customize the system for your needs.

Configuration Components


























The system's configuration is divided into several components:

1. Environment Variables

   - API keys
   - Environment-specific settings
   - Debug flags

2. Video Configuration

   - File size limits
   - Supported formats
   - Processing parameters

3. System Configuration

   - Resource limits
   - Concurrent processing
   - Memory management

Getting Started


























Basic Setup


-----------





-----------





-----------





-----------





-----------




1. Create a ``.env`` file in your project root:

   .. code-block:: bash

      Required API Keys








=





=

      GEMINI_API_KEY=your_gemini_key_here
      TWELVE_LABS_API_KEY=your_twelve_labs_key_here

      Environment Settings








=





=

      DEBUG=true

      Processing Settings








=





=

      MAX_CONCURRENT_JOBS=3
      CACHE_TTL=86400

2. Load configuration in your code:

   .. code-block:: python

      from src.core.config import load_config, VideoConfig

      Load environment configuration








=





=


      Initialize video configuration








=





=

      video_config.validate()

Common Use Cases


























.. index::

   single: video configuration
   single: processing settings
   pair: configuration; video processing

Custom Video Processing Settings


--------------------------------





--------------------------------





--------------------------------





--------------------------------





--------------------------------




Customize video processing parameters:

.. code-block:: python

   from pathlib import Path
   from src.core.config import VideoConfig

   Custom video configuration










=





=

      upload_directory=Path("/custom/uploads"),
      supported_formats=["MP4", "MOV"],

      max_file_size=1024 * 1024 * 1024,  1GB








=





=









=





=

   )

   Validate configuration










=





=


Resource Management


-------------------





-------------------





-------------------





-------------------





-------------------




.. index::

   single: resource management
   pair: configuration; resources
   pair: configuration; memory limits

Configure system resource limits:

.. code-block:: python

   from src.core.config import ProcessingConfig

   Custom processing configuration










=





=

      MAX_CONCURRENT_JOBS=5,

      MEMORY_LIMIT_PER_JOB=8 * 1024 * 1024 * 1024  8GB








=





=


Environment-Specific Configuration


----------------------------------





----------------------------------





----------------------------------





----------------------------------





----------------------------------




.. index::

   single: environment configuration
   pair: configuration; environment
   pair: configuration; production

Handle different environments:

.. code-block:: python

   def get_environment_config():
      config = load_config()

      if config['environment'] == 'production':
         return VideoConfig(

               max_file_size=5 * 1024 * 1024 * 1024,  5GB








=





=

         )
      else:
         return VideoConfig(

               max_file_size=1024 * 1024 * 1024,  1GB








=





=

         )

Best Practices


























Environment Variables


---------------------





---------------------





---------------------





---------------------





---------------------




.. index::

   single: environment variables
   pair: configuration; security
   pair: configuration; API keys

1. **Security**:

   .. code-block:: python

      import os
      from dotenv import load_dotenv

      def load_secure_config():

         Load from environment first








=





=


         Validate API keys








=





=

         if not api_key:
            raise ConfigurationError(
                  "OpenAI API key not found. Please set OPENAI_API_KEY."
            )

         Never log or expose API keys








=





=









=





=

See Also






























\* :doc:`/guides/security`*


-------------------------




Indices and Tables





























\* :ref:`modindex`*
