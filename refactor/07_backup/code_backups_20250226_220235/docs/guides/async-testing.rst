Asynchronous Testing Guide
=======================

Overview
--------

Testing asynchronous code presents unique challenges, especially when dealing with
external services, API calls, or complex context managers. This guide provides best
practices for testing asynchronous components of the Video Understanding AI system.

Prerequisites
------------

- Understanding of Python's asyncio library
- Familiarity with pytest and pytest-asyncio
- Knowledge of unittest.mock, particularly AsyncMock

Key Concepts
-----------

1. **Async Context Managers**

   Asynchronous context managers implement the `__aenter__` and `__aexit__` protocol
   methods, which must be properly mocked in tests.

2. **Coroutines vs Awaitable Objects**

   A common mistake is returning a coroutine object when an awaitable object is expected.
   This leads to errors when using `await` with the mock.

3. **Async Fixtures**

   pytest-asyncio enables fixtures that can be awaited, allowing proper setup and
   teardown of async resources.

Common Issues and Solutions
--------------------------

Improper Mocking of Async Context Managers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Issue**:

When mocking libraries that use async context managers (like aiohttp.ClientSession),
tests often fail with errors like:

```
AttributeError: 'coroutine' object has no attribute '__aenter__'
```

or

```
TypeError: object MagicMock can't be used in 'await' expression
```

**Solution**:

Create properly configured AsyncMock objects that implement the async context manager protocol:

```python
from unittest.mock import AsyncMock

@pytest.fixture
def create_async_context_manager_mock(**attrs):
    """Create a properly configured AsyncMock for async context managers."""
    mock = AsyncMock(**attrs)
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    return mock
```

HTTP Client Session Mocking
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Issue**:

HTTP client sessions like aiohttp.ClientSession are commonly used with async context
managers and need special handling.

**Solution**:

Create a fixture that properly mocks the session and its response:

```python
@pytest.fixture
def mock_response() -> AsyncMock:
    """Mock response for API calls."""
    mock = AsyncMock()

    # Set basic response attributes
    mock.status = 200
    mock.text = AsyncMock(return_value='{"success": true}')
    mock.json = AsyncMock(
        return_value={
            "choices": [{"message": {"content": "Test response"}}],
            "status": "completed",
        }
    )

    # Configure async context manager correctly
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)

    return mock

@pytest.fixture
def mock_aiohttp_session(mock_response: AsyncMock) -> AsyncMock:
    """Mock aiohttp ClientSession."""
    session = AsyncMock()

    # Make sure request methods return the mock_response directly, not a coroutine
    session.post = AsyncMock(return_value=mock_response)
    session.get = AsyncMock(return_value=mock_response)
    session.request = AsyncMock(return_value=mock_response)
    session.close = AsyncMock()

    # Configure session's async context manager
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)

    return session
```

API Call Mocking
~~~~~~~~~~~~~~~

**Issue**:

Asynchronous API calls need to be mocked to avoid actual network requests during tests.

**Solution**:

Use patches with AsyncMock to replace the actual API call methods:

```python
@pytest.mark.asyncio
async def test_process(self, model, image_file):
    """Test content processing."""
    expected_result = {
        "description": "A test image",
        "objects": ["person", "laptop"],
    }

    with patch.object(model, "process", return_value=expected_result):
        result = await model.process({"image_path": str(image_file)})
        assert "description" in result
        assert "objects" in result
```

Resource Cleanup
~~~~~~~~~~~~~~~

**Issue**:

Async resources like sessions need proper cleanup, even in test environments.

**Solution**:

Use async fixtures with cleanup:

```python
@pytest.fixture
async def model(
    mock_env_vars: Dict[str, str], mock_aiohttp_session: AsyncMock
) -> AsyncGenerator[Model, None]:
    """Create a model instance with proper cleanup."""
    model = None
    try:
        model = Model(config={"api_key": mock_env_vars["API_KEY"]})
        model._session = mock_aiohttp_session
        yield model
    finally:
        if model:
            await model.close()
```

Best Practices
-------------

1. **Use AsyncMock for All Async Components**

   Always use AsyncMock from unittest.mock when mocking async functions or methods:

   ```python
   from unittest.mock import AsyncMock

   mock_function = AsyncMock(return_value={"status": "success"})
   ```

