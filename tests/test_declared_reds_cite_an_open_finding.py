"""A declaration of deliberate redness must not outlive the finding it cites.

`CA-10-DF-15`, CONSUMED RATHER THAN ROUTED. The finding says two tests carried
`**DELIBERATELY RED (RM-06, group 2). DO NOT MAKE IT GREEN HERE**` in their
docstrings while being GREEN. `SS-06` re-measured it at `8dd0442` and the
population is **three, not two** -- `test_the_shipped_rh5_demonstration_still_
goes_red` carries the same declaration and the same citation, and the finding
missed it. All three cite `RM-06-DF-02`, whose ledger disposition is `settled`
and whose subject row in `specs/results/scorecards/INSTRUMENT-LOG.toml` records
`settled_by = "RM-04"`. `audit` reports **0 violations, exit 0** over this
repository. The declarations describe a violation that no longer exists.

WHY THIS FILE EXISTS AND NOT JUST A DOCSTRING EDIT. `planning_rules.
consumption_is_changing_what_the_substrate_checks`: filing a finding routes it;
it does not change what the substrate checks. `CA-10-DF-15` names a MECHANISM --
*a declaration of deliberate redness that outlives the red* -- and the reason it
survived from `RM-06` to `CA-10` to here is that **nothing computed it**. The
declarations are prose, the dispositions are data, and no instrument ever put
the two beside each other. This does.

WHAT IT CHECKS, AND WHAT IT DELIBERATELY DOES NOT. For every test in `tests/`
that declares itself red, at least one finding id it cites must be NON-TERMINAL
in the ledger (`open` or `carried`, per `scripts/disposition.py`'s own
vocabulary -- not a second opinion about it). That is a NECESSARY condition and
it is not a sufficient one: it catches *the finding this declaration rests on
was settled*, and it does NOT catch *the test is green for some other reason*.
Establishing THAT costs a subprocess run of every declared-red test -- the
`rh5` one alone takes five and a half minutes -- and a check nobody can afford
to run is a check nobody runs. The limit is stated here rather than discovered
later.

NOT A GATE OVER ANY SUBJECT PROGRAM. It reads this repository's own test text
and this repository's own ledger, which is the population
`planning_rules.the_static_gates_doctrine_as_adjudicated` explicitly permits.
It refuses nothing about an adopter's code.

ABSENT INPUT (`R1` as extended by `SS-02`): the correct answer to "I found no
declarations" is a REFUSAL, never "all clear". A recogniser that silently
matches nothing reports green forever, which is the same signature defect as
`score_tools._finding_ids` answering "read nothing" with "found nothing" --
and it is the exact shape `SS-06` was chartered to remove. `test_the_recogniser
_is_not_matching_nothing` is that refusal.
"""
from __future__ import annotations

import ast
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import disposition as D  # noqa: E402

TESTS_DIR = ROOT / "tests"

#: The forms this repository has actually used to declare a test red. Matched
#: case-insensitively over the whole function source, because the declaration
#: has appeared in a docstring AND in an assertion message on the same test.
DECLARATION_FORMS = ("deliberately red", "deliberate red", "expected red",
                     "declared red", "this test is red on purpose")

#: THE WITHDRAWAL MARKER, and it is a TOKEN rather than a phrase on purpose.
#:
#: `SS-06-DF-06`, found by the independent reviewer of PR #286 and not by me. The
#: first version of this file matched `DECLARATION_FORMS` as a lowercase substring
#: over the whole function source -- so a docstring saying *"this USED TO declare
#: itself red, here is when the red was settled and by what"* still counted as a
#: LIVE declaration. The three corrected `test_score_tools.py` docstrings passed
#: only because they now cite `CA-10-DF-15`, which is still `carried`. Flipping it
#: to `repaired` in a throwaway ledger turns two named tests RED -- and
#: `SS-06-DF-03` is filed `repaired`, so **this check went red exactly when the
#: next ticket did the right thing.** A time bomb for `SS-05` and `SS-08`.
#:
#: THE CHECK COULD NOT TELL A DECLARATION FROM A QUOTATION OF ONE, which is
#: `SS-06-DF-02`'s class -- a recogniser reading its subject's prose as its
#: subject's state -- third instance in this ticket, this time inside the check
#: written to police the class.
#:
#: A phrase cannot fix a phrase-matching bug, so this is a literal token no
#: ordinary prose produces. And it is NOT a mute button: a withdrawal must be
#: CORROBORATED by a cited finding whose disposition is terminal, so it cannot be
#: used to silence a declaration whose subject is still live.
WITHDRAWN_MARKER = "SS-06:WITHDRAWN-DECLARATION"

