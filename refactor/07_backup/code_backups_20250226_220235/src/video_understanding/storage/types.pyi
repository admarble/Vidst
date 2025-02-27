from typing import Any, TypeVar

import numpy as np
import numpy.typing as npt

T = TypeVar("T")

class VectorMetadata:
    vector_id: str
    source_id: str
    vector_type: str
    timestamp: float | None
    metadata: dict[str, Any]

    def __init__(
        self,
        vector_id: str,
        source_id: str,
        vector_type: str,
        timestamp: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None: ...

class VectorStorageConfig:
    dimension: int
    max_vectors: int
    similarity_threshold: float
    index_type: str
    cache_size: int

    def __init__(
        self,
        dimension: int,
        max_vectors: int = 1000000,
        similarity_threshold: float = 0.8,
        index_type: str = "flat",
        cache_size: int = 1024 * 1024 * 1024,
    ) -> None: ...

class VectorStorage:
    def __init__(self, config: VectorStorageConfig) -> None: ...
    def add(
        self, vector_id: str, vector: npt.NDArray[np.float32], metadata: VectorMetadata
    ) -> None: ...
    def get(self, vector_id: str) -> tuple[npt.NDArray[np.float32], VectorMetadata]: ...
    def delete(self, vector_id: str) -> None: ...
    def search(
        self,
        query_vector: npt.NDArray[np.float32],
        k: int = 10,
        threshold: float | None = None,
    ) -> list[tuple[str, float, VectorMetadata]]: ...
    def clear(self) -> None: ...
    @property
    def size(self) -> int: ...
