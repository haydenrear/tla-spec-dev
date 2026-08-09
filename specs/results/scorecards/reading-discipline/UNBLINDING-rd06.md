# UNBLINDING KEY — DO NOT GIVE THIS FILE TO A JUDGE

RD-06's produced subjects. Written **before** any tree existed, in the same
commit as `GOAL-product-round/RD-06/SEALED-BEFORE-DISPATCH.md`, so the mapping
was fixed before there was anything to map.

Example: `ab_quota_ledger`.

## The draw

Labels were drawn from `score_tools.py`'s `LABEL_POOL` minus
`RESERVED_LABELS` minus every label any round has published
(`used_labels()` — `H K P Q R S T U W X Y` and `A-CONTROL-REFERENCE` at
`3806af8`), leaving `D E F G J L M N V Z`.

```python
import random
random.Random(6).sample(["D","E","F","G","J","L","M","N","V","Z"], 6)
# -> ['Z', 'E', 'N', 'M', 'F', 'D']
```

The **assignment rule was fixed before the draw was run**: draw positions 1–3
take the greenfield arms in the order `arm_a`, `arm_b`, `arm_c`; positions 4–6
take the revision of each of those three, in the same order.

## The mapping

| label | is | dispatched prompt | before-tree |
|---|---|---|---|
| `Z` | **greenfield, `arm_a`** — the ordinary implementation ask | `arm_a/PROMPT.md` | — |
| `E` | **greenfield, `arm_b`** — hexagonal + minimize-complexity | `arm_b/PROMPT.md` | — |
| `N` | **greenfield, `arm_c`** — the length-matched control, no architectural vocabulary | `arm_c/PROMPT.md` | — |
| `M` | **revision of `Z`** | `revision/PROMPT.md` | `Z` |
| `F` | **revision of `E`** | `revision/PROMPT.md` | `E` |
| `D` | **revision of `N`** | `revision/PROMPT.md` | `N` |

The pairing (`M`←`Z`, `F`←`E`, `D`←`N`) **is published** in
`GOAL-product-round/RD-06/SUBJECTS-RD-06.md`, because a judge cannot award D2
anchor 3 without knowing which tree is the before. The arm column above is not.
Every greenfield tree has a revision, so the pairing is uninformative about the
arm: there is no tree identifiable by having been left out.

## What each producing agent could and could not see

- Each agent received exactly the bytes preserved in
  `examples/validation/ab/dispatch/reading-discipline/<label>.dispatched.md`,
  and nothing else from this repository was described to it.
- The dispatch envelope names an **opaque working directory** and forbids
  opening anything outside `examples/validation/ab/` other than the files the
  prompt names. `PA-06-DF-10`: the previous round's envelope carried the epic's
  own name in a path, into the arm whose entire job was architectural silence.
- No agent was told which arm it was, what the comparison was, or that a
  revision pass existed. The revisers were not told who wrote the tree they were
  given or what it had been asked for.
- Disclosures any agent volunteered are recorded in
  `GOAL-product-round/RD-06/SUBJECTS-RD-06.md`. **A disclosed leak is recorded,
  never used as grounds to discard a tree** — discarding a subject after seeing
  what it produced is the one move a round may not make.
