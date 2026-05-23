# Shared Adapter Runtime

`run_generated_case_adapters.py` currently defines the adapter contract
informally.

Add an importable runtime module with typed protocol/dataclasses for adapters
and normalized results.

Acceptance criteria:

- Provide `CaseAdapter` protocol.
- Provide `CaseRunResult` dataclass.
- Generated programs import this runtime instead of duplicating helper code.
- Existing TOML mapping runner keeps working.
