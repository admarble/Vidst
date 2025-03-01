"""Unit tests for the core configuration module."""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from video_understanding.core.config import (
    ProcessingConfig,
    VideoConfig,
    AIModelConfig,
    StorageConfig,
    SecurityConfig,
    LoggingConfig,
    DEFAULT_PROCESSING_CONFIG,
    DEFAULT_VIDEO_CONFIG,
    DEFAULT_AI_MODEL_CONFIG,
    DEFAULT_STORAGE_CONFIG,
    DEFAULT_SECURITY_CONFIG,
    DEFAULT_LOGGING_CONFIG,
    load_config,
    save_config,
)


class TestProcessingConfig:
    """Test suite for ProcessingConfig."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        config = ProcessingConfig()

        assert (
            config.max_video_duration_seconds
            == DEFAULT_PROCESSING_CONFIG.max_video_duration_seconds
        )
        assert (
            config.max_video_file_size_mb
            == DEFAULT_PROCESSING_CONFIG.max_video_file_size_mb
        )
        assert config.supported_formats == DEFAULT_PROCESSING_CONFIG.supported_formats
        assert (
            config.scene_detection_threshold
            == DEFAULT_PROCESSING_CONFIG.scene_detection_threshold
        )
        assert (
            config.minimum_scene_duration_seconds
            == DEFAULT_PROCESSING_CONFIG.minimum_scene_duration_seconds
        )
        assert (
            config.max_concurrent_jobs == DEFAULT_PROCESSING_CONFIG.max_concurrent_jobs
        )
        assert (
            config.job_timeout_seconds == DEFAULT_PROCESSING_CONFIG.job_timeout_seconds
        )

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        custom_config = ProcessingConfig(
            max_video_duration_seconds=600,
            max_video_file_size_mb=500,
            supported_formats=["MP4", "MOV"],
            scene_detection_threshold=0.4,
            minimum_scene_duration_seconds=3.0,
            max_concurrent_jobs=5,
            job_timeout_seconds=300,
        )

        assert custom_config.max_video_duration_seconds == 600
        assert custom_config.max_video_file_size_mb == 500
        assert custom_config.supported_formats == ["MP4", "MOV"]
        assert custom_config.scene_detection_threshold == 0.4
        assert custom_config.minimum_scene_duration_seconds == 3.0
        assert custom_config.max_concurrent_jobs == 5
        assert custom_config.job_timeout_seconds == 300

    def test_validation(self):
        """Test validation rules for ProcessingConfig."""
        # Invalid max_video_duration_seconds (negative)
        with pytest.raises(ValueError):
            ProcessingConfig(max_video_duration_seconds=-1)

        # Invalid max_video_file_size_mb (negative)
        with pytest.raises(ValueError):
            ProcessingConfig(max_video_file_size_mb=-1)

        # Invalid supported_formats (empty list)
        with pytest.raises(ValueError):
            ProcessingConfig(supported_formats=[])

        # Invalid scene_detection_threshold (out of range)
        with pytest.raises(ValueError):
            ProcessingConfig(scene_detection_threshold=1.5)

        # Invalid minimum_scene_duration_seconds (negative)
        with pytest.raises(ValueError):
            ProcessingConfig(minimum_scene_duration_seconds=-1)

        # Invalid max_concurrent_jobs (negative)
        with pytest.raises(ValueError):
            ProcessingConfig(max_concurrent_jobs=-1)

        # Invalid job_timeout_seconds (negative)
        with pytest.raises(ValueError):
            ProcessingConfig(job_timeout_seconds=-1)

    def test_from_dict(self):
        """Test creation from dictionary."""
        config_dict = {
            "max_video_duration_seconds": 600,
            "max_video_file_size_mb": 500,
            "supported_formats": ["MP4", "MOV"],
            "scene_detection_threshold": 0.4,
            "minimum_scene_duration_seconds": 3.0,
            "max_concurrent_jobs": 5,
            "job_timeout_seconds": 300,
        }

        config = ProcessingConfig.from_dict(config_dict)

        assert config.max_video_duration_seconds == 600
        assert config.max_video_file_size_mb == 500
        assert config.supported_formats == ["MP4", "MOV"]
        assert config.scene_detection_threshold == 0.4
        assert config.minimum_scene_duration_seconds == 3.0
        assert config.max_concurrent_jobs == 5
        assert config.job_timeout_seconds == 300

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = ProcessingConfig(
            max_video_duration_seconds=600,
            max_video_file_size_mb=500,
            supported_formats=["MP4", "MOV"],
            scene_detection_threshold=0.4,
            minimum_scene_duration_seconds=3.0,
            max_concurrent_jobs=5,
            job_timeout_seconds=300,
        )

        config_dict = config.to_dict()

        assert config_dict["max_video_duration_seconds"] == 600
        assert config_dict["max_video_file_size_mb"] == 500
        assert config_dict["supported_formats"] == ["MP4", "MOV"]
        assert config_dict["scene_detection_threshold"] == 0.4
        assert config_dict["minimum_scene_duration_seconds"] == 3.0
        assert config_dict["max_concurrent_jobs"] == 5
        assert config_dict["job_timeout_seconds"] == 300

    def test_equality(self):
        """Test equality comparison."""
        config1 = ProcessingConfig(
            max_video_duration_seconds=600,
            max_video_file_size_mb=500,
        )

        config2 = ProcessingConfig(
            max_video_duration_seconds=600,
            max_video_file_size_mb=500,
        )

        config3 = ProcessingConfig(
            max_video_duration_seconds=1200,
            max_video_file_size_mb=500,
        )

        assert config1 == config2
        assert config1 != config3
        assert config1 != "not a config"


class TestVideoConfig:
    """Test suite for VideoConfig."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        config = VideoConfig()

        assert config.upload_dir == DEFAULT_VIDEO_CONFIG.upload_dir
        assert config.temp_dir == DEFAULT_VIDEO_CONFIG.temp_dir
        assert config.processed_dir == DEFAULT_VIDEO_CONFIG.processed_dir
        assert config.quarantine_dir == DEFAULT_VIDEO_CONFIG.quarantine_dir
        assert config.extract_audio == DEFAULT_VIDEO_CONFIG.extract_audio
        assert config.extract_frames == DEFAULT_VIDEO_CONFIG.extract_frames
        assert (
            config.frame_extraction_interval
            == DEFAULT_VIDEO_CONFIG.frame_extraction_interval
        )

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        custom_config = VideoConfig(
            upload_dir="custom_uploads",
            temp_dir="custom_temp",
            processed_dir="custom_processed",
            quarantine_dir="custom_quarantine",
            extract_audio=False,
            extract_frames=False,
            frame_extraction_interval=5.0,
        )

        assert custom_config.upload_dir == "custom_uploads"
        assert custom_config.temp_dir == "custom_temp"
        assert custom_config.processed_dir == "custom_processed"
        assert custom_config.quarantine_dir == "custom_quarantine"
        assert custom_config.extract_audio is False
        assert custom_config.extract_frames is False
        assert custom_config.frame_extraction_interval == 5.0

    def test_validation(self):
        """Test validation rules for VideoConfig."""
        # Invalid upload_dir (empty string)
        with pytest.raises(ValueError):
            VideoConfig(upload_dir="")

        # Invalid temp_dir (empty string)
        with pytest.raises(ValueError):
            VideoConfig(temp_dir="")

        # Invalid processed_dir (empty string)
        with pytest.raises(ValueError):
            VideoConfig(processed_dir="")

        # Invalid quarantine_dir (empty string)
        with pytest.raises(ValueError):
            VideoConfig(quarantine_dir="")

        # Invalid frame_extraction_interval (negative)
        with pytest.raises(ValueError):
            VideoConfig(frame_extraction_interval=-1)

    def test_from_dict(self):
        """Test creation from dictionary."""
        config_dict = {
            "upload_dir": "custom_uploads",
            "temp_dir": "custom_temp",
            "processed_dir": "custom_processed",
            "quarantine_dir": "custom_quarantine",
            "extract_audio": False,
            "extract_frames": False,
            "frame_extraction_interval": 5.0,
        }

        config = VideoConfig.from_dict(config_dict)

        assert config.upload_dir == "custom_uploads"
        assert config.temp_dir == "custom_temp"
        assert config.processed_dir == "custom_processed"
        assert config.quarantine_dir == "custom_quarantine"
        assert config.extract_audio is False
        assert config.extract_frames is False
        assert config.frame_extraction_interval == 5.0

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = VideoConfig(
            upload_dir="custom_uploads",
            temp_dir="custom_temp",
            processed_dir="custom_processed",
            quarantine_dir="custom_quarantine",
            extract_audio=False,
            extract_frames=False,
            frame_extraction_interval=5.0,
        )

        config_dict = config.to_dict()

        assert config_dict["upload_dir"] == "custom_uploads"
        assert config_dict["temp_dir"] == "custom_temp"
        assert config_dict["processed_dir"] == "custom_processed"
        assert config_dict["quarantine_dir"] == "custom_quarantine"
        assert config_dict["extract_audio"] is False
        assert config_dict["extract_frames"] is False
        assert config_dict["frame_extraction_interval"] == 5.0

    def test_equality(self):
        """Test equality comparison."""
        config1 = VideoConfig(
            upload_dir="custom_uploads",
            temp_dir="custom_temp",
        )

        config2 = VideoConfig(
            upload_dir="custom_uploads",
            temp_dir="custom_temp",
        )

        config3 = VideoConfig(
            upload_dir="different_uploads",
            temp_dir="custom_temp",
        )

        assert config1 == config2
        assert config1 != config3
        assert config1 != "not a config"


