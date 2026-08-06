# Aspect Decomposition — sub-agent prompt (AC-03)

**Dispatch this file verbatim as the prompt for a sub-agent.** It is the ask
from the *user's* side of a view: enumerate the aspects of the public surface,
name each aspect's Given, map each to a case module and its action scope, and
state for each Given what it asserts is **irrelevant**. Its output is the
`case_modules:` block CM-01 mechanized. Doctrine:
`references/case_modules.md`; the Program Spec Rule it must not weaken:
`SKILL.md`.

---

## What you are being asked to produce

A BDD decomposition of one view, written as a manifest block and a claims
table — nothing else. Concretely:

```yaml
case_modules:
  Scenario_CheckoutHappyPath:
    extends: External
    view: external
    form: slice
    actions: [SubmitCreateAccount, SubmitAddCartItem, SubmitCheckout, RunFulfillmentWorker]
  Scenario_IdempotentResubmit:
    extends: External
    form: given
    actions: [SubmitDuplicateCreateAccount, SubmitDuplicateAddCartItem, SubmitDuplicateCheckout]
    claim: >-
      Resubmitting an already-applied command is independent of the reachable
      cart and order configuration it is replayed from.
```

The block is validated, not decorative:

```bash
python3 scripts/case_modules.py validate --manifest <manifest>
```

`extends:` and a non-empty, duplicate-free `actions:` are required on every
entry; `form:` is `slice` (default) or `given`; **`claim:` is a schema error to
omit on a `form: given` entry**, because an unexplained Given is unreviewable.
Write the block so that command exits 0 — not because it gates anything (it
does not), but because a block generation cannot parse is *warned and ignored*,
and an ignored declaration is a decomposition that never happened.

---

## Step 0 — The one thing you must not fake

**The action set is mechanical. The grouping into aspects is not.**

You can enumerate every action of a view with a command, and this prompt makes
you. You **cannot** derive from the model which of them belong to the same
user-facing aspect. `SubmitCheckout` and `RunFulfillmentWorker` are one aspect
("a customer checks out and the order is fulfilled") because of what the
program is *for*, and nothing in the TLA+ says so. An agent that clusters
actions by name prefix, by shared variables, or by modularity is inventing
product structure out of syntax, and the result will look exactly like a real
decomposition.

So:

> **The aspect list comes from the model author or the user. You elicit it, you
> record who gave it, and you never generate it.**

If no one will supply it, the correct output is **not** a plausible
decomposition. It is: *"the aspects of this surface are not derivable from the
model; the author must name them."* Say that, attach the enumerated action set
and any candidate groupings you would *ask about* (clearly marked as
questions), and stop. That is a useful result. A confident aspect list nobody
authored is not.

What you may do unaided: enumerate, check coverage, check the schema, and
challenge a supplied grouping against the measured action set.

### This requirement is UNENFORCEABLE. Read that before you rely on it.

**Nothing checks it, and nothing can.** The `Source` column below is free text.
`case_modules.py validate` checks the schema; `case_modules.py coverage` counts
cases; neither has any way to know whether a human named an aspect or you did.
There is no artifact difference between the two outputs — that is the entire
point of Step 0, and it applies to the check as much as to the carving.

This is not hypothetical: an eval agent following this prompt produced a
complete, schema-valid, coverage-clean decomposition of a real fixture with **no
author in the loop at all**, and the only thing that surfaced the violation was
the agent volunteering it (EV-02-DF-04).

Two ideas were considered and rejected rather than shipped as theatre:

- *requiring a non-empty `Source`* — an agent writes one. A guard a determined
  agent walks around is worse than no guard, because it makes the next reader
  believe the column was verified.
- *rejecting `Source: the model` / `Source: derived`* — same, one word longer.

So the honest contract is: **a decomposition carries the provenance its author
claims, and a reader must treat provenance as an unverified claim.** If you
produce a decomposition without an author, you must say so in your report
(Step 6.1) and label the output *unreviewed*. That is a self-report, and a
self-report is exactly as reliable as the agent making it. Anyone consuming an
aspect list should ask the named source directly.

---

## Step 1 — Enumerate the surface. Do not curate it.

Same discipline as `prompts/coverage_audit.md`: **the row set is produced by a
command, not by your attention.** Run these, record the raw counts, and carry
exactly that many rows.

Run these from the project root, with `$REPO` set to the checkout that holds
`scripts/`. Both were run as written on
`examples/validation/ex4_pipeline_coherent`; substitute your own paths and
nothing else.

