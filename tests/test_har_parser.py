"""
Unit tests for the HAR parser in hario-core.

- Test model selection, registration, and parsing of various HAR formats.
- Cover standard, DevTools, and custom entry models.
- Ensure correct error handling for invalid and edge-case inputs.
"""

import io
import json
from pathlib import Path
from typing import Any, Callable, Dict, Type
from unittest.mock import patch

import orjson
import pytest

from hario_core.models import DevToolsEntry, Entry, HarLog
from hario_core.parse import (
    entry_selector,
    har_parser,
    parse,
    register_entry_model,
    validate,
)

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
    @pytest.mark.parametrize(
        "har_input, loader, expected_type",
        [
            ("cleaned_har", validate, Entry),
            (CLEANED_HAR_BYTES, parse, Entry),
            ("chrome_devtools_har", validate, DevToolsEntry),
            (CHROME_DEVTOOLS_HAR_BYTES, parse, DevToolsEntry),
        ],
    )
    def test_load_har(
        self,
        request: Any,
        har_input: Dict[str, Any],
        loader: Callable[[Any], HarLog],
        expected_type: Type[Entry],
    ) -> None:
        if isinstance(har_input, str):
            har_input = request.getfixturevalue(har_input)
        har_log = loader(har_input)
        assert isinstance(har_log.entries, list)
        assert len(har_log.entries) == 1
        assert isinstance(har_log.entries[0], expected_type)

    @pytest.mark.parametrize(
        "entry_fixture, expected_model",
        [
            ("chrome_devtools_entry", DevToolsEntry),
            ("cleaned_entry", Entry),
        ],
    )
    def test_entry_selector(
        self, request: Any, entry_fixture: Dict[str, Any], expected_model: Type[Entry]
    ) -> None:
        entry_json = request.getfixturevalue(entry_fixture)
        model = entry_selector(entry_json)
        assert model is expected_model

    @pytest.mark.parametrize(
        "har_dict, expected_type",
        [
            ("cleaned_har", Entry),
            ("chrome_devtools_har", DevToolsEntry),
        ],
    )
    def test_validate_with_dict(
        self, request: Any, har_dict: Dict[str, Any], expected_type: Type[Entry]
    ) -> None:
        har_log = validate(request.getfixturevalue(har_dict))
        assert isinstance(har_log.entries[0], expected_type)

    @pytest.mark.parametrize(
        "har_bytes, expected_type",
        [
            (CLEANED_HAR_BYTES, Entry),
            (CHROME_DEVTOOLS_HAR_BYTES, DevToolsEntry),
        ],
    )
    def test_load_har_with_bytes(
        self, har_bytes: bytes, expected_type: Type[Entry]
    ) -> None:
        har_log = parse(har_bytes)
        assert isinstance(har_log.entries[0], expected_type)

    def test_load_har_with_mixed_entries(self) -> None:
        har_log = validate(CHROME_DEVTOOLS_HAR)
        assert len(har_log.entries) == 1
        assert isinstance(har_log.entries[0], Entry)
        assert isinstance(har_log.entries[0], DevToolsEntry)
        assert har_log.entries[0].response.transferSize == 116558
        assert har_log.entries[0].initiator is not None
        assert har_log.entries[0].initiator.type == "parser"

    @patch("hario_core.parse.har_parser.ENTRY_MODEL_REGISTRY", [])
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
            "hario_core.parse.har_parser.ENTRY_MODEL_REGISTRY",
            [(custom_detector, CustomEntry)],
        ):
            model = entry_selector(entry_data)
            assert model is CustomEntry

        # Test with a default entry when no custom model matches
        entry_data.pop("_connectionId")
        with patch("hario_core.parse.har_parser.ENTRY_MODEL_REGISTRY", []):
            model = entry_selector(entry_data)
            assert model is Entry

    def test_load_har_from_file(self, tmp_path: Path) -> None:
        """Tests loading a HAR from a file path."""
        file_path = tmp_path / "test.har"
        with open(file_path, "w") as f:
            json.dump(CLEANED_HAR, f)
        result = parse(file_path)
        assert isinstance(result.entries, list)

    def test_parse_with_file_like(self, cleaned_har: Dict[str, Any]) -> None:
        data = orjson.dumps(cleaned_har)
        file_like = io.BytesIO(data)
        har_log = parse(file_like)
        assert hasattr(har_log, "entries")
        assert isinstance(har_log.entries, list)

    @pytest.mark.parametrize(
        "invalid_bytes",
        [
            b"not a json",
            orjson.dumps(INVALID_HAR_NO_LOG),
            orjson.dumps(INVALID_HAR_NO_VERSION),
            orjson.dumps(INVALID_HAR_NO_ENTRIES),
            orjson.dumps(INVALID_HAR_LOG_EMPTY),
            orjson.dumps(INVALID_HAR_LOG_WITH_VERSION_BUT_NO_ENTRIES),
            orjson.dumps(INVALID_HAR_ROOT_NOT_DICT),
        ],
    )
    def test_load_har_invalid_cases(self, invalid_bytes: bytes) -> None:
        """Tests loading a HAR with invalid JSON content."""
        with pytest.raises(ValueError):
            parse(invalid_bytes)

    def test_load_har_with_invalid_file_path(self) -> None:
        """Tests loading a HAR from a non-existent file path."""
        with pytest.raises(FileNotFoundError):
            parse(Path("non_existent_file.har"))

    def test_entry_selector_returns_default_entry(
        self, cleaned_entry: Dict[str, Any]
    ) -> None:
        def never_true_detector(entry: Dict[str, Any]) -> bool:
            return False

        register_entry_model(never_true_detector, DevToolsEntry)
        model = entry_selector(cleaned_entry)
        assert model is Entry

    def test_validate_empty_entries(self, cleaned_har: Dict[str, Any]) -> None:
        har = dict(cleaned_har)
        har["log"] = dict(har["log"])
        har["log"]["entries"] = []
        har_log = validate(har)
        assert isinstance(har_log, HarLog)
        assert har_log.entries == []

    def test_validate_multiple_entries(self, cleaned_har: Dict[str, Any]) -> None:
        har = dict(cleaned_har)
        har["log"] = dict(har["log"])
        entry = har["log"]["entries"][0]
        har["log"]["entries"] = [entry, entry]
        har_log = validate(har)
        assert isinstance(har_log, HarLog)
        assert len(har_log.entries) == 2
        assert all(isinstance(e, Entry) for e in har_log.entries)

    def test_validate_with_invalid_log_structure(
        self, cleaned_har: Dict[str, Any]
    ) -> None:
        har = dict(cleaned_har)
        har["log"] = "not a dict"
        with pytest.raises(ValueError):
            validate(har)

    def test_validate_with_invalid_entries(self, cleaned_har: Dict[str, Any]) -> None:
        har = dict(cleaned_har)
        har["log"] = dict(har["log"])
        har["log"]["entries"] = dict()
        with pytest.raises(ValueError):
            validate(har)

    def test_har_log_model_dump_preserves_extension_fields(self) -> None:
        """
        Test that har_log.model_dump() preserves
        Chrome DevTools extension fields at all levels.
        """
        har_log = parse(CHROME_DEVTOOLS_HAR_BYTES)
        dumped = har_log.model_dump()
        # Check that entries exists and is not empty
        assert "entries" in dumped
        assert len(dumped["entries"]) > 0
        entry_dump = dumped["entries"][0]
        # Check that DevTools extension fields are preserved
        assert "initiator" in entry_dump
        assert "connectionId" in entry_dump
        # Check that nested fields are preserved
        assert isinstance(entry_dump["initiator"], dict)
        assert entry_dump["initiator"]["type"] == "parser"
        assert "transferSize" in entry_dump["response"]
