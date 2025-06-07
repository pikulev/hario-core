"""Transformation logic for HAR data."""
import json
from collections import deque
from typing import Any, Deque, Dict, Tuple

MAX_DEPTH: int = 3
SIZE_LIMIT: int = 32_000


def _should_stringify(name: str, value: Any, depth: int) -> bool:
    """Return *True* if *value* must be stored as a JSON-string."""
    if not isinstance(value, (dict, list)):
        return False
    if (
        isinstance(value, list)
        and len(json.dumps(value, separators=(",", ":"))) > SIZE_LIMIT
    ):
        return True
    if depth >= MAX_DEPTH:
        return True
    return False


def transform_har_entry_for_storage(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of *doc* where oversized/deep structures are JSON-strings."""
    result = doc.copy()
    queue: Deque[Tuple[Dict[str, Any], str, str, int]] = deque(
        (result, k, k, 1) for k in list(result.keys())
    )
    while queue:
        parent, key, path, depth = queue.popleft()
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