#!/usr/bin/env python3
"""SM-06's gap mutant for a DE-DUPLICATION -- before the removal and after it.

`removal_is_a_delta_rule` says a removal with no mutant in its gap is not a
measurement. The gap a de-duplication opens is not "does the feature still
work" -- nothing executed the copies in the first place. It is:

    IF A COPY OF THE CARD DISAGREED WITH THE CARD, WOULD ANYTHING GO RED?

So each mutant makes ONE copy of a dimension or a scoring rule say something the
card does not say, and the whole repository is asked whether it notices. A copy
nothing can contradict is a copy nothing is guarding, and that -- not the line
count -- is what the duplication cost.

THIS FILE SPELLS NO PART OF THE CARD. Every find-string is located at run time
by matching a needle parsed out of `references/eval_scorecard.md`, so the
measurement script is not itself a copy of the thing it is measuring. That is
not tidiness: `tests/test_card_has_one_home.py` scans generators under
`specs/results/` and this is one, so a literal here would be a violation of the
rule this run exists to establish.

## --before, run at 6aac1ec, BEFORE anything was deleted

  M1  a charter's restated dimension table, two rows swapped so the keys carry
      each other's titles. The PORTS-AS-ADAPTERS shape exactly.
  M2  a scoring rule inverted inside the evidence packet a judge is handed.
  M3  the same rule inverted in the heading every scaffolded card carries.
  M4  CONTROL -- an anchor edited inside a sealed `scorecard.md`, which is a
      copy something does compare (`seal`, and R-H4 via `audit`).

M4 is the control because R2: if M4 were also green the harness would be broken
and a green on M1-M3 would say nothing at all.

## --after, run on the de-duplicated tree

The copies M1-M3 mutated are gone, so the after-mutant is REINTRODUCTION: put a
disagreeing copy back into a live file and require that something goes red. A
removal that merely deletes the copies leaves the next author free to write them
again; the check is what makes the removal hold.

Usage:
    python3 .../SM-06/run_dup_mutants.py --before [--only M1]
    python3 .../SM-06/run_dup_mutants.py --after

Reverts every mutation on the way out, including on failure.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
CARD = ROOT / "references/eval_scorecard.md"
SCORE_TOOLS = ROOT / "examples/validation/scorecards/score_tools.py"

sys.path.insert(0, str(ROOT / "tests"))


def _card_module():
    """The needles, and the matcher, from the check itself -- never a second copy."""
    spec = importlib.util.spec_from_file_location(
        "sm06_one_home", ROOT / "tests/test_card_has_one_home.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _rubric(one_home):
    spec = importlib.util.spec_from_file_location("sm06_st", SCORE_TOOLS)
    st = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(st)
    return st.load_rubric(CARD)


# ---------------------------------------------------------------------------
# locating a copy without naming it
# ---------------------------------------------------------------------------

def find_line(path: str, one_home, needle: str, occurrence: int = 0) -> str:
    """The n-th line of `path` whose content words contain `needle`."""
    hits = [ln for ln in (ROOT / path).read_text().splitlines()
            if needle in one_home._content(ln)]
    if len(hits) <= occurrence:
        raise SystemExit(f"{path}: no line #{occurrence} whose content words contain "
                         f"{needle!r} (found {len(hits)})")
    return hits[occurrence]


def replace_once(path: str, old: str, new: str) -> None:
    p = ROOT / path
    text = p.read_text()
    if text.count(old) != 1:
        raise SystemExit(f"{path}: {old[:80]!r} occurs {text.count(old)} times, expected 1")
    p.write_text(text.replace(old, new))


def invert(line: str) -> str:
    """Make a restated rule say the opposite, without writing the rule down."""
    for word, opposite in (("never", "ALWAYS"), ("NEVER", "ALWAYS"),
                           ("no ", "every "), ("not ", "")):
        if word in line:
            return line.replace(word, opposite, 1)
    return line + "  <!-- SM-06: made to disagree -->"


# ---------------------------------------------------------------------------
# the mutants
# ---------------------------------------------------------------------------

def before_mutants(one_home, rubric) -> list[dict]:
    needles = one_home.card_needles(rubric)
    # Whichever rule the card numbers 7 -- looked up, not typed.
    mech = dict(needles["rules"])["rule 7"]
    titles = [one_home._flat(d["name"]) for d in rubric["dimensions"].values()]

    def swap_dimension_rows(path: str):
        """Give two adjacent dimension rows each other's titles."""
        def apply() -> None:
            text = (ROOT / path).read_text()
            rows = [ln for ln in text.splitlines()
                    if needles["dimensions"].search(ln)]
            if len(rows) < 2:
                raise SystemExit(f"{path}: fewer than two dimension rows to swap")
            a, b = rows[2], rows[3]
            ta = next(t for t in titles if t.lower() in a.lower())
            tb = next(t for t in titles if t.lower() in b.lower())
            replace_once(path, a + "\n" + b,
                         a.replace(ta, tb) + "\n" + b.replace(tb, ta))
        return apply

    def invert_rule(path: str, needle: str, occurrence: int = 0):
        def apply() -> None:
            line = find_line(path, one_home, needle, occurrence)
            replace_once(path, line, invert(line))
        return apply

    def break_sealed_anchor():
        """The CONTROL: an anchor inside a sealed card, which something compares."""
        def apply() -> None:
            card = _sealed_card(one_home, needles)
            anchor = next(n for _, n in needles["anchors"])
            line = find_line(str(card.relative_to(ROOT)), one_home, anchor)
            replace_once(str(card.relative_to(ROOT)), line,
                         line + " (SM-06 M4: no longer the card's anchor)")
        return apply

    return [
        {"id": "M1", "kind": "prose copy", "where": "README.md",
         "copies": "the dimension table",
         "makes_it_say": "two dimension keys carrying each other's titles -- the "
                         "PORTS-AS-ADAPTERS shape, a restated table whose rows got "
                         "attributed to the wrong thing",
         "apply": swap_dimension_rows("README.md")},
        {"id": "M2", "kind": "prose copy",
         "where": "specs/results/scorecards/ports-as-adapters/measure/build_evidence_packets.py",
         "copies": "a scoring rule, written into the evidence packet a judge is handed",
         "makes_it_say": "the exact inversion of that rule, in the one place it most "
                         "corrupts a measurement",
         "apply": invert_rule(
             "specs/results/scorecards/ports-as-adapters/measure/build_evidence_packets.py",
             mech, 1)},
        {"id": "M3", "kind": "prose copy",
         "where": "examples/validation/scorecards/score_tools.py (`_skeleton_md`)",
         "copies": "the same rule, hand-written into every scaffolded scorecard.md "
                   "OUTSIDE the served rubric and outside `served_digest`",
         "makes_it_say": "its inversion, in the file the judge fills in",
         "apply": invert_rule("examples/validation/scorecards/score_tools.py", mech)},
        {"id": "M4", "kind": "digest-covered copy (CONTROL)",
         "where": "a sealed scorecard.md under specs/results/scorecards/",
         "copies": "the anchors, reproduced so the bar sits beside the score",
         "makes_it_say": "an anchor that is no longer the card's",
         "apply": break_sealed_anchor()},
    ]


