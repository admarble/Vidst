"""Test helper utilities for the test suite."""

import json
from pathlib import Path
from typing import Any


def get_test_video_path(name: str) -> Path:
    """Get the path to a test video file."""
    return Path("tests/fixtures/video_samples/valid") / name


def get_test_audio_path(name: str) -> Path:
    """Get the path to a test audio file."""
    return Path("tests/fixtures/audio_samples/clean") / name


def get_mock_response(model: str, name: str) -> dict[str, Any]:
    """Get a mock response for a given model."""
    mock_file = Path("tests/fixtures/mock_responses") / model / f"{name}.json"
    if not mock_file.exists():
        raise FileNotFoundError(f"Mock response file not found: {mock_file}")
    return json.loads(mock_file.read_text())


def setup_test_environment() -> None:
    """Set up the test environment with required directories."""
    dirs = [
        "tests/fixtures/video_samples/valid",
        "tests/fixtures/video_samples/invalid",
        "tests/fixtures/audio_samples/clean",
        "tests/fixtures/audio_samples/noisy",
        "tests/fixtures/mock_responses/gpt4v",
        "tests/fixtures/mock_responses/whisper",
        "tests/fixtures/mock_responses/twelvelabs",
    ]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)


def cleanup_test_files() -> None:
    """Clean up temporary test files."""
    # Add cleanup logic here
    pass
