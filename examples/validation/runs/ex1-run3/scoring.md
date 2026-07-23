# ex1 run 3 — scored against PREDICTIONS.md (E1-* + R3-E1)

Run date 2026-07-22, against the main-readiness batch tip. Owner re-verified:
bound 1,024 with merged domain sources ("TypeInvariant + the configured
invariants (resolved transitively)" — the VAL-17 merge visible in the output),
both fitness rules hold, TLC green both views.

| Prediction | Verdict | Evidence |
| --- | --- | --- |
| E1-P1 scaffold + TLC green | **PASS** | Richest model of the three runs: explicit reject actions + outcome/exit observables, both views green (298 / 488 distinct). |
| E1-P2 no silent bound = 1 | **PASS (exceeded)** | Bound 1,024 with ALL dimensions resolved, zero exclusions — first run with nothing unknown. |
| E1-P3 grounded judgment | **PASS** | "No refactor warranted," argued per the reading order; applied the write-only-state test in the KEEP direction (lastOutcome/exitCode have nameable dependents — invariants beyond type + verbatim-message tests); recorded what would flip the decision. |
| E1-P4 composed fitness rules | **PASS (exceeded)** | Two multi-predicate rules hold; mechanism negative-tested (temporary rule FIRED with leaf trace, then restored). Deliberate non-constraint of god_state_count recorded with reasoning. |
| E1-P5 advisory stays advisory | **PASS** | Defaults kept, rationale recorded, `source: defaults`. |
| **R3-E1 no route-arounds; X-P3 passes** | **PASS — the key result** | Operator-defined sets, wrapped conjuncts, and multi-view naming all resolved without workarounds (VAL-06/16/17 fixes confirmed in anger); fitness JSON path used per docs with the documented CONFIG ERROR semantics (VAL-01); no gate-era language encountered (VAL-04); the agent never read toolchain source to proceed — X-P3 passes for the first time in three runs. |
| X-P1/X-P2 | PASS | No PATH wrapper; 4 findings recorded, none fixed. |

## New findings (recorded for post-main triage; none blocking)

- **R3-DF-01** (most substantive): the scaffold's single-module adapter
  layout collides with its own MF-015 transitive-import gate — spec-unit
  adapters must import the production package, and the scaffolded
  `testgraph_bindings.yml` points all external roles at the same module.
  The shipped worked example only survives via a package-name coincidence.
  Route-around: split `spec_unit_adapters.py`. Scaffold template + doc gap.
- **R3-DF-02**: PyYAML asymmetry deserves one doc line — the fallback
  manifest parser reads `budgets:`/`justification:` fine; only fitness
  rules need PyYAML (behavior matches docs but surprises).
- **R3-DF-03**: `scaffold project` epilogue's "next" step 5 is malformed
  (stray `end` token, missing the required `TICKET-ID "Title"` args).
- **R3-DF-04** (unconfirmed): scaffolded `test_spec_unit_adapters.py`
  hardcodes a cases path that may mismatch the manifest's package name;
  flagged for whoever first generates cases.
