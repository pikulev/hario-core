# Welcome to Hario-Core

A modern, extensible, and type-safe library for parsing and processing HAR (HTTP Archive) files. Built with Pydantic, `hario-core` provides a robust foundation for working with HAR data, including built-in support for Chrome DevTools extensions and a powerful mechanism for adding your own extensions.

## Why Hario-Core?

-   **Type-Safe**: Leverages Pydantic for robust data validation and a great developer experience.
-   **Extensible by Design**: Easily add support for custom HAR formats (e.g., Safari, Firefox) using a simple registration pattern.
-   **Flexible Enrichment**: Add custom data to your HAR entries using a pluggable enricher pipeline.
-   **Protocol-Based**: Core logic is built on abstract protocols, allowing you to easily integrate `hario-core` into your own tools.

## Getting Started

To get started, install the library from PyPI:

```bash
pip install hario-core
```

Then, you can start parsing your HAR files:

```python
from hario_core import load_har

# Load a HAR file from a path
har_log = load_har("path/to/your/file.har")

# Access validated data
for entry in har_log.entries:
    print(f"{entry.request.method} {entry.request.url} -> {entry.response.status}")
```

For more advanced use cases, check out the **API Guide**. 