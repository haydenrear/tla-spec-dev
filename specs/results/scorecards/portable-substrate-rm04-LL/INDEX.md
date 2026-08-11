# Scorecards — portable-substrate-rm04-LL

scorecard_version 4. See `references/eval_scorecard.md`.

**Never average across examples.** `ex6_jenga` is a deliberately
incoherent fixture and is supposed to score low on D3; averaging it
with `ex4` produces a number about nothing. Nothing in this file is
computed across two examples.

**No total, from scorecard_version 3.** Four of its five terms cannot
carry a delta, so a sum over them moves most where the card reads
worst. Read a dimension.

**`contested` is computed, never declared.** Scoring rule 5 — a spread
greater than 1 across the judges of one artifact — is re-derived from the
cards on every run. A card's own `contested` field is a declaration and
cannot manufacture one or erase one; where the two differ, the difference
is printed below the table.

| example | arm | judge | tier | D1 bug detection | D2 complexity | D3 modularity | D4 behavior preservation | D5 honesty | contested |
|---|---|---|---|---|---|---|---|---|---|
| eval_toolchain | LL | pass 1 | opus | — | 1 | 1 | — | — | — |
| eval_toolchain | LL | pass 2 | sonnet | — | 2 | 0 | — | — | — |

### Contested — rule 5, computed

None. No dimension has a spread greater than 1 in any judge group here.

### Tier splits

A dimension where two judge tiers do not overlap at all on the same
artifact. Reported only where the ranges are DISJOINT — an overlap is two
tiers agreeing as far as this can tell.

- **eval_toolchain / arm LL, D2** — `opus` [1]; `sonnet` [2]; `sonnet` higher by 1.0 point(s).
- **eval_toolchain / arm LL, D3** — `opus` [1]; `sonnet` [0]; `opus` higher by 1.0 point(s).

- **eval_toolchain** (20260810-rm04-LL-p1): Route the eight unguarded `--out` write sites (generate_docs.py:20, run_kill_test.py:102, tla_spec_dev.py:593, effect_conformance_report.py:170, infer_action_params.py:872, generate_python.py:992, export_testgraph_cases.py:174) through spec_paths.resolve_evidence_out/resolve_spec_tree_out or declare ports that cover them, and correct the 'true of every caller' claim at spec_paths.py:69 -- a fault I seeded wrote outside every declared port target at exit 0, which is why this scores D3 1 and not 2. DISCLOSED, no arm leak: `git status`, run to confirm I had changed nothing else, showed sibling card PATH NAMES (subjects GG and JJ, two passes each, plus a p2 on LL) which I did not open; nothing maps LL to an arm.
- **eval_toolchain** (20260810-rm04-LL-p2): scripts/ is a well-measured, low-god-state CLI toolchain (D2: 2) that is honest in its own code about what it cannot see, but it enforces ports-and-adapters discipline on the projects it scaffolds without practicing that discipline on itself -- effects are written from everywhere in its own modules and it declares no interface of its own (D3: 0).