```bash
# (a) the actions the toolchain sees in this view -- the coverage contract is
#     EXTENDS followed, INSTANCE/LOCAL fail closed, actions are the top-level
#     disjuncts of the next-state relation.
#
#     NOTE: --spec-root does NOT resolve the positional .tla/.cfg. Give their
#     path relative to your current directory (or absolute); a bare `<View>.tla`
#     exits with "ERROR: spec not found".
#
#     This used to read `analyze architecture`, removed 2026-08-04 with the
#     static architecture scanners (references/architecture_advice.md).
#     `analyze complexity` carries the same `.measured.actions` list, with each
#     action's read and write set.
python3 "$REPO/scripts/tla_spec_dev.py" --spec-root specs analyze complexity \
  <spec dir>/<View>.tla <spec dir>/<View>.cfg --format json | python3 -c \
  "import json,sys; [print(a['name']) for a in sorted(json.load(sys.stdin)['measured']['actions'], key=lambda a: a['name'])]"

# (b) the actions the project DECLARES for this view, with their layer.
#     Uses the toolchain's own manifest reader: this repository deliberately does
#     not require PyYAML, and `import yaml` fails in its default environment.
python3 -c "
import sys
sys.path.insert(0, sys.argv[3])
from pathlib import Path
from extract_spec_manifest import load_manifest
actions = load_manifest(Path(sys.argv[1])).get('actions') or {}
for name in sorted(actions):
    if (actions[name] or {}).get('layer') == sys.argv[2]:
        print(name)
" <spec dir>/actions.yml <external|internal> "$REPO/scripts"
```

**Reconcile (a) against (b) and report both directions.** An action in the
module that `actions.yml` does not declare, and a declared action the module
does not contain, are each a finding — and each makes the coverage report
downstream lie. CM-01 reports the same two drifts at generation time; do not
wait for it.

Drop `Stutter`, `Terminating`, and any explicit no-op disjunct from the aspect
row set, and **say that you did**. They are not public surface. Every other
action is a row.

---

## Step 2 — One row per action, assigned by the author

| # | Action | Aspect | Given (one sentence, user's voice) | Form | Asserted irrelevant | Source |
|---|---|---|---|---|---|---|

- **Aspect** — the user-facing capability. Supplied, never inferred (Step 0).
- **Given** — the situation the aspect starts from, in the user's words:
  *"an account exists and its cart has one item"*. Not a predicate yet.
- **Form** — `slice` if the Given is just "from the start" (restrict `Next`,
  keep `Init`); `given` if the Given asserts a pre-state (replace `Init`).
- **Asserted irrelevant** — required on every `given` row, and it is the whole
  content of the `claim:`. Phrase it as *"X is independent of Y"*, naming Y.
  "The cart is pre-filled" is a description; *"resubmission behavior is
  independent of which reachable cart configuration it is replayed from"* is a
  claim, and only a claim can be reviewed or falsified.
- **Source** — who supplied the aspect. A name, a message, a ticket. Not "the
  model".

An action may appear in more than one aspect. An action in **no** aspect is
allowed only if you write, on its row, that the view's own corpus covers it —
which is rule 2 of `references/case_modules.md`, and which
`scripts/case_modules.py coverage` will check against measured case counts.

Close the step with `enumerated N = <count>, rows M = <count>, N == M`.

---

## Step 3 — Write the Given as a predicate, and pay for it out loud

A `form: given` module replaces `Init` with an initial-state predicate over
**every variable of the view**. That is where the reduction comes from — the
probe measured three duplicate-command actions going 504 cases to 12 — and it
is where the claim is made.

**This is the step you cannot do from the outside.** A `slice` is writable from
action names alone: `actions.yml` and a README are enough. A `Given` requires
every state variable of the view, its type, and enough of each action's guard to
land on a pre-state the aspect can actually run from — none of which a public
surface tells you. If you are working from the outside, the honest split is that
you supply the **claim** ("X is independent of Y") and someone with the model
open writes the predicate. Say which of the two you did.
`references/case_modules.md`, "The authoring asymmetry", is the authority.

Two rules:

1. **A partial Given is not a Given.** Leave one variable unconstrained and TLC
   enumerates its whole domain from the initial state; the module is neither
   the reduction you wanted nor the situation you described. List the view's
   variables and constrain each.
2. **Write the claim next to the predicate, in prose, in the module file**, as
   well as in `claim:`. The manifest is where tooling reads it; the module is
   where a reviewer is standing when the question occurs to them.

