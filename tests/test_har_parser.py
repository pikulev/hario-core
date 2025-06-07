"""Tests for the HAR parser."""
import json
from typing import Any, Dict

import pytest
from pydantic import Field

from hario_core.har_parser import entry_selector, load_har, register_entry_model
from hario_core.models.extensions.chrome_devtools import DevToolsEntry
from hario_core.models.har_1_2 import Entry
from .samples import CLEAN_HAR, CLEAN_HAR_BYTES, DEVTOOLS_HAR, DEVTOOLS_HAR_BYTES


# A dummy Safari model for testing registration
class SafariEntry(Entry):
    webkitTrace: Dict[str, Any] = Field(alias="_webkitTrace")


def is_safari_entry(entry_json: Dict[str, Any]) -> bool:
    return "_webkitTrace" in entry_json


def test_entry_selector_clean_har() -> None:
    """Tests that the selector returns the base Entry for a clean HAR."""
    entry_json = CLEAN_HAR["log"]["entries"][0]
    model = entry_selector(entry_json)
    assert model is Entry


def test_entry_selector_devtools_har() -> None:
    """Tests that the selector returns DevToolsEntry for a HAR with extensions."""
    entry_json = DEVTOOLS_HAR["log"]["entries"][0]
    model = entry_selector(entry_json)
    assert model is DevToolsEntry


def test_load_har_clean() -> None:
    """Tests loading a standard HAR file."""
    har_log = load_har(CLEAN_HAR_BYTES)
    assert len(har_log.entries) == 1
    entry = har_log.entries[0]
    assert isinstance(entry, Entry)
    assert not isinstance(entry, DevToolsEntry)
    assert entry.request.url == "http://example.com/clean"


def test_load_har_devtools() -> None:
    """Tests loading a HAR file with DevTools extensions."""
    har_log = load_har(DEVTOOLS_HAR_BYTES)
    assert len(har_log.entries) == 1
    entry = har_log.entries[0]
    assert isinstance(entry, DevToolsEntry)
    assert entry.resourceType == "fetch"
    assert entry.response.transferSize == 812
    assert entry.initiator.type == "script"


def test_load_har_invalid_json() -> None:
    """Tests that loading invalid JSON raises a ValueError."""
    with pytest.raises(json.JSONDecodeError):
        load_har(b"{'invalid_json")


def test_load_har_invalid_har() -> None:
    """Tests that loading a valid JSON that is not a HAR raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid HAR file"):
        load_har(b'{"not_a_har": true}')


def test_load_har_missing_version() -> None:
    """Tests that a HAR missing a required field like 'version' raises an error."""
    invalid_har = {
        "log": {
            # "version": "1.2",  <-- missing
            "creator": {"name": "Test", "version": "1.0"},
            "entries": [],
        }
    }
    with pytest.raises(ValueError, match="Invalid HAR file"):
        load_har(json.dumps(invalid_har).encode("utf-8"))


def test_load_har_with_custom_registered_model() -> None:
    """Tests that a custom, user-registered model is correctly used."""
    # Register the custom model
    register_entry_model(is_safari_entry, SafariEntry)

    safari_har = {
        "log": {
            "version": "1.2",
            "creator": {"name": "Safari", "version": "17.0"},
            "entries": [
                {
                    "_webkitTrace": {"foo": "bar"},
                    "startedDateTime": "2024-01-01T12:00:02.000Z",
                    "time": 20,
                    "request": {"method": "GET", "url": "/"},
                    "response": {"status": 200, "content": {"size": 0}},
                    "cache": {},
                    "timings": {"send": 1, "wait": 1, "receive": 1},
                }
            ],
        }
    }
    safari_har_bytes = json.dumps(safari_har).encode("utf-8")

    har_log = load_har(safari_har_bytes)
    assert len(har_log.entries) == 1
    entry = har_log.entries[0]

    assert isinstance(entry, SafariEntry)
    assert entry.webkitTrace == {"foo": "bar"}

    # Clean up registry for other tests if needed (pytest runs tests in separate contexts,
    # but this is good practice if tests shared state)
    from hario_core.har_parser import ENTRY_MODEL_REGISTRY
    ENTRY_MODEL_REGISTRY.pop(0)