#: A finding id as this project writes them: `RM-06-DF-02`, `CA-10-DF-15`,
#: `SS-00-DF-01`.
FINDING_ID = re.compile(r"\b[A-Z]{2,3}-\d{2}-DF-\d{2}\b")


class Declaration:
    def __init__(self, path: pathlib.Path, name: str, cited: set[str],
                 withdrawn: bool = False) -> None:
        self.path = path
        self.name = name
        self.cited = cited
        self.withdrawn = withdrawn

    @property
    def where(self) -> str:
        return f"{self.path.relative_to(ROOT)}::{self.name}"

    def __repr__(self) -> str:  # pragma: no cover - failure messages only
        state = "WITHDRAWN" if self.withdrawn else "live"
        return f"{self.where} [{state}] cites {sorted(self.cited) or 'NOTHING'}"


def declarations_in(text: str, path: pathlib.Path) -> list[Declaration]:
    """Every `test_*` in `text` that mentions being red, with the ids it cites.

    Reads the function's own source segment, so a declaration in the docstring
    and a declaration in an assertion message are both seen, and a declaration
    in a NEIGHBOURING test is not attributed here. Whether the mention is a LIVE
    declaration or a QUOTATION of a withdrawn one is decided by
    `WITHDRAWN_MARKER`, structurally -- never by trying to read the prose.
    """
    found: list[Declaration] = []
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue
        source = ast.get_source_segment(text, node) or ""
        lowered = source.lower()
        if not any(form in lowered for form in DECLARATION_FORMS):
            continue
        found.append(Declaration(path, node.name,
                                 set(FINDING_ID.findall(source)),
                                 withdrawn=WITHDRAWN_MARKER in source))
    return found


def stale(declaration: Declaration, dispositions: dict[str, str]) -> str | None:
    """Why this declaration no longer stands, or `None` if it does.

    THE PREDICATE, and the only place the verdict is computed. `TERMINAL` and
    `DEFERRAL` come from `scripts/disposition.py` so this file cannot drift into
    a second opinion about what "closed" means.

    A LIVE declaration stands while at least one finding it cites is still live.
    A WITHDRAWN one is the opposite requirement: it must cite a finding that is
    CLOSED, because that closure is the whole evidence that the withdrawal was
    earned. Both directions are asserted, so the marker cannot silence anything.
    """
    if not declaration.cited:
        return ("mentions being red and cites no finding id at all -- a "
                "declaration with nothing behind it is a hunch, and so is a "
                "withdrawal with nothing behind it")
    unknown = sorted(i for i in declaration.cited if i not in dispositions)
    if unknown and len(unknown) == len(declaration.cited):
        return (f"cites {unknown}, and no such row is in the ledger -- the "
                "declaration points at nothing")
    live = sorted(i for i in declaration.cited
                  if dispositions.get(i) in D.DEFERRAL | {"open"})
    closed = sorted(i for i in declaration.cited
                    if dispositions.get(i) in D.TERMINAL)
    if declaration.withdrawn:
        if closed:
            return None
        return (f"carries {WITHDRAWN_MARKER} but every finding it cites is "
                f"still live ({sorted(declaration.cited)}). A withdrawal has to "
                f"be corroborated by a settled finding; the marker is not a way "
                f"to stop a live declaration being checked (`SS-06-DF-06`)")
    if live:
        return None
    shown = sorted(f"{i}={dispositions.get(i, 'ABSENT')}"
                   for i in declaration.cited)
    return (f"every finding it cites is closed ({shown}), so the red it "
            f"declares was settled and the declaration was not. If the "
            f"declaration WAS withdrawn, say so with {WITHDRAWN_MARKER}")


