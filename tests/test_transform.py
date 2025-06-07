"""Tests for transformation logic."""
from hario_core.utils.transform import transform_har_entry_for_storage


def test_transform_max_depth() -> None:
    """Tests transformation by max nesting depth."""
    doc = {"level1": {"level2": {"level3": {"level4": "value"}}}}
    transformed = transform_har_entry_for_storage(doc)
    assert isinstance(transformed["level1"]["level2"]["level3"], str)


def test_transform_size_limit() -> None:
    """Tests transformation by max size."""
    large_list = [{"a": "b"}] * 5000
    doc = {"data": large_list}
    transformed = transform_har_entry_for_storage(doc)
    assert isinstance(transformed["data"], str)


def test_no_transform_needed() -> None:
    """Tests a document that does not require transformation."""
    doc = {"level1": {"key": "value"}, "list": [1, 2, 3]}
    original_doc = doc.copy()
    transformed = transform_har_entry_for_storage(doc)
    assert transformed == original_doc


def test_transform_with_no_content() -> None:
    """Tests transformation when response has no content field."""
    entry: dict[str, any] = {"response": {"status": 200}}
    transformed = transform_har_entry_for_storage(entry)
    assert "content" not in transformed["response"]


def test_transform_list_of_dicts() -> None:
    """Tests that a list of dictionaries is recursively transformed."""
    doc = {
        "level1": [
            {"level2_a": {"level3_a": "value"}},
            {"level2_b": {"level3_b": "value"}},
        ]
    }
    transformed = transform_har_entry_for_storage(doc)
    # The list itself should not be stringified
    assert isinstance(transformed["level1"], list)
    # But the nested dicts at level 3 inside the list should be
    assert isinstance(transformed["level1"][0]["level2_a"]["level3_a"], str)
    assert isinstance(transformed["level1"][1]["level2_b"]["level3_b"], str) 