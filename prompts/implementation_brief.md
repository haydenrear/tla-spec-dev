# Implementation Brief — sub-agent prompt (AC-03)

**Dispatch this file verbatim as the prompt for a sub-agent.** It renders one
AC-01 architecture descriptor into one constrained implementation ask, in the
shape of `templates/implementation_brief.md`. See
`references/architecture_coherence.md` for what the descriptor measures and
`references/architecture_tractability.md` (Move 3, target shapes) for the
vocabulary; this file is the executable procedure.

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
| The descriptor JSON | `analyze architecture --format json` | yes |
| The subject **action** | the caller — the modeled action this work implements | yes |
| The subject **component** | the caller; defaults per Step 3 | conditional |
| The work description (§1) | the caller, in prose | yes |
| The manifest's `effects:` block | `spec_manifest.yaml` (the descriptor names its path) | yes |

```bash
python3 scripts/tla_spec_dev.py --spec-root specs analyze architecture \
  <tla> <cfg> [--components <partition.yaml>] --format json > descriptor.json
```

**You may not choose the partition to make the brief look better.** The
partition is whatever the project declared, or whatever the interaction graph
emitted. Re-running with a different `--components` file until the criteria
pass is metric-gaming: it produces a confident brief about a boundary chosen
for its score. If you believe the declared partition is wrong, that is a
sentence in your report to the owner, not a second `--components` file.

**The descriptor is the only source of structure.** The manifest supplies
effects (§3.3) and nothing else. You may not read the production source to
enrich the brief: a clause sourced from code describes the code, and the whole
point is to constrain code by the model.

---

## Step 1 — The non-vacuity precondition. Check it before writing a word.

This is the step that keeps this prompt from producing confident nonsense, and
it exists because of a measurement, not a worry.

**Measured, AC-01, 2026-07-27:** this repository's own model
(`specs/current/TlaSpecDevCli.tla`) emerges as **one component at Q = 0.000** —
`lastCommand` and `result` are written by all fifteen commands, so the
interaction graph is effectively complete. The shipped worked example
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

### The two gates

**Gate A — may I render at all?**

```bash
jq '.measured.partition.consumable_as_architecture' descriptor.json
```

`false` → **emit the refusal block from the template and stop.** Do not render
constraints. Do not "render it anyway with a caveat". There is no component for
the work to belong to.

**Gate A is necessary and not sufficient, and you must know why.**
`consumable_as_architecture` is `true` for *any* declared partition, including
one that fails every decomposition criterion —
`scripts/analyze_architecture.py` returns
`partition_source == "declared" or decomposes`. That is correct for AC-02,
whose question is "did the project name a boundary to compare code against".
It is **not** sufficient for you, whose question is "does this boundary
constrain anything". A project can declare `[everything] / [one unused
variable]` and pass Gate A.

**Gate B — is the rendered brief worth anything?** Compute these three from the
descriptor and record each in §6:

| test | vacuous when | what it costs the brief |
|---|---|---|
| `V1` | `components` has length 1 | §2 and §3.2 constrain nothing. **Refuse** — this is Gate A's case reached through a declaration. |
| `V2` | the subject component's `owns` **and** `internal_actions` are both empty | "this work belongs to C" restricts nothing: every action touching C also commits elsewhere. Render **DEGRADED**, and say this in §6 in one sentence. |
| `V3` | `crossing_action_fraction > 0.5` | "reach C2 only through this port" names a port most actions already cross. Render **DEGRADED**, and give the fraction as `<n> of <m> actions`. |

`V1` refuses. `V2` and `V3` degrade — they do not refuse, because §3.1
(write set), §3.3 (effects) and §3.4 (commitment) are measured **per action**
and survive a bad partition intact. A DEGRADED brief still carries three real
constraints; a REFUSED one carries none.

**Confidence is not a vibe.** `FULL` iff all three decomposition criteria are
met and neither `V2` nor `V3` fires. Otherwise `DEGRADED`, naming every test
that fired. You do not get to round up.

**Confidence describes the partition, not every clause.** A `FULL` brief can
still carry an `UNMAPPED` §3.3, because the effect declaration comes from the
manifest and no partition can supply one the project never wrote. Say so in
§3.3 and again in §6; do not let the banner absorb it.

**One field lies about this, and you must not be fooled by it.** For a
single-component partition, `ownership.single_writer_violations` is `null` and
`ownership.single_writer_basis` carries the reason — but
`components[0].owns` is the empty list `[]`, which reads as *owns nothing* when
it means *not measurable*. The text renderer says `NOT MEASURABLE with one
component`; the JSON does not. Gate A catches this case before you can reach
the field, which is exactly why Gate A is a gate and not a caveat.

---

## Step 2 — Render §2 and §3 by field lookup

Each clause has exactly one source. Copy; do not paraphrase, do not summarize,
do not "clean up" a list.

| Brief clause | Descriptor field |
|---|---|
| §2 component, variables, `owns` | `partition.components[] | select(.name == <component>)` |
| §2 reads / writes, per component | `crossing_actions[] | select(.action == <A>)`, else `actions[] | select(.name == <A>)` |
| §2 internal? | `<A> in components[].internal_actions` |
| §3.1 write set | `actions[].writes`, split by component |
| §3.2 reach | `components[].reaches[] → {component, name, via_actions}` |
| §3.3 effects | manifest `effects.actions.<A>` → `effects.components.*.ports.<port>` |
| §3.4 commitment | `spanning_actions[] | select(.action == <A>)` |
| §3.5 coordination | the crossing action's `writes` on the far side of each port |
| §3.6 single-writer | `ownership.single_writer_violations`, filtered to variables this action writes |
| §6 criteria table | `partition.criteria[] → {name, measured, rule, met}` |

Four of these have a wrong-looking right answer. Get them right:

1. **`owns` is writes-confined, not membership.** A variable can be in the
   component and not owned by it, because some action writes it while also
   writing elsewhere. Never render §3.6 from `variables`.
2. **`reaches[].via_actions` is the port, and it is the *only* port.** §3.2 is
   the "through this port only" clause the whole ticket is about. Render the
   action names literally. An empty `reaches` is the strongest form of the
   clause — say *this action is internal to the component*, not "reaches
   nothing".
3. **`spanning_actions` is a violation, not a permission.** An action listed
   there commits in more than one component *today*. §3.4 must say the model
   asserts atomicity and the implementation must either honor it or report the
   model wrong. It must **not** say "you may write in both".
4. **An empty `effects.actions.<A>` row is not a missing one.** This
   repository's manifest carries deliberately empty rows and documents the
   distinction: empty claims *performs no distinct effect*, absent claims
   *unmapped*. §3.3 must state which it found. Collapsing them turns "we
   checked, there are none" into "nobody looked".

---

## Step 3 — When the action spans, the caller names the component

If the action appears in `spanning_actions`, it commits in more than one
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
- a claim about the production code. You did not read it. AC-02's reflexion
  check is the only thing that compares model to code.

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

1. Which clauses did you render, and from which `jq` expression? A clause you
   cannot name a field for is a clause you wrote.
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
