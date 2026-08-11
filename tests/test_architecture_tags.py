"""RD-05. The `effect_boundary` axis, and the four ways it must not become a key.

`references/architecture_tags.md` is the design and RD-04's evidence directory is
the measurement. What is asserted here is the part a document cannot hold: that
the properties the design rests on are executed rather than promised.

  * an `INCOMPARABLE` pair PRINTS BOTH SCORE SETS -- the tag can only add a word
    beside two numbers, never remove one;
  * refusal authority is PER DIMENSION -- a separation demonstrated on D3 grants
    nothing on D1, D2, D4 or D5;
  * only the DERIVED value refuses, and every unresolved state FAILS OPEN;
  * a `does not separate` verdict carries the population's observed range and is
    marked NULL-ENTAILED where that range is a single point.

R1: the failing input is `toolchain_removal`'s four sealed cards, which are real
historical cards and not a fixture. Two of them cite predominantly outside the
scope they were attributed to, and that is the defect the axis exists to make
visible -- it is why D3 came out 2, 2, 3, 4 there.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TAGS = REPO_ROOT / "examples/validation/scorecards/architecture_tags.py"
TOOL = REPO_ROOT / "examples/validation/scorecards/score_tools.py"
SCORECARDS = REPO_ROOT / "specs/results/scorecards"

#: THE 49 CARDS SEALED BEFORE `reading-discipline` -- RD-04's population, and
#: the one every claim about the shipped `[[demonstration]]` row is measured
#: over. NAMED POSITIVELY AND ON PURPOSE.
#:
#: RM-04: this was `r["round"] != "reading-discipline"` in three places, which
#: is not a fixed population at all -- it is "everything that is not that one
#: round", so it GREW the moment any later round sealed a card, and RM-04's six
#: took it to 55. That is the identical open-population error RM-04 diagnosed in
#: the ledger row these very tests are about: a figure whose denominator moves
#: is a statement about how many cards happen to exist. Naming the rounds closes
#: it, and a round added later cannot silently join a sealed population.
SEALED_BEFORE_RD = frozenset({
    "architectural-coherence",
    "falsifiable-instruments-rescore-v1",
    "falsifiable-instruments-rescore-v2",
    "hexagonal-prompting",
    "hexagonal-prompting-rerun",
    "ports-as-adapters",
    "subtract-to-measure-sm04-rescore-v2",
    "subtract-to-measure-sm04-rescore-v3",
    "subtract-to-measure-sm05",
    "subtract-to-measure-sm05-greenfield",
})

TOOLCHAIN = "subtract-to-measure-sm05/toolchain_removal"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def at():
    return _load(TAGS, "architecture_tags_rd05")


@pytest.fixture(scope="module")
def st():
    return _load(TOOL, "score_tools_rd05")


@pytest.fixture(scope="module")
def world(at):
    subjects = at.load_subjects()
    derived = at.derive_subjects(subjects, REPO_ROOT)
    rows = at.card_rows(SCORECARDS)
    entries = at.demonstration_table(rows, derived, subjects)
    return {"subjects": subjects, "derived": derived, "rows": rows,
            "entries": entries, "table": at.authority(entries)}


# ---------------------------------------------------------------------------
# 1. the printing rule -- A6, the `EVAL-SUPPRESS` shape
# ---------------------------------------------------------------------------

def test_an_incomparable_pair_prints_both_score_sets(at, world) -> None:
    """THE INVARIANT THE WHOLE DESIGN RESTS ON, run end to end.

    `EVAL-SUPPRESS` is this repository's demonstration that a declared verdict
    will be used to erase a measured one: `verified: true, green: true, exit 0`
    over a demonstrated kill. The tag's version of that attack is to emit
    INCOMPARABLE and drop the row.

    So: run the comparison that IS refused, and assert that every score on both
    sides is still on the page -- compared against the cards themselves, not
    against a remembered list.
    """

    proc = subprocess.run(
        [sys.executable, str(TOOL), "tags", "--compare", "arm_b", "arm_a"],
        capture_output=True, text=True, cwd=str(REPO_ROOT))
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout

    d3 = [line for line in out.splitlines() if line.startswith("D3 ")
          or line.strip().startswith("arm_a [") or "INCOMPARABLE" in line]
    assert any("INCOMPARABLE" in line for line in d3), out

    # the D3 block, exactly as printed
    lines = out.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("D3 "))
    block = "\n".join(lines[start:start + 3])
    assert "INCOMPARABLE" in block

    def scores(subject: str, dim: str) -> list[int]:
        """Read straight off the cards on disk -- the tag machinery is what is
        under test, so the expected numbers may not come from it."""
        found = []
        for path in sorted(SCORECARDS.glob("*/*/*/scorecard.json")):
            card = json.loads(path.read_text())
            parts = path.relative_to(SCORECARDS).parts
            row = {"round": parts[0], "example": parts[1], "arm": card.get("arm"),
                   "declared_subject": (card.get("subject") or {}).get("name")}
            if at.subject_of(row, world["subjects"]) != subject:
                continue
            score = (card.get("dimensions") or {}).get(dim, {}).get("score")
            if isinstance(score, int):
                found.append(score)
        return sorted(found)

    for subject in ("arm_b", "arm_a"):
        printed = [line for line in block.splitlines() if subject in line]
        assert printed, f"{subject}'s scores are not on the INCOMPARABLE row: {block}"
        numbers = json.loads(printed[0][printed[0].index("["):])
        assert numbers == scores(subject, "D3"), (
            f"the INCOMPARABLE row for {subject} does not print every card's D3. "
            f"A tag may add a word beside two numbers; it may never remove one."
        )


def test_incomparable_absent_and_underivable_are_three_states(at, world) -> None:
    """A missing row and an incomparable one are not the same claim, and this
    repository has been caught conflating `absent` with `checked, none found`."""

    assert len({at.COMPARABLE, at.INCOMPARABLE, at.ABSENT}) == 3
    state, reason = at.verdict("D3", "ports-and-adapters", "effectful", world["table"])
    assert state == at.INCOMPARABLE
    assert "demonstrated on D3" in reason and "tiers measured" in reason


# ---------------------------------------------------------------------------
# 2. authority is per dimension -- A4
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("dim", ["D1", "D2", "D4", "D5"])
def test_the_tag_cannot_refuse_a_comparison_on_a_dimension_it_did_not_move(
        at, world, dim) -> None:
    """A tag that demonstrated nothing on D1 cannot excuse a D1 comparison.

    This is the design's answer to the trap. Over 34 cards D3 separates
    disjointly and these four overlap, so on them a "different architecture"
    objection is not available AT ALL -- not weighted, not discounted,
    unavailable.
    """

    state, reason = at.verdict(dim, "ports-and-adapters", "effectful", world["table"])
    assert state == at.COMPARABLE, (dim, reason)
    assert "demonstrated no separation" in reason


def test_authority_is_keyed_on_dimension_and_value_pair(at, world) -> None:
    """One row, and its key carries the dimension. Measured today."""

    keys = sorted((dim, sorted(pair)) for dim, pair in world["table"])
    assert keys == [("D3", ["effectful", "ports-and-adapters"])], keys


def test_the_one_row_carries_its_tier_limit(at, world) -> None:
    """RD-04 §9.1 IS CLOSED, AND THE CLAIM IS REWRITTEN RATHER THAN THE NUMBER
    RESTORED (`RM-06`, group 3).

    Through three tickets this asserted `tiers_measured == ["opus"]` and said in
    as many words that *no `sonnet` judge has ever scored a `ports-and-adapters`
    subject on `ab_quota_ledger`: n = 0*. RD-03 dispatched twelve judges at two
    tiers and that sentence stopped being true. Pinning `["opus"]` back would be
    asserting a fact about the world that the world has left; the honest repair
    is to say what is true now AND to carry the bound, because this is the one
    result in the round that flatters the apparatus.

    THE BOUND, RE-DERIVED FROM THE CARDS RATHER THAN QUOTED. The `sonnet`
    `ports-and-adapters` population is four cards over TWO declared subjects,
    and those two subjects are the `E`→`F` revision pair — one tree and its
    revision at 163 → 163 `code_lines`. `n = 0` became `n = 1 tree`. That is a
    real move off zero and it is not a measured population, so the count of
    distinct subjects is asserted here and not only the tier list.
    """

    row = next(e for e in world["entries"] if e["separates"])
    assert row["tiers_measured"] == ["opus", "sonnet"], row["tiers_measured"]

    # Re-derived, so this still goes red if the population is widened by
    # dispatching more sonnet judges at more ports-and-adapters trees -- which
    # is the event that would make the bound stop applying.
    sonnet_pa = [r for r in world["rows"]
                 if r["example"] == "ab_quota_ledger" and r["tier"] == "sonnet"
                 and r["status"] != "unfilled"
                 and (name := at.subject_of(r, world["subjects"])) is not None
                 and world["derived"][name]["derived"] == "ports-and-adapters"]
    assert len(sonnet_pa) == 4, [r["key"] for r in sonnet_pa]
    trees = sorted({at.subject_of(r, world["subjects"]) for r in sonnet_pa})
    assert trees == ["rd06_artifact_E", "rd06_artifact_F"], trees
    assert len(trees) == 2, (
        "the sonnet ports-and-adapters population has moved off the E/F revision "
        "pair; re-state the bound rather than deleting it"
    )


# ---------------------------------------------------------------------------
# 3. derivation over declaration, and everything unresolved fails open
# ---------------------------------------------------------------------------

def test_a_declaration_has_no_refusal_authority(at, world) -> None:
    """A1 -- declare the tag that makes the loss go away.

    `ex5_pipeline_divergent` is declared `ports-and-adapters` by a reader of its
    own prose and derives `UNDERIVABLE:no-effect-surface`. The declaration is
    RECORDED and refuses nothing; the derived value is what any comparison uses.
    """

    entry = world["derived"]["ex5_pipeline_divergent"]
    assert entry["declared"] == "ports-and-adapters"
    assert entry["derived"].startswith(at.UNDERIVABLE)
    assert entry["agreement"] == "UNDERIVABLE"
    assert not at.has_authority(entry["derived"])
    state, _ = at.verdict("D3", entry["derived"], "effectful", world["table"])
    assert state == at.COMPARABLE


def test_a_derivation_declaration_disagreement_fails_open_and_is_reported(at) -> None:
    """`TAG-DISPUTED` is never corrected and never blocks anything."""

    assert at.agreement_of("effectful", "ports-and-adapters") == "TAG-DISPUTED"
    assert at.agreement_of("effectful", "effectful") == "agree"
    assert at.agreement_of("UNDERIVABLE:no-effect-surface", "effectful") == "UNDERIVABLE"


@pytest.mark.parametrize("value", [
    "UNDERIVABLE:no-effect-surface",
    "UNDERIVABLE:unparsed",
    "UNDERIVABLE:unmeasurable",
    "UNDEMONSTRATED:pure",
    "UNDEMONSTRATED:greenfield",
])
def test_saying_nothing_never_buys_more_than_saying_something(at, world, value) -> None:
    """A2 and A3. An underivable subject is comparable to everything, and a
    value with no demonstrated separation fails open exactly like one."""

    assert not at.has_authority(value)
    for dim in ("D1", "D2", "D3", "D4", "D5"):
        state, reason = at.verdict(dim, value, "effectful", world["table"])
        assert state == at.COMPARABLE, (dim, value, reason)


def test_the_threshold_is_a_printed_constant_and_is_not_measured(at) -> None:
    """RD-04 §9.2 asked for exactly this and it stays an open question.

    `< 0.5` is a number RD-04 chose. The observed values are 0.100-0.125 against
    1.000, so any threshold in that interval gives the same answer on every
    subject in the record and NO ARTIFACT NEAR THE BOUNDARY HAS EVER BEEN
    MEASURED (`RD-04-DF-04`).
    """

    assert at.STATE_COLOCATION_MAX == 0.5
    out = subprocess.run([sys.executable, str(TAGS), "derive"],
                         capture_output=True, text=True, cwd=str(REPO_ROOT))
    assert "state_colocation threshold = 0.5" in out.stdout
    assert "NOT MEASURED" in out.stdout


# ---------------------------------------------------------------------------
# 4. earn-its-place, and what it cannot see
# ---------------------------------------------------------------------------

def test_every_shipped_value_with_authority_has_a_demonstration(at, world) -> None:
    """The DELETION rule, executed on the shipped vocabulary.

    A value that appears in no separating cell is decoration and is deleted.
    Both shipped values appear in the one cell there is -- which is also the
    limit: the vocabulary ships with exactly two authoritative values because
    exactly one separation exists.
    """

    demonstrated = {v for e in world["entries"] if e["separates"] for v in e["values"]}
    assert demonstrated == set(at.VALUES), (
        f"{sorted(set(at.VALUES) - demonstrated)} carries refusal authority with no "
        f"demonstrated separation. Earn-its-place is a deletion rule: delete it."
    )


def test_a_null_verdict_that_could_not_have_come_out_otherwise_is_marked(
        at, world) -> None:
    """RD-04 §7.3, carried forward as a rule rather than a footnote — and the
    claim REWRITTEN rather than the number restored (`RM-06`, group 3).

    This used to assert `D2 null_entailed is True` and `population_values ==
    [2]`. That was a true statement about the 49 sealed cards RD-04 measured.
    RD-06's three before/after pairs put D2 at 3 and 4 on `ab_quota_ledger`, so
    D2's population now takes [2, 3, 4] and a separation on it is no longer
    impossible-by-construction. **The record therefore contains no null-entailed
    cell at all**, and restoring `True` would be asserting a fact the corpus has
    left.

    So the rule is asserted TWO ways, neither of which is a floor:

    1. **Exact correspondence over the live record.** `null_entailed` is
       re-derived here from the raw card scores — not read back out of the same
       function that produced it — and must agree cell for cell. Today that set
       is empty; if the flag started firing on a multi-valued population, or
       stopped firing on a single-valued one, this goes red.
    2. **The marking is still DEMONSTRATED FIRING, on real sealed cards.** The
       49 cards written before `reading-discipline` are RD-04's own population
       and they are not a fixture. Over them D2 takes [2] alone and the flag
       comes back True — so what changed is the corpus, not the mechanism, and
       that is asserted rather than argued.
    """

    live = {e["dimension"]: e for e in world["entries"]
            if e["example"] == "ab_quota_ledger"}

    def observed(rows, dim: str) -> list[int]:
        """The population's distinct values, counted straight off the cards."""
        return sorted({r["scores"][dim] for r in rows
                       if r["example"] == "ab_quota_ledger"
                       and at.subject_of(r, world["subjects"]) is not None
                       and isinstance(r["scores"].get(dim), int)})

    for dim, entry in live.items():
        expected = (not entry["separates"]) and len(observed(world["rows"], dim)) < 2
        assert entry["null_entailed"] is expected, (dim, entry)
        assert entry["population_values"] == observed(world["rows"], dim), dim

    # 1. and what that comes to on the record as it now stands.
    assert [d for d, e in live.items() if e["null_entailed"]] == [], (
        "a cell is null-entailed again; the demonstration below is no longer "
        "the only place the marking fires and this test should say so"
    )
    assert live["D2"]["population_values"] == [2, 3, 4], live["D2"]

    # 2. the same rule, still firing, on the 49 cards RD-04 measured.
    sealed = [r for r in world["rows"] if r["round"] in SEALED_BEFORE_RD]
    assert len(sealed) == 49, len(sealed)
    before = {e["dimension"]: e for e in
              at.demonstration_table(sealed, world["derived"], world["subjects"])
              if e["example"] == "ab_quota_ledger"}
    assert before["D2"]["null_entailed"] is True, before["D2"]
    assert before["D2"]["population_values"] == [2], before["D2"]
    for dim in ("D1", "D4", "D5"):
        assert before[dim]["separates"] is False
        assert before[dim]["null_entailed"] is False
        assert len(before[dim]["population_values"]) > 1


