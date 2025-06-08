import re
from typing import Any, Tuple, Union


def parse_path(path: str) -> Tuple[Union[str, int], ...]:
    """
    Convert dot-path like 'foo.bar[0].baz' to tuple ('foo', 'bar', 0, 'baz').
    """
    parts = []
    for part in path.split("."):
        m = re.match(r"(\w+)(\[(\d+)\])?", part)
        if m:
            parts.append(m.group(1))
            if m.group(3):
                parts.append(int(m.group(3)))
    return tuple(parts)


def get_or_create_by_path(obj: Any, path: Tuple[Union[str, int], ...]) -> Any:
    """
    Walks the structure by path, creating dicts/lists as needed.
    Returns the parent container for the last element in path.
    """
    parent = obj
    for key in path:
        if isinstance(parent, list) and isinstance(key, int):
            while len(parent) <= key:
                parent.append({})
            parent = parent[key]
        elif isinstance(parent, dict) and isinstance(key, str):
            if key not in parent or parent[key] is None:
                parent[key] = {}
            parent = parent[key]
        else:
            raise TypeError(f"Invalid path: {path}")
    return parent
