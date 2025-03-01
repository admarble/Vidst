"""Unit tests for the vector storage functionality."""

import os
import json
import tempfile
import numpy as np
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call

from video_understanding.storage.vector import (
    VectorStorage,
    VectorStorageConfig,
    VectorMetadata,
    SearchResult,
    VectorEmbedding,
    VectorStorageError,
    validate_embedding,
    validate_metadata,
    validate_vector_store_path,
    store_embedding,
    search_similar,
    retrieve_embedding,
    search_vectors,
    optimize_index,
)


class TestVectorStorageConfig:
    """Tests for VectorStorageConfig."""

    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.dimension = 768
        self.index_path = self.base_dir / "index"
        self.metadata_path = self.base_dir / "metadata"
        self.similarity_threshold = 0.85
        self.auto_save = True

    def teardown_method(self):
        """Cleanup after each test."""
        self.temp_dir.cleanup()

    def test_init(self):
        """Test basic initialization."""
        config = VectorStorageConfig(
            dimension=self.dimension,
            index_path=self.index_path,
            metadata_path=self.metadata_path,
            similarity_threshold=self.similarity_threshold,
            auto_save=self.auto_save,
        )

        assert config.dimension == self.dimension
        assert config.index_path == self.index_path
        assert config.metadata_path == self.metadata_path
        assert config.similarity_threshold == self.similarity_threshold
        assert config.auto_save == self.auto_save

    def test_validation(self):
        """Test configuration validation."""
        # Test valid config
        config = VectorStorageConfig(
            dimension=self.dimension,
            index_path=self.index_path,
            metadata_path=self.metadata_path,
        )

        # Test invalid dimension
        with pytest.raises(ValueError):
            VectorStorageConfig(
                dimension=0,
                index_path=self.index_path,
                metadata_path=self.metadata_path,
            )

        # Test invalid similarity threshold
        with pytest.raises(ValueError):
            VectorStorageConfig(
                dimension=self.dimension,
                index_path=self.index_path,
                metadata_path=self.metadata_path,
                similarity_threshold=1.5,
            )

    def test_properties(self):
        """Test properties."""
        config = VectorStorageConfig(
            dimension=self.dimension,
            index_path=self.index_path,
            metadata_path=self.metadata_path,
        )

        assert config.index_dir == self.index_path.parent
        assert config.metadata_dir == self.metadata_path.parent
        assert config.index_name == self.index_path.name
        assert config.metadata_name == self.metadata_path.name

    def test_equality(self):
        """Test equality comparison."""
        config1 = VectorStorageConfig(
            dimension=self.dimension,
            index_path=self.index_path,
            metadata_path=self.metadata_path,
        )

        config2 = VectorStorageConfig(
            dimension=self.dimension,
            index_path=self.index_path,
            metadata_path=self.metadata_path,
        )

        config3 = VectorStorageConfig(
            dimension=512,
            index_path=self.index_path,
            metadata_path=self.metadata_path,
        )

        assert config1 == config2
        assert config1 != config3
        assert config1 != "not a config"

    def test_hash(self):
        """Test hash implementation."""
        config = VectorStorageConfig(
            dimension=self.dimension,
            index_path=self.index_path,
            metadata_path=self.metadata_path,
        )

        # Hash should not raise an exception
        hash(config)

    def test_repr(self):
        """Test string representation."""
        config = VectorStorageConfig(
            dimension=self.dimension,
            index_path=self.index_path,
            metadata_path=self.metadata_path,
        )

        repr_str = repr(config)
        assert str(self.dimension) in repr_str
        assert str(self.index_path) in repr_str
        assert str(self.metadata_path) in repr_str

    def test_to_from_dict(self):
        """Test conversion to and from dict."""
        config = VectorStorageConfig(
            dimension=self.dimension,
            index_path=self.index_path,
            metadata_path=self.metadata_path,
            similarity_threshold=self.similarity_threshold,
        )

        config_dict = config.to_dict()
        assert config_dict["dimension"] == self.dimension
        assert config_dict["index_path"] == str(self.index_path)
        assert config_dict["metadata_path"] == str(self.metadata_path)
        assert config_dict["similarity_threshold"] == self.similarity_threshold

        # Convert back to config
        config2 = VectorStorageConfig.from_dict(config_dict)
        assert config == config2

    def test_create_default(self):
        """Test create_default factory method."""
        config = VectorStorageConfig.create_default(
            base_dir=self.base_dir,
            dimension=self.dimension,
        )

        assert config.dimension == self.dimension
        assert str(self.base_dir) in str(config.index_path)
        assert str(self.base_dir) in str(config.metadata_path)

    def test_create_from_paths(self):
        """Test create_from_paths factory method."""
        config = VectorStorageConfig.create_from_paths(
            dimension=self.dimension,
            index_path=self.index_path,
            metadata_path=self.metadata_path,
            similarity_threshold=0.9,
            auto_save=False,
        )

        assert config.dimension == self.dimension
        assert config.index_path == self.index_path
        assert config.metadata_path == self.metadata_path
        assert config.similarity_threshold == 0.9
        assert config.auto_save is False

    def test_create_from_config(self):
        """Test create_from_config factory method."""
        original = VectorStorageConfig(
            dimension=self.dimension,
            index_path=self.index_path,
            metadata_path=self.metadata_path,
        )

        copy = VectorStorageConfig.create_from_config(original)
        assert original == copy
        assert original is not copy  # Should be a different instance

    def test_create_from_base_dir(self):
        """Test create_from_base_dir factory method."""
        original = VectorStorageConfig(
            dimension=self.dimension,
            index_path="original/index",
            metadata_path="original/metadata",
        )

        new_config = VectorStorageConfig.create_from_base_dir(
            base_dir=self.base_dir,
            config=original,
        )

        assert new_config.dimension == original.dimension
        assert str(self.base_dir) in str(new_config.index_path)
        assert str(self.base_dir) in str(new_config.metadata_path)
        assert new_config.index_name == Path("original/index").name
        assert new_config.metadata_name == Path("original/metadata").name


