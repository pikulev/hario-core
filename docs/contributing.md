# Contributing

We welcome contributions to `hario-core`! Please see our issue tracker for ideas.

## Architecture and Type System Notes

- **Pydantic models** (`Entry`, `Request`, `Response`, etc.) implement the HAR 1.2 structure and are used for strict data validation.
- **Protocols** in `hario_core/interfaces.py` describe interfaces for extensibility and type safety.
  - Do not inherit Pydantic models directly from protocols — use structural subtyping (matching structure is enough).
  - For forward references, use string annotations and import types inside an `if TYPE_CHECKING` block.
- **Extensibility**: new HAR entry types are added via registration of custom models and detector functions.
- **Optional fields**: if a field is optional in the HAR spec (e.g., `postData`), always use `Field(default=None)` for correct Pydantic 2.x behavior.
- **Test coverage**: the project is covered by tests at 97%+, please maintain high coverage when adding new code. 