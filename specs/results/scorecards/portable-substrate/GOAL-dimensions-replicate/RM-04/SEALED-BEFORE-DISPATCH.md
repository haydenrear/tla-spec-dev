# RM-04 — sealed before any judge was dispatched

**Committed before the round exists.** The epic's standing rule: *commit
predictions before dispatch, and if every prediction passes, that is an ALARM.*
`subtract-to-measure`'s best material was that its founding premise was false,
and it was only visible because the premise had been written down first.

Scaffolded at `dbf355c` + this ticket's instrument fixes. Example
`eval_toolchain`, three declared subjects, labels drawn with seed `20260810`
from the width-2 pool (see [the label pool](#5-what-the-label-pool-did)).
Mapping is in `UNBLINDING.md` and no judge is given it.

---

## 1. The predictions

Each is a claim about **this round**, at the scope its own words carry.

| # | prediction | why | how it is decided |
|---|---|---|---|
| **P1** | **D2 = 2 on every card of the two subjects with no before/after** (`rm04_scripts`, `rm04_eval_harness`) | D2's anchor 3 requires a simplification *and* its measured effect. Neither subject is given one. If a judge awards 3 anyway, the anchor is not doing what the record says it does. | the cards |
| **P2** | **D2 ≥ 3 on at least one card of `rm04_removal_pricer`** | it is the one subject with a real before/after: 1209 lines replaced by 899, same job. If D2 does **not** move here, D2's movement on `ab_quota_ledger` was about that example and not about the dimension. | the cards |
| **P3** | **D3 separates `rm04_scripts` from `rm04_eval_harness`** — disjoint ranges, `effectful` below `ports-and-adapters` | it is what the `ab_quota_ledger` row says, on 58 cards. A second example either reproduces it or bounds it. | `score_tools.py tags` |
| **P4** | **no card of any `effectful` subject scores D3 ≥ 3** | RM-02 §7: whether D3 discriminates *inside* `effectful` is the single untested thing that would decide whether D3 exports unconditionally. This round is the first that could answer it. | the cards |
| **P5** | **at least one dimension tier-splits on at least one artifact** | four splits are on the record and every round that looked has found one. | `score_tools.py contested` |
| **P6** | **at least one judge cites `examples/validation/scorecards/subjects.toml` or `score_tools.py`** — the blinding key, which is *inside* `rm04_eval_harness`'s declared scope | the subject contains the instrument. This is the leak this round could not remove, and it is measured rather than hoped about. | grep over every card's citations |

**P1, P4 and P6 are the ones this ticket expects to be wrong about**, and each
is written so that being wrong is legible. A round in which all six pass has
told us nothing we did not already believe.

## 2. What this round CANNOT decide, written down first

- **Whether `D3 = 4` reproduces.** No subject here is `ports-and-adapters` *and*
  ships a driven port exercised by a real adapter and a fake, which is D3's
  anchor 4. If nothing reaches 4, that bounds RM-03's `D3 = 4 on 4 of 4` to the
  arm it was measured on; it does not refute it. **Saying so afterwards would be
  a story; saying so here is a scope.**
- **Whether the `state_colocation` threshold is right.** `rm04_eval_harness`
  derives at **0.412** — the nearest to `0.5` any subject this project has ever
  declared — so this round produces the first independent D3 judgement of a
  near-boundary artifact. One artifact decides a constant for nobody.
- **Anything about `ab_quota_ledger`.** No card here is about it, and no figure
  from this round may be read across to it (`R-H2`).

## 3. The premise in the work order that is already false

The ticket says RM-03's removal is *"a genuine before/after"* for the toolchain
and that after RM-03 `scripts/` *"will be meaningfully smaller."*

**`19c5c7b:scripts` and `dbf355c:scripts` are the same tree,
`e9d5544aaa33b2f910e75a461194a3360b511b90`.** RM-03 removed the mutant catalogue
and the gap-mutant runner, both under `examples/validation/`. `scripts/` was not
touched by any commit in this epic.

So the before/after this round needs had to be found somewhere else, and it was:
`examples/validation/gap_mutants`, which is the subject `rm04_removal_pricer`.

## 4. What the derivation says before any judge sees anything

Re-derivable with `python3 examples/validation/scorecards/score_tools.py tags`.

| subject | scope | derived | `state_colocation` |
|---|---|---|---|
| `rm04_scripts` | `scripts` | `effectful` | 1.0 |
| `rm04_eval_harness` | `examples/validation` | `ports-and-adapters` | **0.412** |
| `rm04_removal_pricer` | `examples/validation/gap_mutants` | `effectful` | *(no instance state)* |

## 5. What the label pool did

The pool was down to `G J L V` of 17 (`RM-02-DF-01`). This round draws
**width-2 labels over the four characters this repository has never published**,
so no label here has been published and no *character* of one has either. Three
were drawn: they are recorded in `UNBLINDING.md` and not here.
