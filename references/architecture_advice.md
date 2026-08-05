# Architecture Advice

*Everything three epics of static architecture checking actually established,
written down as instructions an agent can follow today and as a specification
any future architecture tool must satisfy before it is allowed to say anything
binding.*

This page replaces `references/architecture_coherence.md` and the two commands
it documented. On 2026-08-04, by owner direction, `tla-spec-dev analyze
architecture` was removed along with `scripts/analyze_architecture.py` (1,192
lines) and `scripts/architecture_reflexion.py` (2,325). The scanners were ad
hoc. If a static architecture check is ever built here again it must be
architected deliberately, and the way to make that possible is to write down
what it should do rather than leave 3,500 lines of the wrong thing standing.

**Nothing was removed because it was ineffective at catching bugs and might
have improved.** It was removed because each check was measured, each was
defeated cheaply, and the aggregate never moved a single number:

> Every mechanical gate this project shipped was defeated cheaply and none of
> them ever caught a bug. The complexity gate failed every normal program and
> was retired to advisory. The architecture check reported a clean on a
> divergent codebase for **six lines of YAML** in round 1, and for a **41-line
> re-export file** in round 2, with every declaration digest unchanged. Across
> two full eval rounds and seven repair tickets, **bug detection did not move
> by a single cell**: 4 of 6, 6 of 6, 0 of 3, 0 of 3, before and after.
> — `references/eval_scorecard.md`

That is why guidance goes in prompts and verdicts come from judged scorecards.
Two eval rounds (EV-02, 2026-07-27, tip `60d4a51`; EV-03, 2026-07-30, tip
`897ea14`) and the repair tickets between them (RP-01..RP-05, RP-07 landed of
RP-01..RP-07 planned) produced exactly one durable class of result: a set of
*facts about what a static architecture check cannot do*. Those facts are below.
Each is measured, each names its evidence, and each is stated twice — once as
what to do now, once as what a tool would have to do to earn back the authority
this one lost.

---

## Reading order

- **Part 1 — Advice you can act on now.** Nine rules, derived from the nine
  measurements. No tool required. This is the part a reviewer, a ticket agent,
  or an implementation brief should be reading.
- **Part 2 — The specification a replacement must meet.** The same nine
  findings, stated as acceptance criteria, with the evidence attached. A tool
  that does not satisfy all of these is a tool that will be gamed within one
  ticket, and we know because this one was.
- **Part 3 — The one doctrine that survived intact.**

Related pages that are still live: `references/architecture_tractability.md`
(the three design moves, "Advisory, Not Blocking", the justification table),
`references/complexity_intuition.md` (how to read a complexity descriptor),
`references/hexagonal_prompting.md` (why architecture guidance is a prompt),
`references/eval_scorecard.md` (how architecture work is actually judged).

---

# Part 1 — Advice you can act on now

## 1. Ask what calls what, not what imports what

An import graph is not a coupling graph, in **both** directions, and the error
is large in both.

When you are asked whether two components are coupled, the question to answer is
whether a change to one can break the other at run time. Read the call sites.
Check whether the object one component holds was constructed by the other.
Check what is passed as an argument. An import list will mislead you two ways:

- **A module can import nothing from a component it is entirely dependent on**,
  because someone put an indirection module in between, or because the
  collaborator arrives as a parameter, or because the type is annotated as a
  string.
- **A module can import a component it has no relationship with**, because
  someone needed a constant, or because the import is unused.

When you write a boundary, say what the boundary *forbids at run time* —
"`ingest` never holds a `Journal`", "`dispatch` receives its ledger as a
constructor argument and never constructs one". Those are checkable by reading
code and are not erased by moving a file.

## 2. A criterion that cannot fail is not a criterion — and neither is one nothing satisfies

Before you accept any threshold, structural or otherwise, ask two questions and
answer both with a measurement:

1. **What real input fails this?** If you cannot name one, the rule is
   decoration. `modularity_q > 0` was the shipped decomposition criterion, and
   the value it clears is *any positive number*.
2. **What real input passes this?** If nothing does, it is not a standard, it is
   an excuse to refuse everything.

