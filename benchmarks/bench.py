from bench_core import (
    STRATEGIES, HAR_PATH,
    bench_flatten, bench_full, bench_normalize_sizes, bench_normalize_timings, bench_cpu_heavy,
    create_results_table, create_results_csv, average_run, get_entries
)
from rich.console import Console
import argparse
import cProfile
import pstats
import sys



def main() -> None:
    parser = argparse.ArgumentParser(
        description="""
        Microbenchmark for HAR Pipeline with different strategies, averaging, profiling and CSV output.

        Example usage:
          python bench.py flatten -f my.har --no-gc --csv results.csv
          python bench.py --csv all_results.csv
          python bench.py full --profile process
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="all",
        choices=["flatten", "normalize", "full", "cpu_heavy", "all"],
        help="Benchmark mode: flatten, normalize, full, cpu_heavy, all (default: all)"
    )
    parser.add_argument(
        "-f", "--file",
        default=HAR_PATH,
        help="Path to HAR file (default: benchmarks/test_lg.har)"
    )
    parser.add_argument(
        "--profile",
        choices=STRATEGIES,
        help="Enable cProfile profiling for the given strategy (e.g. --profile process)"
    )
    parser.add_argument(
        "--no-gc",
        action="store_true",
        help="Disable GC during measurement (default: GC enabled)"
    )
    parser.add_argument(
        "--csv",
        nargs="?",
        const="-",
        help="Save results to CSV file (or stdout if no file is specified)"
    )
    args = parser.parse_args()

    mode = args.mode
    har_path = args.file
    profile_strategy = args.profile
    use_gc = not args.no_gc

    console = Console()
    console.print(f"Loading HAR file: {har_path} ...")
    entries = get_entries(har_path)
    console.print(f"Loaded {len(entries)} entries.")

    bench_map = {
        "flatten": bench_flatten,
        "normalize_sizes": bench_normalize_sizes,
        "normalize_timings": bench_normalize_timings,
        "full": bench_full,
        "cpu_heavy": bench_cpu_heavy,
    }

    if profile_strategy:
        if mode == "all":
            console.print("[red]Profiling is only available for a single mode, not for 'all'.[/red]")
            sys.exit(1)
        bench_func = bench_map[mode]
        profile_file = f"benchmarks/{mode}.stats"
        console.print(f"Profiling... profile saved in {profile_file} (strategy: {profile_strategy})")
        def prof():
            bench_func(entries, profile_strategy, use_gc=use_gc)
        cProfile.runctx("prof()", globals(), locals(), profile_file)
        p = pstats.Stats(profile_file)
        console.print("\n=== TOP-20 functions by cumtime ===\n")
        p.strip_dirs().sort_stats("cumtime").print_stats(20)
        console.print(f"\n=== For visualization, run: snakeviz {profile_file} ===")
    else:
        results = {strategy: {} for strategy in STRATEGIES}
        if mode == "all":
            for test_name, bench_func in bench_map.items():
                for strategy in STRATEGIES:
                    console.print(f"\n[bold]Running {test_name} with {strategy} strategy...[/bold]")
                    elapsed, current, peak, rss = average_run(bench_func, entries, strategy, use_gc=use_gc)
                    results[strategy][test_name] = (elapsed, current, peak, rss)
        else:
            bench_func = bench_map[mode]
            for strategy in STRATEGIES:
                console.print(f"\n[bold]Running {mode} with {strategy} strategy...[/bold]")
                elapsed, current, peak, rss = average_run(bench_func, entries, strategy, use_gc=use_gc)
                results[strategy][mode] = (elapsed, current, peak, rss)
        # Display results table
        table = create_results_table(results)
        console.print(table)
        # CSV output
        if args.csv:
            filename = None if args.csv == "-" else args.csv
            create_results_csv(results, f"benchmarks/{filename}")

if __name__ == "__main__":
    main()
