# CD-02 self-review: intuition doc vs acceptance assertions

Reviewed 2026-07-21 against the CD-02 acceptance assertions in
`specs/desired_program_model/ticket_plan.yaml`. The artifact under review is
`references/complexity_intuition.md` plus the SKILL.md wiring.

## How the worked examples were produced

Every descriptor excerpt in the doc is verbatim output of the merged CD-01
scanner, run as:

```bash
python3 scripts/tla_spec_dev.py --spec-root specs analyze complexity <model>.tla <MC.cfg> [--manifest ...]
```

against five checkable models:

| example | model | source | TLC result (120s external timeout) |
|---|---|---|---|
| 1 (good, modular) | `Shop.tla` | authored for this ticket (scratch) | green, 13 distinct states |
| 2 (good, pipeline nuance) | `OrderFlow.tla` | authored for this ticket (scratch) | green, 36 distinct states |
| 3 (bad, god-state) | `AppState.tla` | authored for this ticket (scratch) | did not finish: 18.8M distinct states generated in 120s, still climbing |
| 4 (validated refactor) | `AppState.tla` remodeled | authored for this ticket (scratch) | green, 36 distinct states |
| 5 (real, mixed) | `specs/program_model/TlaSpecDevCli.tla` + `MC.cfg` + manifest | this repository, as merged by CD-01 | green (same baseline as tlc_current.txt) |

The authored models were designed to *exhibit* the shapes (clean port,
pipeline chain, god-state, oversized domains, unconstrained variables), but
all numbers, tables, cluster assignments, Q scores, warnings, and unknown
markers in the doc are what the scanner actually printed — no output was
invented or edited beyond excerpting. TLC evidence for examples 1–4 was
produced with `bash scripts/run_tlc.sh <model>.tla <MC.cfg>` under an
external 120-second timeout, with `CHECK_DEADLOCK FALSE` in the example cfgs
(terminal states are intended in these toy protocols).

## Assertion 1 — a doc an agent can read to interpret a descriptor and decide whether/how to refactor, with worked good/bad examples and reasoning

Met. The doc walks every section of the real output format (dimension table,
bound/UNKNOWN, R/W matrix, modularity Q + clusters + port-crossing actions,
dense rows/columns, invariant coverage, justification linkage, advisory
thresholds), gives a good-shape and bad-shape reading for each, and closes
with a six-step reading order ending in a recommendation taken to the user.
Five worked examples with reasoning, including real excerpts such as:

```text
[MEASURED] Near-decomposability
  graph modularity Q = 0.314 over the variable interaction graph
  C1: cart, checkout_phase, receipt_issued  (3 variables, 4 actions)
  C2: reorder_open, stock_level, supplier_ack  (3 variables, 4 actions)
  candidate port-crossing actions:
    CompletePurchase crosses C1, C2
```

(good: nameable clusters, one crossing = the real transaction), and

```text
  dense rows (god-state signature -- variable touched by more than half the actions):
    app_state touched by 5/5 actions
    audit_log touched by 5/5 actions
    cache_epoch touched by 5/5 actions
```

(bad: bookkeeping written by every action; no cut exists). Example 2
deliberately teaches the two places the metrics mislead if read naively
(Q = 0.000 on a clean pipeline; dense-row flags noisy in small models), and
example 5 teaches the deliberate-unknown case on this repository's own model
(`lastCommand`/`result`: dense, invariant-unread, bound-excluded — and an
intentional observability channel).

## Assertion 2 — the refactor-input framing is wired into the workflow/doctrine

Met. The exact framing "take this complexity descriptor to consider how to
refactor complexity out of the app" now appears:

- as the opening sentence of `references/complexity_intuition.md`;
- in SKILL.md, "What Is Shipped And What Is Experimental", shipped-descriptor
  paragraph ("The working framing is: **take this complexity descriptor to
  consider how to refactor complexity out of the app** — the descriptor is
  refactoring *input* the agent reads and judges, never automated moves"),
  pointing to the new reference;
- in SKILL.md, "Complexity Budgets Are Advisory" ("Whenever a descriptor is
  produced, take it to consider how to refactor complexity out of the
  app..."), pointing to the new reference;
- in the SKILL.md References index entry for the new doc.

## Assertion 3 — "how complex should a program be" best-practices section; validated refactors encouraged

Met. The doc's second section is titled "How Complex Should A Program Be?"
and states the proportionality principle in both directions (big-because-
behavior is fine; big-because-representation is accidental), gives the
essential-distinction test, and states: "A validated architectural refactor
that lowers complexity is encouraged as normal practice, not an exceptional
event", defining validated as (1) TLC and tests green, (2) behavior
preserved, (3) before/after descriptors compared and reported jointly with
retention evidence. Worked example 4 demonstrates the full pattern with a
real before/after (bound 1,654,784 with two unbounded unknowns and a TLC
timeout → bound 576, full invariant coverage, TLC green), including the
honesty notes (coarsening is only behavior-preserving when no property made
the finer distinction; the irreducible small core still flags dense rows;
check the transition-level diff for deleted self-loops). The encouragement is
repeated in the SKILL.md "Complexity Budgets Are Advisory" wiring.

## Assertion 4 — no automated-suggestion claims anywhere

Met. The doc's second paragraph states the CD-01 removal and its reason (the
chooser was confidently wrong on standard TLA+), and the doc states —
opening, per-example, and in the closing reminders — that these are
intuitions for the agent to judge with, never automated moves; the scanner
prescribes nothing; recommendations go to the user for approval. Checked by
re-reading the full doc and the SKILL.md diff: no sentence claims the tool
suggests, recommends, or chooses a move; the new References index entry says
"never automated suggestions" explicitly. The descriptor excerpts themselves
carry the scanner's own "makes no suggestions" language.

## Assertion 5 — zero TLA+ model delta; TLC green; max_distinct_states 500000 carried with rationale

Met.

- `diff -r specs/tickets/CD-02/current specs/tickets/CD-02/desired` — no
  output (identical), and both are unchanged from the epic baseline merged by
  CD-01 (docs-only ticket; `git status` shows no edits under either
  directory).
- TLC on ticket current (`bash scripts/run_tlc.sh
  specs/tickets/CD-02/current/TlaSpecDevCli.tla
  specs/tickets/CD-02/current/MC.cfg`, 120s external timeout):
  `Model checking completed. No error has been found.` — 5,619,356 states
  generated, 231,621 distinct, depth 25 (`results/tlc_current.txt`),
  identical to the CD-01 baseline figures and 46.3% of the 500000 budget.
- `specs/tickets/CD-02/desired/spec_manifest.yaml` line 98 carries
  `max_distinct_states: 500000` with the full NEGOTIATED 2026-07-19
  derivation rationale (measured throughput, decay halving, epic worst case,
  REVISIT note) — byte-identical in `current/`, and the same block is in the
  promoted project `specs/current/spec_manifest.yaml` (verified post-close).

## Validation matrix results

| check | command | result | evidence |
|---|---|---|---|
| TLC (ticket current) | `bash scripts/run_tlc.sh specs/tickets/CD-02/current/TlaSpecDevCli.tla specs/tickets/CD-02/current/MC.cfg` (120s ext. timeout) | green, 231,621 distinct / depth 25 | `results/tlc_current.txt` |
| spec-unit | `python3 scripts/tla_spec_dev.py --spec-root specs run spec-unit-tests --ticket CD-02` | passed, 2 targets (63 + 60) | `results/spec_unit_tests.txt` |
| repository unit | `uv run --with pytest --with pyyaml -m pytest tests -q` | 532 passed | `results/repo_unit_tests.txt` |
| specWorkflow graph | `python3 ~/.claude/skills/test-graph/scripts/run.py specWorkflow` | BUILD SUCCESSFUL, 8 steps | `results/graph_specWorkflow.txt`, `results/graph-reports/specWorkflow-20260722-004036-104c0f98` |
| cliWorkflow graph | `python3 ~/.claude/skills/test-graph/scripts/run.py cliWorkflow` | BUILD SUCCESSFUL, 2 steps | `results/graph_cliWorkflow.txt`, `results/graph-reports/cliWorkflow-20260722-004058-48922790` |

## Deferred findings

One, batch mode, non-blocking: `CD-02-DF-01` in
`specs/desired_program_model/deferred_findings.yaml` — `analyze complexity`
without `--manifest` prints the sentinel path in its warning ("no readable
spec manifest at does-not-exist"), from `scripts/analyze_complexity.py:1044`.
Cosmetic; defaults are applied correctly. Budget used: 1 of 5.
