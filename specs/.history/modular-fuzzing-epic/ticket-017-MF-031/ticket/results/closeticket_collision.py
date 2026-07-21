#!/usr/bin/env python3
"""MF-031: characterize the CloseTicket label collision, with evidence.

Enumerates every adapter class bound to the `CloseTicket` action, shows how the
runner's one-label-to-one-adapter mapping resolves it, and classifies each as a
case executor (`run`) or a spec-unit conformance battery (`apply` only).
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "specs" / "tickets" / "MF-031" / "current"))
import production_adapters as pa  # noqa: E402

LABEL = "CloseTicket"

classes = [
    obj for _n, obj in inspect.getmembers(pa, inspect.isclass)
    if getattr(obj, "action_name", None) == LABEL and obj.__module__ == pa.__name__
]

print(f"adapter classes with action_name == {LABEL!r}: {len(classes)}")
for cls in sorted(classes, key=lambda c: c.__name__):
    has_run = "run" in cls.__dict__ or any("run" in b.__dict__ for b in cls.__mro__[1:] if b is not object)
    has_apply = hasattr(cls, "apply")
    # how many times does apply() drive a close? A battery closes >1 (directly
    # via `"close","ticket"` or through a local `close(...)` helper).
    src = inspect.getsource(cls)
    closes = src.count('"close"') + src.count("'close'") - src.count("def close") + src.count("close(")
    print(f"  - {cls.__name__:38s} run()={'yes' if 'run' in cls.__dict__ else 'no':3s} "
          f"apply()={'yes' if has_apply else 'no'}  close-drives-in-apply~={max(closes,1)}")

print()
print("Runner mapping model: run_generated_case_adapters.adapter_for_case() returns")
print("exactly ONE mapping per label (the toml is a dict keyed by label). So the")
print("corpus label 'CloseTicket' binds to a SINGLE adapter; the others are")
print("unreachable from the corpus regardless of any run() they grow.")
print()
print("FINDING: this is a binding-model limitation, not an adapter defect.")
print(f"  * {len(classes)} classes claim the CloseTicket transition; only 1 can bind.")
print("  * The non-canonical ones are multi-close BATTERIES (each drives several")
print("    closes to assert accumulation/gating) -- not single transitions, so they")
print("    cannot be case executors even in principle. They are correct as the")
print("    spec-unit apply() conformance tests they already are.")
print("  * Even the canonical CloseTicketAdapter's before-state needs a ticket at")
print("    ticket_state=SpecUnitTestsPassed(4), which requires the spec-unit/close")
print("    gate machinery MF-031 deliberately refuses (out-of-segment). So CloseTicket")
print("    case execution is blocked by that same surface, independent of the collision.")
