# Complexity Intuition: Reading A Descriptor

Take this complexity descriptor to consider how to refactor complexity out of
the app. That sentence is the whole workflow: `analyze complexity` prints
facts about a model, and this document teaches an agent to read those facts
and form a judgment about whether and how to refactor. The descriptor is
**refactoring input** — evidence you carry into a design conversation — not a
verdict and not a to-do list.

Everything here is **intuition for the agent to judge with, never an
automated move**. The tool prescribes nothing. CD-01 deliberately removed the
scanner's suggested-move output after validation showed it confidently wrong
on standard TLA+ (an aliased invariant made it recommend projecting away
every variable). The descriptor now states only what it measured; the
diagnosis is made by a person, or an agent using this document, from the
facts — and any resulting move is a recommendation the user approves,
adjusts, or vetoes (`references/architecture_tractability.md`,
"Recommendations, Never Verdicts"). Nothing in this document is a rule the
scanner enforces; none of it blocks promotion. Complexity is a scanner, not a
gate.

Every descriptor excerpt below is real `analyze complexity` output, produced
by running the shipped scanner against a checkable model (commands recorded
with each example). None of the shapes are invented.

## How Complex Should A Program Be?

**Complexity should be proportional to the essential behavior the program
must exhibit.** That is the entire best practice, and both directions of it
matter:

- A program whose model has a large bound because its *behavior* genuinely
  has many distinguishable situations — many protocol states an invariant
  distinguishes, many independent actors, many real modes — is not too
  complex. It is the size of its job. The descriptor will show the bound
  concentrated in dimensions that invariants actually read, domains whose
  every value some guard or invariant treats differently, and a matrix whose
  density follows the real coupling of the domain.
- A program whose bound is large because of *representation* — counters
  wider than the distinctions the behavior makes, bookkeeping variables
  written by every action, state that no invariant constrains — is carrying
  accidental complexity. The behavior did not grow; the state did.

The test for "essential" is always the same question: **which distinctions
does the behavior actually make?** If the program behaves differently at
retry 0, retry 1..N-1, and retry N, the essential domain has three values —
however wide the production counter is. If no invariant, guard, or observable
effect distinguishes two states, the distinction between them is
representation, not behavior.

**A validated architectural refactor that lowers complexity is encouraged as
normal practice, not an exceptional event.** The standing objective of this
workflow is reducing program complexity while retaining every behavior
(SKILL.md, "Complexity Budgets Are Advisory"), and the refinement loop in
`references/architecture_tractability.md` runs on every ticket, not only
when a warning fires. "Validated" is load-bearing and means all of:

1. the model stays **green under TLC** and the repository tests stay green;
2. **behavior is preserved** — every distinction and invariant the old model
   enforced is still enforced (or its removal is explicitly agreed with the
   user as a behavior change, which is a different kind of ticket);
3. **before/after descriptors are compared** and the delta is reported
   jointly with the behavior-retention evidence from the same run. A bound
   that fell because behavior was dropped is gaming the metric, not a
   refactor.

Production-code refactors additionally always require explicit user approval
before they begin (`references/architecture_tractability.md`, "Move 3").
Representation-only refactors (remodeling the same program) still get their
before/after comparison recorded as ticket evidence. Worked example 4 below
shows the full pattern.

The inverse rule also holds: complexity going **up** is acceptable exactly
when a new essential behavior arrived, and the increase should be justified
by naming that behavior (the recursive refinement loop, step 2). Growth
without a nameable behavior is drift.

## What A Good Descriptor Looks Like

Section by section of the real output:

- **Dimension table** — every variable has a resolved domain; cardinalities
  match the distinctions the behavior makes (a 3-value status where the
  program has 3 statuses, not `0..255` where the program cares
  changed/unchanged). No `(unconstrained) unknown` rows, or only ones you
  can explain (see "honest unknowns" below).
- **State-space upper bound** — proportional to the essential behavior; the
  dominant dimensions are the ones the program is *about*. No `excluded (no
  resolvable domain)` line silently shrinking the bound.
- **R/W matrix** — balanced: most cells `.`, each variable written by few
  actions (single-writer is the ideal), reads clustered near the writes.
  Band or block structure visible by eye.
- **Near-decomposability** — clusters that correspond to subsystems you can
  name, with few port-crossing actions, each crossing a real transaction
  between subsystems. A high modularity Q confirms block structure, but a
  low Q is not automatically bad — see the pipeline nuance in example 2.
- **Dense rows and columns** — none, or a short list you can defend
  (an irreducibly central protocol variable in a small core).
- **Invariant coverage** — `every variable is read by at least one
  configured invariant`: every dimension of state is load-bearing for some
  property. A variable no invariant reads is state the verification cannot
  see.
- **Justification linkage** — every variable carries a recorded reason to
  exist, so dead weight is auditable.
- **Thresholds** — `No complexity warnings` is pleasant but not the point;
  the warnings are advisory either way. A good descriptor can carry
  warnings (a genuinely large domain), and a bad one can be warning-free
  (small but shapeless).

