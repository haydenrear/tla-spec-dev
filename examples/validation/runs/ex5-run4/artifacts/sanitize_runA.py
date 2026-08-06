#!/usr/bin/env python3
"""EV-03 blind-run-A sanitizer.

EV-02-PROTO-01, binding: the fixture gets PURPOSE-WRITTEN NEUTRAL TEXT, not
redaction stubs. Round 1's sanitizer left `\\* --` scars and the agent noticed.

Every replacement here is LINE-COUNT PRESERVING, so the answer key's `file:line`
sites are unchanged and the run can be scored against the same key. Only
docstrings and comments are touched; no statement is altered.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(sys.argv[1])

REPLACEMENTS: dict[str, list[tuple[str, str]]] = {
    "pipeline/ledger/journal.py": [
        (
            '''"""Model variable `ledger`.

Component: ledger.

SEEDED DIVERGENCE D3 lives in this file: `backlog_hint` reaches into the ingest
component, and there is no ingest <-> ledger port. The import is function-local
because the top-level direction is already taken by D1/D2 -- exactly the
cycle-breaking move a real codebase makes, and a check that only reads
module-level imports would miss it.

SEEDED ABSENCE A1 also lives here: `Record(i)` reads `delivered`, so the model
declares port P2 (dispatch <-> ledger). This file no longer imports
`pipeline.dispatch.delivery` -- the delivered set arrives as an argument from
the composition root -- so no code edge realizes P2.
"""''',
            '''"""The durable ledger: model variable `ledger`.

Holds the append-only record of what the service delivered, and persists it
through a store port.

`backlog_hint` is an operator convenience added late: it prints a one-line
summary of what is still waiting upstream. The import it needs is written
inside the function rather than at module level, because a module-level import
there closes an import cycle that Python refuses to load.

`record()` takes the delivered set as an argument rather than holding a
reference to the dispatcher, so this module can be constructed and tested
without one. The composition root in `tests/driver.py` supplies it on each
call.
"""''',
        ),
        (
            '''    """The ledger\'s rendering of one item. Used by ingest in D2."""''',
            '''    """The ledger\'s rendering of one item, reused by callers upstream."""''',
        ),
    ],
    "pipeline/ingest/queue.py": [
        (
            '''"""Model variable `queue`, and the ingest side of the ingest <-> dispatch port.

Component: ingest.

SEEDED DIVERGENCE D1 lives in this file: the backlog report reaches into the
ledger component directly, and there is no ingest <-> ledger port.
"""''',
            '''"""The outbound work queue: model variable `queue`.

Holds accepted items in insertion order until dispatch takes them.

`backlog_report` renders the queue for the operator view; it borrows the
ledger\'s formatting so the two reports read alike.
"""''',
        ),
    ],
    "pipeline/ingest/inbox.py": [
        (
            '''"""Model variables `inbox` and `accepted`.

Component: ingest. Writes only ingest state.

SEEDED DIVERGENCE D2 lives in this file: the status-line helper reaches into
the ledger component directly, and there is no ingest <-> ledger port.
"""''',
            '''"""Item intake: model variables `inbox` and `accepted`.

Tracks what has arrived and what has been accepted for processing.

`status_line` renders one item for the operator view; it borrows the ledger\'s
formatting so the two reports read alike.
"""''',
        ),
    ],
    "pipeline/dispatch/delivery.py": [
        (
            '''"""Model variable `delivered`, and the dispatch side of port P1.

Component: dispatch. Reaches ingest through `WorkQueue.take` only -- that is
port P1 (`Deliver`). It must not reach ledger: `Record` is dispatch <-> ledger
(port P2) and is driven from the ledger side.
"""''',
            '''"""Delivery outcomes: model variable `delivered`.

Takes items from the work queue and marks them delivered. The only thing it
reaches upstream is `WorkQueue.take`, which is the handoff itself. Recording a
delivery in the ledger is driven from the ledger side, not from here.
"""''',
        ),
    ],
    "pipeline/dispatch/failures.py": [
        (
            '''"""Model variable `failed`.

Component: dispatch. Reaches only its own component (an internal edge to
`delivery`).
"""''',
            '''"""Delivery failures: model variable `failed`.

Records deliveries that later failed. Talks only to the dispatcher beside
it.
"""''',
        ),
    ],
    "tests/driver.py": [
        (
            '''"""Composition root for the divergent twin.

Identical observable behavior to `ex4_pipeline_coherent/tests/driver.py`. The
twin differs ONLY in dependency structure: the seeded divergences are reporting
helpers, and the seeded absence is a parameter passed instead of an import. A
behavioral test suite cannot tell the two fixtures apart, which is the point --
whatever EV-02 measures here is measuring structure, not behavior.
"""''',
            '''"""Composition root: wires the three parts of the service together.

This is where the object graph is built. Each part is constructed with the
collaborators it needs, and the five operations below are the entry points the
behavioural suite drives. Nothing here holds state of its own; it exists so
the production packages do not have to know how to find one another, and so
that wiring is not a dependency of any production package.
"""''',
        ),
    ],
    "tests/test_behavior.py": [
        (
            '''"""Behavioral conformance to Pipeline.tla.

This file is BYTE-IDENTICAL in ex4_pipeline_coherent and ex5_pipeline_divergent.
Both must pass. If a fix to the divergent twin\'s structure changes what this
file asserts, the fix changed behavior, and EV-02 scores that as a failure of
the fix, not a success of the check.

    python3 -m pytest examples/validation/ex4_pipeline_coherent/tests -q
"""''',
            '''"""Behavioural conformance to Pipeline.tla.

These eight tests are the contract: each one asserts that a sequence of calls
against the wired service produces the state the model says it should. They
say nothing about how the packages are arranged, so a change that only moves
code should leave every one of them passing, unchanged.

    python3 -m pytest tests -q
"""''',
        ),
    ],
    "pipeline/ledger/__init__.py": [
        (
            '''"""ledger component: owns the append-only ledger."""''',
            '''"""The ledger package: the durable record of delivered items."""''',
        )
    ],
    "pipeline/dispatch/__init__.py": [
        (
            '''"""dispatch component: owns delivered and failed."""''',
            '''"""The dispatch package: delivery outcomes and their failures."""''',
        )
    ],
    "pipeline/ingest/__init__.py": [
        (
            '''"""ingest component: owns inbox and accepted, and holds the work queue."""''',
            '''"""The ingest package: item intake and the outbound work queue."""''',
        )
    ],
}

failures = []
for rel, pairs in REPLACEMENTS.items():
    path = ROOT / rel
    text = path.read_text()
    before_lines = text.count("\n")
    for old, new in pairs:
        if old not in text:
            failures.append(f"{rel}: pattern not found:\n{old[:80]}")
            continue
        if old.count("\n") != new.count("\n"):
            failures.append(
                f"{rel}: replacement changes line count "
                f"({old.count(chr(10))} -> {new.count(chr(10))}) -- would move the answer key"
            )
            continue
        text = text.replace(old, new, 1)
    path.write_text(text)
    after_lines = text.count("\n")
    if before_lines != after_lines:
        failures.append(f"{rel}: file line count changed {before_lines} -> {after_lines}")
    print(f"sanitized {rel}  ({after_lines} lines, unchanged)")

if failures:
    print("\nFAILURES:")
    for f in failures:
        print("  " + f)
    raise SystemExit(1)
print("\nall replacements applied, every file line count preserved")
