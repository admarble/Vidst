"""Tests for video upload functionality."""

import os
from pathlib import Path
from unittest.mock import Mock, patch
from uuid import UUID

import pytest

from src.core.config import VideoConfig
from src.core.exceptions import FileValidationError
from src.models.video import Video
from src.video.upload import VideoUploader


@pytest.fixture
def video_config(tmp_path):
    config = VideoConfig(upload_directory=tmp_path / "uploads")
    # Customize the config after initialization if needed
    config.MAX_FILE_SIZE = 1024 * 1024 * 100  # 100MB
    config.SUPPORTED_FORMATS = {"MP4", "AVI", "MOV"}
    return config


@pytest.fixture
def uploader(video_config):
    return VideoUploader(config=video_config)


@pytest.fixture
def temp_video_file(tmp_path):
    video_file = tmp_path / "test.mp4"
    # Create a dummy video file
    with open(video_file, "wb") as f:
        f.write(b"dummy video content")
    return video_file


def test_uploader_initialization(video_config):
    uploader = VideoUploader(config=video_config)
    assert uploader.config == video_config


def test_validate_file_success(uploader, temp_video_file):
    assert uploader.validate_file(str(temp_video_file)) is True


def test_validate_nonexistent_file(uploader):
    with pytest.raises(FileValidationError, match="File does not exist"):
        uploader.validate_file("/nonexistent/path/video.mp4")


def test_validate_unsupported_format(uploader, tmp_path):
    unsupported_file = tmp_path / "video.xyz"
    unsupported_file.write_text("dummy content")

    with pytest.raises(FileValidationError, match="Unsupported format"):
        uploader.validate_file(str(unsupported_file))


def test_validate_empty_file(uploader, tmp_path):
    empty_file = tmp_path / "empty.mp4"
    empty_file.touch()

    with pytest.raises(FileValidationError, match="File is empty"):
        uploader.validate_file(str(empty_file))


def test_validate_oversized_file(uploader, tmp_path):
    # Create a file that's larger than MAX_FILE_SIZE
    large_file = tmp_path / "large.mp4"
    with open(large_file, "wb") as f:
        f.seek(uploader.config.MAX_FILE_SIZE + 1)
        f.write(b"\0")

    with pytest.raises(FileValidationError, match="File exceeds maximum size"):
        uploader.validate_file(str(large_file))


@patch("src.video.upload.uuid4")
def test_upload_success(mock_uuid4, uploader, temp_video_file, tmp_path):
    # Mock UUID generation
    test_uuid = "12345678-1234-5678-1234-567812345678"
    mock_uuid4.return_value = UUID(test_uuid)

    # Mock upload directory
    uploader.config.UPLOAD_DIRECTORY = tmp_path / "uploads"
    uploader.config.UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

    # Perform upload
    video = uploader.upload(str(temp_video_file))

    # Verify the file was copied to the correct location
    expected_path = uploader.config.UPLOAD_DIRECTORY / test_uuid / temp_video_file.name
    assert expected_path.exists()
    assert video.id == UUID(test_uuid)
    assert video.filename == temp_video_file.name
    assert video.format == temp_video_file.suffix[1:].upper()


def test_upload_invalid_file(uploader, tmp_path):
    invalid_file = tmp_path / "invalid.xyz"
    invalid_file.write_text("invalid content")

    with pytest.raises(FileValidationError):
        uploader.upload(str(invalid_file))


@patch("src.video.upload.shutil.copy2")
def test_upload_copy_failure(mock_copy2, uploader, temp_video_file):
    # Mock copy2 to raise an exception
    mock_copy2.side_effect = OSError("Copy failed")

    with pytest.raises(OSError, match="Copy failed"):
        uploader.upload(str(temp_video_file))


@pytest.fixture
def test_dir():
    """Create and clean up a temporary test directory."""
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    # Cleanup after tests
    if test_dir.exists():
        for file in test_dir.glob("*"):
            file.unlink()
        test_dir.rmdir()


@pytest.fixture
def valid_video_file(test_dir):
    """Create a valid test video file."""
    file_path = test_dir / "test_video.mp4"
    # Create a small valid MP4 file
    with open(file_path, "wb") as f:
        f.write(b"0" * 1024)  # 1KB of zeros
    yield file_path
    if file_path.exists():
        file_path.unlink()


@pytest.fixture
def invalid_format_file(test_dir):
    """Create a file with invalid format."""
    file_path = test_dir / "invalid.xyz"
    with open(file_path, "wb") as f:
        f.write(b"0" * 1024)
    yield file_path
    if file_path.exists():
        file_path.unlink()