**Honest unknowns.** `unknown` in the bound column is the scanner refusing
to guess — never a silent 1. Some unknowns are deliberate: this repository's
own model leaves `lastCommand`/`result` unconstrained as an observability
channel (see example 5). The intuition is not "no unknowns ever"; it is
"every unknown has an owner-known reason, and you remember the printed bound
excludes it."

## What A Bad Descriptor Looks Like

- **God-state / dense rows** — one or more variables touched by more than
  half the actions, especially *written* by nearly all of them. The dense-row
  list names them. Bookkeeping smeared across every action (a log, a cache
  epoch, a status mirror) is the classic signature.
- **Dense columns** — actions that touch most of the variables: transactions
  doing several subsystems' work in one step, or effects (logging, cache
  bumps) threaded through every action.
- **Low modularity with a dense matrix** — one cluster containing
  everything, `no port-crossing actions (single component)`: no cut exists
  because everything reads and writes everything.
- **Bound exploding past the behavior** — dominant dimensions that are
  representation, not behavior: a `0..100` retry counter where behavior has
  three retry situations, an epoch counter contributing 256x for a
  changed/unchanged distinction. Symptom at check time: TLC generates
  millions of states without finishing, states differing only in dimensions
  no invariant reads.
- **Unexplained unknowns** — `(unconstrained)` rows nobody can account for,
  which also mean the printed bound *understates* the model.
- **Coverage gaps** — variables no configured invariant reads: state that
  exists but that no property depends on. Paired with a dense row, that is
  weight with no verification value.
- **Domains wider than needed** — cardinalities out of proportion to the
  distinctions guards and invariants actually make.

A bad descriptor is still **not a failure**: the scanner exits 0, promotion
is not blocked, and some pieces genuinely need their shape (performance
paths, protocol-mandated shapes, irreducible domain complexity — the
descriptor says so in its own trailer). A bad shape is a *finding to bring
to the user*, with the descriptor as evidence.

## Worked Examples

The models are small on purpose — small enough to run TLC to completion in
seconds — and every descriptor excerpt is verbatim scanner output from:

```bash
python3 scripts/tla_spec_dev.py --spec-root specs analyze complexity <model>.tla <MC.cfg>
bash scripts/run_tlc.sh <model>.tla <MC.cfg>   # wrapped in a 120s external timeout
```

The excerpts in examples 1–4 were recorded at CD-02 with the CD-01 scanner
against scratch models (provenance:
`specs/.history/complexity-descriptor-epic/ticket-001-CD-02/results/intuition_doc_review.md`).
The shipped scanner has since grown a per-variable `source` column in the
dimension table, an action-attribution line above the R/W matrix, and footer
notes (CD-05/CD-06), so a fresh run prints slightly richer output around the
same kinds of measurement; example 5 is recorded against the current tree with
the current scanner.

### Example 1 — GOOD: two subsystems, one port (`Shop`)

A shop with an inventory subsystem (`stock_level`, `reorder_open`,
`supplier_ack`; actions `OpenReorder`, `AckReorder`, `Restock`) and a
checkout subsystem (`cart`, `checkout_phase`, `receipt_issued`; actions
`AddToCart`, `StartCheckout`, `IssueReceipt`), joined by one transaction,
`CompletePurchase`, which decrements stock for carted items. Real output:

```text
[MEASURED] State-space upper bound
  bound = 3,456  (product of 6 bounded dimensions; domains from TypeInvariant)

[MEASURED] Variables x actions read/write matrix
variable        OpenReorder  AckReorder  Restock  AddToCart  StartCheckout  CompletePurchase  IssueReceipt
--------------  -----------  ----------  -------  ---------  -------------  ----------------  ------------
stock_level     r            .           rw       .          .              rw                .
reorder_open    rw           r           rw       .          .              .                 .
supplier_ack    .            rw          rw       .          .              .                 .
cart            .            .           .        rw         r              rw                .
checkout_phase  .            .           .        r          rw             rw                r
receipt_issued  .            .           .        .          .              .                 rw

[MEASURED] Near-decomposability
  graph modularity Q = 0.314 over the variable interaction graph
  C1: cart, checkout_phase, receipt_issued  (3 variables, 4 actions)
  C2: reorder_open, stock_level, supplier_ack  (3 variables, 4 actions)
  candidate port-crossing actions:
    CompletePurchase crosses C1, C2

[MEASURED] Invariant coverage (aliased/composed invariants resolved transitively)
  every variable is read by at least one configured invariant.

  No complexity warnings -- every metric is within its advisory threshold.
```

Why this is good, in the descriptor's own terms:

- The matrix is two visible blocks with one bridging column. The clusters
  the scanner found are the subsystems the design intended — you can *name*
  C1 ("checkout") and C2 ("inventory") without looking at the code.
- Exactly one port-crossing action, and it is the real business transaction.
  If this model ever needed decomposing for tractability, the cut is already
  drawn: contract environments at `CompletePurchase`.
- Every variable is read by some invariant: all state is load-bearing.
- Bound 3,456 for a shop with reordering and checkout over two items is
  proportional; no dimension is carrying representation weight. TLC (with
  `CHECK_DEADLOCK FALSE`; terminal states are fine here) completes
  instantly: 13 distinct reachable states — reachability far below the
  bound, because guards like "restock only after ack" prune hard. A bound
  is a product over declared domains, not a reachability count; a big gap
  between them is normal and not itself a finding.