@pytest.fixture(scope="module")
def dispositions() -> dict[str, str]:
    path = D.resolve_ledger(ROOT / D.LEDGER, explicit=False)
    rows = D.load(path)
    # The absent-input half: a ledger that resolved to nothing must refuse, not
    # report every declaration clean. `SS-00-DF-01` is exactly this failure in
    # the other direction and every audit figure in this epic is caveated by it.
    assert len(rows) > 200, (
        f"the ledger at {path} carries {len(rows)} rows; this check cannot "
        "decide anything about a declaration against a ledger that small, and "
        "reporting the declarations clean would be worse than no check"
    )
    return {str(r["id"]): str(r.get("disposition", "")) for r in rows}


@pytest.fixture(scope="module")
def declared() -> list[Declaration]:
    out: list[Declaration] = []
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        if path.name == pathlib.Path(__file__).name:
            continue  # this file's own prose is not a declaration
        out.extend(declarations_in(path.read_text(encoding="utf-8"), path))
    return out


def test_the_recogniser_is_not_matching_nothing(declared):
    """REFUSE rather than report all-clear when the population is empty.

    A recogniser that matches nothing passes every downstream assertion
    vacuously and forever. That is `CA-10-DF-14`'s shape applied to this file,
    and it is the failure this whole ticket exists to remove, so it is refused
    here rather than trusted.

    BOTH populations are refused when empty, not just the total. A tree with
    only withdrawn quotations left would satisfy a bare `assert declared` while
    nothing live was being checked at all.
    """
    assert declared, (
        "no test in tests/ mentions being red. Either every declaration was "
        f"removed -- in which case DELETE THIS FILE -- or the recogniser "
        f"({DECLARATION_FORMS}) stopped matching the form this repository "
        "writes. It must not silently report clean."
    )
    assert [d for d in declared if not d.withdrawn], (
        "every mention of redness in tests/ now carries "
        f"{WITHDRAWN_MARKER}, so this check has no LIVE declaration left to "
        "adjudicate and its central assertion is vacuous. Delete this file, or "
        "find out why the deliberate reds stopped declaring themselves."
    )


def test_every_declaration_names_a_finding(declared):
    """A declared red with no finding id behind it cannot be adjudicated."""
    naked = [d.where for d in declared if not d.cited]
    assert naked == [], naked


def test_no_declaration_of_deliberate_redness_outlives_its_finding(declared, dispositions):
    """THE CHECK. `CA-10-DF-15`, computed instead of described."""
    verdicts = [(d.where, why) for d in declared
                if (why := stale(d, dispositions)) is not None]
    assert verdicts == [], (
        "stale declarations of deliberate redness:\n"
        + "\n".join(f"  {where}: {why}" for where, why in verdicts)
    )


def test_it_refuses_a_real_stale_declaration(dispositions):
    """`R1`: a demonstrated FAILING input, built from the real ledger.

    Not a fixture id and not a hand-written disposition: the terminal id below
    is SELECTED FROM THE LEDGER AT RUN TIME, so nothing here is fitted to a
    known answer (`MF-020`). If the ledger ever contains no terminal row this
    skips and says so rather than passing on an empty selection.
    """
    terminal = sorted(i for i, d in dispositions.items() if d in D.TERMINAL)
    if not terminal:
        pytest.skip("no terminal-disposition row exists in the ledger, so this "
                    "demonstration has no real stale citation to build from")
    text = (
        'def test_example():\n'
        f'    """**DELIBERATELY RED.** See `{terminal[0]}`."""\n'
        '    assert False\n'
    )
    found = declarations_in(text, TESTS_DIR / "synthetic.py")
    assert [d.name for d in found] == ["test_example"]
    why = stale(found[0], dispositions)
    assert why is not None and "was settled and the declaration was not" in why