def test_the_population_range_is_printed_beside_every_non_separating_verdict(
        world) -> None:
    """`RM-06`, group 3, and downstream of the test above.

    The population range is still printed beside every non-separating verdict
    and that half is unchanged. The second half used to be `assert
    "NULL-ENTAILED" in out.stdout` — an EXISTENCE claim that was true of RD-04's
    49 cards and is false of the 73 there are now, because no cell is
    null-entailed any more.

    Replaced with an EXACT CORRESPONDENCE rather than dropped: the set of
    printed marks must equal the set of entries the table derives as
    null-entailed. That is currently empty, so what is asserted is that the
    marker appears NOWHERE — which a printer that started marking every
    overlapping cell would fail, and which a printer that stopped marking
    altogether would also fail as soon as a single-valued population returns.
    The firing case is demonstrated on real sealed cards one test above.
    """

    out = subprocess.run([sys.executable, str(TAGS), "table"],
                         capture_output=True, text=True, cwd=str(REPO_ROOT))
    printed = [line for line in out.stdout.splitlines()
               if line.strip().startswith("does not separate")]
    assert printed, out.stdout
    for line in printed:
        assert "population took" in line, line

    marked = {(line.split()[3], line.split()[4])
              for line in printed if "NULL-ENTAILED" in line}
    derived = {(e["example"], e["dimension"])
               for e in world["entries"] if e["null_entailed"]}
    assert marked == derived, (marked, derived)


