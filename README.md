# Hario Core — Type-safe HAR Model & Transform

[![PyPI version](https://badge.fury.io/py/hario-core.svg)](https://badge.fury.io/py/hario-core)
[![Build Status](https://github.com/pikulev/hario-core/actions/workflows/python-package.yml/badge.svg)](https://github.com/pikulev/hario-core/actions/workflows/python-package.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/pikulev/hario-core/branch/main/graph/badge.svg?token=BUJG4K634B)](https://codecov.io/gh/pikulev/hario-core)

A modern, extensible, and type-safe Python library for parsing, transforming, and analyzing HAR (HTTP Archive) files. Built on Pydantic, Hario-Core provides robust validation, flexible transformation, and easy extension for custom HAR formats.

## Features

- **Type-Safe Parsing**: Validates HAR files using Pydantic models, catching errors early.
- **Transformers**: Apply built-in or custom transformations to each HAR entry (e.g., stringifying, flattening).
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
from hario_core import parse, Pipeline, by_field, normalize_sizes, stringify, flatten

# Build a processing pipeline: deterministic ID and size normalization
pipeline = Pipeline(
    id_fn=by_field(["request.url", "startedDateTime"]),
    transformers=[normalize_sizes()],
)

# Parse your HAR file (from path, bytes, or file-like object)
model = parse("example.har")
result_dict = pipeline.process(model)

for entry in result_dict:
    print(entry["id"], entry["request"]["url"])
```

## Documentation

- [API Reference](https://github.com/pikulev/hario-core/blob/main/docs/api.md)
- [Changelog](https://github.com/pikulev/hario-core/blob/main/docs/changelog.md)
- [Contributing](https://github.com/pikulev/hario-core/blob/main/CONTRIBUTING.md)

### Why use this library instead of just json + pandas?

If you've ever tried to analyze real HAR files with just json and pandas, you know it quickly turns into a mess of manual checks, edge cases, and one-off scripts. hario-core is built to save you from that pain:

- You get strict validation out of the box, so you immediately see if your data is broken or incomplete.
- Modern HAR files from browsers often have extra fields and extensions—hario-core understands them and lets you easily add your own.
- You don't have to write boilerplate to clean up negative sizes, missing timings, or weird nested structures: it's all handled for you.
- Need to flatten, normalize, or enrich your data? Just use a ready-made transformer instead of reinventing the wheel.
- You can build repeatable, testable pipelines for analytics, not just ad-hoc scripts that are hard to maintain.
- Your code is safer, more readable, and much easier to support—especially as your data or requirements grow.

In short: hario-core lets you focus on your analysis, not on endless data wrangling. It's the tool you wish you had after your first real HAR analytics project.

## License

MIT License. See [LICENSE](https://github.com/pikulev/hario-core/blob/main/LICENSE).

## Supported Python Versions

- Python 3.10+