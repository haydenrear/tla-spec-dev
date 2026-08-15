# `CA-07` results — `CA-06-DF-02` consumed, and what consuming it exposed

**Subject, named by the epic owner at `schedule_revision 2`: `CA-06-DF-02`.**
The negative corpus keyed each case's `params` by the TLA+ **formal** parameter
names while the positive corpus keys them by the names the module **declares**
in its own action marker — the names every shipped adapter reads. All 11
negative cases the generator emits for `examples/distributed_history` died on
`KeyError` before asserting anything. **The measured yield of `--negative-cases`
on a real subject was zero cases *executed*.**

---

## 1. The constraint that blocked `CA-06` does not bind, and here is why

`CA-06` filed this and deliberately did not fix it. Its stated reason:

> *"Re-keying the arguments CHANGES WHAT A CORPUS CONTAINS … the same rule
> forbids `CA-06` changing the keys of a corpus under the one fixture whose
> sealed kill tables are quoted throughout this programme."*

**That caution was right, and the row's own `why_out_of_scope` asserted as
settled fact something the row's own `suggested_fix` prescribed a check for.**
The check is quoted in §1a below; `CA-07` ran it, and it came back the other
way. **The gap is between two fields of one row** — not, as this document first
said, between the row and a reader nobody had thought to be.

The names the positive corpus uses are **not** recovered from the state pair
at all. They are
read out of the module's own action-marker record —
`params_from_action_marker`, `generate_cases_from_tlc_dump.py:414` — which is
why `Internal.tla:28` writing

```tla
/\ lastInternalAction' = [name |-> "AddCartItem", params |-> [account |-> a, sku |-> sku]]
```

is what makes `account` the adapter's key.

**`examples/validation/ab/model/QuotaLedger.tla` declares no action marker at
all.** It therefore declares no argument names, has nothing to re-key, and its
corpus cannot move. **Measured rather than argued** — the fixture's negative
corpus was generated on both keyings and diffed:

```
BEFORE  emitted: 118 case(s) from 47682 candidate triples
AFTER   emitted: 118 case(s) from 47682 candidate triples
$ diff -r <before>/quota_neg <after>/quota_neg
        (only case_coverage.json's `source` field — the scratch path each run wrote to)
```

`specs/results/scorecards/cut-the-apparatus/CA-07/quota-ledger-corpus-unchanged.txt`,
and **regenerated independently by the reviewer of PR #269**, who got the same
118 cases and the same 4,028 cross-checked edges on both keyings.
**No sealed cell can move.**

**Stated precisely, because an earlier version of this sentence was false.**
The fix is inert on every model **that declares no action marker** — *not* on
"every model that predates it". `examples/distributed_history` predates it and
is precisely the model it is not inert on; that is the entire point of the
change. The evidence file said it correctly and this section did not.

### 1a. `CA-06`'s `suggested_fix`: one clause wrong, one clause right

**The clause that is wrong:**

> *"Map each formal parameter to its recovered name through the `ActionRecipe`
> the pass already holds."*

**An `ActionRecipe` is keyed by the formal names.** `build_recipes`
(`infer_action_params.py:402`) builds one `ParamRecovery` per formal parameter
of the definition, and `infer_params` returns `{recovery.name: value}` — so on
`AddCartItem(a, sku)` the recipe can only ever say `a`. It cannot supply
`account`, because nothing in the recovery machinery has ever seen that word.
A ticket that followed **that clause** literally would have got nowhere.
Filed as `CA-07-DF-01`.

**The clause that is right, and it is the best instruction on the row:**

> *"…and re-run `QuotaLedger`'s sealed negative kill table on BOTH keyings to
> show the sealed cells do not move. If they do move, the keying is
> load-bearing and that is a bigger finding than this one."*

**That is exactly the check §1 reports, and `CA-07` ran it because the row
asked for it.** Corrected on the review of PR #269, which was right that
"the premise was never checked" implied nobody had thought of the check when
the row itself specifies it. **What is notable is that it was the first
`suggested_fix` on this ledger to be *executed* rather than quoted — not that
it was unimagined.**

---

## 2. The same defect had a second face, and it disabled a soundness check

The negative pass runs a **cross-check before it emits anything**: every
enabled edge in the dump whose arguments were fully recovered is re-evaluated
at its own source state, and an action whose guard the evaluator gets wrong is
dropped rather than trusted — *"the corpus never states something the checker
itself has just been shown to get wrong."*

That check compares `set(params_for_case(...))` against
`set(signature.params)`: **declared names against formal names.** On every
model that declares an action marker the two sets never matched, every edge hit
`continue`, and **the check examined nothing.**

`CA-06`'s own sealed report prints the zero and nobody read it:

```
cross-check:  0 ENABLED edge(s) with fully recovered arguments re-evaluated ...
```

over a dump holding **141** such edges. Measured at this branch:

| | `examples/distributed_history` | `QuotaLedger` |
|---|---:|---:|
| before | **0** edges cross-checked | 4,028 |
| after | **141** edges cross-checked, **0** disagreed | 4,028 |

`QuotaLedger` was never affected — it declares no marker, so its key sets
always matched. **The check has been vacuous on exactly the models it was
never measured on, which is `CA-06-DF-01`'s shape a second time.** Repairing
it suppressed no action and changed no corpus: 0 of 141 disagreed.

### 2a. And **this repair is routed, not consumed** — `CA-07-DF-05`

**The sharpest thing either this ticket or its review produced, and it is
against this ticket.**

**Nothing in the repository protects the cross-check repair.** The reviewer of
PR #269 deleted the 11-line `formal_for` remap and re-ran the shipped
conformance case: **5 passed.** Every call in
`tests/test_negative_corpus_adapter_conformance.py` passes `edges=[]`, so the
cross-check loop body never executes, and no other generator test asserts a
nonzero `crosschecked_edges` either.

**So `CA-07`'s production delta splits in two and only one half is consumed:**

| half of `CA-06-DF-02` | evidence | verdict |
|---|---|---|
| the **emission** keying | back it out and the shipped case goes red on `KeyError` | **CONSUMED** |
| the **cross-check** remap | `cross-check: 0` → `141, 0 disagreed` in a transcript | **ROUTED** |

**Roughly a third of the production delta lands as a transcript, not as an
executable check** — and the transcript is a real measurement on a real
subject, which is exactly what makes it seductive. `CA-05-DF-03` measured that
the disposition instrument cannot tell consumption from routing. **This is that
finding arriving on a real input, produced by the epic's own consumption
ticket, and nothing in the mechanism noticed.** An independent reviewer
deleting code and re-running did.

**Not closed here, on the epic owner's instruction.** Adding the missing
coverage after review would erase the measurement the review produced, which is
worth more than the coverage. What it would take is written down in
`CA-07-DF-05`'s `suggested_fix`: one edge whose after-state carries a populated
action marker, and `assert report.crosschecked_edges == 1`.

---

## 3. What the fix buys, stated exactly, and what it does not

**It buys execution.** The 11 cases now reach the implementation with real
arguments. `negative-corpus-execution-before.txt` → `-after.txt`:

```
BEFORE   ERROR: 11 batched case executions failed
         case_0094_add_cart_item_rejected via AddCartItem: KeyError: 'account'   (x7 'account', x4 'order')

AFTER    ERROR: 11 batched case executions failed
         case_0094 ... AssertionError: adapter output mismatch:
           {'status': 404, 'body': {'error': 'account_not_found'}}
           != StateGraphRejection(action='AddCartItem', params={'account': 'acct-1', 'sku': 'sku-1'}, ...)
```

**It does not buy a green run, and reporting it as one would be false.** All 11
still fail. **But the failures are now informative, and they split two ways —
which is the first thing `--negative-cases` has ever said about a subject
outside the house fixture.** Read off `-after.txt`:

| cases | what the implementation did | what this is |
|---|---|---|
| `AddCartItem` ×2, `Checkout` ×4 | **refused** — `404 account_not_found`, `409 empty_cart` | the adapter has **no rejection contract**: it returns `{status, body}` and the corpus expects a `StateGraphRejection`. A reporting gap, not a behaviour gap |
| `CreateAccount` ×1 | **`201 Created`** on an account that already exists | the model guards `a \notin accounts`; `domain.py:88` is `insert or ignore` and always returns 201. **The implementation does not refuse.** |
| `ProjectOrder` ×4 | **`200 {"processed": 0}`** on an order not in the outbox | the model guards `o \in outbox`; `domain.py:145` returns a no-op success. **The implementation does not refuse.** |

**Five of eleven are a model/implementation divergence in behaviour, not in
output shape**, and they were surfaced by running a mechanism that has never
run on this subject before. **They are filed (`CA-07-DF-02`) and not fixed.**
Whether the model over-constrains or the implementation under-refuses is the
owner's call, and *"file findings, fix nothing during a measurement"* applies:
a ticket that repaired the divergence it just measured would have no
measurement left to report.

**And the honest limit on that claim.** Because the adapters carry no rejection
contract at all, this run **cannot separate** "refuses, cannot say so" from
"does not refuse" by the oracle alone — the split above was read off the
returned status codes and confirmed against `domain.py` by hand. **A run that
could make the distinction mechanically does not exist yet.**

---

## 4. The regression, and the two commands that check it

`tests/test_negative_corpus_adapter_conformance.py` — **255 lines, 5 cases, and
it did not exist.** It is an **adapter conformance case** in the owner's §4
shape: it takes what the generator emits for the real subject and hands it to
the adapter classes that subject's own `case_adapters.toml` names.

