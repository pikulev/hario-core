import json
from typing import Any, Dict

from hario_core.har_parser import parse
from hario_core.models.har_1_2 import HarLog
from hario_core.pipeline import Pipeline
from hario_core.utils.id import by_field, uuid
from hario_core.utils.transform import normalize_sizes

from .samples import CLEAN_HAR


def test_pipeline_basic() -> None:
    pipeline = Pipeline(
        id_fn=uuid(),
    )
    har_log = parse(json.dumps(CLEAN_HAR).encode("utf-8"))
    results = pipeline.process(har_log)
    assert len(results) == 1
    assert "id" in results[0]
    assert results[0]["request"]["url"] == "http://example.com/clean"


def test_pipeline_custom_id_field(har_log: HarLog) -> None:
    pipeline = Pipeline(
        id_fn=uuid(),
        id_field="custom_id",
    )
    results = pipeline.process(har_log)
    assert "custom_id" in results[0]
    assert "id" not in results[0]


def test_pipeline_with_transformer(har_log: HarLog) -> None:
    pipeline = Pipeline(
        id_fn=uuid(),
        transformers=[normalize_sizes()],
    )
    results = pipeline.process(har_log)
    assert results[0]["request"]["headersSize"] == 100


def test_pipeline_with_deterministic_id(har_log: HarLog) -> None:
    pipeline = Pipeline(
        id_fn=by_field(["request.url", "startedDateTime"]),
    )
    results = pipeline.process(har_log)
    # Deterministic id should be the same for the same data
    id1 = pipeline.id_fn(har_log.entries[0])
    assert results[0]["id"] == id1


def test_pipeline_invalid_input_typeerror() -> None:
    pipeline = Pipeline(id_fn=uuid())
    # Pass non HarLog, but just dict
    not_harlog: Dict[str, Any] = {"entries": []}
    try:
        pipeline.process(not_harlog)  # type: ignore
    except TypeError as e:
        assert "Pipeline.process expects a HarLog" in str(e)
    else:
        assert False, "TypeError was not raised for invalid input"