def test_a_withdrawn_declaration_survives_its_finding_being_disposed(dispositions):
    """`SS-06-DF-06`, pinned in the direction that produced the time bomb.

    The three `test_score_tools.py` docstrings QUOTE a declaration they say was
    withdrawn. They cite `CA-10-DF-15` and `RM-06-DF-02`, and `SS-06-DF-03` is
    filed `repaired` -- so the moment `CA-10-DF-15` is disposed, every id they
    cite is closed. Before the marker existed that turned two named tests RED
    when the next ticket did the right thing.
    """
    terminal = sorted(i for i, d in dispositions.items() if d in D.TERMINAL)
    if not terminal:
        pytest.skip("no terminal-disposition row exists in the ledger, so a "
                    "corroborated withdrawal cannot be built from real data")
    text = (
        'def test_example():\n'
        f'    """Was **DELIBERATELY RED**; withdrawn. {WITHDRAWN_MARKER}.\n'
        f'    Settled, see `{terminal[0]}`."""\n'
        '    assert True\n'
    )
    found = declarations_in(text, TESTS_DIR / "synthetic.py")
    assert len(found) == 1 and found[0].withdrawn, found
    assert stale(found[0], dispositions) is None


def test_the_withdrawal_marker_cannot_silence_a_live_declaration(dispositions):
    """The other direction, so the marker is evidence and not a mute button.

    A withdrawal whose cited findings are ALL still live is refused: nothing in
    the record says the red it describes was settled, so the withdrawal is
    asserted rather than earned.
    """
    live = sorted(i for i, d in dispositions.items() if d in D.DEFERRAL | {"open"})
    if not live:
        pytest.skip("every row in the ledger is disposed -- there is no live "
                    "finding to build an unearned withdrawal from")
    text = (
        'def test_example():\n'
        f'    """**DELIBERATELY RED**, and withdrawn. {WITHDRAWN_MARKER}.\n'
        f'    See `{live[0]}`."""\n'
        '    assert False\n'
    )
    found = declarations_in(text, TESTS_DIR / "synthetic.py")
    why = stale(found[0], dispositions)
    assert why is not None and "is not a way" in why, why


def test_it_accepts_a_real_standing_declaration(dispositions):
    """The half that stops the rule being a constant.

    A predicate that refused every declaration would pass the test above and
    say nothing. `RM-06-DF-01` -- the `same_tag_control` red -- is `open`, and
    a declaration citing a live finding must STAND.
    """
    live = sorted(i for i, d in dispositions.items() if d in D.DEFERRAL | {"open"})
    if not live:
        pytest.skip("every row in the ledger is disposed -- the backlog is "
                    "clear and this demonstration has nothing left to accept")
    text = (
        'def test_example():\n'
        f'    """**DELIBERATELY RED.** See `{live[0]}`."""\n'
        '    assert False\n'
    )
    found = declarations_in(text, TESTS_DIR / "synthetic.py")
    assert stale(found[0], dispositions) is None


def test_a_declaration_with_no_citation_is_refused(dispositions):
    """The third branch, exercised rather than merely written."""
    text = ('def test_example():\n'
            '    """**DELIBERATELY RED.** Trust me."""\n'
            '    assert False\n')
    found = declarations_in(text, TESTS_DIR / "synthetic.py")
    why = stale(found[0], dispositions)
    assert why is not None and "cites no finding id at all" in why


def test_the_recogniser_does_not_reach_into_a_neighbouring_test():
    """Attribution: a declaration belongs to the function that carries it.

    Read line-wise, the ids of an adjacent test would be swept in and a stale
    declaration could be certified by its neighbour's live citation.
    """
    text = (
        'def test_declared():\n'
        '    """**DELIBERATELY RED.** No id here."""\n'
        '    assert False\n'
        '\n'
        'def test_neighbour():\n'
        '    """Ordinary. See `RM-06-DF-01`."""\n'
        '    assert True\n'
    )
    found = declarations_in(text, TESTS_DIR / "synthetic.py")
    assert [d.name for d in found] == ["test_declared"]
    assert found[0].cited == set()


def test_an_empty_module_is_no_declarations_not_a_clean_bill():
    """Absent input, third shape: nothing to read is not the same as nothing wrong.

    `declarations_in` returns an empty LIST, and the empty list is what
    `test_the_recogniser_is_not_matching_nothing` refuses on. The two answers
    stay distinguishable, which is the `set[str] -> set[str] | None` lesson
    `planning_rules.r1_now_requires_an_absent_input` names as the worked shape.
    """
    assert declarations_in("", TESTS_DIR / "synthetic.py") == []
    assert declarations_in("def test_x():\n    assert True\n",
                           TESTS_DIR / "synthetic.py") == []
