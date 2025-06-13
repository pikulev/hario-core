import sys
import time
import tracemalloc
import hashlib
import orjson
from typing import Dict, Tuple, Any
import gc
import psutil
import os
import csv
from rich.table import Table

from hario_core import (
    Pipeline,
    PipelineConfig,
    by_field,
    flatten,
    normalize_sizes,
    normalize_timings,
    set_id,
    parse,
)

REPEAT = 5
BATCH_SIZE = 12
MAX_WORKERS = 6

HAR_PATH = "benchmarks/test_lg.har"
STRATEGIES = ["process", "thread", "sequential", "async"]

def get_entries(har_path: str) -> dict:
    """
    Get entries from HAR file.
    """
    har_log = parse(har_path)
    return har_log.model_dump()['entries']


def bench_flatten(entries: dict, strategy: str, use_gc: bool = True) -> Tuple[float, int, int, int]:
    config = PipelineConfig(
        batch_size=BATCH_SIZE,
        processing_strategy=strategy,
        max_workers=MAX_WORKERS if strategy in ["process", "thread"] else None,
    )
    pipeline = Pipeline(
        transformers=[set_id(by_field(["request.url", "startedDateTime"])), flatten()],
        config=config,
    )
    return run_pipeline(pipeline, entries, f"flatten ({strategy})", use_gc=use_gc)


def bench_normalize_sizes(entries: dict, strategy: str, use_gc: bool = True) -> Tuple[float, int, int, int]:
    config = PipelineConfig(
        batch_size=BATCH_SIZE,
        processing_strategy=strategy,
        max_workers=MAX_WORKERS if strategy in ["process", "thread"] else None,
    )
    pipeline = Pipeline(
        transformers=[set_id(by_field(["request.url", "startedDateTime"])), normalize_sizes()],
        config=config,
    )
    return run_pipeline(pipeline, entries, f"normalize_sizes ({strategy})", use_gc=use_gc)


def bench_normalize_timings(entries: dict, strategy: str, use_gc: bool = True) -> Tuple[float, int, int, int]:
    config = PipelineConfig(
        batch_size=BATCH_SIZE,
        processing_strategy=strategy,
        max_workers=MAX_WORKERS if strategy in ["process", "thread"] else None,
    )
    pipeline = Pipeline(
        transformers=[set_id(by_field(["request.url", "startedDateTime"])), normalize_timings()],
        config=config,
    )
    return run_pipeline(pipeline, entries, f"normalize_timings ({strategy})", use_gc=use_gc)


def bench_full(entries: dict, strategy: str, use_gc: bool = True) -> Tuple[float, int, int, int]:
    config = PipelineConfig(
        batch_size=BATCH_SIZE,
        processing_strategy=strategy,
        max_workers=MAX_WORKERS if strategy in ["process", "thread"] else None,
    )
    pipeline = Pipeline(
        transformers=[
            set_id(by_field(["request.url", "startedDateTime"])),
            normalize_sizes(),
            normalize_timings(),
            flatten(),
        ],
        config=config,
    )
    return run_pipeline(pipeline, entries, f"full pipeline ({strategy})", use_gc=use_gc)


class CpuHeavy:
    def __call__(self, data: Dict[str, Any]) -> Dict[str, Any]:
        payload = orjson.dumps(data)
        for _ in range(1000):
            payload = hashlib.sha256(payload).digest()
        data["cpu_hash"] = payload.hex()
        return data


def cpu_heavy_transformer() -> CpuHeavy:
    return CpuHeavy()


def bench_cpu_heavy(entries: dict, strategy: str, use_gc: bool = True) -> Tuple[float, int, int, int]:
    config = PipelineConfig(
        batch_size=BATCH_SIZE,
        processing_strategy=strategy,
        max_workers=MAX_WORKERS if strategy in ["process", "thread"] else None,
    )
    pipeline = Pipeline(
        transformers=[set_id(by_field(["request.url", "startedDateTime"])), cpu_heavy_transformer(), flatten()],
        config=config,
    )
    return run_pipeline(pipeline, entries, f"cpu_heavy_transformer ({strategy})", use_gc=use_gc)


def run_pipeline(pipeline: Pipeline, entries: dict, label: str, use_gc: bool = True) -> Tuple[float, int, int, int]:
    if use_gc:
        gc.collect()
    else:
        gc.disable()
    tracemalloc.start()
    start = time.perf_counter()
    result = pipeline.process(entries)
    elapsed = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    rss = psutil.Process(os.getpid()).memory_info().rss
    if not use_gc:
        gc.enable()
    return elapsed, current, peak, rss


def average_run(bench_func, entries: dict, strategy: str, use_gc: bool = True):
    times = []
    currents = []
    peaks = []
    rss_list = []
    for _ in range(REPEAT):
        elapsed, current, peak, rss = bench_func(entries, strategy, use_gc=use_gc)
        times.append(elapsed)
        currents.append(current)
        peaks.append(peak)
        rss_list.append(rss)
    n = REPEAT
    return (
        sum(times) / n,
        sum(currents) / n,
        sum(peaks) / n,
        sum(rss_list) / n,
    )


def create_results_table(results: Dict[str, Dict[str, Tuple[float, int, int, int]]]) -> Table:
    table = Table(title="Benchmark Results")
    table.add_column("Test", style="cyan")
    for strategy in STRATEGIES:
        table.add_column(strategy, justify="right", style="green")
    for test_name in results[STRATEGIES[0]].keys():
        row = [test_name]
        for strategy in STRATEGIES:
            elapsed, current, peak, rss = results[strategy][test_name]
            row.append(f"{elapsed:.3f}s\nPyHeap: {current/1024/1024:.1f}MB\nPyPeak: {peak/1024/1024:.1f}MB\nRSS: {rss/1024/1024:.1f}MB")
        table.add_row(*row)
    return table


def create_results_csv(results: Dict[str, Dict[str, tuple]], filename: str = None):
    fieldnames = ["Test"] + [f"{strategy}_elapsed" for strategy in STRATEGIES] + [f"{strategy}_pyheap" for strategy in STRATEGIES] + [f"{strategy}_pypeak" for strategy in STRATEGIES] + [f"{strategy}_rss" for strategy in STRATEGIES]
    rows = []
    for test_name in results[STRATEGIES[0]].keys():
        row = {"Test": test_name}
        for strategy in STRATEGIES:
            elapsed, current, peak, rss = results[strategy][test_name]
            row[f"{strategy}_elapsed"] = f"{elapsed:.6f}"
            row[f"{strategy}_pyheap"] = f"{current/1024/1024:.2f}"
            row[f"{strategy}_pypeak"] = f"{peak/1024/1024:.2f}"
            row[f"{strategy}_rss"] = f"{rss/1024/1024:.2f}"
        rows.append(row)
    if filename:
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)