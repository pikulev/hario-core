"""Normalization logic for HAR data."""

from typing import Any

from hario_core.interfaces import HarEntry


def normalize_har_entry(entry: HarEntry) -> HarEntry:
    """Normalizes HAR entry in-place.

    It replaces negative values in timing and size fields with None.
    It operates on a deep copy of the entry to avoid side effects.
    """
    result = entry.model_copy(deep=True)

    def _normalize_to_none(obj: Any, fields: list[str]) -> None:
        """Replaces negative values with None in the specified fields of the object."""
        if obj is None:
            return
        for field in fields:
            current_value = getattr(obj, field, None)
            if isinstance(current_value, (int, float)) and current_value < 0:
                setattr(obj, field, None)

    _normalize_to_none(result, ["time"])
    _normalize_to_none(
        result.timings,
        ["blocked", "dns", "connect", "send", "wait", "receive", "ssl"],
    )
    _normalize_to_none(result.request, ["headersSize", "bodySize"])
    _normalize_to_none(result.response, ["headersSize", "bodySize"])

    return result 