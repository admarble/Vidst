Common Issues and Resolutions
=============================

Overview
--------

This guide provides solutions for common issues encountered in the Video Understanding AI system.

Prerequisites
-------------

Before troubleshooting:

- Review system requirements
- Check configuration files
- Verify API credentials
- Ensure test environment is properly configured

Common Issues
-------------

Exception Handling Issues
~~~~~~~~~~~~~~~~~~~~~

1. **Exception Hierarchy**

   - Issue: Incorrect exception inheritance
   - Impact: Broken error handling, failed isinstance checks
   - Resolution: Follow proper inheritance chain:
      ```python
      # Correct way to define exceptions
      from ...core.exceptions import ModelError

      class CustomError(ModelError):
         """Custom exception for specific errors."""
         def __init__(self, message: str, cause: Exception | None = None):
               super().__init__(message, cause)
      ```

2. **Error Cause Handling**

   - Issue: Missing or incorrect error cause propagation
   - Impact: Lost error context, difficult debugging
   - Resolution: Properly handle error causes:
      ```python
      try:
         # Some operation
         process_video(file_path)
      except ValueError as e:
         raise ValidationError("Invalid video format", cause=e)
      ```

3. **Exception Import Issues**

   - Issue: Circular imports or wrong import paths
   - Impact: Import errors, undefined symbols
   - Resolution: Use correct relative imports:
      ```python
      # INCORRECT ❌
      from src.core.exceptions import ModelError
      from .base import ModelError  # Duplicate definition

      # CORRECT ✅
      from ...core.exceptions import ModelError  # Use relative import
      ```

4. **Custom Exception Implementation**

   - Issue: Improper exception class implementation
   - Impact: Missing error details, broken error chains
   - Resolution: Implement all required methods:
      ```python
      class CustomError(ModelError):
         def __init__(self, message: str, cause: Exception | None = None,
                     details: dict | None = None):
               super().__init__(message, cause)
               self.details = details or {}

         def __str__(self) -> str:
               return f"{self.message} - {self.details}"
      ```

Video Upload Issues
~~~~~~~~~~~~~~~~~

1. **File Validation**

   - Issue: Invalid file formats or sizes
   - Impact: Upload failures and validation errors
   - Resolution: Ensure files meet these requirements:
      ```python
      # Configuration example
      config = VideoConfig(
         upload_directory=Path("/path/to/uploads"),
         supported_formats=["MP4", "AVI", "MOV"],
         max_file_size=1024 * 1024 * 1024  # 1GB
      )
      ```

2. **Permission Errors**

   - Issue: Insufficient permissions for file operations
   - Impact: Failed uploads and directory creation
   - Common scenarios:
      - Read permission denied on source file
      - Write permission denied on upload directory
      - Directory creation permission denied
   - Resolution:
      ```python
      try:
         # Check file readability
         if not os.access(file_path, os.R_OK):
               raise FileValidationError("Permission denied")

         # Check directory write permission
         if not os.access(upload_dir, os.W_OK):
               raise FileValidationError("Permission denied")
      except OSError as e:
         # Handle specific error cases
         if "Permission denied" in str(e):
               raise FileValidationError("Permission denied")
      ```

3. **Storage Issues**

   - Issue: Insufficient disk space
   - Impact: Failed file copies
   - Resolution: Implement proper error handling:
      ```python
      try:
         shutil.copy2(source_path, dest_path)
      except OSError as e:
         if "No space left on device" in str(e):
               raise FileValidationError("No space left on device")
      ```

4. **Concurrent Upload Handling**

   - Issue: Race conditions during concurrent uploads
   - Impact: Directory conflicts, incomplete uploads
   - Resolution:
      - Use unique IDs for upload directories
      - Implement atomic operations
      - Example:
         ```python
         video_id = uuid4()
         upload_dir = base_dir / str(video_id)
         upload_dir.mkdir(parents=True, exist_ok=True)
         ```

