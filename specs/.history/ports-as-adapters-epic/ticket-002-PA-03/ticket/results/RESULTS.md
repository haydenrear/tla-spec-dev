# PA-03 — ports in the manifest, and cases generated per port

**The headline is a negative and it is the informative one.** A port declared in
the manifest now produces its own case set, that case set executes at a higher
rate than anything else in this project's record, and it inherits guard
relaxation at 3 of 3 without touching the negative corpus. And **the two arms
still agree on every strictly comparable cell** — 56 of 56 becomes **64 of 64**
once the new column is counted. Generation alone cannot make a hexagonal
codebase and a flat one produce different verdicts, and the reason is
structural rather than a bug.

## What was built

`--port-cases {off,with-positive,only}` on `generate cases`, plus
`--port-dedupe {none,region}` and `--port-manifest`.

Declarations are read from the manifest, in the shape the effect ports already
use — `effects.components.<C>.ports.<P>` and `effects.actions.<A>` — through one
shipped builder, `load_port_catalog`.

A port's **region** is derived from the model, never named by hand: the
variables written by actions that declare the port, minus every variable written
by a MAPPED action that does not. On the A/B fixture this yields
`{committed, ledger, closed}` for `ledger.LedgerAppendPort` — the hand-authored
`Aspect_Ledger` slice, obtained from the declaration alone, with no second
`.tla`, no `.cfg` and no hand-written projector.

Every port case carries `port:<component>.<name>` and either
`port-expect:emitted` (the manifest declares this action on this port) or
`port-expect:silent` (it maps the action and does not name the port). An action
**absent** from `effects.actions` gets neither and produces no port case:
absent means unmapped, empty means checked.

## Surface cost, stated before the flag was added

**Model delta: ZERO.** `effects` is a declaration table, not TLA+ state. No
variable, no action, no `Next` disjunct, no CONSTANT. TLC explores the identical
state graph before and after, so `max_distinct_states` and
`max_state_space_bound` are untouched and the predecessor's measured ~8x
state-space cost per surface-adding ticket does not apply.

The cost is corpus size, and it is measured rather than promised:

| model | ports | source cases | port cases before dedupe | after dedupe |
| --- | --- | --- | --- | --- |
| A/B fixture `QuotaLedger` | 1 | 43,246 | 4,146 | **1,855** |
| this repository's `TlaSpecDevCli` | 15 | 99,817 | 374,376 | **29,921** |

On this repository's own model, 11 of the 15 declared ports get **no case set at
all**, because every variable their actions write is also written by a mapped
action that does not declare them. That is printed per run.

## Case counts per declared port (A/B fixture)

```
ledger.LedgerAppendPort: 1855 case(s) (750 emitted, 1105 silent)
  region {closed, committed, ledger}; declared by CloseTenant, Commit
    CloseTenant: 362   Commit: 388   Release: 436   Reserve: 669
UNMAPPED: RefuseCloseAlreadyClosed, RefuseCloseOutstanding, RefuseCommitUnknown,
          RefuseReleaseUnknown, RefuseReserveClosed, RefuseReserveNotPositive,
          RefuseReserveOverQuota
```

## Executable counts, beside every kill number

From each run's own control pass on unmutated code. **Identical on both arms.**

| instrument | cases | executed | % | accepting `Reserve` |
| --- | --- | --- | --- | --- |
| `corpus-whole` | 43,128 | 3,734 | 8.66% | 294 |
| `corpus-neg` | 118 | 94 | 79.7% | 0 |
| `corpus-slice-res` | 2,438 | 320 | 13.1% | 100 |
| `corpus-slice-led` | 56 | 10 | 17.9% | 0 |
| **`corpus-port`** | **1,855** | **1,543** | **83.2%** | **294** |
| `map-silent` / `map-checking` | 43,128 | 3,734 | 8.66% | 294 |
| `suite` | 28 tests | 28 | 100% | — |

The port corpus is 4.3% of the whole-view corpus and carries 41% of its executed
volume, because the 39,100 refusal edges that carry no arguments belong to
actions the manifest never maps.

## Per-class, per-arm kill table — `corpus-port` beside the inherited columns