And then the third question, which is the one that actually caught this:

3. **What happens to the verdict if I add one variable and tune nothing?** A
   criterion whose answer is "it flips" is measuring size, not structure.

When you must report a structural number, report it against the *published*
threshold for the measure, and if you are not applying that threshold, say the
number is uninterpreted. Do not print Newman's 0.3 next to a rule of `> 0` and
let the reader assume they are related.

## 3. A metric improving is not evidence the design improved

A number can fall because an edge was deleted. Before recording any reduction as
a result:

- Name **what got simpler**, in one sentence, at the level of behaviour.
- Name **how the behaviour survived it**, with the evidence that would have
  caught it if it had not. "Six tests passed" is not that evidence if none of
  the six reads the thing you removed.
- If the reduction came from a deletion, say so in the same sentence as the
  number. A deletion may be exactly right; a deletion presented as a
  simplification is not.

This is MF-020 and it is enforced for the complexity half by the ledger's
transition-diff gate. For the architecture half there is no longer anything
mechanical, so it is on you.

## 4. A declaration drifts from code unless something executes it

Every declaration in this repository — an effect port glob, a component map, a
scope list, a count in a comment — will disagree with the code it describes
within a few tickets unless a test resolves it against the shipped code path.

The test that closes this class is `tests/test_port_declarations.py`, and its
shape is the whole lesson: **it checks each declared glob against paths built by
the SHIPPED builders**, not against paths a test author typed. A rename fails the
test instead of silently orphaning a declaration.

When you write a declaration:

- Make it **falsifiable**. If it accepts every string, it asserts nothing.
- Make something **execute** it against real inputs, not literal counts. Two
  wrong globs shipped inside a change whose only added assertions were the
  numbers `26 -> 28`, which pass whether or not a port is correct.
- **Assert your test found something.** The first version of the test above read
  the wrong key, found zero ports, and reported green — which made it another
  instance of the class it was written to close.

## 5. "Make the check clean" is a standing instruction to duplicate

When any boundary check reports an illegal edge between two components, the
remedies available to whoever must clear it are: duplicate the code across the
boundary, push the dependency up into a caller the check does not look at, or
re-place a module so the edge becomes legal. **All three make the report green.
Only some of them make the design better, and no report says which one happened.**

So:

- Never write "make the coherence check clean" or any equivalent as a task.
  Write what you want to be true of the design, and let a reviewer read the
  diff.
- When reviewing a diff that cleared a structural finding, ask which of the
  three remedies it used. If it duplicated, ask whether the duplication is the
  honest price of a real boundary — sometimes it is — and record that it was
  paid.

## 6. Advice may describe a good boundary; it must not choose one

A tool that picks the boundary makes every edge legal by construction, because
the boundary it will pick is the one the code already has. This is CD-01, and it
was earned: the suggested-move chooser removed under it was confidently wrong on
standard TLA+ — an aliased invariant made it recommend projecting away every
variable.

So an agent producing architecture guidance:

- **states measured facts** — this action writes these variables, this pair has
  no declared port, this action commits in two places at once;
- **states what may not be done** — a list of prohibitions reads as a boundary,
  a list of permissions reads as a summary;
- **does not propose a cut, a refactor, a target shape, or a module move**, even
  when the move is obvious. "This is a fact you should know" and "here is what
  you should do" are different documents, and only the first is falsifiable.

The target shapes in `references/architecture_tractability.md` (functional core
/ imperative shell, single-writer state, explicit commit points, explicit
protocol state) are the **vocabulary the facts are stated in**, not goals to
assign.

## 7. Anything outside the scanned root is free — including the composition root

Any check with a scope has a complement, and the complement is where the
coupling goes. Push cross-component wiring into a root the check does not look
at, and the codebase reads coherent by construction. A dependency-injection-heavy
service passes trivially, because the thing that knows about every component is
the one file nobody scanned.

There is no good answer to this that we found, and pretending otherwise is worse
than saying it:

- Inside a scanned root, the composition root has an edge to everything and
  reports as a violation for doing its only job.
- Outside it, the composition root is invisible and so is everything routed
  through it.

