#!/usr/bin/env python3
"""MF-032 corpus executability, re-measured (not assumed).

Executability has TWO axes, and this ticket moves the second one:

  * before-state materializable -- MF-031's axis: a case whose before-state has
    any ticket at stage >= 4 (SpecUnitTestsPassed/Closed) cannot be built,
    because that needs the spec-unit/close gate machinery. MF-031 measured this
    alone and reported 26.0% -> 81.6%.
  * action has a run() adapter -- MF-032's axis: even a materializable
    before-state cannot be EXECUTED end to end unless the case's action has a
    run(). MF-031 left InstallLocalCli, ScaffoldWorkflow, RecordBudgets and
    OpenTicket without one.

A case is genuinely executable only when BOTH hold. Measuring the before-state
axis alone over-counts: it credits RunEffectConformance / RunKillTest /
AnalyzeCorpus / AnalyzeComplexity / CloseTicket / RunSpecUnitTests cases whose
action still has no single-transition run(). This script buckets by both.
"""
from __future__ import annotations
import re, sys
from collections import Counter
from pathlib import Path

CASES = Path(sys.argv[1])

# run()-having actions at the MF-031 tip (before this ticket) and after MF-032.
RUN_BEFORE = {"BuildSkillCli", "ScaffoldProject", "UpdateTicketDesired", "UpdateTicketCurrent", "Stutter"}
RUN_AFTER = RUN_BEFORE | {"InstallLocalCli", "ScaffoldWorkflow", "RecordBudgets", "OpenTicket"}

name_re = re.compile(r"name='(case_\d+_[a-z_]+)'")
action_re = re.compile(r"action='([A-Za-z]+)'")
before_ts_re = re.compile(r"'ticket_state':\s*(\{[^{}]*\})")

total = 0
materializable = 0
exec_before = 0
exec_after = 0
per_action = Counter()
per_action_exec_after = Counter()
name = None
before_stage = None
for line in CASES.open():
    m = name_re.search(line)
    if m:
        name, before_stage = m.group(1), None
        continue
    if name is None:
        continue
    if before_stage is None and "before={" in line:
        bm = before_ts_re.search(line)
        stages = [int(v) for v in re.findall(r":\s*(\d+)", bm.group(1))] if bm else [0]
        before_stage = max(stages) if stages else 0
        continue
    am = action_re.search(line)
    if am and before_stage is not None:
        action = am.group(1)
        mat = before_stage <= 3
        total += 1
        per_action[action] += 1
        if mat:
            materializable += 1
        if mat and action in RUN_BEFORE:
            exec_before += 1
        if mat and action in RUN_AFTER:
            exec_after += 1
            per_action_exec_after[action] += 1
        name = None
        before_stage = None

def pct(n): return f"{100*n/total:.1f}%"
print(f"reduced corpus: {CASES}")
print(f"total cases: {total}\n")
print("AXIS 1 -- before-state materializable (MF-031's axis):")
print(f"  {materializable:7d}  {pct(materializable)}  before-state stage <= 3 (materializable)")
print(f"  {total-materializable:7d}  {pct(total-materializable)}  before-state stage >= 4 (needs gate machinery / MF-023)\n")
print("AXIS 2 -- action has a run() adapter, AND before-state materializable (true executability):")
print(f"  EXECUTABLE before MF-032 (run(): {sorted(RUN_BEFORE)}):")
print(f"    {exec_before:7d}  {pct(exec_before)}")
print(f"  EXECUTABLE after  MF-032 (added: InstallLocalCli, ScaffoldWorkflow, RecordBudgets, OpenTicket):")
print(f"    {exec_after:7d}  {pct(exec_after)}")
print(f"  NET UNBLOCKED by MF-032: {exec_after-exec_before}  ({pct(exec_after-exec_before)})\n")
print("per-action corpus counts and MF-032 executable-after breakdown:")
for a in sorted(per_action):
    tag = "run() [MF-032]" if a in (RUN_AFTER-RUN_BEFORE) else ("run()" if a in RUN_BEFORE else "apply()-only (HARD/BLOCKED)")
    print(f"  {per_action[a]:7d}  {a:22s} {tag:28s} exec-after={per_action_exec_after.get(a,0)}")