def test_the_same_tag_control_holds(at, world) -> None:
    """Without it any two artifacts pass, because any two differ in something.

    **THIS TEST IS DELIBERATELY RED (`RM-06`, group 2). DO NOT MAKE IT GREEN.**

    It is not pinned to a count the corpus grew. It is a CONTROL, it is now
    reporting a real result, and the result is unflattering: nine same-tag pairs
    separate — eight on D2 and one on D5 — every one of them a before-tree
    scoring disjointly from an after-tree at the SAME derived value. RD-06's
    three revision pairs gave this control its first within-value TREATMENT
    difference and it cannot tell that apart from a difference in architecture
    (`RD-03-DF-12`).

    The two repairs that would clear it were both rejected. Scoping the control
    to the dimension the separation is claimed on (D3, where it still holds)
    would make it a check about the row rather than about the axis. Excluding
    revision pairs from the population would remove exactly the evidence the
    control exists to see. Either one converts a measurement into a tautology,
    which is the failure this epic family exists to prevent.

    Filed as `RM-06-DF-01`. It goes green when the axis can distinguish
    treatment from architecture, or when the epic decides it cannot and says so.
    """

    controls = at.same_tag_controls(world["rows"], world["derived"], world["subjects"])
    assert controls, "no same-tag control is available; the separation is uncontrolled"
    failed = [c for c in controls if c["separates"]]
    assert failed == [], (
        f"{len(failed)} same-tag pair(s) separate: "
        f"{[(c['dimension'], c['a'], c['b']) for c in failed]}. "
        f"EXPECTED RED -- see this test's docstring and RM-06-DF-01. The control "
        f"is reporting a real result and may not be narrowed to silence it."
    )


