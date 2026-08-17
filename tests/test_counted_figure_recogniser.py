"""SS-04 — the prose counted-figure recogniser, and the three things it may not do.

`GOAL-counted-figures-reach-the-record` has four clauses this file decides
mechanically, so that a reader does not have to take the write-up's word for any
of them:

  (a) it REACHES counted figures written as ordinary `<n> of <m>` prose;
  (b) UNREACHABLE IS THE DEFAULT — never HOLDS and never REFUTED from FORM P;
  (c) IT IS NOT A GATE — no exit code changes for an input that resolves, and
      no figure that had a verdict before FORM P existed has a different one;
  (d) `MF-020` — the recogniser is not fitted to the five figures the issue
      names, and three of those five DO NOT PARSE. That is asserted here rather
      than promised in prose, because a promise not to fit is worth nothing and
      a test that the fitted cases FAIL is worth something.

Plus `SS-02`'s absent-input extension, on `scope`'s own three states, and the two
findings routed to this ticket: `SS-01-DF-03` (the tree a figure was measured in
is recorded) and `SS-00-DF-04` (the joint distribution is computed, never
inferred from two marginals).
"""
from __future__ import annotations

import importlib.util
import pathlib
import shutil
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
TOOL = REPO / "examples/validation/scorecards/score_tools.py"


