from typing import Any, Sequence

from hario_core.models.har_1_2 import HarLog
from hario_core.utils.id import EntryIdFn
from hario_core.utils.transform import Transformer

__all__ = ["Pipeline"]


class Pipeline:
    """
    Pipeline for processing HAR data (HarLog, Pydantic model).

    Args:
        id_fn: EntryIdFn
            A function that generates an ID for an entry.
        id_field: str
            The field name to store the generated ID.
            Defaults to "id".
        transformers: Sequence[Transformer]
            A sequence of transformers to apply to HAR entries.
            Defaults to an empty sequence.
    """

    def __init__(
        self,
        id_fn: EntryIdFn,
        id_field: str = "id",
        transformers: Sequence[Transformer] = (),
    ):
        self.id_fn = id_fn
        self.transformers = list(transformers)
        self.id_field = id_field

    def process(self, har_log: HarLog) -> list[dict[str, Any]]:
        """
        Process a HarLog object (already parsed HAR data, Pydantic model).
        Returns a list of transformed dicts with assigned IDs.
        """
        if not hasattr(har_log, "entries") or not isinstance(har_log.entries, list):
            raise TypeError(
                "Pipeline.process expects a HarLog (Pydantic model with .entries)"
            )
        results = []
        for entry in har_log.entries:
            entry_dict = entry.model_dump()
            for transform in self.transformers:
                entry_dict = transform(entry)
            id = self.id_fn(entry)
            entry_dict[self.id_field] = id
            results.append(entry_dict)
        return results
