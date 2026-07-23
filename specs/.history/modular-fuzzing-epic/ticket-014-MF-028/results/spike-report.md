# MF-028 — Spike: make one adapter execute one generated case

**Investigation ticket. The deliverable is a measured answer, not a feature.**

Epic tip measured against: `c2239a6`. Corpus: 57,617 generated cases.
Evidence in this directory: `case-execution-run.txt` (runner output),
`case-execution-projection.txt` (field-by-field comparison + negative
controls), `tlc.txt`, `pytest.txt`, `spec-unit.txt`, `graph-*.txt`.

---

## 0. Headline

**One case runs. It is not the hard part, and the hard part is not what the
ticket predicted.**

The ticket assumed before-state materialization would be the dominant cost —
"for a CLI whose state is a filesystem tree plus a manifest, materializing a
specified before-state means constructing a repository already in that state."
That turned out to be **cheap and almost entirely shared**, for a reason
specific to this model: `setup_phase` and `ticket_state` are **ordinals**, not
free-form state. A before-state is a *prefix of a command sequence*, not an
arbitrary tree. Replaying a prefix is ~40 shared lines and no adapter
contributes anything adapter-specific to it.

Three other things, none of them anticipated in the ticket, are the real cost:

1. **Generated cases carry no action parameters.** All 57,617 cases have
   `params={}`. Every argument to every parameterized action is lost.
2. **Two modelled actions have no adapter at all**, which blocks **72.5%** of
   the corpus, not by difficulty but by absence.
3. **Most adapters' `apply()` is not one transition.** Several are multi-branch
   conformance batteries; two close a ticket *twice* to assert accumulation.
   A `run(case)` shim over those is not possible without splitting them.

The honest cost is therefore **not** "16 × the cost of the one I did."

---

## 1. One adapter, one generated case, executed end to end

### Which adapter, and why

**`ScaffoldProjectAdapter`** is the measured case. It is the simplest adapter
whose before-state is **non-vacuous** and whose action **mutates persistent
state**:

- before-state `setup_phase=2` is a real prefix, so materialization is actually
  exercised rather than skipped;
- the action writes a `program_model` tree, so the after-state is recoverable
  from the **filesystem** rather than merely asserted on stdout;
- it changes exactly two observable variables, so a mismatch localizes.

Everything cheaper — `BuildSkillCli`, `InstallLocalCli`, `ValidateTestGraphCli`
— has an **empty before-state and no persistent effect**, and therefore cannot
measure the thing the ticket asked about.

`BuildSkillCliAdapter` is included as well, explicitly as the **floor** of the
difficulty scale, not as a representative sample.

### Actual command output

```
$ python3 scripts/run_generated_case_adapters.py <corpus> \
    --mapping specs/tickets/MF-028/results/spike_case_adapters.toml \
    --import-root specs/tickets/MF-028/current \
    --case case_0005_scaffold_project --case case_0001_build_skill_cli --batch

validated 16 adapter mappings for 15 labels
executed 2 cases in batch
exit=0
```

This is the real runner (`run_generated_case_adapters.py`) driving real
generated cases through `run(case, work_dir)` — not a unit test standing in for
a run.

### What was actually compared

For `case_0005_scaffold_project` (full detail in
`case-execution-projection.txt`):

| | |
|---|---|
| **CHECKED (9)** | `complexity_gate`, `corpus_gate`, `effect_conformance`, `kill_test`, `lastCommand`, `result.accepted`, `result.reason`, `setup_phase`, `ticket_state` |
| **UNCHECKED (2)** | `result.next`, `spec_root` |
| **MISMATCH (0)** | — |

`setup_phase: 3` was **derived from the real filesystem** (a `program_model`
tree containing `.tla` files exists; no negotiated budgets block; no
`current/`), not copied from the case.

### Negative controls — because a green run alone proves nothing

MF-016 nearly shipped a spurious perfect kill rate. Three deliberately
corrupted after-states were run; all three were rejected:

```
REJECTED setup_phase: setup_phase: expected 4, observed 3
REJECTED ticket_state: ticket_state: expected {'cli_entrypoint': 2}, observed {'cli_entrypoint': 0}
REJECTED result.accepted: result.accepted: expected False, observed True
```

**The negative control caught a defect in this spike's own adapter.** A fourth
control — corrupting `spec_root` — **passed when it should have failed**. Cause:
the first draft defaulted the CLI's spec root to `case.after["spec_root"]`,
reading the expected answer out of the case and echoing it back as an
observation. That made the `spec_root` check a tautology. It is now declared
**UNCHECKED** rather than faked. See §3.1.

---

## 2. What it actually took

### 2.1 Before-state materialization — cheap, and ~100% shared

`materialize_before(case, work_dir)` is ~40 lines and lives at module scope, not
on any adapter. Every adapter in the setup segment can call it unchanged.

It is cheap for a structural reason worth stating plainly:

- **`setup_phase` is an ordinal over a fixed 5-step pipeline.** Materializing
  "setup_phase = N" is replaying `SETUP_PIPELINE[:N]`. There is no arbitrary
  filesystem content to construct.
- **Phases 0→2 materialize to an empty directory.** `BuildSkillCli` and
  `InstallLocalCli` concern the *tla-spec-dev checkout itself*, which is already
  built in any working tree. They cost literally nothing.
- **Phases 3→5 are the CLI's own scaffold commands** — which the adapters were
  *already* calling by hand. `prepare_ticket_workflow()` at
  `specs/current/production_adapters.py` is precisely a hardcoded prefix replay.

**The machinery already existed. It was just parameterized by a constant
instead of by `case.before`.** That is the single most reusable finding here.

One place the replay stops being a pure command sequence: **`RecordBudgets` has
no corresponding CLI command.** The model has it as its own transition; the
shipped CLI emits the budgets block as part of `scaffold project` and expects an
agent to negotiate values. Replaying it is an in-place manifest edit
(`_negotiate_budgets`). Expect more of these where the model and CLI disagree
about transition granularity.

### 2.2 Projection — the half that does not come for free

`project_state()` reads the repository back into the nine model variables.

- `setup_phase`, `spec_root`: **~10 lines of directory evidence.** Shared.
- The four gate variables: read from results artifacts. For setup-segment
  actions they are carried from `case.before` **because the TLA+ action lists
  them `UNCHANGED`.** Carrying an UNCHANGED variable is sound; carrying a
  CHANGED one would be fabrication, and the changed-set is asserted instead.
