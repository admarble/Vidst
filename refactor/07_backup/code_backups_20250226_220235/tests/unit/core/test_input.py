"""Unit tests for the input module."""

# Standard library imports
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, Mock, patch

# Third-party imports
import cv2
import pytest

# Local imports
from video_understanding.core.config import ProcessingConfig
from video_understanding.core.exceptions import ValidationError, VideoFormatError
from video_understanding.core.input import (
    VideoInfo,
    create_video_directory,
    get_video_info,
    list_video_files,
    process_video_file,
    validate_video,
)

# pylint: disable=redefined-outer-name,unused-argument

# Test data
SAMPLE_VIDEO_INFO = VideoInfo(
    file_path=Path("/test/video.mp4"),
    video_format="mp4",
    duration=10.0,
    width=1920,
    height=1080,
    fps=30.0,
    total_frames=300,
    file_size=1024000,
)


@pytest.fixture
def test_video_file(tmp_path: Path) -> Path:
    """Create a test video file for testing."""
    video_path = tmp_path / "test.mp4"
    video_path.write_bytes(b"test video content")
    return video_path


@pytest.fixture
def mock_video_capture() -> Generator[MagicMock, None, None]:
    """Create a mock cv2.VideoCapture."""
    with patch("cv2.VideoCapture") as mock_cap:
        cap_instance = Mock()
        cap_instance.isOpened.return_value = True
        cap_instance.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 300,
        }.get(prop, 0)
        mock_cap.return_value = cap_instance
        yield mock_cap


@pytest.fixture
def mock_magic() -> Generator[MagicMock, None, None]:
    """Create a mock python-magic."""
    with patch("magic.Magic") as mock:
        magic_instance = Mock()
        magic_instance.from_file.return_value = "video/mp4"
        mock.return_value = magic_instance
        yield mock


@pytest.fixture
def processing_config() -> ProcessingConfig:
    """Create a test video configuration."""
    config = ProcessingConfig()
    config.max_video_size = 1024 * 1024 * 1024  # 1GB
    config.supported_formats = ["mp4", "avi", "mov"]
    config.min_scene_length = 2.0
    config.max_scenes = 500
    config.concurrent_jobs = 3
    config.memory_limit = 4096
    return config


@pytest.fixture
def sample_video_path(tmp_path: Path) -> Path:
    """Create a temporary video file for testing."""
    video_path = tmp_path / "test_video.mp4"
    video_path.write_bytes(b"")
    return video_path


@pytest.fixture
def mock_cv2():
    """Mock cv2.VideoCapture for testing."""
    with patch("cv2.VideoCapture") as mock_cap:
        cap_instance = Mock()
        cap_instance.isOpened.return_value = True
        cap_instance.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 300,
        }.get(prop, 0)
        mock_cap.return_value = cap_instance
        yield mock_cap


@pytest.fixture
def mock_magic_lib():
    """Mock python-magic for testing."""
    with patch("magic.Magic") as mock_magic:
        magic_instance = Mock()
        magic_instance.from_file.return_value = "video/mp4"
        mock_magic.return_value = magic_instance
        yield mock_magic


@pytest.fixture
def config():
    """Create a ProcessingConfig for testing."""
    config = ProcessingConfig()
    config.max_video_size = 1024 * 1024 * 1024  # 1GB
    config.supported_formats = ["mp4", "avi", "mov"]
    config.min_scene_length = 2.0
    config.max_scenes = 500
    config.concurrent_jobs = 3
    config.memory_limit = 4096
    return config


class TestVideoInfo:
    """Test cases for VideoInfo class."""

    def test_video_info_creation(self):
        """Test VideoInfo creation with valid data."""
        info = SAMPLE_VIDEO_INFO
        assert info.file_path == Path("/test/video.mp4")
        assert info.video_format == "mp4"
        assert info.duration == 10.0
        assert info.width == 1920
        assert info.height == 1080
        assert info.fps == 30.0
        assert info.total_frames == 300
        assert info.file_size == 1024000


