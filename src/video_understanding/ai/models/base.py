"""Base model interface for AI models.

This module defines the base interface that all AI models must implement.
It ensures consistent behavior and type safety across different model
implementations.
"""

import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar

from ..exceptions import ModelError

T = TypeVar("T")


class BaseModel(ABC):
    """Base class for all AI models.

    This abstract base class defines the interface that all models
    must implement. It ensures that models provide:
    - Input validation
    - Asynchronous processing
    - Resource cleanup
    - Error handling
    """

    @abstractmethod
    def validate(self, input_data: dict[str, Any]) -> bool:
        """Validate input data before processing.

        Args:
            input_data: Dictionary containing model inputs

        Returns:
            bool: True if input is valid

        Raises:
            ValidationError: If validation fails
        """
        pass

    @abstractmethod
    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process input data through the model.

        This method must be implemented as a coroutine to support
        asynchronous processing.

        Args:
            input_data: Dictionary containing model inputs

        Returns:
            Dictionary containing model outputs

        Raises:
            ProcessingError: If processing fails
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Clean up model resources.

        This method must be implemented as a coroutine to support
        asynchronous cleanup.

        This method should:
        - Release system resources
        - Close network connections
        - Clear caches
        - Reset internal state
        """
        pass

    def _process_impl(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Implementation of process method.

        This method should be overridden by subclasses to implement
        model-specific processing logic.

        Args:
            input_data: Dictionary containing validated input data

        Returns:
            Dictionary containing processed results

        Raises:
            ModelError: If processing fails
        """
        return {}

    def validate_input(self, input_data: Any) -> None:
        """Validate any input data before processing.

        This method performs basic input validation and then calls
        the model-specific validate() method for detailed checks.

        Args:
            input_data: Data to validate

        Raises:
            ValueError: If input is None, empty, or invalid
            TypeError: If input is not of the expected type
        """
        if input_data is None:
            raise ValueError("Input cannot be None or empty")
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a dictionary")
        if not input_data:
            raise ValueError("Input dictionary cannot be empty")
        if not self.validate(input_data):
            raise ValueError("Input validation failed for model-specific requirements")

    def retry_with_backoff(
        self, func: Callable[[], T], max_retries: int = 3, initial_delay: float = 1.0
    ) -> T:
        """Execute a function with exponential backoff retry.

        Args:
            func: Function to execute
            max_retries: Maximum number of retries
            initial_delay: Initial delay between retries in seconds

        Returns:
            Result of the function

        Raises:
            ModelError: If all retries fail
        """
        delay = initial_delay
        last_exception = None

        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2

        raise ModelError(f"Failed after {max_retries} attempts: {last_exception!s}")

    def process_with_cleanup(self, func: Callable[[], T]) -> T:
        """Execute a function with proper resource cleanup.

        Args:
            func: Function to execute

        Returns:
            Result of the function
        """
        try:
            return func()
        finally:
            self._cleanup_resources()

    def _cleanup_resources(self) -> None:
        """Clean up any resources used by the model."""
        pass  # Override in subclasses if needed
