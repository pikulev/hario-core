# Hario Core

Hario Core is a modern, extensible, and type-safe Python library for parsing, transforming, and analyzing HAR (HTTP Archive) files. Built on Pydantic, it provides robust validation, flexible transformation, and easy extension for custom HAR formats.

---

## API Overview

Hario Core exposes three main namespaces:

### 1. Models (`hario_core.models`)

- **Purpose:** Type-safe data structures for HAR 1.2 and browser extensions.
- **Key classes:** `Entry`, `HarLog`, `DevToolsEntry`
- **Usage:** Use these models for type checking, validation, and extension.

```python
from hario_core.models import Entry, HarLog, DevToolsEntry
```

---

### 2. Parse (`hario_core.parse`)

- **Purpose:** Loading, validating, and extending HAR files.
- **Key functions:**
  - `parse(path_or_bytes_or_filelike) -> HarLog`
  - `validate(har_dict: dict) -> HarLog`
  - `register_entry_model(detector, model)`
  - `entry_selector(entry_dict) -> Type[Entry]`
- **Usage:** Always start with parsing or validating your HAR data.

```python
from hario_core.parse import parse, validate, register_entry_model, entry_selector

har_log = parse("example.har")
# or, if you already have a dict:
har_log = validate(har_dict)
```

---

### 3. Transform (`hario_core.transform`)
- **Purpose:** Transforming and processing HAR entries with pipelines and utilities.
- **Key classes/functions:** `Pipeline`, `flatten`, `normalize_sizes`, `normalize_timings`, `set_id`, `by_field`, `uuid`, `json_array_handler`
- **Usage:** Build flexible pipelines for cleaning, normalizing, and analyzing HAR data.

```python
from hario_core.transform import Pipeline, flatten, set_id, by_field

entries = har_log.model_dump()["entries"]
pipeline = Pipeline([
    set_id(by_field(["request.url", "startedDateTime"])),
    flatten()
])
results = pipeline.process(entries)
```

---

## Key Features

- **Type-Safe Parsing:** Validates HAR files using Pydantic models, catching errors early.
- **Composable Transformations:** Build pipelines from built-in or custom transformers.
- **Extensible:** Register your own entry models for browser-specific or proprietary HAR extensions.
- **Deterministic & Random IDs:** Generate unique or deterministic IDs for each entry.
- **Batch & Parallel Processing:** Built-in strategies for processing large HAR files.

---

## Example: Full Workflow

```python
from hario_core.parse import parse
from hario_core.transform import Pipeline, by_field, flatten, normalize_sizes, set_id

har_log = parse("example.har")
entries = har_log.model_dump()["entries"]

pipeline = Pipeline([
    set_id(by_field(["request.url", "startedDateTime"])),
    flatten(),
    normalize_sizes(),
])
results = pipeline.process(entries)
```

---

### Parallel Processing with Custom Batch Size and Workers

```python
from hario_core.transform import Pipeline, PipelineConfig, flatten

config = PipelineConfig(
    strategy="process",      # or "thread" for multithreading
    batch_size=20,          # process 20 entries per batch
    num_workers=6            # use 6 parallel workers
)

pipeline = Pipeline([
    flatten(),
],
    config=config
)
results = pipeline.process(entries)
```

#### Available Processing Strategies

- `sequential` (default): Process entries one by one in a single thread. Best for small datasets or debugging.
- `thread`: Parallel processing using threads. Useful for I/O-bound tasks or when GIL is not a bottleneck.
- `process`: Parallel processing using multiple processes. Recommended for CPU-bound tasks and large datasets.
- `async`: Asynchronous processing (if your transformers support async). For advanced use cases with async I/O.

---

## Extending with Custom Entry Models

```python
from hario_core.parse import register_entry_model
from hario_core.models import Entry

def is_custom_entry(entry: dict) -> bool:
    return "x-custom" in entry

class CustomEntry(Entry):
    x_custom: str

register_entry_model(is_custom_entry, CustomEntry)
```

---

## Installation

```bash
pip install hario-core
```

---

See the [API Reference](api.md) for more details and advanced usage. 