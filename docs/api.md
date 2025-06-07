# API Guide

This page provides a detailed guide to the main functions and extensibility patterns in `hario-core`.

## Loading HAR Files

The primary entry point is `load_har`, which parses a HAR file and automatically selects the correct Pydantic model for its entries.

```python
from hario_core import load_har

# load_har can handle paths, bytes, or file-like objects
har_log = load_har("path/to/your/file.har")

# The returned object is a Pydantic model
print(har_log.creator.name)
```

## Extensibility Patterns

`hario-core` is designed to be extended without modifying the core library.

### 1. Adding Support for a New HAR Format

If you need to parse a custom HAR format (e.g., from Safari or a proprietary tool), you can create your own Pydantic model and register it.

**a) Create your custom model and a detector function:**

```python
# my_safari_extension.py
from typing import Any, Dict
from pydantic import Field
from hario_core.models.har_1_2 import Entry

class SafariEntry(Entry):
    """A Pydantic model for Safari HAR entries."""
    webkit_trace: Dict[str, Any] = Field(alias="_webkitTrace")

def is_safari_entry(entry_json: Dict[str, Any]) -> bool:
    """Detects if a HAR entry is from Safari."""
    return "_webkitTrace" in entry_json
```

**b) Register your model in your application's startup code:**

```python
from hario_core import register_entry_model, load_har
from my_safari_extension import SafariEntry, is_safari_entry

# Register your extension
register_entry_model(detector=is_safari_entry, model=SafariEntry)

# Now, load_har will automatically use SafariEntry for matching files
har_log = load_har("my_safari.har")
```

### 2. Custom Data Enrichment

The `apply_enrichment` function allows you to apply a pipeline of custom functions to enrich your data. An "enricher" is any callable that takes an `HarEntry` model and a data dictionary.

```python
from typing import Any, Dict
from hario_core import load_har, apply_enrichment
from hario_core.interfaces import HarEntry

# Example: an enricher to extract User-Agent details
def user_agent_enricher(entry: HarEntry, data: Dict[str, Any]) -> None:
    """Parses the User-Agent header and adds it to the data."""
    for header in entry.request.headers:
        if header.name.lower() == "user-agent":
            # (A real implementation would parse this more thoroughly)
            data["user_agent_details"] = {"raw": header.value}
            break

har_log = load_har("my.har")
first_entry = har_log.entries[0]

# Apply your custom enricher
enriched_data = apply_enrichment(first_entry, enrichers=[user_agent_enricher])

# The result is a dictionary ready for storage or further analysis
print(enriched_data.get("user_agent_details"))
```

## Har Parser

::: hario_core.har_parser

## Models

::: hario_core.models

## Logic

::: hario_core.logic

## Interfaces

::: hario_core.interfaces

## ID Generators

::: hario_core.id_generators 