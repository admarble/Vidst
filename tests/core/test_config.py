import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.config import ProcessingConfig, VideoConfig, load_config


def test_video_config_initialization():
    """Test VideoConfig initialization and directory creation"""
    config = VideoConfig()

    # Test directory creation
    assert config.UPLOAD_DIRECTORY.exists()
    assert config.UPLOAD_DIRECTORY.is_dir()

    # Test constants
    assert config.MAX_FILE_SIZE == 2 * 1024 * 1024 * 1024  # 2GB
    assert config.SUPPORTED_FORMATS == {"MP4", "AVI", "MOV"}
    assert config.MIN_SCENE_LENGTH == 2.0
    assert config.MAX_SCENES_PER_VIDEO == 500


def test_processing_config():
    """Test ProcessingConfig initialization and values"""
    config = ProcessingConfig()

    assert config.MAX_CONCURRENT_JOBS == 3
    assert config.MEMORY_LIMIT_PER_JOB == 4 * 1024 * 1024 * 1024  # 4GB


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Setup mock environment variables"""
    env_vars = {
        "OPENAI_API_KEY": "test_openai_key",
        "GEMINI_API_KEY": "test_gemini_key",
        "TWELVE_LABS_API_KEY": "test_twelve_labs_key",
        "ENVIRONMENT": "testing",
        "DEBUG": "true",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


def test_load_config(mock_env_vars):
    """Test configuration loading from environment variables"""
    config = load_config()

    assert config["openai_api_key"] == "test_openai_key"
    assert config["gemini_api_key"] == "test_gemini_key"
    assert config["twelve_labs_api_key"] == "test_twelve_labs_key"
    assert config["environment"] == "testing"
    assert config["debug"] is True


def test_load_config_defaults():
    """Test default values when environment variables are not set"""
    with patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "test-openai-key",
            "GEMINI_API_KEY": "test-gemini-key",
            "TWELVE_LABS_API_KEY": "test-twelve-labs-key",
        },
    ):
        config = load_config()
        assert config["environment"] == "development"
        assert config["debug"] is False
        assert config["cache_ttl"] == 86400
        assert config["openai_api_key"] == "test-openai-key"
        assert config["gemini_api_key"] == "test-gemini-key"
        assert config["twelve_labs_api_key"] == "test-twelve-labs-key"


@pytest.fixture
def temp_upload_dir():
    """Create a temporary upload directory"""
    temp_dir = Path("temp_uploads")
    yield temp_dir
    # Cleanup
    if temp_dir.exists():
        for item in temp_dir.glob("**/*"):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                item.rmdir()
        temp_dir.rmdir()


def test_custom_upload_directory(temp_upload_dir):
    """Test using a custom upload directory"""
    # Create the directory if it doesn't exist
    temp_upload_dir.mkdir(parents=True, exist_ok=True)

    config = VideoConfig()
    config.UPLOAD_DIRECTORY = temp_upload_dir

    assert config.UPLOAD_DIRECTORY == temp_upload_dir
    assert config.UPLOAD_DIRECTORY.exists()

    # Clean up
    temp_upload_dir.rmdir()
