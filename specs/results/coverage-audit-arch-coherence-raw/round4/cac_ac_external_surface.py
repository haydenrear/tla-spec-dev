#!/usr/bin/env python3
"""Enumerate the CLI's EXTERNAL surface (Sweep 4): every caller-drivable
command path, positional and option, walked from the shipped argparse tree.

    python3 specs/results/coverage-audit-arch-coherence-raw/cac_ac_external_surface.py
"""
import argparse, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from scripts.tla_spec_dev import build_parser  # noqa: E402

rows = []

def walk(parser, path):
    subs = None
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            subs = action
            continue
        if isinstance(action, (argparse._HelpAction, argparse._VersionAction)):
            continue
        if action.option_strings:
            for opt in action.option_strings:
                rows.append((path, "option", opt))
        else:
            rows.append((path, "positional", action.dest))
    if subs:
        for name, sub in subs.choices.items():
            rows.append((path, "subcommand", name))
            walk(sub, f"{path} {name}")

walk(build_parser(), "tla-spec-dev")
for p, kind, name in rows:
    print(f"{p}\t{kind}\t{name}")
print(f"# TOTAL {len(rows)}", file=sys.stderr)