def _module():
    spec = importlib.util.spec_from_file_location("ss04_score_tools", TOOL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("ss04_score_tools", mod)
    spec.loader.exec_module(mod)
    return mod


st = _module()


def claims(text: str, tmp_path: pathlib.Path, name: str = "doc.md") -> list[dict]:
    p = tmp_path / name
    p.write_text(text)
    return st.find_claims(p, tmp_path)


def prose(text: str, tmp_path: pathlib.Path) -> list[dict]:
    return [c for c in claims(text, tmp_path) if c["form"] == "P"]


# --------------------------------------------------------------------------
# (a) it reaches ordinary prose
# --------------------------------------------------------------------------

@pytest.mark.parametrize("sentence,n,m", [
    ("the kill probe caught 0 of 9 content bugs", 0, 9),
    ("consumption ran at 1 of 38 findings", 1, 38),
    ("three of the four cut targets did not exist", 3, 4),
    ("8 out of 9 rounds were re-run", 8, 9),
    ("it moved 1,490 of 1,558 nodes", 1490, 1558),
    ("seventeen of twenty judged goals", 17, 20),
    ("**39 of 49** rows are undisposed", 39, 49),
    ("`0 of 20` judged goals have an openable baseline", 0, 20),
])
def test_ordinary_prose_is_reached(sentence, n, m, tmp_path):
    """Clause (a). None of these carries a dimension token, so `scope` as it
    shipped reads ZERO counted figures in every one of them."""
    got = prose(sentence, tmp_path)
    assert [(c["n"], c["m"]) for c in got] == [(n, m)], got


def test_two_figures_on_one_line_are_both_reached(tmp_path):
    """The greedy-noun bug, pinned. Captured normally the noun ate `and two of`
    and `finditer` never tried the second figure — four whole-record misses."""
    got = prose("arm B's 44 of 105, and two of those four are paths", tmp_path)
    assert [(c["n"], c["m"]) for c in got] == [(44, 105), (2, 4)], got


def test_the_charters_are_reached(tmp_path):
    """Clause (a)'s named list, on the two documents the issue names. `scope`
    reads 0 counted figures on BOTH at the epic base; the numbers below are the
    tip's, and a regression to zero is what this catches."""
    for doc in ("STABILIZE-SUBSTRATE-EPIC.md", "CUT-THE-APPARATUS-EPIC.md"):
        found = st.find_claims(REPO / doc, REPO)
        assert found, f"{doc} reads zero counted figures — the CA-08-DF-01 state"
        assert all(c["form"] == "P" for c in found), (
            f"{doc} has no dimension-bound figure in it; every figure reached "
            f"there is FORM P's, which is the whole point")


# --------------------------------------------------------------------------
# (b) UNREACHABLE is the default, and (c) it cannot gate
# --------------------------------------------------------------------------

def test_form_p_never_refutes_and_never_holds_over_the_whole_record():
    """The strongest form of clause (b) available: not "we were careful", but
    "the verdict set is closed and here it is over 2,800 real figures".

    A FALSE REFUTED IS WORSE THAN AN UNREACHABLE. FORM P carries no value bound
    to it, so it has nothing to refute; and it never confirms either, because a
    denominator that re-derives is only half of a claim.
    """
    run = st.run_scope_full(REPO, REPO / "specs/results/scorecards")
    p = [r for r in run["figures"] if r.get("form") == "P"]
    assert p, "FORM P found nothing over the record — the recogniser is dead"
    bad = sorted({r["verdict"] for r in p} - set(st.PROSE_VERDICTS))
    assert not bad, f"FORM P produced {bad}; its verdicts are {st.PROSE_VERDICTS}"


def test_a_card_noun_whose_denominator_re_derives_is_unreachable_not_holds(tmp_path):
    """HALF-CHECKED IS NOT HOLDS, and this is the case that makes the point."""
    cards = [{"example": "e", "dimensions": {}, "status": "filled"}] * 3
    c = prose("the finding is visible on 2 of 3 cards", tmp_path)[0]
    got = st.evaluate_claim(c, cards, {"e"})
    assert got["verdict"] == st.UNREACHABLE
    assert got["reason"] == "numerator has no predicate"


def test_a_card_noun_whose_denominator_moved_is_count_moved(tmp_path):
    cards = [{"example": "e", "dimensions": {}, "status": "filled"}] * 5
    c = prose("visible on 2 of 3 cards", tmp_path)[0]
    got = st.evaluate_claim(c, cards, {"e"})
    assert got["verdict"] == st.COUNT_MOVED
    assert got["hits"] is None, "the numerator is not checked and must not read as if it were"


def test_row_and_judge_nouns_are_refused_by_form_p(tmp_path):
    """MEASURED, NOT ASSUMED: the first whole-record run returned 88 COUNT-MOVED
    and 42 of them counted LEDGER ROWS -- `39 of 49 rows` answered with "the
    population is 95 rather than 49". A category error in the voice of a
    re-derivation is exactly the false confidence this instrument exists against.
    """
    cards = [{"example": "e", "dimensions": {}, "status": "filled"}] * 95
    for sentence in ("39 of 49 rows are undisposed",
                     "three of the four judges cited it"):
        c = prose(sentence, tmp_path)[0]
        got = st.evaluate_claim(c, cards, {"e"})
        assert got["verdict"] == st.UNREACHABLE, (sentence, got["verdict"])
        assert got["reason"] == "non-card noun"


def test_the_exit_code_is_unchanged_for_an_input_that_resolves():
    """Clause (c). `scope` exits 1 iff something is REFUTED; FORM P cannot
    produce a REFUTED; therefore nothing anyone runs changes its answer."""
    r = subprocess.run([sys.executable, str(TOOL), "scope", "--form", "bound"],
                       capture_output=True, text=True, cwd=REPO)
    full = subprocess.run([sys.executable, str(TOOL), "scope"],
                          capture_output=True, text=True, cwd=REPO)
    assert r.returncode == full.returncode, (
        "adding FORM P moved the process exit code, which makes it a gate")


def test_no_bound_figure_changed_its_verdict():
    """Clause (c)'s other half, and the one a reviewer should care about most:
    FORM P is ADDITIVE. Every figure that had a verdict before still has the
    same one, in the same place."""
    run = st.run_scope_full(REPO, REPO / "specs/results/scorecards")
    bound = [r for r in run["figures"] if r.get("form") != "P"]
    counts = {v: sum(1 for r in bound if r["verdict"] == v)
              for v in (st.REFUTED, st.COUNT_MOVED, st.HOLDS, st.UNREACHABLE)}
    assert sum(counts.values()) == len(bound)
    # ALL FOUR ASSERTED, AND THE POPULATION TOO. The first version of this test
    # COMPUTED `counts` and then asserted only two of the four, so `REFUTED
    # 81 -> 80` would have passed the test whose entire purpose is that no bound
    # verdict moved — the check for the class not checking. Reviewer, PR #285.
    assert len(bound) == 103, len(bound)
    assert counts[st.REFUTED] == 81, counts
    assert counts[st.COUNT_MOVED] == 0, counts
    assert counts[st.HOLDS] == 2, counts
    assert counts[st.UNREACHABLE] == 20, counts


# --------------------------------------------------------------------------
# (d) MF-020 — the DECLARED misses must still miss
# --------------------------------------------------------------------------

@pytest.mark.parametrize("sentence", [
    "seven epics, zero bugs",
    "8 failed, 1490 passed",
    "four rounds' claims went unchecked",
    "the suite is 17 / 1483 / 4 at collection 1504",
    "1 in 38 findings were consumed",
    "thirty-one of forty rows",
])
def test_the_declared_misses_still_miss(sentence, tmp_path):
    """`MF-020`, ASSERTED IN THE DIRECTION THAT COSTS SOMETHING.

    Three of the five figures the issue names are in this list. They were
    written into `PROSE-FORM-SPEC.md` S5 as declared misses BEFORE the
    recogniser existed, and a later hand that widens FORM P to catch one of them
    — because it is on a list of figures whose answers are known — fails here.
    That is the only mechanical protection against fitting that this ticket can
    ship: make the fit break a test.
    """
    assert prose(sentence, tmp_path) == []


def test_the_distributive_numerator_is_refused(tmp_path):
    """`every one of the 10 was inspected` is 10 of 10, not 1 of 10. Found by a
    hand audit of 40 sampled matches, not by looking for it."""
    assert prose("every one of the 10 was inspected", tmp_path) == []
    assert prose("one of the 10 was inspected", tmp_path) != []


# --------------------------------------------------------------------------
# SS-02's absent-input extension, on this instrument's own input
# --------------------------------------------------------------------------

def _scope(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(TOOL), "scope", *args],
                          capture_output=True, text=True, cwd=REPO)


