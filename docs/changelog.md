# Changelog

## v0.3.0

- BREAKING: Pipeline now only accepts HarLog objects (parsed HAR), does not parse sources itself.
- `parse` is now the main entry point for loading HAR files.
- Removed enrichment pipeline, enricher utilities, `normalize_har_entry`, `transform_har_entry_for_storage`, and old ID generator classes.
- Documentation and all usage examples fully updated to reflect new API.
- Improved extensibility: custom entry models via `register_entry_model`.
- Improved type safety and validation throughout the codebase.
- Docs now explain why normalization and deterministic IDs matter for analytics and deduplication.
- Requires Python >=3.12.

## v0.2.0

-   **Major Refactoring**: The library has been completely refactored to be more modular and extensible.
-   **Extensible Parser**: Introduced a registration pattern (`register_entry_model`) to allow adding support for custom HAR formats (e.g., Safari).
-   **Pluggable Enrichment**: Reworked the enrichment logic to use a flexible pipeline (`apply_enrichment`).
-   **Model Separation**: HAR 1.2 models are now separated from DevTools extension models.
-   **Removed pandas**: Removed the `to_dataframe` method and the `pandas` dependency to keep the core library lightweight.

## Version 0.1.0

- Initial release of `hario-core`. 