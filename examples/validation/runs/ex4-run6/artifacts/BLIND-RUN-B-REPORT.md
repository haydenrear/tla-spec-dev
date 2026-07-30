# QA report — case modules on the `pipeline` service

Author: QA engineer, first contact with this codebase.
Date: 2026-07-30.

Everything below was run. Where a number is quoted, the command that produced it
is quoted with it. Where something did not work, it is in §5.

Environment used throughout:

```bash
PY=.../ev03/venv/bin/python
TOOLS=.../ev03/blind/toolchain
export PATH="$HOME/.skill-manager/bin/cli:$PATH"
cd .../ev03/blind/runB
```

Artifacts shipped in this directory:

| file | what it is |
|---|---|
| `specs/case_modules/Scenario_IntakeToDelivery.{tla,cfg}` | case module 1 — a **slice** |
| `specs/case_modules/Scenario_DurableOutcome.{tla,cfg}` | case module 2 — a **Given** |
| `specs/program_model/spec_manifest.yaml` | `case_modules:` block added (only edit to a pre-existing file) |
| `specs/program_model/case_adapters_slice.toml` | **added under protest**, see §2 |
| `mutant_catalogue.toml` | 16 seeded bugs, exact `find`/`replace` |
| `mutant_run.py` | green control + apply/run/restore harness |
| `mutant_results.json` | machine-readable kill matrix |
| `out_view/`, `out_cm/`, `out_gen2/` | generated corpora (gen 1, gen 1, gen 2 for the determinism check) |

---

## 0. Provenance of the aspect list — read this before the numbers

`prompts/aspect_decomposition.md` Step 0 requires the aspect list to come from
the model author, and requires me to say so when it does not.

**No author was in the loop.** There was nobody to elicit from. What I used
instead is the closest thing this project has to a written product statement —
`README.md`, "What the service promises":

> An item that arrives is accepted, queued, and handed to delivery. A delivery
> either succeeds or fails, and **a failed item is recorded as failed**. Either
> way **the ledger records each outcome**, and the ledger is persisted through
> the store port so the record survives a restart.

I carved two aspects on the two sentences of that paragraph. That is a *document*,
not a *person*, and it is a document I go on to show is **wrong about the
program** (§6.1). So:

> **This decomposition is UNREVIEWED.** Treat the aspect carving as a proposal
> from someone who read the README, not as validated product structure. The
> `Source` column below says exactly that, and nothing in the toolchain checked
> it — `case_modules.py validate` exited 0 on it without a murmur.

I also wrote the `form: given` predicate myself, from the model, having read
`Pipeline.tla`. Per `references/case_modules.md` ("The authoring asymmetry") that
is an inside-out artifact and I am not claiming otherwise: the *claim* came from
the README, the *predicate* came from having the model open.

### Step 1 — the action surface, from a command

```bash
$PY $TOOLS/scripts/tla_spec_dev.py --spec-root specs analyze architecture \
  specs/program_model/Pipeline.tla specs/program_model/Pipeline.cfg --format json | ...
# (a) measured:  Accept Deliver Enqueue Fail Record          -> N = 5
# (b) declared internal in actions.yml: Accept Deliver Enqueue Fail Record -> 5
```

Reconciliation is clean in both directions: no measured action missing from
`actions.yml`, no declared action missing from the module. No `Stutter`,
`Terminating` or explicit no-op disjunct exists to drop. **N = 5, M = 5, N == M.**

### Step 2 — the table

| # | Action | Aspect | Given (user's voice) | Form | Asserted irrelevant | Source |
|---|---|---|---|---|---|---|
| 1 | Accept | intake to delivery | "nothing has happened yet; work is arriving" | slice | — | README ¶1 sentence 1 (**no human author**) |
| 2 | Enqueue | intake to delivery | as above | slice | — | as above |
| 3 | Deliver | intake to delivery | as above | slice | — | as above |
| 4 | Fail | durable outcome | "an item has been delivered and is waiting for its outcome" | given | the outcome of a delivered item is independent of the intake path (`inbox`/`accepted`/`queue` configuration) it was delivered from | README ¶1 sentences 2–3 (**no human author**) |
| 5 | Record | durable outcome | as above | given | as above | as above |

