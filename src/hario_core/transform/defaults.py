import hashlib
import uuid as uuid_lib
from datetime import datetime
from typing import Any, Dict, cast

import orjson


class ByField:
    """
    A class that generates a deterministic ID based on
    the specified fields of an entry dictionary.
    """

    def __init__(self, fields: list[str]):
        self.fields = fields

    def get_field_value(self, entry: Dict[str, Any], field_path: str) -> str:
        value: Any = entry
        for part in field_path.split("."):
            if not isinstance(value, dict):
                raise ValueError(f"Field '{field_path}' is not a dictionary")
            value = value[part]
            if value is None:
                raise ValueError(f"Field '{field_path}' is None")

        # Special handling for datetime
        if isinstance(value, datetime):
            # Format in ISO 8601 with Z at the end
            return value.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        return str(value)

    def __call__(self, entry: Dict[str, Any]) -> str:
        raw_id_parts = [self.get_field_value(entry, field) for field in self.fields]
        raw_id = ":".join(raw_id_parts).encode()
        return hashlib.blake2b(raw_id, digest_size=16).hexdigest()


def by_field(fields: list[str]) -> ByField:
    return ByField(fields)


class UUID:
    def __call__(self, entry: Dict[str, Any]) -> str:
        """
        Returns a function that generates a UUID for an entry.
        """
        return str(uuid_lib.uuid4())


def uuid() -> UUID:
    return UUID()


def json_array_handler(arr: list[Any], path: str) -> str:
    """
    JSON array handler that returns a compact JSON string.
    """
    if not arr:
        return "[]"
    return cast(str, orjson.dumps(arr).decode("utf-8"))