def test_absent_document_is_undecided(tmp_path):
    r = _scope("--path", str(tmp_path / "nope.md"))
    assert r.returncode == st.SCOPE_UNDECIDED
    assert r.stdout.startswith("UNDECIDED: [absent]"), r.stdout[:200]


def test_empty_document_is_undecided_not_no_figures_all_clear(tmp_path):
    """The exact shape `SS-02` wrote the rule against. A zero-byte charter and a
    charter with no figures in it are different facts and the second is a real
    answer."""
    doc = tmp_path / "empty.md"
    doc.write_bytes(b"")
    r = _scope("--path", str(doc))
    assert r.returncode == st.SCOPE_UNDECIDED
    assert r.stdout.startswith("UNDECIDED: [empty]"), r.stdout[:200]
    assert "0 counted figure(s)" not in r.stdout


def test_whitespace_only_document_is_undecided(tmp_path):
    doc = tmp_path / "ws.md"
    doc.write_text("   \n\n\t\n")
    r = _scope("--path", str(doc))
    assert r.returncode == st.SCOPE_UNDECIDED
    assert r.stdout.startswith("UNDECIDED: [empty]"), r.stdout[:200]


def test_unreadable_document_is_undecided_and_is_not_the_empty_answer(tmp_path):
    """`SS-01-DF-04`: a fallback that answers an unparseable input with the empty
    input's verdict has moved the false PASS, not removed it."""
    doc = tmp_path / "bin.md"
    doc.write_bytes(b"\x00\xff\xfe\x80")
    r = _scope("--path", str(doc))
    assert r.returncode == st.SCOPE_UNDECIDED
    assert r.stdout.startswith("UNDECIDED: [unreadable]"), r.stdout[:200]


