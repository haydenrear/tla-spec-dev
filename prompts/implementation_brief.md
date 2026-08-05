# Implementation Brief — sub-agent prompt (AC-03)

**Dispatch this file verbatim as the prompt for a sub-agent.** It renders the
structure of one model into one constrained implementation ask, in the shape of
`templates/implementation_brief.md`. See `references/architecture_advice.md` for
what may and may not be claimed about structure here and why, and
`references/architecture_tractability.md` (Move 3, target shapes) for the
vocabulary; this file is the executable procedure.

**Changed 2026-08-04.** This prompt used to read a JSON payload from
`tla-spec-dev analyze architecture`, which was removed with the static
architecture scanners. You now derive the same facts from `analyze complexity
--format json` plus the module text, and you carry the partition the CALLER
declares. That is more work and it is the honest amount of work: the tool that
used to produce a component partition also chose it, and a tool that picks the
boundary makes every edge legal by construction (CD-01,
`references/architecture_advice.md` S6). Everything below about what you may not
write is unchanged and is the part that mattered.

---

## What you are being asked to produce

Not a design. Not a plan. **A constrained ask** — the difference between

> "implement checkout"

and

> "implement this action inside component C, which owns `orders` and `outbox`,
> reaching the cart component only through its declared port; effects at the
> boundary; one externally visible commitment."

Only the second is derivable from a model, and it is derivable *mechanically*:
every clause of the brief is a field of the descriptor JSON. Your job is the
lookup and the honest header, not the architecture.

The brief's reader is **a coding agent that will not open the model.** That
constrains your output more than it constrains your process:

- **Self-contained.** No "see the descriptor", no "as the spec says". If a
  constraint is not written in the brief, it will not be honored.
- **Names what may NOT be done.** A list of permissions is read as a summary; a
  list of prohibitions is read as a boundary.
- **Short.** A brief a coding agent skims is a brief that changes nothing.
  Section 3 is the load-bearing part and belongs on one screen. Everything you
  add to it costs attention that the constraints were paying for.

---

## Step 0 — Inputs. Two, and you do not choose either.

| Input | Where it comes from | Required |
|---|---|---|
| The complexity JSON | `analyze complexity --format json` | yes |
| The module text | the `.tla` the JSON names, read directly | yes |
| The **partition** — named components, each a set of variables | the CALLER, in writing | yes |
| The subject **action** | the caller — the modeled action this work implements | yes |
| The subject **component** | the caller; defaults per Step 3 | conditional |
| The work description (§1) | the caller, in prose | yes |
| The manifest's `effects:` block | `spec_manifest.yaml` (the JSON names its path) | yes |

```bash
python3 scripts/tla_spec_dev.py --spec-root specs analyze complexity \
  <tla> <cfg> --format json > complexity.json
```

The payload you need is under `.measured`:

| you need | field |
|---|---|
| every action with its read and write set | `.measured.actions[] → {name, reads, writes}` |
| the emergent variable clusters | `.measured.components` (a list of variable lists) |
| the actions that cross those clusters | `.measured.port_crossing_actions` |
| the modularity score of that clustering | `.measured.modularity` |
| variables no invariant reads, and unjustified variables | `.measured.unread_by_invariant`, `.measured.unjustified_variables` |

**YOU DO NOT CHOOSE THE PARTITION AND NEITHER DOES THE TOOL.** `.components` is
the clustering the interaction graph happens to admit — a measurement of the
matrix, never a proposal, and never a boundary anyone committed to. If the
caller has not named components, you have two honest options and no third:

1. Ask the caller to name them, in one sentence per component, and wait.
2. Render from `.components` and mark the brief **DEGRADED**, saying in §6 that
   the partition is emergent, that nobody declared it, and that the emergent
   clusters carry no names a reader can act on.

Re-clustering, re-grouping, or hand-adjusting variables until the numbers
improve is metric-gaming and produces a confident brief about a boundary chosen
for its score. If you believe the declared partition is wrong, that is a
sentence in your report to the owner, not a different partition.

**The model is the only source of structure.** The manifest supplies effects
(§3.3) and nothing else. You may not read the production source to enrich the
brief: a clause sourced from code describes the code, and the whole point is to
constrain code by the model. You may not claim anything about the production
code at all — no tool here compares model to code, and the one that used to was
removed for reporting `coherent` on a divergent codebase after a 41-line diff
(`references/architecture_advice.md` S1).

