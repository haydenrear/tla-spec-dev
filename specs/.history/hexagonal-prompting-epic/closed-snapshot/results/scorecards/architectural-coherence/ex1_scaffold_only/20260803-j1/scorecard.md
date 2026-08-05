# ex1_scaffold_only — judge pass 1 (`20260803-j1`)

scorecard_version 1 · commit `ab0dfee` · arm `null` (single-artifact eval)
Judge: `claude-opus-5[1m]`, pass 1, blind to arm.

| D1 | D2 | D3 | D4 | D5 | total |
|---|---|---|---|---|---|
| 2 | 2 | 1 | 3 | 3 | **11**/20 |

## What is and is not in the fixture

I enumerated it: `taskq.py` (84 lines), `tests/test_taskq.py` (6 tests), a README
that ends "This project has no spec workflow yet." **No specs, no adapters, no
providers, no architecture declarations.** So no descriptor and no architecture
figure was reproducible by me — every model-side number in `mechanical.json` is
`from_record`, produced by an agent's scaffold in a scratch copy. That is a real
limit on this card and it is recorded rather than papered over.

## D1 — bug detection: 2

The fixture alone would sit at anchor 0 or 1: six pytest tests over pure functions
(`test_taskq.py:9-42`), none of which reads the persisted file.

The run evidence lifts it to anchor 2, and it is real code, not a claim:
`ex1-run4/artifacts/providers.py:86-98` compares the persisted task map against
the modeled after-state and raises, and additionally checks that persisted
statuses are members of `STATES` and that the running cap of 2 holds in the
persisted bytes. It caught the seeded fault — `finish()` persisting `"pending"`
with message and exit code unchanged (`kill_probe_head.txt:1-6`) — 45 points, all
by the content assertion, with a working replay and a verified green restore.

Anchor 1 does not fit: the fault required a content assertion and was not missed.
Anchor 3 is not close: **n = 1 fault, one class, no catalogue, no arm split**, and
no attempt at a refusal, an ordering, or a cross-aspect before-state — despite
taskq's model encoding refusals as first-class actions (`CliAddDuplicate`,
`CliStartNotPending`, `CliStartCapReached`, `CliFinishNotRunning`), which would
have made the attempt cheap.

## D2 — complexity: 2

`taskq.py:34-60` is four pure functions over one dict, each touching that dict and
one name. As simple as the behavior requires.

The relationship between figures and design is *argued*, not merely reported —
`ex1-run3/artifacts/complexity_decision.md:12-45` walks unknowns, bound-vs-behavior,
dense rows and clusters in the documented reading order and defends each dimension
against a named consumer. That is past anchor 1. Anchor 3 is deliberately
unreachable: every run concluded "no refactor warranted", so there is no
simplification to measure.

**Tension recorded, not scored down for.** Three of four runs' descriptors show a
dense row (`ex1-run4/artifacts/descriptor.txt:41-42`, `cli` touched by 9/9
actions) and two fired the `max_component_actions` advisory — a variable written
from everywhere by the tool's own definition. It is an artifact of the
observability encoding, not of the program, and the epic measured that itself: the
same 84-line program yields bound 64 under one encoding and 1,152 under another
(`ex1-run2/scoring.md:25-30`). Recorded as a limit on what a cross-project
descriptor comparison can mean.

## D3 — modularity: 1

Anchor 1. A boundary was declared — run 4's agent added a `TaskStorePort` effect
port with a generated Protocol — and the production code does not follow it.

`taskq.py:19-31` keeps `state_path`/`load`/`save` in the same module as the domain
functions, doing their own `os`, `json` and filesystem work; `taskq.py:63-80`'s
`main()` calls `load()` and `save()` directly. Nothing is injected and no adapter
is swappable.

How the declared port is actually realized is stated in the provider's own
docstring (`ex1-run4/artifacts/providers.py:11-16`): the provider owns a concrete
file and "the spec-unit adapter points `TASKQ_STATE` at `binding.state_file` and
runs the real CLI." **That is environment-variable redirection of a hardcoded
path, not a port** — the domain still performs its own I/O on whatever path it
computes. Anchor 2 needs a cross-boundary call through something identifiable as a
port; there is none. Anchor 3 needs the domain not to import its I/O;
`taskq.py:10-13` imports `json` and `os` and uses them inline.

`add`/`start`/`finish`/`listing` *are* separable in principle, which is why this is
1 and not 0 — and separable in principle is exactly what anchor 1 describes.

## D4 — behavior preservation: 3

Anchor 3 is met: behaviors enumerated (`test_taskq.py:9-42`) and shown to hold,
and the check is model-derived — TLC-green Internal and External views in all four
runs, an exhaustive generated corpus, and a 1,640-point campaign.

Anchor 4's condition is literally met once (`ex1-run4/scoring.md:12`: a deliberate
behavior-breaking change, caught, replayed exactly, restore verified green). I take
the lower anchor because the model-derived half has a measured hole nothing closed:
`ex1-run4/scoring.md:28-36` records that pure alias wrapper actions were attributed
to the inner definition site so **7 of 9 external actions silently generated zero
cases until anchored**, and that parameter inference recovered **0 of 454 external
cases** — the same oracle-leakage and vacuity exposure RP-02 had to fix for ex4,
present here and never fixed. A check demonstrated capable of failing on one fault,
over an arm where a whole class of cases was silently empty and no argument is
audited, is a 3.

## D5 — honesty: 3

Anchor 3 is clear:

- The descriptor refuses to invent a bound and prints an explicit `UNKNOWN` rather
  than the silent `bound = 1` the old path produced (`ex1-run1/scoring.md:12`).
- X-P3 is scored **FAIL** in runs 1, 2 and 4 (`ex1-run1/scoring.md:18`).
- VAL-04 is filed *against the toolchain's own scaffold* for contradicting the
  advisory doctrine (`ex1-run1/scoring.md:22-26`).
- The run-1 vs run-2 divergence is reported as a fact about the descriptor's
  sensitivity to encoding rather than smoothed over
  (`ex1-run2/scoring.md:25-30`).

What stops it reaching 4 is a specific over-reach. `ex1-run4/scoring.md:12`
concludes **"The 0/9 era is measurably over"** and the run's verdict calls the
result "the compounding the two epics were built for" — from one seeded fault of
one class on one 84-line program. The epic's own later measurement contradicts the
generalization: `ROUND-2-DELTA.md:65`, the mutant matrix did not move a single
cell, guard relaxation and ordering still 0 of 3. Anchor 4 asks for a result
unflattering to the thing being scored; the R4-X1 PARTIAL and five filed defects
qualify, but a record whose headline sentence outruns its own n does not clear the
top of an honesty scale. Torn between 3 and 4, lower per rule 5.

## Verdict

The entry-path fixture works and its four runs are honest about the friction, but
it is a single-file program whose domain does its own I/O, whose declared port is
an environment variable pointing at a path, and whose entire bug-detection evidence
is one seeded fault — from which its own record concludes that an era is over.