### Example 2 — GOOD, with a nuance: a pipeline scores Q = 0 (`OrderFlow`)

An order pipeline: `PlaceOrder` → `TakePayment` → `ShipOrder` →
`NotifyCustomer` → `CloseOrder`, one status variable per stage, each stage's
invariant tying it to the previous (`shipped => paid`, etc.). Real output:

```text
[MEASURED] Variables x actions read/write matrix
variable         PlaceOrder  TakePayment  ShipOrder  NotifyCustomer  CloseOrder
---------------  ----------  -----------  ---------  --------------  ----------
order_status     rw          r            .          .               rw
payment_status   .           rw           r          .               .
shipment_status  .           .            rw         r               .
notified         .           .            .          rw              r

[MEASURED] Near-decomposability
  graph modularity Q = 0.000 over the variable interaction graph
  C1: notified, shipment_status  (2 variables, 3 actions)
  C2: order_status, payment_status  (2 variables, 4 actions)
  candidate port-crossing actions:
    CloseOrder crosses C1, C2
    ShipOrder crosses C1, C2

[MEASURED] Dense rows and columns of the R/W matrix
  dense rows (god-state signature -- variable touched by more than half the actions):
    order_status touched by 3/5 actions
  no dense columns (no action touches more than half the variables)
```

Two intuitions this example exists to teach:

- **Do not read Q as a quality score.** This is a clean design —
  single-writer everywhere (each variable written by exactly one stage, plus
  the close), reads only one step away from writes, a near-diagonal band —
  yet Q = 0.000, because a *chain* has no block structure to find: every
  cluster boundary cuts a chain link. Q answers exactly one question — "does
  a narrow decomposition cut exist?" — and for a pipeline the honest answer
  is "only mid-chain". The matrix's band shape, not the scalar, is what
  tells you this model is fine.
- **Dense-row flags are noisy in small models.** `order_status touched by
  3/5 actions` trips the more-than-half threshold with only five actions.
  Read the row before reacting: written twice (place, close), read once
  (payment guard). That is a lifecycle variable behaving like one, not a
  god-state. The flag is a pointer to go look — here, looking says "fine".

### Example 3 — BAD: god-state, oversized domains, invisible state (`AppState`)

A session/loading model where every action also bumps a cache epoch and
appends to an audit log, the retry counter is modeled at production width,
and two variables have no TypeInvariant conjunct. Real output:

```text
[MEASURED] Dimension table
variable     domain                                            cardinality  note
-----------  ------------------------------------------------  -----------  ---------------------------------------------------------
app_state    [Users -> {"idle", "loading", "ready", "error"}]  16           4^2 total functions
retry_count  0..100                                            101
last_error   (unconstrained)                                   unknown      unconstrained by TypeInvariant -- excluded from the bound
cache_epoch  0..255                                            256
session      [Users -> BOOLEAN]                                4            2^2 total functions
audit_log    (unconstrained)                                   unknown      unconstrained by TypeInvariant -- excluded from the bound

[MEASURED] State-space upper bound
  bound = 1,654,784  (product of 4 bounded dimensions; domains from TypeInvariant)
  excluded (no resolvable domain): last_error, audit_log
  dominant dimensions:
    cache_epoch: 256 (38.7% of the bound in log space)
    retry_count: 101 (32.2% of the bound in log space)

[MEASURED] Variables x actions read/write matrix
variable     Login  Load  Fail  Retry  Logout
-----------  -----  ----  ----  -----  ------
app_state    rw     rw    rw    rw     rw
retry_count  .      w     rw    rw     w
last_error   .      .     w     .      .
cache_epoch  rw     rw    rw    rw     rw
session      rw     r     r     .      rw
audit_log    rw     rw    rw    rw     rw

[MEASURED] Near-decomposability
  graph modularity Q = 0.000 over the variable interaction graph
  C1: app_state, audit_log, cache_epoch, last_error, retry_count, session  (6 variables, 5 actions)
  no port-crossing actions (single component, or fully independent components)

[MEASURED] Dense rows and columns of the R/W matrix
  dense rows (god-state signature -- variable touched by more than half the actions):
    app_state touched by 5/5 actions
    audit_log touched by 5/5 actions
    cache_epoch touched by 5/5 actions
    retry_count touched by 4/5 actions
    session touched by 4/5 actions
  dense columns (action touching more than half the variables):
    Fail
    Load
    Login
    Logout
    Retry

[MEASURED] Invariant coverage (aliased/composed invariants resolved transitively)
  variables no configured invariant reads:
    last_error
    audit_log

  WARNING: state-space upper bound 1,654,784 exceeds max_state_space_bound 1,000,000
```

How to read this, fact by fact:

- **The bound is representation, not behavior.** The two dominant dimensions
  are `cache_epoch` (256) and `retry_count` (101). No invariant distinguishes
  epoch 17 from epoch 18; the behavior's only epoch distinction is "changed".
  The behavior's retry distinctions are three: fresh, retrying, exhausted.
  Roughly 26,000x of this bound (256 x 101) is carrying at most 2 x 3 = 6
  distinctions the program actually makes. That is the meaning of "domains
  wider than the behavior needs".
