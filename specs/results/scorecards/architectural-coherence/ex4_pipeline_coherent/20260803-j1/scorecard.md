# ex4_pipeline_coherent — judge pass 1 (`20260803-j1`)

scorecard_version 1 · commit `ab0dfee` · arm `null` (single-artifact eval)
Judge: `claude-opus-5[1m]`, pass 1, blind to arm.

| D1 | D2 | D3 | D4 | D5 | total |
|---|---|---|---|---|---|
| 2 | 2 | **3** | 3 | **4** | **14**/20 |

## What I re-ran myself

Read-only, at this commit, via `python3 scripts/tla_spec_dev.py` (never the PATH
wrapper):

- `analyze complexity` on `Pipeline.tla`/`.cfg` — bound 4,096 COMPLETE, Q = 0.194
  emergent, one dense row (`delivered`, 3/5), no dense columns, no warnings.
- `analyze architecture` with `--components --code pipeline --map` — `coherent`,
  exit 0, 8/8 modules mapped, 4 edges, 2 convergences, 0 divergences, 0 absences,
  `divergence_detectable = true`.
- `analyze architecture` with no `--components` — `emergent`, C1 = {delivered,
  failed, ledger, queue}, C2 = {accepted, inbox}.
- `grep` across both twins and all runs for `PipelineSpecDouble` — zero hits
  outside the generated package.

The answer key reproduces. Everything else in `mechanical.json` is transcribed
from committed run artifacts and labelled `from_record`.

## D1 — bug detection: 2

`providers.py:88-96` raises on `sorted(persisted) != sorted(modeled after-state)`
and `tlc_projection.py:58-63` puts three counts and a status enum into the output
oracle. Those are content assertions in code, not a claim about content
assertions — which is why F1/F2/F4/F6 die on the corpus alone and F3/F5 die only
under the provider. That is anchor 2, cleanly.

Anchor 3 asks for a fault in a class the whole-view corpus **structurally cannot
reach** — the anchor names refusals, orderings, cross-aspect before-states.
Measured three times by three instruments: guard relaxation 0/3 on both arms and
0/4 on all five corpus instruments; ordering 0/3 and 0/2, killed by nothing at
all including pytest (`ex4-run4/scoring.md:73-74`,
`ex4-run6/scoring.md:112-125`). The one cross-aspect before-state mutant in the
blind catalogue (M16) was killed **by** the whole-view corpus, which is the
inverse of the anchor's condition.

The genuinely hard call: F3 and F5 are unreachable by the corpus alone and are
reached by the provider. I read them at anchor 2 rather than 3 because anchor 2's
own wording is "wrong-content faults through adapters that assert content", which
is exactly what they are, and because anchor 3's parenthetical enumerates the
three classes this project has repeatedly measured as structural. Torn, so lower,
per rule 5.

**Prose note.** This fixture's write-up is the most disciplined in the tree —
per-arm, per-class, never aggregate, with the honest negative as its own heading.
It earned nothing. The score is the kill matrix and two provider classes and
would be identical if the prose were unreadable.

## D2 — complexity: 2

Six variables, five actions, no variable written by more than two actions
(`Pipeline.tla:24-99`); bound 4,096 with every domain resolved. Proportional to
behavior, no god-state. Anchor 2.

Anchor 3 is unreachable here: no simplification was made to this fixture, so
there is no before/after pair to record. The one structural argument the fixture
does make (`README.md:96-107` — three components rather than two, so a divergence
is possible at all) is a reason for *adding* structure. That is an argued
relationship between figures and design, which is above anchor 1, but adding
structure for a measured reason is not a measured simplification.

**Recorded, not scored** (card rule 7 — a disagreement between the mechanical
block and the artifact is a finding): `README.md:102` states that greedy
modularity returns two components with "`queue` clusters with ingest". The
descriptor I ran puts `queue` in C1 with `delivered`, `failed` and `ledger`. The
two-component conclusion survives; the parenthetical is false of the tool.

