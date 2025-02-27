"""Tests for security scanning functionality."""

import pytest
from pathlib import Path
import tempfile
import os

from video_understanding.core.upload.security import SecurityScanner
from video_understanding.core.exceptions import SecurityError

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
async def test_security_scan(sample_file):
    """Test basic security scanning."""
    scanner = SecurityScanner()
    await scanner.scan(sample_file)  # Should not raise any exceptions

@pytest.mark.asyncio
async def test_virus_scan_config():
    """Test virus scan configuration."""
    scanner = SecurityScanner()

    # Test enabling/disabling virus scan
    scanner.set_virus_scan(False)
    assert scanner.virus_scan_enabled is False

    scanner.set_virus_scan(True)
    assert scanner.virus_scan_enabled is True

@pytest.mark.asyncio
async def test_content_validation_config():
    """Test content validation configuration."""
    scanner = SecurityScanner()

    # Test enabling/disabling content validation
    scanner.set_content_validation(False)
    assert scanner.content_validation_enabled is False

    scanner.set_content_validation(True)
    assert scanner.content_validation_enabled is True

@pytest.mark.asyncio
async def test_nonexistent_file():
    """Test handling of nonexistent file."""
    scanner = SecurityScanner()
    with pytest.raises(SecurityError, match="File not found"):
        await scanner.scan(Path("nonexistent.mp4"))

@pytest.mark.asyncio
async def test_scan_tasks(sample_file):
    """Test that appropriate scan tasks are run."""
    scanner = SecurityScanner()

    # Disable all scans
    scanner.set_virus_scan(False)
    scanner.set_content_validation(False)
    await scanner.scan(sample_file)  # Should complete quickly with no tasks

    # Enable virus scan only
    scanner.set_virus_scan(True)
    scanner.set_content_validation(False)
    await scanner.scan(sample_file)  # Should run virus scan only

    # Enable content validation only
    scanner.set_virus_scan(False)
    scanner.set_content_validation(True)
    await scanner.scan(sample_file)  # Should run content validation only

    # Enable both scans
    scanner.set_virus_scan(True)
    scanner.set_content_validation(True)
    await scanner.scan(sample_file)  # Should run both scans