- **Dense rows name the god-state.** `audit_log` and `cache_epoch` are
  written by 5/5 actions — bookkeeping effects threaded through every
  transition. Every column is dense for the same reason, so *no* cut exists
  (single component, Q = 0.000): the log and epoch couple everything to
  everything.
- **The unknowns are not honest here.** `last_error` and `audit_log` are
  excluded from the bound *and* read by no invariant: unbounded state the
  verification cannot see. The real bound is larger than the printed one,
  and — because `audit_log` grows without limit — actually infinite.
- **The check-time symptom matches.** Under the doctrine's 120-second
  external timeout, TLC on this model did not finish: 18.8 million distinct
  states generated in two minutes and still climbing, states differing only
  in epoch values, retry counts, and log prefixes that no property reads.

What the scanner did **not** do: fail the build (exit 0; one advisory
warning), or tell you which move fixes it. Choosing among abstraction,
decomposition, or a production refactor — and getting user approval for the
last — is the owner's move (`references/architecture_tractability.md`, "The
Three Moves"). This descriptor is the evidence you would attach to that
recommendation.

### Example 4 — ENCOURAGED: the validated refactor, before and after

The normal-practice response to example 3, worked end to end. The remodel
keeps every essential behavior — login/logout, load success and failure, a
bounded retry budget with exhaustion, the no-error-when-idle property — and
removes the representation weight: `retry_count 0..100` becomes
`retry_state {fresh, retrying, exhausted}` (the three distinctions the
behavior makes, with `GiveUp` modeling exhaustion explicitly);
`cache_epoch`, `audit_log`, and `last_error` leave model state — they are
effects, which belong at port boundaries (the functional-core /
imperative-shell target shape), not dimensions of every transition. After,
real output:

```text
[MEASURED] Dimension table
variable     domain                                            cardinality  note
-----------  ------------------------------------------------  -----------  -------------------
app_state    [Users -> {"idle", "loading", "ready", "error"}]  16           4^2 total functions
retry_state  [Users -> {"fresh", "retrying", "exhausted"}]     9            3^2 total functions
session      [Users -> BOOLEAN]                                4            2^2 total functions

[MEASURED] State-space upper bound
  bound = 576  (product of 3 bounded dimensions; domains from TypeInvariant)

[MEASURED] Invariant coverage (aliased/composed invariants resolved transitively)
  every variable is read by at least one configured invariant.

  No complexity warnings -- every metric is within its advisory threshold.
```

The before/after comparison, reported jointly as the validation discipline
requires:

| measure | before | after |
|---|---|---|
| state-space bound | 1,654,784 (+ two excluded unknowns) | 576, nothing excluded |
| TLC under 120s timeout | did not finish (18.8M states and climbing) | green, 36 distinct states |
| invariant coverage | 2 variables invisible to invariants | every variable read |
| invariants enforced | TypeInvariant, NoErrorWhenIdle | same, plus RetryOnlyOnError |
| behaviors | login/load/fail/retry/logout, bounded retries | same, exhaustion now explicit (`GiveUp`) |

This is what "validated" means: green under TLC, the properties preserved
and strengthened, and the descriptors diffed — the bound fell ~2,900x
because *representation* left, not behavior. A drop like this is a normal,
encouraged outcome of the refinement loop, worth a ledger entry and nothing
more dramatic. Two honesty notes: (a) coarsening `retry_count` to three
values is only behavior-preserving because no property distinguished
individual counts — if the program observably behaved differently at retry
7, that count was essential and must stay; deciding that is design judgment,
made with the user, not a mechanical rewrite. (b) The after-descriptor still
flags all three variables as dense rows — three core protocol variables in
a six-action model *are* touched by most actions. An irreducible small core
looks like this, and that flag is a fact to note, not a problem to fix.
Also check the transition-level diff before recording any reduction: a
generated-states drop at constant distinct states is a deleted self-loop
(a red flag the distinct-state count cannot see), not a win.

### Example 5 — REAL AND MIXED: this repository's own model

Descriptors on real programs are rarely all-good or all-bad. This repo's
baseline (`specs/program_model/TlaSpecDevCli.tla`, run with its manifest)
shows, in one output: resolved domains sized to real distinctions *and* two
deliberate unknowns; a fully justification-linked state vector *and* a single
dense component with warnings. Excerpts:

```text
[MEASURED] Dimension table (excerpt)
variable            domain                                                        cardinality  source         note
------------------  ------------------------------------------------------------  -----------  -------------  -------------------------------------------------------------------------------------------------------------
setup_phase         0..5                                                          6            TypeInvariant
ticket_state        [Tickets -> 0..5]                                             216          TypeInvariant  6^3 total functions
lastCommand         (unconstrained)                                               unknown      -              unconstrained by TypeInvariant / the configured invariants (resolved transitively) -- excluded from the bound
result              (unconstrained)                                               unknown      -              unconstrained by TypeInvariant / the configured invariants (resolved transitively) -- excluded from the bound

[MEASURED] State-space upper bound
  bound = 699,840  (product of 7 bounded dimensions; domains from TypeInvariant)
  excluded (no resolvable domain): lastCommand, result

[MEASURED] Near-decomposability
  graph modularity Q = 0.000 over the variable interaction graph
  C1: complexity_gate, corpus_gate, effect_conformance, kill_test, lastCommand, result, setup_phase, spec_root, ticket_state  (9 variables, 14 actions)
  no port-crossing actions (single component, or fully independent components)

[MEASURED] Dense rows and columns of the R/W matrix
  dense rows (god-state signature -- variable touched by more than half the actions):
    lastCommand touched by 14/15 actions
    result touched by 14/15 actions
    setup_phase touched by 12/15 actions
    spec_root touched by 10/15 actions

[MEASURED] Invariant coverage (aliased/composed invariants resolved transitively)
  variables no configured invariant reads:
    lastCommand
    result

  WARNING: component C1 has 9 variables (complexity_gate, corpus_gate, effect_conformance, kill_test, lastCommand, result, setup_phase, spec_root, ticket_state), exceeding max_component_variables 6

  WARNING: component C1 is touched by 14 actions (BuildSkillCli, InstallLocalCli, ScaffoldProject, RecordBudgets, ScaffoldWorkflow, OpenTicket, UpdateTicketDesired, UpdateTicketCurrent, AnalyzeComplexity, AnalyzeCorpus, RunEffectConformance, RunKillTest, RunSpecUnitTests, CloseTicket), exceeding max_component_actions 8
```

Reading it with the intuitions above:

- The domain-model variables are sized to real distinctions (a six-step
  `setup_phase` for the setup commands, a per-ticket lifecycle function over
  the 3-ticket constant — 216 = 6^3 — and oracle-verdict enums whose 3-to-5
  values are exactly each oracle's verdict vocabulary), and every variable
  carries a recorded justification linkage — plus the observability pair.
- `lastCommand`/`result` show a textbook god-state signature — written by
  14/15 actions (every action except the stutter step), read by no
  invariant, excluded from the bound. Here the
  owner's judgment is that they are a *deliberate observability channel*
  (every action records what ran and what came back, for the spec-double
  layer). What makes that judgment defensible is not the stated intent but a
  **named consumer**: the spec-double conformance layer reads these fields
  back — the generated cases and production adapters carry and compare
  `last_command` in every snapshot. That is the evidence that separates this
  pair from example 3's `audit_log` (see "The write-only-state test" below).
  The descriptor correctly refuses to distinguish "deliberate" from
  "accidental" — it prints the same facts either way; example 3's
  `audit_log` and this `lastCommand` look alike on the page. Knowing which
  one you have is exactly the judgment this document exists for. And when
  reading the rest of the output, discount the channel's contribution
  mentally: the top dense rows and much of the single component's edge
  weight (and hence the Q of 0.000) come from a pair every action touches
  by design, and the remaining dense rows (`setup_phase` 12/15, `spec_root`
  10/15) are guard reads on the phase and root every command checks first —
  example 2's lifecycle-hub reading, not a smear. The *rest* of the model
  is better-shaped than the headline numbers suggest.
- The warnings are the component-size pair (9 variables against the
  advisory 6, 14 actions against the advisory 8): an ordinary CLI over
  shared state — the exact shape the advisory reframe was measured on
  (`references/architecture_tractability.md`, "Advisory, Not Blocking") —
  with much of the component's coupling being the observability pair again.
  The bound, 699,840, sits under the 1M advisory threshold, dominated by
  the 216-value per-ticket lifecycle dimension — essential behavior (the
  workflow really does track per-ticket state independently), so the
  response is a budget rationale, not a remodel: the manifest's
  `max_distinct_states: 500000` records the agreed reachable-state budget
  for exactly this reason. Note the two figures are not interchangeable:
  the bound is static declared-representation size; `max_distinct_states`
  is checked against what TLC actually reaches.

A mixed descriptor like this is the common case. The reading is not "good
model" or "bad model" but a short list of facts worth carrying forward:
which density is deliberate, which dimension justifies the bound, what the
budget rationale is — and whether any of it has drifted since the last
ledger entry.

### The write-only-state test (the example-3 / example-5 boundary)

Dense, write-only state — a variable every action stamps and nothing reads —
sits exactly on the line between example 3 (bookkeeping smear: remove it) and
example 5 (deliberate density: defend it). The test that decides which side it
is on:

> **A write-only stamped variable is bookkeeping — regardless of stated
> design intent — unless you can name a concrete dependent: a guard that
> branches on it, an invariant beyond its type conjunct, a test that asserts
> its value, or a reader that consumes it (in production code or in the
> verification/observability toolchain).**

The test is about *readers*, and stated intent is not a reader. "The app
deliberately stamps this on every operation" is a sentence about the writer;
a README can say it about any variable, including pure bookkeeping. Example
5's `lastCommand`/`result` pass the test because the spec-double conformance
layer reads them back (snapshots carry and compare `last_command`); example
3's `audit_log`-style stamps fail it because nothing — no guard, no property,
no test, no consumer — ever looks.

This test exists because the boundary was *measured* to be ambiguous. In the
recorded validation divergence
(`examples/validation/runs/ex3-run1/artifacts/complexity_decision.md` vs
`ex3-run2/artifacts/complexity_decision.md`), two agents with identical
instructions read the identical descriptor of the same model, whose `mode`
and `dirty` variables were stamped by every action and read by nothing.
Run 1 applied exactly this test — "no guard, no invariant beyond type, no
test, no code reader" — classified them as bookkeeping, and removed them
(bound 624). Run 2 read the README's "the hub deliberately stamps the shared
mode … and dirty flag" as example-5 deliberate density and kept them (bound
6,240). Both runs were green, warning-free, and grounded — *whether* the
representation was over-wide converged; *which* variables to keep did not.
Under this test, run 1's classification is the canonical one: no dependent
existed, so the stamps were bookkeeping and the stated design intent did not
upgrade them.