class TestGetVideoInfo:
    """Test cases for get_video_info function."""

    def test_get_video_info_nonexistent_file(self):
        """Test get_video_info with nonexistent file."""
        with pytest.raises(ValidationError):
            get_video_info(Path("/nonexistent/video.mp4"))

    def test_get_video_info_valid_file(
        self,
        test_video_file: Path,
        mock_video_capture: MagicMock,
        mock_magic: MagicMock,
    ):
        """Test get_video_info with valid video file."""
        info = get_video_info(test_video_file)
        assert isinstance(info, VideoInfo)
        assert info.video_format == "mp4"
        assert info.width == 1920
        assert info.height == 1080
        assert info.fps == 30.0
        assert info.total_frames == 300

    def test_get_video_info_invalid_format(
        self, test_video_file: Path, mock_magic: MagicMock
    ):
        """Test get_video_info with invalid file format."""
        mock_magic.return_value.from_file.return_value = "text/plain"
        with pytest.raises(VideoFormatError, match="Invalid file format"):
            get_video_info(test_video_file)

    def test_get_video_info_no_extension(self, tmp_path: Path, mock_magic: MagicMock):
        """Test get_video_info with file missing extension."""
        file_path = tmp_path / "video"
        file_path.write_bytes(b"mock content")
        with pytest.raises(VideoFormatError, match="Missing file extension"):
            get_video_info(file_path)

    def test_get_video_info_failed_open(
        self,
        test_video_file: Path,
        mock_video_capture: MagicMock,
        mock_magic: MagicMock,
    ):
        """Test get_video_info with failed video open."""
        mock_video_capture.return_value.isOpened.return_value = False
        with pytest.raises(VideoFormatError, match="Failed to open video file"):
            get_video_info(test_video_file)

    def test_get_video_info_zero_fps(
        self,
        test_video_file: Path,
        mock_video_capture: MagicMock,
        mock_magic: MagicMock,
    ):
        """Test get_video_info with zero FPS."""
        mock_video_capture.return_value.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080,
            cv2.CAP_PROP_FPS: 0.0,
            cv2.CAP_PROP_FRAME_COUNT: 300,
        }.get(prop, 0)
        info = get_video_info(test_video_file)
        assert info.duration == 0.0


