"""
Core logic for reading, validating, and extending HAR (HTTP Archive) files.

- Provides the main entry point for loading and validating HAR files (`load_har`).
- Supports extensibility via registration of custom entry models and detectors.
- Handles both standard HAR and Chrome DevTools extensions out of the box.
"""

import json
from pathlib import Path
from typing import IO, Any, Callable, Union, cast

from pydantic import ValidationError

from hario_core.models.extensions.chrome_devtools import DevToolsEntry
from hario_core.models.har_1_2 import Entry, HarLog

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


def entry_selector(entry_json: dict[str, Any]) -> type[Entry]:
    """Selects an Entry model by checking the registry.

    It iterates through the registered detectors and returns the first model
    that matches. If no custom model matches, it returns the base Entry model.
    """
    for detector, model in ENTRY_MODEL_REGISTRY:
        if detector(entry_json):
            return model
    return Entry  # Default model


# --- Default registrations ---


def is_devtools_entry(entry_json: dict[str, Any]) -> bool:
    """Detects if an entry is from Chrome DevTools by checking for keys
    starting with an underscore.
    """
    return any(key.startswith("_") for key in entry_json)


# Register the built-in DevTools extension
register_entry_model(is_devtools_entry, DevToolsEntry)


JsonSource = Union[str, Path, bytes, bytearray, IO[Any]]


def _read_json(src: JsonSource) -> dict[str, Any]:
    if isinstance(src, (str, Path)):
        with open(src, "rb") as fh:
            return cast(dict[str, Any], json.load(fh))
    if isinstance(src, (bytes, bytearray)):
        return cast(dict[str, Any], json.loads(src))
    # assume file‑like
    return cast(dict[str, Any], json.load(src))


def parse(
    src: JsonSource,
    *,
    entry_model_selector: Callable[[dict[str, Any]], type[Entry]] = entry_selector,
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
        log_data = data["log"]
        raw_entries = log_data["entries"]

        # Validate entries one by one using the selector
        validated_entries = [
            entry_model_selector(entry).model_validate(entry) for entry in raw_entries
        ]

        # Replace raw entries with validated models
        log_data["entries"] = validated_entries

        # Validate the entire HarLog object at once
        return HarLog.model_validate(log_data)
    except (KeyError, ValidationError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid HAR file") from exc
