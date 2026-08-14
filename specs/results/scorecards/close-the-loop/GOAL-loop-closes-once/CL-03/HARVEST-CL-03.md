# The judges' notes, swept — seven epics, 83 cards, and what was in them

**`RM-05-DF-05` ended with a rule: *"sweep your own judges' `notes` and
`judging_practice.what_was_run` for defects in the artifact and FILE them."*
This is the first time that sweep has been run. It is run over the whole sealed
record, not over one round.**

## Method, and its bound

The corpus is every `scorecard.json` under `specs/results/scorecards/` —
**83 cards, 391 dimension rationales, 389 `refuses_to_claim` fields, 52
`judging_practice.what_was_run` entries, 8 `notes` blocks, 83 verdicts,
800,181 characters of judge prose.** It was split by epic into four slices and
each slice was read **in full** by a separate agent that had not seen the others
and was given no hypothesis beyond *"find every statement in which a judge
asserts something is wrong, missing, unverified, vacuous or false about the
artifact, the fixture, the suite, the tooling or the instrument."*

**The bound on this sweep, stated first.** The harvesters were asked for defect
claims and they returned defect claims. **Nothing below is verified by this
ticket** except the four items marked **[RUN]**, which CL-03 or its own judges
executed. A judge's sentence is an observation, not a finding, until somebody
reproduces it — and the point of this document is that for seven epics nobody
tried either way.

## The headline, and it is a channel result

**Every one of the classes below was written into a sealed card by a judge who
was paid to look. Across seven epics, the number of them that became an entry in
`deferred_findings.yaml` is approximately one — `RM-05-DF-05`, filed by the
round that was measuring the record rather than producing it.**

The strongest signal in the corpus is not any single defect. It is that **the
same defects were rediscovered independently, by different judges, in different
epics, under different card versions, up to six times each** — which is what a
finding looks like when nothing downstream consumes it.

| class | independent judge passes that found it |
|---|---|
| the positive control `M07` is red / not green while its columns are read as measurements | **6** |
| `corpus-port-swap:fake` re-runs the REAL implementation when no second one is shipped | **5** |
| the D3 ladder has no rung for the subject being scored | **5** |
| the real journal adapter's persistence is asserted by no test | **4** *(+2 in CL-03's own round)* |
| the 400-step "independent model" sweep accepts ~5 of 400 and its anti-vacuity guard passes anyway | **4** |
| the SM-05 removal broke its own model-derived measurement (`apply_wiring` ImportError, all four corpus columns `CONTROL_RED`) | **4** |
| non-integer / bool amounts reach the durable ledger, refused by nothing | **4+** |
| the shared 28-case suite is green on refusal-precedence, id-reuse and ordering faults | **24 cards — every card of one epic** |
| D2's anchor 3 is unreachable for the subject | **effectively every card in three epics** |

---

## A. The durable record — the class this ticket carried through the loop