Two boundaries of the test itself:

- **Classification and authorization are separate.** The test decides what
  the variable *is*; it does not authorize touching production code. Run 1's
  code deletion was separately authorized by its ticket — without that, the
  right move is to record the classification, take the model change, and
  bring the production refactor to the user for approval.
- **A dependent must be nameable, not hypothetical.** "Something might read
  it someday" fails the test; a named consumer (a test, an adapter field, a
  downstream tool) passes it. If a variable genuinely is a planned
  observability channel, give it a consumer — or a `justification:` entry
  linking it to the effect it carries — and the classification changes with
  the evidence.

## Deciding Whether And How To Refactor

A reading order that works, given a fresh descriptor:

1. **Unknowns first.** Every `(unconstrained)` row: deliberate (an
   observability channel with an owner-known reason) or a hole? A hole means
   the bound understates and verification is blind there — fix the model
   before judging the program.
2. **Bound vs behavior.** For each dominant dimension ask the essential-
   distinction question. Invariant-read, guard-distinguished dimensions are
   the program's size; wide counters nobody distinguishes are refactor
   candidates.
3. **Dense rows, then columns.** For each: what role does this variable
   play? Lifecycle hub in a small model (example 2), deliberate
   observability (example 5), or bookkeeping smeared everywhere (example
   3)? Only the last is a finding — and for write-only stamped state,
   decide with the write-only-state test above: name a concrete dependent
   (guard, invariant beyond type, test, or reader) or classify it as
   bookkeeping; stated design intent alone does not upgrade it.
4. **Clusters.** Can you name them? Do the port-crossing actions look like
   real transactions between subsystems? Nameable clusters with narrow
   crossings mean a decomposition cut exists if you ever need it; a single
   dense component means the coupling itself is the finding.
5. **Coverage.** State no invariant reads is either missing a property or
   is not really state. Either way it is on the list.
6. Then form the recommendation — abstract, decompose, or refactor the
   program (`references/architecture_tractability.md`, "The Three Moves") —
   with the descriptor excerpts as evidence, and take it to the user.
   Production refactors require explicit approval; validated reductions are
   encouraged, celebrated in the ledger, and then the loop recurses.

And the standing reminders, one last time: these are intuitions for the
agent to judge with. The scanner makes no suggestions and this document
makes none on its behalf; a poor score is not a verdict; nothing here blocks
promotion; and a complexity delta only counts when reported jointly with the
behavior-retention evidence from the same run.

---

## The Other Descriptor: Complexity Of Produced Code

Everything above reads a **model**. `scripts/analyze_complexity.py` measures
TLA+, and every A/B this project has run produces **Python**. That gap is not
academic: when the predecessor epic asked whether the hexagonal prompt made
the produced code simpler, D2 measured **2 for both arms from all four
judges** — not because the prompt failed to simplify, but because nothing in
the toolchain could tell.

`scripts/code_complexity.py` is the instrument that was missing.

```
python3 scripts/code_complexity.py <tree-or-file> [more...]
python3 scripts/code_complexity.py <tree> --json     # goes in mechanical.json
```

It is a **thermometer**, held to exactly the same rules as the model
descriptor and two more besides:

- It **reports**. It refuses nothing and it exits 0 on every target,
  including a target that does not exist and a file it cannot parse. An
  unparseable construct costs *completeness*, which is printed with the path
  and the reason.
- **CD-01**: it proposes no cut, no refactor, no move. A tool that picks the
  boundary makes every edge legal by construction.
- **MF-020**: it prints **no comparison and no delta**. There is deliberately
  no `--compare` mode. A printed `-12` is the shape that invites a reader to
  treat a fall as a finding, and the best complexity result on this project's
  record was withheld from a top score by both blind judges for exactly that
  reading. Run it twice; read two tables.
- **No threshold exists.** There is no constant in that file a measured figure
  is compared against, and nothing in this toolchain reads its output as a
  condition. Both are asserted by `tests/test_code_complexity.py` against the
  shipped source and the shipped repository, not promised here.

Its figures go in the scorecard's **mechanical block**, which is recorded and
never scored, so that a disagreement between the measurement and the judges is
visible as a finding rather than resolved by arithmetic.

### The figures

