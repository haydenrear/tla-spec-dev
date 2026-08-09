#!/usr/bin/env python3
"""Emit one re-anchored catalogue per tree for eval/run_controls.py.

That driver applies ONE find/replace per mutant, so a mutant whose re-anchoring
on a tree needs more than one edit cannot be expressed through it. Those are
emitted to `skipped` and reported as such -- never silently dropped.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from anchors import TREES, INEXPRESSIBLE

CLASS = {"M01":"guard_relaxation","M02":"guard_relaxation","M03":"guard_relaxation",
         "M04":"durable_content","M05":"durable_content","M06":"output_oracle",
         "M07":"wrong_value","M08":"cross_aspect","M09":"ordering","M10":"wrong_value",
         "PA-M11":"adapter_internal","PA-M12":"adapter_internal","PA-M13":"adapter_internal",
         "PA-M14":"wrong_value","FI-M15":"wrong_value"}
ORDER = list(CLASS)

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
summary = {}
for tree, anchors in TREES.items():
    lines, skipped = [f'# RD-03 re-anchored catalogue for {tree}. Generated, not hand-edited.\n'], {}
    for mutant in ORDER:
        entry = anchors.get(mutant)
        if entry is INEXPRESSIBLE or entry is None:
            skipped[mutant] = "INEXPRESSIBLE on this tree"; continue
        if len(entry) != 1:
            skipped[mutant] = f"re-anchoring needs {len(entry)} edits; this driver applies one"
            continue
        path, find, replace = entry[0]
        lines.append("[[mutants]]")
        lines.append(f'id = {json.dumps(mutant)}')
        lines.append(f'fault_class = {json.dumps(CLASS[mutant])}')
        lines.append(f'path = {json.dumps(path)}')
        lines.append(f'find = {json.dumps(find)}')
        lines.append(f'replace = {json.dumps(replace)}')
        lines.append("")
    (out / f"{tree}.toml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    summary[tree] = {"emitted": [m for m in ORDER if m not in skipped], "skipped": skipped}
print(json.dumps(summary, indent=2))
