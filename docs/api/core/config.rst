
Configuration

=============











Overview


--------





--------





--------





--------





--------




The configuration module provides centralized management of system settings and options.

Classes


-------





-------





-------





-------





-------








Config


------
























.. autoclass:: src.core.config.Config

   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:




ProcessingConfig

























.. autoclass:: src.core.config.ProcessingConfig

   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:




StorageConfig

























.. autoclass:: src.core.config.StorageConfig

   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:




VideoConfig

























.. autoclass:: src.core.config.VideoConfig

   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Functions


---------





---------





---------





---------





---------




.. autofunction:: src.core.config.load_config

   :no-index:

.. autofunction:: src.core.config.get_default_config

   :no-index:

.. autofunction:: src.core.config.validate_config

   :no-index:

Configuration Examples


----------------------





----------------------





----------------------





----------------------





----------------------







Environment Variables

























Loading configuration from environment variables:

.. code-block:: python

      VIDST_API_KEY=xxx
      VIDST_MAX_THREADS=4
      VIDST_CACHE_TTL=3600




File-based Configuration

























Loading from configuration files:

.. code-block:: python

      config = load_config(Path("config.yaml"))




Dynamic Configuration

























Runtime configuration updates:

.. code-block:: python

      config.api_keys["openai"] = "new_key"
      config.validate()

Best Practices


--------------





--------------





--------------





--------------





--------------




- Use environment variables for sensitive data
- Store defaults in version control
- Document all configuration options
- Validate configuration at startup
- Provide helpful error messages
- Handle missing values gracefully

See Also


--------





--------





--------





--------





--------




\* :doc:`/guides/configuration`*
\* :doc:`/api/core/exceptions`*

Indices and Tables


------------------





------------------





------------------





------------------





------------------







\* :ref:`modindex`*
