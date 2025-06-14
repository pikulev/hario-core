from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Sequence

from hario_core.transform.interfaces import Processor, ProcessorConfig, Transformer
from hario_core.transform.strategies import (
    AsyncStrategy,
    ProcessingStrategy,
    ProcessPoolStrategy,
    SequentialStrategy,
    ThreadPoolStrategy,
)


def _chunked(seq: list[Any], size: int) -> list[list[Any]]:
    return [seq[i : i + size] for i in range(0, len(seq), size)]


@dataclass
class PipelineConfig(ProcessorConfig):
    batch_size: int = 20000
    processing_strategy: str = "sequential"
    max_workers: Optional[int] = None


DEFAULT_PIPELINE_CONFIG = PipelineConfig()


class Pipeline(Processor):
    """
    Pipeline for processing HAR data (HarLog, Pydantic model).
    Uses threading for parallel transformation.

    Args:
        transformers: Sequence[Transformer]
            A sequence of transformers to apply to HAR entries.
            Defaults to an empty sequence.
        config: PipelineConfig
            Configuration object with batch_size, processing_strategy, max_workers.
            If not provided, uses DEFAULT_PIPELINE_CONFIG.
    """

    def __init__(
        self,
        transformers: Sequence[Transformer] = (),
        config: PipelineConfig = DEFAULT_PIPELINE_CONFIG,
    ):
        self.transformers = list(transformers)
        self.config = config
        self.batch_size = self.config.batch_size
        self.strategy = self._get_strategy(
            self.config.processing_strategy, self.config.max_workers
        )

    def _get_strategy(
        self, strategy_name: str, max_workers: Optional[int]
    ) -> ProcessingStrategy:
        strategies = {
            "process": ProcessPoolStrategy(max_workers),
            "thread": ThreadPoolStrategy(max_workers),
            "sequential": SequentialStrategy(),
            "async": AsyncStrategy(),
        }
        return strategies.get(strategy_name, ProcessPoolStrategy(max_workers))

    def process(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Process a list of HAR entry dicts (model_dump'ed entries).
        Returns a list of transformed dicts with assigned IDs.
        """
        if not isinstance(entries, list) or (
            entries and not isinstance(entries[0], dict)
        ):
            raise TypeError(
                "Pipeline.process expects a list of dicts (model_dump'ed entries)"
            )
        batches = _chunked(entries, self.batch_size)
        return self.strategy.process_batches(batches, self.transformers)
