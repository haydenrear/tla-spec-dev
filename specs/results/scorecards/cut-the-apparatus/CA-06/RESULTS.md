# CA-06 — what the case-generation / adapter path costs and catches

**Subject: `examples/distributed_history`** — the README's active checked-in
example, an ecommerce backend with its own hand-written test, its own adapters,
and a TLA+ internal/external model. **Not** `ab_quota_ledger`, the house fixture
every prior kill measurement in this project used.

Measured on `feature/CA-06`, branch point `e379d6b`.

---

## 0. The tension, stated rather than resolved

The owner keeps this path and wants it dead simple. The measurement on the
record says the generated corpus has **0 unique kills against 4 the other way**,
replicated. Those are compatible only if it gets dramatically smaller.

**This ticket did not make it dramatically smaller, and says why.** The mass is
`--negative-cases` (a hand-written TLA+ expression parser and guard evaluator,
290 lines, on a 1,043-line shared TLA+ expression parser and guard evaluator)
and `--port-cases` (397 lines, on the same parser) -- 1,730 lines together. **`SM-02` measured both one epic
ago and refused exactly the widening this work order asks for**, in a shipped
test that is still green:

> `tests/test_ports_binding_removed.py` — *"TWO CLAIMS, NOT ONE. Defunding
> `[ports.*]` is supported; defunding the CORPUS is not, and the second half of
> this file exists so a later reader cannot quietly widen the first into the
> second."*

**Lesson 1 of this epic says to check the work order against the sealed record.
Checked: the record refuses the deletion.** So this ticket measured what those
mechanisms actually produce on a subject that is not the fixture they were
measured on — and that turned out to be the result.

---

## 1. The headline: the two defended mechanisms emit ZERO on a real subject

`scripts/generate_cases_from_tlc_dump.py:2211` declares
`extract_action_signatures(definitions, evaluator, next_name: str = "Next")`.
**Neither caller ever passes it** — `negative_cases_for_corpus:2438` and
`_signatures_for_regions:2794` both take the default.

The sibling module in the same directory already solves this.
`scripts/analyze_complexity.py:643` is `find_next_relation(cfg_text,
defs_by_name)`: `NEXT Name` from the `.cfg` wins, otherwise `SPECIFICATION Spec`
is followed to the `[][Next]_vars` box-action. **The generator never calls it.**

Resolved names, measured:

| model | `.cfg` says | next relation | `Next` defined? |
|---|---|---|---|
| `examples/validation/ab/model/QuotaLedger.tla` | `SPECIFICATION Spec` | `Next` | **yes** |
| `specs/program_model/TlaSpecDevCli.tla` | — | `Next` | **yes** |
| `examples/distributed_history/.../Internal.tla` | `SPECIFICATION InternalSpec` | **`InternalNext`** | **no** |
| `examples/distributed_history/.../External.tla` | `SPECIFICATION ExternalSpec` | **`ExternalNext`** | **no** |

So on the repository's own worked real-world example, run as documented:

```
negative corpus (HP-03): the DISABLED edges of every reachable state, asserted REJECTED
  emitted:        0 case(s) from 0 candidate (state, action, argument) triples
  negated:        (none)
  SUPPRESSED:  Next -- no such definition
...
corpus gate PASS: 93 internal case(s)
```

**Zero cases, and the run still prints `corpus gate PASS`.** The one line that
says why is `SUPPRESSED: Next -- no such definition`, inside a report a reader
reaches after the gate has already said PASS.

**Every measurement that defends these two mechanisms —
`SM-02`'s "guard relaxation 3 of 3, a class no other instrument has reached"
and "83.2 % executable against the whole-view corpus's 8.66 %" — is measured on
`QuotaLedger`, the one model in this repository whose next-state relation is
literally named `Next`.** That is `R1`: an instrument shipped without a
demonstrated input on a real subject. The charter counts three such; this is
the fourth and fifth.