---

## Step 1 — The non-vacuity precondition. Check it before writing a word.

This is the step that keeps this prompt from producing confident nonsense, and
it exists because of a measurement, not a worry.

**Measured, AC-01, 2026-07-27:** this repository's own model
(`specs/current/TlaSpecDevCli.tla`) emerged as **one component at Q = 0.000** —
`lastCommand` and `result` are written by every command, so the interaction
graph is effectively complete. The shipped worked example
(`examples/distributed_history/.../External.tla`) emerges as two components at
Q = 0.047 with **9 of 12 actions crossing**. A brief rendered from either would
read:

> Component C1. It owns every variable. It reaches nothing. Do not write
> outside it.

Every clause true. Every clause vacuous. And it is **indistinguishable from a
real brief** — same template, same confident voice, same measured provenance.
That is the MF-027 failure mode (a clean report on a target that was never
observed) reproduced at generation time, and it is worse here than in a scan,
because a coding agent will act on it.

**Re-measured 2026-08-04, and the re-measurement is the better lesson.** The
same model now emerges as **two** clusters at Q = 0.003, because two variables
and one action were deleted. Nobody drew a boundary; the emergent number moved
anyway, twice, in both directions, on changes that had nothing to do with
design. Treat `.measured.modularity` and `.measured.components` as facts about
the matrix on the day you ran it, never as an architecture, and never as
something a brief may cite as authority
(`references/architecture_advice.md` S2).

### The two gates

Compute both yourself, from the partition you were given and the action read and
write sets in the JSON. Show your arithmetic in §6.

**Gate A — is there a boundary at all?**

There is a boundary iff the partition has **two or more components** and **at
least one variable is written only by actions that write nothing outside its
own component**. Neither holds → **emit the refusal block from the template and
stop.** Do not render constraints. Do not "render it anyway with a caveat".
There is no component for the work to belong to.

**Gate A is necessary and not sufficient, and you must know why.** A project can
declare `[everything] / [one unused variable]` and clear it. Gate A asks "did
someone name a boundary"; Gate B asks "does this boundary constrain anything",
and only the second is your question.

**Do not import a threshold to settle this.** The removed scanner published
`modularity_q > 0` as its decomposition rule, ~26x below the Newman threshold it
printed on the same page and did not apply, and one added variable flipped this
repository's own verdict to "every criterion met" — on a component consisting of
the scanner's own bookkeeping. If you quote `.measured.modularity` in §6, quote
it as **an uninterpreted number**, say what threshold you are not applying, and
do not let it decide anything. `references/architecture_advice.md` S2.

**Gate B — is the rendered brief worth anything?** Compute these three from the
descriptor and record each in §6:

| test | vacuous when | what it costs the brief |
|---|---|---|
| `V1` | the partition has one component | §2 and §3.2 constrain nothing. **Refuse** — this is Gate A's case reached through a declaration. |
| `V2` | the subject component owns nothing **and** has no internal action (no action whose entire write set falls inside it) | "this work belongs to C" restricts nothing: every action touching C also commits elsewhere. Render **DEGRADED**, and say this in §6 in one sentence. |
| `V3` | more than half the actions write into more than one component | "reach C2 only through this port" names a port most actions already cross. Render **DEGRADED**, and give the fraction as `<n> of <m> actions`. |
| `V4` | the partition is emergent — nobody declared it | the components have no names, so §2 can only say "C1". Render **DEGRADED** and say so. |

`V1` refuses. `V2` and `V3` degrade — they do not refuse, because §3.1
(write set), §3.3 (effects) and §3.4 (commitment) are measured **per action**
and survive a bad partition intact. A DEGRADED brief still carries three real
constraints; a REFUSED one carries none.

**Confidence is not a vibe.** `FULL` iff Gate A holds on a DECLARED partition
and none of `V2`, `V3`, `V4` fires. Otherwise `DEGRADED`, naming every test that
fired. You do not get to round up, and you may not invent a fourth level.

**Confidence describes the partition, not every clause.** A `FULL` brief can
still carry an `UNMAPPED` §3.3, because the effect declaration comes from the
manifest and no partition can supply one the project never wrote. Say so in
§3.3 and again in §6; do not let the banner absorb it.

