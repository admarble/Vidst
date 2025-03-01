"""
Shared pytest fixtures for video processing tests.
"""

# Standard library imports
import os
import shutil
import sys
from abc import ABC, abstractmethod
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from unittest.mock import MagicMock, patch
from uuid import UUID

# Third-party imports
import pytest
import numpy as np

# Type variables for generics
ProcessingConfigT = TypeVar("ProcessingConfigT", bound="BaseProcessingConfig")
VideoConfigT = TypeVar("VideoConfigT", bound="BaseVideoConfig")
VideoFileT = TypeVar("VideoFileT", bound="BaseVideoFile")
VideoProcessingStatusT = TypeVar(
    "VideoProcessingStatusT", bound="BaseVideoProcessingStatus"
)
VideoT = TypeVar("VideoT", bound="BaseVideo")


# Base classes for mocks
class BaseProcessingConfig(ABC):
    @property
    @abstractmethod
    def max_video_size(self) -> int:
        """Maximum allowed video size in bytes."""

    @property
    @abstractmethod
    def max_concurrent_uploads(self) -> int:
        """Maximum number of concurrent uploads allowed."""

    @property
    @abstractmethod
    def test_mode(self) -> bool:
        """Whether the processor is in test mode."""


class BaseVideoConfig(ABC):
    @property
    @abstractmethod
    def upload_directory(self) -> Path:
        """Directory for video uploads."""

    @property
    @abstractmethod
    def max_file_size(self) -> int:
        """Maximum allowed file size in bytes."""

    @property
    @abstractmethod
    def supported_formats(self) -> list[str]:
        """List of supported video formats."""


class BaseVideoFile(ABC):
    @property
    @abstractmethod
    def filename(self) -> str:
        """Name of the video file."""

    @property
    @abstractmethod
    def file_path(self) -> str:
        """Path to the video file."""

    @property
    @abstractmethod
    def format(self) -> str:
        """Video format."""

    @property
    @abstractmethod
    def file_size(self) -> int:
        """Size of the file in bytes."""


class BaseVideoProcessingStatus(ABC):
    @property
    @abstractmethod
    def status(self) -> str:
        """Current processing status."""


class BaseVideo(ABC):
    @property
    @abstractmethod
    def id(self) -> UUID:
        """Unique identifier for the video."""

    @property
    @abstractmethod
    def file_info(self) -> BaseVideoFile:
        """Video file information."""

    @property
    @abstractmethod
    def processing(self) -> BaseVideoProcessingStatus:
        """Video processing status."""


# Type aliases for imports
if TYPE_CHECKING:
    from video_understanding.core.config import (
        ProcessingConfig as ImportedProcessingConfig,  # type: ignore
    )
    from video_understanding.core.config import (
        VideoConfig as ImportedVideoConfig,  # type: ignore
    )
    from video_understanding.models.video import (
        Video as ImportedVideo,  # type: ignore
    )
    from video_understanding.models.video import (
        VideoFile as ImportedVideoFile,  # type: ignore
    )
    from video_understanding.models.video import (
        VideoProcessingStatus as ImportedVideoProcessingStatus,  # type: ignore
    )

    ProcessingConfigType = Union[ImportedProcessingConfig, "MockProcessingConfig"]
    VideoConfigType = Union[ImportedVideoConfig, "MockVideoConfig"]
    VideoType = Union[ImportedVideo, "MockVideo"]
    VideoFileType = Union[ImportedVideoFile, "MockVideoFile"]
    VideoProcessingStatusType = Union[
        ImportedVideoProcessingStatus, "MockVideoProcessingStatus"
    ]
else:
    ProcessingConfigType = Any
    VideoConfigType = Any
    VideoType = Any
    VideoFileType = Any
    VideoProcessingStatusType = Any

