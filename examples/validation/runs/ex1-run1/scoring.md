# ex1 run 1 — scored against PREDICTIONS.md (E1-*)

Run date 2026-07-21. Agent onboarded taskq in a scratch copy: full
Internal/External view split, 9-action CLI surface with error paths, TLC
green on both views (Internal 292/139 d10; External 15,148/1,377 d11),
19 project+scaffold tests passing. Owner spot-verified TLC output, the
descriptor, the fitness scan, the decision doc, and finding 1's source lines.

| Prediction | Verdict | Evidence |
| --- | --- | --- |
| E1-P1 scaffold via documented commands, TLC green | **PASS** | `scaffold project` → both views green, real behavior modeled (cap 2 exercised with 3 names). |
| E1-P2 no silent bound = 1 | **PASS** | Final bound = 64 with the two observability variables listed as explicit unknowns excluded from the bound. Note: the agent first hit `UNKNOWN` because domain resolution cannot see module-defined set operators (VAL-06) and inlined the literal to proceed — the honest-unknown path worked as designed, but the resolver is narrower than real models need. |
| E1-P3 no suggestion language; judgment cites facts + intuition doc | **PASS** | Decision: "no refactor warranted," argued unknown-by-unknown and dense-row-by-dense-row against the intuition doc's examples; the one advisory warning (12 actions > 8) explained as enumerated CLI error variants, not scattered writers. |
| E1-P4 composed fitness rules persist and surface | **PASS** | Two multi-predicate rules in `fitness_functions.json`; rescan shows both `holds` (owner re-read). |
| E1-P5 advisory treated as advisory | **PASS** | Warning acknowledged and reasoned about; budgets kept at defaults with rationale. |
| X-P1 no PATH wrapper | PASS (per report) |
| X-P2 findings filed, not fixed | **PASS** | 5 findings reported, none fixed. |
| X-P3 docs sufficient without reading source | **FAIL (by design → findings)** | The agent had to read `analyze_complexity.py` source to learn the justification-table schema (VAL-05) and the domain-resolver limits (VAL-06). |

## Findings filed from this run

- **VAL-04** (major, owner-confirmed in source): scaffold output contradicts
  the advisory doctrine — the `scaffold project` epilog and the generated
  manifest comment (`scripts/new_ticket_workflow.py:615,666`) say "Budgets are
  hard gates … analyze complexity … read them," predating the reframe that
  SKILL.md, the references, and the scanner's own output all state.
- **VAL-05**: the `justification:` table schema (dict with non-empty
  `invariants`/`effects`/`kill_tests` lists; prose strings silently flagged
  DEAD WEIGHT) is documented nowhere.
- **VAL-06**: `_set_size` domain resolution only handles literals, ranges,
  BOOLEAN, unions, cfg constants — `[Names -> TaskStatus]` with `TaskStatus`
  defined in Core.tla yields UNKNOWN; undocumented.
- **VAL-07**: the R/W matrix attributes writes to syntactic primers, so
  wrapper actions priming variables only via a helper operator vanish from
  the matrix/dense columns/action count (9 CLI actions collapsed to 4 until
  the agent inlined the assignments).
- Finding 5 of the report = **VAL-01**, independently rediscovered
  (cross-run corroboration; not refiled).

## Toolchain verdict for this run

The entry path works end to end and F3's honest-unknown behavior showed up
exactly where predicted. The cost: two places where the agent needed
toolchain source as documentation, one measurement blind spot (VAL-07 can
understate action counts — which also feeds fitness facts), and gate-era
language still stamped into every new scaffold (VAL-04).
