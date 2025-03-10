Cache System






.. module:: src.storage.cache

   :no-index:

This module provides caching functionality for the video processing system. It includes both in-memory
and file-based caching with TTL (Time To Live) and size management capabilities.

Key Features






- Thread-safe caching operations
- Hybrid memory and file-based storage
- Automatic cache size management
- TTL-based entry expiration
- Corruption-resistant storage
- Generic type support

Classes


-------




CacheStore


----------




.. autoclass:: CacheStore

   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

   .. rubric:: Size Management

   The CacheStore implements intelligent size management:

   - Tracks total cache size on disk
   - Enforces maximum size limits
   - Removes oldest entries when size limit is reached
   - Performs automatic cleanup of expired entries

   .. rubric:: Error Handling

   Robust error handling for common scenarios:

   - Disk space exhaustion
   - Corrupted cache files
   - Permission issues
   - Concurrent access

   .. rubric:: Example Usage

   .. code-block:: python

         from src.storage.cache import CacheStore
         from datetime import timedelta

         Initialize cache with custom settings





















































         cache = CacheStore(
            cache_dir="/tmp/my_cache",

            max_size=1024 * 1024 * 1024,  1GB

























































default_ttl=timedelta(hours=24)














































         Store data with custom TTL





















































         cache.store(
            key="my_data",
            value={"result": 42},
            ttl=timedelta(hours=1),

metadata={"source": "calculation"}


----------------------------------





----------------------------------





----------------------------------





----------------------------------





----------------------------------





----------------------------------





----------------------------------





----------------------------------





----------------------------------




         Retrieve data





















































         data = cache.retrieve("my_data")

         Clear expired entries





















































         cache.clear_expired()

      Cache




.. autoclass:: Cache

   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

   .. rubric:: Thread Safety

   The Cache class provides thread-safe operations using:

   - Lock-based synchronization
   - Atomic file operations
   - Safe memory cache access

   .. rubric:: Example Usage

   .. code-block:: python

         from src.storage.cache import Cache

         cache = Cache(
            cache_dir="/tmp/cache",

            ttl=3600,  1 hour





















































            max_memory_items=1000
         )

         Store and retrieve data





















































         cache.set("key", {"data": "value"})
         result = cache.get("key")

      CacheEntry




.. autoclass:: CacheEntry

   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

   .. rubric:: Generic Type Support

   CacheEntry supports generic types:

   .. code-block:: python

         from typing import Dict, Any

         Dictionary entry





















































         entry_dict = CacheEntry[Dict[str, Any]](...)

         List entry





















































         entry_list = CacheEntry[list](...)

      Utility Functions




.. autofunction:: cache_data

   :no-index:

.. autofunction:: get_cached_data

   :no-index:

.. autofunction:: clear_cache

   :no-index:

.. autofunction:: clear_expired_cache

   :no-index:

.. autofunction:: get_cache_store

   :no-index:

Configuration





The cache system uses several configuration constants that can be customized:

.. code-block:: python

      DEFAULT_CACHE_SIZE = 1024 * 1024 * 1024  1GB





















































      DEFAULT_TTL = timedelta(hours=24)

      DEFAULT_TTL_SECONDS = 86400  24 hours





















































      DEFAULT_CACHE_DIR = Path("/tmp/cache")
      MAX_KEY_LENGTH = 255

      MEMORY_CACHE_SIZE = 1000  Maximum items in memory cache





















































      Best Practices




1. **Key Managemen***t**

   - Use descriptive but concise keys
   - Keep keys under 255 characters
   - Use consistent key naming patterns

2. **Size Managemen***t**

   - Monitor cache size regularly
   - Set appropriate size limits
   - Use cleanup functions periodically

3. **Error Handlin***g**

   - Always handle StorageError exceptions
   - Implement fallback mechanisms
   - Log cache errors appropriately

4. **Performanc***e**

   - Use memory cache for frequently accessed items
   - Set appropriate TTL values
   - Clean expired entries regularly

Implementation Details





Cache Storage Format





Cache entries are stored in JSON format with the following structure:

.. code-block:: json

      {
         "key": "cache_key",
         "value": "cached_data",
         "created_at": "2024-03-21T10:00:00",
         "expires_at": "2024-03-22T10:00:00",
         "metadata": {
            "custom": "metadata"
         }
      }

File Organization


-----------------





-----------------





-----------------





-----------------





-----------------




Cache files are organized as follows:

.. code-block:: text

      cache_dir/
      ├── key1.cache
      ├── key2.cache
      └── key3.cache

      Each cache entry is stored in a separate file with the .cache extension.

Indices and Tables












\* :doc:`/modindex`*