def test_a_figure_free_document_is_the_one_zero_that_is_a_real_answer(tmp_path):
    """The fourth input, and the control for the three above: it READS, it is
    non-empty, and it genuinely counts nothing. That is `checked, none found`,
    it exits 0, and it says which of the two it is."""
    doc = tmp_path / "prose.md"
    doc.write_text("This document counts nothing at all. It is prose about prose.\n")
    r = _scope("--path", str(doc))
    assert r.returncode == 0
    assert "0 counted figure(s)" in r.stdout
    assert "CHECKED, NONE FOUND" in r.stdout


def test_absent_scorecard_corpus_is_undecided():
    """`scope --scorecards /nonexistent` printed `0 REFUTED, 82 UNREACHABLE` and
    EXITED 0 at the epic base. One of CA-10's 48, inside `scope` itself."""
    r = _scope("--scorecards", "/nonexistent-corpus", "--path",
               str(REPO / "CUT-THE-APPARATUS-EPIC.md"))
    assert r.returncode == st.SCOPE_UNDECIDED
    assert r.stdout.startswith("UNDECIDED: [absent]"), r.stdout[:200]


def test_empty_scorecard_corpus_is_undecided(tmp_path):
    r = _scope("--scorecards", str(tmp_path), "--path",
               str(REPO / "CUT-THE-APPARATUS-EPIC.md"))
    assert r.returncode == st.SCOPE_UNDECIDED
    assert r.stdout.startswith("UNDECIDED: [empty]"), r.stdout[:200]


def test_an_empty_sweep_is_undecided_not_a_satisfied_population(tmp_path):
    """CA-10's seventh sub-shape: an empty selection reported as a satisfied
    population. `0 counted figures, 0 REFUTED` over zero files is that."""
    r = _scope("--root", str(tmp_path))
    assert r.returncode == st.SCOPE_UNDECIDED
    assert r.stdout.startswith("UNDECIDED: [empty]"), r.stdout[:200]


def test_the_three_states_are_distinguishable_by_execution():
    """`SS-02` checks distinguishability BY EXECUTION rather than by reading the
    contract, because an instrument that CLAIMS three behaviours and delivers one
    is the class one layer up. These three carry three different state tokens."""
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        base = pathlib.Path(d)
        (base / "empty.md").write_bytes(b"")
        (base / "bin.md").write_bytes(b"\xff\xfe")
        outs = {}
        for name, arg in (("absent", base / "nope.md"),
                          ("empty", base / "empty.md"),
                          ("unreadable", base / "bin.md")):
            outs[name] = _scope("--path", str(arg)).stdout.splitlines()[0]
    assert len(set(outs.values())) == 3, outs
    for name, line in outs.items():
        assert line.startswith(f"UNDECIDED: [{name}]"), (name, line)


# --------------------------------------------------------------------------
# SS-01-DF-03 and SS-00-DF-04, consumed into what the instrument computes
# --------------------------------------------------------------------------

def test_the_output_records_the_tree_it_was_swept_in(tmp_path):
    """`SS-01-DF-03`. The same ledger bytes score 21/18/3 under a bare `--root`
    and 20/17/3 inside the repository, and until this existed `scope`'s output
    said NOTHING about which root produced a figure."""
    r = _scope("--path", str(REPO / "CUT-THE-APPARATUS-EPIC.md"))
    assert "## The tree this was swept in" in r.stdout
    assert str(REPO.resolve()) in r.stdout
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    assert head and head in r.stdout, "the HEAD a figure was measured at is not on the page"


def test_a_constructed_root_is_distinguishable_from_the_repository(tmp_path):
    """The half that actually stops the error: a `--root` figure must not look
    like a repository figure."""
    (tmp_path / "doc.md").write_text("0 of 9 content bugs\n")
    r = _scope("--root", str(tmp_path))
    assert r.returncode == 0
    assert "NOT A GIT CHECKOUT" in r.stdout, r.stdout[:400]


