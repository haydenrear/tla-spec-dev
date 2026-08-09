"""RD-06. The subjects this ticket produced, and the one thing it must not have done.

RD-06 produces subjects; RD-03 scores them, blind. Producing a subject and
judging it are different jobs, and one agent doing both is how a round scores
its own homework. So the properties asserted here are the ones that decide
whether the handover is honest:

  * every subject carries a scope DECLARED before it existed, and a tag DERIVED
    by RD-05's shipped predicate rather than asserted by this ticket;
  * every subject's prompt is preserved AS DISPATCHED, so a later measurement
    reads what was sent -- `PA-06-DF-10`, where a length headline was measured
    against a file the arm never received;
  * every before/after pair has BOTH complexity records on disk, which is the
    precondition D2 anchor 3 has never had on the product side;
  * no arm edited the shared behavioural contract, because two arms measured
    against two requirements are not an A/B;
  * and **nothing here is scored**. `scan_for_scores` is the executable form of
    that claim.

R1 -- an instrument ships with a demonstrated FAILING input.
`test_the_score_scanner_fires_on_a_demonstrated_failing_input` feeds
`scan_for_scores` a card-shaped file and a `D3 = 4` line and requires it to
report both. A scanner nobody has seen fire is a scanner that reports zero
because it cannot report anything.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
AB = REPO_ROOT / "examples/validation/ab"
SUBJECTS_TOML = REPO_ROOT / "examples/validation/scorecards/subjects.toml"
TAGS_PY = REPO_ROOT / "examples/validation/scorecards/architecture_tags.py"
DISPATCH_DIR = AB / "dispatch/reading-discipline"
BLIND = REPO_ROOT / "specs/results/scorecards/reading-discipline/blind"
EVIDENCE = (REPO_ROOT
            / "specs/results/scorecards/reading-discipline/GOAL-product-round/RD-06")

#: The six labels RD-06 produced. Opaque on purpose: the label -> arm mapping is
#: in `UNBLINDING-rd06.md`, which no judge is given.
GREENFIELD = ("Z", "E", "N")
#: after -> before. Published, because a judge cannot award D2 anchor 3 without
#: being told which tree is the before.
PAIRS = {"M": "Z", "F": "E", "D": "N"}
LABELS = GREENFIELD + tuple(PAIRS)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def subject_name(label: str) -> str:
    return f"rd06_artifact_{label}"


def declared_subjects() -> dict:
    return tomllib.loads(SUBJECTS_TOML.read_text())["subject"]


def tree(label: str) -> Path:
    return BLIND / f"artifact_{label}"


# --------------------------------------------------------------------------
# the scope, declared before the subject existed
# --------------------------------------------------------------------------

def test_every_rd06_subject_declares_a_scope_that_points_at_a_real_tree():
    subjects = declared_subjects()
    missing = [label for label in LABELS if subject_name(label) not in subjects]
    assert not missing, f"declared no scope for: {missing}"

    for label in LABELS:
        entry = subjects[subject_name(label)]
        assert entry["example"] == "ab_quota_ledger"
        assert entry["scope"] == [
            f"specs/results/scorecards/reading-discipline/blind/artifact_{label}"
        ]
        assert (REPO_ROOT / entry["scope"][0]).is_dir(), (
            f"artifact_{label}: the declared scope does not exist. A scope "
            f"declared before the tree is the point; a scope that never "
            f"acquires a tree is a subject nobody can score."
        )
        # The declaration is a PRIOR, not a derivation. It must be one of the
        # two values that carry refusal authority, so a disagreement with the
        # derived value is legible as TAG-DISPUTED rather than as a typo.
        assert entry["declared_effect_boundary"] in ("effectful", "ports-and-adapters")
        assert entry["labels"] == [], (
            f"artifact_{label}: no card has scored this subject. RD-06 scores "
            f"nothing, so a card mapping here would be one this ticket invented."
        )


# --------------------------------------------------------------------------
# the tag, DERIVED -- RD-05's predicate used rather than re-litigated
# --------------------------------------------------------------------------

def test_every_rd06_subject_carries_a_tag_derived_by_rd05s_shipped_predicate():
    tags = _load(TAGS_PY, "rd06_architecture_tags")
    subjects = declared_subjects()
    for label in LABELS:
        scope = subjects[subject_name(label)]["scope"]
        record = tags.measure(scope, REPO_ROOT)
        assert record is not None, (
            f"artifact_{label}: the shipped complexity instrument could not "
            f"report on the declared scope at all."
        )
        value, facts = tags.derive(record)
        assert value in tags.VALUES or value.startswith(tags.UNDERIVABLE), value
        if value.startswith(tags.UNDERIVABLE):
            reason = value[len(tags.UNDERIVABLE):]
            assert reason, (
                f"artifact_{label}: UNDERIVABLE with no reason. Underivable "
                f"fails open and is not a defect, but an unreasoned refusal is "
                f"an absence dressed as a measurement."
            )
        assert facts, f"artifact_{label}: derived with no facts behind it"


def test_a_disagreement_between_derived_and_declared_fails_open():
    """Guard, not a result. Whatever the six derive, none of it may refuse."""
    tags = _load(TAGS_PY, "rd06_architecture_tags_agreement")
    subjects = declared_subjects()
    for label in LABELS:
        entry = subjects[subject_name(label)]
        record = tags.measure(entry["scope"], REPO_ROOT)
        value, _ = tags.derive(record)
        agreement = tags.agreement_of(value, entry["declared_effect_boundary"])
        assert agreement in ("agree", "TAG-DISPUTED", "UNDERIVABLE")
        # All three states are comparable. `has_authority` is what a refusal
        # would have to consult, and a disputed pair must never reach it.
        if agreement != "agree":
            assert not tags.has_authority(None)


# --------------------------------------------------------------------------
# the before/after, which is the shape the product side has never had
# --------------------------------------------------------------------------

def _complexity_record(label: str) -> dict:
    path = EVIDENCE / f"complexity-artifact_{label}.json"
    assert path.is_file(), f"no recorded complexity figures for artifact_{label}"
    return json.loads(path.read_text())


def test_each_before_after_pair_has_both_trees_and_both_figures_recorded():
    """D2 anchor 3: 'the before and after figures are BOTH recorded.'

    This asserts the precondition and nothing else. Whether a simplification
    was made, and whether it was worth anything, is the judge's call and is
    deliberately not checked here.
    """
    for after, before in PAIRS.items():
        assert tree(before).is_dir(), f"artifact_{before}: the before tree is missing"
        assert tree(after).is_dir(), f"artifact_{after}: the after tree is missing"
        for label in (before, after):
            record = _complexity_record(label)
            assert record.get("modules"), (
                f"artifact_{label}: complexity record with no modules in it"
            )
        # Two records, never a delta. MF-020 is wired into the instrument --
        # `code_complexity.py` ships no comparison mode -- and it is wired in
        # here too: this test may not compute one.


def test_the_pairing_is_published_so_a_judge_can_reach_anchor_three():
    published = (EVIDENCE / "SUBJECTS-RD-06.md").read_text()
    for after, before in PAIRS.items():
        assert re.search(rf"\bartifact_{after}\b.*\bartifact_{before}\b", published) \
            or re.search(rf"`{after}`.*`{before}`", published), (
            f"the pairing {after} <- {before} is not published. A before/after "
            f"nobody is told about is two greenfield artifacts."
        )


# --------------------------------------------------------------------------
# what was DISPATCHED is what a later measurement reads
# --------------------------------------------------------------------------

def test_the_dispatched_prompt_is_preserved_and_verifies():
    record_py = _load(AB / "dispatch_record.py", "rd06_dispatch_record")
    problems = record_py.verify(DISPATCH_DIR, verbose=False)
    assert problems == [], problems

    rows = {r.arm: r for r in record_py.load_records(DISPATCH_DIR)}
    for label in LABELS:
        arm = f"artifact_{label}"
        assert arm in rows, f"{arm}: nothing records what this subject was sent"
        assert rows[arm].provenance == "preserved", (
            f"{arm}: {rows[arm].provenance}. A reconstruction is strictly weaker "
            f"evidence and must never read as a preserved dispatch."
        )


def test_the_greenfield_envelope_is_identical_across_the_three_arms():
    """The delta a dispatch adds may not itself be a treatment.

    `PA-06-DF-10`: the previous round's additions differed per arm and two of
    them named the epic to the arm whose whole job was architectural silence.
    Here the envelope is one block, and the only thing that varies in it is the
    opaque label of the working directory.
    """
    envelopes = {}
    for label in GREENFIELD:
        text = (DISPATCH_DIR / f"artifact_{label}.dispatched.md").read_text()
        head, sep, _ = text.partition("\n---\n\n")
        assert sep, f"artifact_{label}: no envelope boundary in the dispatched bytes"
        envelopes[label] = head.replace(f"artifact_{label}", "artifact_<LABEL>")
    distinct = set(envelopes.values())
    assert len(distinct) == 1, (
        "the three greenfield arms did not receive the same envelope:\n"
        + "\n---\n".join(sorted(distinct))
    )
    envelope = distinct.pop()
    for word in ("reading-discipline", "hexagonal", "ports", "adapter", "complexity"):
        assert word not in envelope.lower(), (
            f"the shared envelope leaks {word!r} to every arm"
        )


# --------------------------------------------------------------------------
# no arm changed the requirement
# --------------------------------------------------------------------------

def test_no_produced_tree_carries_its_own_copy_of_the_shared_contract():
    shared = (AB / "tests/test_behavior.py").read_bytes()
    for label in LABELS:
        for path in tree(label).rglob("test_behavior.py"):
            assert path.read_bytes() == shared, (
                f"{path} differs from the shared behavioural contract. Two arms "
                f"measured against two requirements are not an A/B."
            )


# --------------------------------------------------------------------------
# RD-06 SCORED NOTHING, and here is the scanner that says so
# --------------------------------------------------------------------------

#: `D3 = 4`, `D2=2`, `D5 = 0` -- a dimension with a number assigned to it.
#: Deliberately NOT `\bD[1-5]\b` alone: this repository's prose says "D2 anchor
#: 3" and "D3 went 1 -> 4" constantly, and a scanner that fired on those would
#: be reporting the vocabulary rather than the act.
_SCORE_LINE = re.compile(r"\bD[1-5]\s*[:=]\s*[0-4]\b")


def scan_for_scores(root: Path) -> list[str]:
    """Every place under `root` where something was given a D-number.

    Two shapes: a card-shaped JSON object (`dimensions` mapping a D-key to an
    object with a numeric `score`), and a line assigning a value to a
    dimension. Returns findings as strings; it decides nothing and raises
    nothing.
    """
    findings: list[str] = []
    if not root.exists():
        return findings
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if path.name == "scorecard.json":
            findings.append(f"{path}: a filled card")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if path.suffix == ".json":
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                data = None
            dims = (data or {}).get("dimensions") if isinstance(data, dict) else None
            if isinstance(dims, dict):
                for key, block in dims.items():
                    if (re.fullmatch(r"D[1-5]", str(key))
                            and isinstance(block, dict)
                            and isinstance(block.get("score"), (int, float))):
                        findings.append(f"{path}: dimensions.{key}.score")
        for number, line in enumerate(text.splitlines(), start=1):
            if _SCORE_LINE.search(line):
                findings.append(f"{path}:{number}: {line.strip()[:90]}")
    return findings


def test_the_score_scanner_fires_on_a_demonstrated_failing_input(tmp_path):
    """R1. An instrument that has never been seen to fire reports zero for free."""
    (tmp_path / "scorecard.json").write_text(json.dumps(
        {"dimensions": {"D3": {"score": 4, "citation": "..."}}}))
    (tmp_path / "mechanical.json").write_text(json.dumps(
        {"dimensions": {"D2": {"score": 2}}}))
    (tmp_path / "NOTES.md").write_text(
        "the artifact is modular\nD3 = 4 on this tree\nand D2 anchor 3 is reachable\n")
    findings = scan_for_scores(tmp_path)
    assert any("scorecard.json" in f for f in findings), findings
    assert any("dimensions.D2.score" in f for f in findings), findings
    assert any("NOTES.md:2" in f for f in findings), findings
    # And the line it must NOT fire on: the vocabulary without an assignment.
    assert not any("NOTES.md:3" in f for f in findings), findings


def test_rd06_scored_nothing():
    findings = scan_for_scores(EVIDENCE) + scan_for_scores(BLIND)
    assert findings == [], (
        "RD-06 produces subjects and scores none of them. Something under its "
        "evidence or its produced trees assigns a D-number:\n  "
        + "\n  ".join(findings)
    )
