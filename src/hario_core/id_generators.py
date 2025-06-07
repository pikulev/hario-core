from __future__ import annotations

"""A deterministic ID generator for HAR entries."""
import hashlib
from typing import TYPE_CHECKING

from hario_core.interfaces import IdGenerator

if TYPE_CHECKING:
    from hario_core.interfaces import HarEntry


class DeterministicIdGenerator(IdGenerator):
    """
    Generates a deterministic ID for a HAR entry based on its
    start time and URL.
    """

    def generate_id(self, entry: HarEntry) -> str:
        """
        Generates a blake2b hash from the entry's start time and URL.
        """
        raw_id = f"{entry.startedDateTime}:{entry.request.url}".encode()
        doc_id = hashlib.blake2b(raw_id, digest_size=16).hexdigest()
        return doc_id
