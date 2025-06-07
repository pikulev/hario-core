# Changelog

## Version 0.1.0

- Initial release of `hario-core`. 

## v0.2.0

-   **Major Refactoring**: The library has been completely refactored to be more modular and extensible.
-   **Extensible Parser**: Introduced a registration pattern (`register_entry_model`) to allow adding support for custom HAR formats (e.g., Safari).
-   **Pluggable Enrichment**: Reworked the enrichment logic to use a flexible pipeline (`apply_enrichment`).
-   **Model Separation**: HAR 1.2 models are now separated from DevTools extension models.
-   **Removed pandas**: Removed the `to_dataframe` method and the `pandas` dependency to keep the core library lightweight.