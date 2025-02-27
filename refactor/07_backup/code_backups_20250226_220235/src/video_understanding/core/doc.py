"""Documentation generation module.

This module provides classes and utilities for documentation generation.
"""

from datetime import datetime
from typing import Any


class TestProcessor:
    """A test processor class demonstrating documentation features.

    This class shows how to document a class with various features including
    attributes, methods, and type hints.

    Attributes:
        name: The name of the processor
        created_at: Timestamp when the processor was created
        config: Configuration dictionary for the processor
    """

    def __init__(self, name: str, config: dict[str, Any] | None = None) -> None:
        """Initialize the TestProcessor.

        Args:
            name: The name to assign to the processor
            config: Optional configuration dictionary
        """
        self.name = name
        self.created_at = datetime.now()
        self.config = config or {}

    def process_data(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        """Process the input data and return results.

        This method demonstrates documenting a method with complex types
        and multiple paragraphs in the description.

        Args:
            data: List of dictionaries containing the data to process

        Returns:
            A dictionary containing the processed results

        Raises:
            ValueError: If the input data is empty
        """
        if not data:
            raise ValueError("Input data cannot be empty")

        return {
            "processor": self.name,
            "timestamp": self.created_at,
            "processed_items": len(data),
            "config_used": self.config,
        }

    @property
    def status(self) -> str:
        """Get the current status of the processor.

        Returns:
            A string indicating the processor's status
        """
        return f"Processor {self.name} initialized at {self.created_at}"


def helper_function(param1: str, param2: int = 42) -> bool:
    """A helper function demonstrating function documentation.

    This function shows how to document a function with parameters,
    return values, and type hints.

    Example:
        >>> result = helper_function("test", 123)
        >>> print(result)
        True

    Args:
        param1: First parameter description
        param2: Second parameter description, defaults to 42

    Returns:
        True if successful, False otherwise
    """
    return bool(param1 and param2)