# Local imports
try:
    from video_understanding.core.config import (
        ProcessingConfig as RealProcessingConfig,  # type: ignore
    )
    from video_understanding.core.config import (
        VideoConfig as RealVideoConfig,  # type: ignore
    )
    from video_understanding.models.video import (
        Video as RealVideo,  # type: ignore
    )
    from video_understanding.models.video import (
        VideoFile as RealVideoFile,  # type: ignore
    )
    from video_understanding.models.video import (
        VideoProcessingStatus as RealVideoProcessingStatus,  # type: ignore
    )

    ProcessingConfig = cast(type[ProcessingConfigType], RealProcessingConfig)
    VideoConfig = cast(type[VideoConfigType], RealVideoConfig)
    Video = cast(type[VideoType], RealVideo)
    VideoFile = cast(type[VideoFileType], RealVideoFile)
    VideoProcessingStatus = cast(
        type[VideoProcessingStatusType], RealVideoProcessingStatus
    )

except ImportError:
    # Mock implementations
    class MockProcessingConfig(BaseProcessingConfig):
        """Mock implementation of ProcessingConfig."""

        def __init__(
            self, max_concurrent_uploads: int = 3, test_mode: bool = False
        ) -> None:
            self._max_video_size: int = 100 * 1024 * 1024  # 100MB
            self._max_concurrent_uploads: int = max_concurrent_uploads
            self._test_mode: bool = test_mode

        @property
        def max_video_size(self) -> int:
            """Maximum allowed video size in bytes."""
            return self._max_video_size

        @property
        def max_concurrent_uploads(self) -> int:
            """Maximum number of concurrent uploads allowed."""
            return self._max_concurrent_uploads

        @property
        def test_mode(self) -> bool:
            """Whether the processor is in test mode."""
            return self._test_mode

    class MockVideoConfig(BaseVideoConfig):
        """Mock implementation of VideoConfig."""

        def __init__(
            self,
            upload_directory: Path,
            max_file_size: int,
            supported_formats: list[str],
            file_path: str = "",  # Added required parameter with default
        ) -> None:
            self._upload_directory: Path = upload_directory
            self._max_file_size: int = max_file_size
            self._supported_formats: list[str] = supported_formats
            self._file_path: str = file_path

        @property
        def upload_directory(self) -> Path:
            """Directory for video uploads."""
            return self._upload_directory

        @property
        def max_file_size(self) -> int:
            """Maximum allowed file size in bytes."""
            return self._max_file_size

        @property
        def supported_formats(self) -> list[str]:
            """List of supported video formats."""
            return self._supported_formats

    class MockVideoFile(BaseVideoFile):
        """Mock implementation of VideoFile."""

        def __init__(
            self,
            filename: str,
            file_path: str,
            file_format: str,  # Renamed from format to avoid shadowing built-in
            file_size: int,
        ) -> None:
            self._filename: str = filename
            self._file_path: str = file_path
            self._format: str = file_format
            self._file_size: int = file_size

        @property
        def filename(self) -> str:
            """Name of the video file."""
            return self._filename

        @property
        def file_path(self) -> str:
            """Path to the video file."""
            return self._file_path

        @property
        def format(self) -> str:
            """Video format."""
            return self._format

        @property
        def file_size(self) -> int:
            """Size of the file in bytes."""
            return self._file_size

    class MockVideoProcessingStatus(BaseVideoProcessingStatus):
        """Mock implementation of VideoProcessingStatus."""

        def __init__(self, status: str) -> None:
            self._status: str = status

        @property
        def status(self) -> str:
            """Current processing status."""
            return self._status

    class MockVideo(BaseVideo):
        """Mock implementation of Video."""

        def __init__(
            self,
            video_id: UUID,  # Renamed from id to avoid shadowing built-in
            file_info: BaseVideoFile,
            processing: BaseVideoProcessingStatus,
        ) -> None:
            self._id: UUID = video_id
            self._file_info: BaseVideoFile = file_info
            self._processing: BaseVideoProcessingStatus = processing

        @property
        def id(self) -> UUID:
            """Unique identifier for the video."""
            return self._id

        @property
        def file_info(self) -> BaseVideoFile:
            """Video file information."""
            return self._file_info

        @property
        def processing(self) -> BaseVideoProcessingStatus:
            """Video processing status."""
            return self._processing

    # Assign mock classes with proper type casting
    ProcessingConfig = cast(type[ProcessingConfigType], MockProcessingConfig)
    VideoConfig = cast(type[VideoConfigType], MockVideoConfig)
    Video = cast(type[VideoType], MockVideo)
    VideoFile = cast(type[VideoFileType], MockVideoFile)
    VideoProcessingStatus = cast(
        type[VideoProcessingStatusType], MockVideoProcessingStatus
    )