## D3 — modularity: 3

This is where the fixture is strongest, and the evidence is runtime, not import
topology.

`journal.py:27-49` takes its store as an injected collaborator and calls
`store.persist(...)`; it imports no store implementation. The swap is not
asserted, it is **executed**: `case_adapters.toml:22-23` and
`case_adapters_corpus_only.toml:22-23` bind two different providers, and
`ex4-run4/scoring.md:24-28` records 330 cases exit 0 under each, with run 4's
`kill_matrix.json` showing the *same* stdout sha256 (`26bd9bc2…`) for both
control arms. Same cases, two adapters, both green — that is what anchor 3 asks
for, named specifically.

Not 4. Anchor 4 needs a real adapter **and a fake**. Both providers wrap the same
real `FileLedgerStore`; the only generated fake, `PipelineSpecDouble.persist`,
raises `NotImplementedError` and is referenced nowhere outside its own package (I
grepped both twins and every run directory). Two weaknesses recorded and not
scored up: the port is typed `object | None`, so the generated `LedgerStorePort`
Protocol is decorative; and only one of the three component crossings is a port
in fact — `dispatch -> ingest` and `ledger -> dispatch` are direct concrete
imports and direct method calls.

## D4 — behavior preservation: 3

Anchor 3 is met without argument: one test per action plus an interleaving
(`test_behavior.py:23-113`), three TLC invariants (`Pipeline.cfg:2-4`), and a
330-case corpus generated from the state graph. The check is model-derived, not
only hand-written.

Anchor 4's literal condition is also satisfiable — 12 of 19 mutants killed with
failing-case sets recorded. I take the lower anchor for a specific reason that is
about this artifact and not about the anchor: the fixture's own enumeration of
behavior contains a claim that is **false of the model and that no check can fail
on**. Two independent blind agents found that `Fail(i)` removes an item from
`delivered` while `Record(i)` requires it, so a failed item can never reach the
ledger, while the README promises the opposite; `LedgerIsDownstream` is written
weakly enough to pass vacuously on the half that matters; and
`test_two_item_interleaving` asserts the negation of the README sentence
(`ex4-run6/scoring.md:176-190`). A behavior-preservation check that cannot fail on
the artifact's headline promise is not a 4.

## D5 — honesty: 4

- Blind spots in the artifact, not only in a report: `README.md:126-136` states
  that the composition root has nowhere to live and that this is a question the
  check cannot answer; `README.md:166-167` pre-commits a condition under which the
  **fixture itself** is the finding.
- Refusal rather than false certification: `analyze architecture` on this fixture
  with no code emits `architecture_scan = unmappable` with its reason. I
  reproduced it.
- Correction in place rather than edit-to-agree: `seeded_faults.toml:137-151`
  keeps the original answer-key text and appends "the paragraph above is
  superseded, and it was WRONG on its second half."
- Unflattering results in the record: "the mutant matrix did not move a single
  cell" (`ex4-run4/scoring.md:79-99`); `--effect-report` silently writes nothing on
  this very fixture while a code comment two lines above the gate claims it writes
  unconditionally (`ex4-run6/scoring.md:200-215`); and this fixture's `coherent`
  is documented as conditional on directory nesting depth.

`refuses_to_claim`: that its `coherent` is a property of the code.
`ROUND-2-DELTA.md:310-318` records that "precision 1.000" must now carry "on a
tree that was not attacked through a nested first-party package", and that moving
the generated package up one directory flips `coherent` to `unmappable` with zero
bytes of Python changed. It also refuses to claim the corpus reaches guard
relaxation or ordering, and refuses to report the 56-case aspect union as
coverage of the 330-case view.

## Verdict

The strongest of the five: a real injected port swapped between two providers and
executed under both, a per-arm per-class kill matrix that reproduces cell for
cell, and a record that publishes its own false-clean route — but its bug
detection stops exactly where a generated corpus structurally stops, and its own
README makes a promise about failed items that the model contradicts and no check
can fail on.
