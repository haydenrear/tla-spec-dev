# Case Modules (BDD Slices Over A View)

**Status: OPTION. Evidence-backed by one probe, partly mechanized, not
required.** Nothing in the workflow asks for case modules, nothing warns when a
project has none, and a project that never writes one loses nothing it has
today. This reference exists so that a project that *wants* the shape has a
doctrine to follow instead of inventing one. CM-01 mechanized the declaration
and the coverage report — see "What is mechanized" — but the shape itself is
still something you write, not something a template writes for you.

## The shape

The accepted baseline is unchanged: `Core.tla` + `Internal.tla` + `External.tla`
— one semantic authority, two executable views. A **case module** is a third
kind of file that sits beside them:

```tla
---- MODULE Scenario_CheckoutHappyPath ----
EXTENDS External

CheckoutHappyPathNext ==
  \/ \E c \in Clients, a \in Accounts : SubmitCreateAccount(c, a)
  \/ \E c \in Clients, a \in Accounts, sku \in Skus : SubmitAddCartItem(c, a, sku)
  \/ \E c \in Clients, a \in Accounts, o \in Orders : SubmitCheckout(c, a, o)
  \/ \E c \in Clients : RunFulfillmentWorker(c)

CheckoutHappyPathSpec == ExternalInit /\ [][CheckoutHappyPathNext]_ExternalVars
====
```

It declares **no VARIABLES, no CONSTANTS, and no actions**. It EXTENDS a view
and does exactly two things, either or both:

- restricts the next-state relation to the entry points one aspect of the
  program exercises (a **slice**);
- replaces `Init` with an initial-state predicate that asserts the situation
  the aspect starts from (a **Given**).

It generates cases through the same command, the same `actions.yml`, the same
`case_adapters.toml` / `testgraph_bindings.yml`, and the same effect providers
as the view it extends. A case module needs no adapter of its own — if it did,
it would be introducing behavior, which is the thing it must not do.

## What it is NOT (reconciling with the Program Spec Rule)

SKILL.md's Program Spec Rule stands: *do not create one TLA+ module per feature*.
A case module is not a feature module and does not weaken that rule, because it
adds nothing to the semantic authority:

| Program spec (Core/Internal/External) | Case module |
|---|---|
| Owns state, actions, invariants | Owns none of them |
| Where behavior is added | Where existing behavior is *entered* |
| Reviewed as the model of the program | Reviewed as a test-design decision |
| Deleting it loses program meaning | Deleting it loses only a corpus |

The test: **remove every case module and the program is still fully
represented.** If removing one loses a behavior, that behavior was written in
the wrong file — move it into the view.

SKILL.md's "Program Spec Rule" states this distinction once and is the
authority; the table above is the same claim in this reference's terms, not a
second version of it.

The doctrine this extends is already in
`references/architecture_tractability.md`, "Irreducible Pieces: Creative
Representations": *many small lenses instead of one big mirror* and *temporal
decomposition*. Case modules are that idea applied to case generation rather
than to an untouchable component, and they are additive to the view rather than
a replacement for it.

## Two forms, and only the second one is lossy

**Form 1 — the slice (restrict `Next`, keep `Init`).** Enumerates the same
reachable states the view would, minus whatever is only reachable through the
excluded actions. Cheap, and nearly lossless for the actions it keeps.

**Form 2 — the Given (replace `Init`).** Asserts the pre-state instead of
enumerating a path to it. This is where the real reduction comes from and where
the real claim is made: *this aspect's behavior does not depend on which
reachable configuration you replay it from*. That is a **modeling claim about
the program**, and it must be recorded with the module, in prose, next to the
Given. It is not a filter, and the difference matters — see "Integrity" below.

A BDD "Given" is naturally form 2. Writing the Given as a replay of the setup
actions instead (`Next` containing the whole happy path plus the aspect's
actions) puts the enumeration back and buys almost nothing.

## Measured evidence (one probe, `examples/case_modules/`)

Against the shipped worked example `examples/distributed_history`, three case
modules versus the whole External view, same constants, same projectors, same
`--dedupe projected`:

| | states | cases | wall clock |
|---|---|---|---|
| `External` (whole view) | 49,386 distinct / 632,658 generated, depth 11 | 732 | 1m 23s |
| `Scenario_CheckoutHappyPath` (slice) | 1,175 | 160 | 2.2s |
| `Scenario_IdempotentResubmit` (Given) | 113 | 16 | 1.1s |
| `Scenario_RejectedRequests` (slice) | 37 | 14 | 1.0s |

Per action — every external action of the view is covered by exactly one or two
modules:

| action | whole view | slices |
|---|---|---|
| SubmitCreateAccount | 2 | 2 + 2 |
| SubmitAddCartItem | 40 | 40 |
| SubmitCheckout | 52 | 52 |
| RunFulfillmentWorker | 74 | 66 + 2 |
| RunFulfillmentWorkerNoop | 48 | 2 |
| SubmitDuplicateCreateAccount | 120 | 4 |
| SubmitDuplicateAddCartItem | 200 | 4 |
| SubmitDuplicateCheckout | 184 | 4 |
| SubmitAddCartItemMissingAccount | 4 | 4 |
| SubmitCheckoutMissingAccount | 4 | 4 |
| SubmitCheckoutEmptyCart | 4 | 4 |
| **total** | **732** | **190** |

Three things to read out of that table, in order of importance:

1. **The slice form is close to lossless.** `Scenario_CheckoutHappyPath`
   reproduces the whole view's corpus *exactly* for three of its four actions
   (2 / 40 / 52) and loses 8 of 74 on `RunFulfillmentWorker` — before-states
   reachable only through actions the slice excludes.
2. **The Given form is where the reduction lives, and it is a claim.** The three
   duplicate-command actions go 504 → 12. Those 504 were distinct projected
   before-states; collapsing them asserts that resubmission behavior is
   independent of cart/order configuration. True or false, it is a statement
   about the program, and it belongs in review.
3. **What the reduction hits is what the corpus diagnostics already flagged.**
   The whole view's diagnostics name `SubmitDuplicateAddCartItem` (200),
   `SubmitDuplicateCheckout` (184), `SubmitDuplicateCreateAccount` (120) as the
   dominating strata — 69% of the corpus — and the example had to raise
   `max_external_cases_per_action` from 50 to 200 to ship (VAL-08). The Given
   form addresses that fan-out **in the diagram**, which is what
   `references/modular_fuzzing.md`, "Corpus Discipline", says to do.

## Integrity: a Given is upstream, dropping cases is downstream

The evidence-integrity rule in `references/architecture_tractability.md` is
unchanged and outranks everything here: **cases are never dropped, filtered,
sampled, or truncated.** A case module does not do that. It does not touch a
generated corpus at all — it is a different model, and TLC exhaustively
enumerates *it*.

The line to hold, because it is easy to cross:

- Legitimate: "resubmission is independent of cart contents, so this aspect
  starts from an asserted Given" — a representation decision, recorded with the
  module, reviewable, and still exhaustively checked within the slice.
- **Degenerate**: writing case modules until every corpus fits under a cap, and
  treating the union as if it were the view's corpus. That is trimming with
  extra steps, and the fact that it produces a green corpus gate is exactly why
  it is dangerous.

The rules that keep the first from becoming the second:

1. **The view keeps its own corpus.** Case modules are additive. A project that
   stops generating from `External.tla` has replaced its representation with a
   sample of it, whatever the file layout says. If whole-view generation is too
   expensive to run every time, run it on a declared cadence and record the
   cadence — do not silently retire it.
2. **Every action stays owned.** Each action of the view is exercised by at
   least one case module *or* by the view's own corpus. An action no module
   enters and no view run covers is unvalidated surface, which the coverage
   audit already treats as a gap.
3. **Every Given carries its claim in prose**, next to the predicate, naming
   what it asserts is irrelevant. An unexplained Given is unreviewable.
4. **Cross-aspect interleaving is what you gave up.** Slices do not enumerate
   the interleavings between aspects — the whole-view run is the only thing that
   does. Say so when reporting coverage; do not report the union as equivalent.

## Mechanics that already work today

No toolchain change is needed to try this. Everything below was run in the probe:

