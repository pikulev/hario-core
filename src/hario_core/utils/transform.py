"""
Transformation logic for HAR data.
This module provides a set of functions that can be used to transform HAR data.
"""

import json
from typing import Any, Dict, Protocol

from hario_core.models.har_1_2 import Entry

__all__ = [
    "flatten",
    "normalize_sizes",
    "normalize_timings",
]


class Transformer(Protocol):
    def __call__(self, entry: Entry) -> Dict[str, Any]: ...


def flatten(max_depth: int = 3, size_limit: int = 32_000) -> Transformer:
    """
    Flattens the HAR data into a single level.
    This is useful for storing HAR data in a database.

    Args:
        max_depth: The maximum depth of the nested data to flatten.
        size_limit: The maximum size (in bytes) of the nested data to flatten.
    """

    def transformer(entry: Entry) -> Dict[str, Any]:
        doc = entry.model_dump()

        def _should_stringify(name: str, value: Any, depth: int) -> bool:
            if not isinstance(value, (dict, list)):
                return False
            if (
                isinstance(value, list)
                and len(json.dumps(value, separators=(",", ":"))) > size_limit
            ):
                return True
            if depth >= max_depth:
                return True
            return False

        result = doc.copy()
        queue = [(result, k, k, 1) for k in list(result.keys())]
        while queue:
            parent, key, path, depth = queue.pop(0)
            value = parent[key]
            if _should_stringify(path, value, depth):
                parent[key] = json.dumps(value, ensure_ascii=False)
                continue
            if isinstance(value, dict):
                for child_key in list(value.keys()):
                    queue.append((value, child_key, f"{path}.{child_key}", depth + 1))
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        for child_key in list(item.keys()):
                            queue.append(
                                (item, child_key, f"{path}[{i}].{child_key}", depth + 1)
                            )
        return result

    return transformer


def normalize_sizes() -> Transformer:
    def transformer(entry: Entry) -> Dict[str, Any]:
        data = entry.model_dump()
        for path in [
            ("request", "headersSize"),
            ("request", "bodySize"),
            ("response", "headersSize"),
            ("response", "bodySize"),
            ("response", "content", "size"),
        ]:
            parent = data
            for key in path[:-1]:
                parent = parent.get(key, {})
            last = path[-1]
            if last in parent and isinstance(parent[last], int) and parent[last] < 0:
                parent[last] = 0
        return data

    return transformer


def normalize_timings() -> Transformer:
    def transformer(entry: Entry) -> Dict[str, Any]:
        data = entry.model_dump()
        timing_fields = [
            ("timings", "blocked"),
            ("timings", "dns"),
            ("timings", "connect"),
            ("timings", "send"),
            ("timings", "wait"),
            ("timings", "receive"),
            ("timings", "ssl"),
        ]
        for path in timing_fields:
            parent = data
            for key in path[:-1]:
                parent = parent.get(key, {})
            last = path[-1]
            if (
                isinstance(parent, dict)
                and last in parent
                and isinstance(parent[last], (int, float))
                and parent[last] < 0
            ):
                parent[last] = 0.0
        return data

    return transformer
