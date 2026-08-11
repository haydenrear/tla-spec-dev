#!/usr/bin/env python3
"""RM-02 evidence extraction. Reads the 73 sealed cards and dumps a flat
per-(card, dimension) record so every later claim can be re-derived.

Run from the repository root. Writes JSON to stdout.
NO production code: this lives under the evidence root and nothing imports it.
"""
import json
import glob
import os
import sys

ROOT = os.environ.get("CARDS", "specs/results/scorecards")


def load():
    rows = []
    for p in sorted(glob.glob(os.path.join(ROOT, "**", "scorecard.json"), recursive=True)):
        d = json.load(open(p))
        rel = os.path.relpath(p, ROOT)
        parts = rel.split(os.sep)
        epic_dir = parts[0]
        subject = None
        # arm/subject is recorded on the card where it exists
        subject = d.get("arm")
        for dim, v in sorted((d.get("dimensions") or {}).items()):
            if not isinstance(v, dict):
                continue
            rows.append({
                "path": rel,
                "epic_dir": epic_dir,
                "epic": d.get("epic"),
                "example": d.get("example"),
                "run_id": d.get("run_id"),
                "arm": subject,
                "version": d.get("scorecard_version"),
                "model": (d.get("judge") or {}).get("model"),
                "pass": (d.get("judge") or {}).get("pass"),
                "dim": dim,
                "score": v.get("score"),
                "citations": v.get("citations") or [],
                "rationale": v.get("rationale") or "",
                "refuses_to_claim": v.get("refuses_to_claim"),
                "anchor_reading": v.get("anchor_reading"),
                "practice": (d.get("judging_practice") or {}).get("executed_own_faults"),
            })
    return rows


if __name__ == "__main__":
    json.dump(load(), sys.stdout, indent=1)
