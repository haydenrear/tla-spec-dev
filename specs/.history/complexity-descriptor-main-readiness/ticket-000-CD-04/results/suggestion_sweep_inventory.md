# CD-04 suggestion-language sweep inventory (resolves VAL-13)

Full repo-wide inventory of prescriptive-suggestion language, with a
per-occurrence disposition. The owner's stated concern is that earlier passes
missed cases; this is the complete grep-driven census, before and after the
change.

## Method

```
grep -rniE "suggested move|suggest_move|recommendation requiring|apply the suggested" . --exclude-dir=.git
```

Run at the worktree root on branch `feature/89-cd04-redesign-question`
(base: `origin/epic/complexity-descriptor` @ 48f3ff6), 2026-07-22.
Case-insensitive; all four patterns from the plan entry.

## Exempt directories (declared by the plan entry, listed as required)

| Directory | Occurrences (before) | Occurrences (after) | Why exempt |
|---|---|---|---|
| `specs/.history/` | 660 | 660 | Append-only immutable history; sealed snapshots of past tickets. Never edited. |
| `examples/validation/runs/` | 3 | 3 | Sealed validation-run evidence (the VAL-13 discovery itself lives here). Never edited. |

Totals: 734 occurrences before (663 exempt + 71 non-exempt);
734 after (663 exempt + 71 non-exempt, every non-exempt one now a negative
guard, historical record, self-reference, or finalization-deferred mirror —
see dispositions).

## Disposition legend

- **REWORDED** — prescriptive wording replaced by the finding + redesign-question form in this ticket.
- **REMOVED** — prescriptive machinery/assertion deleted in this ticket.
- **NEGATIVE GUARD** — the occurrence *asserts the absence* of the banned wording (doctrine enforcement). Kept; it is the regression tripwire, not prescriptive output.
- **HISTORICAL RECORD** — narrative of a past ticket/epic describing the old behavior or its removal; sealed evidence or immutable work order. Exempt, left verbatim.
- **SELF-REFERENTIAL** — CD-04's own plan/ticket text quoting the wording it removes. Exempt.
- **DOCTRINE STATEMENT** — documentation sentence of the form "emits no suggested move". Descriptive of absence, not prescriptive. Kept.
- **FINALIZATION-DEFERRED** — workflow-level model mirror (`specs/program_model/`, `specs/desired_program_model/` adapters) that only whole-workflow promotion may reconcile; ticket agents must not run `close_tickets.py`. Recorded in the epic deferred-findings backlog (CD04-DF-1).

## Per-occurrence inventory (all 71 non-exempt occurrences, before state)

### Reachable output / production code

| File:line | Occurrence | Disposition |
|---|---|---|
| `scripts/corpus_diagnostics.py:47` | docstring "Remediation output is a RECOMMENDATION REQUIRING USER APPROVAL" | REWORDED — docstring (also `main()` help text) now states the finding + redesign-question doctrine |
| `scripts/corpus_diagnostics.py:48` | docstring "same rule as analyze complexity's suggested move" | REWORDED (same hunk) |
| `scripts/corpus_diagnostics.py:93` | `RECOMMENDATION_BANNER = "RECOMMENDATION REQUIRING USER APPROVAL -- not applied automatically."` | REMOVED — replaced by `REDESIGN_QUESTION` constant |
| `scripts/corpus_diagnostics.py:760` | `lines.append(f"  Suggested move: {group.recommendation}")` | REMOVED — per-group output now ends at the measured cause + evidence; report closes with the REDESIGN QUESTION block |
| `scripts/corpus_diagnostics.py:767` | `"Apply the suggested move above, once the user approves it."` | REMOVED — way-forward 1 is now the redesign judgment, made with the descriptor + `references/complexity_intuition.md` |
| (related, not grep-matched) `corpus_diagnostics.py` `RedundantGroup.recommendation` field + `classify_cause` third return value (the prescriptive move strings "Add a state constraint…", "Declare the interchangeable values a symmetry set…", "Abstract the before-state…", "Inspect the varying fields… decide which of symmetry reduction, a state constraint, or abstraction…") | prescriptive-move machinery | REMOVED — `classify_cause` now returns `(cause, evidence)` measurements only |
| `scripts/tla_spec_dev.py:612` | analyze corpus help: "The suggested move is a RECOMMENDATION REQUIRING USER APPROVAL." | REWORDED — help now states the gate prescribes no move and ends with the REDESIGN QUESTION (descriptor + intuition doc as judgment inputs); `next_step` likewise reworded from "Fix the diagram…" to the question form |

### Repository tests

