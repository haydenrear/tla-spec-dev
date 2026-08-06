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

## The authoring asymmetry: a slice comes from outside, a Given cannot

This is the real limit on the "manual test starter" use of case modules, and it
was measured (EV-02-DF-04). An agent who had never seen the fixture, given only
its public surface — the README and `actions.yml` — authored a working slice and
a working Given for it, and reported the difference between the two experiences:

> the aspect came from the outside; the Given could only be written from the
> inside.

Concretely:

| | what you must know to write it | where that knowledge lives |
|---|---|---|
| **slice** (restrict `Next`) | the action *names* you want to enter, and their arities | `actions.yml`, the README, the public surface |
| **Given** (replace `Init`) | **every state variable of the view**, its type, and enough of each action's guard to write a pre-state the aspect can actually run from | the model itself |

A slice is `\/ \E i \in Items : Deliver(i)` repeated — copy the names out of
`actions.yml` and you are done. A Given is
`inbox = Items \ {i} /\ accepted = {i} /\ queue = {} /\ delivered = {i} /\ ...`
over *all six* variables, because rule 1 of Step 3 in
`prompts/aspect_decomposition.md` is not a style preference: leave one variable
unconstrained and TLC enumerates its whole domain from the initial state, and
you get neither the reduction nor the situation you described. You cannot write
that from a README. You cannot even discover the *variable list* from a README.

So plan the work accordingly:

- **A slice is an outside-in artifact.** It can be commissioned from someone who
  knows the product and not the model, and it is the cheap on-ramp.
- **A Given is an inside-out artifact.** It needs the model open. What an
  outsider can contribute is the *claim* — "resubmission is independent of cart
  contents" — which is the part that actually needs product knowledge; someone
  with the model then writes the predicate that encodes it.

Splitting a Given that way is fine and arguably correct: the claim is the
reviewable half. What is not fine is pretending the predicate was authored from
the outside. `form: given` modules are where a decomposition silently stops
being an outside-in artifact, and no tool can tell the difference afterwards.

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

Those commands are for an **external** view. An internal-only project has no
`--view external`, no `generated/testgraph/`, and no `testgraph_bindings.yml`;
see "Worked example: an internal-only project" below, whose commands run as
written.

The last command reported `external channel enforcement passed for 4 binding(s)`
and `validated 11 adapter mappings for 5 labels` on a case-module package with
no adapter changes at all. That is the property that makes the option cheap: a
case module is a new *entry*, never a new *boundary*.

The module resolver follows `EXTENDS` transitively and fails closed on
`INSTANCE` and `LOCAL` (MF-030). **Case modules must use `EXTENDS`.** A module
that instantiates its view is unanalyzable, and the failure is an exit-nonzero
"I could not measure this", not a warning.

### Where a case module may live, and how EXTENDS is resolved (EV-02-DF-02)

**A case module generates from wherever you keep it.** It does not have to sit
beside the view it extends, and it never has to be copied there.

TLC has no `-lib` flag and does not search the current directory: SANY resolves
`EXTENDS` against the directory of the `.tla` it was handed, plus the
`TLA-Library` system property. Generation therefore resolves the whole `EXTENDS`
hierarchy first and hands SANY the directories it found, in this order:

1. the module's own directory — a view sitting beside it always wins;
2. every `--module-path DIR` you passed, in order;
3. **directories beside the module's own that contain `.tla` files.** This is
   what makes the documented layout work with no flag at all: a module in
   `specs/case_modules/` finds a view in `specs/program_model/`. One level,
   never recursive, and a module found in two siblings is an error rather than a
   coin flip — name the one you mean with `--module-path`.

The same path is given to the static complexity/architecture scanner, so the
scan and the corpus can never be reading different files. When anything resolves
outside the module's own directory the run says so before it starts:

```
module search path: .../specs/case_modules, .../specs/program_model
  EXTENDS resolved outside .../specs/case_modules: Pipeline -> .../specs/program_model/Pipeline.tla
```

and a module that cannot be found is one sentence *before* TLC runs, naming the
module, every directory searched, and the flag that fixes it — not a
`tla2sany.semantic.AbortException` thirty lines under a complexity paragraph.

Two consequences of living in a different directory, both handled:

- **the manifest.** `spec_manifest.yaml` belongs to the *view*, not to the case
  module. It is looked up along the same search path, so the `case_modules:`
  declaration, the budgets and the corpus all still describe one project.
- **parameter recovery.** A case module declares no actions — they are all in
  the view — so the MF-029 recipes are built from the whole hierarchy, base
  modules first. Reading only the module's own text recovered arguments for
  nothing and left every case with no argument at all, which the adapters then
  refuse with ``no usable argument for `i```.

### `--out` is resolved against the spec directory

A **relative** `--out` is resolved against the **spec directory** (the `.tla`'s
own directory), not the current directory — unless it already points inside the
spec directory. `--out generated`, run from a repo root, writes
`<spec dir>/generated`, which is rarely what was meant. The rule keeps generated
corpora beside the spec they came from; it is a surprise exactly once, so the
run now prints where the path landed:

```
note: --out generated resolved to .../specs/program_model/generated -- a relative
--out is resolved against the SPEC DIRECTORY (...), not the current directory (...).
Pass an absolute path to control it.
```

**Pass an absolute path when you want cwd-relative behavior.** The worked
example below does.

## Worked example: an internal-only project

Every command in this section was run verbatim on the shipped fixture
`examples/validation/ex4_pipeline_coherent`, whose two case modules live in
`specs/case_modules/` and extend a view in `specs/program_model/`. Nothing is
copied and nothing is edited. The recorded output is
`specs/.history/architectural-coherence-epic/ticket-011-RP-03/ticket/results/internal-view-worked-example.txt`.

This is the shape most projects actually have: one `Pipeline.tla`, every action
`layer: internal`, no External view, no `testgraph_bindings.yml`.

```bash
export REPO=$(git rev-parse --show-toplevel)
cd "$REPO/examples/validation/ex4_pipeline_coherent"
export OUT=$(mktemp -d)          # absolute --out: resolved as given
```

**1 — the action set comes from a command, not from your attention.**

```bash
python3 "$REPO/scripts/tla_spec_dev.py" --spec-root specs analyze complexity \
  specs/program_model/Pipeline.tla specs/program_model/Pipeline.cfg \
  --format json | python3 -c \
  "import json,sys; [print(a['name']) for a in sorted(json.load(sys.stdin)['measured']['actions'], key=lambda a: a['name'])]"
# Accept Deliver Enqueue Fail Record
```

**2 — the view's own corpus. Case modules are additive; this keeps running.**

```bash
PYTHONPATH=$PWD python3 "$REPO/scripts/generate_cases_from_tlc_dump.py" \
  specs/program_model/Pipeline.tla specs/program_model/Pipeline.cfg \
  --out "$OUT" --package Pipeline_cases --view internal \
  --actions-metadata specs/program_model/actions.yml \
  --state-projector specs.program_model.tlc_projection:project_visible_state \
  --output-projector specs.program_model.tlc_projection:project_adapter_output \
  --dedupe projected
# -> 330 cases from 121 states; 330/330 carry recovered arguments
```

**3 — the slice and the Given, generated from `specs/case_modules/` in place.**

```bash
PYTHONPATH=$PWD python3 "$REPO/scripts/generate_cases_from_tlc_dump.py" \
  specs/case_modules/Scenario_DeliveryPath.tla specs/case_modules/Scenario_DeliveryPath.cfg \
  --out "$OUT" --package Scenario_DeliveryPath_cases --view internal \
  --actions-metadata specs/program_model/actions.yml \
  --state-projector specs.program_model.tlc_projection:project_visible_state \
  --output-projector specs.program_model.tlc_projection:project_adapter_output \
  --dedupe projected
# -> 50 cases from 25 states; 50/50 carry recovered arguments

PYTHONPATH=$PWD python3 "$REPO/scripts/generate_cases_from_tlc_dump.py" \
  specs/case_modules/Scenario_RecordAfterDelivery.tla specs/case_modules/Scenario_RecordAfterDelivery.cfg \
  --out "$OUT" --package Scenario_RecordAfterDelivery_cases --view internal \
  --actions-metadata specs/program_model/actions.yml \
  --state-projector specs.program_model.tlc_projection:project_visible_state \
  --output-projector specs.program_model.tlc_projection:project_adapter_output \
  --dedupe projected
# -> 6 cases from 8 states; 6/6 carry recovered arguments
```