---

## 1. Authoring cost vs. yield

### What a human wrote

| artifact | total lines | non-comment lines |
|---|---|---|
| `Scenario_IntakeToDelivery.tla` | 19 | 8 |
| `Scenario_IntakeToDelivery.cfg` | 6 | 6 |
| `Scenario_DurableOutcome.tla` | 38 | 14 |
| `Scenario_DurableOutcome.cfg` | 6 | 6 |
| `case_modules:` block in `spec_manifest.yaml` | 20 | 16 |
| **total authored for the case modules** | **89** | **50** |
| `case_adapters_slice.toml` (forced, §2) | 35 | 16 |

The `.tla` line counts are dominated by prose: the Given's claim is 14 lines of
comment against 14 lines of predicate, and that ratio is correct — the claim is
the reviewable half.

### What came back

| corpus | states | cases | generation wall clock |
|---|---|---|---|
| `Pipeline` (whole view — pre-existing, 0 new lines) | 121 | **330** | 0.95 s |
| `Scenario_IntakeToDelivery` (slice) | 25 | **50** | 0.85 s |
| `Scenario_DurableOutcome` (given) | 16 | **24** | 0.90 s |
| **case modules, union** | 41 | **74** | 1.75 s |

**89 hand-written lines → 74 distinct cases** (0.83 cases per authored line; 1.48
per non-comment line). 330/330, 50/50 and 24/24 cases carry fully recovered
arguments; 0 `UNCHECKED`.

### Actions spent

15 actions from "never written one" to "corpus running against the shipped
adapters", counted honestly:

| # | action | outcome |
|---|---|---|
| 1–4 | write 2 `.tla` + 2 `.cfg` | first try |
| 5 | edit `spec_manifest.yaml` | first try |
| 6 | `case_modules.py validate` | exit 0 first try |
| 7–8 | 2 × `generate_cases_from_tlc_dump.py` | first try |
| 9 | `case_modules.py coverage` | exit 0, `UNCOVERED: none` |
| 10–11 | run **Given** corpus, both shipped mappings | both green |
| 12–13 | run **slice** corpus, both shipped mappings | **both refused** (§2) |
| 14 | write `case_adapters_slice.toml` | forced workaround |
| 15 | re-run slice corpus | green |

Zero actions were lost to my own errors. Three (12, 13, 14) were lost to CM-F5.

### The economics do not work on this project

The measured evidence in `references/case_modules.md` sells case modules on cost:
1m 23s → 2.2s. Here the whole view generates in **0.95 s** and executes 330 cases
in **0.23 s**. There is nothing to save. On this project a case module is worth
authoring for what it *documents* — a named aspect and a written, falsifiable
claim — and for nothing else. The `case_modules:` block plus the claim comment is
genuinely the best-written statement of intent in the repository, and it is 34
lines. That is the honest value proposition here, and it is not the one the
reference leads with.

### Coverage report

```
action   view corpus  Scenario_DurableOutcome  Scenario_IntakeToDelivery  modules total
Accept   22           0                        10                         10
Deliver  66           0                        20                         20
Enqueue  110          0                        20                         20
Fail     88           16                       0                          16
Record   44           8                        0                          8

UNCOVERED: none
```

The per-action losses are large — `Enqueue` 110 → 20, `Fail` 88 → 16 — because
the slice never reaches before-states that need `Fail`/`Record` to have run, and
the Given collapses the entire intake fan-in to one state. §3 measures what that
costs in kills.

---

## 2. Does it run against the existing adapters?

**The Given: yes, unchanged, against both shipped mappings.**

```
run_generated_case_adapters.py out_cm/spec-unit/Scenario_DurableOutcome_cases \
  --mapping specs/program_model/case_adapters.toml --spec-dir specs/program_model \
  --view internal --batch --import-root . --import-root ./generated
# validated 5 adapter mappings for 3 labels
# executed 24 cases in batch          (exit 0)
```

