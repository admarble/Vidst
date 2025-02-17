"""Base class for AI models."""

import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, TypeVar

from src.core.exceptions import ModelError

T = TypeVar("T")


class BaseModel(ABC):
    """Base class for all AI models in the system."""

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results.

        Args:
            input_data: Dictionary containing input data

        Returns:
            Dictionary containing processed results
        """
        pass

    @abstractmethod
    def validate(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data.

        Args:
            input_data: Dictionary containing input data to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    def validate_input(self, input_data: Any) -> None:
        """Validate any input data.

        Args:
            input_data: Data to validate

        Raises:
            ValueError: If input is invalid
        """
        if input_data is None or (isinstance(input_data, str) and not input_data):
            raise ValueError("Input cannot be None or empty")

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

        raise ModelError(f"Failed after {max_retries} attempts: {str(last_exception)}")

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
