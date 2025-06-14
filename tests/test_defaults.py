from typing import Any, Dict

import pytest

from hario_core.transform import by_field, json_array_handler, uuid


class TestDefaults:
    def test_by_field_deterministic(self, cleaned_entry: Dict[str, Any]) -> None:
        id_fn = by_field(["request.url", "startedDateTime"])
        id1 = id_fn(cleaned_entry)
        id2 = id_fn(cleaned_entry)
        assert id1 == id2

    def test_by_field_different_fields(self, cleaned_entry: Dict[str, Any]) -> None:
        from copy import deepcopy

        data1 = deepcopy(cleaned_entry)
        data2 = deepcopy(cleaned_entry)
        data2["request"]["url"] = "http://other-url.com"
        id_fn = by_field(["request.url", "startedDateTime"])
        id1 = id_fn(data1)
        id2 = id_fn(data2)
        assert id1 != id2

    def test_by_field_nested_field(self, cleaned_entry: Dict[str, Any]) -> None:
        id_fn = by_field(["response.content.mimeType"])
        id_val = id_fn(cleaned_entry)
        assert isinstance(id_val, str)
        assert len(id_val) == 32

    def test_by_field_dict_and_attr_access(self, cleaned_entry: Dict[str, Any]) -> None:
        orig_size = cleaned_entry["response"]["content"]["size"]
        id_fn = by_field(["response.content.size"])
        id_val = id_fn(cleaned_entry)
        assert id_val == id_fn(cleaned_entry)
        assert cleaned_entry["response"]["content"]["size"] == orig_size

    def test_uuid_different(self, cleaned_entry: Dict[str, Any]) -> None:
        id_fn = uuid()
        id1 = id_fn(cleaned_entry)
        id2 = id_fn(cleaned_entry)
        assert id1 != id2

    def test_by_field_missing_field(self, cleaned_entry: Dict[str, Any]) -> None:
        id_fn = by_field(["request.nonexistent"])
        with pytest.raises(KeyError):
            id_fn(cleaned_entry)

    def test_by_field_not_dict_raises_value_error(
        self, cleaned_entry: Dict[str, Any]
    ) -> None:
        # Make "url" a string, so the next step can't access "something"
        id_fn = by_field(["request.url.something"])
        with pytest.raises(
            ValueError, match="Field 'request.url.something' is not a dictionary"
        ):
            id_fn(cleaned_entry)

    def test_by_field_none_raises_value_error(
        self, cleaned_entry: Dict[str, Any]
    ) -> None:
        # Make "url" a string, so the next step can't access "something"
        cleaned_entry["request"]["nonexistent"] = None
        id_fn = by_field(["request.nonexistent"])
        with pytest.raises(ValueError, match="Field 'request.nonexistent' is None"):
            id_fn(cleaned_entry)
        # remove the None
        del cleaned_entry["request"]["nonexistent"]

    def test_uuid_unique(self, cleaned_entry: Dict[str, Any]) -> None:
        uuid_fn = uuid()
        ids = {uuid_fn(cleaned_entry) for _ in range(10)}
        assert len(ids) == 10
        for val in ids:
            assert isinstance(val, str)
            assert len(val) == 36

    def test_json_array_handler_empty(self) -> None:
        assert json_array_handler([], "some.path") == "[]"

    def test_json_array_handler_numbers(self) -> None:
        arr = [1, 2, 3]
        result = json_array_handler(arr, "numbers")
        assert result == "[1,2,3]"

    def test_json_array_handler_dicts(self) -> None:
        arr = [{"a": 1}, {"b": 2}]
        result = json_array_handler(arr, "dicts")
        # orjson.dumps returns compact JSON without spaces
        assert result == '[{"a":1},{"b":2}]'