Same result with `case_adapters_corpus_only.toml`. No adapter, provider,
projector or mapping was touched.

**The slice: no. Both shipped mappings refuse it.**

```
# --mapping case_adapters.toml            -> exit 1
# --mapping case_adapters_corpus_only.toml -> exit 1
ERROR: invalid semantic effect provider configuration: provider configured for
       semantic effect port(s) not required by any selected case: LedgerStorePort
```

This is **CM-F5**, documented as OPEN in `references/case_modules.md`. What the
doc does not say, and what this project makes concrete: CM-F5 is not survivable
by *choosing the other mapping*. `case_adapters.toml` and
`case_adapters_corpus_only.toml` differ only in **which** `LedgerStorePort`
provider they bind — both bind one — so every mapping the project ships is
refused by every slice that excludes `Record`, and `Record` is the only action
carrying the port. A project with one effect port and a slice that does not enter
it has zero working mappings, not one.

**What I changed, and why.** I added a third mapping,
`specs/program_model/case_adapters_slice.toml`: a byte-for-byte copy of
`case_adapters.toml` with the `[effect_providers.LedgerStorePort]` block deleted.
Nothing else in the project changed — not one adapter, not one provider, not one
line of `pipeline/`. With it the slice runs:

```
# validated 5 adapter mappings for 4 labels
# executed 50 cases in batch          (exit 0)
```

**This is a finding, and it is worse than a papercut.** The reference's central
selling point is "a case module is a new *entry*, never a new *boundary* — it
needs no adapter of its own". For the slice form on this project that claim is
false: I had to add a mapping file, and the mapping I added is a **strictly
weaker instrument** — it has no durable-write oracle at all. §3 shows the cost:
the slice's 3 kills all come from state comparison; the three `durable_write`
mutants are invisible to it by construction, because the thing that would have
seen them is the provider I was forced to delete. Anyone reading a slice's green
run without reading its mapping will over-read it.

---

## 3. Does it catch anything?

### Instruments (§3b: every kill number below is named by mapping)

| instrument | corpus | mapping | cases |
|---|---|---|---|
| `view_checking` | `Pipeline_cases` | `case_adapters.toml` (content-asserting store) | 330 |
| `view_silent` | `Pipeline_cases` | `case_adapters_corpus_only.toml` (silent store) | 330 |
| `cm_durable_checking` | `Scenario_DurableOutcome_cases` | `case_adapters.toml` | 24 |
| `cm_durable_silent` | `Scenario_DurableOutcome_cases` | `case_adapters_corpus_only.toml` | 24 |
| `cm_intake_slice` | `Scenario_IntakeToDelivery_cases` | `case_adapters_slice.toml` (**no provider** — CM-F5) | 50 |
| `pytest` | — | — | 8 tests |

### Green control (first, before any mutant)

```
GREEN CONTROL (unmutated tree)
  view_checking          PASS  executed 330 cases in batch
  view_silent            PASS  executed 330 cases in batch
  cm_durable_checking    PASS  executed 24 cases in batch
  cm_durable_silent      PASS  executed 24 cases in batch
  cm_intake_slice        PASS  executed 50 cases in batch
  pytest                 PASS  8 passed in 0.01s
```

The harness aborts if this is not green. It was green.

### Kill matrix — 16 mutants, `K` = killed, `.` = survived

Catalogue: `mutant_catalogue.toml` (id, class, path, exact find, exact replace).
Reproduce with `$PY mutant_run.py`. `mutant_run.py` asserts each `find` occurs
**exactly once** in its file, so a stale catalogue fails loudly rather than
mutating nothing and scoring a free survival.

