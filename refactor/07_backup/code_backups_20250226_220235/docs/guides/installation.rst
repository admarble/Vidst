
Installation Guide

==================











Getting Started


---------------





---------------





---------------





---------------





---------------




1. Clone the repository::

      git clone https://github.com/your-org/video-understanding-poc
      cd video-understanding-poc


2. Create virtual environment:

.. code-block:: bash

      On Unix/macOS:








=





=

      source venv/bin/activate

      On Windows:








=





=

      venv\Scripts\activate

3. Install dependencies::

      pip install -r requirements.txt

Configuration


-------------





-------------





-------------





-------------





-------------




Environment Setup


-----------------





-----------------





-----------------





-----------------





-----------------




1. Copy the example environment file::

      cp .env.example .env

2. Edit the configuration::

      Required API keys
      OPENAI_API_KEY=your_key_here
      TWELVE_LABS_API_KEY=your_key_here

      Optional settings
      MAX_CONCURRENT_JOBS=3
      CACHE_TTL=86400

See :doc:`/getting_started` to begin using the system.

Indices and Tables










\* :doc:`/modindex`*
