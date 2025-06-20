from typing import Any, Dict, List

import pytest

from hario_core.transform import (
    Pipeline,
    PipelineConfig,
    by_field,
    flatten,
    normalize_sizes,
    set_id,
    uuid,
)


class TestPipeline:
    @pytest.mark.parametrize(
        "entries_fixture", ["cleaned_entries", "chrome_devtools_entries"], indirect=True
    )
    def test_pipeline_basic(self, entries_fixture: List[Dict[str, Any]]) -> None:
        pipeline = Pipeline(
            transformers=[set_id(uuid())],
        )
        results = pipeline.process(entries_fixture)
        assert len(results) == 1
        assert "id" in results[0]
        assert results[0]["request"]["url"] == entries_fixture[0]["request"]["url"]

    def test_pipeline_custom_id_field(
        self, cleaned_entries: List[Dict[str, Any]]
    ) -> None:
        pipeline = Pipeline(
            transformers=[set_id(uuid(), id_field="custom_id")],
        )
        results = pipeline.process(cleaned_entries)
        assert "custom_id" in results[0]
        assert "id" not in results[0]

    def test_pipeline_with_transformer(
        self, cleaned_entries: List[Dict[str, Any]]
    ) -> None:
        pipeline = Pipeline(
            transformers=[set_id(uuid()), normalize_sizes()],
        )
        results = pipeline.process(cleaned_entries)
        assert results[0]["request"]["headersSize"] == 0

    def test_pipeline_with_deterministic_id(
        self, cleaned_entries: List[Dict[str, Any]], cleaned_entry: Dict[str, Any]
    ) -> None:
        id_generator = by_field(["request.url", "startedDateTime"])
        pipeline = Pipeline(
            transformers=[set_id(id_generator)],
        )
        id1 = id_generator(cleaned_entry)
        results = pipeline.process(cleaned_entries)
        assert results[0]["id"] == id1

    def test_pipeline_invalid_input_typeerror(self) -> None:
        pipeline = Pipeline(transformers=[set_id(uuid())])
        not_entries: Dict[str, Any] = {"entries": []}
        with pytest.raises(TypeError, match="Pipeline.process expects a list of dicts"):
            pipeline.process(not_entries)  # type: ignore

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
        cleaned_entries: List[Dict[str, Any]],
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
        results = pipeline.process(cleaned_entries)
        assert len(results) == len(cleaned_entries)
        assert "id" in results[0]
        assert results[0]["request.headersSize"] == 0
        assert "request.headers" in results[0]
        assert isinstance(results[0]["request.headers"], str)
