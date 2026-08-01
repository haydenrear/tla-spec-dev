"""RC-01: the manifest's own records are checked against what they describe.

MF-026's coverage audit found three defects that no oracle in this toolchain
could ever have caught, because none of them is a behavior:

* **G-5** -- all three `spec_manifest.yaml` files stated "the model's 9
  variables and 15 actions live in TlaSpecDevCli.tla" beside models with
  different counts. AC-01 added `architecture_scan` and `AnalyzeArchitecture`
  and left the comment. The same defect class as EV-01-DF-03, which RP-05 was
  opened to repair -- and RP-05 repaired the instance, not the mechanism.
* **G-7** -- two comments in each manifest cited "the 2026-07-22 scope
  amendment" as their authority. No such amendment exists. A reader following
  the citation found nothing, and one of the two comments was about to become
  affirmatively FALSE when `GenerateCases` landed.
* **G-1** -- `AnalyzeArchitecture` had no row in `effects.actions` at all,
  while the manifest's own rule says an ABSENT row claims "unmapped" and the
  model states that each action's `@port` lines mirror its row.

None of the four oracles can see any of this: TLC checks the model against
itself, the corpus gate counts cases, the effect oracle diffs observed effects
against declarations, and the kill test seeds faults inside modeled boundaries.
A stale number in a comment is invisible to all four. So it is checked here,
against the module beside each manifest, which is the durable form of the check
RP-05 applied by hand to `architecture_components.yaml`.

These tests deliberately DERIVE the figures rather than restating them: a test
that hardcodes 11 and 18 goes stale the same way the comment did.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_TREES = ("program_model", "current", "desired_program_model")


def tree_paths(tree: str) -> tuple[Path, Path]:
    base = REPO_ROOT / "specs" / tree
    return base / "TlaSpecDevCli.tla", base / "spec_manifest.yaml"


def block_after(text: str, header: str, indent: str) -> str:
    """The lines of a YAML block, stopping at the first line less indented."""
    start = text.index(header) + len(header)
    lines = []
    for line in text[start:].splitlines():
        if line.strip() and not line.startswith(indent):
            break
        lines.append(line)
    return "\n".join(lines)


def effects_action_rows(manifest_path: Path) -> set[str]:
    text = manifest_path.read_text(encoding="utf-8")
    assert "\n  actions:\n" in text, f"{manifest_path}: no effects.actions block"
    body = block_after(text, "\n  actions:\n", "    ")
    return set(re.findall(r"^    (\w+):", body, flags=re.MULTILINE))


def justification_rows(manifest_path: Path) -> set[str]:
    text = manifest_path.read_text(encoding="utf-8")
    assert "\njustification:\n" in text, f"{manifest_path}: no justification block"
    body = block_after(text, "\njustification:\n", "  ")
    return set(re.findall(r"^  (\w+):$", body, flags=re.MULTILINE))


def model_counts(tla_path: Path) -> tuple[int, int, int]:
    """(variables, Next disjuncts, @command actions) parsed from the module."""
    text = tla_path.read_text(encoding="utf-8")

    block = re.search(r"^VARIABLES\n(.*?)\n\nvars ==", text, re.S | re.M)
    assert block, f"{tla_path}: no VARIABLES block"
    variables = [line.strip().rstrip(",") for line in block.group(1).splitlines() if line.strip()]

    next_body = re.search(r"\nNext ==\n(.*?)\n\n", text, re.S)
    assert next_body, f"{tla_path}: no Next relation"
    disjuncts = next_body.group(1).count("\\/")

    commands = re.findall(r"^\\\* @command (\w+)", text, flags=re.MULTILINE)
    return len(variables), disjuncts, len(commands)


@pytest.mark.parametrize("tree", MANIFEST_TREES)
def test_the_manifest_states_the_counts_of_the_model_beside_it(tree: str) -> None:
    """G-5. Each manifest is checked against ITS OWN module, not a global figure.

    This distinction is the reason the check exists in this shape. The audit
    reported G-5 against all three manifests as though one model were being
    described three times, and that overstated it: `specs/program_model` is the
    ACCEPTED BASELINE, it predates AC-01, and its "9 variables and 15 actions"
    was correct for the module sitting beside it. Checking each tree against its
    own module states the true property and cannot be satisfied by copying one
    number into three files.
    """
    tla_path, manifest_path = tree_paths(tree)
    variables, disjuncts, commands = model_counts(tla_path)
    # The claim lives in a comment, so it wraps across lines. Strip the comment
    # markers and collapse whitespace before reading it -- a check that only
    # works when the sentence happens to fit on one line is not a check.
    manifest = re.sub(
        r"\s+", " ", re.sub(r"^\s*#\s?", "", manifest_path.read_text(encoding="utf-8"), flags=re.M)
    )

    claim = re.search(
        r"(\d+) variables and (\d+) (?:Next disjuncts|actions)", manifest
    )
    assert claim, f"{manifest_path}: no variable/action count recorded at all"
    assert int(claim.group(1)) == variables, (
        f"{manifest_path} claims {claim.group(1)} variables; "
        f"{tla_path.name} declares {variables}"
    )
    assert int(claim.group(2)) == disjuncts, (
        f"{manifest_path} claims {claim.group(2)} actions; "
        f"{tla_path.name}'s Next has {disjuncts} disjuncts"
    )
    # Stutter carries no @command annotation: it is the stuttering frame
    # condition, not an observable command.
    assert commands == disjuncts - 1


@pytest.mark.parametrize("tree", MANIFEST_TREES)
def test_no_manifest_cites_an_amendment_that_does_not_exist(tree: str) -> None:
    """G-7. A dated citation is a claim, and both of these resolved to nothing.

    The plan's rulings were folded into the PREDECESSOR plan on 2026-07-23 and
    restored into this epic's plan on 2026-08-01. Nothing was ever amended on
    2026-07-22, and two comments per manifest pointed there.
    """
    _, manifest_path = tree_paths(tree)
    manifest = re.sub(r"\s+", " ", manifest_path.read_text(encoding="utf-8"))
    # The two exact citations the audit named. `updated: "2026-07-22"` in the
    # accepted baseline is a date field, not a citation, and is left alone --
    # the defect is pointing a reader at an authority that is not there.
    offenders = [
        phrase
        for phrase in (
            "the 2026-07-22 scope amendment",
            "known_gaps, amended 2026-07-22",
        )
        if phrase in manifest
    ]
    assert offenders == [], (
        f"{manifest_path} cites an amendment that does not exist: {offenders}"
    )


@pytest.mark.parametrize("tree", MANIFEST_TREES)
def test_every_command_action_has_an_effects_row(tree: str) -> None:
    """G-1. An ABSENT row claims "unmapped"; only an EMPTY row claims "no effect".

    `AnalyzeArchitecture` -- this epic's one new action -- had neither, in all
    three manifests, and was the only non-stutter action without a row.
    """
    tla_path, manifest_path = tree_paths(tree)
    text = tla_path.read_text(encoding="utf-8")
    actions = set(re.findall(r"^\\\* @command (\w+)", text, flags=re.MULTILINE))

    rows = effects_action_rows(manifest_path)

    assert actions <= rows, f"{manifest_path}: actions with no effects row: {sorted(actions - rows)}"
    assert rows <= actions, f"{manifest_path}: effects rows that are not actions: {sorted(rows - actions)}"


@pytest.mark.parametrize("tree", MANIFEST_TREES)
def test_every_variable_carries_a_justification_row(tree: str) -> None:
    """Found while closing G-5, and not one of the audit's nine.

    `architecture_scan` had NO row in `justification:` in any tree that has the
    variable. The manifest says `analyze complexity` reads that table and flags
    any variable with no linkage as dead weight, so the epic's own new variable
    has been reported as unjustified since AC-01 closed and nothing failed.
    """
    tla_path, manifest_path = tree_paths(tree)
    variables, _, _ = model_counts(tla_path)
    block = re.search(r"^VARIABLES\n(.*?)\n\nvars ==", tla_path.read_text(encoding="utf-8"), re.S | re.M)
    assert block
    declared = {line.strip().rstrip(",") for line in block.group(1).splitlines() if line.strip()}
    assert len(declared) == variables

    justified = justification_rows(manifest_path)
    assert declared <= justified, (
        f"{manifest_path}: variables with no justification row: {sorted(declared - justified)}"
    )