Do not write the Given as a replay of the setup actions (`Next` containing the
happy path plus the aspect's actions). That puts the enumeration back and buys
almost nothing — and it hides the claim instead of stating it, which is worse
than the cost.

---

## Step 4 — Reconcile with the Program Spec Rule. This is the hard boundary.

A case module is **not** a feature module, and this prompt must not turn into
one. `SKILL.md` stands: do not create one TLA+ module per feature.

A case module you write here:

- declares **no VARIABLES, no CONSTANTS, and no actions**;
- `EXTENDS` its view — never `INSTANCE`, never `LOCAL`; the module resolver
  fails closed on both (MF-030), and an unanalyzable module is an exit-nonzero
  "I could not measure this", not a warning;
- does exactly one or both of: restrict the next-state relation to the entry
  points the aspect exercises, and replace `Init` with an asserted Given.

**The test, and run it on every module you produce:** *remove every case module
and the program is still fully represented.* If removing one loses a behavior,
that behavior was written in the wrong file — move it into the view. A
`Scenario_` module that defines a new operator with a state update in it is a
feature module with a scenario's name.

### Forbidden, in any wording

- a new variable, constant, or action in a case module;
- a next-state disjunct that is not an existing view action;
- **writing case modules until every corpus fits under a budget cap, and
  treating the union as the view's corpus.** That is trimming with extra steps,
  and it produces a green corpus gate, which is exactly why it is dangerous.
  Case modules are **additive**: the view keeps generating its own corpus, on a
  declared cadence if it is expensive, and you record the cadence rather than
  silently retiring it;
- dropping, filtering, sampling, or truncating generated cases — the
  evidence-integrity rule outranks everything in this prompt;
- claiming the union of slices is equivalent to the view. **Cross-aspect
  interleaving is what you gave up.** Only a whole-view run enumerates it,
  nothing measures it, and you say so every time you report coverage;
- proposing a component boundary, a refactor, or any architectural move
  (CD-01). If an aspect's actions span components, report that as a fact you
  observed; do not conclude anything from it.

### One coupling to warn the author about

A case module that reuses the view's invariant adds no obligation. One that
declares its **own** "Then" invariant widens the kill test's required boundary
catalog: the catalog is derived from the `INVARIANT(S)` of every `*.cfg` in the
spec directory, and an uncovered one makes the kill test refuse with
`incomplete_catalog` (CM-F4; `--cfg` scoping is the existing lever). Say this
when you propose a new invariant. Do not decide it for them.

---

## Step 5 — Check coverage with the tool, not with your table

```bash
# EXTERNAL view: packages land under <out>/testgraph/
python3 "$REPO/scripts/case_modules.py" coverage \
  --manifest <manifest> --actions-metadata <spec dir>/actions.yml --view external \
  --corpus <out>/testgraph/<each module>_cases \
  --corpus <out>/testgraph/<View>_cases

# INTERNAL view: packages land under <out>/spec-unit/. An internal-only project
# has no testgraph/ and no testgraph_bindings.yml at all; the end-to-end run is
# worked in references/case_modules.md, "Worked example: an internal-only project".
python3 "$REPO/scripts/case_modules.py" coverage \
  --manifest <manifest> --actions-metadata <spec dir>/actions.yml --view internal \
  --corpus <out>/spec-unit/<each module>_cases \
  --corpus <out>/spec-unit/<View>_cases
```

Read three things out of it and put them in your report:

- every view action **entered by no measured module and not covered by the
  view's own corpus** — unvalidated surface, which the coverage audit already
  treats as a gap;
- every module reported **UNMEASURED** — declared but with no corpus. A
  declaration is an intention; this report counts cases. Do not present an
  UNMEASURED module as coverage;
- a missing **view** corpus, which is how rule 1 above stays visible.

It gates nothing and exits 0 whenever it could measure. A nonzero exit means
"I could not measure this" — fix the input, do not interpret the silence.

---

## Step 6 — Self-check

In your report to the caller, not in the output:

1. Who supplied the aspect list, verbatim? If the answer is "I derived it",
   your output is invalid — go back to Step 0. Nothing checks this answer; it is
   a self-report and Step 0 says so. Answer it anyway, and answer it first.
2. `N == M` for Step 1, with both raw counts and the reconciliation of (a)
   against (b).
3. Every `form: given` row: does its claim read as *"X is independent of Y"*
   with Y named? A claim without a Y is a description.
4. Did `case_modules.py validate` exit 0? Paste the output.
5. Did any module you wrote fail the removal test in Step 4?
6. **Findings about this prompt.** If following it let you produce a
   plausible-looking decomposition without an author naming a single aspect,
   say so and name the step that permitted it. That finding outranks the
   artifact.

---

## Output

1. The `case_modules:` block, pasted into the project's `spec_manifest.yaml`
   (beside `model:`), validating clean.
2. The Step 2 table, as ticket evidence.
3. One `Scenario_*.tla` per entry, each carrying its claim in prose. They may
   live in their own directory (`specs/case_modules/`) and generate from there
   in place — nothing has to be copied beside the view.
4. The provenance of the aspect list, stated plainly, including "no author" when
   that is the truth (Step 0).

---

## Validation status of this prompt — read before trusting it

**Not yet run end-to-end against a project whose aspects an author supplied.**
The mechanized halves are exercised — CM-01 measured the shape on
`examples/case_modules/` (three modules, 732 view cases versus 190 across
slices) and shipped `validate` and `coverage`; RP-03 ran Steps 1, 5 and the
whole generation path verbatim on `examples/validation/ex4_pipeline_coherent`.
Step 0's elicitation is the part with no evidence behind it, and it is the part
everything else rests on.

**Known-open:** this prompt can be followed perfectly and still produce a
decomposition that is wrong about the product, because the only check on the
aspect list is that a human authored it — and *that* is unenforceable too, which
Step 0 now states where the requirement is made rather than only here. Nothing
measures whether the aspects are the *right* aspects. Coverage is checkable;
carving is not; provenance is a self-report.

**Measured once (EV-02-DF-04):** an agent that had never seen the fixture
authored a working slice from the public surface alone, and could not have
written the Given the same way — Step 3 says why. If your report claims an
outside-in decomposition that includes a `form: given` predicate, one of the two
claims is wrong.
