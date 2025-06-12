import sys
import time
import tracemalloc
import cProfile
import pstats

from hario_core import (
    parse,
    Pipeline,
    by_field,
    stringify,
    flatten,
    normalize_sizes
)

HAR_PATH = "benchmarks/test_lg.har"

def bench_stringify(har_log):
    pipeline = Pipeline(
        id_fn=by_field(["request.url", "startedDateTime"]),
        transformers=[stringify()],
    )
    return run_pipeline(pipeline, har_log, "stringify")

def bench_flatten(har_log):
    pipeline = Pipeline(
        id_fn=by_field(["request.url", "startedDateTime"]),
        transformers=[flatten()],
    )
    return run_pipeline(pipeline, har_log, "flatten")

def bench_normalize(har_log):
    pipeline = Pipeline(
        id_fn=by_field(["request.url", "startedDateTime"]),
        transformers=[normalize_sizes()],
    )
    return run_pipeline(pipeline, har_log, "normalize_sizes")

def bench_full(har_log):
    pipeline = Pipeline(
        id_fn=by_field(["request.url", "startedDateTime"]),
        transformers=[stringify(), flatten(), normalize_sizes()],
    )
    return run_pipeline(pipeline, har_log, "full pipeline")

def run_pipeline(pipeline, har_log, label):
    print(f"\n--- Benchmark: {label} ---")
    tracemalloc.start()
    start = time.perf_counter()
    result = pipeline.process(har_log)
    elapsed = time.perf_counter() - start
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Processed {len(result)} entries in {elapsed:.3f} seconds.")
    print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")
    print(f"Average per entry: {elapsed / len(result):.6f} seconds.")
    return elapsed, current, peak

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in {"stringify", "flatten", "normalize", "full"}:
        print("Usage: python measure.py [stringify|flatten|normalize|full] [--profile]")
        sys.exit(1)
    mode = sys.argv[1]
    do_profile = "--profile" in sys.argv

    print("Loading HAR file...")
    har_log = parse(HAR_PATH)
    print(f"Loaded {len(har_log.entries)} entries.")

    bench_map = {
        "stringify": bench_stringify,
        "flatten": bench_flatten,
        "normalize": bench_normalize,
        "full": bench_full,
    }

    bench_func = bench_map[mode]
    profile_file = f"benchmarks/{mode}.stats"

    if do_profile:
        print(f"Profiling... profile saved in {profile_file}")
        cProfile.runctx('bench_func(har_log)', globals(), locals(), profile_file)
        p = pstats.Stats(profile_file)
        print("\n=== TOP-20 functions by cumtime ===\n")
        p.strip_dirs().sort_stats('cumtime').print_stats(20)
        print(f"\n=== For visualization, run: snakeviz {profile_file} ===")
    else:
        bench_func(har_log)

if __name__ == "__main__":
    main()
