# API Reference

This page provides a detailed guide to the main functions, classes, and extensibility patterns in `hario-core`.

---

## HAR Parsing

### `parse`

```python
from hario_core.parse import parse
```

Parses a HAR file from a path, bytes, or file-like object and returns a validated `HarLog` model. Automatically selects the correct Pydantic model for each entry (including extensions).

**Signature:**
```python
def parse(src: str | Path | bytes | bytearray | IO[Any]) -> HarLog
```
- `src`: Path, bytes, or file-like object containing HAR JSON.

**Returns:**
- `HarLog` — a validated Pydantic model with `.entries` (list of `Entry` or extension models).

**Example:**
```python
har_log = parse("example.har")
for entry in har_log.entries:
    print(entry.request.url)
```

---

### `validate`

Validates a HAR dict (already loaded from JSON) and returns a `HarLog` model.

**Signature:**
```python
def validate(har_dict: dict) -> HarLog
```

---

### `register_entry_model`

Register a custom Pydantic model and detector function for new HAR entry formats (e.g., Safari, proprietary extensions).

**Signature:**
```python
def register_entry_model(detector: Callable[[dict], bool], model: type[Entry]) -> None
```
- `detector`: Function that takes an entry dict and returns True if the model should be used.
- `model`: Pydantic model class to use for matching entries.

**Example:**
```python
from hario_core.models import Entry

class CustomEntry(Entry):
    x_custom: str

def is_custom_entry(entry):
    return "x-custom" in entry

register_entry_model(is_custom_entry, CustomEntry)
```

---

### `entry_selector`

Selects the appropriate Entry model for a given entry dict (based on registered detectors).

**Signature:**
```python
def entry_selector(entry_dict: dict) -> type[Entry]
```

---

## Data Models

All core data structures are implemented as Pydantic models in `hario_core.models`.

- `Entry`: Pydantic model for a HAR entry (fields: request, response, timings, cache, etc.).
- `HarLog`: Pydantic model for the HAR log (fields: version, creator, entries, etc.).
- `DevToolsEntry`: Chrome DevTools extension entry model.

**Example:**
```python
from hario_core.models import HarLog, Entry

har_log = HarLog.model_validate(har_json["log"])
for entry in har_log.entries:
    assert isinstance(entry, Entry)
    print(entry.request.url)
```

---

## Transformers & ID Generators

### `Transformer`
A transformer is a callable that takes a dict (parsed HAR entry) and returns a dict (possibly mutated/transformed).

### `set_id`
Sets an ID field in each entry using a provided function.

**Signature:**
```python
def set_id(id_fn: Callable[[dict], str], id_field: str = "id") -> Transformer
```

### `by_field`
Returns a deterministic ID function based on specified fields of a HAR entry.

**Signature:**
```python
def by_field(fields: list[str]) -> Callable[[dict], str]
```

### `uuid`
Returns a function that generates a random UUID for each entry.

**Signature:**
```python
def uuid() -> Callable[[dict], str]
```

### `flatten`
Flattens nested structures in a HAR entry to a flat dict with keys joined by separator. If a list is encountered, array_handler is called (default: str). Useful for exporting to CSV, analytics, or custom DB schemas.

**Signature:**
```python
def flatten(separator: str = ".", array_handler: Callable[[list, str], Any] = None) -> Transformer
```
- `separator`: Separator for keys (default: '.')
- `array_handler`: Function (lambda arr, path) -> value. Default is str(arr)

**Example:**
```python
def header_handler(arr, path):
    return {f"{path}.{item['name']}": item["value"] for item in arr if isinstance(item, dict) and "name" in item and "value" in item}

flat_entry = flatten(array_handler=header_handler)(entry)
```

### `normalize_sizes`
Normalizes negative size fields in request/response to zero.

**Signature:**
```python
def normalize_sizes() -> Transformer
```

### `normalize_timings`
Normalizes negative timing fields in entry.timings to zero.

**Signature:**
```python
def normalize_timings() -> Transformer
```

---

## Pipeline

### `PipelineConfig`
Configuration for the Pipeline processor.

**Signature:**
```python
from hario_core.transform import PipelineConfig

config = PipelineConfig(
    batch_size=1000,                # entries per batch
    processing_strategy="process", # "sequential", "thread", "process", "async"
    max_workers=4                   # number of parallel workers (if applicable)
)
```

- `batch_size`: int, default 20000
- `processing_strategy`: str, one of "sequential", "thread", "process", "async"
- `max_workers`: int | None, number of parallel workers (for thread/process)

---

### `Pipeline`
A high-level class for processing HAR entry dicts: transforming and assigning IDs.

**Signature:**
```python
from hario_core.transform import Pipeline, PipelineConfig

pipeline = Pipeline(
    transformers=[...],
    config=PipelineConfig(...)
)

results = pipeline.process(entries)  # entries: list[dict]
```
- `transformers`: List of transformer functions to apply to each entry.
- `config`: PipelineConfig instance (optional, default: sequential, batch_size=20000)
- `process(entries)`: entries must be a list of dicts (e.g., from HarLog.model_dump()["entries"])

---

### Example: Full Pipeline

```python
from hario_core.parse import parse
from hario_core.transform import Pipeline, PipelineConfig, by_field, flatten, normalize_sizes, set_id

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

### Example: Parallel Processing with Custom Batch Size and Workers

```python
from hario_core.transform import Pipeline, PipelineConfig, flatten

config = PipelineConfig(
    processing_strategy="process",  # or "thread"
    batch_size=20,                  # process 20 entries per batch
    max_workers=6                   # use 6 parallel workers
)

pipeline = Pipeline([
    flatten(),
], config=config)
results = pipeline.process(entries)
```

#### Available Processing Strategies
- `sequential` (default): Process entries one by one in a single thread. Best for small datasets or debugging.
- `thread`: Parallel processing using threads. Useful for I/O-bound tasks or when GIL is not a bottleneck.
- `process`: Parallel processing using multiple processes. Recommended for CPU-bound tasks and large datasets.
- `async`: Asynchronous processing (if your transformers support async). For advanced use cases with async I/O.

---

## Chrome DevTools Extension Example

You can use the Chrome DevTools HAR extension models to validate and work with HAR files that include Chrome-specific fields.

**Example:**
```python
from hario_core.models import DevToolsEntry
from hario_core.models import HarLog

# Suppose har_json is a dict loaded from a Chrome DevTools HAR file
har_log = HarLog.model_validate(har_json["log"])
for entry in har_log.entries:
    devtools_entry = DevToolsEntry.model_validate(entry.model_dump())
    print(devtools_entry.resourceType, devtools_entry.request.url)
```

---

## See Also
- [Quickstart](index.md)
- [Contributing](contributing.md)
- [Changelog](changelog.md) 