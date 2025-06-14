"""
Unit tests for transformation logic in hario-core.
"""

from copy import deepcopy
from typing import Any, Dict, List

import pytest

from hario_core.models import Entry
from hario_core.transform import flatten, normalize_sizes, normalize_timings


class TestTransform:
    def test_normalize_sizes(self, cleaned_entry: Dict[str, Any]) -> None:
        doc = deepcopy(cleaned_entry)
        doc["request"]["headersSize"] = -1
        doc["request"]["bodySize"] = 10
        doc["response"]["headersSize"] = -5
        doc["response"]["bodySize"] = -2
        doc["response"]["content"]["size"] = -100
        entry = Entry.model_validate(doc)
        result = normalize_sizes()(entry.model_dump())
        assert result["request"]["headersSize"] == 0
        assert result["response"]["bodySize"] == 0
        assert result["response"]["content"]["size"] == 0

    def test_normalize_timings(self, cleaned_entry: Dict[str, Any]) -> None:
        doc = deepcopy(cleaned_entry)
        doc["timings"]["blocked"] = -1
        doc["timings"]["dns"] = -2.5
        doc["timings"]["connect"] = 0
        doc["timings"]["send"] = 1
        doc["timings"]["wait"] = -0.1
        doc["timings"]["receive"] = -100
        doc["timings"]["ssl"] = -3
        entry = Entry.model_validate(doc)
        result = normalize_timings()(entry.model_dump())
        t = result["timings"]
        assert t["blocked"] == 0.0
        assert t["dns"] == 0.0
        assert t["wait"] == 0.0
        assert t["receive"] == 0.0
        assert t["ssl"] == 0.0
        assert t["connect"] == 0
        assert t["send"] == 1

    def test_entry_validation_error_on_missing_fields(
        self, cleaned_entry: Dict[str, Any]
    ) -> None:
        for field in [
            "request",
            "response",
            "timings",
            "time",
            "startedDateTime",
            "cache",
        ]:
            entry_missing = deepcopy(cleaned_entry)
            entry_missing.pop(field, None)
            with pytest.raises(Exception):
                Entry.model_validate(entry_missing)

    def test_flatten_basic_headers(self, cleaned_entry: Dict[str, Any]) -> None:
        entry = Entry.model_validate(cleaned_entry)
        flat = flatten()(entry.model_dump())
        # Check that nested keys became flat
        assert "request.headers" in flat
        assert isinstance(flat["request.headers"], str)
        assert "response.headers" in flat
        assert isinstance(flat["response.headers"], str)

    def test_flatten_custom_array_handler(self, cleaned_entry: Dict[str, Any]) -> None:
        entry = Entry.model_validate(cleaned_entry)
        # array_handler returns a string with path and array length
        flat = flatten(array_handler=lambda arr, path: f"{path}:{len(arr)}")(
            entry.model_dump()
        )
        assert "request.headers" in flat
        assert isinstance(flat["request.headers"], str)
        expected = f"request.headers:{len(cleaned_entry['request']['headers'])}"
        assert flat["request.headers"] == expected

    def test_flatten_separator(self, cleaned_entry: Dict[str, Any]) -> None:
        entry = Entry.model_validate(cleaned_entry)
        flat = flatten(separator="__")(entry.model_dump())
        assert "request__headers" in flat
        assert "response__headers" in flat

    def test_flatten_headers_to_keys_by_name(
        self, cleaned_entry: Dict[str, Any]
    ) -> None:
        from urllib.parse import quote

        def handler(arr: List[Dict[str, Any]], path: str) -> Any:
            return {
                f"{path}.{quote(item['name'], safe='')}": item["value"]
                for item in arr
                if isinstance(item, dict) and "name" in item and "value" in item
            }

        entry = Entry.model_validate(cleaned_entry)
        flat = flatten(array_handler=handler)(entry.model_dump())
        # Check for user-agent and :authority keys
        assert any("user-agent" in k for k in flat)
        assert any("%3Aauthority" in k for k in flat)
        # Value matches original
        headers = {h["name"]: h["value"] for h in cleaned_entry["request"]["headers"]}
        for k in flat:
            if "user-agent" in k:
                assert flat[k] == headers["user-agent"]
            if "%3Aauthority" in k:
                assert flat[k] == headers[":authority"]

    def test_flatten_default_array_handler_is_str(
        self, cleaned_entry: Dict[str, Any]
    ) -> None:
        entry = Entry.model_validate(cleaned_entry)
        flat = flatten()(entry.model_dump())
        # By default, headers is a string
        assert isinstance(flat["request.headers"], str)
        assert "user-agent" in flat["request.headers"]

    def test_flatten_array_handler_returns_multiple_keys(
        self, cleaned_entry: Dict[str, Any]
    ) -> None:
        def handler(arr: List[Dict[str, Any]], path: str) -> Any:
            return {
                f"{path}.len": len(arr),
                f"{path}.first_name": (
                    arr[0]["name"] if arr and "name" in arr[0] else None
                ),
            }

        entry = Entry.model_validate(cleaned_entry)
        flat = flatten(array_handler=handler)(entry.model_dump())
        assert flat["request.headers.len"] == len(cleaned_entry["request"]["headers"])
        assert (
            flat["request.headers.first_name"]
            == cleaned_entry["request"]["headers"][0]["name"]
        )

    def test_flatten_array_handler_returns_dict(
        self, cleaned_entry: Dict[str, Any]
    ) -> None:
        def handler(arr: List[Dict[str, Any]], path: str) -> Any:
            return {f"{path}.foo.bar": 1}

        entry = Entry.model_validate(cleaned_entry)
        flat = flatten(array_handler=handler)(entry.model_dump())
        # Key is as returned by handler, not escaped
        assert "request.headers.foo.bar" in flat
        assert flat["request.headers.foo.bar"] == 1

    def test_flatten_header_by_name(self, cleaned_entry: Dict[str, Any]) -> None:
        def handler(arr: List[Dict[str, Any]], path: str) -> Any:
            return {
                f"{path}_{item['name']}": item["value"]
                for item in arr
                if isinstance(item, dict) and "name" in item and "value" in item
            }

        entry = Entry.model_validate(cleaned_entry)
        flat = flatten(separator="_", array_handler=handler)(entry.model_dump())
        # There should be a key with the encoded ':authority' name
        assert "request_headers_:authority" in flat
        # Value should match the original
        headers = {h["name"]: h["value"] for h in cleaned_entry["request"]["headers"]}
        assert flat["request_headers_:authority"] == headers[":authority"]
