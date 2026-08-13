# CA-05 — GOAL-apparatus-cut local signal

The guard goal. `expected_effect: none expected, AND THE HAZARD IS REAL --
this ticket could add apparatus in the name of measuring apparatus. PRICE
anything it ships.`

## The declared command, run on this branch

```
$ find scripts examples/validation -name '*.py' -not -path '*/__pycache__/*' | xargs wc -l | tail -1
   43914 total
```

## Per surface, never combined with the card

```
                     a6bdf42     HEAD     delta
scripts/              27,652    27785    +133   scripts/disposition.py
examples/validation/  16,129    16129       0   NO Python changed

tests/                32,162    32311    +149   NOT in the goal metric; priced anyway
instruments.toml           -        -     +66   TOML, not Python; the registry row
```

## The card, reported separately

```
$ score_tools.py serve | wc -c
    6281
$ score_tools.py serve --digest-only
sha256:2d7d4a0506d9b259
```

**UNCHANGED at 6,281 bytes / `sha256:2d7d4a0506d9b259`. Clause (c) holds.**

## Classification: MOVED THE WRONG WAY, by 133 lines, deliberately

Clause (a) of `GOAL-apparatus-cut` asks `scripts/` + `examples/validation/` to
FALL. This ticket raised `scripts/` by 133. **Said plainly rather than buried:
the guard goal moved the wrong way and this ticket is the cause.**

What was bought for it: a demonstrated refusal on a real input, which `R1`
requires and which prose cannot produce. The cheaper alternatives were measured
and rejected — a `grep` cannot scope to an epic or check the D2/D3 grammar, and
putting the file in `tests/` where the metric does not count it would have been
metric-dodging.

**Clauses (b), (c) and (d) hold:** nothing was deleted (the whole branch has ONE
deletion, this ticket's own `status: planned` -> `done`), the card did not grow,
and the surfaces are reported separately with the tree named in every figure.
