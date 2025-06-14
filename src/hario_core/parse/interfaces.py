from __future__ import annotations

from pathlib import Path
from typing import IO, Any, Protocol, Union

from hario_core.models.har_1_2 import HarLog

JsonSource = Union[str, Path, bytes, bytearray, IO[Any]]


class HarParser(Protocol):
    """Protocol for a function that parses HAR data from a source."""

    def __call__(self, src: Any) -> HarLog:
        """Parses HAR data from a source."""
        ...