- `ticket_state`: **not implemented.** See §3.2.
- `lastCommand` / `result`: **not recoverable from any filesystem.** Two
  different command histories leave byte-identical trees. The complexity
  analyzer independently flagged exactly this pair ("no configured invariant
  reads `[lastCommand, result]`"). They are observed from the invocation the
  adapter actually performed — the command it ran, and that command's exit
  status — never copied from `case.after`.
- `result.next` is genuinely unobservable: the CLI prints a prose `next:` block,
  not the model's token. Comparing it would mean re-encoding the spec inside the
  adapter. Declared UNCHECKED.

### 2.3 A real gap in the runner, shared by all fifteen

`spec_double_compiler/runtime.py::assert_case_result` compares `result.after` to
`case.after` with `==` **over the whole dict**. There is no way to express "this
field is not observable."

Returning a whole-dict `after` therefore forces a choice between failing forever
on `result.next`, or copying it out of the case so it agrees — **and the second
is fabrication**. This spike routed the comparison through the adapter
(`compare_projection` / `enforce_projection`) and reports unchecked fields by
name.

**Every remaining adapter hits this.** It should be fixed in the runner once,
not worked around sixteen times. It is the strongest argument for a shared base
class.

### 2.4 What is shared vs adapter-specific — measured, not estimated

| Concern | Lines | Shared? |
|---|---|---|
| `materialize_before` + `SETUP_PIPELINE` + `_negotiate_budgets` | ~55 | **Fully shared** |
| `project_state` (setup segment) | ~35 | **Fully shared** |
| `compare_projection` + `enforce_projection` + `UNPROJECTABLE_FIELDS` | ~55 | **Fully shared** |
| `ScaffoldProjectAdapter.run` + `can_run` | ~30 | Adapter-specific |
| `BuildSkillCliAdapter.run` + `can_run` | ~28 | Adapter-specific |

**~145 shared lines, ~29 per adapter** — *for the setup segment only*. Do not
extrapolate that per-adapter figure across all sixteen; §3 explains why.

### 2.5 What blocked the run before it could start

The runner's coverage gate is **whole-corpus**: it refuses to execute *anything*
until *every* label in the corpus has a binding. Running one case required
clearing five unbound labels:

- `RunEffectConformance`, `RunKillTest` — adapters exist, bindings absent.
- `Stutter` — no adapter at the epic tip.
- `UpdateTicketDesired`, `UpdateTicketCurrent` — **no adapter anywhere.**

Bindings were added in `spike_case_adapters.toml` **in this evidence directory,
not in the production mapping**, because production bindings are MF-023's
surface (open PR #50) and this spike must not duplicate or pre-empt them.

**This is an ordering finding.** `StutterAdapter` here is spike scaffolding and
should be **deleted in favour of PR #50's version**, not merged alongside it.
MF-028 and MF-023 are more entangled than the plan reflects: the spike could not
reach its measurement without touching bindings and stuttering, both of which
MF-023 owns.

---

## 3. Three findings that change the scope more than the code does

### 3.1 Generated cases carry no action parameters — all 57,617 of them

`ScaffoldProject(root)` is parameterized. Its case carries `params={}`. So does
every other case in the corpus:

```
distinct params values across 57617 cases:
  '{}' -> 57617
```

The generator recovers action arguments from a `lastInternalAction` marker
variable (`generate_cases_from_tlc_dump.py:360`). **This model declares no such
variable**, so every argument to every parameterized action is lost:
`ScaffoldProject(root)`, `RecordBudgets(root)`, `OpenTicket(t)`,
`CloseTicket(t)`, and more.

Consequences, in order of severity:

1. An adapter cannot know which argument the model chose, so it **guesses**.
2. Any state variable *set from that argument* becomes **untestable** — the
   adapter would be checking its own guess.
3. The tempting fix — read it from `case.after` — is a **tautology**, and it
   silently passes corruption tests. This spike wrote that bug and caught it
   only via a negative control.

**This is not adapter work.** No amount of adapter effort fixes it. Either the
spec grows an action-marker variable (raising the state space — note the binding
gate `max_state_space_bound` is already at 70%), or parameterized actions accept
permanently reduced conformance. **This deserves its own ticket and should be
decided before the remaining adapters are scoped**, because it determines
whether that work buys real signal or theatre.

### 3.2 Two modelled actions have no adapter — blocking 72.5% of the corpus

`UpdateTicketDesired` and `UpdateTicketCurrent` (699 cases each) have **no
adapter class anywhere in the repository**. They are not "adapters missing
`run()`"; they were never covered at all, and no gate noticed because nothing
ever drove the corpus.

They are how `ticket_state` advances. Without them, no before-state with
`ticket_state > 0` can be replayed:

```
total cases: 57617
before-state in SETUP segment (ticket_state all 0)  :  15855  (27.5%)
before-state in TICKET segment (some ticket_state>0):  41762  (72.5%)
```

`materialize_before` **raises `BeforeStateUnreachable`** for those rather than
running against a wrong repository and reporting a conformance verdict about a
state the case never described.

They are bound to **refusing stubs** (`_UnimplementedActionAdapter`) purely to
clear the coverage gate. A stub returning success would manufacture exactly the
false signal this ticket exists to eliminate.

### 3.2b The effect oracle moves — and then refuses, for a structural reason

Running the two executable cases with `--effect-report` (evidence:
`effect-conformance.json`):

```
effect conformance unobservable: 6 observed effect(s) over 2 case(s),
  5 declared port(s), 3 gap(s), 5 dead port(s), 1 unobservable target(s)
```

**Making an adapter case-executable DID move oracle 3** — from MF-023's *0
observed effects over 40 cases* to **6 observed effects over 2 cases**. Case
execution is genuinely the root cause of the silence, exactly as the ticket
said.

**But the verdict is `unobservable`, not `clean`, and more `run()` will not
change that:**

```
UNOBSERVABLE BOUNDARY: process '... scripts/tla_spec_dev.py --spec-root specs
  scaffold project --name CliProject' -- a child process was spawned; the
  sandbox records the spawn but observes nothing the child does -- its writes,
  deletes and connections are invisible to this run
```

**Every adapter in this repository drives the CLI through `subprocess.run`.**
The effect sandbox observes the in-process CPython runtime only. So *every*
adapter is structurally invisible to oracle 3, and will remain so after all
sixteen have `run()`. MF-027 made this refusal explicit rather than silent, and
it is refusing correctly here.

Two further specifics worth a ticket each:

- **All 5 declared ports are dead**, and the observed writes are *undeclared*.
  The ports glob `**/specs/**`, `**/results/**`, `**/.venv/**`; the adapters
  work in temp directories, which match nothing. The port declarations describe
  where the CLI writes *in a real repository*, not where the adapters exercise
  it. Even in-process adapters would report dead ports until this is reconciled.
- Fixing this means **adapters calling the CLI in-process** (importing
  `tla_spec_dev` and invoking its entrypoint) rather than shelling out — a
  change to every adapter, and a different axis of work from `run()`.

**Scoping consequence: `run()` alone does not restore oracle 3.** Any plan that
assumes "adapters get `run()`, therefore effect conformance goes green" is
wrong. The two are independent, and this second axis was not in the ticket.

### 3.3 Sixteen adapters cover thirteen labels; eleven are bound

| | |
|---|---|
| Adapter classes | 16 |
| Distinct `action_name`s | 13 |
| Production bindings | 11 |
| Corpus action labels | 15 |

- **Three adapters share `action_name = "CloseTicket"`**
  (`ClosePromotionPreservesCurrent`, `SkillFeedbackCloseOut`,
  `ComplexityLedgerCloseOut`). The mapping is one-label-to-one-adapter, so
  **two of the three are unreachable from the corpus by construction**, no
  matter what `run()` they grow.
- **`ValidateTestGraphCli` is bound but never appears in the corpus** — a dead
  binding.

So "make sixteen adapters executable" is not the right frame. The reachable
surface is **eleven labels**, and three adapters need a *different* mechanism
(multiple adapters per label) before `run()` means anything for them.

---

## 4. Per-adapter difficulty bands for the remaining fifteen

Discriminator: **does `apply()` correspond to one model transition?** Where it
runs a battery of scenarios and aggregates booleans, no shim exists.

Confidence is stated per row. **Bands 1–2 are measured by analogy to the case I
ran; bands 3–4 are read off the code and are less certain.**

### TRIVIAL — a genuine `run()` shim over `apply()`

| # | Adapter | Reason | Confidence |
|---|---|---|---|
| 1 | `TestGraphCliAdapter` | No target repo, no before-state, reads shipped repo files. **But its label never appears in the corpus** — trivial *and* pointless until that is resolved. | High |
| 2 | `InstallLocalCliAdapter` | Before-state = phase 1 (empty dir). One shim; needs `bin_dir`/`cache_dir` from `work_dir`. Sets no observable variable beyond `setup_phase`. | High |

### MODERATE — one transition, but real projection work

| # | Adapter | Reason | Confidence |
|---|---|---|---|
| 3 | `ScaffoldWorkflowAdapter` | Before = phase 4 (replayed, shared). 5 CLI invocations inside `apply()` must be split so only the modelled one is the transition. | High |
| 4 | `RecordBudgetsAdapter` | **No CLI command corresponds to this transition** (§2.1). Projection must detect "negotiated" in the manifest. Parameterized → hit by §3.1. | High |
| 5 | `OpenTicketAdapter` | First adapter needing **`ticket_state` projection**, which this spike did not build. Parameterized by ticket → hit by §3.1. | Medium |
| 6 | `RunSpecUnitTestsAdapter` | Before-state needs `ticket_state = 3`, i.e. the ticket segment — **blocked by §3.2** until the two missing adapters exist. | Medium |

### HARD — `apply()` is not one transition

| # | Adapter | Reason | Confidence |
|---|---|---|---|
| 7 | `AnalyzeComplexityAdapter` | `apply()` asserts **both sides of a gate plus the override** in one call — at minimum three transitions. Must be split before `run()` is meaningful. | High |
| 8 | `AnalyzeCorpusAdapter` | Same shape; 15 aggregated result keys. Also implicated in the `analyze corpus` OOM (FINDING 6, out of scope). | Medium |
| 9 | `RunEffectConformanceAdapter` | Drives an oracle whose before-state requires `corpus_gate` measured — deep in the ticket segment. Multi-branch. | Medium |
| 10 | `RunKillTestAdapter` | 218 lines, 23 result keys, builds 4+ fixture spec trees, asserts three independent properties. **A single case cannot express it.** | High |
| 11 | `CloseTicketAdapter` | Before-state requires a fully advanced ticket — **unreachable while §3.2 stands**. Parameterized → §3.1. | High |

### BLOCKED — not a difficulty, a structural impossibility

| # | Adapter | Reason | Confidence |
|---|---|---|---|
| 12 | `ClosePromotionPreservesCurrentAdapter` | Duplicate `action_name = "CloseTicket"`; **unreachable via one-label-to-one-adapter binding** (§3.3). | High |
| 13 | `SkillFeedbackCloseOutAdapter` | Duplicate label, **and** closes a workflow **twice** to assert accumulation across closes. Not a transition property at all. | High |
| 14 | `ComplexityLedgerCloseOutAdapter` | Duplicate label; multi-close ledger assertions. | High |
| 15 | `UpdateTicketDesired` / `UpdateTicketCurrent` | **No adapter exists.** Not in the fifteen — these are new work, and they gate 72.5% of the corpus. | High |

**Where I am least confident:** rows 8 and 9. Both are entangled with
out-of-scope findings (the `analyze corpus` OOM; effect-oracle port
declarations), so I could not exercise them far enough to distinguish "hard" from
"blocked". I have banded them hard rather than blocked because I could not prove
blocked, and optimism there would be the wrong error.

---

## 5. Recommendation on shape

**A `run()` shim over `apply()` works for exactly two adapters and is the wrong
frame for the rest.** Recommended, in dependency order:

### 5.1 First, decide the parameter question (§3.1) — before scoping adapter work

Whether generated cases can carry action arguments determines whether adapter
work buys real conformance signal or a tautology. It is a **spec/generator**
question, not adapter work, and it is cheap to decide and expensive to discover
late. **Nothing else should be scoped before it.**

### 5.2 Fix the runner's all-or-nothing comparison once (§2.3)

Teach `assert_case_result` about unobservable fields — a per-binding
`unobservable = [...]` list, with the runner reporting them as UNCHECKED. This
is one change in `runtime.py` that removes a workaround from all fifteen
adapters, and it removes the standing temptation to fabricate agreement.

### 5.3 A shared before-state builder + projector — **yes, and it is small**

`materialize_before` / `project_state` / `compare_projection` (~145 lines) are
already shared and adapter-agnostic. Promote them to a **module or mixin, not a
base class** — the adapters have incompatible `apply()` signatures
(`apply()`, `apply(bin_dir, cache_dir)`, `apply(target_repo, *, ...)`), so
inheritance would fight them. This is the cheapest, highest-leverage piece.

### 5.4 Write the two missing adapters (§3.2) — highest value per unit effort

`UpdateTicketDesired` and `UpdateTicketCurrent` gate **72.5%** of the corpus.
They are ordinary CLI-driving adapters of the `ScaffoldProject` shape. **Nothing
else unlocks comparable coverage.** This should be the first implementation
ticket after §5.1 and §5.2.

### 5.5 Split the battery adapters — a rewrite, not a shim

Rows 7–10 and 12–14 have `apply()` methods that assert several scenarios at
once. They are **good conformance tests and bad case executors**, and they
should stay as they are.

Recommended: **keep `apply()` as the spec-unit test, and add a separate,
narrower `run()`** that performs one transition. Do not try to make one method
serve both. The existing tests are the epic's accumulated defect knowledge (each
carries a docstring explaining the defect it prevents) and rewriting them into
single-transition form would destroy that.

### 5.6 Allow multiple adapters per label, or accept three dead adapters (§3.3)

The three `CloseTicket` adapters cannot all be reachable under one-label-to-one-
adapter binding. Either the mapping grows a list form, or those three are
explicitly recorded as spec-unit-only and never counted as case-executable.
Either is fine; **silence is not** — today they look executable and are not.

---

## 6. Honest cost estimate

**"Make sixteen adapters execute cases" is not the shape of the remaining
work.** A defensible decomposition:

| Work | Size | Note |
|---|---|---|
| Decide action-parameter representation (§5.1) | **Design ticket** | Blocks everything; determines whether the rest buys signal |
| Runner unobservable-field support (§5.2) | **Small** | One file; removes a workaround ×15 |
| Promote shared builder/projector (§5.3) | **Small** | ~145 lines already written and exercised |
| Two missing adapters (§5.4) | **Medium** | Unlocks 72.5% of the corpus |
| In-process CLI invocation (§3.2b) | **Large** | Independent axis; oracle 3 stays `unobservable` without it |
| Reconcile port globs with adapter work dirs (§3.2b) | **Small** | All 5 ports dead today |
| Trivial band, 2 adapters (§4) | **Small** | Genuine shims |
| Moderate band, 4 adapters (§4) | **Medium each** | Gated on §5.4 for two of them |
| Hard band, 5 adapters (§4) | **Large each** | Split-and-rewrite, not shim |
| Label-collision decision (§5.6) | **Design ticket** | Or record 3 adapters as unreachable |

**The number the ticket asked for:** the one adapter I made case-executable cost
~29 adapter-specific lines on top of ~145 shared lines. **That figure does not
generalize.** It holds for the trivial band (2 adapters), roughly holds for the
moderate band (4), and **does not apply at all** to the hard band (5) or the
blocked set (4), where the obstruction is structural rather than volumetric.

Extrapolating the measured case across all sixteen would predict a small,
uniform task. **That prediction would be wrong**, which is precisely why this was
spiked before five or six tickets were scoped against a guess.

### What this means for MF-023

MF-023 is blocked by this ticket, and the dependency is **deeper than the plan
reflects**. Running a single case required Stutter handling and
`case_adapters.toml` bindings, both of which live on MF-023's open PR #50. And
three of the four oracles will remain unusable until §5.1, §5.2 and §5.4 land —
not merely until "adapters have `run()`". **MF-023 should not be scheduled on
the assumption that MF-028 unblocks it.** It does not; it identifies what would.

Concretely, oracle 3 was measured here and it **moved but did not recover**
(§3.2b): 0 observed effects became 6, and the verdict is still `unobservable`
because every adapter shells out. Restoring it needs in-process CLI invocation
across all sixteen adapters — an axis of work absent from the current plan.