Video Processing Issues
~~~~~~~~~~~~~~~~~~~~~

1. **Format Compatibility**

   - Supported formats: MP4, AVI, MOV
   - Maximum file size: 2GB
   - Minimum resolution: 480p
   - Resolution: Validate before processing:
      ```python
      if path.suffix.upper().lstrip(".") not in supported_formats:
         raise FileValidationError("Unsupported format")
      ```

2. **Processing Failures**

   - Memory allocation errors
   - Timeout issues
   - GPU acceleration problems
   - Resolution: Monitor resource usage and adjust batch sizes

API Integration Issues
~~~~~~~~~~~~~~~~~~~~~

1. **Authentication**

   - Invalid API keys
   - Expired tokens
   - Rate limiting
   - Resolution: Implement proper token refresh and rate limit handling

2. **Response Handling**

   - Timeout errors
   - Invalid response formats
   - Missing fields
   - Resolution: Add robust error handling and field validation

Testing Issues
~~~~~~~~~~~~~

1. **Test Environment Setup**

   - Issue: Inconsistent test environments
   - Impact: Flaky tests and false failures
   - Resolution: Use fixtures for consistent setup:
      ```python
      @pytest.fixture
      def temp_upload_dir() -> Generator[Path, None, None]:
         """Create a temporary directory for uploads."""
         with tempfile.TemporaryDirectory() as temp_dir:
               yield Path(temp_dir)
      ```

2. **Permission Testing**

   - Issue: Platform-specific permission behavior
   - Impact: Inconsistent test results
   - Resolution: Use platform checks and appropriate permissions:
      ```python
      if os.name != "nt":  # Skip on Windows
         os.chmod(directory, 0o444)  # Read-only
         try:
               # Test permission-denied scenario
               pass
         finally:
               os.chmod(directory, 0o777)  # Restore permissions
      ```

3. **Resource Cleanup**

   - Issue: Leftover test files and directories
   - Impact: Disk space issues, test interference
   - Resolution: Use cleanup fixtures and context managers:
      ```python
      @pytest.fixture
      def test_video_file() -> Generator[Path, None, None]:
         with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
               yield Path(temp_file.name)
               os.unlink(temp_file.name)  # Cleanup
      ```

4. **Async Context Manager Issues**

   - Issue: Improperly mocked async context managers in tests
   - Impact: Test failures when using async with statements, coroutine objects being returned instead of awaitable mock objects
   - Common failures:
      - `AttributeError: 'coroutine' object has no attribute '__aenter__'`
      - `TypeError: object MagicMock can't be used in 'await' expression`
      - `RuntimeError: Session closed`
   - Resolution: Properly configure AsyncMock objects with __aenter__ and __aexit__ methods:
      ```python
      @pytest.fixture
      def create_async_context_manager_mock(**attrs):
         """Create a properly configured AsyncMock for async context managers."""
         mock = AsyncMock(**attrs)
         mock.__aenter__ = AsyncMock(return_value=mock)
         mock.__aexit__ = AsyncMock(return_value=None)
         return mock
      ```
   - For HTTP client session mocks:
      ```python
      @pytest.fixture
      def mock_aiohttp_session(mock_response: AsyncMock) -> AsyncMock:
         """Mock aiohttp ClientSession."""
         session = AsyncMock()

         # Make request methods return mock_response directly, not a coroutine
         session.post = AsyncMock(return_value=mock_response)
         session.get = AsyncMock(return_value=mock_response)
         session.request = AsyncMock(return_value=mock_response)

         # Configure session's async context manager
         session.__aenter__ = AsyncMock(return_value=session)
         session.__aexit__ = AsyncMock(return_value=None)

         return session
      ```
   - For mocking API calls in tests:
      ```python
      @pytest.mark.asyncio
      async def test_process(self, model, image_file):
         """Test content processing."""
         expected_result = {"description": "A test image processed by model"}

         with patch.object(model, "process", return_value=expected_result):
               result = await model.process({"image_path": str(image_file)})
               assert "description" in result
      ```