**Why a conformance case and not a generator unit test.** The defect is a
disagreement between two artifacts — what the corpus emits and what the adapter
reads — and only one of them lives in `scripts/`. **A test of the generator
alone is green on either keying, because either keying is self-consistent.**
That is how this survived three epics.

**Neither side of the central assertion is written in the test.** The left is
what `negative_cases_for_corpus` emits; the right is the corpus already checked
in at `examples/distributed_history/specs/generated/spec_unit/`, which every
adapter in `case_adapters.toml` was written against.

**A sceptic runs these two, from the worktree root, and needs to trust nothing
in this document.** `14fbb10` is the epic tip this branch was cut from and `HEAD` is the ticket commit:

```bash
git checkout 14fbb10 -- scripts/generate_cases_from_tlc_dump.py \
  && uv run --with pytest --with pyyaml -m pytest tests/test_negative_corpus_adapter_conformance.py -q
#   -> 3 failed, 2 passed     KeyError: 'account' x7, KeyError: 'order' x2

git checkout HEAD    -- scripts/generate_cases_from_tlc_dump.py \
  && uv run --with pytest --with pyyaml -m pytest tests/test_negative_corpus_adapter_conformance.py -q
#   -> 5 passed
```

Transcripts: `regression-red.txt`, `regression-green.txt`.

### What the test asserts, and what it deliberately does not

| case | asserts |
|---|---|
| `..._names_its_arguments_as_the_committed_corpus_does` | per action, the emitted key set equals the committed corpus's key set |
| `..._shipped_adapters_execute_every_negative_case` | every case reaches the implementation through the adapter's real `run` entry point |
| `..._declares_no_action_marker_keeps_its_formal_names` | `QuotaLedger` is untouched — the sealed-table guard |
| `..._reaches_every_action_the_model_lets_it_negate` | the corpus is not accidentally empty, which would make the keying assertion vacuous |
| `..._states_carry_exactly_the_modules_variables` | the drift guard on the one transcribed input |

**It does not assert that a negative case passes**, and that omission is
`MF-020` being obeyed rather than an oversight. Making the 11 pass requires
either changing the adapters or changing the model — tuning the subject to the
instrument, on a defect discovered while measuring. The assertion is scoped to
what `CA-06-DF-02` says: **the adapter can read the arguments the corpus
names.**

### `R1`, and the one thing that is transcribed

The subject is `examples/distributed_history` — this repository's own worked
example. Its `Internal.tla`, its `Internal.cfg` constants, its committed
corpus, its `case_adapters.toml`, its adapter classes and its `EcommerceStore`
are all the real thing.

**The one transcribed input is the pair of reachable states the cases are built
at**, because TLC produces a state graph and a unit test may not run one. Both
are the model's own — `InternalInit`, and the state one `CreateAccount` later —
and a fifth case fails if the module's variables move underneath them. The two
states reproduce **every one of the four refusal reasons** the full 11-case TLC
run found (`a \in accounts`, `Len(carts[a]) > 0`, `a \notin accounts`,
`o \in outbox`).

---

## 5. Price

| surface | `14fbb10` | here | delta |
|---|---:|---:|---:|
| `scripts/` | 26,756 | 26,837 | **+81** |
| `examples/validation/` | 14,854 | 14,854 | **0** |
| `tests/` | 30,738 | 30,993 | **+255** |
| **card** (`serve \| wc -c`) | 6,281 | **6,281** | **0**, `sha256:2d7d4a0506d9b259` |

`GOAL-apparatus-cut`'s `expected_effect` for this ticket is *"A SMALL INCREASE
IS EXPECTED AND ACCEPTED — one action or one conformance case. Price it."*
This is one conformance case and one generator function. **+81 in `scripts/`,
+255 in `tests/`, nothing in `examples/validation/`, and the card did not
move.** Never reported as one number. Detail in `line-counts.txt` and
`PRICE-TABLE.md`.

---

## 6. Model delta

**`direction=zero`.** No `.tla`, no `.cfg`, no `spec_manifest.yaml` and no
`case_adapters.toml` changed:

```bash
git diff 14fbb10 -- specs/program_model specs/current \
    specs/desired_program_model/TlaSpecDevCli.tla \
    specs/desired_program_model/spec_manifest.yaml \
    specs/desired_program_model/case_adapters.toml     # -> empty
```

**So TLC was not run, and that is legitimate rather than skipped**: no
variable, action or bound moved. `specs/tickets/CA-07/current` equals `desired`
with no edit, because this ticket's delta touches no seeded path.

**The plan's `model_delta_expectation` for `CA-07` reads "EXPECTED. This
ticket's whole purpose is a model or adapter delta that did not exist before."**
The delta that did not exist before is **the adapter conformance case** — the
second of the two shapes the ticket's own objective names. **Stated plainly
because `CA-06` was corrected for exactly this phrasing**: no model work was
done here, and none was called for by the subject the owner named.