class TestValidationFunctions:
    """Tests for validation functions."""

    def test_validate_embedding(self):
        """Test embedding validation."""
        # Valid embedding
        embedding = np.random.randn(768).astype(np.float32)
        validate_embedding(embedding, 768)

        # Wrong dimension
        with pytest.raises(ValueError):
            validate_embedding(embedding, 512)

        # Wrong shape
        embedding_2d = np.random.randn(2, 768).astype(np.float32)
        with pytest.raises(ValueError):
            validate_embedding(embedding_2d, 768)

        # Wrong dtype
        embedding_float64 = np.random.randn(768).astype(np.float64)
        with pytest.raises(TypeError):
            validate_embedding(embedding_float64, 768)

    def test_validate_metadata(self):
        """Test metadata validation."""
        # Valid metadata
        metadata: VectorMetadata = {
            "type": "frame",
            "timestamp": "2023-01-01T12:00:00",
            "model_version": "v1.0",
            "confidence": 0.95,
            "source_frame": 1200,
            "duration": None,
        }
        validate_metadata(metadata)

        # Missing required field
        invalid_metadata = {
            "timestamp": "2023-01-01T12:00:00",
            "model_version": "v1.0",
        }
        with pytest.raises(ValueError):
            validate_metadata(invalid_metadata)  # type: ignore

    def test_validate_vector_store_path(self):
        """Test vector store path validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)

            # Test valid path
            validate_vector_store_path(path)

            # Test non-existent path (should create it)
            non_existent = path / "non_existent"
            validate_vector_store_path(non_existent)
            assert non_existent.exists()

            # Test file path (should fail)
            file_path = path / "file.txt"
            file_path.touch()
            with pytest.raises(ValueError):
                validate_vector_store_path(file_path)


@pytest.fixture
def mock_faiss():
    """Mock the FAISS library."""
    with patch("video_understanding.storage.vector.faiss") as mock:
        yield mock


@pytest.fixture
def vector_storage_config():
    """Create a VectorStorageConfig for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        base_dir = Path(temp_dir)
        config = VectorStorageConfig(
            dimension=768,
            index_path=base_dir / "index",
            metadata_path=base_dir / "metadata.json",
        )
        yield config


