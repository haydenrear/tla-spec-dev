# Blind run B — author one aspect knowing only the public surface (ex4_pipeline_coherent)

Owner-scored 2026-07-27. QA-engineer persona; never saw PREDICTIONS.md, the
answer key, the seeded-fault table (removed from the copy), or any epic context.

## Aim 2 (manual-test substrate) — the numbers

- **60 lines authored** by the agent (36 `.tla` incl. a 17-line prose claim,
  6 `.cfg`, 18 manifest block) -> **38 cases over 3 actions** from 24 states,
  under a second. Toolchain generated 1,162 lines from those 60.
- **38 cases kill exactly what the 330-case whole-view corpus kills.** The
  Given form bought an 8.7x reduction with ZERO measured loss of kill power on
  a 12-mutant catalog. This is the strongest single result in the epic.
- `case_modules.py validate` and `coverage` both exit 0; CM-F2's fix confirmed
  from the outside (zero spurious zero-case warnings); the removal test passes.

## Aim 1 (harder bugs) — the agent ran its own 12-mutant catalog

| class | mutants | slice (38) | view (330) | hand-written pytest |
|---|---|---|---|---|
| wrong write on an enabled transition | M5-M8, M10 | **5 killed** | 5 killed | 4 killed (M10 MISSED) |
| guard relaxation | M1-M3 | 0 killed | 0 killed | **3 killed** |
| ordering / sequence | M9, M11, M12 | 0 killed | 0 killed | 0 killed |
| equivalent mutant | M4 | n/a | n/a | n/a |

Honest denominator: 5 of 11 non-equivalent, or 5 of the 8 the model can even
express. Three conclusions, each mechanism-attributed:

1. **The corpus and the hand-written suite are complements, neither subsumes
   the other.** M10 (durable ledger persists only the last entry) is killed by
   the corpus and missed by every hand-written test, because `tests/` never
   binds the `LedgerStorePort` boundary. M1-M3 are the reverse.
2. **Guard relaxation is invisible by construction.** A generated corpus
   replays only ENABLED edges, so it contains no rejected inputs: a service
   that accepts what the model forbids passes every case. Compounded by
   ORACLE LEAKAGE — the adapter recovers the action argument from the case's
   AFTER-state, so it only ever calls with the argument that was going to
   succeed. This is EV-01-DF-01 confirmed independently, from the outside.
3. **Ordering is invisible at every layer.** `ledger` and `queue` are TLA+
   SETS; the code implements them as ordered lists documented "append-only"
   and "in insertion order". Projector sorts, adapter uses `frozenset`,
   provider compares `sorted()`. A ledger that silently reverses is
   undetectable. Modeling gap, not a tool bug — and no case module can fix it.

## The finding worth more than the corpus (owner-verified)

Working from the README alone, the agent found that **the public surface is
false of the model and of the service**: `Fail(i)` removes `i` from
`delivered`, `Record(i)` requires `i \in delivered`, so once an item fails it
can NEVER reach the ledger — while the README promises "a failed item is
recorded as failed" and "the ledger records each outcome". Owner confirmed
directly from `Pipeline.tla`.

**No case module could ever catch this.** A case module may not add an action,
and there is no action to enter; a corpus can only test behavior the model has.
The value here came from the human-facing act of writing the aspect, not from
the cases it generated. That is a real and unexpected argument for the
manual-test-starter path — and an argument that its value is not measured by
kill rate.

## Aim 2's limit, stated by the agent

- A **slice** is writable from action names alone: README + `actions.yml`.
- A **Given** must constrain EVERY variable of the view, which forced knowledge
  of all six internal state variables and each action's guard. The README names
  none of them.
- So: **the aspect came from the outside; the Given could only be written from
  the inside.** Neither doc states this. The "non-author writes an aspect"
  claim holds for slices and fails for Givens.

## Step 0 is unenforceable (predicted, confirmed)

The prompt requires the aspect list to come from the model author and never be
derived. Nothing stopped the agent producing a complete, schema-valid,
coverage-clean decomposition with no author in the loop; the `Source` column is
free text, never checked. The agent flagged its own violation, which is the
best available outcome but not a control.

## Doc/tooling friction (8 items, all reproducible)

1. `aspect_decomposition.md` Step 1's command does not run as written
   (`--spec-root` ignored for the positional path); its `jq` pipeline assumes
   JSON-only stdout.
2. **A case module cannot generate from where the docs put it.** TLC runs with
   cwd = the `.tla`'s directory and no module search path, so a module in
   `specs/case_modules/` cannot `EXTENDS` a view in `specs/program_model/`.
   The checked-in module is therefore NOT reproducible in place; the failure is
   a 30-line TLC AbortException preceded by a misleading fail-closed paragraph.
3. `--out` resolves against the `.tla`'s directory, not cwd — undocumented.
4. **Every documented command path assumes an external view** (`--view
   external`, `testgraph/`, `testgraph_bindings.yml`). An internal-only project
   has no worked example anywhere.
5. `run_generated_case_adapters.py` needs two `--import-root` flags; the error
   names one.
6. Interpreter roulette: no `python3` on PATH has both `yaml` (toolchain) and
   `pytest` (README). Neither doc states an environment requirement.
7. `param_recovery_audit.md` says "every parameter is recoverable" while the
   same run reports 0/38 cases carrying arguments — the audit contradicts the
   corpus it audits.
8. Nothing in the repo was modified by this run (owner-verified clean).