# ---------------------------------------------------------------------------
# 5. SCOPE-DRIFT -- A5, and R1's demonstrated failing input on real cards
# ---------------------------------------------------------------------------

def test_scope_drift_is_reported_on_the_sealed_toolchain_cards(at, world) -> None:
    """THE DEMONSTRATED FAILING INPUT, and it is not a fixture.

    `toolchain_removal` D3 = 2, 2, 3, 4 is the only contested group in 49 sealed
    cards. Two of its four judges cite predominantly outside the scope the round
    was attributed to -- one names the fixture, one names the compiler package --
    and within each scope the spread is ZERO. The four judges scored three
    subjects. No card is edited and no judging is redone; the attribution is
    counted from the cards' own D3 citations.
    """

    drifts = at.scope_drift(world["rows"], world["subjects"])
    ours = {d["card"].rsplit("/", 1)[-1]: d for d in drifts if TOOLCHAIN in d["card"]}
    assert set(ours) == {"20260807-sm05rm-K-p3", "20260807-sm05rm-K-p4"}, sorted(ours)
    assert ours["20260807-sm05rm-K-p3"]["cited_subject"] == "toolchain_fixture"
    assert ours["20260807-sm05rm-K-p3"]["score"] == 4
    assert ours["20260807-sm05rm-K-p4"]["cited_subject"] == "toolchain_compiler"
    assert ours["20260807-sm05rm-K-p4"]["score"] == 3


