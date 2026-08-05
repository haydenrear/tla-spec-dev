# QuotaLedger TLC Cases

Generated from a TLC DOT state graph dump.

- View: `internal`
- States: `2649`
- Cases: `1855`

- Emitted transitions before dedupe: `43128`
- TLC transitions before view filtering: `43128`

- Dedupe mode: `none`
- State projection: `none`
- Negative corpus: `with-positive`
- Port corpus: `only`

Each positive case is one action-labeled edge in the reachable state graph.

## Negative cases

- Emitted: `118` of `47682` candidate (state, action, argument) triples
- Negated actions: `CloseTenant, Commit, Release, Reserve`
- Negative dedupe: `guard-reads` (collapsed `39966` -> `118`)
- Enabled edges cross-checked against the same evaluator: `4028`, of which `0` disagreed

A negative case asserts that the program REFUSES the call and that no
modeled variable changes. Its `output` is a `StateGraphRejection` whose
`reason` is the violated conjunct, verbatim from the module.

## Port cases

- Manifest: `/Users/hayde/IdeaProjects/wt-epic-ports-as-adapters-PA-04/examples/validation/ab/model/spec_manifest.yaml`
- Emitted: `1855` from `43246` source case(s)
- Port dedupe: `region` (collapsed `4146` -> `1855`)

| port | cases | emitted | silent | region | declared by |
| --- | --- | --- | --- | --- | --- |
| `ledger.LedgerAppendPort` | 1855 | 750 | 1105 | `closed, committed, ledger` | CloseTenant, Commit |

A port case asserts the transition over the port's OWN REGION -- the modeled
variables written only by actions that declare it -- and carries
`port-expect:emitted` when the manifest declares the action on the port and
`port-expect:silent` when it maps the action and does not. An action ABSENT
from `effects.actions` gets no port case at all: absent means unmapped, and an
empty list means checked with no distinct effect.
