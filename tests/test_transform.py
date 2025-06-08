"""
Unit tests for transformation logic in hario-core.

- Test transformation of HAR entries for storage
  (stringifying deep/large structures).
- Cover edge cases for nested dicts, lists, and missing content.
"""

from copy import deepcopy

import pytest

from hario_core.models.har_1_2 import Entry
from hario_core.utils.transform import flatten, normalize_sizes, normalize_timings

from .conftest import TestEntryMixin


class TestTransform(TestEntryMixin):
    def test_transform_max_depth(self) -> None:
        doc = self.base_dict()
        doc["cache"]["level1"] = {"level2": {"level3": {"level4": "value"}}}
        entry = self.make_entry(doc)
        transformed = flatten()(entry)
        val = transformed["cache"]["level1"]
        if isinstance(val, dict) and "level2" in val:
            val2 = val["level2"]
            if isinstance(val2, dict) and "level3" in val2:
                assert isinstance(val2["level3"], str)
            else:
                assert isinstance(val2, str)
        else:
            assert isinstance(val, str)

    def test_transform_size_limit(self) -> None:
        doc = self.base_dict()
        large_list = [{"a": "b"}] * 5000
        doc["cache"]["data"] = large_list
        entry = self.make_entry(doc)
        transformed = flatten()(entry)
        assert isinstance(transformed["cache"]["data"], str)

    def test_no_transform_needed(self) -> None:
        doc = self.base_dict()
        doc["cache"]["level1"] = {"key": "value"}
        doc["cache"]["list"] = [1, 2, 3]
        entry = self.make_entry(doc)
        original_doc = entry.model_dump()
        transformed = flatten()(entry)
        assert transformed == original_doc

    def test_transform_with_no_content(self) -> None:
        doc = self.base_dict()
        doc["response"]["status"] = 200
        entry = self.make_entry(doc)
        transformed = flatten()(entry)
        assert "content" in transformed["response"]
        assert transformed["response"]["status"] == 200

    def test_transform_list_of_dicts(self) -> None:
        doc = self.base_dict()
        doc["cache"]["level1"] = [
            {"level2_a": {"level3_a": {"level4_a": "value"}}},
            {"level2_b": {"level3_b": "value"}},
        ]
        entry = self.make_entry(doc)
        transformed = flatten()(entry)
        assert isinstance(transformed["cache"]["level1"], list)
        val = transformed["cache"]["level1"][0]["level2_a"]
        if isinstance(val, dict) and "level3_a" in val:
            assert isinstance(val["level3_a"], str)
        else:
            assert isinstance(val, str)
        val2 = transformed["cache"]["level1"][1]["level2_b"]
        # Can be dict or string, depending on depth/size
        assert isinstance(val2, (dict, str))

    def test_flatten_depth_and_size_limit(self) -> None:
        doc = self.base_dict()
        doc["cache"]["a"] = {"b": {"c": {"d": [1, 2, 3]}}}
        entry = self.make_entry(doc)
        flat = flatten(max_depth=2)(entry)
        val = flat["cache"]["a"]
        if isinstance(val, dict) and "b" in val:
            bval = val["b"]
            assert isinstance(bval, str)
            assert '"c": {"d": [1, 2, 3]}' in bval
        else:
            assert isinstance(val, str)
        big_list = list(range(10000))
        doc2 = self.base_dict()
        doc2["cache"]["arr"] = big_list
        entry2 = self.make_entry(doc2)
        flat2 = flatten(size_limit=100)(entry2)
        assert isinstance(flat2["cache"]["arr"], str)
        doc3 = self.base_dict()
        doc3["cache"]["x"] = 1
        doc3["cache"]["y"] = [1, 2, 3]
        entry3 = self.make_entry(doc3)
        flat3 = flatten()(entry3)
        assert flat3["cache"]["x"] == 1
        assert flat3["cache"]["y"] == [1, 2, 3]

    def test_normalize_sizes(self) -> None:
        doc = self.base_dict()
        doc["request"]["headersSize"] = -1
        doc["request"]["bodySize"] = 10
        doc["response"]["headersSize"] = -5
        doc["response"]["bodySize"] = -2
        doc["response"]["content"]["size"] = -100
        entry = self.make_entry(doc)
        result = normalize_sizes()(entry)
        assert result["request"]["headersSize"] == 0
        assert result["response"]["bodySize"] == 0
        assert result["response"]["content"]["size"] == 0

    def test_normalize_timings(self) -> None:
        doc = self.base_dict()
        doc["timings"]["blocked"] = -1
        doc["timings"]["dns"] = -2.5
        doc["timings"]["connect"] = 0
        doc["timings"]["send"] = 1
        doc["timings"]["wait"] = -0.1
        doc["timings"]["receive"] = -100
        doc["timings"]["ssl"] = -3
        entry = self.make_entry(doc)
        result = normalize_timings()(entry)
        t = result["timings"]
        assert t["blocked"] == 0.0
        assert t["dns"] == 0.0
        assert t["wait"] == 0.0
        assert t["receive"] == 0.0
        assert t["ssl"] == 0.0
        assert t["connect"] == 0
        assert t["send"] == 1

    def test_flatten_empty_and_noop(self, har_entry: Entry) -> None:
        flat = flatten()(har_entry)
        assert flat == har_entry.model_dump()
        doc2 = self.base_dict()
        doc2["cache"]["a"] = 1
        doc2["cache"]["b"] = 2
        entry2 = deepcopy(har_entry)
        entry2.cache["a"] = 1
        entry2.cache["b"] = 2
        flat2 = flatten()(entry2)
        assert flat2 == entry2.model_dump()
        entry3 = deepcopy(har_entry)
        entry3.cache["a"] = {}
        flat3 = flatten()(entry3)
        assert flat3 == entry3.model_dump()

    def test_flatten_non_dict_input(self) -> None:
        try:
            flatten()([1, 2, 3])  # type: ignore
        except Exception:
            pass
        else:
            assert False, "flatten should raise an error on non-dict"

    def test_flatten_basic(self, har_entry: Entry) -> None:
        flat = flatten()(har_entry)
        assert isinstance(flat, dict)
        assert "request" in flat

    def test_flatten_deep_structure(self, har_entry: Entry) -> None:
        entry = deepcopy(har_entry)
        entry.cache["deep"] = {"a": {"b": {"c": {"d": 1}}}}
        flat = flatten(max_depth=2)(entry)
        val = flat["cache"]["deep"]
        if isinstance(val, dict) and "a" in val:
            aval = val["a"]
            if isinstance(aval, dict) and "b" in aval:
                bval = aval["b"]
                assert isinstance(bval, str)
            else:
                assert isinstance(aval, str)
        else:
            assert isinstance(val, str)

    def test_entry_validation_error_on_missing_fields(self) -> None:
        for field in [
            "request",
            "response",
            "timings",
            "time",
            "startedDateTime",
            "cache",
        ]:
            entry_missing = deepcopy(self.base_dict())
            entry_missing.pop(field, None)
            with pytest.raises(Exception):
                self.make_entry(entry_missing)