**So: when you assess an architecture, read the wiring first.** The composition
root is the map of what actually depends on what. And when you *state* a scope —
in a scan, in an audit, in a review — state its complement in the same sentence,
because the complement is the finding.

## 8. Direction is part of a boundary

"These two components talk" and "this one may call that one, never the reverse"
are different claims, and only the second is a layering rule. When you declare a
port, declare which way it points, and say what the reverse direction would mean
if it appeared. An undirected boundary cannot see a bad edge sitting inside a
correctly-declared pair, which is the most likely place for one to be.

## 9. Refuse rather than certify what you could not see

This one is Part 3, because it is the only one that survived every round intact.

---

# Part 2 — The specification a replacement must meet

Each item states a **requirement**, the **measurement** that produced it, and
where the evidence lives. A tool that fails any of these has already been built
here and has already been defeated.

## S1. It must reason about calls, not imports

**Requirement.** The dependency edges the tool reports must reflect what one
component can cause another to execute. Static import edges may be an input;
they may not be the definition. A tool that cannot see a collaborator passed as
a parameter, and cannot see through a re-export, is reporting a different graph
than the one that will break.

**Measured, both directions.**

*The false clean.* EV-03, blind run A, 2026-07-30
(`examples/validation/runs/ex5-run4/`). A 24-line lazy re-export module, three
one-line import rewrites and one decorative function-local import — **41 lines
total, none of them in a declared artifact** — took the divergent fixture from
`divergent` to `coherent`: divergences/absences 4/1 → 0/0, `blind_spots: []`,
`basis_limits: []`, `clean_result_supportable: true`, exit 0, and
`architecture_digest` and `map_digest` both byte-identical. The coupling was
still live at run time in the same run: `inbox.format_entry is
journal.format_entry` → `True`, `queue.Journal is journal.Journal` → `True`.

The mechanism was one line. The extractor tested `code_root.parent / name` for
first-partyhood, so a package nested at `generated/pkg` was one directory too
deep and was filed third-party. A second verification isolated it: on the
*coherent* fixture, moving the package up one directory with **zero bytes of
Python changed** flipped `coherent` → `unmappable`. Recorded as
**EV-03-DF-03**, major, in `specs/results/deferred_findings_final.yaml`:

> EVERY divergence on any project is erasable with NO declaration edit, NO map
> edit, NO blind spot and NO basis limit, by re-exporting the offending symbol
> through a first-party package nested more than one directory below the code
> root's parent.

*The false finding.* EV-02, round 1 (`examples/validation/runs/ex5-run1/`). The
seeded `absence` — a declared port with no code edge, reported as dead
architecture — was the pair `dispatch <-> ledger`, which interacted for the
whole run: the driver passed the collaborator in as a **parameter**. Strictly
better decoupling, reported as dead architecture. Round 2 sharpened it: "the
only way to 'realize a port' is to add an import — which means the check's
absence finding systematically pushes code away from dependency inversion and
toward concrete module references", and an **unused** import satisfies it
(tested).

## S2. Every criterion must have a demonstrated failing input and a demonstrated passing input, and must be stable under a size change

**Requirement.** For each criterion the tool applies, ship (a) a real model that
fails it, (b) a real model that passes it, and (c) a demonstration that adding
one unrelated variable to a passing model does not flip the verdict. Publish the
threshold you apply. If you print a conventional threshold you do not apply,
mark the number uninterpreted.

**Measured.** The shipped decomposition rule was:

| criterion | rule |
|---|---|
| `component_count` | `>= 2` |
| `modularity_q` | `> 0` |
| `crossing_action_fraction` | `<= 0.5` |

with Newman's conventional 0.3 "reported next to the score and never applied as
a criterion". RC-01 added **one** variable — `architecture_delta`, written by the
one action that already wrote its neighbour — and the same measurement went from
"does not decompose" to "**the partition is a cut — every criterion above is
met**" at Q = 0.011605. Nothing was tuned. Reproduced by `git stash` of the
`.tla` change alone. Recorded as **RC-01-DF-01**, major:

> The criterion is literally `modularity_q > 0`, ~26x below the Newman threshold
> the tool prints; it is sensitive to model size rather than structure.
> — `specs/results/coverage-audit-arch-coherence-raw/round3/coverage_audit_ledger_input_proposed.yaml`

**And the second component that earned the verdict was the scanner's own
bookkeeping.** Measured on this repository immediately before the removal:

```
C1  complexity_gate, corpus_gate, effect_conformance, kill_test,
    lastCommand, result, setup_phase, spec_root, ticket_state   (9 vars, 17 actions)
C2  architecture_delta, architecture_scan                       (2 vars,  1 action)
    owns (writes confined here): (none)
    internal actions:            (none)
MEASURED RESULT: the partition is a cut -- every criterion above is met.
```

C2 owned nothing and had no internal actions. Two lines further down, the same
report listed `lastCommand` and `result` as single-writer violations **across
that same boundary**. Meanwhile the repository's own hand-written four-component
partition — the one someone actually thought about — measured Q = −0.0228 and
failed. The fragile verdict was the DEFAULT path, taken when nothing is
declared.

Two further calibration points on record: a plain two-component pipeline
measures Q = 0.219 with all three criteria `[OK]` (so the criteria are
satisfiable), and a sweep of 115,975 partitions of this repository's model found
**2** meeting all three shipped criteria, at Q = 0.0029.

*Postscript, measured after the removal:* with the scanner's two variables gone,
this model's emergent partition measures **Q = 0.003** — and would still have
been reported as "every criterion met", at 100× below the printed threshold.

## S3. A number that fell must carry the reason it fell

**Requirement.** Any reported improvement must enumerate the specific things
that disappeared and classify each. A drop the enumeration does not explain is
reported as **unverified**, never as an improvement. This is MF-020, and it must
be applied to whatever quantity the tool reports, not only to state counts.

**Measured.** MF-020 withdrew a projected −13.1% complexity reduction that turned
out to require deleting a legitimate idempotent re-fire transition; the
distinct-state gate was structurally blind to it, because a deleted self-loop
returns to an already-known state. The rule generalises: a divergence count
cannot tell a removed dependency from a deleted file, or from a module that
stopped being mapped and therefore stopped being looked at.

**The best complexity result on record was withheld from a top score by both
judges for exactly this.** `ex3_over_complex`, blind-judged 2026-08-03, bound
8,388,608 → 624, dense rows 3 → 1. Both judges gave D2 = 3, not 4:

> Not 4, and MF-020 is exactly why. Anchor 4 requires the simplification be
> *shown* behavior-preserving. Part (b) is a deleted edge whose preservation
> rests on six hand-written tests that never referenced the deleted variables —
> a check that could not have failed on that change.
> — judge 1

> The deletion also removes two keys from `new_hub()`'s returned dict — a
> public-surface change with no check capable of catching an external reader —
> and run 2 of this same fixture judged the identical deletion a design decision
> and declined it. The record therefore contains two defensible, opposite
> answers to "was this behavior-preserving".
> — judge 2

Across the whole architectural-coherence baseline, **D2 never reached 4**, and
both judges withheld it for the same reason every time.

## S4. Every declaration the tool consumes must be executed against the shipped code path

**Requirement.** If the tool reads a declaration — a glob, a map, a scope — a
test must resolve that declaration against artefacts produced by the shipped
builders, and must assert it found something to check. Literal counts are not
that test.

**Measured: five instances of one class, four consecutive attempts, three
authors, both directions.**

