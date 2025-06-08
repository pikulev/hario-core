# Hario Core

Hario Core is a modern, extensible, and type-safe Python library for parsing, transforming, and analyzing HAR (HTTP Archive) files. Built on Pydantic, it provides robust validation, flexible transformation, and easy extension for custom HAR formats.

## Main Concepts

- **Parser**: Use `parse()` to load and validate HAR files into Pydantic models (`HarLog`, `Entry`).
- **Pipeline**: The `Pipeline` class lets you process HAR logs, assign IDs, and apply transformations in a composable way.
- **Transformers**: Built-in and custom functions (like `flatten`, `normalize_sizes`, `normalize_timings`) to mutate or normalize HAR entries for storage or analytics.
- **Utils**: Utilities for ID generation (`by_field`, `uuid`), model registration (`register_entry_model`), and more.

See the [API Reference](api.md) for detailed usage, signatures, and extension patterns.

## Key Features

- **Type-Safe Parsing**: Validates HAR files using Pydantic models, catching errors early.
- **Transformers**: Apply built-in or custom transformations to each HAR entry (e.g., flattening, normalization).
- **Normalization**: Ensures all numeric fields (sizes, timings) are non-negative, so you can safely sum, aggregate, and analyze data without errors from negative values. This is crucial for analytics and reporting.
- **Deterministic & Random IDs**: Generate unique or deterministic IDs for each entry. Deterministic IDs ensure that the same request always gets the same ID—useful for deduplication, comparison, and building analytics pipelines.
- **Extensible**: Register your own entry models to support browser-specific or proprietary HAR extensions (e.g., Chrome DevTools, Safari).
- **Composable Pipelines**: Chain any number of transformers and ID strategies for flexible data processing.

## Why Normalize HAR Data?

HAR files from browsers or proxies sometimes contain negative values for sizes or timings (e.g., -1 for unknown). Normalization transforms these to zero, so you can safely compute totals, averages, and other metrics without skewing your analytics. This is especially important for dashboards, BI, and automated reporting.

## Why Deterministic IDs?

A deterministic ID is generated from key fields (like URL and timestamp), so the same logical request always gets the same ID—even if the HAR is re-exported or merged. This is essential for deduplication, change tracking, and building reliable analytics or data warehouses.

## Example: Full Pipeline

```python
from hario_core import parse, Pipeline, by_field, flatten, normalize_sizes

pipeline = Pipeline(
    id_fn=by_field(["request.url", "startedDateTime"]),
    transformers=[flatten(), normalize_sizes()],
)

model = parse("example.har")
result_dict = pipeline.process(model)

for entry in result_dict:
    print(entry["id"], entry["request"]["url"])
```

## Installation

```bash
pip install hario-core
```

---

See the [API Reference](api.md) for more details and advanced usage. 