def test_the_two_cards_whose_citations_stay_in_scope_are_not_reported(at, world) -> None:
    """THE PASSING HALF. `K-p1` and `K-p2` cite `scripts/` and are left alone --
    a check that reports everything reports nothing."""

    drifts = {d["card"] for d in at.scope_drift(world["rows"], world["subjects"])}
    for run in ("20260807-sm05rm-K-p1", "20260807-sm05rm-K-p2"):
        assert f"{TOOLCHAIN}/{run}" not in drifts


def test_scope_drift_reaches_only_cards_it_can_locate(at, world) -> None:
    """A card whose citations name no declared scope is not reported at all.

    Silence here is `UNREACHABLE`, not `HOLDS`, and it is the honest default:
    the checker cannot see a scope nobody declared.
    """

    drifts = at.scope_drift(world["rows"], world["subjects"])
    assert all(any(v for v in d["citation_counts"].values()) for d in drifts)


def test_a_scaffolded_scope_is_declared_before_scoring_and_a_moved_one_is_refused(
        st, tmp_path) -> None:
    """A5's other half: choose the scope that carries the flattering tag.

    The scope goes into the UNFILLED skeleton, copied out of `subjects.toml`
    before any judge is dispatched, and `check` refuses a card whose scope no
    longer matches. That reuses the machinery that already refuses a second
    scaffold over a measurement; it invents nothing.

    **RM-04: A BLINDED CARD RESOLVES BY SCOPE, NOT BY NAME**, because
    `subject.name` was a real arm identity in the file the judge is handed --
    RM-03 shipped cards labelled `T` reading `arm_b` and `ports-and-adapters`.
    A5's defence is that the scope was DECLARED BEFORE SCORING AND HAS NOT
    MOVED, and that is exactly what is asserted below; the name was never the
    part doing the work.
    """

    epic = tmp_path / "round"
    assert st.main(["scaffold", str(epic), "--example", "ab_quota_ledger",
                    "--arms", "A,B", "--judges", "1", "--subject", "arm_b",
                    "--run-date", "20260808"]) == 0
    cards = sorted(epic.rglob("scorecard.json"))
    assert cards
    card = json.loads(cards[0].read_text())
    # blinded: the scope, and nothing that identifies it or pre-answers D3
    assert card["subject"]["blinded"] is True
    assert card["subject"]["name"] is None, card["subject"]
    assert "declared_effect_boundary" not in card["subject"], card["subject"]
    assert card["subject"]["scope"] == [
        "specs/results/scorecards/ports-as-adapters/blind/artifact_T"]
    assert card["status"] == "unfilled", "the scope is fixed before the numbers exist"
    problems, _ = st.check(card, str(cards[0]))
    assert problems == [], problems

    # A5, unchanged: a scope that moved is refused, resolved by the scope itself
    card["subject"]["scope"] = ["examples/validation/ab/eval"]
    problems, _ = st.check(card, str(cards[0]))
    assert any("matches no scope declared in subjects.toml" in p for p in problems), problems

    # and an UNBLINDED card still resolves by name, with the old refusals intact
    epic2 = tmp_path / "unblinded"
    assert st.main(["scaffold", str(epic2), "--example", "ab_quota_ledger",
                    "--arms", "A", "--judges", "1", "--subject", "arm_b",
                    "--run-date", "20260808", "--unblinded",
                    "--reason", "A5 regression check"]) == 0
    path2 = sorted(epic2.rglob("scorecard.json"))[0]
    card2 = json.loads(path2.read_text())
    assert card2["subject"]["name"] == "arm_b"
    assert card2["subject"]["declared_effect_boundary"] == "ports-and-adapters"
    card2["subject"]["scope"] = ["scripts"]
    problems, _ = st.check(card2, str(path2))
    assert any("THE SCOPE MOVED" in p for p in problems), problems

    card2["subject"] = {"name": "not_a_subject", "scope": ["scripts"]}
    problems, _ = st.check(card2, str(path2))
    assert any("is not declared in subjects.toml" in p for p in problems), problems


