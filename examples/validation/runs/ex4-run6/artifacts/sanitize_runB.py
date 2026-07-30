#!/usr/bin/env python3
"""EV-03 blind-run-B sanitizer.

EV-02-PROTO-01, binding: PURPOSE-WRITTEN NEUTRAL TEXT, not redaction stubs.
Blind run B measures the aspect-authoring path, which has no `file:line` answer
key, so line counts need not be preserved here -- only the epic context, the
answer keys and the measurement history must go, replaced by text that reads
like a project's own documentation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])

HEADERS: dict[str, str] = {
    "pipeline/ledger/journal.py": '''"""The durable ledger: model variable `ledger`.

Holds the append-only record of what the service delivered, and persists it
through a store port so the record survives a restart.
"""''',
    "pipeline/ingest/queue.py": '''"""The outbound work queue: model variable `queue`.

Holds accepted items in insertion order until dispatch takes them.
"""''',
    "pipeline/ingest/inbox.py": '''"""Item intake: model variables `inbox` and `accepted`.

Tracks what has arrived and what has been accepted for processing.
"""''',
    "pipeline/dispatch/delivery.py": '''"""Delivery outcomes: model variable `delivered`.

Takes items from the work queue and marks them delivered.
"""''',
    "pipeline/dispatch/failures.py": '''"""Delivery failures: model variable `failed`.

Records deliveries that later failed.
"""''',
    "pipeline/ingest/__init__.py": '''"""The ingest package: item intake and the outbound work queue."""''',
    "pipeline/dispatch/__init__.py": '''"""The dispatch package: delivery outcomes and their failures."""''',
    "pipeline/ledger/__init__.py": '''"""The ledger package: the durable record of delivered items."""''',
    "tests/driver.py": '''"""Composition root: wires the three parts of the service together.

It lives outside `pipeline/` deliberately. Wiring touches every package, so a
composition root inside the production tree would make every package appear to
depend on every other one. Keeping it here means the production packages depend
only on what they actually use.
"""''',
    "tests/test_behavior.py": '''"""Behavioural conformance to Pipeline.tla.

Eight tests. Each asserts that a sequence of calls against the wired service
produces the state the model says it should.

    python3 -m pytest tests -q
"""''',
    "specs/program_model/tlc_projection.py": '''"""State and output projections for the Pipeline model.

`project_visible_state` renders the real objects back into the six model
variables. `project_adapter_output` renders what an action RETURNED, which is a
separate observable from the state it left behind:

    {"action": <name>, "status": "applied",
     "ledger_size": int, "queue_size": int, "delivered_size": int}

`status` is always "applied" for a generated transition, because every
generated transition is an action the model says is enabled -- so an
implementation that reports a rejection where the model says the action fired
shows up here and nowhere else. The three counts are what catch an operation
that changed the right thing by the wrong amount.
"""''',
}

# targeted inline replacements after the headers are rewritten
INLINE: dict[str, list[tuple[str, str]]] = {
    "specs/program_model/case_adapters_corpus_only.toml": [
        (
            "# ARM A -- corpus alone (the MF-038 instrument). Real boundary, no assertion.",
            "# The plain configuration: a real file-backed ledger store that writes what\n"
            "# the program tells it to write and checks nothing about the contents.",
        )
    ],
}


def replace_module_docstring(text: str, new: str) -> str:
    m = re.match(r'^("""(?:.|\n)*?""")', text)
    if not m:
        raise SystemExit("no leading module docstring")
    return new + text[m.end(1) :]


for rel, new in HEADERS.items():
    path = ROOT / rel
    path.write_text(replace_module_docstring(path.read_text(), new))
    print(f"header rewritten: {rel}")

for rel, pairs in INLINE.items():
    path = ROOT / rel
    text = path.read_text()
    for old, repl in pairs:
        if old not in text:
            print(f"  WARN {rel}: inline pattern absent")
            continue
        text = text.replace(old, repl)
    path.write_text(text)
    print(f"inline rewritten: {rel}")

print("done")