Arm A and arm B are the sealed EVAL-RERUN artifact pair. Every pre-existing cell
reproduces the sealed tables; see "The boundary" below for the one exception.

### Arm A — the ordinary implementation ask

| class | whole | neg | slice-res | slice-led | **port** | silent | checking | suite |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| guard_relaxation | 0 of 3 | **3 of 3** | 0 of 3 | 0 of 3 | **3 of 3** | 0 of 3 | 0 of 3 | 3 of 3 |
| durable_content | 1 of 2 | 0 of 2 | 0 of 2 | 0 of 2 | **1 of 2** | 1 of 2 | 2 of 2 | 2 of 2 |
| cross_aspect | 1 of 1 | 0 of 1 | 0 of 1 | 0 of 1 | **0 of 1** | 1 of 1 | 1 of 1 | 1 of 1 |
| output_oracle | 1 of 1 | 0 of 1 | 1 of 1 | 0 of 1 | **0 of 1** | 1 of 1 | 1 of 1 | 1 of 1 |
| ordering | 1 of 2 | 0 of 2 | 0 of 2 | 1 of 2 | **1 of 2** | 1 of 2 | 1 of 2 | 1 of 2 |
| wrong_value | 2 of 2 | 0 of 1 (1 nd) | 2 of 2 | 0 of 1 (1 nd) | **0 of 2** | 2 of 2 | 2 of 2 | 2 of 2 |

### Arm B — the hexagonal + minimize-complexity ask

| class | whole | neg | slice-res | slice-led | **port** | silent | checking | suite |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| guard_relaxation | 0 of 3 | **3 of 3** | 0 of 3 | 0 of 3 | **3 of 3** | 0 of 3 | 0 of 3 | 3 of 3 |
| durable_content | 1 of 2 | 0 of 2 | 0 of 2 | 0 of 2 | **1 of 2** | 1 of 2 | 2 of 2 | 2 of 2 |
| cross_aspect | 1 of 1 | 0 of 1 | 0 of 1 | 0 of 1 | **0 of 1** | 1 of 1 | 1 of 1 | 1 of 1 |
| output_oracle | 1 of 1 | 0 of 1 | 1 of 1 | 0 of 1 | **0 of 1** | 1 of 1 | 1 of 1 | 1 of 1 |
| ordering | 1 of 2 | 0 of 2 | 0 of 2 | 1 of 2 | **1 of 2** | 1 of 2 | 1 of 2 | 1 of 2 |
| wrong_value | 2 of 2 | 1 of 2 | 2 of 2 | 0 of 2 | **0 of 2** | 2 of 2 | 2 of 2 | 2 of 2 |

Never a single rate: the interesting quantity is which instrument saw which
class, and merging the rows destroys the only comparison worth making.

## Guard relaxation: still 3 of 3, and the composition is why

`corpus-neg` is **3 of 3 on both arms**, unchanged, because the port pass does
not touch it. The port pass is a *function of* the corpus the positive and
negative passes produced: under `--port-cases with-positive` the source cases
are emitted first and unchanged, case for case
(`test_the_port_pass_composes_with_the_negative_corpus`).

`corpus-port` is **also 3 of 3**, on both arms, because it was generated with
`--negative-cases with-positive --port-cases only` and therefore inherited the
refusal cases the class needs. It composed rather than replaced: the class that
had measured zero on every instrument in this project's history until HP-03
arrives in a port-scoped corpus for free.

## The arms do NOT diverge: 64 of 64

Strictly comparable = the 8 mutants EVAL-RERUN declared comparable (all but
`M07`, `M08`, `M10`) across all 8 instruments.

> **64 of 64 strictly comparable cells are identical between the arms.** The
> 56 of 56 baseline reproduces exactly, and the 8 new cells the port column adds
> agree too.

**GOAL-cases-drive-ports's expected effect for this ticket is MISSED, and the
reason is structural.** A generated corpus is a pure function of `(model,
manifest, flags)`. The A/B holds **one model and one manifest across both arms
by design** — the fixture's own README says why: "if each arm generated its own,
a D1 difference between arms could be a difference between their models and
nobody could tell which produced it." So no change confined to GENERATION can
make the two arms' corpora differ by a single byte. Divergence can only come
from the *binding* — which is PA-04 — or from a per-arm catalogue difference,
which is seeding rather than detection.