def test_a_card_with_no_subject_is_legal_and_is_every_sealed_card(at, world) -> None:
    """R-H4: a sealed card is never edited, so the attribution for the cards
    written before RD-05 lives in `subjects.toml` beside them.

    `RM-06`, group 1: RE-DERIVED, because the count moved for a designed reason.
    This asserted `declared == []` over 49 cards and `48 mapped, 1 unmapped`.
    Both were true of the record RD-05 shipped into and both are false now —
    **RD-05's own design is that a card scaffolded from RD-05 onward carries
    `subject.name` itself**, and RD-03 was the first round to scaffold 24 of
    them. Restoring `[]` would assert that RD-05's feature had not shipped.

    What the rule actually says survives intact and is now stated as two
    directions rather than one count:

      * NO CARD PREDATING `reading-discipline` HAS GROWN A SUBJECT FIELD. That
        is R-H4 — a sealed card is never edited — and it is the half that was
        ever load-bearing.
      * Every card that DOES carry one names a subject `subjects.toml`
        declares, so the field cannot smuggle in an undeclared scope.

    And the mapping is re-derived rather than pinned: every card maps to a
    subject except exactly the one `owner-pre` card, which is the same single
    exception it has always been.
    """

    sealed_before_rd05 = [r for r in world["rows"] if r["round"] in SEALED_BEFORE_RD]
    assert len(sealed_before_rd05) == 49, len(sealed_before_rd05)
    assert [r["key"] for r in sealed_before_rd05 if r["declared_subject"]] == [], (
        "a card sealed before RD-05 grew a subject field"
    )

    declared = [r for r in world["rows"] if r["declared_subject"]]
    assert declared, "no card carries a subject field; RD-05's scaffold has regressed"
    undeclared = sorted({r["declared_subject"] for r in declared
                         if r["declared_subject"] not in world["subjects"]})
    assert undeclared == [], (
        f"{undeclared} is named by a card and declared by no entry in subjects.toml"
    )

    mapped = [r for r in world["rows"] if at.subject_of(r, world["subjects"])]
    unmapped = [r["key"] for r in world["rows"]
                if not at.subject_of(r, world["subjects"])]
    assert len(mapped) == len(world["rows"]) - 1, (len(mapped), len(world["rows"]))
    assert len(unmapped) == 1, unmapped
    assert "owner-pre" in unmapped[0], unmapped


