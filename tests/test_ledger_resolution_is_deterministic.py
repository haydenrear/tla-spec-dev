"""`SS-00-DF-01`: which archived ledger an instrument reads is a fact about the
TREE, never about the checkout.

THE FAILING INPUT, ON A REAL SUBJECT, MEASURED BEFORE THE REPAIR (R1). Two
independent fresh clones of `25600fa` both reported
`score_tools.py audit` -> **9 violation(s)**, every one of them
`filed_as = CL-03-DF-04 is not an id in deferred_findings.yaml`. `CL-03-DF-04`
is a real row: it is in `specs/deferred_findings.yaml` (299 rows) and in
`specs/.history/cut-the-apparatus-epic/closed-snapshot/deferred_findings.yaml`
(296 rows), which is the copy that close RECORDED in its own manifest under
`findings_ledger`. The instrument was reading neither. It was reading
`specs/.history/subtract-to-measure-epic/ticket-005-SM-05/snapshots/desired_program_model/deferred_findings.yaml`
-- 88 ids, four epics old, a MID-TICKET snapshot -- because the old resolution
globbed for the filename and ordered the 85 hits by `(st_mtime, st_size, path)`.

**AND ONE `touch` MOVED THE ANSWER.** In one of those clones, with not a byte of
the tree changed:

    $ python3 examples/validation/scorecards/score_tools.py audit   # 9 violation(s)
    $ touch specs/.history/cut-the-apparatus-epic/closed-snapshot/deferred_findings.yaml
    $ python3 examples/validation/scorecards/score_tools.py audit   # 0 violation(s)

That is the defect in one line: **a verdict about a repository's whole scorecard
record, decided by a filesystem timestamp git does not carry.**

**TWO CORRECTIONS TO THE FILED MECHANISM, re-derived rather than repeated.**
`SS-00-DF-01` and this epic's charter both say all 85 candidates share one mtime,
so the ordering "degenerates to SIZE" and "the largest file wins". Measured on a
fresh clone: the 85 candidates have **85 distinct mtimes** spanning 3.6 seconds
of checkout time, so size never breaks a tie -- **mtime alone decides**, and it
lands on whichever entry git wrote last (`specs/.history` is checked out in name
order, and `subtract-to-measure-epic` sorts last). And the largest candidate is
`cut-the-apparatus-epic/closed-snapshot/deferred_findings.yaml` at 1,152,237
bytes -- **the CORRECT one**. Had the ordering really degenerated to size the
instrument would have been right. The symptom in the finding is exact; its
stated cause is not, and the difference matters because "sort by size instead"
reads like a fix and is not one.

**THE REPAIR.** A workflow close writes the ledger at the top of its history
entry and records the address in that entry's `manifest.json` under
`findings_ledger`, beside `created_at_utc`. Both facts are IN THE TREE and
identical in every checkout. So resolution reads the manifests, and a copy no
manifest points at is not a candidate at all: it cannot be identified as the
ledger any close archived, and guessing at one is what produced the wrong answer.
Where no close recorded one, the answer is **UNVERIFIED** -- not a confident
audit against whichever file happened to be biggest, or newest.

Both instruments carry their own copy of this resolution, deliberately:
`score_tools.py` ships standalone (`RM-05` section 3) and refuses to hard-require
`scripts/`. The two are pinned to the same answer here.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts import disposition as D  # noqa: E402

SCORE_TOOLS = REPO / "examples/validation/scorecards/score_tools.py"
LIVE = REPO / D.LEDGER
#: The one archive a close in this repository has ever recorded.
RECORDED = Path("specs/.history/cut-the-apparatus-epic/closed-snapshot/deferred_findings.yaml")
#: The one the old `(mtime, size, path)` ordering picked on a fresh checkout.
DECOY = Path("specs/.history/subtract-to-measure-epic/ticket-005-SM-05"
             "/snapshots/desired_program_model/deferred_findings.yaml")


def _score_tools():
    spec = importlib.util.spec_from_file_location("_st_ledger", SCORE_TOOLS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _archive_tree(dest: Path, *, keep_manifest: bool = True) -> Path:
    """The real `specs/.history` archives, no live ledger, in a throwaway root."""
    for rel in (RECORDED, DECOY):
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, target)
    manifest_src = REPO / RECORDED.parent / "manifest.json"
    if keep_manifest:
        shutil.copy2(manifest_src, dest / RECORDED.parent / "manifest.json")
    return dest


def _ids(path: Path) -> set[str]:
    import re

    return set(re.findall(r"^\s*-\s+id:\s*\"?([A-Za-z0-9_.-]+)\"?",
                          path.read_text(encoding="utf-8"), re.M))


def test_the_live_ledger_is_at_a_path_the_close_does_not_remove():
    """The address, which is what makes every fallback below the rare case.

    `scripts/close_tickets.py` removes `specs/desired_program_model/` at workflow
    close. The ledger used to live inside it, which is why `CA-09` needed a read
    fallback at all.
    """
    assert D.LEDGER == "specs/deferred_findings.yaml"
    assert not D.LEDGER.startswith("specs/desired_program_model/")
    assert LIVE.exists()
    assert _score_tools().LEDGER_LIVE == D.LEDGER


def test_the_two_instruments_resolve_to_the_same_ledger():
    """One address, two readers. They disagreed for a whole epic and nothing said so."""
    assert D.resolve_ledger(LIVE, explicit=False).resolve() == _score_tools()._ledger_path().resolve()


def test_a_touch_no_longer_moves_the_answer(tmp_path):
    """THE FAILING INPUT. Same bytes, different timestamps, one answer.

    Before the repair this loop returned the DECOY for every ordering in which
    the decoy was newest, and the RECORDED copy otherwise -- 88 ids or 296 ids
    from one tree.
    """
    root = _archive_tree(tmp_path / "tree")
    old, new = 1_000_000_000, 2_000_000_000
    answers = set()
    for recorded_first in (True, False):
        os.utime(root / RECORDED, (old, old) if recorded_first else (new, new))
        os.utime(root / DECOY, (new, new) if recorded_first else (old, old))
        answers.add(D.archived_ledgers(root)[-1].resolve())
    assert answers == {(root / RECORDED).resolve()}, (
        "archive resolution still moves with filesystem mtimes; git does not "
        "carry mtimes, so this is a verdict about the checkout (SS-00-DF-01)"
    )


def test_the_decoy_is_a_real_decoy_and_the_recorded_copy_is_the_real_ledger():
    """R2: the test above proves nothing if the two files were the same file.

    The decoy is what the old ordering actually chose on a fresh clone, and it
    genuinely lacks the id the nine violations named.
    """
    recorded, decoy = _ids(REPO / RECORDED), _ids(REPO / DECOY)
    assert len(decoy) == 88 and len(recorded) == 296
    assert "CL-03-DF-04" not in decoy
    assert "CL-03-DF-04" in recorded
    assert "CL-03-DF-04" in _ids(LIVE)


def test_an_unrecorded_archive_is_not_a_candidate(tmp_path, capsys):
    """THE ABSENT-INPUT CASE. No close recorded a ledger -> UNVERIFIED, not a guess.

    `GOAL-absent-input-consumed`: the correct answer to an input the instrument
    cannot identify is a refusal, never a confident verdict. Here the decoy is
    present, is the only ledger-shaped file in the tree, and is still not an
    answer -- because nothing in the tree says it is the ledger any close kept.
    """
    root = _archive_tree(tmp_path / "tree", keep_manifest=False)
    assert D.archived_ledgers(root) == []

    module = _score_tools()
    module.REPO_ROOT = root
    assert module._ledger_path() is None
    assert module._finding_ids() is None

    # `root=` is load-bearing and was not there before this ticket: the archive
    # search ran against the process's working directory whatever ledger it was
    # asked about, so this assertion was answered from THIS repository's archives
    # rather than from the tree under test. Found by this test failing.
    with pytest.raises(SystemExit) as refusal:
        D.resolve_ledger(root / "specs" / "deferred_findings.yaml", explicit=False, root=root)
    # EXIT 2, and the word on stderr. `SS-01-DF-05`: exit 1 is the CLAUSE verdict
    # `REFUSED <scope>: N of M findings undisposed`, so a caller that checks the
    # code rather than the output cannot otherwise tell "undisposed" from "no
    # ledger could be identified at all".
    assert refusal.value.code == 2
    assert "UNVERIFIED" in capsys.readouterr().err


def test_audit_says_unchecked_rather_than_fabricated_when_it_has_no_ledger(tmp_path):
    """`CA-10-DF-11`'s property, kept: unchecked is not fabricated.

    The old failure reported every `filed_as` in the record as a dangling
    citation. The repaired failure mode is one UNVERIFIED line and no
    VIOLATIONs.
    """
    module = _score_tools()
    module.REPO_ROOT = _archive_tree(tmp_path / "tree", keep_manifest=False)
    ctx = {"changes": [], "claims": [{"id": "c", "status": "sealed",
                                      "filed_as": "NOT-A-REAL-ID"}]}
    out = module.audit_rh3(ctx)
    assert [level for level, _ in out].count(module.UNVERIFIED) == 1
    assert module.VIOLATION not in [level for level, _ in out]


def test_the_recorded_archive_is_not_promised_to_be_frozen():
    """`CA-10-DF-10`, DECIDED AND DEMONSTRATED, not asserted.

    `resolve_ledger` used to promise the archived copy was "FROZEN at that
    close". It was not, on this repository's own record: the close wrote 278
    rows into `closed-snapshot/snapshots/desired_program_model/`, and the copy
    at the top of the same entry -- the one the manifest points at -- carries
    296. Eighteen rows were appended to an "archived" file after its close,
    because the close had left no writable ledger anywhere else.

    SS-01 fixes the CAUSE (the live ledger now survives a close, so nobody has
    reason to write into an archive) and DROPS THE CLAIM rather than restating
    it: this resolution promises the copy the close RECORDED, which is a
    property of the tree, and promises nothing about what happened to it since.
    """
    at_close = _ids(REPO / RECORDED.parent / "snapshots/desired_program_model/deferred_findings.yaml")
    recorded = _ids(REPO / RECORDED)
    assert len(at_close) == 278 and len(recorded) == 296
    assert at_close < recorded, "the archive is no longer a superset of its own close snapshot"

    source = (REPO / "scripts/disposition.py").read_text(encoding="utf-8")
    assert "FROZEN at that close" not in source, (
        "the freeze claim is back, and this repository's own archive falsifies it"
    )


def test_audit_reports_the_same_count_from_a_second_process_in_a_second_root(tmp_path):
    """Cheap standing pin. The real proof is two independent fresh worktrees.

    Recorded under `specs/results/scorecards/stabilize-substrate/SS-01/`. This
    keeps a cross-process check in the suite so a future change that reintroduces
    a filesystem-dependent order has somewhere to fail.
    """
    first = subprocess.run([sys.executable, str(SCORE_TOOLS), "audit"],
                           cwd=REPO, capture_output=True, text=True)
    copy = tmp_path / "root"
    copy.mkdir()
    for rel in ("specs", "examples", "references", "scripts"):
        shutil.copytree(REPO / rel, copy / rel, symlinks=True)
    second = subprocess.run([sys.executable, str(copy / "examples/validation/scorecards/score_tools.py"),
                             "audit"], cwd=copy, capture_output=True, text=True)
    tail = lambda text: [ln for ln in text.splitlines() if "violation(s)" in ln]
    assert tail(first.stdout) == tail(second.stdout), (first.stdout[-400:], second.stdout[-400:])


# -- the three findings an independent reviewer of PR #282 raised here --------


@pytest.mark.parametrize("label,body", [
    ("empty list", "findings: []\n"),
    ("zero bytes", ""),
    ("malformed", "findings:\n  - id: [unclosed\n"),
    ("no findings key", "notes:\n  - hello\n"),
])
def test_a_ledger_that_names_no_findings_is_not_an_answer(tmp_path, label, body):
    """`SS-01-DF-04`. THE THIRD STATE, and `SS-01` shipped without it.

    THE FAILING INPUT, MEASURED END-TO-END ON `587d46c` BEFORE THIS REPAIR:
    `findings: []` -> `_finding_ids()` returned an empty SET, R-H3 read that as
    "the ledger was read and lists nothing", and reported ALL 14 real `filed_as`
    citations as fabrications. Zero bytes and malformed YAML did the same.
    **14 violation(s) against a tree whose ledger was merely unreadable.**

    That is `CA-10-DF-11`'s exact failure moved one input over -- and this
    epic's `GOAL-absent-input-consumed` names that move as NOT a fix in its own
    words: "a fallback that merely moves the false PASS to a rarer input has NOT
    fixed the class." `CA-10-DF-11` repaired ABSENT, `SS-01` repaired WRONG, and
    EMPTY was still answering with full confidence.

    Found by an independent reviewer instructed to refute PR #282, not by this
    suite and not by the ticket that wrote the goal line.
    """
    root = tmp_path / "tree"
    (root / "specs").mkdir(parents=True)
    (root / "specs" / "deferred_findings.yaml").write_text(body, encoding="utf-8")

    module = _score_tools()
    module.REPO_ROOT = root

    assert module._ledger_path() is not None, "the file is there; resolution should find it"
    assert module._finding_ids() is None, (
        f"a ledger that is {label} yielded a confident empty set; every `filed_as` "
        f"citation in the record is then reported as a fabrication (SS-01-DF-04)"
    )

    ctx = {"changes": [], "claims": [{"id": "c", "status": "sealed",
                                      "filed_as": "CL-03-DF-04"}]}
    out = module.audit_rh3(ctx)
    levels = [level for level, _ in out]
    assert module.VIOLATION not in levels, (
        "R-H3 called a real filed finding a fabrication over an unreadable ledger"
    )
    assert levels.count(module.UNVERIFIED) == 1
    assert "names no findings" in " ".join(m for _, m in out), (
        "the UNVERIFIED line must say WHICH of the two states it hit -- an absent "
        "ledger and an empty one are different repairs"
    )


def test_two_recorded_archives_order_by_close_time_not_by_text(tmp_path):
    """`SS-01-DF-06`. The ordering that replaced mtime, exercised against a rival.

    EXACTLY ONE of this repository's 123 entry manifests records a
    `findings_ledger` today, so `sorted()` has never had to choose and a
    lexicographic compare on `created_at_utc` would have gone unnoticed
    indefinitely -- `SS-01-DF-01` keeps it at one candidate, because every close
    from here on records `exists: false`.

    The two stamps below are THE SAME INSTANT written two legal ways. As text
    `...Z` sorts BELOW `...+00:00`, so a string compare picks the older close.
    """
    root = tmp_path / "tree"
    same_instant = ("2026-08-05T11:29:00Z", "2026-08-05T11:29:00+00:00")
    later = "2026-08-12T09:00:00Z"

    def entry(name: str, stamp: str, rows: str) -> None:
        d = root / "specs" / ".history" / name / "closed-snapshot"
        d.mkdir(parents=True)
        (d / "deferred_findings.yaml").write_text(rows, encoding="utf-8")
        (d / "manifest.json").write_text(json.dumps({
            "created_at_utc": stamp,
            "findings_ledger": {
                "exists": True,
                "snapshot": f"specs/.history/{name}/closed-snapshot/deferred_findings.yaml",
            },
        }), encoding="utf-8")

    entry("older-epic", same_instant[1], "findings:\n  - id: OLD-01\n")
    entry("newer-epic", later, "findings:\n  - id: NEW-01\n")
    entry("tie-epic", same_instant[0], "findings:\n  - id: TIE-01\n")

    resolved = D.archived_ledgers(root)
    assert len(resolved) == 3
    assert resolved[-1].parent.parent.name == "newer-epic", (
        "the latest close did not win; ordering is not on the instant"
    )
    # The two equal instants must compare equal, whichever spelling they use.
    assert D._closed_at(same_instant[0]) == D._closed_at(same_instant[1])
    assert D._closed_at(later) > D._closed_at(same_instant[0])
    # A missing or malformed stamp is IGNORED, never a winner.
    assert D._closed_at(None) < D._closed_at(same_instant[0])
    assert D._closed_at("not a date") < D._closed_at(same_instant[0])

    # AND BOTH INSTRUMENTS, on the same three-way tree. The duplication is
    # deliberate (score_tools ships standalone, RM-05 section 3), so the pin has
    # to be exercised where they could actually diverge -- on THIS repository
    # they cannot, because only one manifest qualifies, which is precisely why
    # `test_the_two_instruments_resolve_to_the_same_ledger` could not see it.
    module = _score_tools()
    module.REPO_ROOT = root
    assert module._ledger_path() == resolved[-1], (
        "score_tools picked a different archive than disposition.py on a tree "
        "with more than one recorded close (SS-01-DF-06)"
    )
    assert module._closed_at(same_instant[0]) == module._closed_at(same_instant[1])
    assert module._closed_at(later) > module._closed_at(same_instant[0])


@pytest.mark.xfail(
    reason="SS-01-DF-01: spec_evolution.snapshot_findings_ledger still sources the "
           "archive from desired_program_model/, which SS-01 emptied, so every close "
           "from here records findings_ledger.exists=false and archives nothing. "
           "Outside SS-01's conflict keys; routed to the epic owner because no "
           "ticket on this epic carries scripts/spec_evolution.py. WHEN THIS GOES "
           "XPASS THE FINDING IS FIXED -- do not delete it, close the finding.",
    strict=True,
)
def test_the_close_still_archives_the_ledger_it_no_longer_deletes():
    """`SS-01-DF-01`, executable in BOTH directions.

    An independent reviewer of PR #282 observed that dropping the old
    `assert record["exists"] is True` left the finding untested either way:
    nothing failed while it was broken and nothing would flip when it was fixed.
    An xfail is the smallest thing that does both.
    """
    source = (REPO / "scripts" / "spec_evolution.py").read_text(encoding="utf-8")
    marker = 'source=specs_dir / "desired_program_model" / FINDINGS_LEDGER_NAME'
    assert marker not in " ".join(source.split()), (
        "the close still looks for the ledger inside the directory it removes"
    )