class TestValidateVideo:
    def test_validate_video_valid(self, processing_config: ProcessingConfig):
        """Test validate_video with valid video info."""
        validate_video(SAMPLE_VIDEO_INFO, processing_config)  # Should not raise

    def test_validate_video_file_too_large(self, processing_config: ProcessingConfig):
        """Test validate_video with file size exceeding limit."""
        info = VideoInfo(
            file_path=Path("/test/large.mp4"),
            video_format="mp4",
            duration=10.0,
            width=1920,
            height=1080,
            fps=30.0,
            total_frames=300,
            file_size=processing_config.max_video_size + 1,
        )
        with pytest.raises(ValidationError, match="Video file too large"):
            validate_video(info, processing_config)

    def test_validate_video_unsupported_format(
        self, processing_config: ProcessingConfig
    ):
        """Test validate_video with unsupported format."""
        info = VideoInfo(
            file_path=Path("/test/video.xyz"),
            video_format="xyz",
            duration=10.0,
            width=1920,
            height=1080,
            fps=30.0,
            total_frames=300,
            file_size=1024000,
        )
        with pytest.raises(ValidationError, match="Unsupported video format"):
            validate_video(info, processing_config)

    def test_validate_video_zero_duration(self, processing_config: ProcessingConfig):
        """Test validate_video with zero duration."""
        info = VideoInfo(
            file_path=SAMPLE_VIDEO_INFO.file_path,
            video_format=SAMPLE_VIDEO_INFO.video_format,
            duration=0.0,  # Zero duration
            width=SAMPLE_VIDEO_INFO.width,
            height=SAMPLE_VIDEO_INFO.height,
            fps=SAMPLE_VIDEO_INFO.fps,
            total_frames=SAMPLE_VIDEO_INFO.total_frames,
            file_size=SAMPLE_VIDEO_INFO.file_size,
        )
        with pytest.raises(ValidationError, match="Invalid video duration"):
            validate_video(info, processing_config)

    def test_validate_video_invalid_dimensions(
        self, processing_config: ProcessingConfig
    ):
        """Test validate_video with invalid dimensions."""
        # Test zero width
        info = VideoInfo(
            file_path=SAMPLE_VIDEO_INFO.file_path,
            video_format=SAMPLE_VIDEO_INFO.video_format,
            duration=SAMPLE_VIDEO_INFO.duration,
            width=0,  # Invalid width
            height=SAMPLE_VIDEO_INFO.height,
            fps=SAMPLE_VIDEO_INFO.fps,
            total_frames=SAMPLE_VIDEO_INFO.total_frames,
            file_size=SAMPLE_VIDEO_INFO.file_size,
        )
        with pytest.raises(ValidationError, match="Invalid video dimensions"):
            validate_video(info, processing_config)

        # Test zero height
        info = VideoInfo(
            file_path=SAMPLE_VIDEO_INFO.file_path,
            video_format=SAMPLE_VIDEO_INFO.video_format,
            duration=SAMPLE_VIDEO_INFO.duration,
            width=SAMPLE_VIDEO_INFO.width,
            height=0,  # Invalid height
            fps=SAMPLE_VIDEO_INFO.fps,
            total_frames=SAMPLE_VIDEO_INFO.total_frames,
            file_size=SAMPLE_VIDEO_INFO.file_size,
        )
        with pytest.raises(ValidationError, match="Invalid video dimensions"):
            validate_video(info, processing_config)

    def test_validate_video_zero_fps(self, processing_config: ProcessingConfig):
        """Test validate_video with zero FPS."""
        info = VideoInfo(
            file_path=SAMPLE_VIDEO_INFO.file_path,
            video_format=SAMPLE_VIDEO_INFO.video_format,
            duration=SAMPLE_VIDEO_INFO.duration,
            width=SAMPLE_VIDEO_INFO.width,
            height=SAMPLE_VIDEO_INFO.height,
            fps=0.0,  # Zero FPS
            total_frames=SAMPLE_VIDEO_INFO.total_frames,
            file_size=SAMPLE_VIDEO_INFO.file_size,
        )
        with pytest.raises(ValidationError, match="Invalid frame rate"):
            validate_video(info, processing_config)


class TestProcessVideoFile:
    """Test cases for process_video_file function."""

    def test_process_video_file_valid(
        self,
        test_video_file: Path,
        mock_video_capture: MagicMock,
        mock_magic: MagicMock,
        processing_config: ProcessingConfig,
    ):
        """Test process_video_file with valid file."""
        info = process_video_file(test_video_file, processing_config)
        assert isinstance(info, VideoInfo)
        assert info.video_format == "mp4"
        assert info.width == 1920
        assert info.height == 1080

    def test_process_video_file_invalid_format(
        self,
        test_video_file: Path,
        mock_magic: MagicMock,
        processing_config: ProcessingConfig,
    ):
        """Test process_video_file with invalid format."""
        mock_magic.return_value.from_file.return_value = "text/plain"
        with pytest.raises(VideoFormatError):
            process_video_file(test_video_file, processing_config)

    def test_process_video_file_validation_error(
        self,
        test_video_file: Path,
        mock_video_capture: MagicMock,
        mock_magic: MagicMock,
        processing_config: ProcessingConfig,
    ):
        """Test process_video_file with validation error."""
        mock_video_capture.return_value.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_WIDTH: 0,  # Invalid width
            cv2.CAP_PROP_FRAME_HEIGHT: 1080,
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_COUNT: 300,
        }.get(prop, 0)
        with pytest.raises(ValidationError):
            process_video_file(test_video_file, processing_config)