| # | Declaration | Mismatch | Where |
|---|---|---|---|
| 1 | `spec_tree_delete`, `**/specs/**` on `RunEffectConformance` | **NARROWER than behaviour** — the delete runs at an unconstrained `--work-dir` | HP-04's agent; found by MF-026 round 1 (G-1) |
| 2 | the `--no-batch` spawn of `<work_dir>/programs/case_*.py` | **NO declared port at all**, `work_dir` defaults to `tempfile.mkdtemp` — pre-existing, missed by four prior audit rounds | round 1 (G-2) |
| 3 | `case_work_dir_delete`, target `**` | **WIDER than behaviour** — `_target_matches` collapses `**` to `*`, and fnmatch's `*` crosses separators, so it accepts *every string*. No `filesystem.delete` on that action could ever be a gap again | owner, commit `b9836f7`; found in round 2 (F-7) |
| 4 | `case_program_process`, target `*programs/case_*` | **Off by one character** — underscore, while the shipped builder emits `case-<hex>` with a hyphen. Matched nothing, by construction | owner, commit `b9836f7`; found in round 2 (F-8) |
| 5 | `tests/test_port_declarations.py`, first version | **Passed vacuously** — read `effects.ports`, which does not exist (the real path is `effects.components.<Component>.ports`), found zero ports, reported green | owner, commit `e77de36`, self-caught while writing the test for the class |

The closure that introduced #3 and #4 added exactly two test changes: the literal
counts `26 -> 28`. Those pass whether or not a port is correct.

> Round 1 found a declaration narrower than the behaviour. Round 2 found one
> wider than the behaviour and one that misses it by a character. [...] F-9 is
> the fix for the class, and it is cheaper than any of the individual repairs.
> — `specs/results/coverage_audit_report_hexagonal_prompting.md`

**The artifact that closes it** is `tests/test_port_declarations.py`. Read it
before writing any check that consumes a declaration. It runs every declared
port in all three manifest trees against paths built by the shipped builders,
refuses targets that match `/etc/passwd` or `""`, keeps a four-entry allowlist
of ports that are `*` deliberately and on record so a fifth takes a deliberate
edit and a reason — and asserts the port set is non-empty, because a test that
silently finds nothing to test is worse than no test.

## S5. The report must say what the remedy cost

**Requirement.** When a finding is cleared, the tool (or the reviewer, if there
is no tool) must be able to say which of the three remedies was used —
duplicate, push into an unscanned caller, or re-place in the map — and the diff
must be readable as such. A report that scores a duplication as strictly better
without saying it added duplication is training the codebase.

**Measured.** EV-03 blind run A. The agent cleared findings 1 and 2 by copying
the format string `f"[{item}]"` from `pipeline/ledger/journal.py` into a new
module-local `format_item` in `pipeline/ingest/inbox.py`, and then said so
unprompted:

> The check now scores the codebase strictly better. Two copies of a format
> string is the honest cost of a real boundary and I stand by paying it here —
> but note that for *every* unported pair, this tool's only accepted remedies
> are (i) duplicate, (ii) push the dependency into the caller, or (iii) move a
> module in the map. It will always prefer copy-paste to reuse across an
> unported pair, it will never say so, and nothing in the report tells a
> reviewer that the diff which cleared the finding added duplication. On a
> larger codebase, "make the coherence check clean" is a standing instruction to
> duplicate across component boundaries.
> — `examples/validation/runs/ex5-run4/artifacts/BLIND-RUN-A-REPORT.md` §4.5

Round 1 had already measured that deletion and refactoring are
indistinguishable to the check. This is the third remedy, also invisible.

## S6. The tool may not choose the boundary (CD-01)

**Requirement.** The tool measures the partition the project declares, or
reports the one the graph admits and labels it as emergent. It never proposes a
partition, a refactor, a target shape, or a module move. Advice may *describe* a
good boundary; a tool must not *choose* one.

> The descriptor reports dimensions, a state-space bound, an R/W matrix,
> modularity, dense rows. **It proposes nothing and refuses nothing** (CD-01),
> and that is deliberate: a tool that picks the boundary makes every edge legal
> by construction.
> — `PORTS-AS-ADAPTERS-EPIC.md`

**Measured.** CD-01 removed the abstract/decompose/refactor chooser after
validation found `SUGGESTED MOVE: ABSTRACT` telling the user to project away
*every* variable whenever the cfg names a composed or aliased invariant
(`INVARIANT Inv` where `Inv == RealInv`) — a normal pattern the scaffold itself
ships. This is also why Newman's 0.3 is printed and not applied: picking a
threshold to pass or fail models is the same tuned judgment.

## S7. It must state its scope's complement, and it must have a home for the composition root

