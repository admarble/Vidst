# Testing Guide

## Overview

Our testing framework provides comprehensive test coverage across multiple test types and levels. It uses pytest as the primary testing framework with additional tools for coverage reporting and performance testing.

## Test Structure

```
tests/
├── unit/               # Unit tests
│   ├── test_basic.py
│   ├── test_ai_models.py
│   └── test_error_handling.py
├── integration/        # Integration tests
├── performance/        # Performance tests
├── storage/           # Storage-specific tests
├── ai/                # AI model tests
├── video/             # Video processing tests
├── core/              # Core functionality tests
└── conftest.py        # Shared test fixtures
```

## Test Types

### Unit Tests

Located in `tests/unit/`, these tests verify individual components in isolation.

```python
# tests/unit/test_error_handling.py
def test_file_validation_errors():
    config = VideoConfig()
    uploader = VideoUploader(config)

    with pytest.raises(FileValidationError, match="File does not exist"):
        uploader.validate_file("nonexistent.mp4")
```

### Integration Tests

Located in `tests/integration/`, these tests verify component interactions.

```python
# tests/integration/test_pipeline.py
def test_full_processing_pipeline():
    pipeline = VideoPipeline(config)
    result = pipeline.process({
        "video_path": "test.mp4",
        "start_time": 0,
        "end_time": 10
    })
    assert result["status"] == "completed"
```

### Performance Tests

Located in `tests/performance/`, these tests verify system performance.

```python
# tests/performance/test_processing_speed.py
@pytest.mark.slow
def test_processing_time():
    start_time = time.time()
    result = pipeline.process(video_data)
    processing_time = time.time() - start_time
    assert processing_time < video_duration * 2  # Max 2x video duration
```

## Test Fixtures

### Global Fixtures

Defined in `conftest.py`, these fixtures are available to all tests:

```python
@pytest.fixture(scope="session")
def test_files_dir() -> Generator[Path, None, None]:
    """Create and manage a test files directory."""
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    if test_dir.exists():
        shutil.rmtree(test_dir)
```

### Video Test Files

```python
@pytest.fixture(scope="session")
def sample_video_files(test_files_dir) -> Dict[str, Path]:
    """Provide sample video files for testing."""
    return {
        "valid_mp4": test_files_dir / "sample.mp4",
        "valid_avi": test_files_dir / "sample.avi",
        "invalid_format": test_files_dir / "invalid.xyz",
        "empty": test_files_dir / "empty.mp4"
    }
```

### Environment Mocking

```python
@pytest.fixture
def mock_env_vars(monkeypatch) -> Dict[str, str]:
    """Setup mock environment variables."""
    env_vars = {
        "OPENAI_API_KEY": "test_key",
        "ENVIRONMENT": "testing",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars
```

## Running Tests

### All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run with detailed output
pytest -v
```

### Specific Tests

```bash
# Run unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_error_handling.py

# Run specific test function
pytest tests/unit/test_error_handling.py::test_file_validation_errors
```

### Test Categories

```bash
# Skip slow tests
pytest -m "not slow"

# Run only integration tests
pytest tests/integration/

# Run with specific marker
pytest -m "api"
```

## Coverage Requirements

### Minimum Coverage

- Overall project coverage: 85%
- Individual module coverage: 80%
- Critical paths: 90%

### Coverage Report

```bash
# Generate coverage report
pytest --cov=src --cov-report=html

# Check coverage threshold
pytest --cov=src --cov-fail-under=85
```

## Test Writing Guidelines

### 1. Test Structure

```python
def test_function_name():
    """Test description."""
    # Setup
    config = VideoConfig()
    
    # Exercise
    result = process_video(config)
    
    # Verify
    assert result["status"] == "success"
    
    # Cleanup (if needed)
    cleanup_resources()
```

### 2. Naming Conventions

- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

### 3. Assertions

```python
# Use specific assertions
assert isinstance(result, dict)
assert "error" not in result
assert len(result["scenes"]) > 0
assert result["duration"] == pytest.approx(10.5, rel=1e-2)
```

### 4. Error Testing

```python
def test_error_handling():
    with pytest.raises(VideoProcessingError) as exc_info:
        process_invalid_video()
    assert "Invalid format" in str(exc_info.value)
```

## Best Practices

1. **Test Independence**:
   - Each test should be independent
   - Clean up resources after tests
   - Don't rely on test execution order

2. **Test Data**:
   - Use fixtures for common test data
   - Create minimal test data
   - Clean up test files

3. **Performance**:
   - Mark slow tests with `@pytest.mark.slow`
   - Use appropriate scopes for fixtures
   - Clean up resources properly

4. **Mocking**:
   ```python
   @pytest.fixture
   def mock_api(mocker):
       return mocker.patch("src.api.client.APIClient")
   ```

## Common Patterns

### 1. Resource Management

```python
@pytest.fixture
def resource_fixture():
    # Setup
    resource = setup_resource()
    yield resource
    # Cleanup
    resource.cleanup()