**One distinction will trip you, and it tripped the tool that used to do this.**
"Owns nothing" and "ownership is not measurable" are different facts, and an
empty list expresses both. With one component every variable is trivially
confined and the honest answer is NOT MEASURABLE, not zero violations — a
flawless architecture report for a model with no architecture is
indistinguishable from the real thing. Gate A catches this case before you can
reach the question, which is exactly why Gate A is a gate and not a caveat.
Whenever you would write `0` or `none`, check whether the true answer is *not
measurable*, and write that instead. `references/architecture_advice.md` Part 3.

---

## Step 2 — Render §2 and §3 by field lookup

Each clause has exactly one source. Copy; do not paraphrase, do not summarize,
do not "clean up" a list.

Write out the derivation for each clause. Let `owner(v)` be the component whose
variable set contains `v`, and for an action `A` let `W(A)` be
`.measured.actions[] | select(.name == A) | .writes` and `R(A)` its `.reads`.

| Brief clause | Derivation |
|---|---|
| §2 component and its variables | the caller's partition, verbatim |
| §2 `owns` | the variables `v` in the component such that **every** action writing `v` writes only inside this component |
| §2 reads / writes, per component | `R(A)` and `W(A)`, each grouped by `owner(·)` |
| §2 internal? | `{owner(w) : w ∈ W(A)}` is exactly this one component |
| §3.1 write set | `W(A)`, split by component |
| §3.2 reach | the components other than this one that `A` writes into, and every action that crosses that same pair — that set of action names IS the port |
| §3.3 effects | manifest `effects.actions.<A>` → `effects.components.*.ports.<port>` |
| §3.4 commitment | `A` spans iff `|{owner(w) : w ∈ W(A)}| > 1` |
| §3.5 coordination | for each crossed pair, `A`'s writes on the far side |
| §3.6 single-writer | variables `A` writes that are also written by an action committing in another component |
| §6 the derivation itself | the arithmetic above, so a reviewer can redo it |

Five of these have a wrong-looking right answer. Get them right:

1. **`owns` is writes-confined, not membership.** A variable can be in the
   component and not owned by it, because some action writes it while also
   writing elsewhere. Never render §3.6 from the variable list.
2. **The port is the set of crossing actions, and it is the *only* port.** §3.2
   is the "through this port only" clause the whole brief is about. Render the
   action names literally. Reaching nothing is the strongest form of the clause
   — say *this action is internal to the component*, not "reaches nothing".
3. **A port has a DIRECTION and you must state it.** "These two components talk"
   and "this one may call that one, never the reverse" are different claims, and
   only the second is a layering rule. Derive it from the reads and writes you
   already have: `A` reading `x` in C1 and writing `y` in C2 is `C1 -> C2`, and
   the reverse edge is a different fact. The removed tool computed this and then
   discarded it into an unordered pair, which made a layering violation inside a
   correctly-ported pair invisible (`references/architecture_advice.md` S8).
   Do not repeat that.
4. **A spanning action is a violation, not a permission.** An action that
   commits in more than one component does so *today*. §3.4 must say the model
   asserts atomicity and the implementation must either honor it or report the
   model wrong. It must **not** say "you may write in both".
5. **An empty `effects.actions.<A>` row is not a missing one.** This
   repository's manifest carries deliberately empty rows and documents the
   distinction: empty claims *performs no distinct effect*, absent claims
   *unmapped*. §3.3 must state which it found. Collapsing them turns "we
   checked, there are none" into "nobody looked".

---

## Step 3 — When the action spans, the caller names the component

If the action spans (§3.4), it commits in more than one
component and **there is no derivable answer to "which component does this work
belong to".** Ask the caller. Do not pick.

Only if the caller will not name one: render the component the action writes
*most* of its variables into, and say in §6, in one sentence, that the subject
component was defaulted and by what rule. A defaulted subject is a fact the
reader is entitled to; guessing silently is how a brief acquires an authority
it did not earn.

---

## Step 4 — What you may not put in the brief

This is the CD-01 boundary and it is absolute.

**Forbidden, in any wording:**

