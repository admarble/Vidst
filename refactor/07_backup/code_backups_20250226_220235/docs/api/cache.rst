
Cache API






.. module:: src.storage.cache

The Cache module provides a flexible caching system for storing and retrieving data efficiently.

Cache Class






.. class:: Cache

   The main cache class that handles data storage and retrieval.

   .. method str = None, ttl: int = 3600)

      Initialize a new cache instance.

      :param cache_dir: Directory to store cache files
      :param ttl: Time-to-live in seconds (default: 1 hour)

   .. method:: set(key: str, value: Any, ttl: Optional[int] = None) -> None

      Store a value in the cache.

      :param key: Unique identifier for the cached item
      :param value: Data to cache
      :param ttl: Optional custom TTL for this item

   .. method:: get(key: str) -> Optional[Any]

      Retrieve a value from the cache.

      :param key: Key of the item to retrieve
      :returns: Cached value or None if not found/expired

Basic Usage






.. code-block:: python

         from src.storage.cache import Cache

   Initialize cache


































































   cache = Cache(cache_dir="./cache", ttl=3600)

   Store data


































































   cache.set("video_123", processed_data)

   Retrieve data


































































   data = cache.get("video_123")

Configuration






The cache can be configured with the following options:

- ``cache_dir``: Directory for cache storage
- ``ttl``: Default time-to-live for cached items
- ``max_size``: Maximum cache size in bytes
- ``cleanup_interval``: Interval for automatic cleanup

Error Handling






The cache module uses the following error types:

.. class:: StorageError

   Base exception for cache-related errors.

   .. method str, cause: Optional[Exception] = None)

      :param message: Error description
      :param cause: Original exception that caused this error

Best Practices






1. Use descriptive keys
2. Set appropriate TTL values
3. Handle cache misses gracefully
4. Monitor cache usage
5. Implement cleanup strategies

Example:

.. code-block:: python

         try:
         data = cache.get("key")
         if data is None:
            data = expensive_operation()
            cache.set("key", data)

   except StorageError as e:
         logger.error(f"Cache error: {e}")
         data = expensive_operation()

      Indices and Tables








\* :doc:`/modindex`*