Stated plainly because the epic prefers it to a flattering result: **the port
boundary is now visible to generation and the verdicts still did not move.**

## Its blind spot, measured rather than assumed

`corpus-port` does not decide the catalogue's positive control on any tree.
`M07` inflates a held total; the port region is `{committed, ledger, closed}`;
the symptom lands on `available`.

This is **not** an executability limit, and the numbers rule that explanation
out: `corpus-port` executes **294 accepting `Reserve` cases**, exactly as many
as the whole-view corpus, and still cannot see it. The projection is the only
operative constraint. Two findings were filed rather than repaired:

* **PA-03-DF-02** — a declared `limitation` can only say "this instrument never
  executed that action". A projected corpus's real limitation is the opposite
  shape and is inexpressible, so the only honest outcome is a red control.
* **PA-03-DF-03** — no positive control in the catalogue is seeded inside a
  port's region, so no port-scoped instrument can have a green one. It is a gap
  in the CATALOGUE, not in the corpus: `corpus-port` kills `M05`, a
  durable-content fault inside the region, on all three trees.

Read the `corpus-port` column as a floor under a red control until a control
exists that a port-scoped instrument can decide.

## Byte-identity, including failing executions

**The corpus.** Two independent generations to the same path, every file of the
written package compared byte for byte — `cases.py`, `docs.md`, `types.py`,
`doubles.py`, `validators.py`, `__init__.py`, `case_coverage.json`,
`param_recovery_audit.md`. Identical.

```
08265aff0d81f27f4dfc9694d2a69c3c5b6e695c  cases.py
2304fa76832e4f3c49742eefa015672da38a91b5  docs.md
a1e19353e4a66d7d72acb50e447ebeced7d1e1e2  case_coverage.json
```

**The measurement.** Two independent end-to-end runs of the arm-A kill table
(`kill-table-arm-a.json`, `determinism-arm-a-run-2.json`) are byte-identical
after JSON normalisation, **including the `evidence` block**, which carries the
failure text of every failing execution. Zero keys differ.

## The boundary this run sits on — named, not crossed silently

**EVAL-SUPPRESS (`d8608ce`) post-dates EVAL-RERUN (`b3a0199`).** This run uses
the repaired driver, so it is not comparable to the sealed EVAL-RERUN tables
without saying so.

Compared cell by cell against the sealed tables:

* **arm A: not one cell differs.**
* **arm B: exactly one cell differs** — `M07 / corpus-slice-led`,
  `NOT_DECIDABLE -> SURVIVED`. That is the cell EVAL-SUPPRESS itself published
  as moving under the repaired driver (`arm-b-repaired-sealed-catalogue.json`),
  because arm B's `corpus-neg` kills M07 while executing zero accepting
  `Reserve` cases and so falsifies that limitation's scope.

No `NOT_DECIDABLE` became a `KILLED`. `M07` is not a strictly comparable mutant,
so the 56-of-56 denominator is unaffected and the identity result survives the
repair, exactly as EVAL-SUPPRESS reported.

## The cap

Nothing in this repository fits the default `max_internal_cases_per_component:
200`, and that predates this ticket (HP-03-DF-02, open). What changed:

* `--port-cases` is **off by default**, so no existing corpus moves.
* On the A/B fixture the port corpus is **1,855 against the whole-view
  corpus's 43,128** — 23x smaller — and both exit 2 on the uncalibrated default.
* On this repository's own model the port corpus is **29,921 against 99,817**.

The port pass therefore did not grow a corpus past its cap; it shrank every
corpus it was run beside. It is not a substitute for the whole-view corpus and
makes no claim about unmapped actions.

## Commands

