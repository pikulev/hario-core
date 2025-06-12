"""
Transformation logic for HAR data.
This module provides a set of functions that can be used to transform HAR data.
"""

from typing import Any, Callable, Dict, Optional, Union, cast

import orjson

from hario_core.interfaces import Transformer

__all__ = [
    "normalize_sizes",
    "normalize_timings",
    "flatten",
]


def normalize_sizes() -> Transformer:
    def transformer(data: Dict[str, Any]) -> Dict[str, Any]:
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
    def transformer(data: Dict[str, Any]) -> Dict[str, Any]:
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
                isinstance(parent, Dict)
                and last in parent
                and isinstance(parent[last], (int, float))
                and parent[last] < 0
            ):
                parent[last] = 0.0
        return data

    return transformer


def _json_array_handler(arr: list[Any], path: str) -> str:
    """
    JSON array handler that returns a compact JSON string.
    """
    if not arr:
        return "[]"
    return cast(str, orjson.dumps(arr).decode("utf-8"))


def flatten(
    separator: str = ".",
    array_handler: Optional[
        Callable[[list[Any], str], Union[Any, Dict[str, Any]]]
    ] = None,
) -> Transformer:
    """
    Flattens a nested Dict (or Entry) into a flat Dict with keys joined by separator.
    If a list is encountered, array_handler is called.
    - If array_handler returns a Dict, its keys/values are merged into the result.
    - If array_handler returns a value, it is used as the value for the current key.
    """
    if array_handler is None:
        array_handler = _json_array_handler

    def _flatten(
        obj: Any,
        parent_key: str = "",
        result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if result is None:
            result = {}
        if isinstance(obj, Dict):
            for k, v in obj.items():
                new_key = f"{parent_key}{separator}{k}" if parent_key else k
                _flatten(v, new_key, result)
        elif isinstance(obj, list):
            value = array_handler(obj, parent_key)
            if isinstance(value, Dict):
                result.update(value)
            else:
                result[parent_key] = value
        else:
            result[parent_key] = obj
        return result

    def transformer(data: Dict[str, Any]) -> Dict[str, Any]:
        return _flatten(data)

    return transformer
