"""
Shared pytest fixtures for video processing tests.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Generator
from uuid import UUID

import pytest

from src.core.config import VideoConfig
from src.models.video import Video


@pytest.fixture(scope="session")
def test_files_dir() -> Generator[Path, None, None]:
    """Create and manage a test files directory for the entire test session."""
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    # Cleanup after all tests
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture(scope="session")
def sample_video_files(test_files_dir) -> Generator[Dict[str, Path], None, None]:
    """
    Create a set of sample video files with different formats and sizes.
    Returns a dictionary of file paths keyed by their description.
    """
    files = {}

    # Valid MP4 file (1MB)
    mp4_path = test_files_dir / "sample.mp4"
    with open(mp4_path, "wb") as f:
        f.write(b"0" * (1024 * 1024))
    files["valid_mp4"] = mp4_path

    # Valid AVI file (2MB)
    avi_path = test_files_dir / "sample.avi"
    with open(avi_path, "wb") as f:
        f.write(b"0" * (2 * 1024 * 1024))
    files["valid_avi"] = avi_path

    # Valid MOV file (512KB)
    mov_path = test_files_dir / "sample.mov"
    with open(mov_path, "wb") as f:
        f.write(b"0" * (512 * 1024))
    files["valid_mov"] = mov_path

    # Invalid format file (1KB)
    invalid_path = test_files_dir / "invalid.xyz"
    with open(invalid_path, "wb") as f:
        f.write(b"0" * 1024)
    files["invalid_format"] = invalid_path

    # Empty file
    empty_path = test_files_dir / "empty.mp4"
    empty_path.touch()
    files["empty"] = empty_path

    yield files


@pytest.fixture(scope="session")
def large_video_file(test_files_dir) -> Generator[Path, None, None]:
    """Create a large video file that exceeds size limits."""
    file_path = test_files_dir / "large.mp4"
    max_size = VideoConfig.MAX_FILE_SIZE

    # Create sparse file to avoid actual disk usage
    file_path.touch()
    os.truncate(str(file_path), max_size + 1024)  # MAX_FILE_SIZE + 1KB

    yield file_path


@pytest.fixture
def temp_upload_dir() -> Generator[Path, None, None]:
    """Create a temporary upload directory for testing."""
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    yield temp_dir
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def video_config(temp_upload_dir) -> VideoConfig:
    """Create a VideoConfig instance with test settings."""
    config = VideoConfig()
    config.UPLOAD_DIRECTORY = temp_upload_dir
    return config


@pytest.fixture
def sample_video() -> Video:
    """Create a sample Video instance for testing."""
    return Video(
        filename="test.mp4",
        file_size=1024 * 1024,  # 1MB
        format="MP4",
        id=UUID("12345678-1234-5678-1234-567812345678"),
    )


@pytest.fixture
def mock_env_vars(monkeypatch) -> Dict[str, str]:
    """Setup mock environment variables for testing."""
    env_vars = {
        "OPENAI_API_KEY": "sk-test-openaikey123456789abcdefghijklmnopqrstuvwxyz",
        "GEMINI_API_KEY": "AI-test-geminikey123456789abcdefghijklmnopqrstuvwxyz",
        "TWELVE_LABS_API_KEY": "tlk-test-12labskey123456789abcdefghijklmnopqrstuvwxyz",
        "ENVIRONMENT": "testing",
        "DEBUG": "true",
        "UPLOAD_DIRECTORY": "test_uploads",
        "MAX_CONCURRENT_JOBS": "2",
        "CACHE_TTL": "3600",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["TWELVE_LABS_API_KEY"] = "test_key_12345678901"
    yield
    # Clean up after tests
    if "TWELVE_LABS_API_KEY" in os.environ:
        del os.environ["TWELVE_LABS_API_KEY"]
