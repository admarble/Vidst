from typing import Union, Protocol


class BaseVectorStorage(Protocol):
    """Base protocol for vector storage implementations."""

    pass


class FAISSConfig:
    """Configuration for FAISS vector storage."""

    pass


class PineconeConfig:
    """Configuration for Pinecone vector storage."""

    pass


class FAISSVectorStorage(BaseVectorStorage):
    """FAISS vector storage implementation."""

    def __init__(self, config: FAISSConfig):
        self.config = config


class PineconeVectorStorage(BaseVectorStorage):
    """Pinecone vector storage implementation."""

    def __init__(self, config: PineconeConfig):
        self.config = config


class VectorStorageFactory:
    """Factory for creating vector storage instances."""

    @staticmethod
    def create(config: Union[FAISSConfig, PineconeConfig]) -> BaseVectorStorage:
        """Create a vector storage instance based on configuration.

        Args:
            config: Vector storage configuration

        Returns:
            Vector storage instance

        Raises:
            ValueError: If configuration type is unknown
        """
        if isinstance(config, FAISSConfig):
            return FAISSVectorStorage(config)
        elif isinstance(config, PineconeConfig):
            return PineconeVectorStorage(config)
        else:
            raise ValueError(
                f"Unknown vector storage configuration type: {type(config)}"
            )
