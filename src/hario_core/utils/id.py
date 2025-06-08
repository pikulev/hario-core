import hashlib
import uuid as uuid_lib
from typing import Any

from hario_core.interfaces import EntryIdFn
from hario_core.models.har_1_2 import Entry

__all__ = ["by_field", "uuid", "EntryIdFn"]


def by_field(fields: list[str]) -> EntryIdFn:
    """
    Returns a lambda that generates a deterministic ID
    based on the specified fields of an entry.
    """

    def get_field_value(entry: Entry, field_path: str) -> str:
        value: Any = entry
        for part in field_path.split("."):
            value = getattr(value, part, None)
            if value is None:
                raise AttributeError(f"Field '{field_path}' not found in entry")
        return str(value)

    def id_func(entry: Entry) -> str:
        raw_id_parts = [get_field_value(entry, field) for field in fields]
        raw_id = ":".join(raw_id_parts).encode()
        return hashlib.blake2b(raw_id, digest_size=16).hexdigest()

    return id_func


def uuid() -> EntryIdFn:
    """
    Returns a lambda that generates a UUID for an entry.
    """
    return lambda entry: str(uuid_lib.uuid4())