- a proposed cut, refactor, target shape, or "next step";
- "consider extracting…", "this would be cleaner if…", "ideally C2 would own…";
- a threshold, score, or grade you invented (the criteria table is copied, and
  Newman's 0.3 is *reported next to* Q, never applied);
- any constraint not traceable to a named field — including a constraint that
  is obviously good practice;
- a claim about the production code. You did not read it, and since 2026-08-04
  NOTHING in this toolchain compares model to code. The check that did was
  removed after a 41-line re-export file took a divergent codebase to
  `coherent` with the coupling live at run time
  (`references/architecture_advice.md` S1). "The code is coherent with this
  model" is not a sentence you may write;
- a remedy for a structural fact you reported. Clearing a boundary finding is
  reachable by duplicating across the boundary, by pushing the dependency into a
  caller nobody looks at, or by redrawing the boundary — and no report says
  which happened. Telling a coding agent to "make it clean" is a standing
  instruction to duplicate (`references/architecture_advice.md` S5).

Move 3's target shapes — functional core / imperative shell, single-writer
state, explicit commit points, explicit protocol state — are **the vocabulary
the measured facts are stated in**, not goals to assign. §3.3 says *these are
your declared ports*, not *push effects to the edges*. §3.4 says *the model
says these commit together*, not *introduce a commit point*. The difference is
that the first is falsifiable and the second is advice, and this repository
removed its advice-giver on evidence (CD-01: the suggested-move chooser was
confidently wrong on standard TLA+).

**The brief is advisory.** It refuses no merge, gates no promotion, and blocks
no close. It asks the implementer to report a collision rather than hide one.

---

## Step 5 — Self-check before you hand it over

Answer these in your report to the caller, not in the brief:

1. Which clauses did you render, and from which derivation? A clause you cannot
   show the arithmetic for is a clause you wrote.
2. Did any test in Step 1 fire? Which, and is the confidence banner consistent
   with that? (`FULL` with a failing criterion is the single most likely defect
   in this procedure.)
3. Is §3 one screen? If not, what did you add, and what is it worth?
4. Did you read any production source? If yes, name the file and remove what it
   contributed.
5. **Would this brief have been different if the work were "implement
   checkout"?** If the answer is no — if the constraints are so weak the brief
   collapses to the unconstrained ask — say so plainly. That is the finding
   this prompt exists to produce, and it outranks a tidy artifact.

---

## Output

Fill in `templates/implementation_brief.md`. Write it wherever the caller asks;
if it is ticket evidence, write it under the ticket's `results/` directory so
it travels with the ticket into `.history/` at close.

---

## Validation status of this prompt — read before trusting it

**The run below predates the 2026-08-04 rewrite** and was performed against the
descriptor JSON this prompt no longer reads. Its findings about *briefs* still
hold — they are about vacuity and about what a partition can constrain, not
about the tool — but nothing has re-run this procedure in its current form. Read
the table as calibration, not as validation of the steps above.

**Run 1 (AC-03, 2026-07-27).** Four renders, evidence in AC-03's `results/`:

| render | model | partition | outcome |
|---|---|---|---|
| `OpenTicket` | `specs/current/TlaSpecDevCli.tla` | declared | `DEGRADED` (`modularity_q`) |
| `AnalyzeComplexity` | same | declared | `DEGRADED` (`modularity_q`, `V2`) |
| `OpenTicket` | same | emergent | `REFUSED` (Gate A, `V1`) |
| `CreateAccount` | `examples/distributed_history/.../Internal.tla` | emergent | `FULL` |

What that run established, and what it did not:

- **The lookup is mechanical.** Every clause resolved to a named field. No
  clause needed judgment, which is the property that makes the brief checkable
  by a reviewer who did not write it.
- **`FULL` was 1 of 4, and the one was thin.** `Internal.tla` clears
  `modularity_q` by 0.007 and clears `crossing_action_fraction` by exactly
  zero. **Treat `FULL` as rare and near the line until more real models say
  otherwise.**
- **A declared partition earns names; an emergent one does not.** The `FULL`
  brief tells its reader "you are in `C1`". The DEGRADED ones say "you are in
  `workflow`". The second is the more usable instruction, from the worse
  partition — so declaring a partition is worth doing even where the emergent
  one already decomposes.
- **The two DEGRADED briefs are not equally weak.** `V2` fired on one and not
  the other, from the *same* descriptor: whether a brief constrains anything
  depends on which component the work lands in, not only on the partition's
  score. Per-component vacuity is not a refinement of the criteria table; it is
  a separate question, and Step 1 asks it separately for that reason.
- **Known-open, and no wording fixes it:** *nothing measures whether a brief
  changes what a coding agent produces.* This prompt makes the ask derivable
  and falsifiable. Whether a derivable ask yields more coherent code is an
  empirical question, unanswered here, and belongs to the epic's evaluation
  tickets. Until it is answered, a brief is a hypothesis with good provenance —
  not a result.
