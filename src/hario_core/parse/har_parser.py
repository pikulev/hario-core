"""
Core logic for reading, validating, and extending HAR (HTTP Archive) files.

- Provides the main entry point for loading and validating HAR files (`load_har`).
- Supports extensibility via registration of custom entry models and detectors.
- Handles both standard HAR and Chrome DevTools extensions out of the box.
"""

from pathlib import Path
from typing import Any, Callable, Dict, cast

import orjson
from pydantic import ValidationError

from hario_core.models.extensions.chrome_devtools import DevToolsEntry
from hario_core.models.har_1_2 import Entry, HarLog
from hario_core.parse.interfaces import JsonSource

# The registry for custom Entry models.
# It's a list of (detector_function, model_class) tuples.
ENTRY_MODEL_REGISTRY: list[tuple[Callable[[dict[str, Any]], bool], type[Entry]]] = []


def register_entry_model(
    detector: Callable[[dict[str, Any]], bool], model: type[Entry]
) -> None:
    """Registers a new Entry model and its detector function.

    The new model is inserted at the beginning of the registry, so it's
    checked first. This allows overriding default behavior.

    Args:
        detector: A function that takes an entry dict and returns True if
                  the `model` should be used for it.
        model: The Pydantic model class to use for matching entries.
    """
    ENTRY_MODEL_REGISTRY.insert(0, (detector, model))


def is_devtools_entry(entry_json: dict[str, Any]) -> bool:
    """Detects if an entry is from Chrome DevTools by checking for keys
    starting with an underscore.
    """
    return any(key.startswith("_") for key in entry_json)


# --- Default registrations ---
# Register the built-in DevTools extension
register_entry_model(is_devtools_entry, DevToolsEntry)


def entry_selector(entry_json: dict[str, Any]) -> type[Entry]:
    """Selects an Entry model by checking the registry.

    It iterates through the registered detectors and returns the first model
    that matches. If no custom model matches, it returns the base Entry model.
    """
    for detector, model in ENTRY_MODEL_REGISTRY:
        if detector(entry_json):
            return model
    return Entry  # Default model


def _to_bytes(src: JsonSource) -> bytes:
    if isinstance(src, (str, Path)):
        with open(src, "rb") as fh:
            return fh.read()
    if isinstance(src, (bytes, bytearray)):
        return cast(bytes, src)
    return cast(bytes, src.read())


def _read_json(src: JsonSource) -> dict[str, Any]:
    return cast(dict[str, Any], orjson.loads(_to_bytes(src)))


def parse(
    src: JsonSource,
    *args: Any,
) -> HarLog:
    """Parse *src* into a validated `HarLog` instance.

    It uses a model selector strategy to determine which `Entry` model to use,
    allowing for extensions like DevTools.

    Raises `ValueError` if the JSON is invalid HAR.
    """
    try:
        data = _read_json(src)
        if not isinstance(data, dict):
            raise ValueError("Invalid HAR file: root element must be a JSON object")
        return validate(data)
    except (KeyError, ValidationError, orjson.JSONDecodeError) as exc:
        raise ValueError("Invalid HAR file") from exc


def validate(har_dict: Dict[str, Any]) -> HarLog:
    """
    Validate HAR-structure (dict) with support for extensions.
    All entries are validated by one model, defined by the first entry.
    Returns HarLog with Entry/DevToolsEntry.

    Args:
        har_dict: dict
            The HAR-structure to validate.

    Returns:
        HarLog
    """
    if "log" not in har_dict:
        raise ValueError("Invalid HAR file: missing 'log'")
    if not isinstance(har_dict["log"], dict):
        raise ValueError("Invalid HAR file: 'log' must be a dict")
    if "entries" not in har_dict["log"]:
        raise ValueError("Invalid HAR file: missing 'entries' in 'log'")
    if not isinstance(har_dict["log"]["entries"], list):
        raise ValueError("Invalid HAR file: 'entries' must be a list")
    entries = har_dict["log"]["entries"]
    if not entries:
        log_copy = dict(har_dict["log"])
        log_copy["entries"] = []
        return HarLog.model_validate(log_copy)
    model_cls = entry_selector(entries[0])
    validated_entries = [model_cls.model_validate(entry) for entry in entries]
    log_copy = dict(har_dict["log"])
    log_copy["entries"] = validated_entries
    return HarLog.model_validate(log_copy)
