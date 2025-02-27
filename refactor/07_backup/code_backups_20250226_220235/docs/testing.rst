
Testing Guide









































Overview





















This guide covers testing practices for the Video Understanding AI system.






















Directory Structure





















.. code-block:: text

      tests/

      ├── unit/              Unit tests








=





=









=





=









=





=

Getting Started


---------------





---------------





---------------





---------------





---------------





---------------




























Running Tests




































.. code-block:: bash

      Run all tests








^





"


      Run specific test file








"





"


      Run tests with coverage








"





"


Test Categories


---------------





---------------





---------------





---------------





---------------





---------------

















==========



Unit Tests

==========





































Integration Tests


































End-to-End Tests


----------------
























Code Coverage

























Coverage Reports

























Coverage Thresholds

























Handling Coverage Files in Git

























Additional Resources

























\* Coverage Configuration*








Indices and Tables

























\* :ref:`modindex`*








Table of Contents






















1. :ref:`testing_rst__running_tests`
2. :ref:`testing_rst__code_coverage`
3. `CI/CD Integration`_
4. :ref:`testing_rst__best_practices`




Test Implementation

























Test Structure






















.. code-block:: text

      tests/

      ├── unit/           Unit tests








"





"









"





"









"





"

Test Categories


---------------





---------------





---------------





---------------





---------------





---------------













Unit Tests


----------





----------





----------





----------





----------




Unit tests focus on testing individual components in isolation:

.. code-block:: python

      def test_video_processor():
         processor = VideoProcessor()
         result = processor.process("test.mp4")
         assert result.status == "success"

Integration Tests


-----------------





-----------------





-----------------





-----------------





-----------------




Integration tests verify component interactions:

.. code-block:: python

      def test_end_to_end_processing():
         video = upload_video("sample.mp4")
         result = process_video(video.id)
         assert result.scenes > 0
         assert result.transcript




Configuration





































Prerequisites































.. code-block:: bash

      Install test dependencies








"





"


Test Markers


------------





------------





------------





------------





------------





------------













We use the following test markers:




\* ``@pytest.mark.performance``: Performance tests*





.. code-block:: bash

      Run tests by marker








"





"

      pytest -m "not slow"

Coverage Setup


--------------





--------------





--------------





--------------





--------------





--------------
















Configuration





































Coverage settings are configured in ``pyproject.toml``:




\* Branch coverage enabled*





      * ``**/__init__.py``
      * ``**/conftest.py``
      * ``src/core/config.py``

Report Generation































.. code-block:: bash

      Terminal report








"





"


      HTML report








"





"


      XML report (for CI)








"





"


      Generate coverage badge








"





"


Reports are generated in:




\* XML: ``coverage.xml``*





Best Practices


--------------





--------------





--------------





--------------





--------------





--------------
















File Management





































When working with coverage files, follow these guidelines:

1. **coverage.xml**:

   \* Generated during test runs and pre-commit hooks*
   \* Tracked in git but may show as modified*
   \* Use ``git commit --no-verify`` for coverage updates*

2. **coverage.svg**:

   \* Generated badge file for README*
   \* Commit when coverage changes*
   \* Updates in CI/CD*

3. **coverage_html/**:

   \* Local coverage report directory*
   \* Keep in .gitignore*
   \* Generate on demand*

CI/CD Integration


































GitHub Actions

























\* Enforces coverage thresholds*









Coverage Comments

























\* Coverage diff visualization*









Codecov Integration

























\* PR coverage checks*