**A1. The real adapter's one distinguishing property is observed by nothing.**
**[RUN]** — reproduced by CL-03 and independently by two of its four judges.
Found before this round by **four** judges across three artifacts:
`portable-substrate-rm04-GG/…-p1` (`claude-opus-4`, seeded `JF-4` and read the
file out of band: *"the port reporting `['COMMIT acme 3 3']` while the ledger
file on disk was empty … a 'real' adapter that is secretly a second fake passes
as the real one"*), `portable-substrate/RM-03-rescore/v4/…-T-p1`
(*"the shared suite therefore preserves nothing about the file on disk"*),
`subtract-to-measure-sm05-greenfield/…-S-p1` (fault `F6`),
`subtract-to-measure-sm04-rescore-v3/…-R-p1` (fault `J10`, *"SURVIVED both"*).
**Filed once, as `RM-05-DF-05`. Carried into a card iteration by nobody, which
is what CL-03 exists to change.**

**A2. The in-memory fake is not a faithful double, and the parity cases were
chosen where it agrees.** `hexagonal-prompting-rerun/…-Q-p2`: *"for
`append('A\nB')` the file adapter returns `['A','B']` and the fake `['A\nB']`,
and for `append('')` the file adapter returns `[]` and the fake `['']`. The
chosen contract cases happen to be ones both satisfy."* Reproduced in CL-03's
own round on the shipped fixture: a tenant name containing a newline makes
`FileJournal` report **two** ledger lines where `InMemoryJournal` reports one,
so *"the same cases pass against both"* speaks only for the region where the two
agree. **[RUN]**

**A3. `M09` — a fault seeded in the REAL adapter is invisible through the fake.**
`falsifiable-instruments-rescore-v1/…-T-p1,p2`, `-v2/…-T-p1,p2`,
`ports-as-adapters/…-T-p1`. Two judges used the identical cell for opposite
purposes — proof the binding is real, and a limit on how far the fake
substitutes — and neither reading was ever filed.

**A4. `corpus-port-swap:fake` silently runs the real implementation** when the
tree ships only one, so both columns are identical on all eleven mutants and
constitute no evidence of a fake at all. Five judges:
`sm04-rescore-v2/…-H-p1,p2`, `sm04-rescore-v3/…-R-p1,p2`,
`sm05-greenfield/…-S-p3`, plus the `falsifiable-instruments` and
`ports-as-adapters` rounds. **A swap instrument that degrades to running one
implementation twice and still emits two populated columns.**

**A5. R2 is not enforced under a failing durable append.** Two judges injected a
raising journal and got `committed('acme') == 3` against an empty ledger
(`hexagonal-prompting-rerun/…-Q-p1,p2`); five more name it on `artifact_T`.
Memory is mutated before the durable write, no rollback, no write-ahead
ordering, **and no case covers it**.

**A6. The port abstracts destination only.** The domain renders the finished
line, the port carries a bare `str`, so no adapter substitution can vary the
record format (`hp06-X-p2`, `rerun-Q-p1`, `v2-T-p2`).

**A7. `ex4`'s generated `LedgerStorePort` fake raises `NotImplementedError` and
the conformance function that would compare it against the real adapter is
invoked nowhere.** Both `ex4` judges, independently, plus
`portable-substrate-rm04-GG/…-p2`.

---

## B. Checks that cannot fail

**B1. The shared 28-case behavioural contract — *"the floor of done"* — is green
on real bugs.** All 24 `reading-discipline` cards, both judge models, every arm.
It never collides two rejection clauses in one call, never allocates past `r3`,
and never reads the ledger file. Judges seeded 13, 12, 10, 9, 5, 4 and 3 faults
respectively and reproduced the blindness every time.

**B2. The 400-step "randomized model-based sweep" accepts about 5 of 400
commands, closes all tenants by step 30, and never once accepts a release** —
and its own anti-degeneracy guard passes on that run. Four independent
instrumentations, two epics, identical numbers. Consequence: two deliberate
release faults survive the artifact's entire suite.

**B3. `test_ledger.py:181` asserts a substring that cannot occur.** Two judge
models independently verified that neither `file_journal` nor `memory_journal`
contains `journal_` — so the domain/adapter import boundary is pinned by
nothing. **And two other cards credit that same assertion at D3.**

**B4. Vacuous or unobservable tests, each proved by deletion or by mutation:**
the blank-line filter in `FileJournal.lines()` (dead — `str.splitlines()` emits
no trailing empty element, and the justification in two documents is factually
wrong); `domain.py:108`'s sort (insertion order never diverges from numeric id
order across 400 randomized operations); `test_a_bad_amount_beats_quota_exceeded`
(its two clauses can never both hold); `_Tenant.quota` (deleted in a scratch copy
— 28 and 21 passed unchanged); `test_extra.py:108-114` (*"trivially true since
an unknown tenant can hold no reservations"*).

**B5. `mutation_check.py` reports every mutant caught when pytest is missing**,
because the harness reads any nonzero exit as a kill — a perfect 12/12 table on a
broken environment. Its shared-suite column additionally prints `n/a` from every
location the script can actually be run from.

**B6. `W`'s only raw-bytes durability assertion commits once, so amount and
running total are the same number and a transposition is invisible.** Two judges
mutated two different lines and got eleven green.

---

## C. Gates that report clean on broken input

**C1. A 41-line re-export flips `divergent` to `coherent`** with every
declaration digest unchanged, the behavioural suite green, and the coupling
proven still live at runtime by object identity. Two judges, a blind agent, and
the scorer.

**C2. `consumable_as_architecture` is true for any declared partition**,
including one failing all three decomposition criteria; a declared one-component
partition converts the headline refusal into a clean.

**C3. `ex4`'s `coherent` verdict flips to `unmappable` when the generated
package moves up one directory, with zero bytes of Python changed** — and the
ANSWER KEY still presents `coherent` as ground truth.

**C4. Eight of ten `--out` write sites bypass the path guard.** `spec_paths.py:69`
claims the port targets are enforced *"in one place, so the declaration in
`spec_manifest.yaml` is true of every caller."* It is true of two callers. The
judge seeded the fault and it landed: a write outside every declared port target
exited 0. **[RUN by the judge]**

**C5. `price_removal.price()` returns `PRICED` over a column that provably did
not run**, and `altered_score_probe.problems()` ignores the exit code so a check
that dies with a traceback prints `UNCAUGHT`. Both limits are written into the
files and neither is enforced. **[RUN by the judge]** *(CL-02 owns this surface;
recorded here, not touched.)*

**C6. The invariant-coverage check counts a `TypeOK` type conjunct as a semantic
read**, so write-only variables show clean coverage. Two fixtures, two judges.

**C7. The rejection vocabulary is enforced only by an `assert`** — under
`python -O` `Result.rejected()` mints any string. Two judges, two artifacts, both
executed it; one notes it is predicted nowhere.

---

## D. Numbers that do not mean what they appear to mean

**D1. The positive control `M07` is `green: false` with `deciding: []` while its
columns each executed 294 accepting `Reserve` cases** — so every `SURVIVED` cell
is a floor, not a measurement. Six judges, three epics, every pass.

**D2. `"-225 lines"` is true of one file and false of the repository:** the same
change is **+1677** `code_lines` summed across the three trees, and the busiest
callable got denser. Two judges, two models.

**D3. `internal_import_edges: 0` reads as maximal decoupling because there is
exactly one module.** `mechanical.json`'s import-edge block additionally asserts
edges that do not exist in the tree, in both directions.

**D4. The complexity descriptor cannot see the change it exists to measure** —
it counts `self.*` attributes and not dataclass fields, and on one arm
`branch_points` moves the **wrong way** across the simplification. Eight
independent statements, two models, two arms.

**D5. Identical before/after complexity tables on a byte-identical tree are the
arithmetic consequence of an empty diff, not a measured null.** Four cards.

**D6. A kill cell is almost certainly flake counted as a kill** — the same mutant
reads `SURVIVES` in a sibling run.

**D7. The model-derived corpora are byte-identical across all three artifacts**,
so any difference between artifact columns is a difference in the code's
observability and never in that artifact's own checking. Four judges.

---

## E. Documentation asserting what the code does not do

**E1. *"`_append` is the only code that writes to the file."*** The constructor
truncates the same path outside it — **the one write the claim exists to make
checkable is the single most destructive write in the program.** Two artifact
families, two judge models.

**E2. `NOTES.md` says 37 tests in a tree that has 39;** another ships a
`NOTES.md` it has itself declared factually wrong, whose staleness disclosure
**under-counts** (*"one place"*, against at least three, one being a run command
pointing at another tree).

**E3. *"The 0/9 era is measurably over"*** — a class claim from one seeded fault
of one class on one 84-line program, contradicted by the epic's own round-2 data.
Two judges.

**E4. `README.md:102` states greedy modularity clusters `queue` with `ingest`;**
the judge re-ran the descriptor and it clusters with `dispatch`.

**E5. `ex4`'s README promises failed items reach the ledger; the model makes it
impossible, the invariant is weak enough to pass vacuously on the half that
matters, and a shipped test asserts the negation of the README sentence.**

---

## F. The instrument, about itself

**F1. `DIMS` and the judge-tier derivation are duplicated between two modules
that already import each other, AND THE TWO COPIES HAVE ALREADY DIVERGED** —
`score_tools.py` derives three tiers and returns `None` on ambiguity;
`architecture_tags.py:274` derives two inline and `?` otherwise, with its
`tiers_measured` loop hardcoded to `(opus, sonnet)`. **[RUN — confirmed still
true at `10cf11a`; CL-03 keyed `score_tools`'s split on the full model id and
left the second derivation alone, so the divergence is now WIDER.]**

**F2. The harness does not practise what it enforces.** `architecture_tags.py`
names its instrument as a path constant and shells out to it in the same module
that computes the tag, and reads every card off disk in the function that builds
the rows it computes over. Two judges, two scopes.

**F3. Blinding leaked, five different ways:** a card's own `subject` named the
arm before scoring; `subjects.toml` declares the scored scope's effect boundary
**and** predicts its D2 bound, inside the scope being scored; an arm name sat in
a test docstring; a concurrent process wrote a mutation script into the shared
scratchpad and a judge read it; `git status` printed sibling card path names.
**CL-03's own round adds a sixth: the fixture's docstrings quote the predecessor
finding `BA-B14` including the phrase "the fake that earned arm B its D3 = 4",
so the packet hands a judge a prior D3 number before it forms its own.** Both v4
judges disclosed it unprompted.

**F4. The D3 ladder has no rung for the subject.** *"Between anchors 2 and 3 the
ladder silently changes what 'the domain' refers to."* No rung for a measuring
instrument, for a subtraction, or for an artifact that names no boundary at all
— anchor 0 requires *"state written from everywhere"* (false) and anchor 1
requires *"boundaries named in prose"* (absent), so judges score a ladder
position rather than an anchor and say so. Five passes, three epics.

**F5. D2's anchor 3 pays for motion.** *"The correct decision scores 2, and an
author who had deleted the redundant sort purely to have something to report
would have scored 3."* Named by the judge as an **anchor** defect, with the
action item *"fix the anchor, not the artifact."*

**F6. Two judges of the same artifact made mutually contradictory FACTUAL
claims** — whether a boundary is named in prose at all — from the same permitted
read list, five cards, two points apart.

---

## What this document is not

It is not a fix list and it is not a promotion gate. Nothing here is repaired by
CL-03; the five entries filed as `CL-03-DF-01 … 05` in
`specs/desired_program_model/deferred_findings.yaml` name the classes this round
is willing to stand behind, and this register is the evidence under them.

**The rule that produced it stands and is now demonstrated rather than asserted:
a finding written into a card note is a finding nobody carries forward, and the
carrying is a separate act that has to be funded.**

---

# ADDENDUM — `CA-05`, 2026-08-13: the register was not being kept

**Everything above this line is `CL-03`'s and is not edited.** This section
appends; it corrects no sentence of the sweep.

## Why an addendum was needed

`CL-03` swept **83 cards on 2026-08-11** and named 38 classes. The register was
then **untouched for a whole epic**, while `SV-01-DF-05` filed three new defect
classes into `deferred_findings.yaml` and **not into this file**. So `38`
stopped growing on 2026-08-11, and every *"1 in 38"* quoted since was measured
against a register nobody maintained.

## G. Classes filed to the ledger and never swept in — `SV-01-DF-05`

Found by four blind judges scoring `artifact_under_score` in `SV-01`'s round.
All four judges declined to move a score on any of them and said why; **the code
is correct on all three and the gap is in the cases.** Sealed evidence: the four
`N-D1` blocks in `score-drives-validation-sv01-v4/` and `-sv01-v5/`.

**G1. Rejection precedence is pinned by no case, and it is the requirement the
specification was most emphatic about.** `FEATURE.md` fixes the order of
`reserve`'s rejections in a numbered list — the only thing it numbers — and the
artifact implements it correctly. Swapping `tenant_closed` and
`amount_not_positive` at `quota_ledger/domain.py:139-142` leaves **53/53 and
28/28 green**, because no case anywhere constructs an input where two rejection
conditions hold at once. **Found independently by all four judges.** One:
*"the requirement the spec was most emphatic about is the one nothing pins."*
*(Related to `B1`, which records the 28-case contract as green on
refusal-precedence faults; `G1` is the same blindness located in the artifact's
own suite as well, and pinned to a numbered requirement.)*

**G2. The shipped composition root is exercised by no case.** The artifact's own
suite never constructs `QuotaLedger` and the shared suite never looks at the
path it is handed, so rewiring `quota_ledger/__init__.py:39` to an
`InMemoryJournal` — after which **the shipped program writes no durable file at
all** — passes both suites. Two judges; both considered it grounds for `D3 = 3`
and both routed it to `N-D1` instead, on the ground that it is a hole in the
cases rather than in the design.

**G3. The one case that reads bytes off disk cannot see a line-ending fault.**
`tests/test_ledger.py:247` compares through `Path.read_text()`, which silently
normalises CRLF, so **the single independent observer of the durable effect is
blind to the framing the adapter is responsible for.** One judge. **This is the
very line `SV-01`'s verdict rests on**, and `SV-01` filed it rather than
softening it.

*(Carried in `SV-01-DF-05` and not promoted to a class here: closing tenant A
while tenant B holds a live reservation is tested nowhere. It is a single
missing case, not a class.)*

## The true denominator

<!-- HARVEST-DENOMINATOR-START -->
| | classes |
|---|---|
| `CL-03`'s sweep, 2026-08-11 | 38 (A1–A7, B1–B6, C1–C7, D1–D7, E1–E5, F1–F6) |
| appended by `CA-05` from `SV-01-DF-05` | 3 (G1–G3) |
| **register total** | **41** |

**Per `denominator_rule` — which half moved:**

> **The denominator rose, 38 → 41. The numerator did not move.**
>
> - **consumed into program validation: 1 of 38 (2.6%) → 1 of 41 (2.4%)** — still
>   `A1`, by `SV-04`, and no second class has been consumed since.
> - **named by a ledger row: 4 of 38 → 4 of 41** — `A1`, `E1`, `F3`, `F6`.
>
> **No consumption was lost and nothing regressed.** The rate fell because the
> register was repaired, and a rate that falls on a bookkeeping repair was
> always overstated.
<!-- HARVEST-DENOMINATOR-END -->

**41 is a floor, not a recount.** `CL-03` swept **83** cards; the tree now holds
**95**. **Twelve cards have been sealed since and nobody has swept them.** 41 is
what one bounded, reproducible repair yields — not what re-running `CL-03`'s
method over 95 cards would yield. **Quoting 41 as "the number of known classes"
is the same error quoting 38 was**, and the only honest fix is to run the sweep
again, which `CA-05` did not do and does not claim to have done.

## Read the numerator honestly

Four classes are named by a ledger row. **Three of the four are this project
catching *itself* committing the class, not consuming it:**

| class | the ledger row | what actually happened |
|---|---|---|
| `A1` | `SV-04` | **CONSUMED** — carried into program validation, control 3,3 vs treatment 4,4 |
| `E1` | `SV-04-DF-01` | **COMMITTED** — the file written to consume `A1` asserted in its own docstring what its code did not do, and a judge caught it in the same round |
| `F3` | `SV-04-DF-02`, `CL-04-DF-05`, `SV-04-DF-05` | **COMMITTED** — a blinding leak, this time located in the instrument itself |
| `F6` | `SV-04-DF-04` | **COMMITTED** — a round's own two judges made mutually contradictory factual claims |

**One class in 41 has been consumed. Three more were re-committed by the
programme that named them.** A table that reports *"4 of 38 named"* without that
sentence overstates the loop by a factor of four.

*(Disclosed for completeness: `SV-04-DF-05` also names the whole `C` section —
*"gates that report clean on broken input"* — inside the scoring toolchain. That
is a reference at section granularity, not to any of `C1`–`C7`, so it does not
move the count of 4. Recorded rather than counted.)*

## An internal inconsistency in the sweep, recorded and not repaired

The method paragraph says *"the four items marked **[RUN]**"*. The file carries
**five** run markers: `A1`, `A2` and `F1` as `[RUN]`, and `C4` and `C5` as
`[RUN by the judge]`. **Not repaired here** — `CL-03`'s text is sealed and the
discrepancy is one sentence against five markers, which a reader can resolve.
Recorded so the next person does not have to rediscover it.

## How to keep this register

**`references/consumption.md` carries the requirement.** The short version: a
finding that names a defect *class* belongs in **both** the ledger and this
register, and the epic that files it appends it here **before it closes**.
`SV-01-DF-05` did the first half and not the second, which is the entire reason
this addendum exists.