| File:line | Occurrence | Disposition |
|---|---|---|
| `tests/test_corpus_diagnostics.py:239` | `assert "Abstract the before-state" in group.recommendation` | REMOVED (field gone); cause/evidence assertions retained |
| `tests/test_corpus_diagnostics.py:247` | `assert "symmetry" in group.recommendation.lower()` | REMOVED (field gone) |
| `tests/test_corpus_diagnostics.py:254` | `assert "state constraint" in group.recommendation` | REMOVED (field gone) |
| `tests/test_corpus_diagnostics.py:274,276-277` | test asserting the banner appears per over-cap group | REWORDED — replaced by `test_over_cap_output_asks_the_redesign_question_and_prescribes_nothing` + `PRESCRIPTIVE_MOVE_WORDING` tripwire (fails if any prescriptive wording returns, in render output, CLI over-cap output, or `--help`) |
| `tests/test_corpus_diagnostics.py:446` | `assert "RECOMMENDATION REQUIRING USER APPROVAL" in result.stdout` (help test) | REWORDED — help test now asserts REDESIGN QUESTION + intuition doc and bans the prescriptive family |
| `tests/test_analyze_complexity.py:442` | docstring "Validation project 1 proved the suggested moves confidently wrong" | HISTORICAL RECORD in a docstring explaining a NEGATIVE GUARD — kept |
| `tests/test_analyze_complexity.py:452` | `"SUGGESTED MOVE"` in banned-token list | NEGATIVE GUARD — kept (CD-01 tripwire). File owned by CD-05 conflict keys; not touched |
| `tests/test_analyze_complexity.py:473` | `for name in ("suggest_move", …)` asserting removal | NEGATIVE GUARD — kept |
| `tests/test_analyze_complexity.py:750` | `assert "Suggested move" not in message` | NEGATIVE GUARD — kept |
| `tests/test_analyze_complexity.py:896` | `assert "SUGGESTED MOVE" not in result.stdout` | NEGATIVE GUARD — kept |

### Spec-unit adapters and adapter tests (ticket-local + project current)

The `AnalyzeCorpusAdapter` in `production_adapters.py` positively asserted the
old banner (`"RECOMMENDATION REQUIRING USER APPROVAL -- not applied
automatically." in over.stdout`, line 1540) and exported it as
`remediation_labeled_recommendation`. Updated identically in the three trees
this ticket owns; the check is now `asks_redesign_question_never_prescribes`
(REDESIGN QUESTION + descriptor + intuition doc present, prescriptive family
absent).

| File:line | Occurrence | Disposition |
|---|---|---|
| `specs/tickets/CD-04/desired/production_adapters.py:1540` | positive banner assertion | REWORDED (redesign-question check + negative guards) |
| `specs/tickets/CD-04/current/production_adapters.py:1540` | positive banner assertion | REWORDED (same) |
| `specs/current/production_adapters.py:1540` | positive banner assertion | REWORDED (same; whole-program working copy per `current_model_rule`, re-promoted from ticket desired at close) |
| `specs/tickets/CD-04/{desired,current}/production_adapters.py:1376,1381` and `specs/current/production_adapters.py:1376,1381` | CD-01 banned-token list ("SUGGESTED MOVE", "RECOMMENDATION", …) for `analyze complexity` output | NEGATIVE GUARD — kept |
| `specs/tickets/CD-04/{desired,current}/tests/test_tla_spec_dev_corpus_adapter.py:65` and `specs/current/tests/test_tla_spec_dev_corpus_adapter.py:65` | `test_remediation_is_a_recommendation_never_auto_applied` (docstring "Same rule as analyze complexity's suggested move") | REWORDED — now `test_over_cap_output_asks_the_redesign_question_never_prescribes` |
| `specs/tickets/CD-04/{desired,current}/tests/test_tla_spec_dev_analyze_adapter.py:6,47` and `specs/current/tests/test_tla_spec_dev_analyze_adapter.py:6,47` | "no suggested move and no recommendations" docstrings | NEGATIVE GUARD / DOCTRINE STATEMENT — kept |

### Workflow-level model mirrors (not owned by a wave-1 ticket)

| File:line | Occurrence | Disposition |
|---|---|---|
| `specs/program_model/production_adapters.py:1540` | positive banner assertion | FINALIZATION-DEFERRED — `program_model` is the accepted whole-model; only workflow finalization promotes it (`promotion_rule`; ticket agents never run `close_tickets.py`). Not executed by ticket validation (spec-unit runs `specs/current` + `specs/tickets/CD-04/current`; the test_graph specWorkflow graph runs against a scaffolded fixture repo). Recorded as deferred finding CD04-DF-1 |
| `specs/program_model/production_adapters.py:1376,1381` | CD-01 banned-token list | NEGATIVE GUARD — kept (consistent with promoted trees) |
| `specs/program_model/tests/test_tla_spec_dev_corpus_adapter.py:65` | old test name/docstring | FINALIZATION-DEFERRED (CD04-DF-1) |
| `specs/program_model/tests/test_tla_spec_dev_analyze_adapter.py:6,47` | "no suggested move" docstrings | NEGATIVE GUARD — kept |
| `specs/desired_program_model/production_adapters.py:1540` | positive banner assertion | FINALIZATION-DEFERRED (CD04-DF-1) — workflow-level desired tree is reconciled from current at finalization (precedent: 195b07d) |
| `specs/desired_program_model/production_adapters.py:1376,1381` | CD-01 banned-token list | NEGATIVE GUARD — kept |
| `specs/desired_program_model/tests/test_tla_spec_dev_corpus_adapter.py:65` | old test name/docstring | FINALIZATION-DEFERRED (CD04-DF-1) |
| `specs/desired_program_model/tests/test_tla_spec_dev_analyze_adapter.py:6,47` | "no suggested move" docstrings | NEGATIVE GUARD — kept |

