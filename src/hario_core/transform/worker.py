from typing import Any, Dict, List

from hario_core.transform.interfaces import Transformer

_transformers: List[Transformer] = []


def init_worker(transformers: List[Transformer]) -> None:
    """
    Initialize the worker with the provided transformers.

    Args:
        transformers: List of transformers to apply
    """
    global _transformers
    _transformers = transformers


def process_entry(entry_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process an entry dictionary using the provided transformers.

    Args:
        entry_dict: Dictionary representing an entry
    """
    for transform in _transformers:
        entry_dict = transform(entry_dict)
    return entry_dict


def process_batch(
    batch: List[Dict[str, Any]], transformers: List[Transformer]
) -> List[Dict[str, Any]]:
    """
    Process a batch of entries using the provided transformers.

    Args:
        batch: List of entry dictionaries to process
        transformers: List of transformers to apply

    Returns:
        List of processed entry dictionaries
    """
    global _transformers
    _transformers = transformers
    return [process_entry(entry) for entry in batch]