Filed as **`CA-06-DF-01`** and fixed, because the fix is the deletion of a
hardcoded constant in favour of a function the repository already ships and
tests. It is a **no-op on both models that already worked** — `find_next_relation`
returns `Next` for each — so no sealed corpus moves.

**After the fix, on the same subject: 0 → 11 negative cases**, from 742
candidate triples, 247 proved DISABLED, collapsed to 11 by `guard-reads`.

## 1b. And the 11 cases cannot be executed

They are emitted with `params` keyed by the action's **TLA formal parameter
names** (`{'a': 'acct-1', 'sku': 'sku-1'}`), while the positive corpus emits the
**recovered** names the adapters are written against
(`{'account': 'acct-1', 'sku': 'sku-1'}`). Every one of the shipped adapters
fails:

```
ERROR: 11 batched case executions failed
case_0094_add_cart_item_rejected via AddCartItem: KeyError: 'account'
...
```

Filed as **`CA-06-DF-02`**, **not fixed**: changing the keys changes what a
corpus contains, which `HP-03` says must never happen silently, and it is a
larger decision than this ticket is scoped to make.

**So the measured yield of `--negative-cases` on a real subject is zero cases
executed, and the 1,333 lines behind it have never run outside `QuotaLedger`.**
That is reported as the result, not worked around.

---

## 2. Cost and catch on a real subject — the mutation table

**MF-020 compliance, stated before the numbers.** The mutant population is
**enumerated exhaustively** from a fixed grammar over every eligible AST site in
`ecommerce_backend/domain.py`. No mutant was chosen, named, skipped or ordered
by the author, and the population was fixed **before** §1 was discovered. The
grammar: comparison-operator swap, `not` removal, `and`/`or` swap, boolean
constant flip, integer constant `+1`, string constant rotation to the next
distinct string constant in the file.

Two instruments on the same 128 mutants:

- **suite** — `tests/test_ecommerce_backend.py`, the subject's own hand-written
  test. **42 lines, one test, one happy path.**
- **corpus** — the 93 TLC-derived cases through
  `scripts/run_generated_case_adapters.py` and the subject's 199-line adapters.

| population | n | both | suite-only | **corpus-only** | neither |
|---|---:|---:|---:|---:|---:|
| **all** | 128 | 44 | 9 | **39** | 36 |
| string rotation | 101 | 35 | 8 | 36 | 22 |
| **non-string** (CMP/INT/BOOL/NOT/BOOLC) | 27 | 9 | **1** | **3** | 14 |

### Does the simplified path still yield zero unique kills? **No — and the scope matters**

**On this subject the generated corpus has 39 unique kills against the
hand-written suite's 9.** That is not zero, and it is the opposite direction
from the epic's headline.

**`R3` — the claim carries its scope, and the scope is doing most of the work:**

1. **The comparison is not "generation versus hand-writing". It is 93 generated
   cases against one hand-written test.** The prior `0 unique kills against 4`
   was measured on `ab_quota_ledger` against a *developed* hand-written suite.
   **This result does not refute that one.** It says the prior figure is a
   statement about that subject's suite, not about generation.
2. **17 of the 39 corpus-only kills are in code the corpus itself drives** —
   13 in `load_state` and 4 in `reset`, the state-installation path each
   generated case calls to load its `before`. The hand-written test never calls
   `load_state`. Discounting those leaves **22** corpus-only kills on program
   behaviour: `project_order` 10, `snapshot` 5, `checkout` 4, `add_cart_item` 2,
   `create_account` 1.
3. **36 of 101 string rotations are corpus-only, and most are SQL-string
   mutations that raise rather than misbehave.** On the 27 non-string mutants
   the tally is **3 corpus-only against 1 suite-only** — much closer, and the
   honest number for semantic faults.
4. **All 9 suite-only kills are in `process_outbox` (7) and `checkout` (2).**
   The internal corpus has no case that drives the outbox drain to the depth the
   hand-written test does. **A real gap, measured, not argued.**

