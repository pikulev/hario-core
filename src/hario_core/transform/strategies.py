from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from hario_core.transform.interfaces import Transformer
from hario_core.transform.worker import init_worker, process_batch


class ProcessingStrategy(ABC):
    """
    Abstract base class for processing strategies.

    Args:
        batches: List[List[Dict[str, Any]]]
            A list of batches of HAR entries to process.
        transformers: List[Transformer]
            A list of transformers to apply to the HAR entries.

    Returns:
        List[Dict[str, Any]]
    """

    @abstractmethod
    def process_batches(
        self, batches: List[List[Dict[str, Any]]], transformers: List[Transformer]
    ) -> List[Dict[str, Any]]:
        pass


class ProcessPoolStrategy(ProcessingStrategy):
    """
    Processing strategy that uses a ProcessPoolExecutor to process batches in parallel.
    """

    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers

    def process_batches(
        self, batches: List[List[Dict[str, Any]]], transformers: List[Transformer]
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        with ProcessPoolExecutor(
            max_workers=self.max_workers,
            initializer=init_worker,
            initargs=(transformers,),
        ) as executor:
            futures = [
                executor.submit(process_batch, batch, transformers) for batch in batches
            ]
            for future in as_completed(futures):
                results.extend(future.result())
        return results


class ThreadPoolStrategy(ProcessingStrategy):
    """
    Processing strategy that uses a ThreadPoolExecutor to process batches in parallel.
    """

    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers

    def process_batches(
        self, batches: List[List[Dict[str, Any]]], transformers: List[Transformer]
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(process_batch, batch, transformers) for batch in batches
            ]
            for future in as_completed(futures):
                results.extend(future.result())
        return results


class SequentialStrategy(ProcessingStrategy):
    """
    Processing strategy that processes batches sequentially.
    """

    def process_batches(
        self, batches: List[List[Dict[str, Any]]], transformers: List[Transformer]
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for batch in batches:
            results.extend(process_batch(batch, transformers))
        return results


class AsyncStrategy(ProcessingStrategy):
    """
    Processing strategy that processes batches asynchronously.
    """

    def process_batches(
        self, batches: List[List[Dict[str, Any]]], transformers: List[Transformer]
    ) -> List[Dict[str, Any]]:
        import asyncio

        async def process_batch_async(
            batch: List[Dict[str, Any]]
        ) -> List[Dict[str, Any]]:
            return process_batch(batch, transformers)

        async def process_all() -> List[List[Dict[str, Any]]]:
            tasks = [process_batch_async(batch) for batch in batches]
            return await asyncio.gather(*tasks)

        results = asyncio.run(process_all())
        return [item for sublist in results for item in sublist]
