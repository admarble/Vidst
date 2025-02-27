"""Configuration management for vector storage.

This module provides configuration management for vector storage, including
loading from environment variables, validation, and serialization.
"""

import os
from os import _Environ
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Dict, Optional, Union, cast

from .exceptions import ConfigurationError
from .utils import wrap_errors

@dataclass(frozen=True)
class VectorStorageConfig:
    """Configuration for vector storage.

    This is an immutable configuration class that handles all settings for
    vector storage. It supports loading from environment variables and includes
    validation of all settings.

    Attributes:
        dimension: Dimensionality of vectors to store
        index_type: Type of FAISS index to use (e.g., "flat", "hnsw")
        index_path: Path to save/load the FAISS index
        metadata_path: Path to save/load metadata
        similarity_threshold: Minimum similarity score for matches
        max_vectors: Maximum number of vectors to store
        cache_size_bytes: Size of cache in bytes
        auto_save: Whether to auto-save after modifications
    """

    # Required parameters
    dimension: int
    index_path: Path
    metadata_path: Path

    # Optional parameters with defaults
    index_type: str = "flat"
    similarity_threshold: float = 0.8
    max_vectors: int = 1_000_000
    cache_size_bytes: int = 1024 * 1024 * 1024  # 1GB
    auto_save: bool = True

    # Environment variable mappings
    ENV_MAPPINGS: ClassVar[Dict[str, str]] = {
        "dimension": "VECTOR_STORAGE_DIMENSION",
        "index_type": "VECTOR_STORAGE_INDEX_TYPE",
        "index_path": "VECTOR_STORAGE_INDEX_PATH",
        "metadata_path": "VECTOR_STORAGE_METADATA_PATH",
        "similarity_threshold": "VECTOR_STORAGE_SIMILARITY_THRESHOLD",
        "max_vectors": "VECTOR_STORAGE_MAX_VECTORS",
        "cache_size_bytes": "VECTOR_STORAGE_CACHE_SIZE_BYTES",
        "auto_save": "VECTOR_STORAGE_AUTO_SAVE",
    }

    # Validation settings
    VALID_INDEX_TYPES: ClassVar[set[str]] = {"flat", "hnsw", "ivf"}
    MIN_DIMENSION: ClassVar[int] = 1
    MAX_DIMENSION: ClassVar[int] = 10000
    MIN_SIMILARITY: ClassVar[float] = 0.0
    MAX_SIMILARITY: ClassVar[float] = 1.0
    MIN_CACHE_SIZE: ClassVar[int] = 1024 * 1024  # 1MB

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self.validate()

    @wrap_errors(ConfigurationError)
    def validate(self) -> None:
        """Validate all configuration settings.

        Raises:
            ConfigurationError: If any setting is invalid
        """
        # Validate dimension
        if not isinstance(self.dimension, int):
            raise ConfigurationError("Dimension must be an integer")
        if not self.MIN_DIMENSION <= self.dimension <= self.MAX_DIMENSION:
            raise ConfigurationError(
                f"Dimension must be between {self.MIN_DIMENSION} "
                f"and {self.MAX_DIMENSION}"
            )

        # Validate index type
        if self.index_type not in self.VALID_INDEX_TYPES:
            raise ConfigurationError(
                f"Invalid index type. Must be one of: {self.VALID_INDEX_TYPES}"
            )

        # Validate paths
        if not isinstance(self.index_path, Path):
            raise ConfigurationError("Index path must be a Path object")
        if not isinstance(self.metadata_path, Path):
            raise ConfigurationError("Metadata path must be a Path object")

        # Validate similarity threshold
        if not isinstance(self.similarity_threshold, float):
            raise ConfigurationError("Similarity threshold must be a float")
        if not self.MIN_SIMILARITY <= self.similarity_threshold <= self.MAX_SIMILARITY:
            raise ConfigurationError(
                f"Similarity threshold must be between "
                f"{self.MIN_SIMILARITY} and {self.MAX_SIMILARITY}"
            )

        # Validate max vectors
        if not isinstance(self.max_vectors, int) or self.max_vectors <= 0:
            raise ConfigurationError("Max vectors must be a positive integer")

        # Validate cache size
        if not isinstance(self.cache_size_bytes, int):
            raise ConfigurationError("Cache size must be an integer")
        if self.cache_size_bytes < self.MIN_CACHE_SIZE:
            raise ConfigurationError(
                f"Cache size must be at least {self.MIN_CACHE_SIZE} bytes"
            )

        # Validate auto save
        if not isinstance(self.auto_save, bool):
            raise ConfigurationError("Auto save must be a boolean")

    @classmethod
    def from_env(cls, env: Optional[Union[Dict[str, str], _Environ[str]]] = None) -> "VectorStorageConfig":
        """Create configuration from environment variables.

        Args:
            env: Optional environment dictionary (uses os.environ if None)

        Returns:
            New configuration instance

        Raises:
            ConfigurationError: If required variables are missing or invalid
        """
        env_dict = os.environ if env is None else env
        config_dict: Dict[str, Any] = {}

        for attr, env_var in cls.ENV_MAPPINGS.items():
            if env_var in env_dict:
                value = env_dict[env_var]
                if attr in {"index_path", "metadata_path"}:
                    config_dict[attr] = Path(value)
                elif attr in {"dimension", "max_vectors", "cache_size_bytes"}:
                    config_dict[attr] = int(value)
                elif attr == "similarity_threshold":
                    config_dict[attr] = float(value)
                elif attr == "auto_save":
                    config_dict[attr] = value.lower() in {"true", "1", "yes"}
                else:
                    config_dict[attr] = value

        try:
            return cls(**config_dict)
        except TypeError as e:
            raise ConfigurationError(f"Missing required configuration: {e}") from e

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            "dimension": self.dimension,
            "index_type": self.index_type,
            "index_path": str(self.index_path),
            "metadata_path": str(self.metadata_path),
            "similarity_threshold": self.similarity_threshold,
            "max_vectors": self.max_vectors,
            "cache_size_bytes": self.cache_size_bytes,
            "auto_save": self.auto_save,
        }

    def to_json(self) -> str:
        """Convert configuration to JSON string.

        Returns:
            JSON string representation of configuration
        """
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VectorStorageConfig":
        """Create configuration from dictionary.

        Args:
            data: Dictionary containing configuration

        Returns:
            New configuration instance

        Raises:
            ConfigurationError: If dictionary is invalid
        """
        try:
            # Convert path strings to Path objects
            if "index_path" in data:
                data["index_path"] = Path(data["index_path"])
            if "metadata_path" in data:
                data["metadata_path"] = Path(data["metadata_path"])
            return cls(**data)
        except (TypeError, ValueError) as e:
            raise ConfigurationError(f"Invalid configuration data: {e}") from e

    @classmethod
    def from_json(cls, json_str: str) -> "VectorStorageConfig":
        """Create configuration from JSON string.

        Args:
            json_str: JSON string containing configuration

        Returns:
            New configuration instance

        Raises:
            ConfigurationError: If JSON is invalid
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON: {e}") from e