Best Practices
--------------

1. Exception Handling
   - Always inherit from appropriate base exceptions
   - Properly propagate error causes
   - Include descriptive error messages
   - Add relevant error details
   - Example:
      ```python
      try:
         result = process_video(file_path)
      except Exception as e:
         if isinstance(e, VideoUnderstandingError):
               raise  # Re-raise our custom exceptions
         raise handle_error(e)  # Convert standard exceptions
      ```

2. Exception Testing
   - Test exception inheritance
   - Verify error message content
   - Check error cause propagation
   - Test error details
   - Example:
      ```python
      def test_error_with_cause():
         cause = ValueError("Original error")
         error = CustomError("Custom error", cause=cause)
         assert isinstance(error, ModelError)
         assert error.__cause__ == cause
         assert str(error) == "Custom error"
      ```

3. Error Documentation
   - Document all custom exceptions
   - Include example usage
   - List possible error conditions
   - Provide resolution steps
   - Example:
      ```python
      class ValidationError(ModelError):
         """Exception raised when input validation fails.

         Example:
               try:
                  validate_input(data)
               except ValueError as e:

                  raise ValidationError("Invalid input data", cause=e)

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
         pass
      ```

4. File Validation
   - Validate files before processing
   - Check permissions early
   - Handle all error cases explicitly
   - Use appropriate error messages

5. Error Handling
   - Use custom exceptions for different error types
   - Include descriptive error messages
   - Implement proper error propagation
   - Add logging for debugging

6. Testing
   - Write comprehensive unit tests
   - Use appropriate fixtures
   - Test error scenarios
   - Clean up test resources
   - Maintain test coverage above 85%
   - Properly mock async context managers in asyncio tests

7. Resource Management
   - Implement proper cleanup
   - Handle concurrent operations
   - Monitor disk space
   - Check permissions before operations

Additional Resources
--------------------

- :doc:`/api/core/troubleshooting`
- :doc:`/api/testing/best_practices`
- :doc:`/api/error_handling`

Indices and Tables
------------------

* :ref:`modindex`
* :ref:`search`

Linting and Code Quality Issues
~~~~~~~~~~~~~~~~~~

1. **Line Length Violations**

   - Issue: Lines exceeding 88 characters
   - Impact: Reduced code readability and maintainability
   - Resolution: Used tools to reformat long lines:
      ```python
      # Tools used
      ruff check --select E501  # Check for line length violations
      black .  # Auto-format code
      ```
   - Fixed files:
      - `src/video_understanding/core/upload.py`: Reformatted docstrings
      - `src/video_understanding/video/upload.py`: Split long docstrings
      - `src/video_understanding/storage/metadata.py`: Reformatted docstrings
      - `src/video_understanding/storage/cache.py`: Split error messages

2. **Import Resolution**

   - Issue: Unknown import symbols and incorrect imports
   - Impact: Code fails to compile or run
   - Resolution: Fixed import paths and added missing imports:
      ```python
      # Before
      from src.core.exceptions import StorageError

      # After
      from ...core.exceptions import StorageError
      ```
   - Fixed in multiple files to use relative imports

3. **Type Checking**

   - Issue: Missing or incorrect type annotations
   - Impact: Type checker errors and potential runtime issues
   - Resolution: Added proper type hints and fixed attribute access:
      ```python
      # Before
      def process(self, video: Video) -> dict:

      # After
      def process(self, video: Video) -> dict[str, Any]:
      ```
   - Implemented in processing and storage modules

4. **Protocol Implementation**

   - Issue: Incorrect protocol class usage
   - Impact: Interface implementation errors
   - Resolution: Fixed protocol implementations:
      ```python
      # Before
      class VideoUploader(Protocol):
         def upload(self) -> None:
               ...

      # After
      class VideoUploader(Protocol):
         def upload(self, file_path: str) -> Video:
               ...
      ```
