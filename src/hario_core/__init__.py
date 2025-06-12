"""
Hario Core package root.

- Exposes main API: loading, parsing, enrichment, and extension registration
  for HAR files.
- Imports and re-exports all core models, protocols, and utilities
  for public use.
- See documentation for usage examples and extension patterns.
"""

__version__ = "0.2.0"  # Bump version after refactoring

from hario_core.har_parser import entry_selector, parse, register_entry_model
from hario_core.interfaces import (
    EntryIdFn,
    HarParser,
    HarStorageRepository,
    Processor,
    Transformer,
)
from hario_core.models.extensions.chrome_devtools import DevToolsEntry
from hario_core.models.har_1_2 import (
    Browser,
    Content,
    Cookie,
    Creator,
    Entry,
    HarLog,
    Header,
    Page,
    PageTimings,
    PostData,
    PostParam,
    QueryString,
    Request,
    Response,
    Timings,
)
from hario_core.pipeline import Pipeline
from hario_core.utils.id import by_field, uuid
from hario_core.utils.transform import flatten, normalize_sizes, normalize_timings

__all__ = [
    # har_parser
    "parse",
    "entry_selector",
    "register_entry_model",
    # pipeline
    "Pipeline",
    # id utils
    "by_field",
    "uuid",
    # transform utils
    "flatten",
    "normalize_sizes",
    "normalize_timings",
    # interfaces
    "HarStorageRepository",
    "HarParser",
    "Processor",
    "Transformer",
    "EntryIdFn",
    # models
    "Entry",
    "HarLog",
    "Request",
    "Response",
    "Timings",
    "Browser",
    "Content",
    "Cookie",
    "Creator",
    "Header",
    "Page",
    "PageTimings",
    "PostData",
    "PostParam",
    "QueryString",
    # extensions
    "DevToolsEntry",
]
