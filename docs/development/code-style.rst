
Code Style Guide

================











Overview


--------





--------





--------





--------





--------




This guide outlines the coding standards for the Video Understanding AI project.

Python Style Guide


------------------





------------------





------------------





------------------





------------------








General Rules


-------------
























- Follow PEP 8
- Use 4 spaces for indentation
- Maximum line length: 88 characters
- Use type hints
- Write docstrings in Google style




Naming Conventions

























- Classes: ``_UpperCamelCas```_``_```_e`_`_`_`_
- Functions: ``_lower_snake_cas```_``_```_e`_`_`_`_
- Variables: ``_lower_snake_cas```_``_```_e`_`_`_`_
- Constants: ``_UPPER_SNAKE_CAS```_``_```_E`_`_`_`_
- Private members: ``_prefix```_``_```_`_`_``_``




Type Hints

























Use type hints for all function parameters and return values:

.. code-block:: python

      def process_video(
         file_path: Path,
         config: ProcessingConfig,
         *,
         max_duration: Optional[int] = None
      ) -> ProcessingResult:
         """Process a video file.

         Args:
            file_path: Path to the video file
            config: Processing configuration
            max_duration: Optional maximum duration in seconds

         Returns:

            ProcessingResult object containing analysis results




         pass




Docstrings

























Use Google-style docstrings:

.. code-block:: python

      def validate_config(config: Dict[str, Any]) -> bool:
         """Validate configuration dictionary.

         Args:
            config: Configuration dictionary to validate

         Returns:
            True if valid, False otherwise

         Raises:

            ConfigurationError: If configuration is invalid




         pass




Code Organization

























- One class per file (with exceptions)
- Group related functionality
- Use meaningful directory structure
- Keep files focused and small




Error Handling

























- Use custom exceptions
- Catch specific exceptions
- Add context to errors
- Log appropriately




Testing

























- Write unit tests for all code
- Use pytest fixtures
- Mock external dependencies
- Aim for high coverage




Tools

























Use these tools to maintain code quality:

- black: Code formatting
- isort: Import sorting
- pylint: Linting
- mypy: Type checking
- pytest: Testing




Example

























Here's a complete example following our style guide:

.. code-block:: python

      from pathlib import Path
      from typing import Dict, Optional

      from .exceptions import ProcessingError
      from .types import ProcessingResult

      class VideoProcessor:
         """Process video files for analysis.

         Attributes:
            config: Processing configuration

            max_workers: Maximum number of worker threads






         def __init__(self, config: Dict[str, Any], max_workers: int = 4) -> None:
            """Initialize video processor.

            Args:
                  config: Processing configuration

                  max_workers: Maximum number of worker threads




            self.config = config
            self.max_workers = max_workers

         def process(
            self,
            file_path: Path,
            *,
            max_duration: Optional[int] = None
         ) -> ProcessingResult:
            """Process a video file.

            Args:
                  file_path: Path to video file
                  max_duration: Optional maximum duration in seconds

            Returns:
                  ProcessingResult with analysis data

            Raises:

                  ProcessingError: If processing fails




            try:

                  Processing logic here








"





"

            except Exception as e:
                  raise ProcessingError(f"Failed to process {file_path}: {e}") from e

Indices and Tables


------------------





------------------





------------------





------------------





------------------







\* :ref:`modindex`*
