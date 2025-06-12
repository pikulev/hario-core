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

import orjson
import pytest

from hario_core import har_parser
from hario_core.har_parser import entry_selector, parse, register_entry_model
from hario_core.models.extensions.chrome_devtools import DevToolsEntry
from hario_core.models.har_1_2 import Entry

from .samples import (
    CHROME_DEVTOOLS_HAR,
    CHROME_DEVTOOLS_HAR_BYTES,
    CLEANED_HAR,
    CLEANED_HAR_BYTES,
    INVALID_HAR_LOG_EMPTY,
    INVALID_HAR_LOG_WITH_VERSION_BUT_NO_ENTRIES,
    INVALID_HAR_NO_ENTRIES,
    INVALID_HAR_NO_LOG,
    INVALID_HAR_NO_VERSION,
    INVALID_HAR_ROOT_NOT_DICT,
)


# A dummy Safari model for testing registration
class SafariEntry(Entry):
    """A dummy Safari model for testing registration."""

    webkitTrace: Dict[str, Any] = {}


class TestHarParser:
    def test_entry_selector_with_devtools(self) -> None:
        """Tests that the DevTools model is correctly selected."""
        entry_json = CHROME_DEVTOOLS_HAR["log"]["entries"][0]
        model = entry_selector(entry_json)
        assert model is DevToolsEntry

    def test_entry_selector_with_clean_har(self) -> None:
        """Tests that the default model is selected for a clean HAR."""
        entry_json = CLEANED_HAR["log"]["entries"][0]
        model = entry_selector(entry_json)
        assert model is Entry

    def test_load_har_with_bytes(self) -> None:
        """Tests that a HAR file is correctly loaded from bytes."""
        har_log = parse(CHROME_DEVTOOLS_HAR_BYTES)
        assert len(har_log.entries) == 1
        assert isinstance(har_log.entries[0], Entry)

    def test_load_har_with_clean_bytes(self) -> None:
        """Tests loading a clean HAR from bytes."""
        har_log = parse(CLEANED_HAR_BYTES)
        assert len(har_log.entries) == 1
        entry = har_log.entries[0]
        assert isinstance(entry, Entry)
        assert entry.request.url == "https://test.test/assets/css/f2aaccf1.css"

    def test_load_har_with_mixed_entries(self) -> None:
        """Tests loading a HAR with mixed entry types."""
        har_log = parse(orjson.dumps(CHROME_DEVTOOLS_HAR))
        assert len(har_log.entries) == 1
        assert isinstance(har_log.entries[0], Entry)
        assert isinstance(har_log.entries[0], DevToolsEntry)
        assert har_log.entries[0].response.transferSize == 116558
        assert har_log.entries[0].initiator is not None
        assert har_log.entries[0].initiator.type == "parser"

    @patch("hario_core.har_parser.ENTRY_MODEL_REGISTRY", [])
    def test_register_entry_model(self) -> None:
        """Tests the registration of a custom entry model."""

        class CustomEntry(Entry):
            """Custom entry model for testing."""

        def custom_detector(entry: Dict[str, Any]) -> bool:
            """Detector for custom entry."""
            return "_connectionId" in entry

        register_entry_model(custom_detector, CustomEntry)
        assert len(har_parser.ENTRY_MODEL_REGISTRY) == 1
        assert har_parser.ENTRY_MODEL_REGISTRY[0] == (
            custom_detector,
            CustomEntry,
        )

    def test_select_entry_model(self) -> None:
        """Tests the selection of the correct entry model."""

        class CustomEntry(Entry):
            """Custom entry model for testing."""

        def custom_detector(entry: Dict[str, Any]) -> bool:
            """Detector for custom entry."""
            return "_connectionId" in entry

        entry_data = dict(CHROME_DEVTOOLS_HAR["log"]["entries"][0])
        # Test with a valid custom entry
        with patch(
            "hario_core.har_parser.ENTRY_MODEL_REGISTRY",
            [(custom_detector, CustomEntry)],
        ):
            model = entry_selector(entry_data)
            assert model is CustomEntry

        # Test with a default entry when no custom model matches
        entry_data.pop("_connectionId")
        with patch("hario_core.har_parser.ENTRY_MODEL_REGISTRY", []):
            model = entry_selector(entry_data)
            assert model is Entry

    def test_load_har_with_dict(self) -> None:
        """Tests loading a HAR from a dictionary by encoding it first."""
        result = parse(orjson.dumps(CLEANED_HAR))
        assert isinstance(result.entries, list)
        assert len(result.entries) == 1
        assert isinstance(result.entries[0], Entry)

    def test_load_har_from_file(self, tmp_path: Path) -> None:
        """Tests loading a HAR from a file path."""
        file_path = tmp_path / "test.har"
        with open(file_path, "w") as f:
            json.dump(CLEANED_HAR, f)
        result = parse(file_path)
        assert isinstance(result.entries, list)

    def test_load_har_with_invalid_json(self) -> None:
        """Tests loading a HAR with invalid JSON content."""
        with pytest.raises(ValueError, match="Invalid HAR file"):
            parse(b"not a json")

    def test_load_har_missing_log(self) -> None:
        """Tests loading a HAR with a missing 'log' field."""
        with pytest.raises(ValueError, match="Invalid HAR file"):
            parse(orjson.dumps(INVALID_HAR_NO_LOG))

    def test_load_har_with_invalid_file_path(self) -> None:
        """Tests loading a HAR from a non-existent file path."""
        with pytest.raises(FileNotFoundError):
            parse(Path("non_existent_file.har"))

    def test_load_har_missing_version(self) -> None:
        """Tests that a HAR file with a missing version raises an error."""
        with pytest.raises(ValueError, match="Invalid HAR file"):
            parse(orjson.dumps(INVALID_HAR_NO_VERSION))

    def test_load_har_missing_entries(self) -> None:
        """Tests that a HAR file with a missing entries raises an error."""
        with pytest.raises(ValueError, match="Invalid HAR file"):
            parse(orjson.dumps(INVALID_HAR_NO_ENTRIES))

    def test_load_har_log_without_entries(self) -> None:
        """Checks that ValueError is raised if 'log' has no 'entries'."""
        with pytest.raises(ValueError, match="Invalid HAR file"):
            parse(orjson.dumps(INVALID_HAR_LOG_EMPTY))

    def test_load_har_log_with_version_but_no_entries(self) -> None:
        """
        Checks that ValueError is raised if 'log' has 'version'
        and 'creator', but no 'entries'.
        """
        with pytest.raises(ValueError, match="Invalid HAR file"):
            parse(orjson.dumps(INVALID_HAR_LOG_WITH_VERSION_BUT_NO_ENTRIES))

    def test_load_har_root_not_dict(self) -> None:
        """Checks that ValueError is raised if root element is not a dict."""
        with pytest.raises(ValueError, match="root element must be a JSON object"):
            parse(orjson.dumps(INVALID_HAR_ROOT_NOT_DICT))
