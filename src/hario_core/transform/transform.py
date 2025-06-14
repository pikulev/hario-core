"""
Transformation logic for HAR data.
This module provides a set of functions that can be used to transform HAR data.
"""

from typing import Any, Callable, Dict, Optional

from hario_core.transform.defaults import json_array_handler
from hario_core.transform.interfaces import Transformer


class NormalizeSizes:
    """
    A transformer that normalizes the sizes of the request and response.
    """

    def __call__(self, data: Dict[str, Any]) -> Dict[str, Any]:
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


def normalize_sizes() -> Transformer:
    return NormalizeSizes()


class NormalizeTimings:
    """
    A transformer that normalizes the timings of the request.
    """

    def __call__(self, data: Dict[str, Any]) -> Dict[str, Any]:
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


def normalize_timings() -> Transformer:
    return NormalizeTimings()


class Flatten(Transformer):
    """
    A transformer that flattens the nested structure of the HAR data.
    """

    def __init__(
        self,
        separator: str = ".",
        array_handler: Optional[Callable[[list[Any], str], Any]] = None,
    ):
        self.separator = separator
        self.array_handler = array_handler or json_array_handler

    def _flatten(
        self, obj: Any, parent_key: str = "", result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if result is None:
            result = {}
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f"{parent_key}{self.separator}{k}" if parent_key else k
                self._flatten(v, new_key, result)
        elif isinstance(obj, list):
            value = self.array_handler(obj, parent_key)
            if isinstance(value, dict):
                result.update(value)
            else:
                result[parent_key] = value
        else:
            result[parent_key] = obj
        return result

    def __call__(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        return self._flatten(doc)


def flatten(
    separator: str = ".",
    array_handler: Optional[Callable[[list[Any], str], Any]] = None,
) -> Transformer:
    return Flatten(separator, array_handler or json_array_handler)


class SetId:
    """
    A transformer that sets the ID of the HAR data.
    """

    def __init__(self, id_fn: Callable[[Dict[str, Any]], str], id_field: str = "id"):
        self.id_fn = id_fn
        self.id_field = id_field

    def __call__(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data[self.id_field] = self.id_fn(data)
        return data


def set_id(id_fn: Callable[[Dict[str, Any]], str], id_field: str = "id") -> Transformer:
    return SetId(id_fn, id_field)
