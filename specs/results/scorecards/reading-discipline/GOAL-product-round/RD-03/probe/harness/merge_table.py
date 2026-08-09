#!/usr/bin/env python3
"""One table, per (tree, mutant, instrument). No aggregate kill rate is
computed anywhere in this file and none may be computed from its output."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from anchors import ARCHITECTURE

TREES = ["artifact_Z", "artifact_M", "artifact_N", "artifact_D", "artifact_E", "artifact_F"]
MUTANTS = ["M01","M02","M03","M04","M05","M06","M07","M08","M09","M10",
           "PA-M11","PA-M12","PA-M13","PA-M14","FI-M15"]
HAND = ["own-tests", "shared-suite", "shared-suite-fake"]
MODEL = ["corpus-whole", "corpus-neg", "map-silent", "map-checking"]

table, notes = {}, {}
for tree in TREES:
    hand = json.load((HERE / "out" / f"{tree}.json").open())
    corpus_path = HERE / "out" / "corpus" / f"{tree}.json"
    corpus = json.load(corpus_path.open())["per_mutant"] if corpus_path.exists() else {}
    catalogue_note = json.load((HERE / "out" / "catalogue_coverage.json").open())[tree] \
        if (HERE / "out" / "catalogue_coverage.json").exists() else {}
    table[tree] = {}
    for mutant in MUTANTS:
        row = hand["per_mutant"][mutant]
        kind = row["verdict_kind"]
        cells = dict(row["cells"])
        for name in HAND:
            cells.setdefault(name, "N/A (no such instrument on this tree)")
        for name in MODEL:
            if kind != "MEASURED":
                # A row whose semantic was never reproduced decides nothing on
                # ANY instrument. Reporting a corpus cell for it would report a
                # kill of something that is not the declared fault.
                cells[name] = cells["own-tests"] if kind != "MEASURED" else cells[name]
            elif mutant in corpus:
                cells[name] = corpus[mutant].get(name, "NOT_RUN")
            else:
                cells[name] = "NOT_RUNNABLE (re-anchoring needs >1 edit; that driver applies one)"
        table[tree][mutant] = cells

out = {"architecture": ARCHITECTURE, "instruments_hand_written": HAND,
       "instruments_model_derived": MODEL, "table": table}
(HERE / "out" / "MERGED-TABLE.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")

width = max(len(m) for m in MUTANTS)
for tree in TREES:
    print(f"\n### {tree}  [{ARCHITECTURE[tree]}]")
    header = " " * (width + 2) + "".join(n[:13].ljust(15) for n in HAND + MODEL)
    print(header)
    for mutant in MUTANTS:
        cells = table[tree][mutant]
        print("  " + mutant.ljust(width) +
              "".join(str(cells[n])[:13].ljust(15) for n in HAND + MODEL))
