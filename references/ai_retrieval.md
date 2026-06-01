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

## History Search Recipe

When the question is about how the model evolved, search immutable close
history before opening old desired/current snapshots:

```bash
rg -n "Ticket|CreateWorkspace|LimitInvariant" specs/.history
find specs/.history -name manifest.json
```

Read `summary.md` and `manifest.json` first. Open copied snapshots only when the
manifest shows that the close entry is relevant to the current boundary. This
keeps token cost bounded by active state plus selected immutable history.

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
- selected spec-evolution manifest or summary

This is what lets an AI coding agent avoid guessing from production
machinery.
