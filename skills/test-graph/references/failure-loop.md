# The smart failure loop

Moved here from `SKILL.md` by SI-09 (progressive disclosure). The card carries the
four steps and when to rerun from the beginning; this page is the mechanism an
agent needs once it is actually debugging a failed graph.

Do not blindly rerun a whole graph after every small fix. Test graph nodes are
independently runnable scripts, and repeated full-graph runs can waste hours when
the same late node fails for different reasons.

## When a graph fails

- Inspect the failed node's report first:
  `<test_graph>/build/validation-reports/<runId>/report.md`, `summary.json`,
  `envelope/<node-id>.json`, and any `node-logs/` entries.
- For rerunnable failed nodes, read the report or Gradle output's rerun guidance.
  It includes both a resume-graph command and a run-only command backed by the
  node's saved input context.
- Decide whether the failure is isolated to the failed node or invalidates
  upstream setup. If upstream dependencies still produced valid published
  context, prefer rerunning only the failed node while iterating.

## Resume and run-only

To resume graph execution from that node and continue downstream:

```bash
<skill>/scripts/run.py <graph> \
  --resume-from-build <test_graph>/build/validation-reports/<runId> \
  --resume-from-node <node-id>
```

To run only that node from its saved build context:

```bash
<skill>/scripts/run.py <graph> \
  --resume-from-build <test_graph>/build/validation-reports/<runId> \
  --run-only-node <node-id>
```

This writes a fresh replay report containing only the selected node without
continuing downstream graph nodes. The selected node must have `rerun=true`.

### What the acquisition checks

Resume and run-only commands acquire `--resume-from-build` once as a verified
source snapshot. The source must be a real, non-symlink direct child of the
configured `build/validation-reports/` root; cross-project and nested paths are
rejected. It must also be a full, non-replay attempt with an exact full-plan
match; the selected context must equal the exact ordered current-plan prefix.

Closure v2 binds the raw scope and carrier plus the exact present
context/envelope path-to-SHA-256 maps; changed, added, removed, or symlinked
evidence fails before replay. The captured carrier and selected ordered context
are then used without reopening source paths. A fresh sibling run records the
source closure/context digests in execution scope v3.

This detects accidental or protocol mutation while trusting the
application-owned closure; authenticity against an owner able to rewrite the
closure requires an external signature, MAC, or WORM anchor. A replay report's
`execution.complete` remains scoped to selected-to-tail for resume, or one node
for run-only.

## Evidence, envelopes, and closure

- Canonical node evidence uses the closed `envelopeVersion: 1` schema. One strict
  validator gates executor publication, attempt closure/replay acquisition, and
  report regeneration. Unknown extensions require a version bump, and
  contradictory evidence such as a passed node with a failed assertion is
  rejected rather than rendered green.
- Report regeneration verifies the current attempt closure before trusting
  derived evidence. Missing or mismatched closure state is diagnostic `ERRORED`;
  aggregate report retention is capped at 16 MiB each for envelopes and contexts
  plus 500,000 JSON structural tokens.
- Managed node process groups require macOS or Linux plus `perl` core modules
  `POSIX` and `Time::HiRes`. A reaped orphan group becomes typed, closable
  `ERRORED` evidence; cleanup uncertainty withholds closure.

## Invoking a node script directly

Reuse the failed run's context for that node. Each attempted node writes its
exact input `Context[]` under `context/<node-id>.input.json`; pass it back as
`--context=@<path>`.

```bash
uv run sources/my_node.py \
  --nodeId=<node-id> \
  --runId=<runId> \
  --reportDir=<test_graph>/build/validation-reports/<runId> \
  --result-out=<test_graph>/build/validation-reports/<runId>/.tmp-results/<node-id>.json \
  --context=@<test_graph>/build/validation-reports/<runId>/context/<node-id>.input.json

jbang sources/MyNode.java \
  --nodeId=<node-id> \
  --runId=<runId> \
  --reportDir=<test_graph>/build/validation-reports/<runId> \
  --result-out=<test_graph>/build/validation-reports/<runId>/.tmp-results/<node-id>.json \
  --context=@<test_graph>/build/validation-reports/<runId>/context/<node-id>.input.json
```

Omit `--context` only for root nodes with no dependencies. Root nodes still write
an empty input-context snapshot for auditing.

Keep iterating on the failing node with direct node reruns until it passes or
until you discover an upstream dependency must change. After the targeted node
passes, rerun the containing graph once from the beginning with
`<skill>/scripts/run.py <graph>` to validate dependency ordering, fresh context,
reporting, and integration behavior.

Rerun from the beginning immediately when the fix changes a dependency node,
shared fixture/testbed state, graph composition, node ids, context keys consumed
by multiple downstream nodes, or any behavior that makes the previous run's
context stale.
