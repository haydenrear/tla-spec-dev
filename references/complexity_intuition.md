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
shows, in one output: resolved 2/3/8-cardinality domains sized to real
distinctions *and* two deliberate unknowns; nameable clusters *and* a low Q
with warnings. Excerpts:

```text
[MEASURED] Dimension table (excerpt)
variable                domain                   cardinality  note
----------------------  -----------------------  -----------  ---------------------------------------------------------
active_tickets          SUBSET Tickets           8            powerset of 3 elements
desired_ready           [Tickets -> BOOLEAN]     8            2^3 total functions
lastCommand             (unconstrained)          unknown      unconstrained by TypeInvariant -- excluded from the bound
result                  (unconstrained)          unknown      unconstrained by TypeInvariant -- excluded from the bound

[MEASURED] State-space upper bound
  bound = 1,572,864  (product of 10 bounded dimensions; domains from TypeInvariant)
  excluded (no resolvable domain): lastCommand, result

[MEASURED] Near-decomposability
  graph modularity Q = 0.038 over the variable interaction graph
  C1: cli_built, cli_installed, lastCommand, project_scaffolded, result, spec_root, workflow_scaffolded  (7 variables, 9 actions)
  C2: active_tickets, closed_tickets, current_ready, desired_ready, spec_unit_tests_passed  (5 variables, 5 actions)

[MEASURED] Dense rows and columns of the R/W matrix
  dense rows (god-state signature -- variable touched by more than half the actions):
    lastCommand touched by 9/9 actions
    result touched by 9/9 actions

[MEASURED] Invariant coverage (aliased/composed invariants resolved transitively)
  variables no configured invariant reads:
    lastCommand
    result

  WARNING: state-space upper bound 1,572,864 exceeds max_state_space_bound 1,000,000
```

Reading it with the intuitions above:

- The domain-model variables are sized to real distinctions (booleans for
  real toggles, ticket functions over the 3-ticket constant), and the
  clusters are nameable: C2 is the ticket lifecycle, C1 is CLI/scaffold
  setup — plus the observability pair.
- `lastCommand`/`result` show a textbook god-state signature — written by
  9/9 actions, read by no invariant, excluded from the bound. Here the
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
  mentally: both dense rows and much of the cross-cluster edge weight (and
  hence the low Q) come from a pair every action touches by design — the
  *rest* of the model is better-shaped than the headline numbers suggest.
- The bound warning (1.57M > 1M advisory threshold) is dominated by three
  8-cardinality ticket dimensions — essential behavior (the workflow really
  does track per-ticket readiness independently), so the response is a
  budget rationale, not a remodel: the manifest's
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
