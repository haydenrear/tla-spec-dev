# MF-014 — validations deferred to MF-023 (#30)

Per the epic-wide spec-case execution deferral (owner direction 2026-07-18),
the mechanism, its unit tests, and its adapters were built and validated, but
no generated spec cases were run. MF-023 performs the Internal/External
decomposition by dogfooding the finished toolchain on this repository, and owns
every run listed here.

## Deferred — MF-023 must exercise these

1. **Case generation over the reachable state graph.** Not run. The MF-011
   complexity gate refuses generation against this model
   (`C1 is touched by 12 actions, exceeding max_component_actions 8`). That is
   a TRUE finding about the undecomposed single-module baseline. It was **not**
   worked around with `--allow-over-budget`, and the component budgets were
   **not** renegotiated.

2. **The cap gate on a REAL generated corpus.** The gate wired into
   `generate_cases_from_tlc_dump.py` (post-write) and
   `export_testgraph_cases.py` (pre-selection) has been exercised only against
   fixtures and synthetic packages, never against a corpus TLC actually
   produced. MF-023 should confirm the gate fires on the real ecommerce corpus
   and that the reported cause matches the actual model defect.

3. **The documented 732-case ecommerce corpus.** See "A finding about the
   fixture" below — it is not committed, so the diagnostics have never been run
   against the genuine artifact. MF-023 regenerates it and should re-run
   `tla-spec-dev analyze corpus` against the real output.

4. **Effect-conformance sweep.** Not run.

5. **Mutation kill test.** Not run; arrives with MF-016. Until then the
   behavior-retention evidence in the complexity ledger has no kill-rate
   component, which is recorded there explicitly.

## A finding about the fixture the ticket named

The assignment and the ticket both point at
`examples/distributed_history/specs/generated/testgraph/traces/` as a
committed, real 732-case corpus. **It is not.** That directory holds 4 external
trace files plus a manifest, and the sibling case packages hold 4 internal and
4 external cases:

    examples/distributed_history/specs/generated/testgraph/traces/            -> 4 traces
    examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases -> 4 cases
    examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases -> 4 cases

The 732 figure is documented in four places — `references/examples.md:48`,
`references/edge-cases.md:84`, `references/testgraph_adapters.md:141`, and
`examples/distributed_history/README.md:34` — and every one of them describes
it as regenerated **under a validation report at run time**, not committed:

> `examples/distributed_history/test_graph/build/validation-reports/<run>/generated/testgraph/traces/manifest.json`

Regenerating it needs a TLC run over the reachable state graph, which this
ticket must not do.

**What was used instead.** `tests/corpus_fixtures.py` reconstructs the
documented distribution exactly — 732 cases, 11 actions, 504 duplicate-
submission cases (68.9% ≈ the documented 69%), tail at 4 and 2 — and shapes
each redundant group so all three representation defects are present and
distinguishable. It is clearly labelled a fixture in its module docstring. The
real committed 4-case corpus is also run through the CLI
(`analyze-corpus-committed-example.txt`) so at least one end-to-end path
touches genuine committed artifacts.

This is a documentation/artifact divergence of the same class as #33 and is
reported rather than worked around. No finding in this ticket's evidence should
be read as a measurement of the real ecommerce model.

## NOT deferred — validated here

- `tla-spec-dev analyze corpus` CLI, both exit paths, against the committed
  example corpus and the reconstructed fixture.
- The cap gate wired into generation and export, including the property that
  `--limit`/`--label` cannot bring an over-cap corpus under cap.
- All three cause classifiers (ordering / symmetry / abstraction).
- The structural no-drop guarantees.
- The cap-raise accept path.
- Regression-trace retention.
- TLC on ticket-local current; 196 repository unit tests; 45 spec-unit adapter
  tests; `specWorkflow` and `cliWorkflow`.
