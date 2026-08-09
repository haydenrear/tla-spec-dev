# RD-06 — sealed before anything was dispatched

**This file is committed BEFORE the first producer agent runs.** Everything it
declares is declared with no artifact in existence and no figure known. That is
the whole point: *anything added after the numbers are known is not evidence*,
and this project has a script on its record containing
`if "ab_quota_ledger" not in f: continue` written to confirm a claim after the
claim had been published four times.

Read this beside `git log` — the commit that adds this file precedes every
commit that adds a subject tree, so the ordering is in the history rather than
in a promise (`PREDICTIONS-PA.md`'s N07/N08 precedent).

---

## 0. What this ticket is, and the one thing it does not do

RD-06 **produces subjects**. RD-03 scores them, blind.

**This ticket scores nothing.** No D-number is assigned here, no verdict is
reached about any artifact, no card is filled, and no comparison between arms is
drawn. Producing a subject and judging it are different jobs; one agent doing
both is how a round scores its own homework. `tests/test_rd06_subjects.py`
checks the produced evidence for score-shaped content and has a demonstrated
failing input.

## 1. What will be produced

Six trees: three built from nothing, and a revision of **each** of them.

| label | what it is | dispatched prompt |
|---|---|---|
| `D` | a **revision of one of the greenfield trees** | `examples/validation/ab/revision/PROMPT.md` |
| `E` | greenfield implementation | one of the three arm prompts |
| `F` | a **revision of one of the greenfield trees** | `examples/validation/ab/revision/PROMPT.md` |
| `M` | a **revision of one of the greenfield trees** | `examples/validation/ab/revision/PROMPT.md` |
| `N` | greenfield implementation | one of the three arm prompts |
| `Z` | greenfield implementation | one of the three arm prompts |

Labels are listed **alphabetically**, which carries no information. They were
drawn from the pool of labels no round has ever published
(`score_tools.py`'s `LABEL_POOL` minus `used_labels()`), by a seeded draw whose
seed and whose label→arm mapping live in `UNBLINDING-rd06.md` — a file no judge
is given. Publishing the seed here would make the blinding decorative.

Which tree each revision is a revision of **is published** (see
`SUBJECTS-RD-06.md` after production): a judge cannot award D2 anchor 3 without
being told the pair. Which *arm* produced a given before is not published.
**Every** greenfield tree is revised, so the pairing reveals nothing about which
arm any tree came from — an arm left unrevised would have been identifiable by
subtraction, which is why the sealed design revises all three rather than a
chosen subset.

## 2. Comparability with the sealed record — what is held identical

The point of this round is that it is comparable to what exists, not that it is
a new experiment. Held identical to the `hexagonal-prompting`,
`hexagonal-prompting-rerun` and `ports-as-adapters` rounds:

- the same sealed **`examples/validation/ab/FEATURE.md`**, unchanged;
- the same shared behavioural suite **`examples/validation/ab/tests/test_behavior.py`**, unchanged and un-editable by any arm;
- the same three **arm prompt sources**, `arm_a/PROMPT.md`, `arm_b/PROMPT.md`, `arm_c/PROMPT.md`, unchanged;
- the same seeded catalogue, `seeded_faults.toml`, unchanged;
- the same example name, `ab_quota_ledger`.

**What is NOT identical, stated rather than buried:**

- the **model** is a different one from the model that wrote the sealed arms.
  Every cross-round comparison of these subjects is therefore confounded by the
  producing model, and no number here separates prompt from model. `R-H1`'s
  "unchanged instrument" clause is about the *card*; this is a fourth axis and
  it is not one this ticket can close.
- the **dispatch envelope** differs from the sealed rounds'. Every arm receives
  the same envelope — an opaque working directory, a repository root, a run
  hint, and one extra do-not-open line — and the exact bytes of each dispatch
  are preserved by `dispatch_record.py` with `provenance = "preserved"`. The
  envelope is **byte-identical across the three arms except for the working
  directory's opaque label**, so it cannot move an arm-to-arm comparison.
  `PA-06-DF-10` is why this paragraph exists: the previous round's headline
  length figure was measured on a file the arm never received, and two of the
  four unrecorded additions named the epic to the arm whose entire job was
  architectural silence.

## 3. The before/after, and the choice made before any code existed

D2 anchor 3 requires *"a simplification was made and its effect measured — the
before and after figures are both recorded"*. No greenfield artifact can reach
it. Which trees get a revision is decided here, sealed, with nothing produced
yet:

> **The revision pass is dispatched at ALL THREE greenfield trees — the control
> arm, the treatment arm and the length-matched control. Not at a subset, and
> not at one chosen after the trees exist.**

The reasoning, which is the part that has to be sealed:

- Revising **only** the treatment arm would hand the next round a before/after
  that can only be read as evidence for this epic family's own thesis. A
  simplification found in the arm that received *no* architectural guidance is
  the one this project's charter calls the preferred outcome.
- Revising **only** the control arm would leave the treatment arm's extra
  machinery — a port, a fake, a composition point — untested against a
  simplifier, which is the interesting case and the one a critic would ask for.
- Picking a subset *after* seeing the trees is selection on the outcome, which
  is the defect three of this family's six epics closed on. Dispatching at all
  three removes the choice rather than justifying it.
- A subset would also **break the blinding by subtraction**: with the pairing
  published, an arm nobody revised is the arm identifiable as the one left out.

**The outcome where a reviser changes nothing is a real result and will be
reported as one.** `revision/PROMPT.md` explicitly licenses returning
empty-handed, and `revision/README.md` states that a prompt which cannot come
back empty-handed is a prompt that will always report a simplification. If both
revisers change nothing, this ticket reports that D2 anchor 3 is still not
reachable on the product and says so in those words. **No further revision will
be dispatched to obtain a better before/after**, and no reviser will be re-run.

## 4. The declared `effect_boundary`, declared before it is derived

`references/architecture_tags.md` §3.3 and the epic charter §5 guard 1: *a tag
asserted after the numbers are seen is not a tag.* The **declaration** below is
this ticket's prior, written before any tree exists. The **derivation** is
RD-05's shipped predicate, run afterwards over the produced trees. Where the two
disagree the result is `TAG-DISPUTED`, it **fails open**, it is reported, and it
is never corrected in either direction.

| what the tree is | declared `effect_boundary` | on what basis |
|---|---|---|
| greenfield, `arm_a` | `effectful` | the sealed `arm_a` subject declares `effectful` |
| greenfield, `arm_b` | `ports-and-adapters` | the sealed `arm_b` subject declares `ports-and-adapters` |
| greenfield, `arm_c` | `effectful` | the sealed `arm_c` subject declares `effectful` |
| revision of the `arm_a` tree | `effectful` | the revision prompt forbids restructuring into a different architecture |
| revision of the `arm_b` tree | `ports-and-adapters` | same |
| revision of the `arm_c` tree | `effectful` | same |

These are priors from the record, not predictions this ticket has any stake in.
A derivation that refuses to derive at all (`UNDERIVABLE:<reason>`) carries no
refusal authority, is always comparable, and **is not a defect** — it is one of
the two ways the tag says nothing.

## 5. What will be measured, and by what

Measured, recorded, **not scored**:

- `examples/validation/ab/tests/test_behavior.py` pass/fail per tree, with the
  tree named — for the revision pairs, run on the before **and** the after, so
  behaviour preservation is checkable by someone who is not this ticket;
- `scripts/code_complexity.py --json` per tree, stored per tree. **Two tables,
  never a delta.** `MF-020`: a figure falling is not evidence the design
  improved, and the instrument ships with no comparison mode for that reason;
- the derived `effect_boundary` per tree, from RD-05's shipped predicate, with
  the clause facts that produced it;
- `dispatch_record.py verify` over the round's dispatch directory;
- `check_catalogue.py --arms --dispatch-dir` — the arm length figures measured
  on **what was sent**.

Not measured here and left to RD-03: anything that assigns a number to the
quality of an artifact.

## 6. What this ticket will report as REJECTED

Sealed now so it cannot be assembled afterwards to look thorough:

- **Using a sealed tree (`blind/artifact_T`, `_U`, `_W`) as the "before".** It
  would have been cheaper and the before would already carry judged cards. It is
  rejected because the before and the after would then have different
  provenance — a different epic's dispatch, a different model, a different
  envelope — and a pair whose two halves were produced under different
  conditions is not a controlled pair. It is exactly the sideways move the
  `ports-as-adapters` packet made when it read a before/after across three arms.
- **Writing the revision prompt to ask for a specific simplification.** It would
  have raised the chance that anchor 3 is reachable. It is rejected because the
  resulting before/after would measure the ask, not the code.
- **Producing only the treatment arm.** Cheapest route to a flattering
  comparison; refused for the reason in §3.

---

*Sealed by RD-06 before dispatch. Nothing in this file is edited afterwards; a
correction goes in `SUBJECTS-RD-06.md` with the original left standing.*