2. **Explicitly Configure Async Context Managers**

   Always set `__aenter__` and `__aexit__` methods when mocking async context managers:

   ```python
   mock.__aenter__ = AsyncMock(return_value=mock)
   mock.__aexit__ = AsyncMock(return_value=None)
   ```

3. **Return Mock Objects, Not Coroutines**

   Ensure that mock methods return mock objects directly, not coroutines:

   ```python
   # INCORRECT ❌
   session.get = AsyncMock()  # Will return a coroutine

   # CORRECT ✅
   session.get = AsyncMock(return_value=mock_response)  # Returns the mock directly
   ```

4. **Use pytest-asyncio Markers**

   Mark async tests with `@pytest.mark.asyncio` to run them properly:

   ```python
   @pytest.mark.asyncio
   async def test_async_function():
       result = await function_under_test()
       assert result == expected_value
   ```

5. **Clean Up Resources**

   Always clean up async resources, even in tests:

   ```python
   @pytest.fixture
   async def resource() -> AsyncGenerator[Resource, None]:
       res = Resource()
       try:
           yield res
       finally:
           await res.close()
   ```

6. **Test Exception Handling**

   Test how your async code handles exceptions:

   ```python
   @pytest.mark.asyncio
   async def test_error_handling():
       mock_session = AsyncMock()
       mock_session.get.side_effect = RuntimeError("Network error")

       with pytest.raises(ModelError):
           await api_client.fetch_data(session=mock_session)
   ```

Examples
--------

Testing AI Model Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~

```python
class TestModelProcessing:
    """Tests for AI model processing."""

    @pytest.fixture
    def model(
        self, mock_env_vars: Dict[str, str], mock_aiohttp_session: AsyncMock
    ) -> Model:
        """Create a model instance."""
        model = Model(api_key=mock_env_vars["API_KEY"])
        model._session = mock_aiohttp_session  # Set for testing purposes
        return model

    @pytest.mark.asyncio
    async def test_process(self, model, input_data):
        """Test data processing."""
        expected_result = {
            "description": "Test result",
            "metadata": {"duration": 10},
        }

        with patch.object(model, "process", return_value=expected_result):
            result = await model.process(input_data)
            assert "description" in result
            assert "metadata" in result
```

Testing Async Resource Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

```python
class TestResourceManagement:
    """Tests for async resource management."""

    @pytest.fixture
    async def resource_manager(self, mock_session: AsyncMock) -> AsyncGenerator[ResourceManager, None]:
        """Create a resource manager with cleanup."""
        manager = ResourceManager()
        manager._session = mock_session
        try:
            yield manager
        finally:
            await manager.close()

    @pytest.mark.asyncio
    async def test_acquire_resource(self, resource_manager, mock_session):
        """Test resource acquisition."""
        mock_session.request.return_value.__aenter__.return_value.json.return_value = {
            "resource_id": "test-123"
        }

        resource_id = await resource_manager.acquire()
        assert resource_id == "test-123"
        assert mock_session.request.called
```

Troubleshooting
--------------

1. **'coroutine' object has no attribute '__aenter__'**

   **Issue**: This occurs when using an async context manager incorrectly.

   **Solution**: Ensure `__aenter__` and `__aexit__` are properly configured on the mock.

2. **object MagicMock can't be used in 'await' expression**

   **Issue**: A regular MagicMock is being used where an AsyncMock is needed.

   **Solution**: Use AsyncMock instead of MagicMock for async components.

3. **RuntimeError: Session is closed**

   **Issue**: The mock session was closed or improperly configured.

   **Solution**: Ensure the session mock is configured to appear open.

4. **TypeError: object dict can't be used in 'await' expression**

   **Issue**: A function is returning a regular dict where an awaitable object is expected.

   **Solution**: When mocking async functions, ensure they return awaitable objects.

5. **pytest.PytestUnhandledCoroutineWarning**

   **Issue**: Test is creating coroutines without awaiting them.

   **Solution**: Ensure all coroutines are properly awaited in the test.

Related Documentation
--------------------

- :doc:`/api/testing/best_practices`
- :doc:`/issues-and-resolutions`
- :doc:`/api/core/troubleshooting`