class TestListVideoFiles:
    def test_list_video_files_empty_dir(self, tmp_path, mock_magic):
        """Test list_video_files with empty directory."""
        files = list_video_files(tmp_path)
        assert len(files) == 0

    def test_list_video_files_with_videos(self, tmp_path, mock_magic):
        """Test list_video_files with video files."""
        # Create mock video files
        (tmp_path / "video1.mp4").write_bytes(b"mock content")
        (tmp_path / "video2.mp4").write_bytes(b"mock content")
        (tmp_path / "document.txt").write_bytes(b"text content")

        # Mock magic to identify videos
        mock_magic.return_value.from_file.side_effect = lambda path: (
            "video/mp4" if path.endswith(".mp4") else "text/plain"
        )

        files = list_video_files(tmp_path)
        assert len(files) == 2
        assert all(f.suffix == ".mp4" for f in files)

    def test_list_video_files_recursive(self, tmp_path, mock_magic):
        """Test list_video_files with recursive search."""
        # Create nested directory structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "video1.mp4").write_bytes(b"mock content")
        (subdir / "video2.mp4").write_bytes(b"mock content")

        # Mock magic to identify videos
        mock_magic.return_value.from_file.return_value = "video/mp4"

        files = list_video_files(tmp_path, recursive=True)
        assert len(files) == 2
        assert any(f.name == "video1.mp4" for f in files)
        assert any(f.name == "video2.mp4" for f in files)

    def test_list_video_files_nonexistent_dir(self):
        """Test list_video_files with nonexistent directory."""
        with pytest.raises(ValidationError):
            list_video_files(Path("/nonexistent/dir"))

    def test_list_video_files_not_directory(self, tmp_path):
        """Test list_video_files with file path."""
        file_path = tmp_path / "file.txt"
        file_path.write_bytes(b"content")
        with pytest.raises(ValidationError):
            list_video_files(file_path)

    def test_list_video_files_magic_error(self, tmp_path, mock_magic):
        """Test list_video_files with magic error."""
        (tmp_path / "video.mp4").write_bytes(b"mock content")
        mock_magic.return_value.from_file.side_effect = Exception("Magic error")
        files = list_video_files(tmp_path)
        assert len(files) == 0  # Should skip files that cause errors


class TestCreateVideoDirectory:
    def test_create_video_directory(self, tmp_path):
        """Test create_video_directory with valid path."""
        dir_path = tmp_path / "videos"
        create_video_directory(dir_path)
        assert dir_path.exists()
        assert dir_path.is_dir()
        assert oct(dir_path.stat().st_mode)[-3:] == "755"

    def test_create_video_directory_exists(self, tmp_path):
        """Test create_video_directory with existing directory."""
        dir_path = tmp_path / "videos"
        dir_path.mkdir()
        create_video_directory(dir_path)  # Should not raise
        assert dir_path.exists()

    def test_create_video_directory_nested(self, tmp_path):
        """Test create_video_directory with nested path."""
        dir_path = tmp_path / "parent" / "videos"
        create_video_directory(dir_path)
        assert dir_path.exists()
        assert dir_path.is_dir()

    @patch("src.video_understanding.core.input.os.chmod")
    def test_create_video_directory_permission_error(self, mock_chmod, tmp_path):
        """Test create_video_directory with permission error."""
        mock_chmod.side_effect = PermissionError()
        dir_path = tmp_path / "videos"
        with pytest.raises(ValidationError):
            create_video_directory(dir_path)

    def test_create_video_directory_mkdir_error(self, tmp_path):
        """Test create_video_directory when mkdir raises an error."""
        dir_path = tmp_path / "test_dir"

        # Mock Path.mkdir to raise an error
        with patch.object(Path, "mkdir", side_effect=OSError("Test error")):
            with pytest.raises(ValidationError):
                create_video_directory(dir_path)


def test_get_video_info_valid_file(test_video_file, mock_video_capture, mock_magic):
    """Test get_video_info with valid video file."""
    info = get_video_info(test_video_file)
    assert isinstance(info, VideoInfo)
    assert info.video_format == "mp4"
    assert info.width == 1920
    assert info.height == 1080
    assert info.fps == 30.0
    assert info.total_frames == 300
