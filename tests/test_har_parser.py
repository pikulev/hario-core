"""
Unit tests for the HAR parser in hario-core.

- Test model selection, registration, and parsing of various HAR formats.
- Cover standard, DevTools, and custom entry models.
- Ensure correct error handling for invalid and edge-case inputs.
"""

import json
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import pytest

from hario_core import har_parser
from hario_core.har_parser import entry_selector, parse, register_entry_model
from hario_core.models.extensions.chrome_devtools import DevToolsEntry
from hario_core.models.har_1_2 import Entry

from .samples import CLEAN_HAR, CLEAN_HAR_BYTES, DEVTOOLS_HAR, DEVTOOLS_HAR_BYTES


# A dummy Safari model for testing registration
class SafariEntry(Entry):
    """A dummy Safari model for testing registration."""

    webkitTrace: Dict[str, Any] = {}


def test_entry_selector_with_devtools() -> None:
    """Tests that the DevTools model is correctly selected."""
    entry_json = DEVTOOLS_HAR["log"]["entries"][0]
    model = entry_selector(entry_json)
    assert model is DevToolsEntry


def test_entry_selector_with_clean_har() -> None:
    """Tests that the default model is selected for a clean HAR."""
    entry_json = CLEAN_HAR["log"]["entries"][0]
    model = entry_selector(entry_json)
    assert model is Entry


def test_load_har_with_bytes() -> None:
    """Tests that a HAR file is correctly loaded from bytes."""
    har_log = parse(DEVTOOLS_HAR_BYTES)
    assert len(har_log.entries) > 0


def test_load_har_with_clean_bytes() -> None:
    """Tests loading a clean HAR from bytes."""
    har_log = parse(CLEAN_HAR_BYTES)
    assert len(har_log.entries) == 1
    entry = har_log.entries[0]
    assert isinstance(entry, Entry)
    assert not isinstance(entry, DevToolsEntry)
    assert entry.request.url == "http://example.com/clean"


def test_load_har_with_mixed_entries() -> None:
    """Tests loading a HAR with mixed entry types."""
    har_log = parse(json.dumps(DEVTOOLS_HAR).encode("utf-8"))
    assert len(har_log.entries) > 1

    # Assert that the correct model was used
    assert all(isinstance(entry, (Entry, DevToolsEntry)) for entry in har_log.entries)
    assert any(isinstance(entry, DevToolsEntry) for entry in har_log.entries)


@patch("hario_core.har_parser.ENTRY_MODEL_REGISTRY", [])
def test_register_entry_model() -> None:
    """Tests the registration of a custom entry model."""

    class CustomEntry(Entry):
        """Custom entry model for testing."""

    def custom_detector(entry: Dict[str, Any]) -> bool:
        """Detector for custom entry."""
        return "_custom" in entry

    register_entry_model(custom_detector, CustomEntry)
    assert len(har_parser.ENTRY_MODEL_REGISTRY) == 1
    assert har_parser.ENTRY_MODEL_REGISTRY[0] == (
        custom_detector,
        CustomEntry,
    )


def test_select_entry_model() -> None:
    """Tests the selection of the correct entry model."""

    class CustomEntry(Entry):
        """Custom entry model for testing."""

    def custom_detector(entry: Dict[str, Any]) -> bool:
        """Detector for custom entry."""
        return "_custom" in entry

    entry_data = {
        "_custom": True,
        "pageref": "page_0",
        "startedDateTime": "2022-01-01T00:00:00.000Z",
        "time": 100,
        "request": {},
        "response": {},
        "cache": {},
        "timings": {"send": 0, "wait": 0, "receive": 0},
    }
    # Test with a valid custom entry
    with patch(
        "hario_core.har_parser.ENTRY_MODEL_REGISTRY", [(custom_detector, CustomEntry)]
    ):
        model = entry_selector(entry_data)
        assert model is CustomEntry

    # Test with a default entry when no custom model matches
    entry_data.pop("_custom")
    with patch("hario_core.har_parser.ENTRY_MODEL_REGISTRY", []):
        model = entry_selector(entry_data)
        assert model is Entry


