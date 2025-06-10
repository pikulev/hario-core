from typing import Any, Dict

import pytest

from hario_core.models.har_1_2 import HarLog
from hario_core.pipeline import Pipeline
from hario_core.utils.id import by_field, uuid
from hario_core.utils.transform import normalize_sizes


class TestPipeline:
    def test_pipeline_basic(self, cleaned_log: HarLog) -> None:
        pipeline = Pipeline(
            id_fn=uuid(),
        )
        results = pipeline.process(cleaned_log)
        assert len(results) == 1
        assert "id" in results[0]
        assert (
            results[0]["request"]["url"] == "https://test.test/assets/css/f2aaccf1.css"
        )

    def test_pipeline_custom_id_field(self, cleaned_log: HarLog) -> None:
        pipeline = Pipeline(
            id_fn=uuid(),
            id_field="custom_id",
        )
        results = pipeline.process(cleaned_log)
        assert "custom_id" in results[0]
        assert "id" not in results[0]

    def test_pipeline_with_transformer(self, cleaned_log: HarLog) -> None:
        pipeline = Pipeline(
            id_fn=uuid(),
            transformers=[normalize_sizes()],
        )
        results = pipeline.process(cleaned_log)
        assert results[0]["request"]["headersSize"] == 0

    def test_pipeline_with_deterministic_id(self, cleaned_log: HarLog) -> None:
        pipeline = Pipeline(
            id_fn=by_field(["request.url", "startedDateTime"]),
        )
        results = pipeline.process(cleaned_log)
        id1 = pipeline.id_fn(cleaned_log.entries[0])
        assert results[0]["id"] == id1

    def test_pipeline_invalid_input_typeerror(self) -> None:
        pipeline = Pipeline(id_fn=uuid())
        not_harlog: Dict[str, Any] = {"entries": []}
        with pytest.raises(TypeError, match="Pipeline.process expects a HarLog"):
            pipeline.process(not_harlog)  # type: ignore
