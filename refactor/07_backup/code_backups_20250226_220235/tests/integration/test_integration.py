import os

import pytest


@pytest.mark.integration
def test_environment():
    """Test that environment is properly set up"""
    # Check that we can import our package
    from src import __version__

    # Verify package is importable and has version
    assert __version__ == "0.1.0"


@pytest.mark.integration
def test_filesystem():
    """Test filesystem access"""
    assert os.path.exists("tests")
    assert os.path.exists("src")
