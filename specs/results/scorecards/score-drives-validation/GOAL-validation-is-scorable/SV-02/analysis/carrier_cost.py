#!/usr/bin/env python3
"""SV-02. What each carrier for the validation property COSTS on the served surface.

Run from the repository root:

    python3 specs/results/scorecards/score-drives-validation/\
GOAL-validation-is-scorable/SV-02/analysis/carrier_cost.py

Imports `score_tools` to RENDER hypothetical served text. It changes nothing on
disk, ships no production code and nothing imports it. The renderer is the real
one, so these byte counts are the bytes a judge would actually be handed --
not an estimate of them.

The surface metric is `serve | wc -c`. The shipped value is 6,281 bytes and
9 rungs and IT MUST NOT GROW.
"""
import copy
import os
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join("examples", "validation", "scorecards"))
import score_tools as st  # noqa: E402

RUBRIC = pathlib.Path("references") / "eval_scorecard.md"


def rungs(text):
    return sum(1 for line in text.splitlines()
               if line.startswith("- **") and line[4:5].isdigit())


def report(label, text, base=None):
    n = len(text.encode())
    d = "" if base is None else f"   delta {n - base:+d}"
    print(f"  {label:52s} {n:6d} bytes  {rungs(text):2d} rungs{d}")
    return n


def main():
    rub = st.load_rubric(RUBRIC)
    base_text = st.served_rubric(rub, 5)
    print("## 0. The shipped surface, rendered by the real renderer")
    base = report("v5 as shipped", base_text)
    shell = subprocess.run(
        [sys.executable, "examples/validation/scorecards/score_tools.py", "serve"],
        capture_output=True, text=True).stdout
    print(f"  cross-check against `serve` on stdout:              "
          f"{len(shell.encode()):6d} bytes  (must equal the line above)")
    print()

    # ---------------------------------------------------------------- P
    print("## 1. CARRIER P -- sharpen the N-D1 note prompt. No rung, no anchor.")
    print("    The property is already elicited; this asks for the two things")
    print("    judges volunteer anyway -- the denominator and the structural")
    print("    reason the green region is green.")
    cur = rub["notes"]["N-D1"]["prompt"]
    print(f"\n    current  ({len(cur.encode())} bytes): {cur}")
    # "Name the fault you seeded if you seeded one" is already asked twice on
    # the served surface -- scoring rule 8 and the `Judging practice` block --
    # so replacing it is a DEDUPLICATION, and that is where the budget for the
    # two new asks comes from.
    variants = {
        "P1  denominator only": (
            "What went red when you broke it, with the denominator, and what "
            "class stays green by construction?"),
        "P2  provenance clause only": (
            "What went red when you broke it, and what class stays green by "
            "construction? Who wrote the cases is not an input."),
        "P3  BOTH -- the proposal": (
            "What went red when you broke it, with the denominator, and what "
            "class stays green by construction? Who wrote the cases is not an "
            "input."),
        "P4  both, verbose (rejected)": (
            "Break something the artifact claims to check, run the artifact's "
            "OWN checking, and say what went red -- with the denominator. Then "
            "name a class it stays green on and why that is structural rather "
            "than an oversight. Who wrote the cases is not an input."),
    }
    for name, prompt in variants.items():
        r = copy.deepcopy(rub)
        r["notes"]["N-D1"]["prompt"] = prompt
        report(name, st.served_rubric(r, 5), base)
    print()

    # ---------------------------------------------------------------- R
    print("## 2. CARRIER R -- restore D4 as a SCORED dimension, provenance-free,")
    print("    and drop the N-D4 note (a dimension is scored or noted, never both).")
    d4 = {
        "name": "behavior preservation",
        "question": ("Does the changed design still do everything the baseline "
                     "did, and can the check that says so be shown to fail?"),
        "preamble": "",
        "anchors": {
            0: "Behavior changed and nobody checked.",
            1: ("A check passes, with no argument that it covers the behavior "
                "at issue."),
            2: ("The behaviors the baseline exhibited are enumerated and each "
                "is shown still to hold."),
            3: ("2, **and** a deliberate behavior-breaking change is shown to "
                "be *caught* -- the check is demonstrated to be capable of "
                "failing, with the denominator recorded."),
        },
        "caveat": ("Where the cases came from is not an input. Hand-written, "
                   "generated, property-based and model-derived score "
                   "identically; what is scored is whether the check has a "
                   "demonstrated red and a named region it stays green on. And "
                   "a demonstration you ran is not the artifact's: if the "
                   "artifact's own record carries none, say so and take 2."),
    }
    r = copy.deepcopy(rub)
    r["dimensions"]["D4"] = d4
    del r["notes"]["N-D4"]
    # Render with D4 scored and N-D4 unnoted, the way score_tools would if
    # `scored_dims`/`note_dims` were changed. Those two functions are
    # production code; SV-02 ships none, so they are patched HERE, in the
    # analysis, and restored immediately.
    old_s, old_n = st.scored_dims, st.note_dims
    st.scored_dims = lambda v: ["D2", "D3", "D4"]
    st.note_dims = lambda v: ["D1", "D5"]
    try:
        report("R  D4 scored (0-3), N-D4 note dropped", st.served_rubric(r, 5), base)
    finally:
        st.scored_dims, st.note_dims = old_s, old_n
    print()

    # ---------------------------------------------------------------- N
    print("## 3. CARRIER N -- a NEW sixth dimension, note kept. For comparison only.")
    r = copy.deepcopy(rub)
    r["dimensions"]["D4"] = d4
    old_s = st.scored_dims
    st.scored_dims = lambda v: ["D2", "D3", "D4"]
    try:
        report("N  new scored rung, all three notes kept",
               st.served_rubric(r, 5), base)
    finally:
        st.scored_dims = old_s
    print()

    # ---------------------------------------------------------------- refusal
    print("## 4. RUN, not argued: does `serve` refuse a rubric that carries")
    print("    anchors for a retired dimension? Carrier R needs a production")
    print("    change, and this is the size of it.")
    text = RUBRIC.read_text()
    block = ("### D4 — behavior preservation\n\n"
             "- **0** — Behavior changed and nobody checked.\n"
             "- **1** — A check passes, with no argument that it covers the "
             "behavior at issue.\n"
             "- **2** — The behaviors the baseline exhibited are enumerated "
             "and each is shown still to hold.\n"
             "- **3** — 2, **and** the check is shown capable of failing.\n"
             "- **4** — 3, **and** the artifact's OWN record carries the "
             "demonstration, with its denominator.\n\n")
    patched = text.replace("## The recorded notes", block + "## The recorded notes", 1)
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                     prefix="SV-02-scratch-rubric-") as fh:
        fh.write(patched)
        scratch = fh.name
    try:
        p = subprocess.run(
            [sys.executable, "examples/validation/scorecards/score_tools.py",
             "serve", "--rubric", scratch],
            capture_output=True, text=True)
        print(f"    exit {p.returncode}")
        for line in (p.stderr or p.stdout).strip().splitlines()[:6]:
            print(f"    | {line}")
    finally:
        os.unlink(scratch)


if __name__ == "__main__":
    main()
