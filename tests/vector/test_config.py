"""Tests for vector storage configuration."""

import json
from pathlib import Path
import pytest

from video_understanding.storage.vector.config import VectorStorageConfig
from video_understanding.storage.vector.exceptions import ConfigurationError

def test_config_creation(config: VectorStorageConfig) -> None:
    """Test configuration creation with valid parameters."""
    assert config.dimension == 768
    assert config.index_type == "flat"
    assert isinstance(config.index_path, Path)
    assert isinstance(config.metadata_path, Path)
    assert config.similarity_threshold == 0.8
    assert config.max_vectors == 1000
    assert config.cache_size_bytes == 1024 * 1024
    assert config.auto_save is True

def test_config_validation() -> None:
    """Test configuration validation."""
    # Test invalid dimension
    with pytest.raises(ConfigurationError, match="Dimension must be"):
        VectorStorageConfig(
            dimension=-1,
            index_path=Path("test.faiss"),
            metadata_path=Path("test.json")
        )

    # Test invalid index type
    with pytest.raises(ConfigurationError, match="Invalid index type"):
        VectorStorageConfig(
            dimension=768,
            index_path=Path("test.faiss"),
            metadata_path=Path("test.json"),
            index_type="invalid"
        )

    # Test invalid similarity threshold
    with pytest.raises(ConfigurationError, match="Similarity threshold"):
        VectorStorageConfig(
            dimension=768,
            index_path=Path("test.faiss"),
            metadata_path=Path("test.json"),
            similarity_threshold=2.0
        )

    # Test invalid max vectors
    with pytest.raises(ConfigurationError, match="Max vectors"):
        VectorStorageConfig(
            dimension=768,
            index_path=Path("test.faiss"),
            metadata_path=Path("test.json"),
            max_vectors=0
        )

    # Test invalid cache size
    with pytest.raises(ConfigurationError, match="Cache size"):
        VectorStorageConfig(
            dimension=768,
            index_path=Path("test.faiss"),
            metadata_path=Path("test.json"),
            cache_size_bytes=0
        )

def test_config_from_env(env_vars: None) -> None:
    """Test configuration loading from environment variables."""
    config = VectorStorageConfig.from_env()
    assert config.dimension == 768
    assert config.index_type == "flat"
    assert config.similarity_threshold == 0.8
    assert config.max_vectors == 1000
    assert config.cache_size_bytes == 1048576
    assert config.auto_save is True

def test_config_from_env_missing() -> None:
    """Test configuration loading with missing environment variables."""
    with pytest.raises(ConfigurationError, match="Missing required configuration"):
        VectorStorageConfig.from_env({})

def test_config_serialization(config: VectorStorageConfig) -> None:
    """Test configuration serialization and deserialization."""
    # Test to_dict
    config_dict = config.to_dict()
    assert config_dict["dimension"] == 768
    assert config_dict["index_type"] == "flat"
    assert isinstance(config_dict["index_path"], str)
    assert isinstance(config_dict["metadata_path"], str)

    # Test from_dict
    new_config = VectorStorageConfig.from_dict(config_dict)
    assert new_config == config

    # Test to_json
    config_json = config.to_json()
    assert isinstance(config_json, str)
    parsed = json.loads(config_json)
    assert parsed["dimension"] == 768

    # Test from_json
    new_config = VectorStorageConfig.from_json(config_json)
    assert new_config == config

def test_config_immutability(config: VectorStorageConfig) -> None:
    """Test configuration immutability."""
    with pytest.raises(Exception):  # Frozen dataclass prevents modification
        config.dimension = 512  # type: ignore

def test_config_hash(config: VectorStorageConfig) -> None:
    """Test configuration hash and equality."""
    config2 = VectorStorageConfig(
        dimension=config.dimension,
        index_path=config.index_path,
        metadata_path=config.metadata_path,
        index_type=config.index_type,
        similarity_threshold=config.similarity_threshold,
        max_vectors=config.max_vectors,
        cache_size_bytes=config.cache_size_bytes,
        auto_save=config.auto_save
    )
    assert hash(config) == hash(config2)
    assert config == config2

def test_config_invalid_paths() -> None:
    """Test configuration with invalid paths."""
    with pytest.raises(ConfigurationError, match="Index path"):
        VectorStorageConfig(
            dimension=768,
            index_path="not a path",  # type: ignore
            metadata_path=Path("test.json")
        )

    with pytest.raises(ConfigurationError, match="Metadata path"):
        VectorStorageConfig(
            dimension=768,
            index_path=Path("test.faiss"),
            metadata_path="not a path"  # type: ignore
        )

def test_config_default_values(temp_dir: Path) -> None:
    """Test configuration default values."""
    config = VectorStorageConfig(
        dimension=768,
        index_path=temp_dir / "index.faiss",
        metadata_path=temp_dir / "metadata.json"
    )
    assert config.index_type == "flat"
    assert config.similarity_threshold == 0.8
    assert config.max_vectors == 1_000_000
    assert config.cache_size_bytes == 1024 * 1024 * 1024
    assert config.auto_save is True