| id | class | site | view_checking | view_silent | cm_durable_checking | cm_durable_silent | cm_intake_slice | pytest |
|---|---|---|---|---|---|---|---|---|
| M01 | guard_accepts | `Inbox.accept` membership check removed | . | . | . | . | . | **K** |
| M02 | missing_write | `Inbox.accept` never clears inbox | **K** | **K** | . | . | **K** | **K** |
| M03 | guard_accepts | `WorkQueue.enqueue` dedupe removed | . | . | . | . | . | **K** |
| M04 | guard_rejects | `enqueue` checks `pending` not `accepted` | **K** | **K** | . | . | **K** | **K** |
| M05 | ordering | queue becomes LIFO (`insert(0)`) | . | . | . | . | . | . |
| M06 | missing_write | `WorkQueue.take` never removes | **K** | **K** | . | . | **K** | **K** |
| M07 | guard_accepts | `Dispatcher.deliver` ignores `failed` | . | . | . | . | . | **K** |
| M08 | missing_write | `fail` does not release from `delivered` | **K** | **K** | **K** | **K** | . | **K** |
| M09 | guard_accepts | `Journal.record` loses append-only guard | . | . | . | . | . | **K** |
| M10 | guard_rejects | `Journal.record` never fires | **K** | **K** | **K** | **K** | . | **K** |
| M11 | ordering | ledger prepends instead of appends | . | . | . | . | . | . |
| M12 | wrong_value | ledger records `item.upper()` | **K** | **K** | **K** | **K** | . | **K** |
| M13 | durable_write | `_persist` never writes | **K** | . | **K** | . | . | . |
| M14 | durable_write | persists `entries[:-1]` (stale) | **K** | . | **K** | . | . | . |
| M15 | durable_write | persist happens *before* the append | **K** | . | **K** | . | . | . |
| M16 | guard_rejects | `fail` refuses while the queue is non-empty | **K** | **K** | . | . | . | . |

### Scores

| instrument | killed / 16 | rate |
|---|---|---|
| `view_checking` (330 cases, `case_adapters.toml`) | 10 | 62.5% |
| `pytest` (8 hand-written tests) | 10 | 62.5% |
| **case modules, union** (`cm_durable_checking` ∪ `cm_intake_slice`) | **9** | **56.3%** |
| `view_silent` (330 cases, `case_adapters_corpus_only.toml`) | 7 | 43.8% |
| `cm_durable_checking` (24 cases, `case_adapters.toml`) | 6 | 37.5% |
| `cm_durable_silent` (24 cases, `case_adapters_corpus_only.toml`) | 3 | 18.8% |
| `cm_intake_slice` (50 cases, `case_adapters_slice.toml`) | 3 | 18.8% |
| `view_checking` ∪ `pytest` | 14 | 87.5% |
| case modules ∪ `pytest` | 13 | 81.3% |
| **killed by nothing** | **2** (M05, M11) | — |

### What the matrix actually says

**(a) 74 case-module cases reached 9 of the whole view's 10 kills.** Nine tenths
of the whole-view corpus's yield, from 22% of the cases and 89 hand-written
lines. That is a real result and it is the best thing in this report.

**(b) The one it lost is exactly the one the doctrine predicts it will lose, and
I seeded it deliberately to measure that.** M16 makes `Fail` misbehave *only when
the work queue is still non-empty*. `Scenario_DurableOutcome`'s Given asserts
`queue = {}`, so its 24 cases can never reach that before-state;
`Scenario_IntakeToDelivery` never enters `Fail`. Only the whole view, which
enumerates 121 states instead of 41, gets there. If M16 were not in the catalogue
the case modules would score identically to the view and the report would be
quietly misleading. **Do not read a "case modules == view" result off a catalogue
that has no cross-aspect mutant in it.**

Precise wording matters here. Every generated case is *one* action applied to a
materialized before-state — there are no call sequences in any corpus, view or
module. So "cross-aspect interleaving", on this project, is not about orderings;
it is about **before-state diversity**. The view reaches states the modules'
Given asserts away, and M16 lives in exactly that gap.

