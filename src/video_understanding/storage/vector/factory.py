from typing import Dict, Any, Optional, Type

from video_understanding.storage.vector.base import BaseVectorStorage


class VectorStorageFactory:
    """Factory for creating vector storage instances."""

    _registry: Dict[str, Type[BaseVectorStorage]] = {}

    @classmethod
    def register(cls, name: str, storage_class: Type[BaseVectorStorage]) -> None:
        """Register a vector storage implementation.

        Args:
            name: Name of the implementation
            storage_class: Vector storage class to register
        """
        cls._registry[name] = storage_class

    @classmethod
    def create(cls, name: str, **kwargs: Any) -> BaseVectorStorage:
        """Create a vector storage instance.

        Args:
            name: Name of the implementation to create
            **kwargs: Parameters to pass to the constructor

        Returns:
            Vector storage instance

        Raises:
            ValueError: If the implementation is not registered
        """
        if name not in cls._registry:
            registered = ", ".join(cls._registry.keys()) if cls._registry else "none"
            raise ValueError(
                f"Vector storage implementation '{name}' not found. "
                f"Registered implementations: {registered}"
            )

        return cls._registry[name](**kwargs)

    @classmethod
    def get_registered_implementations(cls) -> Dict[str, Type[BaseVectorStorage]]:
        """Get all registered implementations.

        Returns:
            Dictionary of registered implementations
        """
        return cls._registry.copy()

    @classmethod
    def get_default(cls, **kwargs: Any) -> Optional[BaseVectorStorage]:
        """Get the default vector storage implementation.

        Args:
            **kwargs: Parameters to pass to the constructor

        Returns:
            Default vector storage instance or None if no default
        """
        default_name = "pinecone"
        try:
            return cls.create(default_name, **kwargs)
        except ValueError:
            if cls._registry:
                # Fall back to the first registered implementation
                name = next(iter(cls._registry))
                return cls.create(name, **kwargs)
            return None