def test_video_upload_validation(valid_video_file, invalid_format_file):
    """Test video file validation."""
    config = VideoConfig()
    uploader = VideoUploader(config)

    # Test valid file
    assert uploader.validate_file(str(valid_video_file)) is True

    # Test invalid format
    with pytest.raises(FileValidationError, match="Unsupported format"):
        uploader.validate_file(str(invalid_format_file))

    # Test non-existent file
    with pytest.raises(FileValidationError, match="File does not exist"):
        uploader.validate_file("nonexistent.mp4")


def test_successful_upload(valid_video_file):
    """Test successful video upload."""
    config = VideoConfig()
    uploader = VideoUploader(config)

    video = uploader.upload(str(valid_video_file))

    assert isinstance(video.id, UUID)
    assert video.filename == valid_video_file.name
    assert video.format == "MP4"
    assert video.status == "pending"

    # Verify file was copied to upload directory
    uploaded_path = config.UPLOAD_DIRECTORY / str(video.id) / video.filename
    assert uploaded_path.exists()
    assert uploaded_path.stat().st_size == valid_video_file.stat().st_size


def test_upload_creates_directory():
    """Test that upload directory is created if it doesn't exist."""
    config = VideoConfig()

    # Remove upload directory if it exists
    if config.UPLOAD_DIRECTORY.exists():
        for path in config.UPLOAD_DIRECTORY.glob("**/*"):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                try:
                    path.rmdir()
                except OSError:
                    # Directory not empty, continue with other files/dirs
                    continue

    # Ensure directory doesn't exist
    if config.UPLOAD_DIRECTORY.exists():
        config.UPLOAD_DIRECTORY.rmdir()

    assert not config.UPLOAD_DIRECTORY.exists()

    # Create a test file
    test_file = Path("test.mp4")
    test_file.touch()

    try:
        # Upload should create directory
        uploader = VideoUploader(config)
        uploader.upload(test_file)

        assert config.UPLOAD_DIRECTORY.exists()
        assert config.UPLOAD_DIRECTORY.is_dir()
    finally:
        # Clean up
        test_file.unlink()
        for path in config.UPLOAD_DIRECTORY.glob("**/*"):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                try:
                    path.rmdir()
                except OSError:
                    continue
        if config.UPLOAD_DIRECTORY.exists():
            config.UPLOAD_DIRECTORY.rmdir()


def test_successful_upload_mp4(config, sample_video_files):
    """Test successful upload of MP4 file."""
    uploader = VideoUploader(config)
    video = uploader.upload(str(sample_video_files["valid_mp4"]))

    assert isinstance(video.id, UUID)
    assert video.filename == "sample.mp4"
    assert video.format == "MP4"
    assert video.status == "pending"

    # Verify file was copied to upload directory
    uploaded_path = config.UPLOAD_DIRECTORY / str(video.id) / video.filename
    assert uploaded_path.exists()
    assert (
        uploaded_path.stat().st_size == sample_video_files["valid_mp4"].stat().st_size
    )


def test_successful_upload_avi(config, sample_video_files):
    """Test successful upload of AVI file."""
    uploader = VideoUploader(config)
    video = uploader.upload(str(sample_video_files["valid_avi"]))

    assert isinstance(video.id, UUID)
    assert video.filename == "sample.avi"
    assert video.format == "AVI"
    assert video.status == "pending"


def test_successful_upload_mov(config, sample_video_files):
    """Test successful upload of MOV file."""
    uploader = VideoUploader(config)
    video = uploader.upload(str(sample_video_files["valid_mov"]))

    assert isinstance(video.id, UUID)
    assert video.filename == "sample.mov"
    assert video.format == "MOV"
    assert video.status == "pending"


def test_duplicate_upload(config, sample_video_files):
    """Test uploading the same file twice creates two distinct entries."""
    uploader = VideoUploader(config)

    video1 = uploader.upload(str(sample_video_files["valid_mp4"]))
    video2 = uploader.upload(str(sample_video_files["valid_mp4"]))

    assert video1.id != video2.id
    assert video1.filename == video2.filename

    # Verify both files exist in different directories
    path1 = config.UPLOAD_DIRECTORY / str(video1.id) / video1.filename
    path2 = config.UPLOAD_DIRECTORY / str(video2.id) / video2.filename
    assert path1.exists()
    assert path2.exists()


def test_concurrent_uploads(config, sample_video_files):
    """Test multiple files can be uploaded concurrently."""
    uploader = VideoUploader(config)

    # Upload different formats concurrently
    videos = [
        uploader.upload(str(sample_video_files["valid_mp4"])),
        uploader.upload(str(sample_video_files["valid_avi"])),
        uploader.upload(str(sample_video_files["valid_mov"])),
    ]

    # Verify all uploads succeeded
    for video in videos:
        assert isinstance(video.id, UUID)
        uploaded_path = config.UPLOAD_DIRECTORY / str(video.id) / video.filename
        assert uploaded_path.exists()
