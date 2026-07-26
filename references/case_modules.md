# Case Modules (BDD Slices Over A View)

**Status: OPTION. Evidence-backed by one probe, not mechanized, not required.**
Nothing in the workflow asks for case modules, nothing warns when a project has
none, and a project that never writes one loses nothing it has today. This
reference exists so that a project that *wants* the shape has a doctrine to
follow instead of inventing one.

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

- **CM-F1 — model discovery collides (pre-existing, made worse).** The
  complexity ledger locates its model as the alphabetically first `*.tla` in the
  spec directory excluding `MC*` (`scripts/spec_evolution.py:find_model_files`).
  On the shipped three-module example that is already wrong — it measures
  `Core.tla` against `External.cfg` and reports `bound = None`,
  `modularity = 0.0`. Any case module sorting before `Core.tla` silently becomes
  the measured model instead. Interim convention: name case modules
  `Scenario_*.tla`, which sorts after `Core`/`External`/`Internal` and leaves
  today's behavior unchanged. Real fix: declare the measured model in the
  manifest.
- **CM-F2 — zero-case warnings for actions outside the slice.** Generation warns
  once per declared view action that produced no case (R4-DF-04), and diagnoses
  it as an alias-wrapper problem — which is the wrong cause here, where the
  action simply is not in this aspect. A slice covering 4 of 12 external actions
  emits 8 misleading warnings. Needs a per-module action scope.
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

## What is not mechanized

There is no `case_modules:` block in `spec_manifest.yaml`, no CLI subcommand, no
scaffold template, and no aggregation of per-module corpora into one report.
Ownership (rule 2 above) is checked by hand today. A project using the option
runs its case modules the way the probe did — explicit paths, one command per
module — and records the set it runs in the manifest's prose or its ticket
evidence. Mechanizing it is `tickets/039-case-modules.md`, unscheduled.
