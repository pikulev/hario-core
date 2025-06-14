# Hario Core — Type-safe HAR Model & Transform

[![PyPI version](https://badge.fury.io/py/hario-core.svg)](https://badge.fury.io/py/hario-core)
[![Build Status](https://github.com/pikulev/hario-core/actions/workflows/python-package.yml/badge.svg)](https://github.com/pikulev/hario-core/actions/workflows/python-package.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/pikulev/hario-core/branch/main/graph/badge.svg?token=BUJG4K634B)](https://codecov.io/gh/pikulev/hario-core)

A modern, extensible, and type-safe Python library for parsing, transforming, and analyzing HAR (HTTP Archive) files. Built on Pydantic, Hario-Core provides robust validation, flexible transformation, and easy extension for custom HAR formats.

## Features

- **Type-Safe Parsing**: Validates HAR files using Pydantic models, catching errors early.
- **Transformers**: Apply built-in or custom transformations to each HAR entry (e.g., flatten, normalizations).
- **Normalization**: Ensures all numeric fields (sizes, timings) are non-negative, so you can safely sum, aggregate, and analyze data without errors from negative values. This is crucial for analytics and reporting.
- **Deterministic & Random IDs**: Generate unique or deterministic IDs for each entry. Deterministic IDs ensure that the same request always gets the same ID—useful for deduplication, comparison, and building analytics pipelines.
- **Extensible**: Register your own entry models to support browser-specific or proprietary HAR extensions (e.g., Chrome DevTools, Safari).
- **Composable Pipelines**: Chain any number of transformers and ID strategies for flexible data processing.

## Installation

```bash
pip install hario-core
```

## Quickstart

### 1. Parse and validate a HAR file

```python
from hario_core import parse

har_log = parse("example.har")
entries = har_log.model_dump()["entries"]  # list of dicts
```

### 2. Transform entries with a pipeline

```python
from hario_core.transform import Pipeline, flatten, set_id, by_field

pipeline = Pipeline([
    set_id(by_field(["request.url", "startedDateTime"]))
])
results = pipeline.process(entries)
```

### 3. Custom entry models (extensions)

```python
from hario_core.parse import register_entry_model
from hario_core.models import Entry

def is_custom_entry(entry: dict) -> bool:
    return "x-custom" in entry

class CustomEntry(Entry):
    x_custom: str

register_entry_model(is_custom_entry, CustomEntry)
```

## Public API

### Parsing and validation
- `parse(path_or_bytes_or_filelike) -> HarLog`
- `validate(har_dict: dict) -> HarLog`
- `register_entry_model(detector: Callable, model: Type[Entry])`
- `entry_selector(entry_dict: dict) -> Type[Entry]`

### Models
- `Entry`, `HarLog`, `DevToolsEntry` (and all standard HAR 1.2 models)

### Transform
- `Pipeline`, `flatten`, `normalize_sizes`, `normalize_timings`, `set_id`, `by_field`, `uuid`, `json_array_handler`

## Documentation

- [API Reference](https://github.com/pikulev/hario-core/blob/main/docs/api.md)
- [Changelog](https://github.com/pikulev/hario-core/blob/main/docs/changelog.md)
- [Contributing](https://github.com/pikulev/hario-core/blob/main/CONTRIBUTING.md)


## License

MIT License. See [LICENSE](https://github.com/pikulev/hario-core/blob/main/LICENSE).

## Supported Python Versions

- Python 3.10+ 