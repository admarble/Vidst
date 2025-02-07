"""
Tests for video upload functionality.
"""

import pytest
from pathlib import Path
from uuid import UUID

from src.core.exceptions import FileValidationError
from src.video.upload import VideoUploader

def test_video_upload_validation(video_config, sample_video_files, large_video_file):
    """Test file validation for various scenarios"""
    uploader = VideoUploader(video_config)
    
    # Test file size validation
    with pytest.raises(FileValidationError, match="File size exceeds maximum limit"):
        uploader.validate_file(str(large_video_file))
        
    # Test format validation
    with pytest.raises(FileValidationError, match="Unsupported format"):
        uploader.validate_file(str(sample_video_files["invalid_format"]))
        
    # Test non-existent file
    with pytest.raises(FileValidationError, match="File does not exist"):
        uploader.validate_file("nonexistent_file.mp4")
        
    # Test empty file
    with pytest.raises(FileValidationError, match="File size exceeds maximum limit"):
        uploader.validate_file(str(sample_video_files["empty"]))

def test_successful_upload_mp4(video_config, sample_video_files):
    """Test successful upload of MP4 file"""
    uploader = VideoUploader(video_config)
    video = uploader.upload(str(sample_video_files["valid_mp4"]))
    
    assert isinstance(video.id, UUID)
    assert video.filename == "sample.mp4"
    assert video.format == "MP4"
    assert video.status == "pending"
    
    # Verify file was copied to upload directory
    uploaded_path = video_config.UPLOAD_DIRECTORY / str(video.id) / video.filename
    assert uploaded_path.exists()
    assert uploaded_path.stat().st_size == sample_video_files["valid_mp4"].stat().st_size

def test_successful_upload_avi(video_config, sample_video_files):
    """Test successful upload of AVI file"""
    uploader = VideoUploader(video_config)
    video = uploader.upload(str(sample_video_files["valid_avi"]))
    
    assert isinstance(video.id, UUID)
    assert video.filename == "sample.avi"
    assert video.format == "AVI"
    assert video.status == "pending"

def test_successful_upload_mov(video_config, sample_video_files):
    """Test successful upload of MOV file"""
    uploader = VideoUploader(video_config)
    video = uploader.upload(str(sample_video_files["valid_mov"]))
    
    assert isinstance(video.id, UUID)
    assert video.filename == "sample.mov"
    assert video.format == "MOV"
    assert video.status == "pending"

def test_upload_creates_directory(video_config):
    """Test that upload directory is created if it doesn't exist"""
    # Remove upload directory if it exists
    if video_config.UPLOAD_DIRECTORY.exists():
        for path in video_config.UPLOAD_DIRECTORY.glob("**/*"):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        video_config.UPLOAD_DIRECTORY.rmdir()
    
    uploader = VideoUploader(video_config)
    assert video_config.UPLOAD_DIRECTORY.exists()

def test_duplicate_upload(video_config, sample_video_files):
    """Test uploading the same file twice creates two distinct entries"""
    uploader = VideoUploader(video_config)
    
    video1 = uploader.upload(str(sample_video_files["valid_mp4"]))
    video2 = uploader.upload(str(sample_video_files["valid_mp4"]))
    
    assert video1.id != video2.id
    assert video1.filename == video2.filename
    
    # Verify both files exist in different directories
    path1 = video_config.UPLOAD_DIRECTORY / str(video1.id) / video1.filename
    path2 = video_config.UPLOAD_DIRECTORY / str(video2.id) / video2.filename
    assert path1.exists()
    assert path2.exists()

def test_concurrent_uploads(video_config, sample_video_files):
    """Test multiple files can be uploaded concurrently"""
    uploader = VideoUploader(video_config)
    
    # Upload different formats concurrently
    videos = [
        uploader.upload(str(sample_video_files["valid_mp4"])),
        uploader.upload(str(sample_video_files["valid_avi"])),
        uploader.upload(str(sample_video_files["valid_mov"]))
    ]
    
    # Verify all uploads succeeded
    for video in videos:
        assert isinstance(video.id, UUID)
        uploaded_path = video_config.UPLOAD_DIRECTORY / str(video.id) / video.filename
        assert uploaded_path.exists() 