def _sealed_card(one_home, needles) -> pathlib.Path:
    anchor = next(n for _, n in needles["anchors"])
    for p in sorted((ROOT / "specs/results/scorecards").rglob("scorecard.md")):
        if any(anchor in one_home._content(ln) for ln in p.read_text().splitlines()):
            return p
    raise SystemExit("no scaffolded scorecard.md carrying the anchors was found")


def after_mutants(one_home, rubric) -> list[dict]:
    """The copies are gone. Put one back, disagreeing, and require a red."""
    needles = one_home.card_needles(rubric)
    dims = list(rubric["dimensions"].items())

    def reintroduce_swapped_table():
        def apply() -> None:
            (a_key, a), (b_key, b) = dims[2], dims[3]
            block = (f"\n\n<!-- SM-06 A1 -->\n"
                     f"| **{a_key}** | {one_home._flat(b['name'])} | ... |\n"
                     f"| **{b_key}** | {one_home._flat(a['name'])} | ... |\n")
            p = ROOT / "README.md"
            p.write_text(p.read_text() + block)
        return apply

    def reintroduce_inverted_rule():
        def apply() -> None:
            lead = one_home._flat(re.match(r"\s*\*\*(.+?)\*\*",
                                           rubric["scoring_rules"][0]).group(1))
            p = ROOT / "PORTS-AS-ADAPTERS-EPIC.md"
            p.write_text(p.read_text() + f"\n\n<!-- SM-06 A2 -->\n- **{lead}** optional.\n")
        return apply

    return [
        {"id": "A1", "kind": "reintroduced prose copy", "where": "README.md",
         "copies": "the dimension table, put back",
         "makes_it_say": "two keys carrying each other's titles -- M1's shape, after "
                         "the copy was deleted",
         "apply": reintroduce_swapped_table()},
        {"id": "A2", "kind": "reintroduced prose copy", "where": "PORTS-AS-ADAPTERS-EPIC.md",
         "copies": "a scoring rule, put back into the charter it was deleted from",
         "makes_it_say": "that the rule is optional",
         "apply": reintroduce_inverted_rule()},
    ]


