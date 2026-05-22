# AI Retrieval

Principle:

```text
Retrieve the smallest executable contract that explains the boundary.
```

Generated spec packages should be easy to index. Generated docs should
expose:

- module name
- port names
- command names
- result names
- invariants
- validators
- fake class
- strategy functions
- generated traces
- conformance tests
- adapter mappings

## Retrieval Recipe

When modifying a Postgres adapter for `WorkspacePort`, retrieve:

- `Workspace.tla` action definitions
- `spec_manifest.yaml`
- generated `types.py`
- generated `ports.py`
- generated `fake.py`
- generated `validators.py`
- generated `contract_tests.py`
- the Postgres adapter under modification

Do not begin by reading the entire production implementation. The spec
double package is the minimum reproducible contract.

## Review Questions For AI Agents

- Which port does this adapter implement?
- Which commands cross the boundary?
- Which generated result type must be returned or normalized?
- Which invariant must hold after each transition?
- Which refinement mapping explains production state in spec terms?
- Which generated trace reproduces the edge case?

## Indexing Guidance

Keep generated docs concise and link names to files. The useful retrieval
unit is the smallest set that explains behavior:

- TLA+ action
- manifest command/result/port mapping
- generated fake method
- generated validator
- generated conformance test
- adapter mapping

This is what lets an AI coding agent avoid guessing from production
machinery.
