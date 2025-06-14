from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


class Processor(Protocol):
    """
    Protocol for a processor that can be called with a
    source and returns a list of dicts.
    """

    def process(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processes the source and returns a list of dicts."""
        ...


class ProcessorConfig(Protocol):
    """Protocol for a processor configuration."""

    batch_size: int
    processing_strategy: str
    max_workers: Optional[int]


@runtime_checkable
class Transformer(Protocol):
    """Protocol for transformers that process HAR entries."""

    def __call__(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform the data.

        Args:
            data: The data to transform.

        Returns:
            The transformed data.
        """
        ...
