# next epic — starter for the next epic owner

You are starting a new epic. The previous one (`architectural-coherence`) was
**measured, not asserted**: EV-01 committed predictions before any dispatch,
EV-02 scored against them, two blind agents who had never seen the predictions
worked on sanitized fixtures, and the answer keys were enumerated by the owner
in advance. Read this before anything.

The rule that produced everything below: **a low or unflattering result is the
preferred outcome.** This epic exists in the shape it does because the
complexity-descriptor epic existed, and that one existed because a validation
agent was told exactly that and then found the suggested moves were confidently
wrong. Keep the standard.

---

## 1. What the last epic learned (do not re-litigate)

`architectural-coherence` shipped four levers: an architecture **descriptor**
(AC-01), a **reflexion check** of code against the model's architecture
(AC-02), an **implementation brief** (AC-03), and an attributable **refactor
delta** (AC-04) — plus case modules (CM-01) and the eval fixtures (EV-01/EV-02).
Every claim below is a measurement with a run record behind it in
`examples/validation/runs/`.

### Survived, and is reliable

- **The divergence check is accurate when its basis is honest.** On the
  enumerated answer key: **precision 1.000, recall 1.000** — all four seeded
  divergences at the exact `file:line`, plus the one absence, plus **zero false
  positives on the coherent twin**. A check that finds divergence everywhere is
  as useless as one that finds it nowhere; this one does neither.
  (`runs/ex5-run1/`)
- **The refusals hold on real targets.** This repository's own model reports one
  component, Q = 0.000, `unmappable`, and single-writer ownership **NOT
  MEASURABLE** rather than "zero violations". The synthetic Jenga reports
  `unmappable` via `unfalsifiable_coherence`. Both exit 0. (`runs/ex6-run1/`)
