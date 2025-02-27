"""Tests for TwelveLabsModel cleanup behavior.

This module contains tests that verify the cleanup behavior of the TwelveLabsModel
under various conditions:
- Normal cleanup via explicit close() call
- Cleanup with active tasks
- Cleanup in a running event loop
- Cleanup without a running event loop
- Cleanup during interpreter shutdown

The tests ensure that resources are properly cleaned up in all scenarios
and that the cleanup process handles errors gracefully without raising
exceptions or warnings.

Example:
    >>> # Test explicit cleanup
    >>> model = TwelveLabsModel(api_key="test_key")
    >>> await model.close()  # Should clean up resources
    >>>
    >>> # Test cleanup with active tasks
    >>> model._active_tasks.add("task1")
    >>> await model.close()  # Should clean up tasks

Note:
    These tests use mocking to simulate various conditions and verify
    the cleanup behavior without actually interacting with external
    resources or the Twelve Labs API.
"""

import asyncio
from unittest.mock import Mock, patch

import pytest

from video_understanding.ai.models.twelve_labs.client import TwelveLabsClient
from video_understanding.ai.models.twelve_labs.model import TwelveLabsModel


@pytest.fixture
def mock_client():
    """Create a mock TwelveLabsClient.

    This fixture creates a mock client that simulates the behavior of
    TwelveLabsClient without making actual API calls. It provides a
    mock close() method that can be used to verify cleanup behavior.

    Returns:
        Mock: A mock TwelveLabsClient instance with a coroutine close() method

    Example:
        >>> client = mock_client()
        >>> await client.close()  # Simulates cleanup
        >>> client.close.assert_called_once()
    """
    client = Mock(spec=TwelveLabsClient)

    # Create a coroutine instead of a Future
    async def mock_close():
        pass

    client.close = Mock(wraps=mock_close)
    return client


@pytest.fixture
def model(mock_client):
    """Create a TwelveLabsModel instance with mock client.

    This fixture creates a TwelveLabsModel instance that uses a mock client
    for testing. The model is created fresh for each test to ensure
    isolation.

    Args:
        mock_client: The mock client fixture

    Returns:
        TwelveLabsModel: A model instance with mock client

    Example:
        >>> test_model = model(mock_client)
        >>> await test_model.close()
    """
    with patch(
        "src.ai.models.twelve_labs.model.TwelveLabsClient", return_value=mock_client
    ):
        model = TwelveLabsModel(api_key="test_key")
        yield model


@pytest.mark.asyncio
async def test_explicit_cleanup(model, mock_client):
    """Test explicit cleanup via close() method.

    Verifies that calling close() explicitly properly cleans up resources:
    - Calls client.close()
    - Clears active tasks
    - Doesn't raise exceptions

    Args:
        model: The model fixture
        mock_client: The mock client fixture

    Example:
        >>> await model.close()
        >>> mock_client.close.assert_called_once()
        >>> assert len(model._active_tasks) == 0
    """
    await model.close()
    mock_client.close.assert_called_once()
    assert len(model._active_tasks) == 0


@pytest.mark.asyncio
async def test_cleanup_with_active_tasks(model, mock_client):
    """Test cleanup with active tasks.

    Verifies that cleanup properly handles active tasks:
    - Cleans up client resources
    - Clears all active tasks
    - Handles multiple tasks correctly

    Args:
        model: The model fixture
        mock_client: The mock client fixture

    Example:
        >>> model._active_tasks.add("task1")
        >>> model._active_tasks.add("task2")
        >>> await model.close()
        >>> assert len(model._active_tasks) == 0
    """
    # Simulate some active tasks
    model._active_tasks.add("task1")
    model._active_tasks.add("task2")

    await model.close()
    mock_client.close.assert_called_once()
    assert len(model._active_tasks) == 0


@pytest.mark.asyncio
async def test_cleanup_in_running_loop(model, mock_client):
    """Test cleanup in a running event loop.

    Verifies that cleanup works correctly in a running event loop:
    - Creates cleanup task
    - Executes cleanup asynchronously
    - Completes cleanup successfully

    Args:
        model: The model fixture
        mock_client: The mock client fixture

    Example:
        >>> model.__del__()
        >>> await asyncio.sleep(0)  # Allow cleanup to run
        >>> mock_client.close.assert_called_once()
    """
    model.__del__()
    # Allow event loop to process the cleanup task
    await asyncio.sleep(0)
    mock_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_cleanup_without_running_loop(model, mock_client):
    """Test cleanup when event loop is not running.

    Verifies that cleanup handles missing event loop gracefully:
    - Attempts cleanup without event loop
    - Skips cleanup operations safely
    - Doesn't raise exceptions

    Args:
        model: The model fixture
        mock_client: The mock client fixture

    Example:
        >>> with patch('asyncio.get_event_loop',
        ...           side_effect=RuntimeError("No loop")):
        ...     model.__del__()
        >>> mock_client.close.assert_not_called()
    """
    # Simulate no running loop
    with patch("asyncio.get_event_loop", side_effect=RuntimeError("No running loop")):
        model.__del__()
    # Cleanup should still be attempted
    mock_client.close.assert_not_called()


@pytest.mark.asyncio
async def test_cleanup_during_shutdown(model, mock_client):
    """Test cleanup behavior during interpreter shutdown simulation.

    Verifies that cleanup handles interpreter shutdown gracefully:
    - Attempts cleanup during shutdown
    - Skips cleanup operations safely
    - Doesn't raise exceptions

    Args:
        model: The model fixture
        mock_client: The mock client fixture

    Example:
        >>> with patch('asyncio.get_event_loop',
        ...           side_effect=RuntimeError("Loop closed")):
        ...     model.__del__()
        >>> mock_client.close.assert_not_called()
    """
    with patch(
        "asyncio.get_event_loop", side_effect=RuntimeError("Event loop is closed")
    ):
        # Should not raise any exceptions
        model.__del__()
    # Cleanup should be skipped gracefully
    mock_client.close.assert_not_called()