# Mock cv2 module before any imports
mock_cv2 = MagicMock()

# Video capture and writer
mock_video_capture = MagicMock()
mock_video_capture.isOpened.return_value = True
mock_video_capture.read.return_value = (True, MagicMock())
mock_video_capture.get.side_effect = [
    30.0,
    300,
    1920,
    1080,
]  # fps, frames, width, height
mock_cv2.VideoCapture = MagicMock(return_value=mock_video_capture)
mock_cv2.VideoWriter = MagicMock()

# Image operations
mock_cv2.imread = MagicMock()
mock_cv2.imwrite = MagicMock()
mock_cv2.resize = MagicMock()
mock_cv2.cvtColor = MagicMock()

# Video capture properties
mock_cv2.CAP_PROP_POS_MSEC = 0
mock_cv2.CAP_PROP_POS_FRAMES = 1
mock_cv2.CAP_PROP_POS_AVI_RATIO = 2
mock_cv2.CAP_PROP_FRAME_WIDTH = 3
mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
mock_cv2.CAP_PROP_FPS = 5
mock_cv2.CAP_PROP_FOURCC = 6
mock_cv2.CAP_PROP_FRAME_COUNT = 7
mock_cv2.CAP_PROP_FORMAT = 8
mock_cv2.CAP_PROP_MODE = 9
mock_cv2.CAP_PROP_BRIGHTNESS = 10
mock_cv2.CAP_PROP_CONTRAST = 11
mock_cv2.CAP_PROP_SATURATION = 12
mock_cv2.CAP_PROP_HUE = 13
mock_cv2.CAP_PROP_GAIN = 14
mock_cv2.CAP_PROP_EXPOSURE = 15

# Color conversion codes
mock_cv2.COLOR_BGR2GRAY = 100
mock_cv2.COLOR_RGB2GRAY = 101
mock_cv2.COLOR_GRAY2BGR = 102
mock_cv2.COLOR_GRAY2RGB = 103
mock_cv2.COLOR_BGR2RGB = 104
mock_cv2.COLOR_RGB2BGR = 105

# Window properties
mock_cv2.WINDOW_NORMAL = 200
mock_cv2.WINDOW_AUTOSIZE = 201
mock_cv2.WINDOW_OPENGL = 202

# Mouse events
mock_cv2.EVENT_MOUSEMOVE = 300
mock_cv2.EVENT_LBUTTONDOWN = 301
mock_cv2.EVENT_RBUTTONDOWN = 302
mock_cv2.EVENT_MBUTTONDOWN = 303
mock_cv2.EVENT_LBUTTONUP = 304
mock_cv2.EVENT_RBUTTONUP = 305
mock_cv2.EVENT_MBUTTONUP = 306
mock_cv2.EVENT_LBUTTONDBLCLK = 307
mock_cv2.EVENT_RBUTTONDBLCLK = 308
mock_cv2.EVENT_MBUTTONDBLCLK = 309

# Interpolation methods
mock_cv2.INTER_NEAREST = 400
mock_cv2.INTER_LINEAR = 401
mock_cv2.INTER_CUBIC = 402
mock_cv2.INTER_AREA = 403
mock_cv2.INTER_LANCZOS4 = 404

# Border types
mock_cv2.BORDER_CONSTANT = 500
mock_cv2.BORDER_REPLICATE = 501
mock_cv2.BORDER_REFLECT = 502
mock_cv2.BORDER_WRAP = 503
mock_cv2.BORDER_REFLECT_101 = 504
mock_cv2.BORDER_TRANSPARENT = 505
mock_cv2.BORDER_DEFAULT = 506
mock_cv2.BORDER_ISOLATED = 507

