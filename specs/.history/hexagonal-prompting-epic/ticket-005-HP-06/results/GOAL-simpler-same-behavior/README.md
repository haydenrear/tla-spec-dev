# GOAL-simpler-same-behavior — the run record

The owner amendment at `schedule_revision: 2` resolved HP-02-DF-01 by making the
**arm pair** the measurement: arm A is the "before", arm B is the "after", and
the mechanical half of the harness is a size / state / branch capture over the
two produced trees, **recorded and never scored** (`eval_scorecard.md` rule 7).

The judged half is on the scorecards under
`../ab_quota_ledger/`. This file carries the mechanical block and nothing else.

## The mechanical block

`mechanical.json`, produced by `../measure/mechanical_block.py`. The reference
implementation is included as a third column **for calibration only** — it is
not an arm, it is never placed in a comparison with one, and it ships no tests.

| figure | arm A (control) | arm B (treatment) | reference (not an arm) |
|---|---|---|---|
| modules | 1 | 4 | 1 |
| production lines (significant) | **147** | **123** | 93 |
| own test lines (significant) | 266 | 222 | — |
| public names | 17 | 21 | 15 |
| branches | 13 | 11 | 10 |
| `self.<name>` assignments | 5 | 8 | 7 |
| max distinct methods writing one attribute | 2 | 2 | 2 |
| I/O imports | `os`, `pathlib` | `pathlib` | `pathlib` |

## What this does and does not say

**Arm B is smaller in significant production lines than arm A (123 vs 147)**,
while being spread over four modules instead of one. It is larger in public names
(21 vs 17), which is what a declared port plus two adapters plus a composition
point costs.

> **CORRECTED IN PLACE, by HP-06's adversarial channel (finding F9).** The first
> version of this paragraph also said arm B "has fewer branches (11 vs 13)". That
> figure is **not comparable between the trees, and the difference decomposes
> entirely into things that are not complexity.** Enumerated node by node: three
> of arm A's "extra" branches buy behavior arm B does not implement — parent
> directory creation (`arms/arm_a/quota_ledger.py:103`, an `If` plus a `BoolOp`)
> and turning a missing tenant into a named `KeyError`
> (`arms/arm_a/quota_ledger.py:250-253`) — and the one branch arm B has that arm
> A does not is *the same tenant-membership predicate written on the other side
> of a `for`* (`arms/arm_b/quota_ledger/domain.py:150-154` as a comprehension
> `if`, `arms/arm_a/quota_ledger.py:240` inside an `any(...)`). **On matched
> behavior the two trees have identical decision counts.** `ast.BoolOp` is also
> counted once regardless of arity.
>
> The same channel showed the sentence below it is unsupported *for exactly this
> delta*: the shared suite uses `tmp_path`, so it never asks either arm for a
> ledger path whose parent does not exist and never asks for the unknown-tenant
> message. Filed as **HP-06-DF-08**, not fixed.

This is worth stating plainly because it **contradicts the pilot HP-02 ran on an
earlier draft of the same prompt**, which measured arm B at 5 files / 274 lines
against arm A's 1 file / 120 and recorded it as reproducing sealed prediction
N01. On the shipped prompt text — which HP-02 deliberately did not re-run, so
HP-06 is its first measurement — the line count goes the other way.

**A smaller number is not a better design, and this file does not claim one.**
Both trees pass the identical shared behavioral suite (28 passed each), so
neither bought its figures by deleting behavior; that is the only thing the
mechanical block can establish and it establishes nothing further.

## A figure that is NOT comparable, measured and stated rather than left to mislead

`self.<name> assignments` reads 5 for arm A and 8 for arm B, which invites the
conclusion that the treatment arm carries more mutable state. **It is an
undercount for arm A.** The counter is an AST walk for assignments through
`self`, and arm A holds each tenant's `held`, `committed` and `closed` inside a
`_Tenant` dataclass that it mutates through a local name
(`arms/arm_a/quota_ledger.py:195`, `arms/arm_a/quota_ledger.py:216-217`), which
the walk does not see. Arm B's 8 also counts `_path` and `_lines` from its two
journal adapters, which are one field each in a five-line class.

> **CORRECTED IN PLACE, by HP-06's adversarial channel (finding F10).** The first
> version of this section told the reader to "read `mutable_state` and
> `state_writers` in `mechanical.json` instead of the single figure". **The
> prescribed remedy is wrong in the same way as the figure it replaces.** The
> walk recognises a state write only as an assignment whose target is
> `self.<name>`, which excludes subscript writes
> (`arms/arm_b/quota_ledger/domain.py:124`), method mutation (`.add`, `.pop`),
> `del` (`arms/arm_a/quota_ledger.py:215`), every write through a name other than
> `self` (all of arm A's per-tenant mutation), and dataclass fields, whose
> generated `__init__` has no AST body at all.
>
> The consequence is that **`max_writers_of_one_attribute` is 2 for arm A, 2 for
> arm B and 2 for the reference**, and in all three the one attribute with two
> writers is the id counter. Every other attribute reports exactly one writer:
> `__init__`. `mechanical_block.py`'s docstring markets this figure as the number
> behind "state written from everywhere"; **it is a constant across all three
> trees and discriminates nothing.** Filed as **HP-06-DF-02** (extended), not
> fixed — a fix during a measurement destroys the measurement, and both defects
> are now visible enough to reason around.
>
> Also from the same channel (F11): `io_imports` reports arm A touching the
> outside world through `os`, whose only use in that tree is the type annotation
> `path: os.PathLike | str`. No call, no attribute access at runtime.

The substantive difference the two lists show is real and is in the *other*
direction from the count: arm A stores `held` and derives `available` from it;
arm B stores no held total at all and computes it from the live reservations.
That single difference is why three of the catalogue's ten mutants cannot be
written against arm B — see `../GOAL-catch-bugs/README.md`.

## The confound that this round cannot remove

`check_catalogue.py --arms` measures the two prompts at 73 and 194 lines, with
**16 lines unique to A and 105 unique to B** — a 6.6x ratio of unique content,
the same figure HP-02 measured. Arm B's prompt is longer and asks for more.

**Nothing on this page can distinguish "hexagonal guidance helped" from "a
longer, more specific ask helped."** Separating them needs a third arm — a
prompt as long and as specific as arm B's that asks for something other than
ports and adapters — and this epic does not run one. Sealed confound 1 says so
and it is not argued away here.
