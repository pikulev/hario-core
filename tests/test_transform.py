"""
Unit tests for transformation logic in hario-core.

- Test transformation of HAR entries for storage
  (stringifying deep/large structures).
- Cover edge cases for nested dicts, lists, and missing content.
"""

from copy import deepcopy
from typing import Any, Dict

import pytest

from hario_core.models.har_1_2 import Entry
from hario_core.utils.transform import flatten, normalize_sizes, normalize_timings

# Используем только реальные сэмплы через фикстуры


class TestTransform:
    def test_transform_max_depth(self, cleaned_entry: Dict[str, Any]) -> None:
        doc = deepcopy(cleaned_entry)
        doc["cache"]["level1"] = {"level2": {"level3": {"level4": "value"}}}
        entry = Entry.model_validate(doc)
        transformed = flatten()(entry)
        val = transformed["cache"]["level1"]
        if isinstance(val, Dict) and "level2" in val:
            val2 = val["level2"]
            if isinstance(val2, Dict) and "level3" in val2:
                assert isinstance(val2["level3"], str)
            else:
                assert isinstance(val2, str)
        else:
            assert isinstance(val, str)

    def test_transform_size_limit(self, cleaned_entry: Dict[str, Any]) -> None:
        doc = deepcopy(cleaned_entry)
        large_list = [{"a": "b"}] * 5000
        doc["cache"]["data"] = large_list
        entry = Entry.model_validate(doc)
        transformed = flatten()(entry)
        assert isinstance(transformed["cache"]["data"], str)

    def test_no_transform_needed(self, cleaned_entry: Dict[str, Any]) -> None:
        doc = deepcopy(cleaned_entry)
        doc["cache"]["level1"] = {"key": "value"}
        doc["cache"]["list"] = [1, 2, 3]
        entry = Entry.model_validate(doc)
        original_doc = entry.model_dump()
        transformed = flatten()(entry)
        assert transformed == original_doc

    def test_transform_with_no_content(self, cleaned_entry: Dict[str, Any]) -> None:
        doc = deepcopy(cleaned_entry)
        doc["response"]["status"] = 200
        entry = Entry.model_validate(doc)
        transformed = flatten()(entry)
        assert "content" in transformed["response"]
        assert transformed["response"]["status"] == 200

    def test_transform_list_of_dicts(self, cleaned_entry: Dict[str, Any]) -> None:
        doc = deepcopy(cleaned_entry)
        doc["cache"]["level1"] = [
            {"level2_a": {"level3_a": {"level4_a": "value"}}},
            {"level2_b": {"level3_b": "value"}},
        ]
        entry = Entry.model_validate(doc)
        transformed = flatten()(entry)
        assert isinstance(transformed["cache"]["level1"], list)
        val = transformed["cache"]["level1"][0]["level2_a"]
        if isinstance(val, Dict) and "level3_a" in val:
            assert isinstance(val["level3_a"], str)
        else:
            assert isinstance(val, str)
        val2 = transformed["cache"]["level1"][1]["level2_b"]
        assert isinstance(val2, (Dict, str))

    def test_flatten_depth_and_size_limit(self, cleaned_entry: Dict[str, Any]) -> None:
        doc = deepcopy(cleaned_entry)
        doc["cache"]["a"] = {"b": {"c": {"d": [1, 2, 3]}}}
        entry = Entry.model_validate(doc)
        flat = flatten(max_depth=2)(entry)
        val = flat["cache"]["a"]
        if isinstance(val, Dict) and "b" in val:
            bval = val["b"]
            assert isinstance(bval, str)
            assert '"c": {"d": [1, 2, 3]}' in bval
        else:
            assert isinstance(val, str)
        big_list = list(range(10000))
        doc2 = deepcopy(cleaned_entry)
        doc2["cache"]["arr"] = big_list
        entry2 = Entry.model_validate(doc2)
        flat2 = flatten(size_limit=100)(entry2)
        assert isinstance(flat2["cache"]["arr"], str)
        doc3 = deepcopy(cleaned_entry)
        doc3["cache"]["x"] = 1
        doc3["cache"]["y"] = [1, 2, 3]
        entry3 = Entry.model_validate(doc3)
        flat3 = flatten()(entry3)
        assert flat3["cache"]["x"] == 1
        assert flat3["cache"]["y"] == [1, 2, 3]

    def test_normalize_sizes(self, cleaned_entry: Dict[str, Any]) -> None:
        doc = deepcopy(cleaned_entry)
        doc["request"]["headersSize"] = -1
        doc["request"]["bodySize"] = 10
        doc["response"]["headersSize"] = -5
        doc["response"]["bodySize"] = -2
        doc["response"]["content"]["size"] = -100
        entry = Entry.model_validate(doc)
        result = normalize_sizes()(entry)
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
        result = normalize_timings()(entry)
        t = result["timings"]
        assert t["blocked"] == 0.0
        assert t["dns"] == 0.0
        assert t["wait"] == 0.0
        assert t["receive"] == 0.0
        assert t["ssl"] == 0.0
        assert t["connect"] == 0
        assert t["send"] == 1

    def test_flatten_empty_and_noop(self, cleaned_entry_model: Entry) -> None:
        flat = flatten()(cleaned_entry_model)
        assert flat == cleaned_entry_model.model_dump()
        doc2 = deepcopy(cleaned_entry_model.model_dump())
        doc2["cache"]["a"] = 1
        doc2["cache"]["b"] = 2
        entry2 = Entry.model_validate(doc2)
        flat2 = flatten()(entry2)
        assert flat2 == entry2.model_dump()
        entry3 = deepcopy(cleaned_entry_model)
        entry3.cache["a"] = {}
        flat3 = flatten()(entry3)
        assert flat3 == entry3.model_dump()

    def test_flatten_non_dict_input(self) -> None:
        try:
            flatten()([1, 2, 3])  # type: ignore
        except Exception:
            pass
        else:
            assert False, "flatten should raise an error on non-Dict"

    def test_flatten_basic(self, cleaned_entry_model: Entry) -> None:
        flat = flatten()(cleaned_entry_model)
        assert isinstance(flat, Dict)
        assert "request" in flat

    def test_flatten_deep_structure(self, cleaned_entry_model: Entry) -> None:
        entry = deepcopy(cleaned_entry_model)
        entry.cache["deep"] = {"a": {"b": {"c": {"d": 1}}}}
        flat = flatten(max_depth=2)(entry)
        val = flat["cache"]["deep"]
        if isinstance(val, Dict) and "a" in val:
            aval = val["a"]
            if isinstance(aval, Dict) and "b" in aval:
                bval = aval["b"]
                assert isinstance(bval, str)
            else:
                assert isinstance(aval, str)
        else:
            assert isinstance(val, str)

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