# Apply the mock before any imports
sys.modules["cv2"] = mock_cv2

# Add src directory to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))


@pytest.fixture(scope="session")
def test_files_dir() -> Generator[Path, None, None]:
    """Create and manage a test files directory for the entire test session.

    Returns:
        Generator[Path, None, None]: A generator yielding the test directory
            path.
    """
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    # Cleanup after all tests
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture(scope="session")
def video_file_collection(files_dir) -> Generator[dict[str, Path], None, None]:
    """Create a collection of video files with different formats and sizes.

    Args:
        files_dir: The test files directory fixture.

    Returns:
        Generator[Dict[str, Path], None, None]: A generator yielding a dictionary
            of file paths keyed by their description.
    """
    files = {}

    # Valid MP4 file (1MB)
    mp4_path = files_dir / "sample.mp4"
    with open(mp4_path, "wb") as f:
        f.write(b"0" * (1024 * 1024))
    files["valid_mp4"] = mp4_path

    # Valid AVI file (2MB)
    avi_path = files_dir / "sample.avi"
    with open(avi_path, "wb") as f:
        f.write(b"0" * (2 * 1024 * 1024))
    files["valid_avi"] = avi_path

    # Valid MOV file (512KB)
    mov_path = files_dir / "sample.mov"
    with open(mov_path, "wb") as f:
        f.write(b"0" * (512 * 1024))
    files["valid_mov"] = mov_path

    # Invalid format file (1KB)
    invalid_path = files_dir / "invalid.xyz"
    with open(invalid_path, "wb") as f:
        f.write(b"0" * 1024)
    files["invalid_format"] = invalid_path

    # Empty file
    empty_path = files_dir / "empty.mp4"
    empty_path.touch()
    files["empty"] = empty_path

    yield files


@pytest.fixture(scope="session")
def oversized_video_file(files_dir) -> Generator[Path, None, None]:
    """Create a large video file that exceeds size limits."""
    file_path = files_dir / "large.mp4"
    max_size = MockProcessingConfig().max_video_size

    # Create sparse file to avoid actual disk usage
    file_path.touch()
    os.truncate(str(file_path), max_size + 1024)  # max_video_size + 1KB
    yield file_path


@pytest.fixture
def video_processing_config(tmp_path) -> VideoConfigType:
    """Create a test video configuration.

    Args:
        tmp_path: Temporary path fixture.

    Returns:
        VideoConfig: A test video configuration instance.
    """
    config = MockVideoConfig(
        upload_directory=tmp_path / "uploads",
        max_file_size=100 * 1024 * 1024,  # 100 MB
        supported_formats=["mp4", "avi"],
    )
    return config


@pytest.fixture
def sample_video_instance() -> VideoType:
    """Create a sample Video instance for testing.

    Returns:
        Video: A test video instance.
    """
    file_info = MockVideoFile(
        filename="test.mp4",
        file_path="/test/test.mp4",
        file_format="MP4",
        file_size=1024 * 1024,  # 1MB
    )
    return MockVideo(
        video_id=UUID("12345678-1234-5678-1234-567812345678"),
        file_info=file_info,
        processing=MockVideoProcessingStatus(status="pending"),
    )


@pytest.fixture
def temp_video_file(tmp_path) -> Path:
    """Create a temporary test video file.

    Args:
        tmp_path: Temporary path fixture.

    Returns:
        Path: Path to the temporary video file.
    """
    video_path = tmp_path / "test.mp4"
    video_path.write_bytes(b"test video content")
    return video_path