```

### 2. Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("video.mp4", True),
    ("invalid.txt", False),
    ("", False),
])
def test_validate_filename(input, expected):
    assert validate_filename(input) == expected
```

### 3. Mock External Services

```python
def test_api_integration(mock_api):
    mock_api.return_value.process.return_value = {"status": "success"}
    result = process_with_api()
    assert result["status"] == "success"
```

## Troubleshooting

### Common Issues

1. **Resource Cleanup**:
   ```python
   @pytest.fixture(autouse=True)
   def cleanup_after_test():
       yield
       cleanup_all_resources()
   ```

2. **Test Isolation**:
   ```python
   @pytest.fixture(autouse=True)
   def isolate_db():
       with transaction.atomic():
           yield
           transaction.rollback()
   ```

3. **Performance Issues**:
   ```python
   @pytest.mark.skipif(
       os.getenv("SKIP_SLOW") == "1",
       reason="Skip slow tests"
   )
   def test_slow_operation():
       # ...
   ```

## CI Integration

### GitHub Actions

```yaml
- name: Run tests
  run: |
    pytest tests/unit/ -v --cov=src
    pytest tests/integration/ -v --cov=src --cov-append
    pytest tests/performance/ -v -m "not slow"
```

### Coverage Reports

```yaml
- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
    fail_ci_if_error: true
```

## Testing External API Integrations

### Case Study: Twelve Labs API Integration

This section documents lessons learned from fixing integration issues with the Twelve Labs video processing API.

#### Key Challenges

1. **Response Structure Mocking**
   - Mock responses must exactly match the API's structure
   - Include all required fields (`task_id`, `status`, etc.)
   - Maintain consistency across multiple API calls

```python
# Good: Complete mock response
mock_response = MagicMock(
    status_code=200,
    json=lambda: {
        "task_id": "upload_task_id",
        "status": "completed",
        "result": {"video_id": "test_video_id"}
    }
)

# Bad: Incomplete mock response
mock_response = MagicMock(
    status_code=200,
    json=lambda: {"status": "completed"}  # Missing task_id
)
```

2. **Error Propagation**
   - Properly propagate API-specific errors to application errors
   - Maintain consistent error messages
   - Handle timeouts and rate limits appropriately

```python
try:
    result = api.process_video(video_data)
except APITimeoutError:
    raise ModelError("Task timed out")
except RateLimitError as e:
    raise ModelError(f"Rate limit exceeded: {str(e)}")
except APIError as e:
    raise ModelError(f"API error: {str(e)}")
```

3. **Multi-Stage Process Testing**
   - Test each stage of the process (upload, processing, analysis)
   - Mock appropriate responses for each stage
   - Ensure proper state transitions

```python
def test_process_success(model, mock_session):
    """Test successful multi-stage video processing."""
    responses = [
        # Stage 1: Index check
        MagicMock(status_code=200, json=lambda: {
            "data": [{"name": "default_index"}]
        }),
        # Stage 2: Upload task
        MagicMock(status_code=200, json=lambda: {
            "task_id": "upload_task_id"
        }),
        # Stage 3: Upload status
        MagicMock(status_code=200, json=lambda: {
            "status": "completed",
            "result": {"video_id": "test_video_id"}
        }),
        # Stage 4: Analysis task
        MagicMock(status_code=200, json=lambda: {
            "task_id": "analysis_task_id"
        })
    ]
    mock_session.request.side_effect = responses
```

#### Best Practices

1. **Mock Response Structure**
   - Document the expected response structure
   - Use constants for common response fields
   - Validate mock responses match API documentation

2. **Error Handling**
   - Create specific exception classes for API errors
   - Map API errors to application errors consistently
   - Test all error scenarios (timeout, rate limit, etc.)

3. **Test Organization**
   - Group tests by API operation
   - Test happy path and error cases separately
   - Use descriptive test names

4. **Status Tracking**
   - Test progress callback functionality
   - Verify status transitions
   - Test timeout scenarios

#### Common Pitfalls

1. **Incomplete Mocking**
   - Missing required response fields
   - Inconsistent response structures
   - Incorrect status codes

2. **Error Handling Gaps**
   - Not testing all error scenarios
   - Inconsistent error messages
   - Missing timeout handling

3. **State Management**
   - Not cleaning up resources
   - Missing state transitions
   - Incomplete process flows

#### Testing Checklist

- [ ] Mock responses match API documentation
- [ ] All required fields are included in mocks
- [ ] Error scenarios are properly tested
- [ ] Timeouts are handled correctly
- [ ] Rate limits are respected
- [ ] Progress callbacks are tested
- [ ] Resource cleanup is implemented
- [ ] State transitions are verified
- [ ] Error messages are consistent
- [ ] Edge cases are covered 