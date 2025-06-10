from typing import Any, Dict

import pytest

from hario_core.models.har_1_2 import Entry
from hario_core.utils.id import by_field, uuid


class TestId:
    def test_by_field_deterministic(self, cleaned_entry_model: Entry) -> None:
        id_fn = by_field(["request.url", "startedDateTime"])
        id1 = id_fn(cleaned_entry_model)
        id2 = id_fn(cleaned_entry_model)
        assert isinstance(id1, str)
        assert id1 == id2

    def test_by_field_different_fields(self, cleaned_entry: Dict[str, Any]) -> None:
        from copy import deepcopy

        data1 = deepcopy(cleaned_entry)
        data2 = deepcopy(cleaned_entry)
        entry1 = Entry.model_validate(data1)
        data2["request"]["url"] = "http://other-url.com"
        entry2 = Entry.model_validate(data2)
        id_fn = by_field(["request.url", "startedDateTime"])
        id1 = id_fn(entry1)
        id2 = id_fn(entry2)
        assert id1 != id2

    def test_by_field_nested_field(
        self, cleaned_entry_model: Entry, cleaned_entry: Dict[str, Any]
    ) -> None:
        id_fn = by_field(["response.content.mimeType"])
        id_val = id_fn(cleaned_entry_model)
        assert isinstance(id_val, str)
        assert len(id_val) == 32
        from copy import deepcopy

        data2 = deepcopy(cleaned_entry)
        data2["response"]["content"]["mimeType"] = "other/type"
        entry2 = Entry.model_validate(data2)
        id_val2 = id_fn(entry2)
        assert id_val != id_val2

    def test_by_field_missing_field(self, cleaned_entry_model: Entry) -> None:
        id_fn = by_field(["request.nonexistent"])
        with pytest.raises(AttributeError):
            id_fn(cleaned_entry_model)

    def test_uuid_unique(self, cleaned_entry_model: Entry) -> None:
        uuid_fn = uuid()
        ids = {uuid_fn(cleaned_entry_model) for _ in range(10)}
        assert len(ids) == 10
        for val in ids:
            assert isinstance(val, str)
            assert len(val) == 36

    def test_by_field_dict_and_attr_access(self, cleaned_entry_model: Entry) -> None:
        orig_size = cleaned_entry_model.response.content.size
        id_fn = by_field(["response.content.size"])
        id_val = id_fn(cleaned_entry_model)
        assert isinstance(id_val, str)
        assert len(id_val) == 32
        cleaned_entry_model.response.content.size = orig_size + 1
        id_val2 = id_fn(cleaned_entry_model)
        assert id_val != id_val2
        id_fn2 = by_field(["request.url"])
        id_val_obj = id_fn2(cleaned_entry_model)
        assert isinstance(id_val_obj, str)
        assert len(id_val_obj) == 32