**4 — the declaration, and the coverage report over all three corpora.**

```bash
python3 "$REPO/scripts/case_modules.py" validate \
  --manifest specs/program_model/spec_manifest.yaml

python3 "$REPO/scripts/case_modules.py" coverage \
  --manifest specs/program_model/spec_manifest.yaml \
  --actions-metadata specs/program_model/actions.yml --view internal \
  --corpus "$OUT/spec-unit/Scenario_DeliveryPath_cases" \
  --corpus "$OUT/spec-unit/Scenario_RecordAfterDelivery_cases" \
  --corpus "$OUT/spec-unit/Pipeline_cases"
```

```
action   view corpus  Scenario_DeliveryPath  Scenario_RecordAfterDelivery  modules total
-------  -----------  ---------------------  ----------------------------  -------------
Accept   22           10                     0                             10
Deliver  66           20                     0                             20
Enqueue  110          20                     0                             20
Fail     88           0                      4                             4
Record   44           0                      2                             2

UNCOVERED: none -- every view action is entered by a measured module or covered
by the view's own corpus.
```

**5 — run a case-module corpus against the project's existing adapters.** Two
`--import-root`: one for the project, one for the parent of the generated
contract package. This is the whole point of the option — no adapter changed.

```bash
python3 "$REPO/scripts/run_generated_case_adapters.py" \
  "$OUT/spec-unit/Scenario_RecordAfterDelivery_cases" \
  --mapping specs/program_model/case_adapters.toml \
  --spec-dir specs/program_model --view internal --batch \
  --import-root . --import-root ./generated
# validated 5 adapter mappings for 3 labels
# executed 6 cases in batch
```

**6 — the same command on the slice, which now RUNS (CM-F5, closed in HP-04).**
It used to refuse. The run states, unprompted and before its results, which
effect oracle the mapping does not carry on this corpus:

```bash
python3 "$REPO/scripts/run_generated_case_adapters.py" \
  "$OUT/spec-unit/Scenario_DeliveryPath_cases" \
  --mapping specs/program_model/case_adapters.toml \
  --spec-dir specs/program_model --view internal --batch \
  --import-root . --import-root ./generated
# validated 5 adapter mappings for 4 labels
# EFFECT ORACLES **NOT** CARRIED from .../case_adapters.toml: LedgerStorePort.
#   This corpus enters no action that emits on them -- for a case-module SLICE
#   that is a fact about the slice, not a misconfiguration. A green result here
#   is a statement about the ports listed as CARRIED and says NOTHING about the
#   ports listed here; treat its kill count as a FLOOR.
# executed 50 cases in batch
```

No third mapping file, and no edit to the fixture. See CM-F5 below for what the
notice is for.

## Binding an adapter to a PORT, and the fake/real swap (PA-04)

Every binding above binds a case to an **action**. `[ports."<Component>.<Name>"]`
binds one to a **port**, and it is the only table in this file that names two
implementations of the same thing.

```toml
[ports."ledger.LedgerAppendPort"]
adapter = "port_journal_adapters:RealJournalAdapter"   # the REAL adapter
fake    = "port_journal_adapters:FakeJournalAdapter"   # its FAKE
kind    = "ledger-journal-port"
```

The quoted key is the **qualified port name** the manifest declares under
`effects.components.<Component>.ports.<Name>` — the same declaration
`--port-cases` generates a case set from. The runner resolves it to the case
label by calling the generator's own `PortDeclaration`, so a port renamed in the
manifest breaks a test rather than silently orphaning the binding.

### Which binding wins, and why you can see it

A generated port case carries **both** labels: its action's and its port's. The
port binding wins, and the precedence is read off `mapping.binds` — a field the
table sets — not sniffed from the shape of the label and not decided by which
table appears first in the file. Before this existed, which of two matching
bindings drove a port case depended on typing order.

### The swap

```bash
python3 scripts/run_generated_case_adapters.py <corpus> --mapping <toml> --batch --wiring real
python3 scripts/run_generated_case_adapters.py <corpus> --mapping <toml> --batch --wiring fake
```

**The case list is identical across the two.** Only the implementation behind
the port changes. That is the whole instrument, and it exists because of one
measured hole: a fault in a hexagonal arm's in-memory adapter survived five
corpus instruments, the effect oracle **and** the hand-written suite for a full
epic — not because it was subtle, but because no composition point anywhere
wired that adapter, so nothing ran a line of it.

