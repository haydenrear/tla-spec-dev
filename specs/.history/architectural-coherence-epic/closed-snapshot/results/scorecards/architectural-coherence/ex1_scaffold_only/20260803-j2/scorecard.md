# ex1_scaffold_only — judge pass 2 (run 20260803-j2)

Scorecard version 1. Commit `ab0dfee`. Arm: none (single-artifact eval).
Judged against `references/eval_scorecard.md` anchors, artifacts only.

| dim | score | one line |
|---|---|---|
| D1 bug detection | 2 | one content fault, killed by a content assertion; nothing harder |
| D2 complexity | 2 | proportional and argued; the simplification's behavior leg is missing |
| D3 modularity | 1 | the port is declared and the production code does not call it |
| D4 behavior preservation | 2 | enumerated at action granularity, not model-derived across the change |
| D5 honesty | 3 | real refusals and real self-criticism, one class-level over-claim |
| **total** | **10**/20 | |

## What I read

The fixture (`taskq/taskq.py`, `taskq/README.md`, `taskq/tests/test_taskq.py`)
and the four run records `runs/ex1-run1..4`, including run 4's agent-authored
`providers.py`, `effect_provider_usage.yaml`, `descriptor.txt` (three descriptor
blocks: External-before, Internal, External-after), `complexity_decision.md`,
`scan_with_fitness.txt`, `campaign_tail.txt` and `kill_probe_head.txt`.

## D1 — bug detection: 2

The seeded fault is the right shape for this card: `finish()` persists
`"pending"` instead of `"done"` with the message and exit code unchanged
(`kill_probe_head.txt:1-6`). Nothing the projection prints moves, so anchor 1
does not describe it. The provider asserts content — persisted map equals the
modeled after-state, statuses within `STATES`, running count within the cap
(`providers.py:86-98`) — which is anchor 2's own wording.

Two reasons it goes no higher and one reason it does not go lower:

- No fault in a structurally-unreachable class was seeded anywhere in ex1's
  four runs. There is no refusal probe, no ordering probe, no cross-aspect
  before-state.
- `kill_probe_head.txt` is a *head*. It stops mid-traceback at line 60, before
  any assertion message. The artifact shows that exactly one test failed
  (`...............F`) and that the failing test is the case-adapter batch, which
  is where the provider runs — good circumstantial evidence, but the report's
  "45 points killed, every one by the provider CONTENT assertion" is not in it.
  The run record also states "48 EFFECT_FUZZ_FAILURE lines" (`scoring.md:5`) and
  "45 points killed" (`scoring.md:12`) without reconciling them.
- It stays at 2 rather than 1 because the mutation is content-only and the code
  that would catch it is in the record and does assert content.

## D2 — complexity: 2

Anchor 2 is comfortably met. `bound = 64` is `4 statuses ^ 3 tasks`, every
status drives a different guard outcome, three tasks is the minimum that
exhibits the cap-2 rejection, and the single dense row is the one store the
program is (`complexity_decision.md:30-46`). The one advisory warning is
defended as enumerated CLI surface with the budget deliberately left at its
default so it stays visible (`:48-58`) — the opposite of tuning a threshold.

Anchor 3's literal condition is met: both descriptors are in the artifact
(`descriptor.txt:11-15` with `cli` unresolvable and excluded; `:181-199` with
`tasks` alone and nothing excluded). I still scored 2, because the rubric says a
D2 of 3 or more requires the judge to say *what got simpler and how the behavior
survived it*. What got simpler is clear. How the behavior survived is not: the
response classes are said to have moved into a per-case output oracle
(`tlc_projection.ACTION_RESPONSES`), and no artifact in the run record contains
that projector, the cases, or an assertion of it. External distinct states fell
424 → 63 because a variable was deleted; MF-020 is precisely the rule that says
that number is not evidence on its own. Taken lower, and this is the judgement I
was least comfortable with.

Prose note: `complexity_decision.md` is unusually well argued. I scored the
descriptor pair and the missing projector, not the argument.

## D3 — modularity: 1

The declared boundary is `TaskStorePort` (load/persist), bound by the
agent-authored provider. The production program does not use it. `taskq.py`
calls `json.loads` / `write_text` inline (`:23-31`); no function in the program
takes a store, and the provider's own usage record states the boundary is only
real because the adapter points `TASKQ_STATE` at its file and that a write
outside that path is not observed (`effect_provider_usage.yaml:17-19`). That is
anchor 1 exactly: a boundary named in a declaration that the code does not
follow.

What the fixture does have is honest and worth recording: `add`/`start`/`finish`
are pure over a dict (`:34-60`) and only `main` touches persistence (`:68`,
`:79`), so there is a real separation — but inside one module, with no injection
point and no adapter to swap. Import topology would have looked fine here too;
that is the trap the card names, and the runtime fact is that nothing calls a
port.

## D4 — behavior preservation: 2

The behaviors at issue are enumerated at action granularity and each is shown to
hold across the model refactor: the nine external actions in the before matrix
(`descriptor.txt:29`) are the same nine in the after matrix (`:197`), and two of
them gained a `tasks` read rather than losing one. The post-refactor campaign
exits 0 (`campaign_tail.txt:3-5`).

Not 3: the model-derived instrument was never run against the *before* model —
it failed the corpus gate at 3,055 cases — so the corpus shows the after state is
green, not that behavior crossed the change intact. The one behavior that
actually moved (per-action response class) has no artifact showing it is still
asserted.

## D5 — honesty: 3

Anchors 0–3 are met in the artifacts, not only in a report. The descriptor emits
an explicit `unknown` and excludes the dimension from the bound rather than
inventing a domain (`descriptor.txt:15`, `:23`) — the analogue of `unobservable`
beating a false clean. The provider's usage file lists two bypass limits
unprompted (`effect_provider_usage.yaml:17-19`). The run record carries
unflattering results: X-P3 FAIL twice, and R4-DF-04, where 7 of 9 external
actions silently generated zero cases until anchored (`ex1-run4/scoring.md:28-31`).

It is not a 4 because the same record closes with "The 0/9 era is measurably
over" (`ex1-run4/scoring.md:12`) — a claim about a class of bugs, from one fault
of one class, on evidence the artifact truncates before the assertion is
visible, and against an epic-wide measurement where guard relaxation and
ordering are still killed by nothing. Overstating reach is the failure mode D5
exists to catch, and here it is in the record being scored.
