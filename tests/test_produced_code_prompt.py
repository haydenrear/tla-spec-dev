"""The produced-code figures reach a PROMPT, and the prompt is not a thermostat.

`ports-as-adapters` shipped the instrument (`scripts/code_complexity.py`) and
the human-readable intuition, and not the prompting: `grep -rn code_complexity
prompts/` was **empty**, so no agent was ever handed the figures and asked what
they meant about its own design. FI-05 ships the ask.

The ask is the easy part. The failure mode is that a prompt handing an agent
numbers becomes a target, which is how every static check this project retired
started. So these tests assert, in order of how much damage the absence has
already caused:

1. **The figures reach a prompt at all** -- the premise of the ticket, made
   executable rather than left as a grep somebody ran once.
2. **The ask names no threshold and no direction.** No budget, no "keep under",
   no verdict vocabulary, and no request for a delta (`MF-020`).
3. **The ask does not choose the boundary** (`CD-01`). It says where the
   boundary IS and states that it cannot say where one should go.
4. **Every figure name the prompt uses is emitted by the shipped instrument**
   (`declaration_executability_rule`): rename a figure and this fails.
5. **Nothing under these trees consumes the instrument AS A CONDITION ON THE
   CODE** -- including the prompt's own machinery, because there deliberately
   is none. Asserted over `examples/` and `prompts/`, the two trees FI-05 added
   files to and the two FI-02's reference scan does not reach, using FI-02's
   OWN `executable_references` and `refusing_uses` rather than a second copy of
   either. *RD-05 restated this from "zero references at all", which was a proxy
   for "nothing branches on it" written while nothing needed to refer to the
   instrument; see `DERIVED_TAG_READER` for the ground and its limits.*
6. **The sealed ask block did not move.** PA-01 sealed arm B at 105 unique
   content lines as the control that separates "hexagonal helped" from "a
   longer ask helped". The produced-code ask is a SEPARATE dispatch precisely
   so that number is untouched, and this asserts it with the shipped builders.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.test_code_complexity import executable_references, refusing_uses  # noqa: E402

PROMPTS = REPO_ROOT / "prompts"
READING_PROMPT = PROMPTS / "produced_code_reading.md"
HEXAGONAL = PROMPTS / "hexagonal_implementation.md"
INTUITION = REPO_ROOT / "references" / "complexity_intuition.md"

ASK_BEGIN = "<!-- PRODUCED-CODE-READING:BEGIN -->"
ASK_END = "<!-- PRODUCED-CODE-READING:END -->"


def ask_block() -> str:
    text = READING_PROMPT.read_text(encoding="utf-8")
    return text.split(ASK_BEGIN, 1)[1].split(ASK_END, 1)[0]


# ---------------------------------------------------------------------------
# 1. the figures reach a prompt at all
# ---------------------------------------------------------------------------


def test_the_figures_reach_a_prompt() -> None:
    """`grep -rn code_complexity prompts/` was the ticket's premise. It is now
    non-empty, and this is the assertion that keeps it that way."""

    hits = [
        path.relative_to(REPO_ROOT)
        for path in sorted(PROMPTS.rglob("*"))
        if path.is_file() and "code_complexity" in path.read_text(encoding="utf-8")
    ]
    assert hits, (
        "no prompt mentions the produced-code instrument. The figures reach a human "
        "reading a reference page and a scorecard's mechanical block, and no agent is "
        "ever asked what they mean about its own design -- which is the half of the "
        "complexity work FI-05 exists to land."
    )
    assert READING_PROMPT.relative_to(REPO_ROOT) in hits
    assert HEXAGONAL.relative_to(REPO_ROOT) in hits, (
        "the implementation prompt still points only at the TLA+ descriptor"
    )


def test_the_ask_block_is_dispatchable_and_delimited() -> None:
    text = READING_PROMPT.read_text(encoding="utf-8")
    assert text.count(ASK_BEGIN) == 1 and text.count(ASK_END) == 1
    assert text.index(ASK_BEGIN) < text.index(ASK_END)
    assert len(ask_block().strip().splitlines()) > 40, "the ask is a stub"


def test_the_intuition_page_points_at_the_prompt() -> None:
    """The reference page was the only place these figures were read. It now
    names the prompt, so a reader of either finds the other."""

    assert "prompts/produced_code_reading.md" in INTUITION.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 2. no threshold, no direction, no verdict
# ---------------------------------------------------------------------------

#: Shapes that turn a reading into a target. Each is a phrasing this repository
#: has actually retired, not a hypothetical. These may never appear at all.
THRESHOLD_SHAPES = (
    r"\bkeep\s+(?:it\s+)?(?:under|below)\b",
    r"\bno\s+more\s+than\s+\d",
    r"\bat\s+most\s+\d",
    r"\bfewer\s+than\s+\d",
    r"\bshould\s+be\s+(?:under|below|less|fewer)\b",
    r"\bmust\s+be\s+(?:under|below|less|fewer)\b",
    r"\blimit\s+of\s+\d",
    r"[<>]=?\s*\d+",
)

#: Words that may appear ONLY where the ask is refusing them. A prompt saying
#: "there is no threshold" is doing the opposite of setting one, and a checker
#: that could not tell the two apart would push the refusal out of the prompt --
#: which is the same defect as PA-06-DF-05, where a tripwire failed a docstring
#: mention and passed an aliased import.
REFUSAL_ONLY_WORDS = ("threshold", "budget", "quota of", "score", "grade")

_REFUSAL = re.compile(r"\b(?:no|not|never|none|nothing|without)\b", re.IGNORECASE)

#: Vocabulary that supplies a DIRECTION the instrument does not have. Each is
#: allowed only where the ask is explicitly refusing it, which the test below
#: enforces by requiring the refusal sentence on the same line.
DIRECTION_WORDS = (
    "lower is better",
    "higher is better",
    "reduce the",
    "minimi",
    "optimi",
    "improve the number",
    "bring it down",
    "make it smaller",
    "aim for",
    "should go down",
)


@pytest.mark.parametrize("shape", THRESHOLD_SHAPES)
def test_the_ask_names_no_threshold(shape: str) -> None:
    found = re.search(shape, ask_block(), re.IGNORECASE)
    assert not found, (
        f"the dispatched ask contains {found.group(0)!r}. A prompt that hands an agent "
        f"figures AND a number to clear is a thermostat: the cheapest way to clear it "
        f"has been measured, twice, to be duplicating code across the boundary the "
        f"check was protecting."
    )


@pytest.mark.parametrize("word", REFUSAL_ONLY_WORDS)
def test_threshold_words_appear_only_in_a_refusal(word: str) -> None:
    ask = ask_block()
    for found in re.finditer(re.escape(word), ask, re.IGNORECASE):
        window = ask[max(0, found.start() - 80):found.start()]
        assert _REFUSAL.search(window), (
            f"{word!r} appears in the dispatched ask without a refusal in front of it: "
            f"...{ask[max(0, found.start() - 80):found.end() + 40].strip()!r}"
        )


@pytest.mark.parametrize("word", DIRECTION_WORDS)
def test_the_ask_supplies_no_direction(word: str) -> None:
    """MF-020: a metric falling is not evidence the design improved."""

    for line in ask_block().splitlines():
        if word in line.lower():
            pytest.fail(
                f"the dispatched ask says {word!r} on: {line.strip()!r}. The instrument "
                f"prints no delta and has no --compare mode for exactly this reason."
            )


def test_the_ask_refuses_a_delta_explicitly() -> None:
    lowered = ask_block().lower()
    assert "do not subtract" in lowered
    assert "not a before-and-after" in lowered or "not a before and after" in lowered
    assert "a metric falling is not evidence" in lowered


def test_the_ask_asks_for_a_reading_not_a_score() -> None:
    lowered = ask_block().lower()
    assert "read it" in lowered or "to **read** it" in lowered
    assert "not a score" in lowered
    assert "in your own words" in lowered
    assert "in prose" in lowered
    for absent in ("score of", "rate the", "grade the", "out of 5", "out of 4"):
        assert absent not in lowered, f"the ask asks for a score: {absent!r}"


# ---------------------------------------------------------------------------
# 3. CD-01 -- it does not choose the boundary
# ---------------------------------------------------------------------------


def test_the_ask_does_not_choose_the_boundary() -> None:
    """CD-01: a tool that picks the cut makes every edge legal by construction."""

    lowered = ask_block().lower()
    assert "cannot tell you where to put one" in lowered
    assert "where your boundary" in lowered
    for prescription in (
        "you should extract", "move the", "split the module", "introduce a port for",
        "the boundary should go between",
    ):
        assert prescription not in lowered, (
            f"the ask proposes a cut ({prescription!r}). CD-01 forbids the instrument and "
            f"anything speaking for it from choosing the boundary."
        )


# ---------------------------------------------------------------------------
# 4. declaration executability -- the figure names are the shipped ones
# ---------------------------------------------------------------------------


#: The row shape of the figure table in `references/complexity_intuition.md`
#: -- "| `key` | scope | what it counts |". That table is bound to the shipped
#: instrument by `test_code_complexity.py::test_documented_figures_match_shipped_output`,
#: which asserts it and the real output name the SAME SET.
_INTUITION_FIGURE = re.compile(r"^\|\s*`([a-z][a-z_]+)`\s*\|", re.MULTILINE)

#: A recorded cell row in the same page's like-for-like table:
#: "| `branch_points_in_effectful_modules` | 10 | 1 | 10 | 1 |". That table is
#: bound to a LIVE RUN by `test_recorded_figures_match_a_live_run`.
_INTUITION_CELLS = re.compile(
    r"^\|\s*`([a-z][a-z_]+)`\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|",
    re.MULTILINE,
)


def _intuition_figures() -> set[str]:
    return set(_INTUITION_FIGURE.findall(INTUITION.read_text(encoding="utf-8")))


def _intuition_cells() -> dict[str, tuple[int, int, int, int]]:
    """`figure -> (reference, reference_ports, arm_a, arm_b)`, like for like.

    The FIRST table wins: the page prints `totals_code_only` before `totals`,
    under the heading "Like for like", and the two must never be mixed.
    """
    out: dict[str, tuple[int, int, int, int]] = {}
    for key, *cells in _INTUITION_CELLS.findall(INTUITION.read_text(encoding="utf-8")):
        out.setdefault(key, tuple(int(c) for c in cells))
    return out


def test_every_figure_the_prompt_names_is_a_documented_figure() -> None:
    """Rename a figure and forget this prompt, and this fails instead of the
    prompt quietly asking about a key nobody emits.

    IT DOES NOT RUN THE INSTRUMENT, and that is deliberate rather than lazy.
    The chain is instrument -> `complexity_intuition.md` -> this prompt, and its
    first link is already executable:
    `test_code_complexity.py::test_documented_figures_match_shipped_output`
    asserts the page's table and the shipped output name the same set. Reading
    the figures again HERE would make this file a reader of the instrument's
    output, which is the one thing the whole ticket is arranging for nothing to
    be.
    """

    documented = _intuition_figures()
    assert "branch_points_in_effectful_modules" in documented, (
        "the reference page's figure table did not parse; this test would then assert "
        "nothing"
    )
    text = READING_PROMPT.read_text(encoding="utf-8")
    named = {m.group(1) for m in re.finditer(r"`([a-z][a-z_]{4,})`", text)}
    # Words in backticks that are prose or paths, not figures.
    named -= {"getattr", "sorted", "python", "scripts", "prompts", "references"}
    structural = {"totals", "totals_code_only", "completeness"}
    unknown = named - documented - structural
    assert not unknown, (
        f"the prompt names figures the reference page does not document: {sorted(unknown)}. "
        f"Either the instrument renamed them or the prompt invented them."
    )
    # And the partition that is the whole reason the ask exists.
    for key in ("branch_points_in_effectful_modules", "instance_state_in_effectful_modules"):
        assert key in named and key in documented


def test_the_partition_quoted_in_the_prompt_matches_the_recorded_table() -> None:
    """The prompt copies cells out of the record to say WHY the figures are
    worth asking about. A copy that drifts is a claim nothing executes.

    Compared against `complexity_intuition.md`'s like-for-like table, which
    `test_recorded_figures_match_a_live_run` pins cell by cell to a live run --
    so a stale number still fails a test, and this file still never reads a
    figure.
    """

    cells = _intuition_cells()
    text = READING_PROMPT.read_text(encoding="utf-8")

    flat, ported, arm_a, arm_b = cells["branch_points_in_effectful_modules"]
    assert (flat, ported, arm_a, arm_b) == (10, 1, 10, 1)
    assert "| `branch_points_in_effectful_modules` | **10** | **1** | **10** | **1** |" in text

    flat, ported, arm_a, arm_b = cells["instance_state_in_effectful_modules"]
    assert (flat, ported, arm_a, arm_b) == (7, 1, 8, 1)
    assert "| `instance_state_in_effectful_modules` | **7** | **1** | **8** | **1** |" in text

    flat, ported, arm_a, arm_b = cells["effectful_calls"]
    assert flat == ported == 3, "the two anchor trees must still make the SAME three calls"
    assert "| `effectful_calls` | 3 | 3 | 5 | 3 |" in text

    # The caution's "a ported tree measures LARGER" cells, same source.
    assert tuple(cells["modules"][:2]) == (1, 5)
    assert tuple(cells["public_surface"][:2]) == (15, 26)
    assert tuple(cells["code_lines"][:2]) == (122, 255)
    assert "5 modules, 26 public surface and 255 code lines" in text
    assert "1, 15 and 122" in text


# ---------------------------------------------------------------------------
# 5. still nothing consumes it
# ---------------------------------------------------------------------------

#: The trees FI-02's REFERENCE scan does not reach. Its
#: `test_nothing_executable_reads_this_instrument` covers `EXECUTABLE_SURFACES`
#: (scripts, skill-scripts, spec_double_compiler, templates, test_graph) and
#: deliberately not `specs/**`; its `test_no_reader_of_this_instrument_gates_on_its_output`
#: is repository-wide but only forbids GATING. Neither reaches `examples/` or
#: `prompts/` with the stronger question, and those are exactly the two trees
#: FI-05 added files to.
FI05_TREES = ("examples", "prompts")

#: RD-05. THE ONE FILE UNDER THOSE TREES THAT REFERS TO THE INSTRUMENT, and the
#: reason the two tests below now say "as a condition on the code" where they
#: said "at all".
#:
#: The epic owner ruled (`READING-DISCIPLINE-EPIC.md` §6b) on the repository-wide
#: gating invariant: it means a figure DECIDING SOMETHING ABOUT THE CODE, and
#: observing where a boundary already is is the thermometer's job. The same
#: reasoning decides these two, because "zero references at all" was a PROXY for
#: "nothing branches on it", written when nothing needed to refer to it. The real
#: property is now checkable -- `refusing_uses` -- so the proxy is replaced by
#: the thing it stood for, not carved out of.
#:
#: THIS IS NOT A NAME ON A SKIP LIST. Every other file under those trees is
#: still reported, and this one is admitted only while it refuses on no figure,
#: which
#: `tests/test_code_complexity.py::test_the_derivation_observes_and_never_refuses`
#: asserts separately and which is re-asserted below. Delete the derivation and
#: these tests go red on the missing file rather than passing quietly.
#:
#: AND THE PART RD-05 DOES NOT CLAIM: §6b names the GATING invariant and not
#: this one. Extending it here is RD-05's reading, reported for review rather
#: than presented as covered.
DERIVED_TAG_READER = "examples/validation/scorecards/architecture_tags.py"


def _references_under(trees) -> list[str]:
    """Executable references to the instrument under `trees`, via the SHIPPED
    builder.

    `executable_references` is FI-02's, not a second copy. FI-02 replaced the
    substring tripwire that PA-06-DF-05 filed -- it excluded docstrings, bare
    string statements and comments, and required a whole-token match -- and a
    private re-implementation here would be two scanners drifting apart, which
    is the `declaration_executability_rule`'s own shape.
    """

    hits: list[str] = []
    for tree in trees:
        root = REPO_ROOT / tree
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix != ".py":
                continue
            if any(part in {"__pycache__", "build", "node_modules"} for part in path.parts):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if "code_complexity" not in text:
                continue
            rel = str(path.relative_to(REPO_ROOT))
            for lineno, why in executable_references(text):
                hits.append(f"{rel}:{lineno}: {why}")
    return sorted(hits)


def test_nothing_under_these_trees_consumes_the_instrument_as_a_condition() -> None:
    """GOAL-instruments-can-fail's local signal, executable.

    The prompt tells the reader to run the shipped command and paste the
    output. A script that ran it for them AND THEN DECIDED SOMETHING WITH THE
    ANSWER would be the first thing in this toolchain to turn a thermometer
    into a thermostat, and this names the file and line if one appears.

    UNTIL RD-05 THIS ASSERTED ZERO REFERENCES AT ALL, which was a stronger
    statement than the thing it was protecting and was true only while nothing
    needed to refer to the instrument. `architecture_tags.py` derives a
    COMPARABILITY LABEL from figures the instrument already prints; under the
    §6b ruling that is observing where a boundary already is, not choosing one,
    and it refuses nothing about any artifact. So the rule now says what it
    means: **anything here may read the figures; nothing here may refuse on
    them.**

    Both halves are asserted. Any file under these trees other than the
    declared derivation must still make ZERO executable references, and the
    derivation itself must make zero REFUSING uses.
    """

    hits = [h for h in _references_under(FI05_TREES)
            if not h.startswith(DERIVED_TAG_READER + ":")]
    assert hits == [], (
        f"FI-05's own trees now refer to the produced-code instrument executably: {hits}. "
        f"It reports; nothing may consume it as a condition on the code."
    )
    derivation = REPO_ROOT / DERIVED_TAG_READER
    assert derivation.is_file(), (
        f"{DERIVED_TAG_READER} is gone; the one admitted reference has no subject and "
        f"this test is asserting nothing"
    )
    assert refusing_uses(derivation.read_text(encoding="utf-8")) == [], (
        f"{DERIVED_TAG_READER} now REFUSES on a figure. A derived comparability label is "
        f"not a thermostat; a figure that raises, asserts or exits is one."
    )


def test_the_prompt_mentions_it_only_as_prose() -> None:
    """Silence and a pass are different claims: the mention must exist, and it
    must be markdown rather than anything that runs."""

    text = READING_PROMPT.read_text(encoding="utf-8")
    assert "code_complexity" in text
    assert READING_PROMPT.suffix == ".md"
    named = sorted(
        str(path.relative_to(REPO_ROOT))
        for tree in FI05_TREES
        for path in (REPO_ROOT / tree).rglob("*")
        if path.is_file() and path.suffix == ".py"
        and "code_complexity" in path.read_text(encoding="utf-8", errors="ignore")
    )
    assert named == [DERIVED_TAG_READER], (
        f"the set of PYTHON files under {FI05_TREES} naming the instrument moved: {named}. "
        f"Each must be re-checked BY HAND -- a mention is how a consumer arrives, and the "
        f"one that is here was admitted by an owner ruling and by a property, not by being "
        f"typed into a list."
    )


def test_the_instrument_still_exits_zero_on_the_artifacts_this_ticket_added() -> None:
    targets = [
        REPO_ROOT / "examples" / "validation" / "ab" / "dispatch",
        REPO_ROOT / "prompts",
        REPO_ROOT / "examples" / "validation" / "check_prediction_seal.py",
        REPO_ROOT / "no" / "such" / "tree",
    ]
    for target in targets:
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "code_complexity.py"), str(target)],
            capture_output=True, text=True, check=False,
        )
        assert proc.returncode == 0, f"{target} produced exit {proc.returncode}"


# ---------------------------------------------------------------------------
# 6. the sealed ask block did not move
# ---------------------------------------------------------------------------


def test_the_sealed_length_match_is_untouched() -> None:
    """PA-01 sealed arm B at 105 unique content lines against arm A's 16.

    FI-05 added a section to `hexagonal_implementation.md`, OUTSIDE
    `HEXAGONAL-ASK:BEGIN/END`, precisely so that number does not move. Arm B
    inlines the ask block verbatim; if the ask block changed, this fails.
    """

    sys.path.insert(0, str(REPO_ROOT / "examples" / "validation" / "ab"))
    import check_catalogue  # noqa: PLC0415

    a = check_catalogue.distinct_lines(check_catalogue.arm_prompt("arm_a"))
    b = check_catalogue.distinct_lines(check_catalogue.arm_prompt("arm_b"))
    assert len(b - a) == 105, (
        "arm B's unique content moved. The produced-code ask is a separate dispatch so "
        "that PA-01's sealed length match stays comparable across the epic boundary."
    )
    assert len(a - b) == 16


def test_the_new_section_is_outside_the_sealed_ask_block() -> None:
    text = HEXAGONAL.read_text(encoding="utf-8")
    ask = text.split("<!-- HEXAGONAL-ASK:BEGIN -->", 1)[1].split("<!-- HEXAGONAL-ASK:END -->")[0]
    assert "code_complexity" not in ask, (
        "the produced-code pointer landed INSIDE the sealed ask block, which moves a "
        "sealed number in a live experiment and puts figures in front of an author "
        "before there is any code to measure."
    )
    assert "produced_code_reading" not in ask
    assert "code_complexity" in text
