from typing import Any, Dict, List, Optional, Protocol, Tuple


class SupportsTimings(Protocol):
    blocked: Optional[float]
    dns: Optional[float]
    connect: Optional[float]
    send: float
    wait: float
    receive: float
    ssl: Optional[float]


class SupportsRequestResponse(Protocol):
    headersSize: Optional[int]
    bodySize: Optional[int]


class SupportsRequest(SupportsRequestResponse, Protocol):
    url: str


class HarEntry(Protocol):
    startedDateTime: str
    request: SupportsRequest
    response: SupportsRequestResponse
    timings: SupportsTimings
    time: float

    # Pydantic models have this method
    def model_dump(self) -> Dict[str, Any]: ...

    def model_copy(self: "HarEntry", *, deep: bool = False) -> "HarEntry": ...


class Enricher(Protocol):
    """
    Interface (Protocol) for a component that enriches a HAR entry.
    It takes the source entry model and modifies the data dictionary in-place.
    """

    def __call__(self, entry: "HarEntry", data: Dict[str, Any]) -> None: ...


class IdGenerator(Protocol):
    """
    Interface (Protocol) for a component that generates
    a unique ID for a HAR entry.
    """

    def generate_id(self, entry: "HarEntry") -> str:
        """Generates a unique ID for the given HAR entry."""
        ...


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
        """Retrie"Retrieves a document by its ID."""
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
