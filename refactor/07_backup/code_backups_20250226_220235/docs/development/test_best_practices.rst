Test Best Practices






This guide covers best practices for writing and maintaining tests in the Vidst project, with specific examples and lessons learned from real issues.

Mock Response Management






When working with mocked API responses, follow these guidelines to ensure reliable tests:

1. **Match Expected Call C**o***u***n******t*****

   - Calculate exact number of API calls expected
   - Account for retries and error cases
   - Document the sequence of calls

   .. code-block:: python

      Example: Mocking API calls with retries





















































      mock_request.side_effect = [

            {"data": [{"name": "default_index"}]},  Index check

























































            {"task_id": "upload_task"},             Upload task creation





















































            First chunk upload (4 failures + 1 success)





















































            RateLimitError("Rate limit exceeded"),
            RateLimitError("Rate limit exceeded"),
            RateLimitError("Rate limit exceeded"),
            RateLimitError("Rate limit exceeded"),


{},  Success










=





=





=





=





=





=





=





=





=











      2. **Document Mock Respons**e**s**


   - Add clear comments for each response
   - Explain retry patterns
   - Note expected outcomes

Test Data Control


-----------------




Proper test data management is crucial for reliable tests:

1. **File Size Con**t***r***o******l*****

   - Use precise file sizes in tests
   - Control chunk sizes explicitly
   - Document size relationships

   .. code-block:: python

      Example: Creating test file with known chunk sizes





















































      with open(test_video_file, "wb") as f:

            f.write(b"chunk1" * 1024)  First bloc*k*

























































            f.write(b"chunk2" * 1024)  Second bloc*k*





















































            f.write(b"chunk3" * 1024)  Third bloc*k*





















































      Set chunk size to match block size





















































      model.CHUNK_SIZE = len(b"chunk1" * 1024*)*

      2. **Test Data Documentati**o**n**


   - Document test data structure
   - Explain size calculations
   - Note dependencies

Rate Limit Testing


------------------




When testing rate-limited APIs:

1. **Retry Simula**t***i***o******n*****

   - Test both success and failure cases
   - Verify retry count limits
   - Check backoff behavior

   .. code-block:: python

      def test_rate_limit_retry(self):
            """Test rate limit retry mechanism with backoff."""

            Mock responses to simulate rate limits





















































            mock_responses = [

               RateLimitError("Rate limit exceeded"),  First attempt

























































               RateLimitError("Rate limit exceeded"),  First retry






















































{},  Success on third try






































































=





=

-
-

-
-





^






      2. **Error Recove**r**y**


   - Verify proper error handling
   - Test recovery mechanisms
   - Check state after retries

Common Issues and Solutions


---------------------------




Real examples of test issues and their solutions:

1. **StopIteration in Mock Respo**n***s***e******s*****

   **I**s***s***u******e**: Mock responses exhausted before all API calls compl**e***t***e******

   **Solu**t***i***o******n*****:******

   - Calculate exact number of calls needed
   - Account for retries in mock responses
   - Control chunk sizes explicitly

   .. code-block:: python

      Before: Incorrect chunk size leading to extra calls

























































      model.CHUNK_SIZE = 6144  Arbitrary size









































"






      After: Precise chunk size matching test data

























































      model.CHUNK_SIZE = len(b"chunk1" * 1024)  Exact block siz*e*









































"






      2. **Flaky Tests Due to File Siz**e**s**


   **I**s***s***u******e**: Inconsistent file chunking causing variable API ca**l***l***s******

   **Solu**t***i***o******n*****:******

   - Use exact file sizes
   - Control chunk sizes
   - Document size relationships

Best Practices Checklist





When writing tests:

1. **Mock Response Manage**m***e***n******t*****

   - [ ] Calculate exact API call count
   - [ ] Document mock response sequence
   - [ ] Account for all retry scenarios
   - [ ] Add clear comments for each response

2. **Test Data Con**t***r***o******l*****

   - [ ] Use precise file sizes
   - [ ] Control chunk sizes explicitly
   - [ ] Document data structure
   - [ ] Note size relationships

3. **Rate Limit Tes**t***i***n******g*****

   - [ ] Test retry mechanisms
   - [ ] Verify error handling
   - [ ] Check recovery behavior
   - [ ] Test backoff logic

4. **Documenta**t***i***o******n*****

   - [ ] Document test purpose
   - [ ] Explain mock responses
   - [ ] Note size calculations
   - [ ] Add example usage

Unit Test Organization





When organizing unit tests:

1. **Test Class Struc**t***u***r******e*****

   - Group related test methods in classes
   - Use descriptive test class names
   - Follow a consistent naming pattern

   .. code-block:: python

      class TestVideoProcessor:
            """Test cases for VideoProcessor class."""

            def setup_method(self):
               """Set up test fixtures."""
               self.processor = VideoProcessor()
               self.test_file = "tests/fixtures/sample_video.mp4"

            def test_valid_video_processing(self):
               """Test successful video processing."""
               result = self.processor.process({"file_path": self.test_file})
               assert result["status"] == "success"

            def test_invalid_video_format(self):
               """Test handling of invalid video format."""
               with pytest.raises(VideoFormatError):
                  self.processor.process({"file_path": "invalid.txt"})

      2. **Test Method Nami**n**g**


   - Use descriptive method names
   - Include success and failure cases
   - Follow pattern: test_[condition]_[expected_result]

   .. code-block:: python

      def test_large_file_upload_succeeds(self):
            """Test successful upload of large file."""

      def test_invalid_api_key_raises_auth_error(self):
            """Test authentication error handling."""

      3. **Test Data Organizati**o**n**


   - Use fixtures for common test data
   - Organize test data by component
   - Document data dependencies

Integration Testing





For integration tests:

1. **Test Environment S**e***t***u******p*****

   - Use separate test environment
   - Mock external services
   - Document environment requirements

   .. code-block:: python

      @pytest.fixture
      def test_environment():
            """Set up test environment with mocked services."""
            with mock.patch("src.ai.models.GPT4VisionAPI") as mock_gpt4v:
               with mock.patch("src.ai.models.TwelveLabsAPI") as mock_twelve_labs:
                  yield {
                        "gpt4v": mock_gpt4v,
                        "twelve_labs": mock_twelve_labs
                  }

      2. **Component Integrati**o**n**


   - Test component interactions
   - Verify data flow
   - Check error propagation

   .. code-block:: python

      def test_video_processing_pipeline(self, test_environment):
            """Test full video processing pipeline."""
            processor = VideoPipeline()
            result = processor.process_video(
               video_path="test.mp4",
               options={"scene_detection": True}
            )
            assert result["scenes"] is not None
            assert result["transcription"] is not None

      3. **Integration Test Cas**e**s**


   - Test end-to-end workflows
   - Verify system boundaries
   - Check performance metrics

Performance Testing




When writing performance tests:

1. **Benchmar**k***i***n******g*****

   - Measure processing time
   - Track memory usage
   - Monitor resource utilization

   .. code-block:: python

      def test_video_processing_performance():
            """Test video processing performance."""
            start_time = time.time()
            result = processor.process_video("test.mp4")
            processing_time = time.time() - start_time

            assert processing_time < MAX_PROCESSING_TIME
            assert result["memory_usage"] < MAX_MEMORY_USAGE

      2. **Load Testi**n**g**


   - Test concurrent processing
   - Verify resource limits
   - Check system stability

   .. code-block:: python

      @pytest.mark.performance
      def test_concurrent_video_processing():
            """Test concurrent video processing."""
            videos = ["test1.mp4", "test2.mp4", "test3.mp4"]
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
               futures = [executor.submit(process_video, v) for v in videos]
               results = [f.result() for f in futures]

            assert all(r["status"] == "success" for r in results)

      3. **Resource Monitori**n**g**


   - Track API usage
   - Monitor cache efficiency
   - Measure throughput

Test Coverage Requirements




Maintain high test coverage:

1. **Coverage Tar**g***e***t******s*****

   - Minimum 90% overall coverage
   - 100% coverage for critical paths
   - Document uncovered sections

2. **Coverage Rep**o***r***t******s*****

   - Generate coverage reports
   - Track coverage trends
   - Address coverage gaps

   .. code-block:: bash

      Generate coverage report





















































      pytest --cov=src tests/ --cov-report=html

      3. **Critical Pat**h**s**


   - Identify critical functionality
   - Ensure comprehensive testing
   - Document test scenarios

Indices and Tables









* :doc:`/modind`_e`_x`*_*_**