### Documentation

| File:line | Occurrence | Disposition |
|---|---|---|
| `references/modular_fuzzing.md:538-539` (pre-change; grep hit at 229 only — the corpus-gate section text "any move derived from it is a recommendation requiring user approval" was reconciled as the plan requires even though only one line grep-matched) | corpus-gate description prescribing recommendation semantics; cause→move arrows ("unconstrained ordering → state constraint" etc.); "**Write the diagram so the redundant cases are never generated…**" | REWORDED — section now states the finding + redesign-question doctrine, names the descriptor + `references/complexity_intuition.md` as judgment inputs, and marks the cause naming as diagnosis, not a to-do list |
| `references/modular_fuzzing.md:229` | "It emits **no suggested move**: CD-01 removed the abstract/decompose/refactor chooser" | DOCTRINE STATEMENT — kept |
| `references/architecture_tractability.md:148,428` | "emits no suggested move" (×2) | DOCTRINE STATEMENT — kept; file owned by CD-05 conflict keys, not touched |
| `examples/validation/README.md:6` | "there are no gates and no suggested moves" | DOCTRINE STATEMENT — kept; `examples/` owned by CD-08, not touched |
| `COMPLEXITY-DESCRIPTOR-EPIC.md:25-26,67` | epic narrative: why suggested moves were removed; a possible future suggested-move agent | HISTORICAL RECORD — kept (epic decision record, not tool output) |
| `tickets/014-corpus-diagnostics-and-caps.md:63-64` | original MF-014 work order describing the (then-intended) recommendation output | HISTORICAL RECORD — kept (immutable ticket work order; the plan's acceptance exempts immutable ticket records) |

### Sealed results / records

| File:line | Occurrence | Disposition |
|---|---|---|
| `specs/tickets/MF-027/results/analyze-complexity.txt:60` | captured `SUGGESTED MOVE: ABSTRACT` scanner output | HISTORICAL RECORD — sealed ticket evidence |
| `specs/tickets/MF-027/results/complexity-delta.md:91,110` | narrative of that captured output | HISTORICAL RECORD — sealed ticket evidence |
| `specs/results/skill_feedback.md:229,550` | MF-014/MF-023 close summaries quoting old behavior | HISTORICAL RECORD — sealed workflow evidence |
| `specs/results/complexity_ledger.json:2399,2412,2534,3719` | ledger narratives quoting old scanner output / CD-01 removal | HISTORICAL RECORD — sealed ledger |
| `specs/results/complexity_ledger_input.yaml:83` | "CD-01: suggested moves removed after validation" | HISTORICAL RECORD — sealed ledger input |
| `specs/results/epic-close/deferred_findings_final.yaml:387,393` | VAL-13 finding text quoting the gate output this ticket removes | HISTORICAL RECORD — the triaged finding that motivated CD-04; sealed |
| `specs/desired_program_model/ticket_plan.yaml:104-105,118-119` | CD-04 objective quoting the wording and the grep patterns | SELF-REFERENTIAL — the canonical plan entry for this ticket |
| `specs/tickets/CD-04/ticket.yaml:107` | same objective, ticket-local copy | SELF-REFERENTIAL |

## Disposition counts (71 non-exempt occurrences, before state)

| Disposition | Count |
|---|---|
| REWORDED / REMOVED (this ticket) | 16 |
| NEGATIVE GUARD — kept | 25 |
| DOCTRINE STATEMENT — kept | 4 |
| HISTORICAL RECORD — kept | 17 |
| SELF-REFERENTIAL — kept | 5 |
| FINALIZATION-DEFERRED (CD04-DF-1) | 4 |
| **Total** | **71** |

(Counting per grep-matched line; the removed `classify_cause` prescriptive
strings and the `recommendation` field were prescriptive machinery removed in
the same pass but did not themselves grep-match the four patterns.)

## After state

Re-running the same grep after the change: zero matches under `scripts/`;
every remaining non-exempt match is a negative guard (banned-wording
tripwires in `tests/test_corpus_diagnostics.py`, `tests/test_analyze_complexity.py`,
and the adapters), a doctrine statement ("emits no suggested move"), a
historical/sealed record, self-referential CD-04 plan text, or the
finalization-deferred workflow mirrors recorded as CD04-DF-1.

No reachable output, help text, or passing test asserts or prints
prescriptive-move wording. The regression tripwires
(`PRESCRIPTIVE_MOVE_WORDING` in `tests/test_corpus_diagnostics.py`;
`asks_redesign_question_never_prescribes` in the corpus adapter) fail the
suite if it returns.