class TestAIModelConfig:
    """Test suite for AIModelConfig."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        config = AIModelConfig()

        assert config.openai_api_key == DEFAULT_AI_MODEL_CONFIG.openai_api_key
        assert config.gemini_api_key == DEFAULT_AI_MODEL_CONFIG.gemini_api_key
        assert config.twelve_labs_api_key == DEFAULT_AI_MODEL_CONFIG.twelve_labs_api_key
        assert config.whisper_api_key == DEFAULT_AI_MODEL_CONFIG.whisper_api_key
        assert config.openai_model == DEFAULT_AI_MODEL_CONFIG.openai_model
        assert config.gemini_model == DEFAULT_AI_MODEL_CONFIG.gemini_model
        assert (
            config.twelve_labs_index_id == DEFAULT_AI_MODEL_CONFIG.twelve_labs_index_id
        )
        assert config.whisper_model == DEFAULT_AI_MODEL_CONFIG.whisper_model

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        custom_config = AIModelConfig(
            openai_api_key="custom_openai_key",
            gemini_api_key="custom_gemini_key",
            twelve_labs_api_key="custom_twelve_labs_key",
            whisper_api_key="custom_whisper_key",
            openai_model="gpt-4-vision-custom",
            gemini_model="gemini-pro-vision-custom",
            twelve_labs_index_id="custom_index_id",
            whisper_model="whisper-custom",
        )

        assert custom_config.openai_api_key == "custom_openai_key"
        assert custom_config.gemini_api_key == "custom_gemini_key"
        assert custom_config.twelve_labs_api_key == "custom_twelve_labs_key"
        assert custom_config.whisper_api_key == "custom_whisper_key"
        assert custom_config.openai_model == "gpt-4-vision-custom"
        assert custom_config.gemini_model == "gemini-pro-vision-custom"
        assert custom_config.twelve_labs_index_id == "custom_index_id"
        assert custom_config.whisper_model == "whisper-custom"

    def test_from_dict(self):
        """Test creation from dictionary."""
        config_dict = {
            "openai_api_key": "custom_openai_key",
            "gemini_api_key": "custom_gemini_key",
            "twelve_labs_api_key": "custom_twelve_labs_key",
            "whisper_api_key": "custom_whisper_key",
            "openai_model": "gpt-4-vision-custom",
            "gemini_model": "gemini-pro-vision-custom",
            "twelve_labs_index_id": "custom_index_id",
            "whisper_model": "whisper-custom",
        }

        config = AIModelConfig.from_dict(config_dict)

        assert config.openai_api_key == "custom_openai_key"
        assert config.gemini_api_key == "custom_gemini_key"
        assert config.twelve_labs_api_key == "custom_twelve_labs_key"
        assert config.whisper_api_key == "custom_whisper_key"
        assert config.openai_model == "gpt-4-vision-custom"
        assert config.gemini_model == "gemini-pro-vision-custom"
        assert config.twelve_labs_index_id == "custom_index_id"
        assert config.whisper_model == "whisper-custom"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = AIModelConfig(
            openai_api_key="custom_openai_key",
            gemini_api_key="custom_gemini_key",
            twelve_labs_api_key="custom_twelve_labs_key",
            whisper_api_key="custom_whisper_key",
            openai_model="gpt-4-vision-custom",
            gemini_model="gemini-pro-vision-custom",
            twelve_labs_index_id="custom_index_id",
            whisper_model="whisper-custom",
        )

        config_dict = config.to_dict()

        assert config_dict["openai_api_key"] == "custom_openai_key"
        assert config_dict["gemini_api_key"] == "custom_gemini_key"
        assert config_dict["twelve_labs_api_key"] == "custom_twelve_labs_key"
        assert config_dict["whisper_api_key"] == "custom_whisper_key"
        assert config_dict["openai_model"] == "gpt-4-vision-custom"
        assert config_dict["gemini_model"] == "gemini-pro-vision-custom"
        assert config_dict["twelve_labs_index_id"] == "custom_index_id"
        assert config_dict["whisper_model"] == "whisper-custom"

    def test_equality(self):
        """Test equality comparison."""
        config1 = AIModelConfig(
            openai_api_key="custom_openai_key",
            gemini_api_key="custom_gemini_key",
        )

        config2 = AIModelConfig(
            openai_api_key="custom_openai_key",
            gemini_api_key="custom_gemini_key",
        )

        config3 = AIModelConfig(
            openai_api_key="different_openai_key",
            gemini_api_key="custom_gemini_key",
        )

        assert config1 == config2
        assert config1 != config3
        assert config1 != "not a config"


class TestStorageConfig:
    """Test suite for StorageConfig."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        config = StorageConfig()

        assert config.vector_db_path == DEFAULT_STORAGE_CONFIG.vector_db_path
        assert config.metadata_db_path == DEFAULT_STORAGE_CONFIG.metadata_db_path
        assert config.vector_dimension == DEFAULT_STORAGE_CONFIG.vector_dimension
        assert config.cache_ttl_seconds == DEFAULT_STORAGE_CONFIG.cache_ttl_seconds
        assert config.max_cache_size_mb == DEFAULT_STORAGE_CONFIG.max_cache_size_mb

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        custom_config = StorageConfig(
            vector_db_path="custom_vector_path",
            metadata_db_path="custom_metadata_path",
            vector_dimension=512,
            cache_ttl_seconds=7200,
            max_cache_size_mb=2048,
        )

        assert custom_config.vector_db_path == "custom_vector_path"
        assert custom_config.metadata_db_path == "custom_metadata_path"
        assert custom_config.vector_dimension == 512
        assert custom_config.cache_ttl_seconds == 7200
        assert custom_config.max_cache_size_mb == 2048

    def test_validation(self):
        """Test validation rules for StorageConfig."""
        # Invalid vector_db_path (empty string)
        with pytest.raises(ValueError):
            StorageConfig(vector_db_path="")

        # Invalid metadata_db_path (empty string)
        with pytest.raises(ValueError):
            StorageConfig(metadata_db_path="")

        # Invalid vector_dimension (negative)
        with pytest.raises(ValueError):
            StorageConfig(vector_dimension=-1)

        # Invalid cache_ttl_seconds (negative)
        with pytest.raises(ValueError):
            StorageConfig(cache_ttl_seconds=-1)

        # Invalid max_cache_size_mb (negative)
        with pytest.raises(ValueError):
            StorageConfig(max_cache_size_mb=-1)

    def test_from_dict(self):
        """Test creation from dictionary."""
        config_dict = {
            "vector_db_path": "custom_vector_path",
            "metadata_db_path": "custom_metadata_path",
            "vector_dimension": 512,
            "cache_ttl_seconds": 7200,
            "max_cache_size_mb": 2048,
        }

        config = StorageConfig.from_dict(config_dict)

        assert config.vector_db_path == "custom_vector_path"
        assert config.metadata_db_path == "custom_metadata_path"
        assert config.vector_dimension == 512
        assert config.cache_ttl_seconds == 7200
        assert config.max_cache_size_mb == 2048

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = StorageConfig(
            vector_db_path="custom_vector_path",
            metadata_db_path="custom_metadata_path",
            vector_dimension=512,
            cache_ttl_seconds=7200,
            max_cache_size_mb=2048,
        )

        config_dict = config.to_dict()

        assert config_dict["vector_db_path"] == "custom_vector_path"
        assert config_dict["metadata_db_path"] == "custom_metadata_path"
        assert config_dict["vector_dimension"] == 512
        assert config_dict["cache_ttl_seconds"] == 7200
        assert config_dict["max_cache_size_mb"] == 2048

    def test_equality(self):
        """Test equality comparison."""
        config1 = StorageConfig(
            vector_db_path="custom_vector_path",
            metadata_db_path="custom_metadata_path",
        )

        config2 = StorageConfig(
            vector_db_path="custom_vector_path",
            metadata_db_path="custom_metadata_path",
        )

        config3 = StorageConfig(
            vector_db_path="different_vector_path",
            metadata_db_path="custom_metadata_path",
        )

        assert config1 == config2
        assert config1 != config3
        assert config1 != "not a config"