- **AC-04's delta cannot be gamed, and this was attacked directly.** Against
  the maximal gaming move — collapse the whole partition to one component and
  re-place all eight modules — it reports `direction = unattributable`, names
  every re-placed module, classifies each lost edge `endpoint_reassigned` ("the
  edge did not go away; the boundary it crossed did"), and reports **stable
  basis 0 → 0**. DP-7 predicted the refusal would hold. It holds.
  (`runs/ex5-run2/`)
- **Content-asserting effect providers catch what nothing else catches.**
  Per fault class, per arm, green control both arms:
  **ARM A (corpus alone) 4 of 6; ARM B (corpus + content provider) 6 of 6.**
  The two survivors under ARM A are exactly the two durable-side faults, killed
  under ARM B by `provider_content_assertion` and by nothing else.
  (`runs/ex4-run1/`)
- **Determinism, including the half nobody had tested.** Generation is
  byte-identical (the same `cases.py` sha256 EV-01 recorded, across worktrees,
  output paths, and two Python interpreters five minor versions apart).
  Execution is byte-identical across two independently generated corpora over
  **14 executions including twelve FAILING ones** — a corpus deterministic only
  when it passes is not a deterministic corpus. Seeded failures **replay
  exactly** from the command the runner prints: three faults, both arms, each
  replayed twice, all six reproducing the originating error string.
  (`runs/ex4-run2/`)
- **Case modules generate, and the tool refuses to oversell them.** 14 authored
  lines → 50 cases; 22 authored lines → 6; the view is 330; and `coverage`
  states unprompted, every run, that the union of aspects is not the view.
  (`runs/ex4-run1/`)

### Killed, or badly wounded

- **`coherent` can be obtained on a divergent codebase, for about six lines of
  YAML, and nothing flags it.** Enumerating all 203 set partitions of the
  divergent fixture's variables: 12 report `coherent`, and **all 12 fail the
  model's own decomposition criteria while zero of the 12 honest partitions
  produce a clean.** The criteria are a perfect discriminator and the reflexion
  check does not consult them. Worse, the **fully degenerate case is not
  caught**: a declared ONE-component partition on a codebase with four real
  divergences reports `coherent`, exit 0, `blind_spots: []` — because the
  `unfalsifiable_coherence` guard is written `len(names) >= 2` and excludes the
  one blob it exists for. `divergence_detectable` is computed as `false` and no
  consumer reads it. **EV-02-DF-01.** (`runs/ex5-run2/`, `runs/ex6-run1/`)
- **The mitigation already exists and lives in the wrong artifact.** AC-03's
  `prompts/implementation_brief.md` documents this exact defect by name and adds
  Gate B: `V1` refuses a 1-component declared partition, `V3` degrades on
  `crossing_action_fraction > 0.5`. AC-03 is a **prompt**; AC-02 is a
  **program**. The check a human must remember is enforced; the check a program
  could enforce is not. Part of EV-02-DF-01.
- **The reflexion check measures static import topology, not interaction.**
  Found by the blind agent, verified: the seeded absence proves it from one side
  — `dispatch` and `ledger` interacted the whole time via a parameter, and with
  no import the tool called it dead architecture. In reverse, pass a function as
  an argument or annotate a type as a string and the divergence vanishes while
  the coupling survives. **Nothing in the tool distinguishes a real refactor
  from that dodge.** (`runs/ex5-run1/`)
- **Anything outside `--code` is free.** Push cross-component wiring into an
  unscanned composition root and the codebase reads coherent by construction; a
  DI-heavy service passes trivially. The blind run demonstrated this **in its
  own fix** — it edited `tests/driver.py`, outside the scanned root, invisible
  to the check that then scored it clean. The adjacent tricks *are* guarded
  (unmapped modules force `unmappable`; suppression-shaped map keys are reported
  and never honored). Scoping is not.
- **A generated corpus cannot see guard relaxation, ever.** It replays only
  ENABLED edges, so it contains no rejected inputs: a service that accepts what
  the model forbids passes every case. Compounded by the adapter recovering the
  action argument from the case's after-state — the oracle hands it the
  argument. Found independently by the blind agent (0 of 3 guard mutants) and
  by EV-01 as DF-01. **This is why "4 of 6 beats MF-038's 0 of 9" is an upper
  bound and must never be quoted without it.**
- **Ordering is invisible at every layer.** `ledger` and `queue` are TLA+ sets;
  the code implements them as ordered lists documented "append-only". The
  projector sorts, the adapter uses `frozenset`, the provider compares
  `sorted()`. A ledger that silently reverses is undetectable by any of the
  three. **Modeling gap, not a tool bug — and no case module can fix it.**
- **X-P3 fails.** Six of eight friction items in the blind aspect run were
  documentation insufficiency, not tool defects, and the root of most of them is
  that **every published command path assumes an external view**. An
  internal-only project has no worked example anywhere in the repo.
  **EV-02-DF-05.** And a checked-in case module **cannot be generated from where
  the convention puts it** (TLC cwd, no module search path, exit 150):
  the shipped convention and the shipped tool disagree. **EV-02-DF-02.**
- **"A non-author can write an aspect" holds for SLICES and fails for GIVENS.**
  A slice needs action names; a Given must constrain every variable of the view
  and know every guard. The Given is the form with the **best** measured
  result — see below — so the mechanism with the strongest number is precisely
  the one that cannot be written from outside, and no document says so.
  **EV-02-DF-04.**

### Scored against the committed predictions

| prediction | outcome |
|---|---|
| A1-P1..P7 (kill table, per class per arm) | **all PASS**, every per-fault prediction exact |
| A2-P1..P4 (aspect ratios, runs, limits) | **PASS**; A2-P4's limit confirmed with a sharper mechanism |
| A3-P1..P4 (determinism, replay) | **all PASS**; A3-P3 converted from prediction to measurement |
| AC-P1..P6 (answer keys, refusals, exit 0) | **all PASS** |
| DP-1 (agent redraws the map) | **PASS at n=1** — see the honesty note below |
| DP-2 (`unfalsifiable_coherence` catches the degenerate case) | **MISSED** — it catches the *near*-degenerate case and misses the *fully* degenerate one |
| DP-2b (declared partition failing all criteria reports a real-looking clean) | **CONFIRMED**, and quantified: 12 of 203 |
| DP-3, DP-5, DP-6, DP-7, DP-8 | **PASS** |
| X-P1, X-P2, X-P4 | **PASS** |
| X-P3 (docs suffice) | **FAIL** |

**The DP-1 honesty note.** DP-1 predicted that at least one run would redraw the
map rather than fix the code. One blind run was dispatched; it did not — all
four declarations byte-identical, only production code moved, recall 1.0 on the
answer key, unprompted. That is a real result and it is **n = 1**. DP-1
predicted a rate, and one honest agent is evidence about one agent under one
prompt. Recording it as "DP-1 disproved" would be exactly the overclaim this
epic was built to avoid. Two things must travel with the PASS: **three of the
four divergences were cleared by DELETING dead code, and the metric cannot tell
deletion from refactoring**; and the agent's own report says the cheapest way to
get clean was **editing the model**, which it declined on judgment, not because
anything stopped it.

### The finding worth more than any mechanism this epic shipped

Working from the public README alone, the blind aspect author found that
**the public surface is false of the model**:

```
Fail(i)   ==  i \in delivered  /\  delivered' = delivered \ {i}  /\  failed' = failed \cup {i}
Record(i) ==  i \in delivered  /\  i \notin ledger  /\  ledger' = ledger \cup {i}
```

Once an item fails it leaves `delivered`, so it can **never** reach the ledger —
while the README promises "a failed item is recorded as failed" and "the ledger
records each outcome", and the model's own `LedgerIsDownstream` invariant
reserves room for exactly the behavior the model then makes unreachable.

**No case module could ever catch this.** A case module may not add an action,
and there is no action to enter; a corpus can only test behavior the model has.
**The value came from the human-facing act of authoring the aspect, not from the
cases it generated.**

This is the one result in the epic that no prediction contains and no metric
measures. It is the strongest available argument for the manual-test-starter
path **and its strength is not expressible as a kill rate.** Whatever the next
epic builds, it must not optimize the aspect surface for kills and lose this.

---

## 2. What the next epic should build

Four pieces, in dependency order. Each one is a fix for something above that was
**measured**, not for something that sounds wrong.

### NE-01 — put the basis in the report (fixes EV-02-DF-01)

The highest-severity finding, and the cheapest fix in the epic. Three changes,
all additive, none of which lets the tool choose a boundary (CD-01 removed
that, permanently):

1. **Delete the `len(names) >= 2` clause** in
   `architecture_reflexion.py:921`. A one-component declared partition is the
   *strongest* case of `unfalsifiable_coherence`, not an exception to it.
   `divergence_detectable == false` must force `unmappable` on its own instead
   of being computed, reported in JSON, and ignored by the verdict.
2. **Move AC-03's Gate B from the prompt into the program.** Carry
   `partition.decomposes`, the failed criteria, and the V1/V3 tests into the
   reflexion text report and into `basis.partition_decomposes` in the JSON.
   `coherent` measured against a partition the model does not support is a
   different claim from `coherent` measured against one it does, and the report
   must say which it is.
3. **Do NOT refuse a declared non-decomposing partition.** Carry the fact, not
   the judgment. A project may have good reasons for a boundary the modularity
   metric dislikes; it may not have them silently.

Acceptance: re-run `runs/ex5-run2/artifacts/df02_blast.py`. The 12 false cleans
must become 0 `coherent` — as `unmappable` or as `coherent (basis: does not
decompose)`, the epic's choice, but never as an unqualified clean.

### NE-02 — measure interaction, not imports

The check's accuracy (precision 1.000, recall 1.000) is real **and is entirely
about static import topology**. Three known evasions, all confirmed: pass a
function as an argument; annotate a type as a string; put the wiring outside
`--code`. The next epic should decide, with a measurement and not an argument,
which of these is worth closing:

- **Parameter-passed collaborators.** The seeded absence in the fixture is a
  worked example of the tool being wrong in the *safe* direction (reporting dead
  architecture where a real interaction existed). The unsafe direction is the
  same blindness.
- **The composition root.** The coherent fixture's own README confesses it has
  nowhere to live: inside `--code` it gives its component an edge to everything;
  outside, it is free. **This has no answer today and the next epic must produce
  one** — a declared `composition_root:` exempt from port checks but *reported*,
  or a rule that a root must be mapped and its edges attributed to the
  components it wires. Pick one and measure it on a DI-heavy real service, not
  on a fixture.
- **Deletion vs refactoring.** The metric cannot tell them apart, and the one
  blind run cleared 3 of 4 divergences by deleting. Whether that matters is a
  judgment the epic should make explicitly rather than by omission.

Build the **negative fixture first**: a codebase that is genuinely coupled and
that the current check reports `coherent`. Until that fixture exists, "the check
is accurate" means "accurate on imports."

### NE-03 — the oracle's blind spots, named in the product

Two whole fault classes are invisible **by construction**, and both were found
independently from outside:

- **Guard relaxation.** A generated corpus contains only enabled edges. The fix
  is not more cases; it is a **negative corpus** — the disabled edges at each
  reachable state, asserted to be REJECTED. TLC already knows them. This is the
  single largest available increase in what the corpus can see, and it is a new
  generator mode, not a tuning knob.
- **Ordering.** Sets in the model, lists in the code, `sorted()` at every oracle
  layer. Either the profile grows sequences, or the toolchain **says in the
  descriptor** that a set-typed variable implemented as an ordered collection is
  unobservable. Saying it is cheap and honest; growing the profile is neither.
- **Parameter recovery (EV-01-DF-01).** MF-029 recovers 0 of 5 parameters when
  actions are guarded by set membership — which is the profile's normal shape.
  Until that changes, every kill rate measured with these adapters is an upper
  bound, and the audit document that says otherwise is EV-02-DF-03.

Ship the corpus and the hand-written suite as **complements with a per-class
table**, never as one kill rate. The blind run measured this directly: the
corpus killed a durable-store mutant that every hand-written test missed, and
the hand-written tests killed all three guard mutants the corpus cannot see.

### NE-04 — the aspect surface as a design review, not only a generator

The unplanned results point the same way twice:

- 60 authored lines → 38 cases that killed **exactly** what the 330-case
  whole-view corpus killed. An **8.7× reduction at zero measured loss** on a
  12-mutant catalog. The Given divides and holds.
- The Given cannot be written from outside (EV-02-DF-04), and the act of trying
  to write one is what surfaced the model/README contradiction.

So: state the precondition per form in the docs; give the Given an authoring aid
that prints the pre-state skeleton from the view; make Step 0's provenance
checkable or delete it (an unenforceable rule teaches agents that these rules
are optional — it was violated in the run, with self-disclosure, which is the
best available outcome and is not a control). And **fix EV-02-DF-02 first**: a
checked-in case module that cannot be generated where it is checked in is the
first command a new author runs and the first one that fails.

---

## 3. Do NOT re-litigate

- **Advisory, not blocking.** Nothing in this line of work refuses a close, a
  promotion, or a case generation. Every fixture exits 0, including the
  `divergent` one. Do not propose an architecture gate; the complexity gate
  already failed every normal program and the pivot is settled.
- **No suggested moves (CD-01).** The tool does not propose a cut, a refactor,
  or a module move. EV-02-DF-01's fix is to *carry a fact*, not to pick a
  boundary. A tool that picks the boundary makes every edge legal by
  construction.
- **The map and the partition are DECLARED, never inferred.** This is not a gap;
  it is the design. The gameability that follows is the price, and AC-04's
  attribution refusal is the mitigation that works. Do not "solve" gaming by
  inferring the map.
- **`unmappable` is never downgraded.** No flag, key, annotation, or environment
  variable turns it into `coherent`. Suppression-shaped map keys are reported
  and never honored. Keep it that way.
- **The single-writer violations on the pipeline fixture are CORRECT OUTPUT.**
  `queue` and `delivered`, both written by `Deliver`: the handoff mutates both
  sides in one step, so it is simultaneously the port and the violation. That is
  the atomicity-fidelity signal. A report that names them scores correct; a
  scorer that counts them as false positives has miscalibrated the key.
- **Emergent partitioning is greedy and mostly vacuous on real models** — and
  "neither real model decomposes" was itself overclaiming: exhaustive
  enumeration of all 115,975 partitions of this repo's model finds 2 that meet
  every criterion, at Q = 0.003. The doctrine survives; the wording was
  corrected on the epic branch. Do not re-derive either half.
- **Generation determinism is settled.** Measured four times now across two
  epics, two interpreters, and three output paths, always byte-identical. Keep
  it as a control precisely because it always passes; do not spend a ticket
  re-proving it. The risk was always **execution**, and that half is now
  measured too.
- **MF-038's 0-of-9 is not superseded.** ARM A reproduces it on exactly the
  faults MF-038 was made of. The improvement to 4 of 6 comes from a
  **content-bearing output projection** (MF-038's own first recommendation), and
  the last two kills come from a **content-asserting provider**. Attribute per
  mechanism or the number is uninterpretable.

---

## 4. How to run it

- Branch off the current `epic/architectural-coherence` tip. You inherit the
  four levers, the case-module surface, and the six eval fixtures.
- The five open findings are in
  `specs/desired_program_model/deferred_findings.yaml` as **EV-02-DF-01..05**,
  each with a reproduction command, a suggested fix, and a blast radius. NE-01
  is EV-02-DF-01; NE-04 is EV-02-DF-02 + DF-04; NE-03 touches EV-02-DF-03.
- **Re-score against `examples/validation/PREDICTIONS.md`**, and commit new
  predictions **before** any dispatch. The predictions in that file are what
  made "as expected" a usable phrase in this epic; six of them were wrong, and
  knowing which six is the whole value.
- Run each example at least twice. Every mechanical arm in EV-02 was run twice
  and the divergence was zero; that is a result, and it is only a result because
  it was checked.

### Eval protocol, corrected by this run

- **EV-02-PROTO-01 — redaction that announces itself is a weak blind.** The
  sanitizer left `\* --` comment stubs in the model; the agent noticed and said
  so. Ship a purpose-written neutral fixture variant, not a stripped one.
- **EV-02-PROTO-02 — a blind run's mutant catalog must be an artifact.** The
  aspect run's 12 mutants were applied in place and restored; no catalog
  survives, so its numbers cannot be re-scored. Blind runs that measure kills
  must ship a `seeded_faults.toml`-shaped file the way EV-01 did.
- **Compare the ARCHITECTURE digest, not only the map digest.** DP-1's scoring
  rule was written against the map. The blind run's own report names editing the
  model as the cheapest way to get clean; the model digest is the only thing
  that would catch it.
- **Pin the interpreter.** No `python3` on PATH carries both `yaml` and
  `pytest`, and `python3` under `timeout(1)` resolved to a different interpreter
  than in an interactive shell. State an absolute path in the validation README.

---

## 5. Standing constraints (unchanged, non-negotiable)

- **Never merge to `main`** and **never run `skill-manager sync`** without
  explicit owner say-so.
- **Never invoke `tla-spec-dev` from PATH** — it execs a stale installed clone.
  Use `python3 scripts/tla_spec_dev.py --spec-root specs ...`.
- **Run pytest with `--with pyyaml`** or the YAML-validity guard skips silently.
- **Validate `ticket_plan.yaml` after every edit.**
- The tool serves a **constrained v0 TLA+ profile**, not arbitrary TLA+. Both
  invisible fault classes in §2/NE-03 are properties of that profile, and
  widening it is a decision with a cost, not a bug fix.
- **Findings are FILED, never fixed inline, during a measurement.** A fix during
  measurement destroys the measurement. EV-02 filed five and fixed none.

---

## 6. Epic-owner discipline that paid off, again

Predictions committed before dispatch; answer keys enumerated by the owner and
not by the agent under test; agents never shown the predictions; two arms
declared as two mappings rather than one mapping with its assertions switched
off, so a reader of the record can see which instrument produced a number.

That last one is the reusable trick. **DP-8 — "an EV-02 number reported without
naming its arm is uninterpretable" — is the reason this epic has a 4/6 and a 6/6
instead of a single misleading number**, and the reason the blind aspect run
reported a per-class table instead of "5 of 11". Apply the same split to any
future claim: separate the mechanism you are selling from the mechanism that did
the work, in the artifact, before the measurement runs.

And the standing one: **an epic that closes with only good news about itself has
not been measured.** This one closes with an accuracy result of 1.000 and a
six-line YAML file that makes it say `coherent` on a codebase with four
divergences. Both are true. Ship both.