**Requirement.** The tool reports, in the same breath as any verdict, what its
scope excluded — not as a caveat but as a finding, because the excluded region
is where the coupling will be pushed. And it must answer, before it ships, where
the composition root lives.

**Measured.** Round 1, `examples/validation/runs/ex5-run1/scoring.md`:

> **Anything outside `--code` is free.** Push cross-component wiring into a
> composition root that is not scanned and the codebase reads coherent by
> construction; a DI-heavy service passes trivially. This run **demonstrates it
> in its own fix**: `tests/driver.py` was modified, and `tests/` is outside
> `--code pipeline`, so that edit is invisible to the check that scored the run
> clean.

Round 2 replicated the driver edit and widened the hazard: EV-03-DF-03 reaches
the same result with `--code` **unchanged**, by adding a file.

The composition root had **no legal home in any version of this design**, and
the coherent fixture's own README says so before being asked:

> `tests/driver.py` wires all three components. Inside `--code pipeline` it
> would give its component an edge to all three — including the unported
> `ingest <-> ledger` pair — and the *coherent* fixture would report a
> divergence for a file whose only job is wiring. The fixture answers it the
> only way the shipped tool allows: keep the wiring outside the code root. Real
> projects hit this. Treat "where does the composition root go" as a question
> the reflexion check does not have an answer for.

Both judges credited the fixture for naming what it could not answer. That is
the standard: a replacement must either give the composition root a declared,
exempt-but-**reported** home, or attribute its edges to the components it wires.
Pick one and measure it on a DI-heavy real service, not on a fixture.

## S8. Ports must carry direction

**Requirement.** A port is an ordered pair. `A -> B` and `B -> A` are different
facts and the tool must not collapse them.

**Measured, and this one is pure waste.** The descriptor **already computed**
direction — `crossing_actions[].reads` and `.writes`, per component — serialized
it, and printed it. The reflexion layer then built its port set as

```python
tuple(sorted((id_to_name[p.between[0]], id_to_name[p.between[1]])))
```

and nothing downstream read the directed fields again. Convergence and
divergence were decided purely on the unordered pair. From the blind agent's
report, §4.4:

> The convergence I added prints as `ledger -> dispatch`; had I built it the
> other way (`dispatch` holding a `Journal`) it would print `dispatch ->
> ledger` and score identically. But the model has a direction: `Record(i)`
> *reads* `delivered` and *writes* `ledger`, and the descriptor already computes
> exactly this. The reflexion half throws it away. [...] this one is a bad edge
> hiding inside a **correctly** ported pair.

A layering violation in a correctly-ported pair was invisible, and the data
needed to see it was already in the payload.

## S9. It must refuse

See Part 3. This is the first requirement, not the last one.

---

# Part 3 — The one honest thing the scanners did

**A refusal beats a false clean.** `unmappable` and `unobservable` — "I could not
see the target" reported as its own verdict rather than folded into "clean" or
into "found nothing" — is the single doctrine that survived every round intact,
and whatever replaces this must keep it.

The rule, from `references/eval_scorecard.md`:

> D5 is not a virtue score. It is here because `unobservable` beating a false
> clean (MF-027) is the single doctrine that has survived every round intact,
> and because an artifact that overstates its own reach corrupts every number
> next to it.

The polarity matters and is the part people get wrong. From MF-027's acceptance
evidence:

> Defaulting to "observable" and refusing only on a list of recognised
> non-Python markers would mean every runtime nobody thought to enumerate
> silently reports clean — the exact defect MF-027 closes.

And `unobservable` **dominates**: a diff computed over a target that was never
seen carries no information, so reporting it as `clean` — or even as `gaps` —
asserts something the run has no evidence for.

Applied to structure, this is why a model that does not decompose was reported
as NOT MEASURABLE rather than as a one-component partition with zero
single-writer violations. The latter is a flawless architecture report for a
model that has no architecture, and it is indistinguishable from the real thing.

**This is the only dimension the scanners ever scored a 4 on**, and they scored
it on exactly the two fixtures where they refused: `ex5_pipeline_divergent` 4/4
and `ex6_jenga` 4/4, from both blind judges. Everything else topped out lower.

