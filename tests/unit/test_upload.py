"""Unit tests for video upload functionality."""

import os
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest
from pytest import MonkeyPatch

from video_understanding.core.config import VideoConfig
from video_understanding.core.exceptions import FileValidationError
from video_understanding.models.video import Video
from video_understanding.video.upload import VideoUploader


@pytest.fixture
def temp_upload_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for uploads."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def config(temp_upload_dir: Path) -> VideoConfig:
    """Create a test configuration."""
    return VideoConfig(
        upload_directory=temp_upload_dir,
        supported_formats=["MP4", "AVI", "MOV"],
        max_file_size=1024 * 1024 * 1024,  # 1GB
    )


@pytest.fixture
def uploader(config: VideoConfig) -> VideoUploader:
    """Create a VideoUploader instance."""
    return VideoUploader(config)


@pytest.fixture
def test_video_file() -> Generator[Path, None, None]:
    """Create a temporary test video file."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        temp_file.write(b"dummy video content")
        temp_file.flush()
        yield Path(temp_file.name)
        os.unlink(temp_file.name)


def test_validate_file_success(uploader: VideoUploader, test_video_file: Path) -> None:
    """Test successful file validation."""
    assert uploader.validate_file(str(test_video_file)) is True


def test_validate_file_not_exists(uploader: VideoUploader) -> None:
    """Test validation of non-existent file."""
    with pytest.raises(FileValidationError, match="File does not exist"):
        uploader.validate_file("nonexistent.mp4")


def test_validate_file_unsupported_format(
    uploader: VideoUploader, test_video_file: Path
) -> None:
    """Test validation of unsupported format."""
    unsupported = test_video_file.with_suffix(".xyz")
    shutil.copy2(test_video_file, unsupported)
    try:
        with pytest.raises(FileValidationError, match="Unsupported format"):
            uploader.validate_file(str(unsupported))
    finally:
        os.unlink(unsupported)


def test_validate_file_empty(uploader: VideoUploader, test_video_file: Path) -> None:
    """Test validation of empty file."""
    empty_file = test_video_file.with_name("empty.mp4")
    empty_file.touch()
    try:
        with pytest.raises(FileValidationError, match="File is empty"):
            uploader.validate_file(str(empty_file))
    finally:
        os.unlink(empty_file)


def test_validate_file_too_large(
    uploader: VideoUploader, test_video_file: Path
) -> None:
    """Test validation of file exceeding size limit."""
    uploader.config.max_file_size = 10  # Set very small limit
    with pytest.raises(FileValidationError, match="File exceeds maximum size"):
        uploader.validate_file(str(test_video_file))


def test_validate_file_unreadable(
    uploader: VideoUploader, test_video_file: Path
) -> None:
    """Test validation of unreadable file."""
    if os.name != "nt":  # Skip on Windows
        os.chmod(test_video_file, 0o000)
        try:
            with pytest.raises(FileValidationError, match="Permission denied"):
                uploader.validate_file(str(test_video_file))
        finally:
            os.chmod(test_video_file, 0o666)


def test_upload_success(uploader: VideoUploader, test_video_file: Path) -> None:
    """Test successful file upload."""
    video = uploader.upload(str(test_video_file))
    assert isinstance(video, Video)
    assert isinstance(video.id, UUID)
    assert video.file_info.filename == test_video_file.name
    assert video.file_info.format == "MP4"
    assert video.file_info.file_size > 0

    # Verify file was copied
    uploaded_path = (
        uploader.config.upload_directory / str(video.id) / video.file_info.filename
    )
    assert uploaded_path.exists()
    assert uploaded_path.stat().st_size == test_video_file.stat().st_size


def test_upload_validation_failure(uploader: VideoUploader) -> None:
    """Test upload with invalid file."""
    with pytest.raises(FileValidationError, match="File does not exist"):
        uploader.upload("nonexistent.mp4")


def test_upload_disk_full(
    uploader: VideoUploader, test_video_file: Path, monkeypatch: MonkeyPatch
) -> None:
    """Test upload when disk is full."""

    def mock_copy2(*args: Any, **kwargs: Any) -> None:
        raise OSError("No space left on device")

    monkeypatch.setattr(shutil, "copy2", mock_copy2)
    with pytest.raises(FileValidationError, match="No space left on device"):
        uploader.upload(str(test_video_file))


def test_upload_permission_error(
    uploader: VideoUploader, test_video_file: Path
) -> None:
    """Test upload with insufficient permissions."""
    if os.name != "nt":  # Skip on Windows
        os.chmod(uploader.config.upload_directory, 0o444)  # Read-only
        try:
            with pytest.raises(FileValidationError, match="Permission denied"):
                uploader.upload(str(test_video_file))
        finally:
            os.chmod(uploader.config.upload_directory, 0o777)


def test_upload_concurrent(uploader: VideoUploader, test_video_file: Path) -> None:
    """Test concurrent uploads of the same file."""
    import threading

    def upload_file() -> None:
        video = uploader.upload(str(test_video_file))
        assert isinstance(video, Video)
        assert video.file_info.filename == test_video_file.name

    # Create multiple threads to upload the same file
    threads = [threading.Thread(target=upload_file) for _ in range(3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def test_upload_directory_creation(
    uploader: VideoUploader, test_video_file: Path
) -> None:
    """Test upload directory creation."""
    # Delete upload directory
    shutil.rmtree(uploader.config.upload_directory)

    # Upload should recreate directory
    video = uploader.upload(str(test_video_file))
    assert isinstance(video, Video)
    assert (uploader.config.upload_directory / str(video.id)).exists()


def test_upload_with_special_characters(
    uploader: VideoUploader, temp_upload_dir: Path
) -> None:
    """Test upload with special characters in filename."""
    special_file = temp_upload_dir / "test!@#$%^&*.mp4"
    special_file.write_bytes(b"test content")
    try:
        video = uploader.upload(str(special_file))
        assert isinstance(video, Video)
        assert video.file_info.filename == special_file.name
        assert (
            uploader.config.upload_directory / str(video.id) / video.file_info.filename
        ).exists()
    finally:
        os.unlink(special_file)
