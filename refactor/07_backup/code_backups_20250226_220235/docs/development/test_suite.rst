Test Suite Implementation






This document details the implementation of our test suite, with a focus on mocking practices
and test organization.

Mock Response Handling


----------------------




We use a custom mock response helper that properly simulates ``_requests.Respons```_``_```_e`_`_ behavior:`_`_

.. code-block:: python

      def create_mock_response(status_code=200, json_data=None, headers=None):
         """Create a mock HTTP response object that simulates requests.Response behavior.

         Args:
            status_code (int): HTTP status code for the response
            json_data (dict): Data to be returned by response.json()
            headers (dict): HTTP headers to include in response

         Returns:

Mock: A mock response object with proper behavior














































         response = Mock(spec=requests.Response)
         response.status_code = status_code
         response.json = Mock(return_value=json_data or {})
         response.headers = headers or {}
         response.ok = 200 <= status_code < 300

         ... additional attributes ...





















































      Test Organization




Our tests are organized by functionality and error cases:

HTTP Status Codes





We test all relevant HTTP status codes:

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Rate Limit
- 500: Server Error
- 503: Service Unavailable

Example test for 400 Bad Request:

.. code-block:: python

      def test_make_request_bad_request(model, mock_session):
         """Test handling of 400 Bad Request API responses."""
         response = create_mock_response(
            status_code=400,

json_data={"error": "Invalid parameters"}


-----------------------------------------





-----------------------------------------





-----------------------------------------





-----------------------------------------





-----------------------------------------





-----------------------------------------





-----------------------------------------





-----------------------------------------





-----------------------------------------




         with pytest.raises(TwelveLabsError):
            model._make_request("GET", "/test")

      API Functionality




Core API functionality tests include:

- Model initialization
- Input validation
- Index management
- Task status tracking
- Video processing
- Search functionality
- Text generation

Example test for search functionality:

.. code-block:: python

      def test_search_success(model, mock_session):
         """Test successful semantic search."""
         expected_result = {
            "data": [
                  {
                     "video_id": "test_video_id",
                     "score": 0.95,
                     "text": "Person explaining code"
                  }
            ]
         }
         response = create_mock_response(
            status_code=200,
            json_data=expected_result
         )
         result = model.search("person explaining code")
         assert result == expected_result

      Resource Management




We test proper resource handling:

- Session management and reuse
- Temporary file cleanup
- Rate limit tracking
- Concurrent request handling

Example cleanup test:

.. code-block:: python

      def test_cleanup_resources(model, tmp_path):
         """Test proper cleanup of temporary resources."""
         test_file = tmp_path / "test.txt"
         test_file.write_text("test")
         model._temp_files.add(str(test_file))
         model._cleanup_resources()
         assert not test_file.exists()

      Test Fixtures




Common test fixtures include:

.. code-block:: python

      @pytest.fixture
      def model():
         """Create a model instance for testing."""
         return TwelveLabsModel("test_api_key")

      @pytest.fixture
      def test_video(tmp_path):
         """Create a test video file."""
         video_file = tmp_path / "test.mp4"
         video_file.write_bytes(b"test content")
         return video_file

      @pytest.fixture
      def mock_session(monkeypatch):
         """Create a mock session."""
         mock = Mock()
         mock.headers = {}
         monkeypatch.setattr("requests.Session", Mock(return_value=mock))
         return mock

      Progress Tracking




We test progress tracking functionality:

.. code-block:: python

      def test_progress_callback(model, test_video, mock_session):
         """Test progress callback functionality."""
         progress_updates = []
         def progress_callback(current, total):
            progress_updates.append((current, total))

         model.process({
            "video_path": str(test_video),
            "progress_callback": progress_callback
         })
         assert progress_updates[-1][0] == progress_updates[-1][1]

      Concurrent Operations




We test concurrent operation handling:

.. code-block:: python

      def test_concurrent_requests(model, mock_session):
         """Test concurrent request handling."""
         with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                  executor.submit(model._make_request, "GET", "/test")
                  f

      Best Practices





1. Mock Response Creation

   - Always use ``create_mock_response`` helper
   - Include appropriate headers
   - Simulate proper error handling

2. Test Organization

   - Group related tests together
   - Use descriptive test names
   - Include detailed docstrings

3. Resource Cleanup

   - Use pytest fixtures for setup/teardown
   - Clean up temporary files
   - Reset mocked objects

4. Error Handling

   - Test both success and error cases
   - Verify error messages
   - Check error types

5. Documentation

   - Document test scenarios
   - Include expected behavior
   - Provide example usage

Indices and Tables












\* :doc:`/modindex`*
