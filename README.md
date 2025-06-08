# Hario Core — Type-safe HAR Model & Transform

[![PyPI version](https://badge.fury.io/py/hario-core.svg)](https://badge.fury.io/py/hario-core)
[![Build Status](https://github.com/pikulev/hario-core/actions/workflows/python-package.yml/badge.svg)](https://github.com/pikulev/hario-core/actions/workflows/python-package.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/pikulev/hario-core/branch/main/graph/badge.svg?token=BUJG4K634B)](https://codecov.io/gh/pikulev/hario-core)

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

# Build a processing pipeline: deterministic ID, normalization, flattening
pipeline = Pipeline(
    id_fn=by_field(["request.url", "startedDateTime"]),
    transformers=[normalize_sizes(), flatten()],
)

# Parse your HAR file (from path, bytes, or file-like object)
model = parse("example.har")
result_dict = pipeline.process(model)

for entry in result_dict:
    print(entry["id"], entry["request"]["url"])
```

## Documentation

- [API Reference](docs/api.md)
- [Changelog](docs/changelog.md)
- [Contributing](CONTRIBUTING.md)

## License

MIT License. See [LICENSE](LICENSE).

## Supported Python Versions

- Python 3.10+ 