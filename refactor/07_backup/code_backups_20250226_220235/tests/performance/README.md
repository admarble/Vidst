# Performance Testing Guide

## Overview

This guide covers the performance testing framework for the Video Understanding AI system. The framework tests various aspects of system performance including processing speed, memory usage, resource utilization, and system stability.

## Test Categories

### 1. Upload Performance

Tests video upload functionality:

- Upload speeds for different file sizes (10MB - 500MB)
- Memory usage during uploads
- Concurrent upload handling
- Error handling and recovery

### 2. Processing Pipeline Performance

Tests video processing capabilities:

- Scene detection speed
- Object recognition accuracy
- Action recognition performance
- Text extraction efficiency
- Processing time vs. video duration ratio

### 3. Memory Usage

Tests memory management:

- Peak memory usage monitoring
- Memory leak detection
- Resource cleanup verification
- Concurrent processing impact

### 4. Cache Performance

Tests caching system:

- Cache hit/miss rates
- Cache invalidation timing
- Memory usage patterns
- Concurrent access handling

### 5. API Rate Limits

Tests API interaction:

- Request throttling
- Backoff strategies
- Error handling
- Recovery mechanisms

### 6. Vector Search

Tests vector operations:

- Search speed with large datasets
- Index performance
- Memory efficiency
- Result accuracy

## Running Tests

```bash
# Run all performance tests
pytest tests/performance/

# Run specific test categories
pytest tests/performance/test_performance.py -k "test_upload"
pytest tests/performance/test_performance.py -k "test_memory"

# Run with different configurations
pytest tests/performance/test_performance.py -m "not slow"  # Skip long-running tests
pytest tests/performance/test_performance.py --durations=0  # Show all test durations
```

## Performance Metrics

### PerformanceMetrics Class

The `PerformanceMetrics` class tracks:

- Execution time
- Memory usage
- CPU utilization
- Custom measurements

Example usage:

```python
metrics = PerformanceMetrics()
metrics.measure("start_operation")
# ... perform operation ...
metrics.measure("end_operation")
report = metrics.get_report()
```

### Success Criteria

1. Upload Performance:
   - Minimum upload speed: 10MB/s
   - Maximum memory usage: 4GB
   - Error rate < 1%

2. Processing Speed:
   - Maximum processing time: 2x video duration
   - 95th percentile latency < 5s
   - Concurrent processing: 3+ videos

3. Memory Management:
   - Peak memory < 4GB
   - No memory leaks
   - Resource cleanup verified

4. Cache Performance:
   - Read latency < 1ms
   - Write latency < 5ms
   - Hit rate > 80%

5. API Handling:
   - Max 10 requests/second
   - Successful recovery from failures
   - Proper rate limit adherence

## Mock Implementations

The framework provides mock implementations for external dependencies:

### 1. MockVideoPipeline

Simulates the video processing pipeline:

- Multi-model processing
- Resource management
- Error handling

### 2. MockTwelveLabsModel

Simulates the AI model API:

- Realistic timing patterns
- Error simulation
- Rate limiting

### 3. MockCache

Simulates caching system:

- TTL handling
- Size limits
- Concurrent access

### 4. MockVectorStorage

Simulates vector operations:

- Search functionality
- Index management
- Memory tracking

## Best Practices

1. Test Setup:
   - Use appropriate fixtures
   - Clean up resources
   - Isolate tests
   - Mock external services

2. Performance Measurement:
   - Use PerformanceMetrics consistently
   - Track multiple metrics
   - Log detailed results
   - Compare against baselines

3. Error Handling:
   - Test error scenarios
   - Verify recovery
   - Check resource cleanup
   - Log error details

4. Resource Management:
   - Monitor memory usage
   - Clean up test files
   - Release system resources
   - Check for leaks

## Troubleshooting

Common issues and solutions:

1. Slow Tests:
   - Use appropriate test categories
   - Skip long-running tests when needed
   - Profile test execution
   - Optimize resource usage

2. Memory Issues:
   - Check cleanup procedures
   - Monitor resource usage
   - Use memory profiling
   - Verify mock implementations

3. Failed Assertions:
   - Check performance thresholds
   - Verify test environment
   - Review system resources
   - Check mock configurations

## Contributing

When adding or modifying performance tests:

1. Follow existing patterns
2. Update documentation
3. Add appropriate fixtures
4. Include success criteria
5. Test error scenarios
6. Verify resource cleanup

## References

- [Main Testing Guide](../README.rst)
- [Mock Implementations](../utils/mocks.py)
- [Custom Exceptions](../utils/exceptions.py)
- [Test Configuration](../conftest.py)
