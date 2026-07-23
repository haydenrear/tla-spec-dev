# Retrieval and authoring evidence

Unique source-line ranges actually opened are counted once per file. Inventory/rg result snippets and post-write validation reads are excluded. Changed-file cost includes project implementation and regenerated source, but excludes .venv, caches, raw experiment evidence, TLC dot/log output, and this self-referential ledger.

- Files read: 32
- Unique lines read: 7701
- Implementation/generated files changed: 51
- Lines changed: 6911
- Authoring wall minutes: 291.79
- Edit/run iterations: 14

The exact per-file read and changed ledgers are in `evidence/retrieval.json`.
Machine-readable authoring timing is in `evidence/authoring.json`.
