# API Reference

This page provides a detailed guide to the main functions, classes, and extensibility patterns in `hario-core`.

---

## HAR Parsing

### `parse`

```python
from hario_core import parse
```

Parses a HAR file from a path, bytes, or file-like object and returns a validated `HarLog` model. Automatically selects the correct Pydantic model for each entry (including extensions).

**Signature:**
```python
def parse(
    src: str | Path | bytes | bytearray | IO[Any],
    *,
    entry_model_selector: Callable[[dict[str, Any]], type[Entry]] = entry_selector,
) -> HarLog
```

- `src`: Path, bytes, or file-like object containing HAR JSON.
- `entry_model_selector`: Optional. Function to select the Pydantic model for each entry (default: registry-based selector).

**Returns:**
- `HarLog` — a validated Pydantic model with `.entries` (list of `Entry` or extension models).

**Example:**
```python
model = parse("example.har")
for entry in har_log.entries:
    print(entry.request.url)
```

---

## Entry Model Registration

### `register_entry_model`

Register a custom Pydantic model and detector function for new HAR entry formats (e.g., Safari, proprietary extensions).

**Signature:**
```python
def register_entry_model(
    detector: Callable[[dict[str, Any]], bool],
    model: type[Entry],
) -> None
```

- `detector`: Function that takes an entry dict and returns True if the model should be used.
- `model`: Pydantic model class to use for matching entries.

**Example:**
```python
from hario_core.models.har_1_2 import Entry
from pydantic import Field

class SafariEntry(Entry):
    webkit_trace: dict = Field(alias="_webkitTrace")

def is_safari_entry(entry_json):
    return "_webkitTrace" in entry_json

register_entry_model(is_safari_entry, SafariEntry)
```

---

## Data Models

All core data structures are implemented as Pydantic models in `hario_core.models.har_1_2`.

- `Entry`: Pydantic model for a HAR entry (fields: request, response, timings, cache, etc.).
- `HarLog`: Pydantic model for the HAR log (fields: version, creator, entries, etc.).

**Example:**
```python
from hario_core.models.har_1_2 import HarLog, Entry

har_log = HarLog.model_validate(har_json["log"])
for entry in har_log.entries:
    assert isinstance(entry, Entry)
    print(entry.request.url)
```

### `Transformer`
A transformer is a function that takes an `Entry` (or its extension) and returns a dict (possibly mutated/transformed).

```python
def my_transformer(entry: Entry) -> dict:
    data = entry.model_dump()
    # mutate data
    return data
```

### `EntryIdFn`
A function that takes an `Entry` and returns a string ID.

---

## ID Generation

### `by_field`

Returns a deterministic ID function based on specified fields of a HAR entry.

**Signature:**
```python
def by_field(fields: list[str]) -> EntryIdFn
```

**Example:**
```python
from hario_core.utils import by_field
id_fn = by_field(["request.url", "startedDateTime"])
```

### `uuid`

Returns a function that generates a random UUID for each entry.

**Signature:**
```python
def uuid() -> EntryIdFn
```

**Example:**
```python
from hario_core.utils import uuid
id_fn = uuid()
```

---

## Transformers

Transformers are functions that mutate or normalize HAR entry data for storage or analysis.

### `flatten`

Flattens nested structures in a HAR entry to a single level, stringifying deep or large fields (useful for DB storage).

**Signature:**
```python
def flatten(
    max_depth: int = 3,
    size_limit: int = 32_000,
) -> Transformer
```
- `max_depth`: Maximum depth to keep as dicts/lists (default: 3).
- `size_limit`: Maximum size (in bytes) for nested data before stringifying (default: 32,000).

**Example:**
```python
flat_entry = flatten()(entry)
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

### `Pipeline`

A high-level class for processing HAR data: transforming and assigning IDs. You must pass a parsed `HarLog` object (see `parse`).

**Signature:**
```python
class Pipeline:
    def __init__(
        self,
        id_fn: EntryIdFn,
        id_field: str = "id",
        transformers: Sequence[Transformer] = (),
    ) -> None
    def process(self, har_log: HarLog) -> list[dict[str, Any]]
```

- `id_fn`: Function to generate an ID for each entry.
- `id_field`: Field name for the generated ID (default: "id").
- `transformers`: List of transformer functions to apply to each entry.

---

## Example: Full Pipeline

```python
from hario_core import Pipeline, by_field, flatten, normalize_sizes, parse

pipeline = Pipeline(
    id_fn=by_field(["request.url", "startedDateTime"]),
    transformers=[flatten(), normalize_sizes()],
)

model = parse("example.har")
result_dict = pipeline.process(model)

for entry in result_dict:
    print(entry["id"], entry["request"]["url"])
```

---

## Chrome DevTools Extension Example

You can use the Chrome DevTools HAR extension models to validate and work with HAR files that include Chrome-specific fields.

**Example:**
```python
from hario_core.models.extensions.chrome_devtools import DevToolsEntry
from hario_core.models.har_1_2 import HarLog

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