**(c) The two mappings are genuinely different instruments, and the gap is
precisely the `durable_write` class.** `case_adapters.toml` kills M13/M14/M15;
`case_adapters_corpus_only.toml` kills none of them, on the same 330 cases.
Those three mutants leave the in-memory ledger perfectly correct and corrupt only
the persisted bytes — the after-state comparison cannot see them, and only
`ContentAssertingLedgerStoreProvider` can. A team that runs `corpus_only` is
running a 330-case suite with **no durable-write oracle**, and the README's
promise that "the record survives a restart" is then unchecked. The mapping
choice is worth 3 kills, 30% of this instrument's total yield.

**(d) The generated corpus is structurally blind to over-permissive guards.**
Every one of M01, M03, M07, M09 — "a guard that accepts something it should
reject" — survived **all five** corpus instruments and was killed only by
`pytest`. The cause is mechanical and I verified it:

```bash
grep -o "'status': '[a-z]*'" out_view/spec-unit/Pipeline_cases/cases.py | sort | uniq -c
#  330 'status': 'applied'
```

All 330 cases expect `status: applied`. The corpus is built from *enabled*
transitions only; it never once asks the program to reject a call. `tlc_projection.py`
says so in its own docstring — "`status` is always 'applied' for a generated
transition" — but frames it as catching implementations that *reject where the
model fires*, and does not say the converse is unreachable. This is not a case
module problem; it is a property of the whole generation approach on this
project, and it is the single largest blind spot found. **The generated corpus
and the hand-written suite are complements, not substitutes.** Their union kills
14/16; neither alone exceeds 10/16.

**(e) Two bugs are invisible to every instrument, and both are ordering.**
`WorkQueue` documents "items in insertion order" and `Journal` documents an
"append-only record". Neither contract is checked by anything:

- the model uses **sets** (`queue \subseteq Items`), so order is not in the model;
- `adapters.py:project()` returns `frozenset(self.queue.items)` and
  `frozenset(self.journal.entries)` — order is discarded before comparison;
- `ContentAssertingLedgerStoreProvider` compares `sorted(actual) != expected` —
  order is discarded again on the durable side;
- `tests/test_behavior.py` only ever asserts single-element lists.

So M05 (queue becomes LIFO) and M11 (ledger prepends) pass every gate this
project has. A FIFO guarantee and an append-only guarantee are stated in
docstrings, relied on by the word "queue" and the word "journal", and verified by
nobody. Fixing this needs a model change (sequences, not sets), not a test change
— which is precisely the kind of thing a spec-first toolchain is supposed to
surface, and did not.

---

## 4. Determinism

**Generation: byte-identical.** Generated everything a second time into
`out_gen2/` and compared:

- `cases.py`, `types.py`, `validators.py`, `doubles.py`, `docs.md`,
  `param_recovery_audit.md` — **identical for all three packages** (18/18 files).
- the TLC state graph `.dot` — identical.
- `case_coverage.json` — differs in **one** field, `"source"`, which is the
  absolute output path. Expected, since `--out` differed. Nothing else.

**Execution: identical.** Each instrument run twice; stdout byte-identical
(`executed 330 / 24 / 50 cases in batch`). Also checked **under a mutant** (M13),
where output is long and content-bearing: the two runs produced identical
`EFFECT_FUZZ_FAILURE` blocks, including the derived provider seed
(`126719035589889030170442443648605559541`, `root_seed: 0`,
`seed_version: tla-spec-dev/effect-seed/v1`) and an exact copy-pasteable replay
command. The failure output is the best-designed thing I touched all day.

The whole 16-mutant harness was run twice (once at 15 mutants, once at 16) and
every shared row scored identically.

---

## 5. Friction — commands and docs that did not behave as written

**F1 — CM-F5 has no survivable configuration on this project, and the doc implies
it does.** `references/case_modules.md` says the workaround is "a second mapping
file with the provider removed". This project ships *two* mappings and **both**
bind `LedgerStorePort`, so the slice is refused by 2/2 shipped instruments. The
reference's headline claim, "a case module needs no adapter of its own", is false
for the slice form here. Cost: 3 of my 15 actions, plus a 35-line file, plus a
permanently weaker instrument. Detail in §2.