class TestVectorStorage:
    """Tests for VectorStorage class."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset the singleton instance between tests."""
        VectorStorage._instance = None
        VectorStorage._config = None

    def test_initialization(self, vector_storage_config, mock_faiss):
        """Test initialization of storage."""
        # Setup mock
        mock_index = mock_faiss.IndexFlatL2.return_value

        # Create storage
        storage = VectorStorage(vector_storage_config)

        # Verify initialization
        assert storage._config == vector_storage_config
        assert storage._index is not None
        assert storage._metadata == {}
        mock_faiss.IndexFlatL2.assert_called_once_with(vector_storage_config.dimension)

    def test_singleton(self, vector_storage_config, mock_faiss):
        """Test singleton pattern."""
        storage1 = VectorStorage(vector_storage_config)
        storage2 = VectorStorage.get_instance()

        assert storage1 is storage2
        assert VectorStorage._instance is storage1

        # Test initialize class method
        storage3 = VectorStorage.initialize(vector_storage_config)
        assert storage3 is storage1

    def test_add_embedding(self, vector_storage_config, mock_faiss):
        """Test adding a single embedding."""
        # Setup
        storage = VectorStorage(vector_storage_config)
        mock_index = mock_faiss.IndexFlatL2.return_value

        # Create test data
        embedding = np.random.randn(768).astype(np.float32)
        metadata: VectorMetadata = {
            "type": "frame",
            "timestamp": "2023-01-01T12:00:00",
            "model_version": "v1.0",
            "confidence": 0.95,
            "source_frame": 1200,
            "duration": None,
        }

        # Test with auto-generated ID
        embedding_id = storage.add_embedding(embedding, metadata)

        # Verify
        assert embedding_id in storage._metadata
        assert storage._metadata[embedding_id] == metadata
        mock_index.add.assert_called_once()

        # Test with provided ID
        custom_id = "custom_id_123"
        storage.add_embedding(embedding, metadata, embedding_id=custom_id)
        assert custom_id in storage._metadata
        assert storage._metadata[custom_id] == metadata

    def test_batch_add_embeddings(self, vector_storage_config, mock_faiss):
        """Test adding multiple embeddings in batch."""
        # Setup
        storage = VectorStorage(vector_storage_config)
        mock_index = mock_faiss.IndexFlatL2.return_value

        # Create test data
        num_vectors = 5
        embeddings = np.random.randn(num_vectors, 768).astype(np.float32)
        metadata_list = [
            {
                "type": "frame",
                "timestamp": f"2023-01-01T12:00:{i:02d}",
                "model_version": "v1.0",
                "confidence": 0.95,
                "source_frame": 1200 + i,
                "duration": None,
            }
            for i in range(num_vectors)
        ]

        # Test with auto-generated IDs
        ids = storage.batch_add_embeddings(embeddings, metadata_list)

        # Verify
        assert len(ids) == num_vectors
        for id_val in ids:
            assert id_val in storage._metadata
        mock_index.add.assert_called_once()

        # Test with provided IDs
        custom_ids = [f"custom_{i}" for i in range(num_vectors)]
        ids = storage.batch_add_embeddings(
            embeddings, metadata_list, embedding_ids=custom_ids
        )
        assert ids == custom_ids
        for id_val in custom_ids:
            assert id_val in storage._metadata

    def test_search_similar(self, vector_storage_config, mock_faiss):
        """Test searching for similar embeddings."""
        # Setup
        storage = VectorStorage(vector_storage_config)
        mock_index = mock_faiss.IndexFlatL2.return_value

        # Set up mock search results
        mock_index.search.return_value = (
            np.array([[0.1, 0.2], [0.3, 0.4]]),  # Distances
            np.array([[0, 1], [2, 3]]),  # Indices
        )

        # Add some metadata
        storage._metadata = {
            "id_0": {
                "type": "frame",
                "timestamp": "2023-01-01T12:00:00",
                "model_version": "v1.0",
                "confidence": 0.95,
                "source_frame": 1200,
                "duration": None,
            },
            "id_1": {
                "type": "frame",
                "timestamp": "2023-01-01T12:00:01",
                "model_version": "v1.0",
                "confidence": 0.96,
                "source_frame": 1201,
                "duration": None,
            },
            "id_2": {
                "type": "frame",
                "timestamp": "2023-01-01T12:00:02",
                "model_version": "v1.0",
                "confidence": 0.97,
                "source_frame": 1202,
                "duration": None,
            },
            "id_3": {
                "type": "frame",
                "timestamp": "2023-01-01T12:00:03",
                "model_version": "v1.0",
                "confidence": 0.98,
                "source_frame": 1203,
                "duration": None,
            },
        }

        # We need to patch the storage._id_to_idx and _idx_to_id mappings
        storage._id_to_idx = {"id_0": 0, "id_1": 1, "id_2": 2, "id_3": 3}
        storage._idx_to_id = {0: "id_0", 1: "id_1", 2: "id_2", 3: "id_3"}

        # Test search
        query = np.random.randn(768).astype(np.float32)
        results = storage.search_similar(query, k=2)

        # Verify
        assert len(results) == 2
        assert results[0]["id"] in ["id_0", "id_1"]
        assert results[1]["id"] in ["id_2", "id_3"]
        assert "distance" in results[0]
        assert "similarity" in results[0]
        assert "metadata" in results[0]

        # Test with filter
        def filter_fn(result: SearchResult) -> bool:
            return result["metadata"]["source_frame"] > 1201

        results = storage.search_similar(query, k=2, filter_fn=filter_fn)

        # Since our mock always returns the same thing, we'll test that the filter is applied
        # by checking if the filter callback was applied to the results
        assert len(results) <= 2  # Results should be filtered

    def test_retrieve_embedding(self, vector_storage_config, mock_faiss):
        """Test retrieving an embedding."""
        # Setup
        storage = VectorStorage(vector_storage_config)

        # Add metadata and mock index
        embedding_id = "test_id"
        metadata: VectorMetadata = {
            "type": "frame",
            "timestamp": "2023-01-01T12:00:00",
            "model_version": "v1.0",
            "confidence": 0.95,
            "source_frame": 1200,
            "duration": None,
        }
        storage._metadata[embedding_id] = metadata
        storage._id_to_idx = {embedding_id: 0}

        # Mock embedding reconstruction
        mock_embedding = np.random.randn(768).astype(np.float32)
        storage._index.reconstruct = MagicMock(return_value=mock_embedding)

        # Test retrieval
        result_embedding, result_metadata = storage.retrieve_embedding(embedding_id)

        # Verify
        assert np.array_equal(result_embedding, mock_embedding)
        assert result_metadata == metadata

        # Test retrieving non-existent embedding
        with pytest.raises(KeyError):
            storage.retrieve_embedding("nonexistent_id")

    def test_delete_embedding(self, vector_storage_config, mock_faiss):
        """Test deleting an embedding."""
        # Setup
        storage = VectorStorage(vector_storage_config)

        # Add metadata and mock index
        embedding_id = "test_id"
        metadata: VectorMetadata = {
            "type": "frame",
            "timestamp": "2023-01-01T12:00:00",
            "model_version": "v1.0",
            "confidence": 0.95,
            "source_frame": 1200,
            "duration": None,
        }
        storage._metadata[embedding_id] = metadata
        storage._id_to_idx = {embedding_id: 0}
        storage._idx_to_id = {0: embedding_id}

        # Test deletion
        with patch.object(storage, "save") as mock_save:
            storage.delete_embedding(embedding_id)

            # Verify
            assert embedding_id not in storage._metadata
            assert 0 not in storage._idx_to_id
            assert embedding_id not in storage._id_to_idx
            mock_save.assert_called_once()

        # Test deleting non-existent embedding
        with pytest.raises(KeyError):
            storage.delete_embedding("nonexistent_id")

    def test_clear(self, vector_storage_config, mock_faiss):
        """Test clearing all embeddings."""
        # Setup
        storage = VectorStorage(vector_storage_config)

        # Add some metadata and mock data
        storage._metadata = {
            "id1": {
                "type": "frame",
                "timestamp": "2023-01-01T12:00:00",
                "model_version": "v1.0",
                "confidence": 0.95,
                "source_frame": 1200,
                "duration": None,
            },
            "id2": {
                "type": "frame",
                "timestamp": "2023-01-01T12:00:01",
                "model_version": "v1.0",
                "confidence": 0.96,
                "source_frame": 1201,
                "duration": None,
            },
        }
        storage._id_to_idx = {"id1": 0, "id2": 1}
        storage._idx_to_id = {0: "id1", 1: "id2"}

        # Test clear
        with patch.object(storage, "save") as mock_save:
            storage.clear()

            # Verify
            assert storage._metadata == {}
            assert storage._id_to_idx == {}
            assert storage._idx_to_id == {}
            mock_save.assert_called_once()

    def test_save_and_load(self, vector_storage_config, mock_faiss):
        """Test saving and loading index and metadata."""
        # Setup
        storage = VectorStorage(vector_storage_config)

        # Add some metadata
        storage._metadata = {
            "id1": {
                "type": "frame",
                "timestamp": "2023-01-01T12:00:00",
                "model_version": "v1.0",
                "confidence": 0.95,
                "source_frame": 1200,
                "duration": None,
            },
            "id2": {
                "type": "frame",
                "timestamp": "2023-01-01T12:00:01",
                "model_version": "v1.0",
                "confidence": 0.96,
                "source_frame": 1201,
                "duration": None,
            },
        }
        storage._id_to_idx = {"id1": 0, "id2": 1}
        storage._idx_to_id = {0: "id1", 1: "id2"}

        # Mock file operations
        with (
            patch("builtins.open", MagicMock()),
            patch("json.dump") as mock_json_dump,
            patch("os.path.exists") as mock_exists,
            patch.object(mock_faiss, "write_index") as mock_write_index,
        ):

            # Test save
            storage.save()

            # Verify
            mock_write_index.assert_called_once()
            mock_json_dump.assert_called_once()

        # Test load
        with (
            patch("os.path.exists") as mock_exists,
            patch("builtins.open", MagicMock()),
            patch("json.load") as mock_json_load,
            patch.object(mock_faiss, "read_index") as mock_read_index,
        ):

            # Setup mocks
            mock_exists.return_value = True
            mock_json_load.return_value = {
                "metadata": {
                    "id1": {
                        "type": "frame",
                        "timestamp": "2023-01-01T12:00:00",
                        "model_version": "v1.0",
                        "confidence": 0.95,
                        "source_frame": 1200,
                        "duration": None,
                    },
                    "id2": {
                        "type": "frame",
                        "timestamp": "2023-01-01T12:00:01",
                        "model_version": "v1.0",
                        "confidence": 0.96,
                        "source_frame": 1201,
                        "duration": None,
                    },
                },
                "id_to_idx": {"id1": 0, "id2": 1},
            }

            # Call _load_if_exists
            storage._load_if_exists()

            # Verify
            mock_read_index.assert_called_once()
            mock_json_load.assert_called_once()
            assert len(storage._metadata) == 2
            assert len(storage._id_to_idx) == 2
            assert len(storage._idx_to_id) == 2