# ---------------------------------------------------------------------------
# the harness
# ---------------------------------------------------------------------------

FAIL_RX = re.compile(r"^(?:FAILED|ERROR)\s+(\S+)", re.M)


def run(cmd: list[str], timeout: int) -> dict:
    t0 = time.time()
    try:
        cp = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        out, code = cp.stdout + cp.stderr, cp.returncode
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        code = -9
    return {"cmd": " ".join(cmd), "exit": code, "secs": round(time.time() - t0, 1),
            "failures": sorted(set(FAIL_RX.findall(out)))}


def observe(skip_suite: bool) -> dict:
    """Every verdict surface in the repository that could plausibly notice."""
    obs = {}
    if not skip_suite:
        # The acceptance command verbatim, so the mutants are judged by the same
        # surface the ticket is accepted on.
        obs["suite"] = run(["uv", "run", "--with", "pytest", "--with", "pyyaml",
                            "python", "-m", "pytest", "tests", "-q", "--no-header",
                            "-p", "no:cacheprovider"], timeout=2400)
    obs["score_tools_check"] = run(
        [sys.executable, "examples/validation/scorecards/score_tools.py", "check",
         "specs/results/scorecards"], timeout=300)
    obs["score_tools_audit"] = run(
        [sys.executable, "examples/validation/scorecards/score_tools.py", "audit"],
        timeout=600)
    obs["score_tools_serve"] = run(
        [sys.executable, "examples/validation/scorecards/score_tools.py", "serve"],
        timeout=120)
    obs["demonstrate"] = run(
        [sys.executable, "examples/validation/instruments/demonstrate.py"], timeout=2400)
    return obs


def red(obs: dict, baseline: dict) -> list[str]:
    out = []
    for key, o in obs.items():
        b = baseline.get(key, {})
        new = sorted(set(o["failures"]) - set(b.get("failures", [])))
        if o["exit"] != b.get("exit") or new:
            out.append(f"{key}: exit {b.get('exit')} -> {o['exit']}"
                       + (f", new failures {new}" if new else ""))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--before", action="store_true")
    g.add_argument("--after", action="store_true")
    ap.add_argument("--only", action="append")
    ap.add_argument("--skip-suite", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args()

    phase = "before" if args.before else "after"
    out_path = pathlib.Path(args.out or HERE / f"dup-mutants-{phase}.json")

    own = str(HERE.relative_to(ROOT))
    dirty = "\n".join(l for l in subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT,
        capture_output=True, text=True).stdout.strip().splitlines()
        if own not in l).strip()
    if dirty:
        print("REFUSING: working tree is dirty. A mutant run on a dirty tree measures "
              "the dirt.\n" + dirty, file=sys.stderr)
        return 2

    one_home = _card_module()
    rubric = _rubric(one_home)
    mutants = before_mutants(one_home, rubric) if args.before \
        else after_mutants(one_home, rubric)

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()
    print(f"# de-duplication gap mutants, phase={phase}, at {head}")
    print("# BASELINE (unmutated tree)")
    baseline = observe(args.skip_suite)
    for k, v in baseline.items():
        print(f"    {k:22s} exit {v['exit']:>3}  {v['secs']:>7}s  {len(v['failures'])} failures")

    results = []
    for m in mutants:
        if args.only and m["id"] not in args.only:
            continue
        print(f"\n# {m['id']} ({m['kind']}) -- {m['where']}")
        print(f"#   makes it say: {m['makes_it_say']}")
        try:
            m["apply"]()
            obs = observe(args.skip_suite)
        finally:
            subprocess.run(["git", "checkout", "--", "."], cwd=ROOT, check=True)
        went_red = red(obs, baseline)
        verdict = "CAUGHT" if went_red else "UNCAUGHT"
        print(f"#   -> {verdict}")
        for line in went_red:
            print(f"       {line}")
        results.append({k: v for k, v in m.items() if k != "apply"}
                       | {"verdict": verdict, "red_surfaces": went_red,
                          "observations": obs})

    out_path.write_text(json.dumps(
        {"phase": phase, "head": head, "baseline": baseline, "mutants": results},
        indent=2) + "\n")
    print(f"\nwrote {out_path}")
    print(f"CAUGHT   {[r['id'] for r in results if r['verdict'] == 'CAUGHT']}")
    print(f"UNCAUGHT {[r['id'] for r in results if r['verdict'] == 'UNCAUGHT']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
