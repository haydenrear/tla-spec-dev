"""Workflow close must not take the cumulative findings ledger with it.

**`SS-01` CHANGED HOW THAT IS ACHIEVED, AND THESE TESTS FOLLOW THE CHANGE.** The
answer used to be a FALLBACK -- the close deleted the ledger and archived a copy,
and `disposition.resolve_ledger` went and found the copy. It is now an ADDRESS:
the ledger lives at `specs/deferred_findings.yaml`, beside the workflow
directories instead of inside one, and the close simply does not remove it. So
the assertion below is the strong form of the same property, and the fallback is
exercised where it now belongs, in
`tests/test_ledger_resolution_is_deterministic.py`.

**AND THE SKIP THESE FOUR TESTS SAT IN WAS COVERING A SECOND REASON.** All four
skipped as `CA-10-DF-12` -- *"`CA-09`'s own proof that the close preserves the
ledger skips itself out on a closed repository"* -- guarded on the live ledger
existing at the old path. Repointing that guard is not enough, and the epic
baseline's expectation that these simply "unskip when `SS-01` repoints" does not
hold: the subject was the LIVE spec tree, and a live spec tree is only closeable
in the minutes between an epic's last ticket closing and its successor being
scaffolded. Run against this epic's tree the close refuses with
*"ticket SS-01 is not closed: status=planned"*, eight times over. **A test whose
subject is the live workflow can only pass while no workflow is open.**

**SO THE SUBJECT IS THE SEALED SNAPSHOT, WHICH IS STILL THIS REPOSITORY AND
STILL NOT A FIXTURE.** Every test copies
`specs/.history/cut-the-apparatus-epic/closed-snapshot/snapshots/{current,
desired_program_model,program_model}` -- the real tree that epic actually closed,
with its tickets really closed -- plus the real receipts and the real
`specs/results/*` inputs, moves the ledger to its post-`SS-01` address, and runs
the real `close_tickets.close_ticket_workflow` over them. A hand-built two-file
spec tree would not have reproduced any of the defects here: they are about what
the shipped close does to the cumulative ledger this project actually carries.

WHAT WAS MEASURED BEFORE THE FIX (a real close, run and observed, not read off
the source):

  - The close DOES archive the ledger. `snapshot_models` copies all three model
    directories into `<entry>/snapshots/`, `copy_ignore` does NOT filter
    `deferred_findings.yaml` (it is not in `IGNORED_COPY_NAMES`), and the file
    landed complete -- all 267 rows -- at
    `closed-snapshot/snapshots/desired_program_model/deferred_findings.yaml`.
    The reports that the archive step was missing, and that `copy_ignore` was
    eating the file, were both WRONG.

  - The five closed-snapshots already in `specs/.history` lack the ledger
    because they PREDATE it living at that path, not because a close dropped it.
    The current ledger file was added at `e6d1351` (2026-08-05 13:25); the
    newest of the five, `hexagonal-prompting-epic`, was written 2026-08-05
    11:29.

  - What was actually broken is the READ. `scripts/disposition.py` addresses the
    ledger only at its live path, the close removes the directory containing it,
    and so `disposition.py --epic cut-the-apparatus` died with a bare
    `FileNotFoundError` traceback the moment the epic it reports on was closed.
    The record survived; nothing could reach it.

So `CA-09`'s fix was a FALLBACK, and `SS-01`'s is the ADDRESS the fallback was
standing in for. The close still removes `desired_program_model/`; the ledger is
no longer in it.

**ONE THING THAT WENT WITH THE MOVE, AND IT IS FILED RATHER THAN FIXED HERE.**
`spec_evolution.snapshot_findings_ledger` still SOURCES its archive from
`desired_program_model/deferred_findings.yaml`, so from here on every close
records `findings_ledger: {exists: false}` and archives nothing. Nothing breaks
-- the ledger it would have archived is the one that no longer needs archiving
-- but a record stops being written, silently. `SS-01-DF-01`, carried to
`SS-07`; `scripts/spec_evolution.py` is outside `SS-01`'s conflict keys. These
tests therefore assert the SURVIVAL of the ledger and deliberately assert
nothing about the manifest record, rather than pinning the degraded state as
correct.

The third test covers `SF-305` in `scripts/complexity_ledger.py`: a substring
test for the template sentinel over free prose, which blanked any narrative
merely QUOTING the word `TODO` and then refused the close for a narrative that
was `absent`.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.close_tickets import close_ticket_workflow  # noqa: E402

WORKFLOW = "cut-the-apparatus-epic"
EPIC = "cut-the-apparatus"
LEDGER_NAME = "deferred_findings.yaml"
#: The address after `SS-01`: `specs/`, not `specs/desired_program_model/`.
LIVE_LEDGER = Path("specs") / LEDGER_NAME
#: Where the sealed subject still carries it, and where the subject builder
#: moves it from. A tree that has not migrated yet is exactly this shape.
LEGACY_LEDGER = Path("specs") / "desired_program_model" / LEDGER_NAME
#: The real tree `cut-the-apparatus-epic` closed, tickets closed and all.
SEALED = REPO / "specs" / ".history" / WORKFLOW / "closed-snapshot" / "snapshots"
DISPOSITION = REPO / "scripts" / "disposition.py"

#: `ticket-<index>-<TICKET-ID>[-<qualifier>]`.
#:
#: The epic history carries TWO successful receipts for CA-05 --
#: `ticket-004-CA-05` and, appended later, `ticket-004-CA-05-reconciled`, the
#: close retaken at the epic tip once CA-05's promotion predecessor had merged.
#: The workflow close refuses a ticket with two successful receipts, so the
#: subject keeps the LAST receipt per ticket id: the reconciled one, which is
#: the authoritative close. (Verified by running the close both ways -- either
#: single receipt satisfies it.) That duplicate is a pre-existing condition of
#: this record, is a genuine blocker for closing this epic for real, and is not
#: what these tests are about.
RECEIPT = re.compile(r"^ticket-\d+-([A-Za-z]+-\d+)(?:-.+)?$")


def _findings(path: Path) -> list[dict]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))["findings"]


def build_subject(dest: Path) -> Path:
    """Copy the real spec workflow `cut-the-apparatus-epic` closed into `dest`.

    Read from the sealed snapshot rather than from `specs/` (see the module
    docstring): the live tree carries whichever workflow is OPEN, and an open
    workflow refuses its own close. Nothing here writes to `specs/.history`;
    `R-H4` is a rule about editing the record, not about reading it.
    """
    history = REPO / "specs" / ".history" / WORKFLOW
    assert SEALED.is_dir() and history.is_dir(), (
        f"the sealed subject is gone: {SEALED} or {history}. These tests have no "
        f"fixture to fall back on, by design."
    )

    (dest / "specs" / ".history" / WORKFLOW).mkdir(parents=True)
    (dest / "specs" / "results").mkdir(parents=True)
    for name in ("current", "desired_program_model", "program_model"):
        shutil.copytree(SEALED / name, dest / "specs" / name)
    # The migration `SS-01` performed, applied to the subject: the ledger leaves
    # the directory the close removes. The sealed snapshot predates it.
    legacy = dest / LEGACY_LEDGER
    assert legacy.is_file(), f"the sealed subject carries no ledger at {LEGACY_LEDGER}"
    shutil.move(str(legacy), dest / LIVE_LEDGER)
    receipts: dict[str, Path] = {}
    for entry in sorted(history.iterdir()):
        if entry.is_dir() and (match := RECEIPT.match(entry.name)):
            receipts[match.group(1)] = entry  # sorted, so the last receipt wins
    for entry in receipts.values():
        shutil.copytree(entry, dest / "specs" / ".history" / WORKFLOW / entry.name)
    for result in sorted((REPO / "specs" / "results").iterdir()):
        if result.is_file():  # the close reads the ledger inputs; the raw sweep
            shutil.copy2(result, dest / "specs" / "results" / result.name)  # dirs are megabytes
    return dest


def close(root: Path) -> None:
    close_ticket_workflow(root, Path("specs"), dry_run=False, summary="R1 close over the real workflow")


def entry_dir(root: Path) -> Path:
    return root / "specs" / ".history" / WORKFLOW / "closed-snapshot"


def run_disposition(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(DISPOSITION), "--epic", EPIC],
        cwd=root, capture_output=True, text=True,
    )


def test_the_close_does_not_remove_the_cumulative_ledger(tmp_path: Path) -> None:
    """`SS-01`. The strong form: nothing is lost, so nothing has to be recovered.

    The close is unchanged and still takes `desired_program_model/` with it. The
    ledger is simply not in there any more, which is the whole repair -- it lived
    inside a workflow directory by accident of scaffolding, and it is a
    cumulative CROSS-EPIC record that belongs to no single workflow
    (`CA-10-DF-10`).
    """
    root = build_subject(tmp_path / "subject")
    before = _findings(root / LIVE_LEDGER)
    # Not a per-epic backlog: one file, every epic's findings. Losing it is not
    # losing an epic's notes, it is losing the project's whole findings record.
    assert len({str(row["id"]).split("-")[0] for row in before}) > 1

    close(root)

    # The workflow directories are REMOVED, as the close intends. No exemption
    # was carved for the ledger; it was moved out of their way.
    assert not (root / "specs" / "desired_program_model").exists()
    assert not (root / "specs" / "current").exists()

    survivor = root / LIVE_LEDGER
    assert survivor.is_file(), (
        f"the close took {LIVE_LEDGER} with it; present under specs/: "
        f"{sorted(p.name for p in (root / 'specs').iterdir())}"
    )
    assert _findings(survivor) == before
    assert survivor.read_bytes() == (REPO / "specs" / ".history" / WORKFLOW
                                     / "closed-snapshot" / "snapshots"
                                     / "desired_program_model" / LEDGER_NAME).read_bytes()


def test_disposition_answers_the_same_way_after_the_workflow_it_reports_on_is_closed(
    tmp_path: Path,
) -> None:
    """The property `CA-09` bought with a fallback, now held by the address.

    Note what is asserted about stderr and why it is the OPPOSITE of what this
    test used to assert: it used to require the words "archived ledger", proving
    the fallback had fired. Now their ABSENCE is the proof -- the live ledger was
    still there to read, so no archive was consulted at all. The fallback itself
    is exercised in `tests/test_ledger_resolution_is_deterministic.py`.
    """
    root = build_subject(tmp_path / "subject")
    before = run_disposition(root)
    assert before.returncode in {0, 1}, before.stderr

    close(root)

    after = run_disposition(root)
    assert "FileNotFoundError" not in after.stderr, after.stderr
    assert after.returncode == before.returncode
    assert after.stdout == before.stdout
    assert "archived ledger" not in after.stderr, (
        "the live ledger survived the close, so nothing should have fallen back "
        "to an archive:\n" + after.stderr
    )


def test_a_narrative_that_quotes_the_template_sentinel_is_not_blanked(tmp_path: Path) -> None:
    """SF-305. Worst exactly where the ledger is most useful: writing about itself."""
    root = build_subject(tmp_path / "subject")
    ledger_input = root / "specs" / "results" / "complexity_ledger_input.yaml"
    document = yaml.safe_load(ledger_input.read_text(encoding="utf-8"))
    narrative = (
        "The scaffolded ledger template ships narrative: \"TODO\", and until SF-305 was "
        "fixed this very sentence could not be recorded: a substring test blanked any "
        "narrative quoting that word, and Gate 7 then refused the close as though no "
        "narrative had been written at all."
    )
    document["narrative"] = narrative
    ledger_input.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")

    close(root)  # before the fix: SystemExit, "REJECTED -- no `narrative:` recorded"

    written = json.loads((root / "specs" / "results" / "complexity_ledger.json").read_text(encoding="utf-8"))
    assert written["entries"][-1]["narrative"] == narrative


def test_an_unfilled_template_narrative_still_refuses_the_close(tmp_path: Path) -> None:
    """The property the substring test was protecting, kept under equality."""
    root = build_subject(tmp_path / "subject")
    ledger_input = root / "specs" / "results" / "complexity_ledger_input.yaml"
    document = yaml.safe_load(ledger_input.read_text(encoding="utf-8"))
    document["narrative"] = "TODO"
    ledger_input.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")

    with pytest.raises(SystemExit) as refusal:
        close(root)
    assert "narrative" in str(refusal.value)