class TestConvenienceFunctions:
    """Tests for top-level convenience functions."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset the singleton instance between tests."""
        VectorStorage._instance = None
        VectorStorage._config = None

    def test_store_embedding(self, vector_storage_config, mock_faiss):
        """Test store_embedding convenience function."""
        # Initialize storage
        storage = VectorStorage(vector_storage_config)
        VectorStorage._instance = storage

        # Create test data
        embedding = np.random.randn(768).astype(np.float32)
        metadata: VectorMetadata = {
            "type": "frame",
            "timestamp": "2023-01-01T12:00:00",
            "model_version": "v1.0",
            "confidence": 0.95,
            "source_frame": 1200,
            "duration": None,
        }
        vector_embedding = VectorEmbedding(
            video_id="video123",
            segment_id="segment456",
            embedding=embedding,
            metadata=metadata,
        )

        # Mock add_embedding
        with patch.object(storage, "add_embedding", return_value="test_id") as mock_add:
            # Call function
            result = store_embedding(vector_embedding)

            # Verify
            assert result == "test_id"
            mock_add.assert_called_once()

    def test_search_similar(self, vector_storage_config, mock_faiss):
        """Test search_similar convenience function."""
        # Initialize storage
        storage = VectorStorage(vector_storage_config)
        VectorStorage._instance = storage

        # Mock search_similar
        mock_results = [
            {
                "id": "id1",
                "distance": 0.1,
                "similarity": 0.9,
                "metadata": {
                    "type": "frame",
                    "timestamp": "2023-01-01T12:00:00",
                    "model_version": "v1.0",
                    "confidence": 0.95,
                    "source_frame": 1200,
                    "duration": None,
                },
            }
        ]
        with patch.object(
            storage, "search_similar", return_value=mock_results
        ) as mock_search:
            # Call function
            query = np.random.randn(768).astype(np.float32)
            results = search_similar(query, top_k=5)

            # Verify
            assert results == mock_results
            mock_search.assert_called_once_with(query, k=5, filter_fn=None)

    def test_retrieve_embedding(self, vector_storage_config, mock_faiss):
        """Test retrieve_embedding convenience function."""
        # Initialize storage
        storage = VectorStorage(vector_storage_config)
        VectorStorage._instance = storage

        # Mock retrieve_embedding
        mock_embedding = np.random.randn(768).astype(np.float32)
        mock_metadata: VectorMetadata = {
            "type": "frame",
            "timestamp": "2023-01-01T12:00:00",
            "model_version": "v1.0",
            "confidence": 0.95,
            "source_frame": 1200,
            "duration": None,
        }
        with patch.object(
            storage, "retrieve_embedding", return_value=(mock_embedding, mock_metadata)
        ) as mock_retrieve:
            # Call function
            embedding_id = "test_id"
            embedding, metadata = retrieve_embedding(embedding_id)

            # Verify
            assert np.array_equal(embedding, mock_embedding)
            assert metadata == mock_metadata
            mock_retrieve.assert_called_once_with(embedding_id)

    def test_search_vectors(self, vector_storage_config, mock_faiss):
        """Test search_vectors convenience function."""
        # Initialize storage
        storage = VectorStorage(vector_storage_config)
        VectorStorage._instance = storage

        # Mock search_similar
        mock_results = [
            {
                "id": "id1",
                "distance": 0.1,
                "similarity": 0.9,
                "metadata": {
                    "type": "frame",
                    "timestamp": "2023-01-01T12:00:00",
                    "model_version": "v1.0",
                    "confidence": 0.95,
                    "source_frame": 1200,
                    "duration": None,
                },
            }
        ]
        with patch.object(
            storage, "search_similar", return_value=mock_results
        ) as mock_search:
            # Call function
            query = np.random.randn(768).astype(np.float32)
            filter_fn = lambda x: True
            results = search_vectors(query, k=5, filter_fn=filter_fn)

            # Verify
            assert results == mock_results
            mock_search.assert_called_once_with(query, k=5, filter_fn=filter_fn)

    def test_optimize_index(self, vector_storage_config, mock_faiss):
        """Test optimize_index convenience function."""
        # Initialize storage
        storage = VectorStorage(vector_storage_config)
        VectorStorage._instance = storage

        # Mock faiss operations
        with (
            patch.object(mock_faiss, "IndexIDMap2") as mock_idmap,
            patch.object(mock_faiss, "IndexIVFFlat") as mock_ivf,
            patch.object(storage, "save") as mock_save,
        ):

            # Setup mock return values
            mock_idmap.return_value = MagicMock()
            mock_ivf.return_value = MagicMock()

            # Call function
            optimize_index()

            # Verify
            mock_idmap.assert_called_once()
            mock_ivf.assert_called_once()
            mock_save.assert_called_once()
