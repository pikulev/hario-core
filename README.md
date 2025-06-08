# Hario-Core: Modern HAR Parsing

[![PyPI version](https://badge.fury.io/py/hario-core.svg)](https://badge.fury.io/py/hario-core)
[![Build Status](https://github.com/v-pikulev/hario-core/actions/workflows/python-package.yml/badge.svg)](https://github.com/v-pikulev/hario-core/actions/workflows/python-package.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A modern, extensible, and type-safe Python library for parsing, transforming, and analyzing HAR (HTTP Archive) files. Built on Pydantic, Hario-Core provides robust validation, flexible transformation, and easy extension for custom HAR formats.

## Features

- **Type-Safe Parsing**: Validates HAR files using Pydantic models, catching errors early.
- **Transformers**: Apply built-in or custom transformations to each HAR entry (e.g., flattening, normalization).
- **Normalization**: Ensures all numeric fields (sizes, timings) are non-negative, so you can safely sum, aggregate, and analyze data without errors from negative values. This is crucial for analytics and reporting.
- **Deterministic & Random IDs**: Generate unique or deterministic IDs for each entry. Deterministic IDs ensure that the same request always gets the same ID—useful for deduplication, comparison, and building analytics pipelines.
- **Extensible**: Register your own entry models to support browser-specific or proprietary HAR extensions (e.g., Chrome DevTools, Safari).
- **Composable Pipelines**: Chain any number of transformers and ID strategies for flexible data processing.

## Installation

```bash
pip install hario-core
```

## Quickstart

```python
from hario_core import parse, Pipeline, by_field, normalize_sizes, flatten

# Parse your HAR file (from path, bytes, or file-like object)
har_log = parse("example.har")

# Build a processing pipeline: deterministic ID, normalization, flattening
pipeline = Pipeline(
    id_fn=by_field(["request.url", "startedDateTime"]),
    transformers=[normalize_sizes(), flatten()],
)

results = pipeline.process(har_log)
for entry in results:
    print(entry["id"], entry["request"]["url"])
```

## Why Normalize HAR Data?

HAR files from browsers or proxies sometimes contain negative values for sizes or timings (e.g., -1 for unknown). Normalization transforms these to zero, so you can safely compute totals, averages, and other metrics without skewing your analytics. This is especially important for dashboards, BI, and automated reporting.

## Why Deterministic IDs?

A deterministic ID is generated from key fields (like URL and timestamp), so the same logical request always gets the same ID—even if the HAR is re-exported or merged. This is essential for deduplication, change tracking, and building reliable analytics or data warehouses.

## Extending: Supporting Custom HAR Formats

You can use the built-in model for Chrome DevTools HAR extensions:

```python
from hario_core.models.extensions.chrome_devtools import DevToolsEntry

# Suppose entry_json is a dict from a Chrome DevTools HAR entry
entry = DevToolsEntry.model_validate(entry_json)
print(entry.resourceType, entry.request.url)
```

You can also register your own Pydantic models for browser-specific or proprietary HAR extensions:

```python
from hario_core import register_entry_model
from hario_core.models.har_1_2 import Entry
from pydantic import Field

class SafariEntry(Entry):
    webkit_trace: dict = Field(alias="_webkitTrace")

def is_safari_entry(entry_json):
    return "_webkitTrace" in entry_json

register_entry_model(is_safari_entry, SafariEntry)
```

> **Note:** The `_webkitTrace` field is not part of the official Safari HAR format. This example is for demonstration purposes only, showing how to extend the model for custom fields.

## Documentation

- [API Reference](docs/api.md)
- [Changelog](docs/changelog.md)
- [Contributing](CONTRIBUTING.md)

## License

MIT License. See [LICENSE](LICENSE).

## Supported Python Versions

- Python 3.12+ 