### Sharpened at review, and it cuts against this ticket's own headline

An independent reviewer re-ran this probe from scratch on its own tree and got
**44 / 9 / 39 / 36 — exact match, zero per-mutant disagreements.** It then took
the discount one step further than I did. **All three semantic corpus-only kills
are in `project_order`** — a near-duplicate of `process_outbox` that the 42-line
hand-written test never calls at all:

| discount | corpus-only | semantic | suite-only | semantic |
|---|---:|---:|---:|---:|
| raw | 39 | 3 | 9 | 1 |
| minus `load_state`/`reset` (mine) | 22 | 3 | 9 | 1 |
| **minus `project_order` too** | **12** | **0** | **9** | **1** |

**On jointly-exercised code the generated corpus has ZERO semantic unique kills
and the hand-written suite has one** (`BOOLC:110:74`, in `checkout`).

**So the 39 measures coverage breadth, not fault-detection power.** The corpus
wins where it is the only thing executing the code, and wins nothing where both
instruments run. **The disproof survives, and this ticket's finding is narrower
than I first wrote it**: what is refuted is the *unqualified generalisation*
carried by the charter, the plan and the goal baseline. The `ab_quota_ledger`
result itself is untouched. The defensible sentence is:

> *"on `ab_quota_ledger`, against that subject's developed hand-written suite,
> the generated corpus had zero unique kills."*

### `MF-020` ordering — stated honestly because it cannot be checked

My claim is that the 128-mutant population was enumerated and run **before**
`CA-06-DF-01` was found. **The reviewer could not verify that from the
repository**, because the probe, its transcript and the finding all landed in a
single commit (`8324551`); it recorded only that the probe's structure is
*consistent* with the account. **The ordering therefore rests on my word and is
not independently checkable.** Weigh it that way. The fix for the next ticket is
cheap and nobody has been doing it: **commit the population before running it.**

### Cost

| | |
|---|---|
| TLC + generation, whole internal view | **< 1 s**, 142 states generated, 106 distinct |
| corpus run, 93 cases, batch | **0.22 s** |
| hand-written suite | **0.17 s** |
| generated corpus size | 93 cases |
| author cost, corpus | `Internal.tla` + `Internal.cfg` + `actions.yml` + 199-line `adapters.py` |
| author cost, suite | 42 lines |

**The path is cheap to run and expensive to author.** Nothing in this
measurement makes ~5,900 lines of generator and runner worth their size; what it
shows is that the corpus those lines produce is not worthless on a subject
outside the house fixture.

---

---

## 3. Dead simple: what an adopter must now type

The sealed adopter transcript
`examples/validation/runs/ex4-run3/artifacts/BLIND-RUN-B-RESULT.md:93` reports
the failure in its own words — *"`run_generated_case_adapters.py` needs two
`--import-root` flags; the error names one."* — and the flag's own help
text repeats it: *"a project normally needs two … Passing only one is the common
cause of a `ModuleNotFoundError` on an otherwise correct mapping."*
**A tool whose help explains how its default fails has a default problem, not a
documentation problem.**

```diff
- python3 scripts/run_generated_case_adapters.py <cases> \
-     --mapping <toml> --view internal --batch --import-root <project>
+ python3 scripts/run_generated_case_adapters.py <cases> --mapping <toml> --view internal
```

- **`--batch` is no longer a decision.** In-process batch execution is the only
  mode. The flag remains **accepted and inert** so the **27 live files** that pass it,
  and every sealed reproduction command under `specs/results/`, keep running.
- **`--import-root` is derived** — the project root is the directory above the
  outermost `specs/` component of the spec directory. It **adds** a path and
  removes none, and is skipped entirely when the flag is supplied.

Both verified on the real subject: the old **four-flag** command and the new
**two-flag** command each report `executed 93 cases in batch`. (This ticket's PR
first said "six flags to two", which its own diff block contradicts — corrected
at review.)