@pytest.fixture
def mock_env_vars(monkeypatch) -> dict[str, str]:
    """Setup mock environment variables for testing.

    Args:
        monkeypatch: Pytest monkeypatch fixture.

    Returns:
        Dict[str, str]: Dictionary of environment variables.
    """
    env_vars = {
        "OPENAI_API_KEY": ("sk-test-openaikey123456789abcdefghijklmnopqrstuvwxyz"),
        "GEMINI_API_KEY": ("AI-test-geminikey123456789abcdefghijklmnopqrstuvwxyz"),
        "TWELVE_LABS_API_KEY": (
            "tlk-test-12labskey123456789abcdefghijklmnopqrstuvwxyz"
        ),
        "ENVIRONMENT": "testing",
        "DEBUG": "true",
        "UPLOAD_DIRECTORY": "test_uploads",
        "MAX_CONCURRENT_JOBS": "2",
        "CACHE_TTL": "3600",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture(autouse=True)
def setup_test_env() -> Generator[None, None, None]:
    """Setup test environment variables.

    This fixture runs automatically before each test.

    Returns:
        Generator[None, None, None]: A generator that yields None.
    """
    os.environ["TWELVE_LABS_API_KEY"] = "test_key_12345678901"
    yield
    # Clean up after tests
    if "TWELVE_LABS_API_KEY" in os.environ:
        del os.environ["TWELVE_LABS_API_KEY"]


@pytest.fixture
def mock_video_capture() -> MagicMock:
    """Create a mock video capture.

    Returns:
        MagicMock: A mock video capture object.
    """
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.get.side_effect = [30.0, 300, 1920, 1080]  # fps, frames, width, height
    mock_cv2.VideoCapture.return_value = mock_cap
    return mock_cap


@pytest.fixture
def empty_video_path(tmp_path) -> Path:
    """Create an empty video file.

    Args:
        tmp_path: Temporary path fixture.

    Returns:
        Path: Path to the empty video file.
    """
    video_path = tmp_path / "empty.mp4"
    video_path.write_bytes(b"")
    return video_path


@pytest.fixture
def corrupted_video_path(tmp_path) -> Path:
    """Create a corrupted video file.

    Args:
        tmp_path: Temporary path fixture.

    Returns:
        Path: Path to the corrupted video file.
    """
    video_path = tmp_path / "corrupted.mp4"
    video_path.write_bytes(b"corrupted content")
    return video_path


@pytest.fixture
def test_output_dir(tmp_path) -> Path:
    """Create a test output directory.

    Args:
        tmp_path: Temporary path fixture.

    Returns:
        Path: Path to the test output directory.
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def test_cache_dir(tmp_path) -> Path:
    """Create a test cache directory.

    Args:
        tmp_path: Temporary path fixture.

    Returns:
        Path: Path to the test cache directory.
    """
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def test_env_vars(monkeypatch) -> dict[str, str]:
    """Set up test environment variables.

    Args:
        monkeypatch: Pytest monkeypatch fixture.

    Returns:
        Dict[str, str]: Dictionary of environment variables.
    """
    monkeypatch.setenv("VIDEO_MAX_SIZE", "104857600")  # 100 MB
    monkeypatch.setenv("VIDEO_FORMATS", "mp4,avi")
    monkeypatch.setenv("CACHE_DIR", "/tmp/cache")
    monkeypatch.setenv("OUTPUT_DIR", "/tmp/output")
    return {
        "VIDEO_MAX_SIZE": "104857600",
        "VIDEO_FORMATS": "mp4,avi",
        "CACHE_DIR": "/tmp/cache",
        "OUTPUT_DIR": "/tmp/output",
    }


@pytest.fixture
def sample_video() -> Path:
    """Fixture providing a sample video file path."""
    return Path("tests/fixtures/sample.mp4")


@pytest.fixture
def processor_config() -> ProcessingConfigType:
    """Fixture providing a processor configuration for testing."""
    return ProcessingConfig(max_concurrent_uploads=1, test_mode=True)


@pytest.fixture
def sample_frame() -> np.ndarray:
    """Fixture providing a sample video frame for testing."""
    return np.zeros((1080, 1920, 3), dtype=np.uint8)


@pytest.fixture(autouse=True)
def mock_cv2(monkeypatch):
    """Mock cv2 module for testing.

    This is an autouse fixture that will be applied to all tests.
    It properly mocks all cv2 functionality used in the codebase.

    Args:
        monkeypatch: pytest monkeypatch fixture

    Returns:
        MagicMock: Mocked cv2 module
    """
    # Create the main mock
    mock_cv2 = MagicMock()

    # Create a mock for VideoCapture
    mock_video_capture_instance = MagicMock()
    mock_video_capture_instance.isOpened.return_value = True
    # Create a real numpy array for read to return
    real_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    mock_video_capture_instance.read.return_value = (True, real_frame)
    mock_video_capture_instance.release.return_value = None

    # Configure get method to return appropriate values for different properties
    def mock_get(prop):
        prop_values = {
            mock_cv2.CAP_PROP_FRAME_WIDTH: 1280,
            mock_cv2.CAP_PROP_FRAME_HEIGHT: 720,
            mock_cv2.CAP_PROP_FPS: 30.0,
            mock_cv2.CAP_PROP_FRAME_COUNT: 300,
            mock_cv2.CAP_PROP_POS_FRAMES: 0,
            mock_cv2.CAP_PROP_POS_MSEC: 0,
            mock_cv2.CAP_PROP_FOURCC: 828601953,  # 'avc1'
            mock_cv2.CAP_PROP_FORMAT: 0,
        }
        return prop_values.get(prop, 0)

    mock_video_capture_instance.get.side_effect = mock_get

    # Set up VideoCapture class
    mock_video_capture = MagicMock(return_value=mock_video_capture_instance)
    mock_cv2.VideoCapture = mock_video_capture

    # Create mock functionality for cv2.cvtColor that returns a real numpy array
    def mock_cvtColor(src, code):
        # Just return the source array as is for simplicity
        return src.copy()

    mock_cv2.cvtColor = mock_cvtColor

    # Set up necessary constants
    mock_cv2.CAP_PROP_FRAME_WIDTH = 3
    mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
    mock_cv2.CAP_PROP_FPS = 5
    mock_cv2.CAP_PROP_FRAME_COUNT = 7
    mock_cv2.CAP_PROP_POS_FRAMES = 1
    mock_cv2.CAP_PROP_POS_MSEC = 0
    mock_cv2.CAP_PROP_FOURCC = 6
    mock_cv2.CAP_PROP_FORMAT = 8

    # Set up other commonly used cv2 functions and constants
    mock_cv2.COLOR_BGR2RGB = 4
    mock_cv2.COLOR_RGB2BGR = 5
    mock_cv2.COLOR_BGR2GRAY = 6
    mock_cv2.COLOR_RGB2GRAY = 7
    mock_cv2.INTER_LINEAR = 1
    mock_cv2.INTER_NEAREST = 0

    # Mock common image manipulation functions using real numpy arrays
    def mock_resize(img, dsize, **kwargs):
        # Return a real numpy array of the specified size
        return np.zeros(dsize[::-1] + (3,), dtype=np.uint8)

    mock_cv2.resize = mock_resize
    mock_cv2.imwrite = MagicMock(return_value=True)
    mock_cv2.imread = MagicMock(return_value=np.zeros((720, 1280, 3), dtype=np.uint8))

    # Patch cv2 module properly
    monkeypatch.setitem(sys.modules, "cv2", mock_cv2)

    return mock_cv2


@pytest.fixture(autouse=True)
def mock_pil(monkeypatch):
    """Mock PIL.Image for testing."""
    mock_pil_image = MagicMock()

    # Create a class for PIL.Image with proper array interface support
    class MockImage:
        @staticmethod
        def fromarray(array):
            # Create a MagicMock that has __array_interface__ attribute
            mock_img = MagicMock()
            # Set the __array_interface__ attribute as a property
            mock_img.__array_interface__ = array.__array_interface__
            # Ensure numpy can access the array interface
            mock_img.__array__ = lambda *args, **kwargs: array
            return mock_img

    mock_pil_image.Image = MockImage
    monkeypatch.setattr("PIL.Image", mock_pil_image.Image)
    return mock_pil_image