```bash
uv run --with pytest --with pyyaml python -m pytest tests -q
# 1062 passed

python3 scripts/tla_spec_dev.py --spec-root specs generate cases \
  examples/validation/ab/model/QuotaLedger.tla \
  examples/validation/ab/model/QuotaLedger.cfg \
  --out <scratch>/specs/corpus-port --package quota_port --view internal \
  --negative-cases with-positive --port-cases only
# 1855 port cases; exit 2 on the uncalibrated 200-case default cap

PYTHONPATH=$PWD/specs/results/scorecards/hexagonal-prompting-rerun/measure \
python3 examples/validation/ab/eval/run_controls.py --label PA03-arm-A \
  --tree specs/results/scorecards/hexagonal-prompting-rerun/arms/arm_a --module-dir . \
  --binding rerun_arm_a_binding \
  --catalogue .../catalogue_arm_a.toml --catalogue .../controls_arm_a.toml \
  --instrument corpus-whole=... --instrument corpus-neg=... \
  --instrument corpus-slice-res=... --instrument corpus-slice-led=... \
  --instrument corpus-port=<scratch>/specs/corpus-port/spec-unit/quota_port \
  --instrument map-silent=...:silent --instrument map-checking=...:checking \
  --suite examples/validation/ab/tests/test_behavior.py --out <out>.json
```

## What was REJECTED

Four generation designs were considered and not shipped.

1. **A port case as a first-class `StateGraphPortInteraction`** — an expected
   output naming the port, the operation and the payload, asserting the port was
   invoked exactly once. It is the strictly better assertion and it is what PA-04
   needs. **Rejected because no shipped adapter could produce it**, so every
   generated port case would have been unexecutable on the day it shipped, and
   "a corpus nobody can run is not a mechanism". The narrowed-`after` form runs
   on the unmodified oracle today and PA-04 can widen it.

2. **A `writes:` key on the port declaration, naming the region.** Simpler to
   implement and it would have let a port declare a region the model does not
   support. **Rejected under `declaration_executability_rule`**: it is a second
   declaration for the same fact, and the failure mode is that the region and
   the model's write sets drift with nothing to notice. Deriving it means the
   declaration cannot be wrong about the model — it can only disagree with it,
   which is reported.

3. **Port cases for UNMAPPED actions, defaulting to "silent".** It would have
   more than doubled the A/B port corpus and covered the seven `Refuse*` actions.
   **Rejected because it converts "nobody looked" into "we checked, there are
   none"** — the exact collapse the manifest's own comment forbids. The seven are
   named in the run output instead. The consequence is honest and pointed: the
   port corpus omits 90.7% of the whole-view corpus, and that 90.7% is precisely
   the part with zero executable cases.

4. **Declaring a `limitation` for `corpus-port` on `M07` so the round would go
   green.** The mechanism exists and would have been accepted by the driver's
   shape. **Rejected because it would have been false**: the only witness form
   available is "this instrument executed zero accepting `Reserve` cases", and
   this instrument executes 294. Writing it would have been a suppression key
   with better manners — the precise defect EVAL-SUPPRESS was opened to remove —
   and the driver would rightly have rejected it. The control is reported RED
   and the missing vocabulary is filed as PA-03-DF-02.

One further thing was rejected on the prompt side. The manifest-declaration ask
was **not folded into the `HEXAGONAL-ASK:BEGIN/END` block**, which is what the
ticket's wording invites. Arm B of the running A/B inlines that block verbatim,
and PA-01 sealed arm B at 105 unique content lines against arm C's 109 as the
control separating "hexagonal helped" from "a longer ask helped". Editing the
block would move a sealed number in a live experiment. It ships as a second
dispatchable block, `PORTS-IN-THE-MANIFEST:BEGIN/END`, with the reason recorded
in the file.

## Evidence in this directory

| file | what it is |
| --- | --- |
| `kill-table-arm-a.json`, `kill-table-arm-b.json` | the two arms, eight instruments, with the control verdicts and per-action executability |
| `determinism-arm-a-run-2.json` | the second independent run; zero keys differ from run 1 |
| `smoke-reference.json` | `corpus-port` alone against the `reference/` tree and PA-01's 15-row catalogue, showing both positive controls red |
| `port-corpus-docs.md` | the generated package's own `docs.md`, carrying the per-port table |