**And the derivation had a bug of its own, found by the reviewer and fixed:** it
took the *first* `specs` component, so a project nested under any ancestor named
`specs` derived the wrong root. It now takes the `specs` that contains the spec
directory, with a regression test built under `tmp_path`.

---

## 4. One regression, expressed once

`regression-as-adapter-case.py` in this directory, in `SV-04`'s shape: a small
conformance suite that asserts the outcome **out of band** rather than through
the generated corpus's own after-state comparison.

The regression is `INT:95:35:404` — `add_cart_item` returning
`404 account_not_found` for an unknown account — one of the 36 that **neither**
instrument in §2 kills.

**CORRECTED AT REVIEW: the stated selection rule was wrong.** This ticket
claimed it was "the first non-string mutant in source order". It is not — four
boolean survivors precede it (`BOOLC:19:18`, `BOOL:27:27`, `BOOLC:28:69`,
`BOOLC:73:75`). It is the first **integer** survivor. **The red/green below is
genuine and reproducible; the selection was filtered, not mechanical, and
describing a filtered choice as a mechanical one is the `MF-020`-adjacent error
this project has paid for before.** Recorded rather than restated correctly and
quietly, because "I applied a rule" and "I applied a rule I wrote down
afterwards" are different claims.

```
PRISTINE   2 passed in 0.01s
MUTANT     E  AssertionError: a cart mutation against an account that does not
              exist must be refused as not-found; got 405
           1 failed, 1 passed in 0.02s
```

**Why neither instrument sees it is the point.** `Internal.tla:22` guards
`AddCartItem(a, sku)` on `a \in accounts`, so **no reachable transition of the
model can express the refusal** — the positive corpus structurally cannot reach
it. The corpus that would is `--negative-cases`, and both its halves are broken
(§1, §1b). So the regression is expressible **as a TLA+ negative case in
principle and as an adapter conformance case today**, and this file is the
second.

**`MF-020`: this file is excluded from §2's kill table and was written after that
population was enumerated and run.** It demonstrates that the class is
EXPRESSIBLE. It is not evidence that any instrument catches it.

---

## 5. What was cut, priced per surface

`PRICE-TABLE.md` in this directory, which prints **three columns** — baseline,
post-`CA-05` epic tip, and this PR's head — because printing only the
counterfactual delta was a presentation failure the review caught.

```
surface               (a) e379d6b   (b) 88165bd   (c) PR head   (c)-(b)   (c)-(a)
                        baseline     epic tip      this PR      CA-06     actual
scripts/                   26,547       26,760       26,756        -4       +209
examples/validation/       14,854       14,854       14,854         0          0
tests/                     30,422       30,635       30,738      +103       +316
```

Card unchanged at **6,281**, `sha256:2d7d4a0506d9b259`. **No model file
changed — and section 3b of the price table explains why that is a defect
rather than a virtue.**

**This ticket was named "the largest single reduction in the epic" and it is
not. It is now approximately nothing.** CA-06's own `scripts/` figure was −32
when the PR opened and is **−4** after the review corrections: the `--no-batch`
tombstone, the renamed test's docstring and the docstring explaining the
import-root bug cost 28 lines between them. **That is `RD-02`'s finding for the
third time inside one ticket** — *"every removal shipped instruments, tests and
demonstrations to prove the removal safe and nobody counted that as a cost"* —
and **responding to a review is itself one of those costs.** The price table
counts it rather than netting it away.

---

## 6. What was rejected

Seven candidate cuts were considered and refused, each with its reason, in §5 of
the pull request body. The two that matter:

- **`--negative-cases`, and the 1,043-line parser and guard evaluator it needs**, and
  **`--port-cases` (397 lines, on the same parser)** — the mass this ticket was sent to
  cut. **`SM-02` measured both and kept them, in a still-green shipped test
  written expressly against this widening.** A ticket does not overturn a
  predecessor's measurement by asserting the opposite; it measures again. §1 is
  what measuring again produced, and it is a stronger case for the owner to
  decide on than the sentence the work order offered.
