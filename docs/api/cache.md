# Cache System Documentation

## Overview

The cache system provides a two-level caching mechanism (memory and file-based) for storing intermediate processing results. It features thread-safe operations, automatic expiration, and cleanup capabilities.

## Features

- Two-level caching (memory and file)
- Thread-safe operations
- Configurable TTL (Time To Live)
- Automatic cleanup of expired entries
- JSON-based persistence
- Error handling with custom exceptions

## Basic Usage

```python
from pathlib import Path
from src.storage.cache import Cache

# Initialize cache with 1-hour TTL
cache = Cache(cache_dir=Path("cache"), ttl=3600)

# Store data
data = {"result": "processed_data", "metadata": {"timestamp": "2024-02-07"}}
cache.set("process_result", data)

# Retrieve data
result = cache.get("process_result")
if result:
    print(f"Found cached result: {result}")
else:
    print("Cache miss")
```

## API Reference

### Constructor

```python
def __init__(self, cache_dir: Path = None, ttl: int = 86400)
```

Initialize the cache system.

**Parameters**:
- `cache_dir`: Directory for cache files (default: "cache")
- `ttl`: Time to live in seconds (default: 24 hours)

### Methods

#### get()

```python
def get(self, key: str) -> Optional[Dict[str, Any]]
```

Retrieve a value from cache.

**Parameters**:
- `key`: Cache key

**Returns**:
- Cached value if found and not expired
- None if not found or expired

**Example**:
```python
cache = Cache()
result = cache.get("computation_result")
if result:
    use_cached_result(result)
else:
    compute_and_cache_result()
```

#### set()

```python
def set(self, key: str, value: Dict[str, Any]) -> None
```

Store a value in cache.

**Parameters**:
- `key`: Cache key
- `value`: Value to cache (must be JSON-serializable)

**Raises**:
- `StorageError`: If cache operation fails

**Example**:
```python
try:
    cache.set("video_metadata", {
        "duration": 120,
        "resolution": "1920x1080",
        "format": "MP4"
    })
except StorageError as e:
    print(f"Failed to cache: {e}")
```

#### clear()

```python
def clear(self) -> None
```

Clear all cached data (memory and file).

**Example**:
```python
# Clear all cache
cache.clear()
```

#### cleanup()

```python
def cleanup(self) -> None
```

Remove expired entries from both memory and file cache.

**Example**:
```python
# Cleanup expired entries
cache.cleanup()
```

## Implementation Details

### Cache Structure

1. **Memory Cache**:
   ```python
   {
       "key": {
           "timestamp": 1644231892,
           "data": {...}
       }
   }
   ```

2. **File Cache**:
   ```
   cache/
   ├── key1.json
   ├── key2.json
   └── key3.json
   ```

### Thread Safety

The cache implements thread safety using:
```python
self.lock = threading.Lock()

with self.lock:
    # Thread-safe operations
    pass
```

### Cache Entry Format

```json
{
    "timestamp": 1644231892,
    "data": {
        "key1": "value1",
        "key2": "value2"
    }
}
```

## Examples

### Basic Caching

```python
from src.storage.cache import Cache

cache = Cache()

# Cache computation result
result = expensive_computation()
cache.set("computation", result)

# Later, retrieve result
cached_result = cache.get("computation")
if cached_result:
    use_result(cached_result)
```

### Custom TTL

```python
# Create cache with 1-hour TTL
cache = Cache(ttl=3600)

# Cache time-sensitive data
cache.set("api_response", api_call_result)

# Data automatically expires after 1 hour
result = cache.get("api_response")  # None if expired
```

### Error Handling

```python
from src.core.exceptions import StorageError

cache = Cache()

try:
    cache.set("key", {"data": "value"})
except StorageError as e:
    print(f"Cache error: {e}")
    # Handle cache failure
```

### Periodic Cleanup

```python
import schedule
import time

cache = Cache()

def scheduled_cleanup():
    print("Running cache cleanup...")
    cache.cleanup()

# Schedule cleanup every hour
schedule.every().hour.do(scheduled_cleanup)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Best Practices

1. **Cache Keys**:
   - Use descriptive, unique keys
   - Consider namespacing for different components
   - Keep keys reasonably short

2. **Data Storage**:
   - Cache only serializable data
   - Consider data size in memory
   - Use appropriate TTL values

3. **Error Handling**:
   - Always handle StorageError exceptions
   - Implement fallback mechanisms
   - Log cache failures

4. **Maintenance**:
   - Run periodic cleanup
   - Monitor cache size
   - Clear cache on version updates

## Performance Considerations

1. **Memory Usage**:
   - Monitor memory cache size
   - Use appropriate TTL
   - Implement size limits if needed

2. **File System**:
   - Regular cleanup of expired files
   - Monitor disk usage
   - Handle I/O errors gracefully

3. **Concurrency**:
   - Thread-safe operations
   - Minimize lock contention
   - Consider read/write patterns 