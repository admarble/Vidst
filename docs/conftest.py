"""Configure test environment for documentation building."""

import os
import sys
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(".."))


# Create mock classes
class MockNumpy:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return MagicMock()

    def __getattr__(self, name):
        return MagicMock()


# Mock modules
MOCK_MODULES = {
    "numpy": MockNumpy(),
    "numpy.core": MagicMock(),
    "numpy.core.multiarray": MagicMock(),
    "numpy.array_api": MagicMock(),
    "cv2": MagicMock(),
    "PIL": MagicMock(),
    "torch": MagicMock(),
    "tensorflow": MagicMock(),
    "sklearn": MagicMock(),
}

# Apply mocks
sys.modules.update(MOCK_MODULES)

# Import the package modules to ensure they're available
try:
    import video_understanding.storage
    import video_understanding.core
    import video_understanding.ai
    import video_understanding.video
except ImportError as e:
    print(f"Warning: Failed to import module: {e}")
