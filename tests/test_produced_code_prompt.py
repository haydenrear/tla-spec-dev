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
5. **Nothing executable consumes the instrument**, still, after the prompt
   landed -- including the prompt's own machinery, because there deliberately
   is none.
6. **The sealed ask block did not move.** PA-01 sealed arm B at 105 unique
   content lines as the control that separates "hexagonal helped" from "a
   longer ask helped". The produced-code ask is a SEPARATE dispatch precisely
   so that number is untouched, and this asserts it with the shipped builders.
"""

from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.code_complexity import analyze_tree  # noqa: E402

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


def test_every_figure_the_prompt_names_is_emitted_by_the_instrument() -> None:
    """Rename a figure in `code_complexity.py` and forget this prompt, and this
    fails instead of the prompt quietly asking about a key nobody emits."""

    record = analyze_tree(REPO_ROOT / "examples" / "validation" / "ab" / "reference_ports")
    emitted = set(record["totals"]) | set(record["modules"][0]) | {
        "totals", "totals_code_only", "completeness",
    }
    text = READING_PROMPT.read_text(encoding="utf-8")
    named = {m.group(1) for m in re.finditer(r"`([a-z][a-z_]{4,})`", text)}
    # Words in backticks that are prose or paths, not figures.
    named -= {"getattr", "sorted", "python", "scripts", "prompts", "references"}
    unknown = {n for n in named if n not in emitted}
    assert not unknown, (
        f"the prompt names figures the shipped instrument does not emit: {sorted(unknown)}. "
        f"Either the instrument renamed them or the prompt invented them."
    )
    # And the partition that is the whole reason the ask exists.
    for key in ("branch_points_in_effectful_modules", "instance_state_in_effectful_modules"):
        assert key in named and key in emitted


def test_the_recorded_partition_in_the_prompt_matches_a_live_run() -> None:
    """The prompt copies four cells out of the record to say WHY the figures are
    worth asking about. A copy that drifts is a claim nothing executes."""

    ab = REPO_ROOT / "examples" / "validation" / "ab"
    flat = analyze_tree(ab / "reference")["totals_code_only"]
    ported = analyze_tree(ab / "reference_ports")["totals_code_only"]
    assert (flat["branch_points_in_effectful_modules"],
            ported["branch_points_in_effectful_modules"]) == (10, 1)
    assert (flat["instance_state_in_effectful_modules"],
            ported["instance_state_in_effectful_modules"]) == (7, 1)
    assert flat["effectful_calls"] == ported["effectful_calls"] == 3

    text = READING_PROMPT.read_text(encoding="utf-8")
    assert "| **10** | **1** |" in text and "| **7** | **1** |" in text
    # And the caution's "a ported tree measures LARGER" cells.
    assert (ported["modules"], ported["public_surface"], ported["code_lines"]) == (5, 26, 255)
    assert (flat["modules"], flat["public_surface"], flat["code_lines"]) == (1, 15, 122)
    assert "5 modules, 26 public surface and 255 code lines" in text
    assert "1, 15 and 122" in text


# ---------------------------------------------------------------------------
# 5. still nothing consumes it
# ---------------------------------------------------------------------------

#: Every place a consumer could hide. Wider than
#: `test_code_complexity.py::EXECUTABLE_SURFACES`, because FI-05 added files
#: under `examples/` and the obvious way to make this prompt convenient is a
#: script there that runs the instrument and renders the ask.
SEARCHED_TREES = (
    "scripts", "skill-scripts", "spec_double_compiler", "templates", "test_graph",
    "examples", "specs",
)


#: Dotted callables that would actually RUN the instrument rather than mention
#: it. Matched against the CALL'S FUNCTION, never against the source text of
#: the call: a call whose argument happens to be a page of markdown containing
#: the word "executable" is not an invocation, and matching text was how the
#: first draft of this test reproduced the very false positive it exists to
#: distinguish from a real read.
_INVOKERS = (
    "subprocess.run", "subprocess.call", "subprocess.check_call",
    "subprocess.check_output", "subprocess.Popen", "os.system", "os.popen",
    "os.execv", "runpy.run_path", "runpy.run_module", "importlib.import_module",
    "__import__", "exec", "eval",
)


def _dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _string_args_mention(call: ast.Call, needle: str) -> bool:
    for node in ast.walk(call):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if needle in node.value:
                return True
    return False


def _executable_readers() -> tuple[list[str], list[str]]:
    """`(executable readers, prose mentions)` of the produced-code instrument.

    The distinction is the point. The shipped
    `test_code_complexity.py::test_nothing_executable_reads_this_instrument`
    scans for the substring, and on the parent commit it is RED because one
    evidence-packet generator embeds the sentence "run
    `python3 scripts/code_complexity.py <target>`" in the markdown it writes
    for a judge. That is a mention, not a read -- and it IS PA-06-DF-05, carried
    out of the predecessor epic as issue #147: "the tripwire is a substring
    grep, so it cannot tell a mention from a gate". The shipped test is left
    exactly as it is, red, because a carried finding is not fixed inline by a
    ticket measuring something else.

    So this asks the harder question with the AST: does anything IMPORT the
    module, or hand its path to something that would run it?
    """
    instrument = (REPO_ROOT / "scripts" / "code_complexity.py").resolve()
    executable: list[str] = []
    prose: list[str] = []
    for tree in SEARCHED_TREES:
        root = REPO_ROOT / tree
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if path.resolve() == instrument or ".history" in path.parts:
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
            try:
                reads = _reads_instrument(text)
            except SyntaxError:
                executable.append(f"{rel} (unparseable -- cannot rule it out)")
                continue
            (executable if reads else prose).append(rel)
    return executable, prose


def _reads_instrument(text: str) -> bool:
    """Does this source IMPORT or RUN the instrument, as opposed to mention it?"""

    reads = False
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.Import):
            reads |= any("code_complexity" in a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            reads |= "code_complexity" in (node.module or "")
        elif isinstance(node, ast.Call):
            if _dotted(node.func) in _INVOKERS and _string_args_mention(
                node, "code_complexity"
            ):
                reads = True
    return reads


#: R1 for the scan above: inputs it must call READ, and inputs it must not.
#: A scan that cannot go red is not evidence that nothing consumes the
#: instrument -- it is silence shaped like evidence.
_READS = (
    "import scripts.code_complexity\n",
    "from scripts.code_complexity import analyze_tree\n",
    "import subprocess\nsubprocess.run(['python3', 'scripts/code_complexity.py', 'x'])\n",
    "import importlib\nimportlib.import_module('scripts.code_complexity')\n",
)
_MENTIONS = (
    '"""run `python3 scripts/code_complexity.py <target>` and paste it."""\n',
    "PAGE = 'read scripts/code_complexity.py output per the intuition page'\n"
    "open('x.md', 'w').write(PAGE)\n",
    "# code_complexity is a thermometer; nothing here reads it\n",
)


@pytest.mark.parametrize("source", _READS)
def test_the_consumer_scan_goes_red_on_a_real_read(source: str) -> None:
    assert _reads_instrument(source), (
        f"the scan misses a real consumer:\n{source}\nA scan that cannot go red proves "
        f"nothing about the absence of consumers."
    )


@pytest.mark.parametrize("source", _MENTIONS)
def test_the_consumer_scan_stays_green_on_a_mention(source: str) -> None:
    assert not _reads_instrument(source), (
        f"the scan calls a prose mention a consumer:\n{source}\nThat is PA-06-DF-05's "
        f"shape, where a tripwire failed a docstring mention and passed an aliased import."
    )


def test_nothing_executable_consumes_the_instrument_after_the_prompt_landed() -> None:
    """GOAL-instruments-can-fail's local signal, executable.

    The prompt tells the reader to run the shipped command and paste the
    output. A script that ran it for them would be the first thing in this
    toolchain to read a thermometer, and this names it if one appears.
    """

    executable, _ = _executable_readers()
    assert executable == [], (
        f"these RUN or IMPORT the produced-code instrument: {executable}. It reports; "
        f"nothing in the toolchain may consume it as a condition."
    )


def test_the_only_mentions_are_prose_and_they_are_named() -> None:
    """Silence and a pass are different claims: print what the scan found."""

    executable, prose = _executable_readers()
    assert not executable
    assert prose == ["specs/results/scorecards/ports-as-adapters/measure/"
                     "build_evidence_packets.py"], (
        f"the set of files MENTIONING the instrument changed: {prose}. Each must be "
        f"re-checked by hand -- a mention today is how a consumer arrives tomorrow."
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
