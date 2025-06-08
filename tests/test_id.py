import pytest

from hario_core.models.har_1_2 import Entry
from hario_core.utils.id import by_field, uuid

from .conftest import TestEntryMixin


class TestId(TestEntryMixin):
    def test_by_field_deterministic(self, har_entry: Entry) -> None:
        id_fn = by_field(["request.url", "startedDateTime"])
        id1 = id_fn(har_entry)
        id2 = id_fn(har_entry)
        assert isinstance(id1, str)
        assert id1 == id2

    def test_by_field_different_fields(self, har_entry: Entry) -> None:
        data1 = self.base_dict()
        data2 = self.base_dict()
        entry1 = self.make_entry(data1)
        data2["request"]["url"] = "http://other-url.com"
        entry2 = self.make_entry(data2)
        id_fn = by_field(["request.url", "startedDateTime"])
        id1 = id_fn(entry1)
        id2 = id_fn(entry2)
        assert id1 != id2

    def test_by_field_nested_field(self, har_entry: Entry) -> None:
        id_fn = by_field(["response.content.mimeType"])
        id_val = id_fn(har_entry)
        assert isinstance(id_val, str)
        assert len(id_val) == 32
        data2 = self.base_dict()
        data2["response"]["content"]["mimeType"] = "other/type"
        entry2 = self.make_entry(data2)
        id_val2 = id_fn(entry2)
        assert id_val != id_val2

    def test_by_field_missing_field(self, har_entry: Entry) -> None:
        id_fn = by_field(["request.nonexistent"])
        with pytest.raises(AttributeError):
            id_fn(har_entry)

    def test_uuid_unique(self, har_entry: Entry) -> None:
        uuid_fn = uuid()
        ids = {uuid_fn(har_entry) for _ in range(10)}
        assert len(ids) == 10
        for val in ids:
            assert isinstance(val, str)
            assert len(val) == 36

    def test_by_field_dict_and_attr_access(self, har_entry: Entry) -> None:
        orig_size = har_entry.response.content.size
        id_fn = by_field(["response.content.size"])
        id_val = id_fn(har_entry)
        assert isinstance(id_val, str)
        assert len(id_val) == 32
        har_entry.response.content.size = orig_size + 1
        id_val2 = id_fn(har_entry)
        assert id_val != id_val2
        id_fn2 = by_field(["request.url"])
        id_val_obj = id_fn2(har_entry)
        assert isinstance(id_val_obj, str)
        assert len(id_val_obj) == 32
