import os
import pytest
from pathlib import Path
from uuid import UUID

from src.core.config import VideoConfig
from src.core.exceptions import FileValidationError
from src.video.upload import VideoUploader

@pytest.fixture
def test_dir():
    """Create and clean up a temporary test directory"""
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    # Cleanup after tests
    for file in test_dir.glob("*"):
        file.unlink()
    test_dir.rmdir()

@pytest.fixture
def valid_video_file(test_dir):
    """Create a valid test video file"""
    file_path = test_dir / "test_video.mp4"
    # Create a small valid MP4 file (1MB)
    with open(file_path, "wb") as f:
        f.write(b"0" * (1024 * 1024))  # 1MB of zeros
    yield file_path
    if file_path.exists():
        file_path.unlink()

@pytest.fixture
def large_video_file(test_dir):
    """Create a video file that exceeds size limit"""
    file_path = test_dir / "large_video.mp4"
    max_size = VideoConfig.MAX_FILE_SIZE
    # Create a file slightly larger than MAX_FILE_SIZE
    with open(file_path, "wb") as f:
        f.write(b"0" * (max_size + 1024))  # MAX_FILE_SIZE + 1KB
    yield file_path
    if file_path.exists():
        file_path.unlink()

@pytest.fixture
def invalid_format_file(test_dir):
    """Create a video file with invalid format"""
    file_path = test_dir / "invalid_video.xyz"
    with open(file_path, "wb") as f:
        f.write(b"0" * 1024)  # 1KB of zeros
    yield file_path
    if file_path.exists():
        file_path.unlink()

def test_video_upload_validation(large_video_file, invalid_format_file):
    """Test file validation for size and format"""
    config = VideoConfig()
    uploader = VideoUploader(config)
    
    # Test file size validation
    with pytest.raises(FileValidationError, match="File size exceeds maximum limit"):
        uploader.validate_file(str(large_video_file))
        
    # Test format validation
    with pytest.raises(FileValidationError, match="Unsupported format"):
        uploader.validate_file(str(invalid_format_file))
        
    # Test non-existent file
    with pytest.raises(FileValidationError, match="File does not exist"):
        uploader.validate_file("nonexistent_file.mp4")

def test_successful_upload(valid_video_file):
    """Test successful video upload"""
    config = VideoConfig()
    uploader = VideoUploader(config)
    
    video = uploader.upload(str(valid_video_file))
    
    assert isinstance(video.id, UUID)
    assert video.filename == "test_video.mp4"
    assert video.format == "MP4"
    assert video.status == "pending"
    
    # Verify file was copied to upload directory
    uploaded_path = config.UPLOAD_DIRECTORY / str(video.id) / video.filename
    assert uploaded_path.exists()
    assert uploaded_path.stat().st_size == valid_video_file.stat().st_size

def test_upload_creates_directory():
    """Test that upload directory is created if it doesn't exist"""
    config = VideoConfig()
    # Remove upload directory if it exists
    if config.UPLOAD_DIRECTORY.exists():
        for path in config.UPLOAD_DIRECTORY.glob("**/*"):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        config.UPLOAD_DIRECTORY.rmdir()
    
    uploader = VideoUploader(config)
    assert config.UPLOAD_DIRECTORY.exists()

def test_duplicate_upload(valid_video_file):
    """Test uploading the same file twice creates two distinct entries"""
    config = VideoConfig()
    uploader = VideoUploader(config)
    
    video1 = uploader.upload(str(valid_video_file))
    video2 = uploader.upload(str(valid_video_file))
    
    assert video1.id != video2.id
    assert video1.filename == video2.filename
    
    # Verify both files exist in different directories
    path1 = config.UPLOAD_DIRECTORY / str(video1.id) / video1.filename
    path2 = config.UPLOAD_DIRECTORY / str(video2.id) / video2.filename
    assert path1.exists()
    assert path2.exists() 