# ---------------------------------------------------------------------------
# 6. the table is re-derived, and a stale row is a violation
# ---------------------------------------------------------------------------

def test_the_committed_demonstration_re_derives_from_the_cards(st, at, world) -> None:
    """R-H1's third clause over the shipped ledger: OK, and no violation.

    **`RM-06-DF-02` IS SETTLED HERE AND THE ROW'S NUMBERS DID NOT CHANGE.**

    RM-06 left this red and proved why: the declaration `effectful = [1, 2]`,
    `tiers_measured = ["opus"]` re-derives EXACTLY over the 49 cards sealed
    before `reading-discipline`, which is RD-04's own population. **The row is
    scoped, not wrong.** What moved underneath it is the card population.

    RM-04's settlement is a REMOVAL and it is argued from what the code reads,
    not from what would be convenient:

    * `architecture_tags.authority()` admits an entry if and only if
      `separates` is true, and keys it on `(dimension, {value, value})`.
      `verdict()` reads the RE-DERIVED entry, including its `tiers_measured`.
      **Nothing reads the DECLARED `ranges` or `tiers_measured` to refuse
      anything**, so agreeing with the cards would not have widened the
      authority and neither does dropping them. That is `RM-04-DF-03`, and it
      is asserted below rather than believed.
    * Every other re-derived declaration in the ledger names a FIXED
      population — `[[movement]]` names two cards, `[[contested]]` names one
      judge group — so neither can go stale. `ranges` is a figure over an OPEN
      population and can only be re-affirmed forever.

    So the two fields are gone from the row, RD-04's figures move into its
    `why` with their population named, and **the control RM-06 identified is
    kept HERE, as an executed assertion at a population that cannot grow.**
    """

    log = st.load_log(SCORECARDS)
    assert log["demonstrations"], "the ledger declares no `[[demonstration]]`"
    declared = log["demonstrations"][0]

    # THE CONTROL, and it is the whole reason this test still exists. RD-04's
    # figures, at RD-04's population, pinned as literals. This population is
    # sealed and cannot grow, so a future card cannot move these numbers -- and
    # if someone silently re-scopes the row, this fails.
    sealed = [r for r in world["rows"] if r["round"] in SEALED_BEFORE_RD]
    assert len(sealed) == 49, len(sealed)
    row = next(e for e in at.demonstration_table(
        sealed, world["derived"], world["subjects"]) if e["separates"])
    assert row["id"] == declared["id"], (row["id"], declared["id"])
    assert row["ranges"] == {"effectful": [1, 2], "ports-and-adapters": [4, 4]}, row["ranges"]
    assert row["tiers_measured"] == ["opus"], row["tiers_measured"]

    # AND THE ROW NO LONGER DECLARES THEM. A row that declared them would have
    # to be re-affirmed against every future card of this example, which is the
    # treadmill `RM-06-DF-02` is about.
    assert "ranges" not in declared, declared
    assert "tiers_measured" not in declared, declared

    # `RM-04-DF-03`: the dropped fields grant nothing. Refusal authority is
    # computed from `separates` alone, and it is unchanged between RD-04's
    # 49-card population and the whole record.
    entries_49 = at.demonstration_table(sealed, world["derived"], world["subjects"])
    entries_now = at.demonstration_table(world["rows"], world["derived"], world["subjects"])
    key = (row["dimension"], frozenset(row["values"]))
    assert key in at.authority(entries_49)
    assert key in at.authority(entries_now), (
        "the separation this row declares no longer holds at the current record; "
        "that is a real result and `separates` is what must be re-decided, not "
        "the ranges beside it"
    )

    findings = st.audit_rh1_architecture(
        {"root": SCORECARDS, "demonstrations": log["demonstrations"]})
    violations = [m for level, m in findings if level == st.VIOLATION]
    assert violations == [], violations
    assert any(level == st.OK and "SEPARATES re-derived" in m for level, m in findings)


