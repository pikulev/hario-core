# Changelog

### v0.4.0
- BREAKING: The old `flatten` (which stringifies nested structures) is now called `stringify`.
- BREAKING: The new `flatten` has different behavior—please update your code if you relied on the old flatten logic.
- BREAKING: Pipeline now requires a list of transformers and a PipelineConfig instance (no more id_fn/id_field in constructor).
- BREAKING: Pipeline.process now expects a list of dicts (e.g., from HarLog.model_dump()["entries"]).
- New: Introduced a new `flatten` transformer that fully flattens nested HAR entries into a flat dict, with customizable key separator and flexible array handling via `array_handler`. Designed for advanced analytics and BI.
- New: PipelineConfig class for configuring batch size, processing strategy (sequential/thread/process/async), and max_workers.
- New: Parallel and batch processing strategies for large HAR files (process, thread, async).
- New: Benchmarks and benchmarking scripts for pipeline performance (see `benchmarks/`).
- New: All transformers (`flatten`, `normalize_sizes`, `normalize_timings`, `set_id`) are now implemented as picklable callable classes, fully compatible with multiprocessing.
- New: `set_id` transformer for assigning IDs to entries using any function (e.g., by_field, uuid).
- Internal: Test suite and samples updated for new API and real-world HAR compatibility.

### v0.3.1
- FIX real-world HAR compatibility: made nested fields like `postData.params` optional in models, so parsing DevTools and other real HAR files is more robust.
- All test samples are now based on real HAR data with valid `pages` and `pageref` links.
- Documentation and comments are now only in English.
- Added section on extensibility and DevTools support to the docs.
- Minor fixes for mypy/flake8 compatibility and test infrastructure.

## v0.3.0

- BREAKING: Pipeline now only accepts HarLog objects (parsed HAR), does not parse sources itself.
- `parse` is now the main entry point for loading HAR files.
- Removed enrichment pipeline, enricher utilities, `normalize_har_entry`, `transform_har_entry_for_storage`, and old ID generator classes.
- Documentation and all usage examples fully updated to reflect new API.
- Improved extensibility: custom entry models via `register_entry_model`.
- Improved type safety and validation throughout the codebase.
- Docs now explain why normalization and deterministic IDs matter for analytics and deduplication.
- Requires Python >=3.10.

## v0.2.0

-   **Major Refactoring**: The library has been completely refactored to be more modular and extensible.
-   **Extensible Parser**: Introduced a registration pattern (`register_entry_model`) to allow adding support for custom HAR formats (e.g., Safari).
-   **Pluggable Enrichment**: Reworked the enrichment logic to use a flexible pipeline (`apply_enrichment`).
-   **Model Separation**: HAR 1.2 models are now separated from DevTools extension models.
-   **Removed pandas**: Removed the `to_dataframe` method and the `pandas` dependency to keep the core library lightweight.

## v0.1.0

- Initial release of `hario-core`.