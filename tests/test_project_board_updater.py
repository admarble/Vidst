#!/usr/bin/env python3
"""Test suite for the project board updater script."""

# Standard library imports
from collections.abc import Generator
from unittest.mock import MagicMock, patch

# Third-party imports
import pytest

# Local imports
from scripts.update_project_board import ProjectBoardUpdater


@pytest.fixture
def updater() -> ProjectBoardUpdater:
    """Create a ProjectBoardUpdater instance for testing.

    Returns:
        ProjectBoardUpdater: A fresh instance of the updater.
    """
    return ProjectBoardUpdater()


@pytest.fixture
def mock_subprocess() -> Generator[MagicMock, None, None]:
    """Mock subprocess for testing git commands.

    Returns:
        Generator[MagicMock, None, None]: A generator yielding a mock object for subprocess.run.
    """
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="test output", stderr="", returncode=0)
        yield mock_run


@pytest.fixture
def mock_gh_cli() -> Generator[MagicMock, None, None]:
    """Mock GitHub CLI commands.

    Returns:
        Generator[MagicMock, None, None]: A generator yielding a mock object for GitHub CLI commands.
    """
    with patch(
        "scripts.update_project_board.ProjectBoardUpdater.run_gh_command"
    ) as mock:
        mock.return_value = "Success"
        yield mock


def test_parse_branch_name(updater: ProjectBoardUpdater) -> None:
    """Test branch name parsing functionality.

    Args:
        updater: ProjectBoardUpdater instance.
    """
    # Test valid branch names
    assert updater.parse_branch_name("feature/video/scene-detection") == {
        "component": "video",
        "description": "scene-detection",
    }
    assert updater.parse_branch_name("fix/ai/model-crash") == {
        "component": "ai",
        "description": "model-crash",
    }

    # Test invalid branch names
    assert updater.parse_branch_name("main") == {}
    assert updater.parse_branch_name("develop") == {}


def test_determine_components(updater: ProjectBoardUpdater) -> None:
    """Test component detection from file paths.

    Args:
        updater: ProjectBoardUpdater instance.
    """
    files = [
        "src/core/video/processor.py",
        "src/ai/models/whisper.py",
        "tests/test_video.py",
    ]
    components = updater.determine_components(files)
    assert "video" in components
    assert "ai" in components
    assert "testing" in components


def test_get_issue_number(
    updater: ProjectBoardUpdater, mock_subprocess: MagicMock
) -> None:
    """Test issue number extraction from commit messages.

    Args:
        updater: ProjectBoardUpdater instance.
        mock_subprocess: Mock subprocess object.
    """
    # Mock git branch command
    mock_subprocess.side_effect = [
        MagicMock(stdout="feature/video/scene-detection\n", stderr="", returncode=0),
        MagicMock(
            stdout="feat(video): implement scene detection #75\n",
            stderr="",
            returncode=0,
        ),
    ]

    assert updater.get_issue_number() == "75"


def test_generate_progress_body(
    updater: ProjectBoardUpdater, mock_subprocess: MagicMock
) -> None:
    """Test progress body generation for issue updates.

    Args:
        updater: ProjectBoardUpdater instance.
        mock_subprocess: Mock subprocess object.
    """
    # Mock git log command
    mock_subprocess.return_value = MagicMock(
        stdout="abc123 - feat(video): implement scene detection\n",
        stderr="",
        returncode=0,
    )

    body = updater.generate_progress_body(["video", "ai"])
    assert "Component implementation status:" in body
    assert "- [x] Video component updates" in body
    assert "- [x] Ai component updates" in body
    assert "Latest update:" in body


@pytest.mark.integration
def test_full_update_flow(
    updater: ProjectBoardUpdater, mock_subprocess: MagicMock, mock_gh_cli: MagicMock
) -> None:
    """Test the complete project board update flow.

    Args:
        updater: ProjectBoardUpdater instance.
        mock_subprocess: Mock subprocess object.
        mock_gh_cli: Mock GitHub CLI object.
    """
    # Mock git commands
    mock_subprocess.side_effect = [
        # get_current_branch
        MagicMock(stdout="feature/video/scene-detection\n", stderr="", returncode=0),
        # get_issue_number (git log)
        MagicMock(
            stdout="feat(video): implement scene detection #75\n",
            stderr="",
            returncode=0,
        ),
        # get_modified_files
        MagicMock(stdout="src/core/video/processor.py\n", stderr="", returncode=0),
        # get_latest_commit_info
        MagicMock(
            stdout="abc123 - feat(video): implement scene detection\n",
            stderr="",
            returncode=0,
        ),
    ]

    # Run the updater
    updater.run()

    # Verify GitHub CLI commands were called
    assert mock_gh_cli.call_count >= 2  # One for label, one for body update


def test_error_handling(
    updater: ProjectBoardUpdater, mock_subprocess: MagicMock
) -> None:
    """Test error handling in the updater.

    Args:
        updater: ProjectBoardUpdater instance.
        mock_subprocess: Mock subprocess object.
    """
    # Mock git command failure
    mock_subprocess.side_effect = Exception("Git command failed")

    # Verify the script handles the error gracefully
    updater.run()  # Should not raise an exception


def test_component_mapping(updater: ProjectBoardUpdater) -> None:
    """Test component path mappings configuration.

    Args:
        updater: ProjectBoardUpdater instance.
    """
    for component, paths in updater.components.items():
        assert isinstance(paths, list)
        assert all(isinstance(path, str) for path in paths)
        assert all(
            path.startswith("src/") or path.startswith("tests/") for path in paths
        )