class TestSecurityConfig:
    """Test suite for SecurityConfig."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        config = SecurityConfig()

        assert (
            config.enable_integrity_check
            == DEFAULT_SECURITY_CONFIG.enable_integrity_check
        )
        assert config.enable_virus_scan == DEFAULT_SECURITY_CONFIG.enable_virus_scan
        assert config.allowed_domains == DEFAULT_SECURITY_CONFIG.allowed_domains
        assert (
            config.max_requests_per_minute
            == DEFAULT_SECURITY_CONFIG.max_requests_per_minute
        )
        assert config.require_api_key == DEFAULT_SECURITY_CONFIG.require_api_key

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        custom_config = SecurityConfig(
            enable_integrity_check=False,
            enable_virus_scan=False,
            allowed_domains=["example.com", "test.org"],
            max_requests_per_minute=30,
            require_api_key=True,
        )

        assert custom_config.enable_integrity_check is False
        assert custom_config.enable_virus_scan is False
        assert custom_config.allowed_domains == ["example.com", "test.org"]
        assert custom_config.max_requests_per_minute == 30
        assert custom_config.require_api_key is True

    def test_validation(self):
        """Test validation rules for SecurityConfig."""
        # Invalid max_requests_per_minute (negative)
        with pytest.raises(ValueError):
            SecurityConfig(max_requests_per_minute=-1)

    def test_from_dict(self):
        """Test creation from dictionary."""
        config_dict = {
            "enable_integrity_check": False,
            "enable_virus_scan": False,
            "allowed_domains": ["example.com", "test.org"],
            "max_requests_per_minute": 30,
            "require_api_key": True,
        }

        config = SecurityConfig.from_dict(config_dict)

        assert config.enable_integrity_check is False
        assert config.enable_virus_scan is False
        assert config.allowed_domains == ["example.com", "test.org"]
        assert config.max_requests_per_minute == 30
        assert config.require_api_key is True

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = SecurityConfig(
            enable_integrity_check=False,
            enable_virus_scan=False,
            allowed_domains=["example.com", "test.org"],
            max_requests_per_minute=30,
            require_api_key=True,
        )

        config_dict = config.to_dict()

        assert config_dict["enable_integrity_check"] is False
        assert config_dict["enable_virus_scan"] is False
        assert config_dict["allowed_domains"] == ["example.com", "test.org"]
        assert config_dict["max_requests_per_minute"] == 30
        assert config_dict["require_api_key"] is True

    def test_equality(self):
        """Test equality comparison."""
        config1 = SecurityConfig(
            enable_integrity_check=False,
            enable_virus_scan=False,
        )

        config2 = SecurityConfig(
            enable_integrity_check=False,
            enable_virus_scan=False,
        )

        config3 = SecurityConfig(
            enable_integrity_check=True,
            enable_virus_scan=False,
        )

        assert config1 == config2
        assert config1 != config3
        assert config1 != "not a config"


class TestLoggingConfig:
    """Test suite for LoggingConfig."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        config = LoggingConfig()

        assert config.log_level == DEFAULT_LOGGING_CONFIG.log_level
        assert config.log_file_path == DEFAULT_LOGGING_CONFIG.log_file_path
        assert (
            config.enable_console_logging
            == DEFAULT_LOGGING_CONFIG.enable_console_logging
        )
        assert config.enable_file_logging == DEFAULT_LOGGING_CONFIG.enable_file_logging
        assert config.log_format == DEFAULT_LOGGING_CONFIG.log_format
        assert config.date_format == DEFAULT_LOGGING_CONFIG.date_format

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        custom_config = LoggingConfig(
            log_level="DEBUG",
            log_file_path="custom_logs/app.log",
            enable_console_logging=False,
            enable_file_logging=True,
            log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            date_format="%Y-%m-%d %H:%M:%S",
        )

        assert custom_config.log_level == "DEBUG"
        assert custom_config.log_file_path == "custom_logs/app.log"
        assert custom_config.enable_console_logging is False
        assert custom_config.enable_file_logging is True
        assert (
            custom_config.log_format
            == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        assert custom_config.date_format == "%Y-%m-%d %H:%M:%S"

    def test_validation(self):
        """Test validation rules for LoggingConfig."""
        # Invalid log_level
        with pytest.raises(ValueError):
            LoggingConfig(log_level="INVALID_LEVEL")

        # Invalid log_file_path (empty string when file logging is enabled)
        with pytest.raises(ValueError):
            LoggingConfig(log_file_path="", enable_file_logging=True)

        # Invalid log_format (empty string)
        with pytest.raises(ValueError):
            LoggingConfig(log_format="")

        # Invalid date_format (empty string)
        with pytest.raises(ValueError):
            LoggingConfig(date_format="")

    def test_from_dict(self):
        """Test creation from dictionary."""
        config_dict = {
            "log_level": "DEBUG",
            "log_file_path": "custom_logs/app.log",
            "enable_console_logging": False,
            "enable_file_logging": True,
            "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S",
        }

        config = LoggingConfig.from_dict(config_dict)

        assert config.log_level == "DEBUG"
        assert config.log_file_path == "custom_logs/app.log"
        assert config.enable_console_logging is False
        assert config.enable_file_logging is True
        assert (
            config.log_format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        assert config.date_format == "%Y-%m-%d %H:%M:%S"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = LoggingConfig(
            log_level="DEBUG",
            log_file_path="custom_logs/app.log",
            enable_console_logging=False,
            enable_file_logging=True,
            log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            date_format="%Y-%m-%d %H:%M:%S",
        )

        config_dict = config.to_dict()

        assert config_dict["log_level"] == "DEBUG"
        assert config_dict["log_file_path"] == "custom_logs/app.log"
        assert config_dict["enable_console_logging"] is False
        assert config_dict["enable_file_logging"] is True
        assert (
            config_dict["log_format"]
            == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        assert config_dict["date_format"] == "%Y-%m-%d %H:%M:%S"

    def test_equality(self):
        """Test equality comparison."""
        config1 = LoggingConfig(
            log_level="DEBUG",
            log_file_path="custom_logs/app.log",
        )

        config2 = LoggingConfig(
            log_level="DEBUG",
            log_file_path="custom_logs/app.log",
        )

        config3 = LoggingConfig(
            log_level="INFO",
            log_file_path="custom_logs/app.log",
        )

        assert config1 == config2
        assert config1 != config3
        assert config1 != "not a config"


class TestConfigFileOperations:
    """Test suite for config file operations."""

    def setup_method(self):
        """Set up the test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "config.json"

    def teardown_method(self):
        """Clean up the test environment."""
        self.temp_dir.cleanup()

    @patch("json.dump")
    def test_save_config(self, mock_dump):
        """Test saving configuration to a file."""
        # Create test configs
        processing_config = ProcessingConfig(max_video_duration_seconds=600)
        video_config = VideoConfig(upload_dir="custom_uploads")
        ai_model_config = AIModelConfig(openai_api_key="custom_key")
        storage_config = StorageConfig(vector_dimension=512)
        security_config = SecurityConfig(enable_virus_scan=False)
        logging_config = LoggingConfig(log_level="DEBUG")

        # Call save_config
        save_config(
            self.config_path,
            processing_config=processing_config,
            video_config=video_config,
            ai_model_config=ai_model_config,
            storage_config=storage_config,
            security_config=security_config,
            logging_config=logging_config,
        )

        # Verify that json.dump was called with the correct arguments
        mock_dump.assert_called_once()
        args, kwargs = mock_dump.call_args
        config_dict = args[0]

        assert config_dict["processing"]["max_video_duration_seconds"] == 600
        assert config_dict["video"]["upload_dir"] == "custom_uploads"
        assert config_dict["ai_model"]["openai_api_key"] == "custom_key"
        assert config_dict["storage"]["vector_dimension"] == 512
        assert config_dict["security"]["enable_virus_scan"] is False
        assert config_dict["logging"]["log_level"] == "DEBUG"

    @patch("json.load")
    @patch("os.path.exists")
    def test_load_config(self, mock_exists, mock_load):
        """Test loading configuration from a file."""
        # Set up mocks
        mock_exists.return_value = True
        mock_load.return_value = {
            "processing": {
                "max_video_duration_seconds": 600,
                "max_video_file_size_mb": 500,
            },
            "video": {
                "upload_dir": "custom_uploads",
                "temp_dir": "custom_temp",
            },
            "ai_model": {
                "openai_api_key": "custom_key",
                "openai_model": "gpt-4-vision-custom",
            },
            "storage": {
                "vector_dimension": 512,
                "max_cache_size_mb": 2048,
            },
            "security": {
                "enable_virus_scan": False,
                "max_requests_per_minute": 30,
            },
            "logging": {
                "log_level": "DEBUG",
                "enable_console_logging": False,
            },
        }

        # Call load_config
        configs = load_config(self.config_path)

        # Verify the returned configs
        processing_config = configs["processing"]
        video_config = configs["video"]
        ai_model_config = configs["ai_model"]
        storage_config = configs["storage"]
        security_config = configs["security"]
        logging_config = configs["logging"]

        assert processing_config.max_video_duration_seconds == 600
        assert processing_config.max_video_file_size_mb == 500

        assert video_config.upload_dir == "custom_uploads"
        assert video_config.temp_dir == "custom_temp"

        assert ai_model_config.openai_api_key == "custom_key"
        assert ai_model_config.openai_model == "gpt-4-vision-custom"

        assert storage_config.vector_dimension == 512
        assert storage_config.max_cache_size_mb == 2048

        assert security_config.enable_virus_scan is False
        assert security_config.max_requests_per_minute == 30

        assert logging_config.log_level == "DEBUG"
        assert logging_config.enable_console_logging is False

    @patch("os.path.exists")
    def test_load_config_defaults(self, mock_exists):
        """Test loading default configuration when file doesn't exist."""
        # Set up mock
        mock_exists.return_value = False

        # Call load_config
        configs = load_config(self.config_path)

        # Verify default configs are returned
        assert configs["processing"] == DEFAULT_PROCESSING_CONFIG
        assert configs["video"] == DEFAULT_VIDEO_CONFIG
        assert configs["ai_model"] == DEFAULT_AI_MODEL_CONFIG
        assert configs["storage"] == DEFAULT_STORAGE_CONFIG
        assert configs["security"] == DEFAULT_SECURITY_CONFIG
        assert configs["logging"] == DEFAULT_LOGGING_CONFIG