**F2 — `--effect-report PATH` silently does nothing.** I passed
`--effect-report eff_1.json` on a run whose action (`Record`) declares
`effect_ports: [LedgerStorePort]` and whose mapping binds a provider for it. No
file was written. No warning. No message. Exit 0. Tracing it:
`run_generated_case_adapters.py:1461` gates the report on
`declarations is not None and bool(declarations.ports)`, and
`load_effect_declarations_for_spec` (line 1420) looks for an **`effects:`** block
in `actions.yml` or `spec_manifest.yaml`. This project has neither — it has
`ports:` in the manifest and `effect_ports:` per action in `actions.yml`. The
code comment two lines above the gate says *"The report is written
unconditionally — it is ticket evidence whether the verdict is clean or not"*,
which is not what the code does. A flag that takes a path and writes nothing
should say "this spec declares no `effects:` block, so there is nothing to
report", not exit 0 in silence. **Not fixed, per instruction.**

**F3 — `analyze architecture` silently substitutes its own component partition
for the one the project declares.** Run as `prompts/aspect_decomposition.md`
Step 1 prints it — no `--components` — the tool reports an **emergent**
2-component partition (greedy modularity, Q = 0.194) and concludes:

```
single_writer_violations: []
spanning_actions: []
ports: [{"id":"P1","between":["C1","C2"],"actions":["Enqueue"]}]
```

The project declares a 3-component partition in
`specs/program_model/architecture_components.yaml`. Passing
`--components specs/program_model/architecture_components.yaml` gives the
opposite answer:

```
single_writer_violations: [delivered (Deliver,Fail), queue (Deliver,Enqueue)]
spanning_actions: [Deliver writes C1: queue; C2: delivered in one step]
ports: [P1 ingest<->dispatch via Deliver, P2 dispatch<->ledger via Record]
```