Concretely, for anything built here next:

1. **Enumerate what you could not see and publish the list**, per run, with
   locations. Every unresolved dynamic edge, every unparsed file, every
   first-party dependency outside the scope, every declaration whose target is
   unfalsifiable.
2. **A non-empty list means the verdict is a refusal**, not a clean with
   caveats.
3. **Findings are still reported under a refusal.** "I could not see all of it"
   and "I saw nothing" are different facts too.
4. **Nothing downgrades a refusal.** No flag, key, annotation, or environment
   variable. Suppression-shaped keys are scanned, reported as ignored, and never
   honored — the shape `scripts/effect_conformance.py` uses, because a silently
   ignored suppression key is nearly as bad as an honored one: the author
   believes the finding was waived.
5. **A verdict computed against a basis that cannot support it is a refusal
   too.** An architecture whose ports permit every pair makes "no divergences"
   true by construction rather than measured, and the word `coherent` may not be
   spent on both.

---

## Where this connects

- **`prompts/implementation_brief.md`** turns the structure of a model into one
  constrained implementation ask for a coding agent that will not open the
  model. It is the main consumer of Part 1: rules 3, 6 and 8 are its Step 4
  boundary, and its non-vacuity gates are rule 2 applied at generation time.
- **`prompts/aspect_decomposition.md`** is the same ask from the user's side —
  enumerate the public surface, name each aspect's Given and what the Given
  asserts is irrelevant.
- **`prompts/hexagonal_implementation.md`** is the architecture lever as a
  prompt rather than as a check, which is the conclusion this whole page argues
  for.
- **`references/architecture_tractability.md`** carries the design doctrine —
  the three moves, the target-shape vocabulary, "Advisory, Not Blocking", and
  the no-degenerate-escapes rules. This page is the measurement half of that
  advice, now that there is no measurement.
- **`references/eval_scorecard.md`** is how architecture work is actually
  decided here: judged scorecards over blind runs, not a green check.

## What is gone, and what would bring it back

Removed 2026-08-04, by owner direction:

| Artifact | Lines |
|---|---|
| `scripts/analyze_architecture.py` | 1,192 |
| `scripts/architecture_reflexion.py` | 2,325 |
| `tests/test_analyze_architecture.py` | 625 |
| `tests/test_architecture_reflexion.py` | 1,918 |
| `specs/*/architecture_components.yaml` | 62 × 3 |
| `specs/*/architecture_map.yaml` | 76 × 3 |
| `tla-spec-dev analyze architecture` | the subcommand |
| model: `architecture_scan`, `architecture_delta`, `AnalyzeArchitecture` | see the tombstone in `specs/*/TlaSpecDevCli.tla` |
| ledger: the `architecture_delta` member | `scripts/complexity_ledger.py` |

`scripts/analyze_complexity.py` and `scripts/fitness_functions.py` are KEPT.
Complexity statistics are the next epic's subject, deliberately.

**The model got smaller, which had never happened here before.** Removing
`architecture_scan` (4-valued) and `architecture_delta` (6-valued) divides the
declared-representation bound by 24: **26,671,680 → 1,111,320**, over 7 of 9
variables instead of 9 of 11. TLC on `MC.cfg` falls with it —
32,122,220 → 13,008,254 generated, 1,292,951 → **563,963** distinct, depth
26 → 25, no error. Every earlier entry in that chain
(`tests/test_analyze_complexity.py`) is a multiplication, each justified by a
real outcome the program produces. This is the first division, and it is
justified the only way a shrink honestly can be: **the program stopped producing
those outcomes.** No invariant was weakened, no guard relaxed, no domain
narrowed, no reachable behaviour quotiented away — two variables and their sole
writer left together. That is the shape a legitimate reduction has, and it is
worth keeping as the reference case, because MF-020 exists precisely because
most reductions do not have it.

A replacement earns its subcommand back by satisfying S1–S9 above, with the
evidence for each in the same form the findings above carry: a measured input
that fails, a measured input that passes, and a demonstration that the verdict
does not move when something irrelevant does.
