# Self-improvement matrix

**The most important output this project produces.** Everything else — the
suite, the graph, the scorecard — says whether a change was correct. This says
**where our bugs come from, and whether we did anything about it.**

**It is maintained by prompting, not by a tool.** A tool that computes this
would have to parse findings, infer areas, and join them across epics, and every
one of those steps is a place to introduce a bug into the instrument we use to
find bugs. **The cost of a wrong row here is higher than the cost of writing it
by hand.** If a tool is ever added it goes in a separate library, and this file
is what it would have to reproduce.

---

## The matrix

One row per architectural area. **Areas are prose, named by whoever found the
bug** — never a derived taxonomy (`references/bug_attribution.md` §4).

| area | caught by graph/suite | escaped to hand | pinned by an assertion | still unpinned | suggestion, and what happened to it |
|---|---|---|---|---|---|
| the workflow-close archive path | 0 | **1** (`AT-EX-CATCH-02`) | 1 — `test_the_ticket_workdir_is_pruned_too…` | 0 | *exclusions attached to a copy are silently absent from every move beside it* — **OPEN** |
| the constrained YAML parser | 4 (differential) | 3 (#298 report) | 7 — the differential + 7 pinned inputs | 0 | *a reimplementation needs a differential against what it reimplements* — **ACTED ON**, #298 |
| the close gate (bookkeeping) | 0 | 2 (`F-02`, refinement cascade) | 0 | **2** | *the close path's entire agent-facing cost is paperwork, not correctness* — **OPEN** |
| the scaffolded spec-unit test | 0 | 1 (#299) | 1 — both-depths test | 0 | *resolve by search, not by counting `..`* — **ACTED ON**, #299 |
| case generation coverage | 0 | 2 (#300, `F-06`) | 1 — `expected_zero` refusal | 1 | *a green that declares nothing is worse than a red* — **PARTLY ACTED ON** |

**Read the `escaped to hand` column first.** It is the only column that says an
automated instrument was blind, and it is the column every other one exists to
reduce.

---

## What the matrix currently says, stated as a hypothesis and not a result

**Every row has `caught by graph/suite` = 0 except the parser**, and the parser's
4 came from a differential written *in the same change as the fixes*. **So on
this record, the standing automated instruments have caught approximately
nothing, and everything was found by hand or by a new instrument built for the
occasion.**

**That is the same shape this repository already measured and published** —
*"seven epics of static checking caught zero bugs in a subject program"* — now
reproduced on its own toolchain.

**Why it is a hypothesis:** the denominators are missing. A row with 1 escape
over 100 invocations and a row with 1 escape over 2 invocations look identical
here. **No round has a per-area denominator yet**, and until one does, the
concentration in this table may be a concentration of *attention* rather than of
*defects*.

---

## Maintaining it

**At every ticket close** and **at every epic evaluation**, the agent is prompted
to add or update rows — see `prompts/regression_architecture.md` and the two
surfaces in `references/workflows.md`.

**Rows are appended and amended, never silently rewritten.** A suggestion that
was `OPEN` and became `REFUSED` keeps its reason. A suggestion that was acted on
names the change, so the next round can ask whether the escapes actually fell.

**An area with no new rows this epic gets no row.** Absence of evidence is
recorded as absence, not as a zero.
