
Caching Guide


























Overview


--------





--------





--------





--------





--------




The Video Understanding AI system uses a sophisticated two-level caching system to optimize performance and reduce computational overhead. This guide explains how to effectively use caching in your applications, with practical examples and best practices.

Why Use Caching?


----------------





----------------





----------------





----------------





----------------




- Improve response times for frequently accessed data
- Reduce computational load on expensive operations
- Minimize API calls to external services
- Optimize resource usage across the system

Cache Architecture


------------------





------------------





------------------





------------------





------------------




Our caching system implements a two-level architecture:

1. Memory Cache

   - Fast access
   - Thread-safe operations
   - Volatile (cleared on system restart)

2. File Cache

   - Persistent storage
   - JSON-based format
   - Automatic cleanup

Getting Started


---------------





---------------





---------------





---------------





---------------


























Basic Setup
























.. code-block:: python

      from pathlib import Path
      from src.storage.cache import Cache

      Initialize with default settings (24-hour TTL)








=





=


      Or customize cache location and TTL








=





=

         cache_dir=Path("custom_cache"),

         ttl=3600  1 hour








=





=


Common Use Cases


----------------





----------------





----------------





----------------





----------------








----------------

























Caching Video Processing Results

































.. code-block:: python

      def process_video_segment(video_id: str, segment_id: str):

         Create cache key








^





"


         Try to get cached result








"





"

         result = cache.get(cache_key)

         if result:
            return result

         Process video if not in cache








"





"


         Cache the result








"





"

            "frames": result.frames,
            "metadata": result.metadata
         })

         return result

Caching API Responses


---------------------





---------------------





---------------------





---------------------





---------------------








---------------------










.. code-block:: python

      def get_video_metadata(video_id: str):

         cache = Cache(ttl=1800)  30-minute TTL








"





"


         Check cache first








"





"

         if metadata:
            return metadata

         Make API call if not cached








"





"


         Cache response








"





"

         return metadata

Best Practices


--------------





--------------





--------------





--------------





--------------








==========



Cache Keys

==========

























1. Use descriptive, hierarchical keys:

   .. code-block:: python

         Good








"





"

         "user_456_preferences"

         Bad








"





"

         "data_1"

2. Include version information for schema changes:

   .. code-block:: python

         cache_key = f"v2_video_{video_id}_analysis"

TTL Management


--------------





--------------





--------------





--------------





--------------








--------------










1. Choose appropriate TTL based on data type:

   .. code-block:: python

         Frequently changing data








"





"









"





"

         Stable data








"





"









"





"

2. Use shorter TTL for memory-intensive data:

   .. code-block:: python

         Large video processing results








"





"









"





"

Error Handling


--------------





--------------





--------------





--------------





--------------








--------------










Implement graceful fallbacks:

.. code-block:: python

      from src.core.exceptions import StorageError

      def get_cached_data(key: str):
         cache = Cache()
         try:
            data = cache.get(key)
            if data:
                  return data
         except StorageError as e:
            logger.warning(f"Cache error: {e}")

            Continue with fallback








"





"

         return compute_fresh_data()

Resource Management


-------------------





-------------------





-------------------





-------------------





-------------------








-------------------










1. Implement periodic cleanup:

   .. code-block:: python

         def maintenance_task():
            cache = Cache()

            try:
                  Clean expired entries
                  cache.cleanup()

                  Log cache stats
                  log_cache_usage()
            except StorageError as e:
                  logger.error(f"Cache maintenance failed: {e}")

      2. Monitor cache size:

   .. code-block:: python

         def check_cache_size():
            cache_dir = Path("cache")
            total_size = sum(f.stat().st_size for f in cache_dir.glob("*.json"))

            if total_size > MAX_CACHE_SIZE:
                  logger.warning("Cache size exceeds limit")
                  cache.clear()

Common Pitfalls


---------------





---------------





---------------





---------------





---------------




1. **Cache Invalidatio***n**: Keep track of dependencies***

   .. code-block:: python

         def update_video(video_id: str):
            Update video
            process_video_update(video_id)

            Invalidate related caches
            cache = Cache()
            cache.clear()  Consider more targeted clearing

      2. **Memory Usage**: Monitor memory cache size

   .. code-block:: python

         def cache_large_data(key: str, data: dict):
            if sys.getsizeof(data) > MAX_MEMORY_CACHE_SIZE:
                  logger.warning("Data too large for memory cache")
                  Consider alternative storage
            cache.set(key, data)

      3. **Concurrent Access**: Use provided thread-safe methods

   .. code-block:: python

         Correct - uses internal locking








"





"


         Incorrect - may cause race conditions








"





"

            cache.memory_cache[key] = value

Advanced Usage


--------------





--------------





--------------





--------------





--------------







Custom Cache Wrapper


--------------------
























Create a domain-specific cache wrapper:

.. code-block:: python

      class VideoCache:
         def __init__(self):
            self.cache = Cache(ttl=3600)

         def get_analysis(self, video_id: str):
            return self.cache.get(f"analysis_{video_id}")

         def set_analysis(self, video_id: str, analysis: dict):
            self.cache.set(f"analysis_{video_id}", analysis)

         def invalidate_video(self, video_id: str):

            Clear all caches related to this video








"





"

                  f"analysis_{video_id}",
                  f"metadata_{video_id}",
                  f"transcription_{video_id}"
            ]
            for pattern in patterns:
                  try:
                     self.cache.clear(pattern)
                  except StorageError:
                     continue

Monitoring and Maintenance


--------------------------





--------------------------





--------------------------





--------------------------





--------------------------








--------------------------










Implement cache monitoring:

.. code-block:: python

      def monitor_cache_health():
         cache = Cache()
         stats = {
            "memory_entries": len(cache.memory_cache),
            "file_entries": len(list(cache.cache_dir.glob("*.json"))),
            "cache_size": sum(f.stat().st_size for f in cache.cache_dir.glob("*.json"))
         }

         Log or report stats








"





"


         Check for issues








"





"

            alert_cache_size_issue()

         return stats

Additional Resources


--------------------





--------------------





--------------------





--------------------





--------------------




- :doc:`/api/storage/cache` - Detailed API documentation
- :doc:`error-handling` - Error handling guide
- :doc:`configuration` - System configuration guide

Indices and Tables


------------------





------------------





------------------





------------------





------------------







\* :ref:`modindex`*
