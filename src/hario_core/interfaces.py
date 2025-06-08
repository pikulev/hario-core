from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol, Tuple

from hario_core.models.har_1_2 import Entry, HarLog

"""
Type protocols and interfaces for hario-core.

- Defines Protocols for HAR entries, enrichers, ID generators, and storage repositories.
- Enables type-safe extensibility and plug-in architecture.
- Used for static type checking and as contracts for core logic.
"""

__all__ = [
    "HarParser",
    "Processor",
    "Transformer",
    "EntryIdFn",
    "HarStorageRepository",
]


class HarParser(Protocol):
    """Protocol for a function that parses HAR data from a source."""

    def __call__(self, src: Any) -> HarLog:
        """Parses HAR data from a source."""
        ...


class Processor(Protocol):
    """
    Protocol for a processor that can be called with a
    source and returns a list of dicts.
    """

    def process(self, src: Any) -> List[Dict[str, Any]]:
        """Processes the source and returns a list of dicts."""
        ...


class Transformer(Protocol):
    """Protocol for a transformer that can be called with a dict."""

    def __call__(self, entry: Entry) -> Dict[str, Any]:
        """
        Transforms the dict in-place.
        User can mutate/add/remove fields as needed.
        """
        ...


class EntryIdFn(Protocol):
    """Protocol for a function that generates an ID for a HAR entry."""

    def __call__(self, entry: Entry) -> str: ...


class HarStorageRepository(Protocol):
    """Interface (Protocol) for a repository that stores HAR data."""

    def save(self, har_data: Dict[str, Any]) -> None:
        """Saves a single HAR document."""
        ...

    def save_many(self, har_data: List[Dict[str, Any]]) -> Tuple[int, int, List[str]]:
        """
        Saves multiple HAR documents in bulk.
        Returns a tuple of (success_count, failure_count, errors).
        """
        ...

    def get_by_id(self, doc_id: str) -> Dict[str, Any]:
        """Retrieves a document by its ID."""
        ...

    def find_all(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Finds all documents, optionally matching a query."""
        ...

    def wait_for_connection(
        self, max_retries: int = 10, delay: int = 10
    ) -> Tuple[bool, str, str]:
        """Waits for the storage to become available."""
        ...

    def create_index_if_not_exists(self, mapping: Dict[str, Any]) -> None:
        """Creates the necessary index/table if it doesn't exist."""
        ...