def test_a_demonstration_the_cards_no_longer_support_is_a_violation(st) -> None:
    """THE FAILING INPUT for the anti-staleness half.

    R-H5's history is the argument: an unnumbered rule with no check was added
    at close and `audit` rejected it within the minute. A row that grants a
    refusal is the last thing that may be allowed to go stale -- a comparison
    would be refused on evidence nobody can find.
    """

    log = st.load_log(SCORECARDS)
    stale = json.loads(json.dumps(log["demonstrations"][0]))
    stale["dimension"] = "D1"
    findings = st.audit_rh1_architecture({"root": SCORECARDS, "demonstrations": [stale]})
    violations = [m for level, m in findings if level == st.VIOLATION]
    assert violations, findings
    assert "declares dimension" in violations[0]

    invented = json.loads(json.dumps(log["demonstrations"][0]))
    invented["id"] = "effect_boundary-ab_quota_ledger-D1-effectful-vs-ports-and-adapters"
    findings = st.audit_rh1_architecture(
        {"root": SCORECARDS, "demonstrations": [invented]})
    assert [m for level, m in findings if level == st.VIOLATION], findings


def test_an_undeclared_separation_grants_nothing_and_is_reported_open(st) -> None:
    """An authority nobody declared is not an authority."""

    findings = st.audit_rh1_architecture({"root": SCORECARDS, "demonstrations": []})
    opens = [m for level, m in findings if level == st.OPEN]
    assert any("the cards support a separation on D3" in m for m in opens), opens


# ---------------------------------------------------------------------------
# 7. no new gates
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("command", ["derive", "table", "drift"])
def test_the_tag_refuses_nothing_and_always_exits_zero(command) -> None:
    """`no_new_gates_rule`: a tag constrains what may be COMPARED and refuses
    nothing about the code. Five epics of static checking on the product caught
    zero bugs and this is deliberately not a sixth."""

    proc = subprocess.run([sys.executable, str(TAGS), command],
                          capture_output=True, text=True, cwd=str(REPO_ROOT))
    assert proc.returncode == 0, proc.stderr


def test_the_derivation_reproduces_rd04s_sealed_machine_record(at, world) -> None:
    """The predicate is RD-04's, not a rewrite of it.

    Compared against `result.json` -- the machine record -- rather than against
    the design page's markdown table, because one of them is the measurement.
    """

    recorded = json.loads((
        REPO_ROOT / "specs/results/scorecards/reading-discipline"
        / "GOAL-tags-earn-their-place/RD-04/analysis/result.json").read_text())["derived"]
    for name, entry in recorded.items():
        if name not in world["derived"]:
            continue
        got = world["derived"][name]
        assert got["derived"] == entry["value"], (name, got["derived"], entry["value"])
        assert got["facts"].get("state_colocation") == entry["facts"].get(
            "state_colocation"), name