def test_the_joint_distribution_is_computed_not_inferred():
    """`SS-00-DF-04`. The owner published *"20 REFUTED, all from the ledger"* by
    reading two MARGINAL totals and assuming they cross-tabulated. They do not.
    The joint distribution is now on the page, per file and per verdict, so the
    sentence that produced that error cannot be written from this output."""
    run = st.run_scope_full(REPO, REPO / "specs/results/scorecards")
    order = (st.REFUTED, st.COUNT_MOVED, st.HOLDS, st.UNREACHABLE)
    assert run["cross_tab"], "no cross-tabulation was computed"
    for verdict in order:
        joint = sum(row[verdict] for row in run["cross_tab"])
        marginal = sum(1 for r in run["figures"] if r["verdict"] == verdict)
        assert joint == marginal, (verdict, joint, marginal)
    assert sum(row["total"] for row in run["cross_tab"]) == len(run["figures"])


def test_a_figure_naming_an_abolished_dimension_does_not_kill_the_command(tmp_path):
    """`SS-04-DF-05`. Card version 5 abolished D1, D4 and D5, and the
    counterexample printer used a SUBSCRIPT, so one refutable `D5 = …` sentence
    anywhere in the swept record raised `KeyError: 'D5'` and took every other
    figure's answer down with it — a traceback on exit 1, indistinguishable from
    the normal "something is REFUTED" exit 1 to anyone reading only the code.

    Found because a finding this ticket filed quoted such a figure into the
    ledger. The defect predates the ticket by five card versions.
    """
    (tmp_path / "doc.md").write_text("D" + "5 = 4 on 95 of 95 cards\n")
    r = _scope("--root", str(tmp_path))
    assert "Traceback" not in r.stdout + r.stderr, r.stderr[-400:]
    assert "1 counted figure(s): 1 REFUTED" in r.stdout, r.stdout[-400:]
    assert "ABSENT" in r.stdout, "the missing dimension is not named in the output"


# --------------------------------------------------------------------------
# The interpreter floor — SS-04-DF-04, made executable for the file that broke
# --------------------------------------------------------------------------

#: `score_tools.py` imports `tomllib`, so its floor is 3.11. `SS-04` shipped a
#: PEP 701 construct — an implicit string concatenation INSIDE an f-string
#: expression — which raised the floor to 3.12 silently, in the ticket that
#: filed the finding about interpreter floors, on the line that consumes
#: `SS-01-DF-03`. This is that finding as an EXECUTED check rather than prose.
INTERPRETER_FLOOR = (3, 11)


def test_the_tool_compiles_at_its_declared_interpreter_floor():
    """`SS-04-DF-04`, executed.

    THERE IS NO IN-PROCESS SUBSTITUTE FOR THIS, and I checked before writing it:
    `ast.parse(src, feature_version=(3, 11))` ACCEPTS the PEP 701 construct that
    breaks a real 3.11, because `feature_version` gates a handful of AST-level
    features and this is a TOKENIZER change. So the floor can only be checked by
    a floor interpreter, and where there is none this SKIPS WITH ITS REASON
    rather than passing — an absent interpreter is an absent input, and the
    correct answer to one is not PASS.
    """
    exe = shutil.which("python%d.%d" % INTERPRETER_FLOOR)
    if exe is None:
        pytest.skip(
            "no python%d.%d on PATH, so the declared floor cannot be checked "
            "here. NOT A PASS: `ast.parse(feature_version=...)` does not catch "
            "PEP 701 (verified), so there is no in-process substitute, and this "
            "repository declares no `requires-python` while `uv` runs 3.13 — "
            "which is exactly why SS-04 raised the floor without noticing."
            % INTERPRETER_FLOOR
        )
    done = subprocess.run([exe, "-m", "py_compile", str(TOOL)],
                          capture_output=True, text=True, cwd=REPO)
    assert done.returncode == 0, (
        f"{TOOL.name} does not compile under {exe}, the floor its own "
        f"`import tomllib` declares:\n{done.stderr}"
    )
