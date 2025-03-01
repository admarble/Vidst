"""Mock modules for documentation."""

from unittest.mock import MagicMock


class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return MagicMock()


MOCK_MODULES = {
    "numpy": Mock(),
    "numpy.array_api": Mock(),
    "numpy.core": Mock(),
    "numpy.core.multiarray": Mock(),
    "torch": Mock(),
    "cv2": Mock(),
    "PIL": Mock(),
    "sklearn": Mock(),
    "tensorflow": Mock(),
    "src": Mock(),
    "src.storage": Mock(),
    "src.core": Mock(),
    "src.ai": Mock(),
    "src.storage.cache": Mock(),
    "src.storage.vector": Mock(),
    "src.storage.metadata": Mock(),
    "src.core.config": Mock(),
    "src.core.processing": Mock(),
    "src.ai.models": Mock(),
}