def test_load_har_with_dict() -> None:
    """Tests loading a HAR from a dictionary by encoding it first."""
    har_data = {
        "log": {
            "version": "1.2",
            "creator": {"name": "Test", "version": "1.0"},
            "entries": [
                {
                    "pageref": "page_0",
                    "startedDateTime": "2022-01-01T00:00:00Z",
                    "time": 100,
                    "request": {
                        "method": "GET",
                        "url": "http://example.com",
                        "httpVersion": "HTTP/1.1",
                        "cookies": [],
                        "headers": [],
                        "queryString": [],
                        "headersSize": 100,
                        "bodySize": 0,
                    },
                    "response": {
                        "status": 200,
                        "statusText": "OK",
                        "httpVersion": "HTTP/1.1",
                        "cookies": [],
                        "headers": [],
                        "content": {"size": 0, "mimeType": "text/plain"},
                        "redirectURL": "",
                        "headersSize": 100,
                        "bodySize": 0,
                    },
                    "cache": {},
                    "timings": {"send": 1, "wait": 1, "receive": 1},
                }
            ],
        }
    }
    result = parse(json.dumps(har_data).encode("utf-8"))
    assert isinstance(result.entries, list)
    assert len(result.entries) == 1
    assert isinstance(result.entries[0], Entry)


def test_load_har_from_file(tmp_path: Path) -> None:
    """Tests loading a HAR from a file path."""
    har_data = {
        "log": {
            "version": "1.2",
            "creator": {"name": "Test", "version": "1.0"},
            "entries": [],
        }
    }
    file_path = tmp_path / "test.har"
    with open(file_path, "w") as f:
        json.dump(har_data, f)
    result = parse(file_path)
    assert isinstance(result.entries, list)


def test_load_har_with_invalid_json() -> None:
    """Tests loading a HAR with invalid JSON content."""
    with pytest.raises(ValueError, match="Invalid HAR file"):
        parse(b"not a json")


def test_load_har_missing_log() -> None:
    """Tests loading a HAR with a missing 'log' field."""
    har_data = {"invalid": "data"}
    with pytest.raises(ValueError, match="Invalid HAR file"):
        parse(json.dumps(har_data).encode("utf-8"))


def test_load_har_with_invalid_file_path() -> None:
    """Tests loading a HAR from a non-existent file path."""
    with pytest.raises(FileNotFoundError):
        parse(Path("non_existent_file.har"))


def test_load_har_missing_version() -> None:
    """Tests that a HAR file with a missing version raises an error."""
    har_data = {
        "log": {
            "creator": {"name": "Test", "version": "1.0"},
            "entries": [],
        }
    }
    with pytest.raises(ValueError, match="Invalid HAR file"):
        parse(json.dumps(har_data).encode("utf-8"))


def test_load_har_missing_entries() -> None:
    """Tests that a HAR file with a missing entries raises an error."""
    har_data = {
        "log": {
            "version": "1.2",
            "creator": {"name": "Test", "version": "1.0"},
        }
    }
    with pytest.raises(ValueError, match="Invalid HAR file"):
        parse(json.dumps(har_data).encode("utf-8"))


def test_load_har_log_without_entries() -> None:
    """Checks that ValueError is raised if 'log' has no 'entries'."""
    har_data: dict[str, Any] = {"log": {}}
    with pytest.raises(ValueError, match="Invalid HAR file"):
        parse(json.dumps(har_data).encode("utf-8"))


def test_load_har_log_with_version_but_no_entries() -> None:
    """
    Checks that ValueError is raised if 'log' has 'version'
    and 'creator', but no 'entries'.
    """
    har_data: dict[str, Any] = {
        "log": {"version": "1.2", "creator": {"name": "Test", "version": "1.0"}}
    }
    with pytest.raises(ValueError, match="Invalid HAR file"):
        parse(json.dumps(har_data).encode("utf-8"))


def test_load_har_root_not_dict() -> None:
    """Checks that ValueError is raised if root element is not a dict."""
    har_data: Any = 123
    with pytest.raises(ValueError, match="root element must be a JSON object"):
        parse(json.dumps(har_data).encode("utf-8"))
