"""Tests for file integrity checking functionality."""

import pytest
from pathlib import Path
import tempfile
import os

from video_understanding.core.upload.integrity import FileIntegrityChecker
from video_understanding.core.exceptions import IntegrityError

@pytest.fixture
def sample_file():
    """Create a sample file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        # Write some test content
        f.write(b"test video content" * 1024)  # ~16KB of data
        f.flush()

    yield Path(f.name)
    Path(f.name).unlink()

@pytest.mark.asyncio
async def test_integrity_check(sample_file):
    """Test basic integrity checking."""
    checker = FileIntegrityChecker()
    await checker.check(sample_file)  # Should not raise any exceptions

@pytest.mark.asyncio
async def test_file_size_check(sample_file):
    """Test file size checking."""
    checker = FileIntegrityChecker()

    # Create a large file
    with open(sample_file, "wb") as f:
        f.write(b"0" * (3 * 1024 * 1024 * 1024))  # 3GB

    with pytest.raises(IntegrityError, match="File too large"):
        await checker.check(sample_file)

@pytest.mark.asyncio
async def test_file_format_check():
    """Test file format checking."""
    checker = FileIntegrityChecker()

    # Create file with invalid extension
    with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
        f.write(b"test content")
        f.flush()

    try:
        with pytest.raises(IntegrityError, match="Unsupported file format"):
            await checker.check(Path(f.name))
    finally:
        os.unlink(f.name)

@pytest.mark.asyncio
async def test_checksum_calculation(sample_file):
    """Test checksum calculation."""
    checker = FileIntegrityChecker()
    checksums = await checker._calculate_checksums(sample_file)

    assert isinstance(checksums, dict)
    assert "md5" in checksums
    assert "sha256" in checksums
    assert len(checksums["md5"]) == 32  # MD5 is 32 characters
    assert len(checksums["sha256"]) == 64  # SHA256 is 64 characters

@pytest.mark.asyncio
async def test_nonexistent_file():
    """Test handling of nonexistent file."""
    checker = FileIntegrityChecker()
    with pytest.raises(IntegrityError, match="File not found"):
        await checker.check(Path("nonexistent.mp4"))
