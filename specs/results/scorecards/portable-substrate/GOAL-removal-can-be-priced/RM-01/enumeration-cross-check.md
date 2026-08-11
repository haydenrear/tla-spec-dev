# Cross-check: the derived walk at `bf0fb29`, read without running a suite

**Why this exists.** A sibling worktree was running its full suite while my
staged `pytest-full` columns ran, and machine contention can manufacture a
`DIES`. This check is deterministic, takes no measurable time, and touches no
suite: it stages `bf0fb29`, applies each fault to a *copy* of the registry in
memory, and calls the tree's own `demonstrate.unregistered()` directly.

It cannot be affected by load, and it agrees with the staged measurement.

```
$ git archive bf0fb29 | tar -x -C /tmp/rm01-bf
$ python3  # load /tmp/rm01-bf/examples/validation/instruments/demonstrate.py

PRISTINE                                      unregistered=[]
RF-1 (tests/test_code_complexity.py)          unregistered=[]
CTRL (scripts/code_complexity.py)             unregistered=['scripts/code_complexity.py']
```

**Read it as a pair.** The two faults are the same class — a registered
instrument silently loses its row — and differ in one property: whether the
path lies under `[registry.enumeration].roots = ["scripts", "examples/validation"]`.

* The one **inside** the derived scope is found. The replacement check works.
* The one **outside** it is invisible. `tests/test_code_complexity.py` is not
  under a declared root, and it is additionally unreachable by the discovery
  predicate, which needs a `__main__` guard and a nonzero exit path that no
  pytest file has.

Before `bf0fb29`, `required <= enumerated` named **both**. That is the price,
and it is visible here without running anything.

**What this does NOT show**, and why the staged run is still the measurement:
it asks one function one question. The claim that rests on the price is
*"nothing else in the repository catches it"*, and only `pytest-full` run whole
at both trees can say that. This check says the enumerator behaves as the
mechanism predicts; the staged table says nothing else picks up the slack.
