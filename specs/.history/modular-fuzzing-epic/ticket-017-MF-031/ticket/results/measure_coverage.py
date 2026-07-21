#!/usr/bin/env python3
"""MF-031 corpus coverage, re-measured (not assumed).

Buckets every generated case by the ticket-lifecycle stage of its BEFORE-state
-- the exact axis MF-028 used for its 72.5% figure -- and reports what was
executable before this ticket vs after it.

  * before MF-031: `materialize_before` refused every before-state with any
    ticket_state > 0, and UpdateTicketDesired/Current were refusing stubs, so
    only setup-segment cases (all ticket_state == 0) could run.
  * after  MF-031: the ticket segment replays for stages 1..3; stages >= 4
    (SpecUnitTestsPassed / Closed) still refuse, needing the gate machinery.

The full-`MC.cfg` corpus is intractable to load (5,619,355 transitions;
cases.py is ~11 GB -- MF-034's OOM surface), so this measures the reduced
single-ticket corpus and says so. The proportions are what matter.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

CASES = Path(sys.argv[1])
text_iter = CASES.open()

name_re = re.compile(r"name='(case_\d+_[a-z_]+)'")
action_re = re.compile(r"action='([A-Za-z]+)'")
before_ts_re = re.compile(r"'ticket_state':\s*(\{[^{}]*\})")

total = 0
by_segment = Counter()
by_action_blocked = Counter()
updateticket_runnable = Counter()
name = action = None
for line in text_iter:
    m = name_re.search(line)
    if m:
        name = m.group(1)
        action = None
        continue
    if name and action is None:
        am = action_re.search(line)
        if am:
            action = am.group(1)
    if name and "before={" in line:
        bm = before_ts_re.search(line)
        stages = [int(v) for v in re.findall(r":\s*(\d+)", bm.group(1))] if bm else [0]
        mx = max(stages) if stages else 0
        total += 1
        if mx == 0:
            seg = "setup-segment (ticket_state all 0)"
        elif mx <= 3:
            seg = "ticket-segment stages 1..3 (UNBLOCKED by MF-031)"
        else:
            seg = "ticket-segment stages >=4 (still needs gate machinery)"
        by_segment[seg] += 1
        for kind in ("update_ticket_desired", "update_ticket_current"):
            if kind in name:
                updateticket_runnable[kind + (" runnable" if mx <= 3 else " still-blocked")] += 1
        name = None

print(f"reduced corpus: {CASES}")
print(f"total cases: {total}\n")
print("before-state segment breakdown:")
setup = by_segment["setup-segment (ticket_state all 0)"]
unblocked = by_segment["ticket-segment stages 1..3 (UNBLOCKED by MF-031)"]
gated = by_segment["ticket-segment stages >=4 (still needs gate machinery)"]
for seg in ("setup-segment (ticket_state all 0)",
            "ticket-segment stages 1..3 (UNBLOCKED by MF-031)",
            "ticket-segment stages >=4 (still needs gate machinery)"):
    n = by_segment[seg]
    print(f"  {n:7d}  {100*n/total:5.1f}%  {seg}")

ticket_segment = unblocked + gated
print(f"\nticket-segment total (any ticket_state>0): {ticket_segment}  ({100*ticket_segment/total:.1f}%)")
print("  ^ MF-028 reported this axis as 72.5% blocked-by-absence on the full corpus.")
print(f"\nEXECUTABLE before MF-031: {setup}  ({100*setup/total:.1f}%)   [setup segment only]")
print(f"EXECUTABLE after  MF-031: {setup+unblocked}  ({100*(setup+unblocked)/total:.1f}%)   [setup + ticket stages 1..3]")
print(f"NET UNBLOCKED by MF-031 : {unblocked}  ({100*unblocked/total:.1f}%)")
print(f"STILL BLOCKED (stages>=4, gate machinery / MF-023 surface): {gated}  ({100*gated/total:.1f}%)")
print("\nUpdateTicketDesired/Current own cases (the two new adapters):")
for k in sorted(updateticket_runnable):
    print(f"  {updateticket_runnable[k]:7d}  {k}")