Every key below is emitted by the shipped instrument, and
`tests/test_code_complexity.py::test_documented_figures_match_shipped_output`
asserts this table and the real output name exactly the same set — so renaming
a figure and not this table fails a test.

| key | scope | what it counts |
|---|---|---|
| `path` | module | file path, relative to the target |
| `role` | module | `test` or `code`, from the NAME alone — never from contents |
| `parsed` | module | whether the file was parsed at all |
| `unparsed_reason` | module | why it was not, when it was not |
| `modules` | totals | files measured |
| `total_lines` | both | all lines |
| `code_lines` | both | non-blank, non-comment lines |
| `callables` | both | `def` and `async def`, at any nesting |
| `classes` | both | `class` statements |
| `public_top_level` | both | module-level names not starting with `_` |
| `public_methods` | both | public methods of public classes |
| `public_surface` | both | the sum of the previous two |
| `declared_exports` | module | `len(__all__)` when it is a literal, else null |
| `instance_state` | both | distinct `self.<name>` assignment targets, per class, summed |
| `module_state` | both | distinct module-level names *rebound* (twice-assigned, augmented, or `global`) |
| `branch_points` | both | decision points, exactly as listed below |
| `max_branch_points_in_callable` | both | the most-branching single callable |
| `busiest_callable` | module | its name |
| `max_depth` | both | deepest nesting of `if`/`for`/`while`/`with`/`try`/`match` in one callable |
| `deepest_callable` | module | its name |
| `declared_interfaces` | both | classes based on `Protocol`/`ABC`, or carrying an `@abstractmethod` |
| `declared_interface_methods` | both | their methods |
| `effectful_calls` | both | syntactic calls to the printed sink vocabulary |
| `effect_sinks` | both | the distinct sink names actually seen |
| `effect_sink_groups` | totals | which of filesystem/process/network/clock/randomness/stdio were seen |
| `imports_internal` | module | in-tree modules this one imports |
| `imports_external` | module | imports resolving outside the tree |
| `internal_import_edges` | totals | in-tree import edges |
| `modules_with_effectful_calls` | totals | how many modules touch the outside world |
| `branch_points_in_effectful_modules` | totals | of the branch points, how many sit in a module that also touches the outside world |
| `instance_state_in_effectful_modules` | totals | the same partition for mutable object state |
| `unresolved_constructs` | module | `import *`, `setattr`, `getattr`, `eval` — things it cannot attribute |

**`branch_points` counts exactly**: `if` (each `elif` is a nested `if`),
conditional expressions, `for`/`async for`, `while`, each `except` handler,
each `if` clause of a comprehension, each `match` case, and each *additional*
operand of a boolean operator. It does **not** count `assert`, `with`, or a
bare `try`. That choice changes the figure for test modules most of all, which
is why it is stated rather than left implicit.

**`effectful_calls` undercounts on purpose.** It matches names syntactically,
so a sink reached through an alias, a local variable or `getattr` is invisible;
and eighteen sink names that collide with ordinary in-memory operations
(`get` ~ `dict.get`, `copy` ~ `dict.copy`, `walk` ~ `ast.walk`, …) are left out
of the vocabulary entirely and printed with every report. A `dict.get` counted
as a network call is a figure that says something false; a missed
`requests.get` is a figure that says less than the truth and says so in the
completeness block. One-sided, the same way the negative corpus is one-sided.

### Reading it

The same intuition as the rest of this document applies: complexity should be
proportional to the essential behavior. Three cautions specific to code:

1. **Totals hide location, and location is usually the question.** The two
   anchor trees under `examples/validation/ab/` implement one feature — the
   flat `reference/` and the ported `reference_ports/` — and report the
   *identical* `effectful_calls=3`. What differs is where those three calls
   sit: in the flat tree the module holding all 10 branch points also holds all
   3, and in the ported tree the domain holds 9 branch points and 0. Read the
   per-module table and the `*_in_effectful_modules` partition, not the total
   alone.
2. **A ported tree measures *larger* on most totals, and that is not a
   defect in it or in the instrument.** `reference_ports/` reports 5 modules,
   26 public surface and 255 code lines against the flat tree's 1, 15 and 122.
   Introducing a boundary adds a declaration, an implementation and a
   composition point. Whether that purchase was worth it is a judgement, and
   this instrument does not make it.
3. **NEVER PUT TWO TREES IN ONE TABLE ON TWO DIFFERENT DENOMINATORS.** The
   instrument prints two totals blocks, `totals` and `totals_code_only`, and a
   table whose columns mix them manufactures a *direction out of nothing*. Not
   hypothetical: PA-02's own first report did it, and the section below is both
   the correction and the reason the rule is written down.

### The denominator rule, and the mistake that bought it

A tree with no test modules reports `totals == totals_code_only`. A tree that
ships its own tests does not. So a four-column table that takes the all-modules
figure for the trees that have tests and — silently, because the two blocks
coincide there — the code-only figure for the trees that do not is **comparing
different things in adjacent columns.**

PA-02's first report tabled exactly that: `totals` for the two sealed arms
beside what was effectively `totals_code_only` for the two anchor trees. Three
figures reverse direction or flatten when the denominator is made uniform:

| figure | as mis-tabled | like for like (`totals_code_only`) |
|---|---|---|
| `branch_points` | 37 → 19, apparently halved | **10 → 11, the ported tree is HIGHER** |
| `max_depth` | 5 → 3 | **1 → 1, identical** |
| `public_surface` | 52 → 48, apparently smaller | **20 → 25, the ported tree is HIGHER** |

**The apparent improvement was an artifact of `arm_a` shipping a bigger test
file.** `arm_a`'s single test module carries **27 of its 37** all-modules branch
points and **15 of its 20** effectful calls; `arm_b`'s carries 8 of 19 and 3 of
6. Nothing about either implementation moved.

This is MF-020 wearing a new hat — a figure that improves because of *what got
counted* — and it is worse than the usual case, because these figures land in a
scorecard's **mechanical block, which is recorded and never scored**. No judge
is going to challenge them. A wrong number in the unscored block is a wrong
number nothing in the protocol catches, which is why the correction below is
executed by a test rather than promised in prose.

The test-inclusive figures are not noise and are not suppressed. "`arm_a`'s
branch count is 37 all-modules and 10 implementation-only, and the difference is
its test file" is a real fact about that arm, and a fact about reading this
instrument. It is reported in its own labelled block, never interleaved.

### The recorded figures for the four subject trees

Two anchor trees implementing one feature (`examples/validation/ab/reference/`
and `.../reference_ports/`) and the previous epic's two sealed arms
(`specs/.history/hexagonal-prompting-epic/closed-snapshot/results/scorecards/hexagonal-prompting-rerun/arms/arm_a`
and `.../arm_b`).

`tests/test_code_complexity.py::test_recorded_figures_match_a_live_run` asserts
**every cell of both tables against a live run**, each from the block its own
heading names — so a stale figure, a renamed block, or a mixed denominator fails
a test instead of becoming a directional claim.

#### Like for like — `totals_code_only` in every column

| figure | reference | reference_ports | arm_a | arm_b |
|---|---|---|---|---|
| `modules` | 1 | 5 | 1 | 4 |
| `code_lines` | 122 | 255 | 151 | 202 |
| `callables` | 13 | 22 | 17 | 23 |
| `classes` | 3 | 8 | 4 | 6 |
| `public_surface` | 15 | 26 | 20 | 25 |
| `instance_state` | 7 | 9 | 8 | 8 |
| `module_state` | 0 | 0 | 0 | 0 |
| `branch_points` | 10 | 11 | 10 | 11 |
| `max_branch_points_in_callable` | 4 | 4 | 4 | 4 |
| `max_depth` | 1 | 1 | 1 | 1 |
| `declared_interfaces` | 0 | 1 | 0 | 1 |
| `declared_interface_methods` | 0 | 2 | 0 | 2 |
| `internal_import_edges` | 0 | 4 | 0 | 3 |
| `effectful_calls` | 3 | 3 | 5 | 3 |
| `modules_with_effectful_calls` | 1 | 1 | 1 | 1 |
| `branch_points_in_effectful_modules` | 10 | 1 | 10 | 1 |
| `instance_state_in_effectful_modules` | 7 | 1 | 8 | 1 |

#### All modules — `totals` in every column, tests included

Reported separately and never interleaved with the block above. For the two
anchor trees these are the same numbers, because neither ships a test module;
for the two arms they are not, and the difference is the size of each arm's own
test file.

| figure | reference | reference_ports | arm_a | arm_b |
|---|---|---|---|---|
| `modules` | 1 | 5 | 2 | 5 |
| `code_lines` | 122 | 255 | 422 | 407 |
| `callables` | 13 | 22 | 50 | 45 |
| `classes` | 3 | 8 | 4 | 6 |
| `public_surface` | 15 | 26 | 52 | 48 |
| `instance_state` | 7 | 9 | 8 | 8 |
| `module_state` | 0 | 0 | 0 | 0 |
| `branch_points` | 10 | 11 | 37 | 19 |
| `max_branch_points_in_callable` | 4 | 4 | 10 | 4 |
| `max_depth` | 1 | 1 | 5 | 3 |
| `declared_interfaces` | 0 | 1 | 0 | 1 |
| `declared_interface_methods` | 0 | 2 | 0 | 2 |
| `internal_import_edges` | 0 | 4 | 1 | 4 |
| `effectful_calls` | 3 | 3 | 20 | 6 |
| `modules_with_effectful_calls` | 1 | 1 | 2 | 2 |
| `branch_points_in_effectful_modules` | 10 | 1 | 37 | 9 |
| `instance_state_in_effectful_modules` | 7 | 1 | 8 | 1 |

**What survives the correction is what measures the port rather than the size.**
Like for like, the arms separate on `declared_interfaces` (0 vs 1),
`internal_import_edges` (0 vs 3) and the effectful-module partition
(`branch_points_in_effectful_modules` 10 → 1,
`instance_state_in_effectful_modules` 8 → 1) — while branching, depth and the
worst single callable are identical, and surface and code lines go *up*. The
instrument still tells the pairs apart. It tells them apart on **structure**,
not on being smaller.
