from typing import Any, Dict

import pytest

from hario_core.models.har_1_2 import HarLog
from hario_core.pipeline import Pipeline, PipelineConfig
from hario_core.utils.defaults import by_field, uuid
from hario_core.utils.transform import flatten, normalize_sizes, set_id


class TestPipeline:
    def test_pipeline_basic(self, cleaned_log: HarLog) -> None:
        pipeline = Pipeline(
            transformers=[set_id(uuid())],
        )
        results = pipeline.process(cleaned_log)
        assert len(results) == 1
        assert "id" in results[0]
        assert (
            results[0]["request"]["url"] == "https://test.test/assets/css/f2aaccf1.css"
        )

    def test_pipeline_custom_id_field(self, cleaned_log: HarLog) -> None:
        pipeline = Pipeline(
            transformers=[set_id(uuid(), id_field="custom_id")],
        )
        results = pipeline.process(cleaned_log)
        assert "custom_id" in results[0]
        assert "id" not in results[0]

    def test_pipeline_with_transformer(self, cleaned_log: HarLog) -> None:
        pipeline = Pipeline(
            transformers=[set_id(uuid()), normalize_sizes()],
        )
        results = pipeline.process(cleaned_log)
        assert results[0]["request"]["headersSize"] == 0

    def test_pipeline_with_deterministic_id(
        self, cleaned_log: HarLog, cleaned_entry: Dict[str, Any]
    ) -> None:
        id_generator = by_field(["request.url", "startedDateTime"])
        pipeline = Pipeline(
            transformers=[set_id(id_generator)],
        )
        results = pipeline.process(cleaned_log)
        id1 = id_generator(cleaned_entry)
        assert results[0]["id"] == id1

    def test_pipeline_invalid_input_typeerror(self) -> None:
        pipeline = Pipeline(transformers=[set_id(uuid())])
        not_harlog: Dict[str, Any] = {"entries": []}
        with pytest.raises(TypeError, match="Pipeline.process expects a HarLog"):
            pipeline.process(not_harlog)  # type: ignore

    @pytest.mark.parametrize(
        "config",
        [
            PipelineConfig(
                batch_size=2,
                processing_strategy="process",
                max_workers=4,
            ),
            PipelineConfig(
                batch_size=2,
                processing_strategy="thread",
                max_workers=4,
            ),
            PipelineConfig(
                batch_size=2, processing_strategy="sequential", max_workers=None
            ),
            PipelineConfig(batch_size=2, processing_strategy="async", max_workers=None),
        ],
    )
    def test_pipeline_strategies(
        self,
        cleaned_log: HarLog,
        config: PipelineConfig,
    ) -> None:
        """Test Pipeline with different processing strategies."""
        pipeline = Pipeline(
            transformers=[
                set_id(by_field(["request.url", "startedDateTime"])),
                normalize_sizes(),
                flatten(),
            ],
            config=config,
        )

        results = pipeline.process(cleaned_log)

        assert len(results) == len(cleaned_log.entries)
        assert "id" in results[0]
        assert results[0]["request.headersSize"] == 0
        assert "request.headers" in results[0]
        assert isinstance(results[0]["request.headers"], str)
