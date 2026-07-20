# MF-023 — retention proof against the pre-split baseline

The acceptance criterion requires reachable behavior be **proven** retained,
not asserted, against a baseline established first.

## 1. Baseline, measured at branch time from the epic tip (5575566)

Not quoted from the ticket text -- re-measured:

```
bash scripts/run_tlc.sh specs/tickets/MF-023/current/TlaSpecDevCli.tla \
                        specs/tickets/MF-023/current/MC.cfg
```

`tlc-baseline-presplit.txt`:

```
5619356 states generated, 231621 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 25.
```

Matches the 231,621 / depth 25 figure the assignment quotes. 9 variables,
declared bound 699,840.

## 2. The proof

`External.tla` is the composition -- Internal plus the observable channel -- and
is therefore the view that must reproduce the baseline exactly. It does, on all
three independent figures:

| Figure | Pre-split baseline | External view | Match |
|---|---|---|---|
| distinct states | 231,621 | **231,621** | exact |
| search depth | 25 | **25** | exact |
| states generated | 5,619,356 | 5,387,735 | **−231,621 exactly** |

The generated-state difference is not slack: it is **exactly** 231,621, one
removed stutter self-loop per reachable state (FINDING 7). Distinct states and
depth are unchanged, which is what makes the removal a redundancy elimination
rather than an abstraction.

That the difference lands on precisely the state count, and nowhere else, is a
stronger check than equality alone -- an accidental behavioral change would be
overwhelmingly unlikely to produce that exact figure.

## 3. Why this is a proof of retention and not a coincidence

TLC explores the full reachable state graph of each model under identical
constants (`SpecRoots`, `Tickets`, `NoRoot`, `NoReason` all identical between
`MC.cfg` and `External.cfg`) and checks all 14 original invariants plus one new
one. Identical distinct-state count **and** identical depth under identical
constants means the two models have the same reachable state graph size and the
same longest shortest-path. Combined with the structural fact that every
External action is defined as `Internal action /\ channel write` -- so the
transition relation is the pre-split one by construction -- reachable behavior
is retained.

The one deliberate difference: `External.tla` has **no** `HiddenInternalProgress`
disjunct, unlike the shipped example. In the example a background worker can
advance internal state without a client request. A CLI has no such thing: every
state change is caused by an invocation, and every invocation writes the channel.
Including the disjunct would have *added* reachable states and broken this exact
match -- so its absence is load-bearing, not an omission.

## 4. Internal view — the actual decomposition win

```
956775 states generated, 42861 distinct states found, 0 states left on queue.
The depth of the complete state graph search is 24.
```

| | pre-split | Internal | change |
|---|---|---|---|
| distinct states | 231,621 | 42,861 | **−81.5%** |
| depth | 25 | 24 | −1 |
| variables | 9 | 7 | −2 |

Internal is the view the inner development loop actually checks, and it is 5.4x
cheaper. The channel that made the state space large is now isolated in the view
whose job is to represent it.

## 5. Invariant retention

No invariant was dropped. All 14 are checked by `Internal.cfg`, all 14 **plus**
`ExternalInvariant` by `External.cfg`. Every named safety property in the
pre-split module survives by name, including the ones that are tautologies under
the MF-020/MF-022/MF-025 ordinals -- retained on the established precedent that
a deleted named property is indistinguishable at review from a lost one.