The second answer is the one `Pipeline.tla`'s own comments assert
("*the ingest <-> dispatch handoff … Port AND single-writer violation, by
construction*", "*the dispatch <-> ledger port*"). The default run erases a
deliberate, documented architectural violation and blames a different action for
a boundary crossing. Worse: `spec_manifest.yaml` contains the comment
*"The component partition lives in its own file,
specs/program_model/architecture_components.yaml"* — prose the tool cannot read.
The `--manifest` path only honours an inline `architecture:` block. A first-day
engineer following the prompt verbatim gets the wrong architecture picture and no
indication that a declared one was ignored. `partition.source` does say
`"emergent"` in the JSON, but the text output is what a human reads and the
prompt's one-liner pipes straight past it.

**F4 — the prompt's Step 1 command needs `--spec-root`, and the doc's warning is
about the wrong flag.** `prompts/aspect_decomposition.md` warns that
`--spec-root` does *not* resolve the positional `.tla/.cfg`. True, but the more
useful warning is that the command is *also* useless without `--components` (F3).
Both were needed here and the prompt supplies only one.

**F5 — `--out` resolution is a genuine trap and the mitigation is a printed
note, not a guard.** A relative `--out generated` from the repo root writes into
`specs/program_model/generated`, silently landing generated corpora inside the
spec tree. I used absolute paths throughout because the reference told me to. The
"documented once, printed at runtime" mitigation is honest, but it is still a
default that is wrong for every invocation I would naturally type.

**F6 — the run-command exit code is easy to misread.** A refused run prints
`ERROR: …` on **stdout** and exits 1. Piping through `tail` in a shell loop
(which is the obvious thing to do — the output is 30+ lines) captures `tail`'s
exit status, and the refusal reads as a pass. This bit me once; I re-ran with
explicit `${PIPESTATUS[0]}`. Not a toolchain defect exactly, but the runner emits
enough noise on success that piping is the default behaviour and the failure mode
is silent.

**F7 — `case_modules.py coverage` never gates, which is correct, and never warns
about the thing that most needs a warning.** It reported `UNCOVERED: none` for a
decomposition whose aspect list has no author. That is exactly the failure the
prompt's own Step 0 predicts (EV-02-DF-04), reproduced here on a second fixture
by a second agent. Schema-valid, coverage-clean, provenance-free. The report even
prints the correct caveat about cross-aspect interleaving — it just has no way to
print the one about who carved the aspects.

**F8 — no scaffold.** There is no `tla-spec-dev` subcommand and no template for
the shape; `references/case_modules.md` says so deliberately. In practice this
means the `.cfg` is copy-paste archaeology: you must know to write
`SPECIFICATION <Module>Spec` and to repeat all three `INVARIANT` lines and the
`CONSTANTS` block, none of which is stated in one place. It worked first try only
because the reference's worked example is in the file.

**Things that worked exactly as documented, and deserve saying:**
`case_modules.py validate`; per-module action-scoping (CM-F2 — the slice emitted
**zero** spurious zero-case warnings for the 2 out-of-scope actions, and said so
in one clear sentence); the `EXTENDS` resolution from a sibling directory with no
flag, which printed its search path unprompted; the recorded-Given-claim echo at
generation time; parameter recovery at 404/404 across all three corpora; and the
mutant failure output with its replay command.

---

## 6. Observations about the service itself

### 6.1 The README's central promise is implemented by neither the model nor the code — and the test suite locks in the contradiction

README, emphasis original:

> A delivery either succeeds or fails, and **a failed item is recorded as
> failed**. Either way **the ledger records each outcome**.

The model:

```tla
Fail(i)   == i \in delivered /\ delivered' = delivered \ {i} /\ failed' = failed \cup {i} ...
Record(i) == i \in delivered /\ i \notin ledger /\ ledger' = ledger \cup {i} ...
```

`Fail` removes the item from `delivered`; `Record` requires it to be *in*
`delivered`. **Once an item fails it can never be recorded.** The ledger cannot
record a failure outcome at all, so "either way the ledger records each outcome"
is unimplementable in this state machine. `pipeline/ledger/journal.py:34` mirrors
the model exactly (`if item not in self._dispatcher.delivered: return False`), so
the code is faithful to the model and both are unfaithful to the README.

Three further things make this worse rather than better:

1. **The invariant is written as if the promise held.**
   `LedgerIsDownstream == ledger \subseteq (delivered \cup failed)` *permits*
   failed items in the ledger. No action can ever produce that state, so the
   invariant is strictly weaker than the truth (`ledger ⊆ delivered` actually
   holds) and passes vacuously on the half that matters. An invariant that
   admits a state the specification cannot reach is a promise nobody kept.
2. **`tests/test_behavior.py:92` asserts the same weak thing** —
   `ledger <= delivered | failed` — and is therefore satisfied by the stronger
   property that really holds. It cannot fail.
3. **`test_two_item_interleaving` bakes the violation into the suite.** It
   delivers `i1`, fails `i1`, and asserts `"ledger": ["i2"]` — i.e. it asserts
   that a failed item is **not** recorded, which is the exact negation of the
   README sentence. Whoever fixes the README's promise will have to change a
   passing test.

Someone has to decide which document is wrong. It is a one-line model change
(`Record(i) == i \in (delivered \cup failed) /\ ...`) if the README is right, or
a two-sentence README edit if the model is right. It is not a QA call.

### 6.2 FIFO and append-only are documented, load-bearing, and unverified

Covered in §3(e). `WorkQueue` says "insertion order", `Journal` says
"append-only", and every oracle in the project — model, projection, adapter,
provider — is order-insensitive. M05 and M11 pass everything. The word "queue" in
`WorkQueue` currently carries no more guarantee than "set".

### 6.3 `Enqueue` never removes from `accepted`, so `accepted` is a monotone log

`accepted` only ever grows. An item that is delivered and failed is still
`accepted`. Consistent between model and code, and probably intended, but it
means `accepted` is not "items awaiting queueing" as `Inbox`'s docstring ("what
has been accepted for processing") reads. It is why a failed item can be
re-enqueued at all (`test_failed_item_cannot_be_redelivered` relies on `Deliver`'s
`i \notin failed` guard, not on `Enqueue` refusing).

### 6.4 The Given I wrote is sound today and is a tripwire tomorrow

`Scenario_DurableOutcome`'s claim — outcome behaviour is independent of the
intake path — is true only because neither `Fail` nor `Record` reads `inbox`,
`accepted` or `queue`. That is checkable in four lines of `Pipeline.tla` today.
The moment either reads the ingest side, the Given becomes a lie and the module
will still generate cleanly and still report green. I wrote the falsification
condition into the module comment, because nothing else will notice. (M16 is,
deliberately, exactly that change — and the Given did not notice.)

### 6.5 The declared architecture is coherent when you ask for it properly

With `--components` and `--code`/`--map`, the reflexion check reports
`architecture_scan: coherent`: 8/8 modules mapped, every boundary-crossing code
edge has a declared port, every declared port realized. Good state, and the
`Deliver` spanning action is a declared, deliberate design decision rather than
drift. The problem is purely that the default invocation does not show any of it
(F3).

---

## 7. What I could not do, and why

1. **Elicit a real aspect list.** There was no author to ask. §0 stands: this
   decomposition is unreviewed, and the toolchain gave me no way to mark that
   other than prose. Any reader who trusts the aspect carving is trusting me,
   and I had been in this codebase for a few hours.

2. **Run the slice against a shipped mapping.** CM-F5, 2/2 mappings refuse. I
   worked around it with a third mapping and reported it rather than declaring
   the slice unrunnable — but I could not measure what the slice would kill *with
   a durable-write oracle attached*, because no such configuration exists for it.
   The `cm_intake_slice` row of §3 is therefore a floor, not the slice's ceiling.

3. **Measure cross-aspect interleaving.** Nothing can — the reference says so and
   it is correct. What I could do, and did, was seed M16 to price the loss in one
   concrete case (1 kill in 16). One mutant is an anecdote, not a rate.

4. **Say whether the mutant classes are representative.** 16 hand-picked mutants
   on a 186-line service. The class balance (4 `guard_accepts`, 3 `guard_rejects`,
   3 `missing_write`, 3 `durable_write`, 2 `ordering`, 1 `wrong_value`) is mine,
   and it directly determines every rate in §3 — a catalogue with two more
   ordering mutants drops every instrument's score. The catalogue is shipped as
   `mutant_catalogue.toml` precisely so the next person can disagree with my
   sampling and re-derive their own numbers.

5. **Compare against the toolchain's own kill test.** `kill_test.py` /
   `run_kill_test.py` exist and `spec_manifest.yaml` declares
   `kill_rate_floor: 0.8`. I did not run them; my 62.5% is against **my**
   catalogue and is not comparable to that floor. Nothing in this report should
   be read as this project failing its declared budget.

6. **Fix anything.** Per instruction, no toolchain defect was fixed. F2 and F3
   are the two worth a ticket.

---

## Restoration

`pipeline/` is byte-identical to its pristine state. `mutant_run.py` takes a
SHA-256 of every `pipeline/**/*.py` before the control run, asserts it after
**every** mutant, and re-asserts at exit:

```
pipeline/ digest before=8c3940b42829db6e after=8c3940b42829db6e RESTORED
```

Independently verified against an out-of-tree copy taken before any mutation
(`diff -r pipeline <pristine>` — clean), and `$PY -m pytest tests -q` →
`8 passed`. `__pycache__` directories created during the runs were removed.

Files added to `runB` and left in place: `QA-REPORT.md`, `mutant_catalogue.toml`,
`mutant_run.py`, `mutant_results.json`, `specs/case_modules/` (4 files),
`specs/program_model/case_adapters_slice.toml`, `out_view/`, `out_cm/`,
`out_gen2/`. One pre-existing file was edited: `specs/program_model/spec_manifest.yaml`
(the `case_modules:` block appended; nothing removed or changed).