Measured on `examples/validation/ab/reference_ports/`, 1,855 generated port
cases, 1,543 executed, both wirings green on unmutated code:

| mutant | port-swap real | port-swap fake | action-bound real | action-bound fake |
|---|---|---|---|---|
| PA-M11 real adapter drops CLOSE | **KILLED** | SURVIVED | **KILLED** | **KILLED** |
| PA-M12 fake adapter drops CLOSE | SURVIVED | **KILLED** | SURVIVED | SURVIVED |

Read the two right-hand columns first. Without the `[ports.*]` table there is
nothing to swap, so `--wiring fake` runs the real adapter and **PA-M12 is
unreachable by any wiring**. The port binding is the only difference between
that pair of columns and the pair beside it.

A port that declares no `fake` is **reported, never refused**:

```
! PORT ledger.LedgerAppendPort: NO FAKE DECLARED, so --wiring fake ran its REAL
  adapter. This column decides nothing about a fake for this port because there
  is not one.
```

That is a fact about the codebase — a flat module has no second implementation —
and turning it into a refusal would make `--wiring` a gate on how code is shaped.

### Every run says which oracles it carries

Unprompted, before the results, on **every** run — not only the ones with
semantic providers configured, which was backwards: the runs carrying the fewest
oracles were the ones that said nothing.

```
ORACLES CARRIED BY THIS MAPPING:
  + output-conformance: 5 binding(s) return a result this run compares field by field ...
  + port-fake-real-swap on ledger.LedgerAppendPort: THIS RUN USED THE FAKE SIDE. One run
    decides one side of a port; a fault seeded in the other implementation is not on this
    run's executed path at all, so this column must be read beside its opposite wiring ...
ORACLES **NOT** CARRIED:
  - projected-state-conformance: no binding declares a projector ...
  - effect-conformance: this mapping binds no [effect_providers.<Port>] provider, so NO
    DURABLE-WRITE ORACLE is in this run and a kill count from it is a FLOOR
  - mutation-kill-test: never carried by this runner. It is a separate instrument
    (scripts/kill_test.py) and a green run here is not evidence any fault would die
```

**The second half is the load-bearing one.** A green run under a mapping with no
durable-write oracle over-reads, and documentation cannot tell a reader that at
the moment they need to know it.

### What the pair does NOT do

It does not assert the two wirings **agree**. A parity test between a real
adapter and its fake passes when the domain is wrong, because both wirings are
wrong together. Both columns are compared against the model's expected
after-state, which is the standard the hand-written suite holds them to.

And a port column is scoped to its region. `corpus-port` executes 294 accepting
`Reserve` cases and still cannot decide the A/B catalogue's positive control,
because that control's symptom lands on `available` while the port's region is
`{closed, committed, ledger}`. Executability was never the limit; the projection
is. Until a control is seeded **inside** a port's region, every port-scoped
column carries a red positive control and its kill count is a floor
(`PA-03-DF-03`).

## Running the EFFECT ORACLE over a case-module corpus (HP-04)

`run effect-conformance` diffs what an adapter actually did against the ports
the model declares for its action. Until HP-04 it had **never been executed
against this repository's own model**, and running it for the first time found
three defects that four rounds of reading it had not. All three are fixed; the
part that matters when you point it at a case module is what it now REPORTS.

```bash
python3 scripts/tla_spec_dev.py --spec-root specs run effect-conformance \
  --target <spec dir> --cases-dir <corpus> --out <report.json>
```

**It loads the project's own adapters.** `case_adapters.toml` — the file
`tla-spec-dev scaffold` writes — names adapters as bare module paths
(`production_adapters:OpenTicketAdapter`). The oracle puts the target spec
directory, the current directory and the toolchain root on `sys.path`, the same
set the enforcing runner gets on `PYTHONPATH`. No `PYTHONPATH=` prefix is
needed, and one being needed used to be the reason nobody could tell whether the
oracle or their project was broken.

**An adapter it cannot drive is SKIPPED and NAMED.** It never aborts the run —
that is a report, not a refusal. Three kinds, kept distinct because they mean
different things:

| kind | what it means |
|---|---|
| `not-runnable` | the adapter implements `apply()` and no `run(case, work_dir)`, so no case can drive it. A fact about the **adapter**. |
| `declined` | the adapter has a `run` and its own `can_run`/`validate` refused this input. A fact about the **case** — usually an argument the corpus could not recover. |
| `unbound` | the mapping binds no adapter for the case's action. A fact about the **mapping**. |

The report answers "how many actions can this oracle see?" from the run rather
than from the source:

```
ADAPTER REACH: 8 of 18 action(s) in this corpus EXECUTED; 10 SKIPPED.
```

and a declared port whose every declaring action was skipped is reported as
`UNEXERCISED PORT (NOT proven dead)` rather than as dead surface. On this
repository's own model that distinction moved **7 of 9** reported dead ports out
of the "dead" column: they were never dead, nothing had ever been in a position
to exercise them.

**Two runs over an identical corpus produce an identical report.** The
per-case work directory is emptied before each case. Before HP-04 it persisted,
so an adapter that materializes its own before-state wrote a file on a cold run
and found it already present on a warm one: the gap count was **20 / 15 / 14**
across three runs of the same corpus on the same tree. Any claim resting on that
number was unciteable. If you pass `--work-dir`, only the per-case
subdirectories are reset; the directory you named and anything else in it is
left alone.

## Known frictions (measured in the probe, filed as CM-F1..F5)

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
- **CM-F5 — a slice narrower than the view orphans the view's effect providers.
  CLOSED in HP-04. Measured in RP-03, sharpened by EV-03-DF-02.**
  `run_generated_case_adapters.py` used to REFUSE a mapping that configures a
  semantic effect provider no *selected* case requires: `provider configured for
  semantic effect port(s) not required by any selected case: LedgerStorePort`.
  On a **slice** that is not a misconfiguration, it is the definition of a
  slice: the ex4 `Scenario_DeliveryPath` slice deliberately excludes `Record`,
  the only action that touches `LedgerStorePort`.

  How bad it was, measured rather than estimated: **both** mappings the ex4
  fixture ships bind a `LedgerStorePort` provider, so the fixture had **zero
  working configurations for its own slice**, and the documented workaround
  needed a third mapping file that existed nowhere in the repository. A round-2
  blind agent lost 3 of its 15 actions to it and had to author that file.

  HP-04 makes the orphan a **report**, never a refusal (the epic's
  `no_new_gates_rule`). The slice runs against the mapping the project already
  ships. Nothing is silently dropped: every run with semantic providers prints
  which oracles it CARRIES — port and provider reference, so a silent provider
  and a content-asserting one can be told apart — and which it does **NOT**,
  with the instruction to read its kill count as a floor. That second half is
  the important one, and it is in the run output rather than only here for a
  measured reason: the same blind agent that authored the third mapping observed
  that the mapping it wrote was a **strictly weaker instrument** with no
  durable-write oracle, so a green slice run OVER-READS. Documentation cannot
  reach a reader at the moment they need that; the run can.

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
set the project runs, and a module in `specs/case_modules/` generates from
there, in place (see "Where a case module may live"). The manifest is found
along the same module search path, so it is the *view's* manifest that governs
the case module's declaration, budgets and coverage record.

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

(That is the **external** shape. For an internal view the packages are under
`<out>/spec-unit/` and the flag is `--view internal` — see the worked example.)

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

**That requirement is not enforceable by a program, and the prompt now says so
where it states it.** The `Source` column is free text checked against nothing;
an eval agent following the prompt produced a complete, schema-valid,
coverage-clean decomposition with no author in the loop and had to flag its own
violation (EV-02-DF-04). Everything downstream of the grouping is measured —
the action set, the schema, per-action coverage — and the grouping itself is
measured by nobody. Treat an undeclared or self-declared `Source` as an
**unreviewed** decomposition, not a validated one.

## What is still not mechanized

There is no scaffold template for the shape and no CLI subcommand under
`tla-spec-dev`. Templating the shape before it has eval coverage would invite
projects to slice by default, which is the degenerate path in "Integrity" above:
case modules are **additive** to a view's corpus, never a replacement for it.
Cross-aspect interleaving (rule 4) is not measured by anything and cannot be —
only a whole-view run produces it, and the report says so every time it runs.
