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

---

## Step 1 — Enumerate the surface. Do not curate it.

Same discipline as `prompts/coverage_audit.md`: **the row set is produced by a
command, not by your attention.** Run these, record the raw counts, and carry
exactly that many rows.

```bash
# (a) the actions the toolchain sees in this view -- same coverage contract as
#     the scanners: EXTENDS followed, INSTANCE/LOCAL fail closed, actions are
#     the top-level disjuncts of the next-state relation.
python3 scripts/tla_spec_dev.py --spec-root specs analyze architecture \
  <View>.tla <View>.cfg --format json | jq -r '.measured.actions[].name' | sort

# (b) the actions the project DECLARES for this view, with their layer
python3 -c "import yaml,sys; d=yaml.safe_load(open(sys.argv[1]))['actions']; \
  [print(k) for k,v in sorted(d.items()) if v.get('layer')=='<external|internal>']" \
  <spec dir>/actions.yml
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
python3 scripts/case_modules.py coverage \
  --manifest <manifest> --actions-metadata <spec dir>/actions.yml --view <view> \
  --corpus generated/testgraph/<each module>_cases \
  --corpus generated/testgraph/<View>_cases
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
   your output is invalid — go back to Step 0.
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
3. One `Scenario_*.tla` per entry, each carrying its claim in prose.

---

## Validation status of this prompt — read before trusting it

**Not yet run end-to-end against a project whose aspects an author supplied.**
The mechanized halves are exercised — CM-01 measured the shape on
`examples/case_modules/` (three modules, 732 view cases versus 190 across
slices) and shipped `validate` and `coverage`. Step 0's elicitation is the part
with no evidence behind it, and it is the part everything else rests on.

**Known-open:** this prompt can be followed perfectly and still produce a
decomposition that is wrong about the product, because the only check on the
aspect list is that a human authored it. Nothing here measures whether the
aspects are the *right* aspects. Coverage is checkable; carving is not.