```bash
# a case module is analyzed like any other model
tla-spec-dev analyze complexity specs/program_model/Scenario_CheckoutHappyPath.tla \
                                specs/program_model/Scenario_CheckoutHappyPath.cfg

# and generates cases like any other view module
python3 scripts/generate_cases_from_tlc_dump.py \
  specs/program_model/Scenario_CheckoutHappyPath.tla \
  specs/program_model/Scenario_CheckoutHappyPath.cfg \
  --out generated --package checkout_happy_cases --view external \
  --actions-metadata specs/program_model/actions.yml \
  --state-projector ... --output-projector ... --dedupe projected

# and binds to the EXISTING adapters, unchanged
python3 scripts/run_generated_case_adapters.py generated/testgraph/checkout_happy_cases \
  --mapping specs/program_model/testgraph_bindings.yml --view external --batch --validate-only
```

The last command reported `external channel enforcement passed for 4 binding(s)`
and `validated 11 adapter mappings for 5 labels` on a case-module package with
no adapter changes at all. That is the property that makes the option cheap: a
case module is a new *entry*, never a new *boundary*.

The module resolver follows `EXTENDS` transitively and fails closed on
`INSTANCE` and `LOCAL` (MF-030). **Case modules must use `EXTENDS`.** A module
that instantiates its view is unanalyzable, and the failure is an exit-nonzero
"I could not measure this", not a warning.

## Known frictions (measured in the probe, filed as CM-F1..F4)

- **CM-F1 — model discovery collides (pre-existing). FIXED in CM-01.** The
  complexity ledger used to locate its model as the alphabetically first `*.tla`
  in the spec directory excluding `MC*`. On the shipped three-module example
  that was already wrong — it measured `Core.tla` against `External.cfg` and
  reported `bound = None`, `modularity = 0.0` for a module with no variables and
  no actions, and any case module sorting before `Core.tla` silently became the
  measured model instead. `scripts/spec_evolution.py:select_model_files` now
  resolves the model **declared first, discovered second**: a `model:` block in
  `spec_manifest.yaml`, else the outermost view of a Core/Internal/External
  baseline, else a legacy single module named by the manifest's `module:`. A
  directory it cannot resolve unambiguously, and a `.tla`/`.cfg` pair where the
  cfg names a `SPECIFICATION`, `INIT`/`NEXT`, invariant, or constant the module
  does not declare, are both **errors** — "I could not measure this" — never a
  silent `bound = None`. The `Scenario_*` naming convention is no longer load
  bearing.
- **CM-F2 — zero-case warnings for actions outside the slice. FIXED in CM-01.**
  Generation warns once per declared view action that produced no case
  (R4-DF-04) and diagnoses it as an alias-wrapper problem — the wrong cause when
  the action simply is not in this aspect. Measured on
  `Scenario_RejectedRequests`, a 4-action slice of an 11-action view: **7 wrong
  warnings**. A module declared in `case_modules:` now has its warning scoped to
  its own `actions:`, and the same run emits **0**. An in-scope action that
  generates nothing still warns; the alias-wrapper diagnosis keeps meaning what
  it says. Scope changes what is *reported*, never what is generated.
- **CM-F3 — descriptor metrics do not compare across a slice and its view.**
  Dense rows, modularity, and component sizes are normalized by the action
  count, so the same program measured through a 4-action slice reported *more*
  dense rows (4/4 variables), lower modularity (Q 0.019 vs 0.047), and a
  `max_component_variables` warning the whole view never emits. Descriptors of
  case modules are readable on their own terms; **never ledger a slice's
  descriptor against a view's.**
- **CM-F4 — the kill test's boundary catalog widens.** The required catalog is
  derived from the `INVARIANT(S)` of every `*.cfg` in the spec directory. A case
  module reusing the view's invariant adds no obligation; one that declares its
  own "Then" invariant requires a seeded mutant for it, or the kill test refuses
  with `incomplete_catalog`. That coupling is arguably correct — a new checked
  property should need a fault seeded at it — but it is a surprise. `--cfg`
  scoping is the existing lever.

## What is mechanized (CM-01)

### The `case_modules:` block

A project declares the modules it runs in `spec_manifest.yaml`, beside the
`model:` block that fixes what the complexity ledger measures:

```yaml
model:                      # CM-F1: the measured model is declared, not discovered
  tla: External.tla
  cfg: External.cfg

case_modules:
  Scenario_CheckoutHappyPath:
    extends: External       # required -- the view this module EXTENDS
    view: external          # optional -- the generation view
    form: slice             # slice (default) | given
    actions:                # required -- the view actions this aspect enters
      - SubmitCreateAccount
      - SubmitAddCartItem
      - SubmitCheckout
      - RunFulfillmentWorker
  Scenario_IdempotentResubmit:
    extends: External
    form: given
    actions: [SubmitDuplicateCreateAccount, SubmitDuplicateAddCartItem]
    claim: >-               # REQUIRED for form: given
      Resubmitting an already-applied command is independent of the reachable
      configuration it is replayed from. ...
```

`claim:` is required on a Given and free text on purpose: it is rule 3 above
made checkable-by-a-human, not by a parser. A `form: given` entry without one
is a schema error, because an unexplained Given is unreviewable. The module
file itself does not have to live beside the manifest — the block declares the
set the project runs, and the probe's modules are kept in
`examples/case_modules/` and copied in.

```bash
python3 scripts/case_modules.py validate --manifest specs/program_model/spec_manifest.yaml
```

A block generation cannot parse **warns and is ignored** — generation keeps its
previous behavior and never refuses.

### Per-module action scope

Generation reads the declaration for the module it is generating and scopes the
R4-DF-04 zero-case warning to that module's `actions:`. It also reports two
kinds of drift, both advisory: an action in the declared scope that the view's
`actions.yml` does not declare, and an action the corpus generated that the
declared scope does not list. A stale declaration makes the coverage report lie,
so it is said out loud.

### The coverage aggregation report

Every generated case package now carries a `case_coverage.json` — measured
per-action counts, the declared view actions, and the declaration in force.
Aggregate them:

```bash
python3 scripts/case_modules.py coverage \
  --manifest specs/program_model/spec_manifest.yaml \
  --actions-metadata specs/program_model/actions.yml --view external \
  --corpus generated/testgraph/Scenario_CheckoutHappyPath_cases \
  --corpus generated/testgraph/Scenario_IdempotentResubmit_cases \
  --corpus generated/testgraph/Scenario_RejectedRequests_cases \
  --corpus generated/testgraph/External_cases
```

It prints per-action coverage across every declared module beside the view's own
corpus, and names every view action **entered by no measured module and not
covered by the view's own corpus** — rule 2 above, mechanized. A module that is
declared but has no corpus is reported UNMEASURED, not zero: a declaration is an
intention, and this report counts cases. So is a missing view corpus, which is
how rule 1 stays visible.

**It gates nothing and always exits 0** when it could be produced. A nonzero
exit means "I could not measure this" — an unreadable manifest, a corpus with no
coverage record. Uncovered actions are a finding to read.

### The prompt that produces a set (AC-03)

`prompts/aspect_decomposition.md` is the procedure for going from a view to a
validated `case_modules:` block: it enumerates the view's action set by command
(the same discipline `prompts/coverage_audit.md` uses — the row set comes from
a command, not from the agent's attention), reconciles that set against
`actions.yml` in both directions, requires every `form: given` row to state its
claim as *"X is independent of Y"* with Y named, and runs `validate` and
`coverage` above rather than self-reporting them.

Its load-bearing rule is a limit, not a capability: **the action set is
mechanical, the grouping into aspects is not.** Which actions belong to the
same user-facing aspect is a fact about what the program is *for*, and nothing
in the TLA+ says so. An agent that clusters by name prefix, shared variables, or
modularity is inventing product structure out of syntax, and the output is
indistinguishable from a real decomposition. The prompt therefore requires the
aspect list to come from the model author and to record who supplied it; with
no author, its correct output is "the aspects of this surface are not derivable
from the model", not a plausible list.

## What is still not mechanized

There is no scaffold template for the shape and no CLI subcommand under
`tla-spec-dev`. Templating the shape before it has eval coverage would invite
projects to slice by default, which is the degenerate path in "Integrity" above:
case modules are **additive** to a view's corpus, never a replacement for it.
Cross-aspect interleaving (rule 4) is not measured by anything and cannot be —
only a whole-view run produces it, and the report says so every time it runs.
