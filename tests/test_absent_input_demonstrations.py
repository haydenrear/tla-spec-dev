"""SS-02. R1 EXTENDED: WHAT AN INSTRUMENT ANSWERS WHEN THE INPUT IS NOT THERE.

`R1` requires a demonstrated FAILING input on a real subject. It does not
require a demonstrated ABSENT one, and `CA-10`'s sweep says that single gap is
why all 48 instances of the absent-input class shipped: every one of them
satisfied `R1` IN FULL and still answered PASS to the question it was built to
refuse.

`score_tools.py absent-input` is that extension executed rather than written
down, over this repository's OWN instrument register. This file is the check's
own `R1`, and it is deliberately four kinds of test:

1. **THE REFUSAL ON A REAL INSTRUMENT, FAILING BEFORE AND PASSING AFTER.** The
   subject is `scorecard-audit` -- `score_tools.py audit`, the instrument whose
   `_finding_ids` signature change is the worked shape of the whole class. With
   its `[instrument.absent_input]` block stripped the check REFUSES it by name;
   with the block as shipped it passes, and all three states are staged and RUN
   rather than read.

2. **THE THREE STATES, AND WHY TWO IS NOT ENOUGH.** `CA-10-DF-11` repaired the
   ABSENT ledger. `SS-01` repaired the WRONG one. An independent reviewer then
   handed the result a ledger that EXISTED and named nothing and got 14
   confident fabrication accusations against real citations (`SS-01-DF-04`). A
   contract declaring only absent-and-present is refused here.

3. **THE SELF-REFERENTIAL TRAP.** The check is itself an instrument that can be
   handed an absent input. An absent register, a zero-byte one, one that does
   not parse, one that parses and declares no instruments, a `--only` matching
   nothing: each is answered UNDECIDED with its own message, each exits 2, and
   NONE of them is 0. If any answered PASS this would be the 49th instance of
   the class, shipped inside the fix for the class.

4. **THE NON-VACUITY GUARDS.** FI-01's lesson: a harness that passes whatever
   the instrument does is worth nothing. The check is shown REPORTING a
   contract that stopped reproducing, REFUSING `answer = "pass"`, and REFUSING
   two states it cannot tell apart -- so a green run means something.

WHAT THIS FILE DOES NOT DO: repair a single instance of the class. `SS-05` owns
the repairs and `SS-08` measures what is left; a ticket that shrank the class
while measuring it would leave the epic with no measurement.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path, PurePosixPath

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCORE_TOOLS = REPO_ROOT / "examples" / "validation" / "scorecards" / "score_tools.py"
REGISTER = REPO_ROOT / "examples" / "validation" / "instruments" / "instruments.toml"

#: The row whose absent-input contract is the worked shape of the class.
SUBJECT = "scorecard-audit"

#: The check's own row -- three states, three distinct messages, exit 2 on all
#: three. Cheap to execute (0.3s), so it is the one this file runs end to end.
SELF = "absent-input-check"


def run_check(*argv: str, registry: Path | None = None) -> subprocess.CompletedProcess:
    command = [sys.executable, str(SCORE_TOOLS), "absent-input", *argv]
    if registry is not None:
        command += ["--registry", str(registry)]
    return subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True,
                          timeout=900)


@pytest.fixture(scope="module")
def register() -> dict:
    return tomllib.loads(REGISTER.read_text(encoding="utf-8"))


def rewrite_register(tmp_path: Path, transform) -> Path:
    """A copy of the REAL register with one edit -- never a hand-built fixture.

    `R1` says a demonstrated failing input is on a real subject. Every negative
    below starts from the shipped register and removes or corrupts exactly one
    thing, so the thing being demonstrated is the only difference between the
    two runs.
    """

    import re

    text = REGISTER.read_text(encoding="utf-8")
    edited = transform(text)
    assert edited != text, "the transform changed nothing -- it demonstrates nothing"
    target = tmp_path / "instruments.toml"
    target.write_text(edited, encoding="utf-8")
    # Parse it back: a negative that does not parse would be caught by the
    # register reader's `unreadable` branch and would prove nothing about the
    # contract clause it was written for.
    assert isinstance(tomllib.loads(edited).get("instrument"), list)
    assert re.search(r"\[\[instrument\]\]", edited)
    return target


def strip_block(text: str, header: str) -> str:
    """Delete one `[instrument.absent_input...]` block from the register text.

    Cuts from the header line to the next line that starts a table at the same
    or a shallower indent, which is how TOML nesting ends.
    """

    lines = text.splitlines(keepends=True)
    start = next(i for i, line in enumerate(lines) if line.strip() == header)
    indent = len(lines[start]) - len(lines[start].lstrip())
    end = start + 1
    while end < len(lines):
        stripped = lines[end].lstrip()
        if stripped.startswith("[") and (
            len(lines[end]) - len(stripped)
        ) <= indent:
            break
        if stripped.startswith("[[instrument]]"):
            break
        end += 1
    return "".join(lines[:start] + lines[end:])


# ---------------------------------------------------------------------------
# 1. The refusal on a real instrument: failing before, passing after
# ---------------------------------------------------------------------------


def test_the_check_REFUSES_a_real_instrument_that_has_no_absent_input_case(tmp_path):
    """FAILING BEFORE. The subject is `score_tools.py audit`, not a fixture.

    This is the state the whole register was in before this ticket: 55 of 55
    instruments had a demonstrated failing input, a demonstrated passing input,
    and nothing at all about an input that is not there.
    """

    registry = rewrite_register(
        tmp_path, lambda text: strip_block(text, "[instrument.absent_input]")
    )
    done = run_check("--contract-only", "--only", SUBJECT, registry=registry)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "NO CONTRACT" in done.stdout
    assert SUBJECT in done.stdout
    assert "no `[instrument.absent_input]` block" in done.stdout


def test_the_check_PASSES_the_same_instrument_with_all_three_states_executed():
    """PASSING AFTER, and the three states are RUN, not read.

    Three staged trees, three real invocations of `score_tools.py audit`, and
    the answer compared against what the register declares. It takes about 80
    seconds, which is why it is one test and not three.
    """

    done = run_check("--only", SUBJECT)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "SATISFIED" in done.stdout
    assert "executed     yes" in done.stdout
    assert "Every selected instrument carries a three-state absent-input" in done.stdout


def test_the_subject_answers_UNDECIDED_and_never_PASS_in_all_three_states(register):
    """The rule itself, read off the contract that was just executed.

    `pass` is not an available answer. This asserts the DECLARED answers; the
    test above asserts the instrument actually produces them.
    """

    contract = next(r for r in register["instrument"] if r["id"] == SUBJECT)["absent_input"]
    answers = {state: contract[state]["answer"] for state in ("absent", "unreadable", "empty")}
    assert set(answers) == {"absent", "unreadable", "empty"}
    assert set(answers.values()) <= {"refusal", "undecided"}
    assert "pass" not in set(answers.values())


# ---------------------------------------------------------------------------
# 2. Three states, not two -- SS-01-DF-04 consumed into the rule
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("state", ["absent", "unreadable", "empty"])
def test_a_contract_that_declares_only_two_states_is_REFUSED(tmp_path, state):
    """`SS-01-DF-04`, executed.

    A repair that distinguishes ABSENT from PRESENT and stops there has moved
    the false PASS to a rarer input, not removed it -- measured end to end on
    `587d46c`, where `findings: []`, a zero-byte file and malformed YAML each
    produced 14 fabrication accusations against real citations. Each of the
    three states is dropped in turn, because a rule that only noticed a missing
    `empty` would be satisfied by a contract missing `absent`.
    """

    registry = rewrite_register(
        tmp_path, lambda text: strip_block(text, f"[instrument.absent_input.{state}]")
    )
    done = run_check("--contract-only", "--only", SUBJECT, registry=registry)
    assert done.returncode == 1, done.stdout + done.stderr
    assert f"`{state}`: no demonstration and no `unreachable` reason" in done.stdout
    assert "INCOMPLETE" in done.stdout
    for other in {"absent", "unreadable", "empty"} - {state}:
        assert f"`{other}`: no demonstration" not in done.stdout


# ---------------------------------------------------------------------------
# 2a. `unreachable`: a reason is not a demonstration -- SS-02-DF-05
# ---------------------------------------------------------------------------
#
# THE HIGHEST-VALUE THING AN INDEPENDENT REVIEWER FOUND IN PR #284, AND IT WAS
# INSIDE THIS CHECK. `unreachable = "<reason>"` is documented in three places as
# "counted and printed, NEVER as satisfied", and the code fell through to
# SATISFIED anyway. One row, three states, each waived with the free-text reason
# "cannot be constructed", nothing else -- SATISFIED, counted 1 under `contract
# EXECUTED and holding`, footer claiming "every state reproduced", exit 0, and
# ZERO demonstrations run. Sub-shape 7 of the class this file exists to close,
# inside the fix for the class. It had NO TEST; that is why it shipped.

WAIVED_ROW = """
schema_version = 1

[registry]
id = "one row, three excuses"

[[instrument]]
id = "all-three-waived"
name = "an instrument that declares every state impossible"
paths = []
family = "measurement"
watches = "nothing, demonstrably"
verdict_surface = "none"
classification = "demonstrated-can-fail"
no_failing_demonstration = "this is a fixture for SS-02-DF-05"

  [instrument.absent_input.absent]
  unreachable = "cannot be constructed"

  [instrument.absent_input.unreadable]
  unreachable = "cannot be constructed"

  [instrument.absent_input.empty]
  unreachable = "cannot be constructed"
"""


def test_a_WAIVED_state_can_never_buy_SATISFIED(tmp_path):
    """`SS-02-DF-05`. The regression that lets the whole check mean something.

    Three free-text excuses used to be worth a green run. They are now their own
    verdict, their own bucket, their own printed section, and exit 2 -- because
    nothing was refused and nothing was demonstrated either.
    """

    registry = tmp_path / "instruments.toml"
    registry.write_text(WAIVED_ROW, encoding="utf-8")
    done = run_check(registry=registry)
    out = done.stdout

    assert done.returncode == 2, out + done.stderr
    # The VERDICT CELL, not the whole report: the report's own prose explains
    # what a waived row is not, and grepping the page for the word would pass on
    # that sentence. Assert the cell the reader acts on.
    verdict = next(line for line in out.splitlines()
                   if line.startswith("all-three-waived "))
    assert "WAIVED (3 of 3)" in verdict
    assert "SATISFIED" not in verdict
    assert "every state reproduced" not in out
    assert "contract EXECUTED and holding               0" in out
    assert "contract with a WAIVED state, nothing run    1" in out
    assert "states declared unreachable, with a reason  3" in out
    assert "A reason is not a demonstration" in out
    # The section that makes the excuse readable rather than merely counted.
    assert "STATES DECLARED UNREACHABLE" in out
    assert "cannot be constructed" in out


def test_one_WAIVED_state_is_enough_to_stop_SATISFIED(tmp_path):
    """Not only the all-waived case.

    A row that demonstrates two states properly and waives the third is the
    shape a later ticket will actually write, and it is the one where a
    fall-through to SATISFIED would be hardest to notice.
    """

    registry = rewrite_register(
        tmp_path,
        lambda text: text.replace(
            '    [instrument.absent_input.empty]\n    summary = "the ledger parses',
            '    [instrument.absent_input.empty]\n'
            '    unreachable = "SS-02 test: pretend this one cannot be built"\n'
            '    summary = "the ledger parses',
            1,
        ),
    )
    done = run_check("--only", SUBJECT, "--state", "absent", "--state", "empty",
                     registry=registry)
    out = done.stdout
    assert done.returncode == 2, out + done.stderr
    verdict = next(line for line in out.splitlines() if line.startswith(f"{SUBJECT} "))
    assert "WAIVED (1 of 3)" in verdict
    assert "SATISFIED" not in verdict


def test_the_bucket_identity_holds_with_a_waived_row(tmp_path):
    """`waived_rows` is IN the sum. Being outside it is how those rows were
    counted as satisfied in the first place: the report printed an identity that
    the buckets did not actually satisfy, and nothing compared them."""

    registry = tmp_path / "instruments.toml"
    registry.write_text(WAIVED_ROW, encoding="utf-8")
    done = run_check("--format", "json", registry=registry)
    report = json.loads(done.stdout.split("\nNo problem was found")[0])
    counts = report["counts"]
    buckets = ("satisfied", "declared_not_executed", "partial", "waived_rows",
               "without_contract", "refused")
    assert sum(counts[b] for b in buckets) == report["selected"] == 1
    assert counts["waived_rows"] == 1
    assert counts["satisfied"] == 0


# ---------------------------------------------------------------------------
# 2b. `expect_exit` is mandatory -- SS-02-DF-06
# ---------------------------------------------------------------------------


def test_a_state_that_declares_no_expect_exit_is_REFUSED(tmp_path):
    """`SS-02-DF-06`. The rule called mandatory was opt-in.

    `_absent_judge` compares the exit code only when the contract declares one,
    and the UNDECIDED-and-exits-0 rule read the DECLARED code -- so DELETING ONE
    LINE turned off exit-code checking AND the rule that depends on it, and a
    contract answering `undecided` while exiting 0 reported SATISFIED. Found by
    an independent reviewer of PR #284.
    """

    registry = rewrite_register(
        tmp_path,
        lambda text: text.replace("\n    expect_exit = 0\n", "\n", 1),
    )
    done = run_check("--contract-only", "--only", SUBJECT, registry=registry)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "declares no `expect_exit`" in done.stdout
    assert "An omitted exit code is not a permissive one" in done.stdout


def test_the_UNDECIDED_and_exits_zero_rule_reads_what_HAPPENED(tmp_path):
    """The other half of `SS-02-DF-06`, and the one a static check cannot do.

    A contract may declare `expect_exit = 1` and the instrument may exit 0. The
    declaration would then satisfy the static rule while the run produces
    exactly the false PASS the rule exists to name, so the rule is applied to the
    OBSERVED code as well. Here the declared code is moved to 1 and the
    `exit_code_cannot_carry_the_answer` declaration removed; `audit` still exits
    0, so BOTH the exit-code comparison and the observed rule must fire.
    """

    def transform(text: str) -> str:
        text = text.replace("\n    expect_exit = 0\n", "\n    expect_exit = 1\n", 1)
        return text.replace("exit_code_cannot_carry_the_answer", "note_about_exit", 1)

    registry = rewrite_register(tmp_path, transform)
    done = run_check("--only", SUBJECT, "--state", "absent", registry=registry)
    out = done.stdout
    assert done.returncode == 1, out + done.stderr
    assert "exit 0, declared 1" in out
    assert "OBSERVED exit 0 while answering `undecided`" in out


def test_a_register_row_with_no_id_is_UNDECIDED_and_not_a_TRACEBACK(tmp_path):
    """Reported by the reviewer of PR #284 while reproducing `SS-02-DF-05`.

    `entry["id"]` on a row that has none died with `KeyError` and a traceback. A
    traceback is not one of the three answers, and "the register is unreadable
    as a register" is an absent-input case for this check like any other.
    """

    registry = tmp_path / "instruments.toml"
    registry.write_text(
        'schema_version = 1\n\n[registry]\nid = "x"\n\n[[instrument]]\n'
        'name = "a row with no id"\nfamily = "measurement"\n',
        encoding="utf-8",
    )
    done = run_check(registry=registry)
    assert done.returncode == 2, done.stdout + done.stderr
    assert "[unreadable]" in done.stdout
    assert "declares no `id`" in done.stdout
    assert "Traceback" not in done.stdout + done.stderr


def test_states_the_instrument_CANNOT_TELL_APART_must_be_declared(tmp_path):
    """Found by EXECUTION, not by reading the TOML.

    `score_tools.py audit` answers `unreadable` and `empty` with the identical
    line, because `_finding_ids` reads ids with a regex and never parses the
    file. That is defensible and it is DECLARED. Remove the declaration and the
    check refuses, which is what stops the next instrument from collapsing two
    states quietly.
    """

    registry = rewrite_register(
        tmp_path,
        lambda text: strip_block(text, "[[instrument.absent_input.indistinguishable]]"),
    )
    done = run_check("--only", SUBJECT, "--state", "unreadable", "--state", "empty",
                     registry=registry)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "INDISTINGUISHABLE" in done.stdout
    assert "'unreadable', 'empty'" in done.stdout or "unreadable" in done.stdout


def test_an_UNDECIDED_answer_that_exits_zero_must_say_so(tmp_path):
    """The half an exit code cannot carry.

    All three of `scorecard-audit`'s states exit 0 with `0 violation(s)`,
    because `UNVERIFIED` deliberately does not increment the violation count. A
    caller that reads the exit code and not the text gets a PASS over a tree
    with no ledger in it. That is declared on every one of the three states, and
    removing the declaration is refused.
    """

    registry = rewrite_register(
        tmp_path,
        lambda text: text.replace("exit_code_cannot_carry_the_answer", "note_about_exit", 1),
    )
    done = run_check("--contract-only", "--only", SUBJECT, registry=registry)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "answers UNDECIDED and exits 0" in done.stdout


def test_PASS_is_not_an_available_answer(tmp_path):
    """A contract may not declare that PASS is the right answer to an absent
    input. That is the entire rule, and it is executed."""

    registry = rewrite_register(
        tmp_path,
        # The INDENTED declaration, not the first occurrence of the string: the
        # register's own preamble quotes `answer = "undecided"` while explaining
        # the rule, and a transform that edited the prose would have produced a
        # green run and proved nothing. Caught by this test failing.
        lambda text: text.replace('\n    answer = "undecided"\n',
                                  '\n    answer = "pass"\n', 1),
    )
    done = run_check("--contract-only", "--only", SUBJECT, registry=registry)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "'pass'" in done.stdout
    assert "not one of them" in done.stdout


# ---------------------------------------------------------------------------
# 3. The self-referential trap: what does the check answer?
# ---------------------------------------------------------------------------


def test_the_check_is_UNDECIDED_on_an_ABSENT_register(tmp_path):
    done = run_check(registry=tmp_path / "nothing-here.toml")
    assert done.returncode == 2, done.stdout + done.stderr
    assert "[absent]" in done.stdout
    assert "no instrument register at" in done.stdout
    assert "SATISFIED" not in done.stdout


def test_the_check_is_UNDECIDED_on_a_ZERO_BYTE_register(tmp_path):
    """`tomllib` parses a zero-byte file into `{}` without complaint.

    So "there is nothing here" and "this reads and declares nothing" arrive at
    the same place unless they are separated on the way in -- which is the class
    itself, one layer up, inside the reader that checks for the class.
    """

    empty = tmp_path / "instruments.toml"
    empty.write_text("", encoding="utf-8")
    done = run_check(registry=empty)
    assert done.returncode == 2, done.stdout + done.stderr
    assert "[unreadable]" in done.stdout
    assert "is EMPTY (0 byte(s))" in done.stdout


def test_the_check_is_UNDECIDED_on_a_register_that_DOES_NOT_PARSE(tmp_path):
    broken = tmp_path / "instruments.toml"
    broken.write_text('[[instrument]\nid = "unclosed\n', encoding="utf-8")
    done = run_check(registry=broken)
    assert done.returncode == 2, done.stdout + done.stderr
    assert "[unreadable]" in done.stdout
    assert "DOES NOT PARSE" in done.stdout


def test_the_check_is_UNDECIDED_on_a_register_that_declares_NO_INSTRUMENTS(tmp_path):
    """READ AND GENUINELY EMPTY -- the third state, on the check itself."""

    hollow = tmp_path / "instruments.toml"
    hollow.write_text('schema_version = 1\n\n[registry]\nid = "nothing"\n', encoding="utf-8")
    done = run_check(registry=hollow)
    assert done.returncode == 2, done.stdout + done.stderr
    assert "[empty]" in done.stdout
    assert "PARSES AND DECLARES 0" in done.stdout
    assert "seventh sub-shape" in done.stdout


def test_the_check_is_UNDECIDED_when_every_row_is_not_an_instrument(tmp_path):
    """A register full of rows and no instruments in it.

    `family = "not-an-instrument"` is how a checked-and-rejected candidate stays
    on the record. A register where EVERY row is one has nothing to ask, and
    reporting `0 of 0 satisfied` over it is the same defect as reporting it over
    an empty file.
    """

    only_non = tmp_path / "instruments.toml"
    only_non.write_text(
        'schema_version = 1\n\n[registry]\nid = "x"\n\n[[instrument]]\n'
        'id = "a"\nname = "a"\nfamily = "not-an-instrument"\n'
        'classification = "not-an-instrument"\nwatches = "nothing"\n'
        'verdict_surface = "none"\nno_failing_demonstration = "not an instrument"\n',
        encoding="utf-8",
    )
    done = run_check(registry=only_non)
    assert done.returncode == 2, done.stdout + done.stderr
    assert "EVERY ONE is" in done.stdout
    assert "SATISFIED" not in done.stdout


def test_the_check_is_UNDECIDED_when_only_selects_nothing():
    """`CA-10-DF-24` / `demonstrate.py:505`, consumed rather than repaired.

    A `--only` that matches no instrument reports *"Every declared
    demonstration reproduced."* and exits 0 in the sibling runner. That instance
    belongs to `SS-05`; what belongs here is not repeating it.
    """

    done = run_check("--only", "no-such-instrument-anywhere")
    assert done.returncode == 2, done.stdout + done.stderr
    assert "selected 0 of" in done.stdout
    assert "seventh sub-shape" in done.stdout


def test_the_four_UNDECIDED_answers_are_pairwise_DISTINGUISHABLE(tmp_path):
    """The rule the check imposes on others, imposed on the check.

    Four different reasons to be undecided must not print the same sentence --
    that is exactly the collapse `SS-01-DF-04` found one layer down, and it
    would be worse here because this is the instrument that reports it.
    """

    absent = tmp_path / "gone.toml"
    zero = tmp_path / "zero.toml"
    zero.write_text("", encoding="utf-8")
    broken = tmp_path / "broken.toml"
    broken.write_text('[[instrument]\n', encoding="utf-8")
    hollow = tmp_path / "hollow.toml"
    hollow.write_text('[registry]\nid = "x"\n', encoding="utf-8")

    answers = {}
    for name, path in (("absent", absent), ("zero", zero),
                       ("broken", broken), ("hollow", hollow)):
        done = run_check(registry=path)
        assert done.returncode == 2
        answers[name] = done.stdout.splitlines()[0]
    assert len(set(answers.values())) == 4, answers


# ---------------------------------------------------------------------------
# 4. Non-vacuity: the check is shown REPORTING a miss
# ---------------------------------------------------------------------------


def test_the_check_REPORTS_a_contract_that_stopped_reproducing(tmp_path):
    """FI-01's lesson: a harness that passes whatever the instrument does is
    worth nothing.

    The declared marker for the ABSENT state is replaced with a sentence
    `score_tools.py audit` does not print. The instrument is untouched; only the
    claim about it moved, and the check has to say the claim no longer holds.
    """

    registry = rewrite_register(
        tmp_path,
        lambda text: text.replace(
            '"no findings ledger this tool can READ ids from",',
            '"a sentence this instrument has never printed",',
            1,
        ),
    )
    done = run_check("--only", SUBJECT, "--state", "absent", registry=registry)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "output does not contain" in done.stdout
    assert "MISS" in done.stdout


def test_the_check_REFUSES_a_demonstration_that_stages_nothing(tmp_path):
    """A `remove` that removes nothing, an `except` that excludes nothing.

    The same rule `demonstrate.py` applies to a `find` occurring zero times: a
    demonstration whose break did not happen reports on an unbroken subject and
    calls it a break.
    """

    registry = rewrite_register(
        tmp_path,
        lambda text: text.replace(
            'except = ["deferred_findings.yaml", ".history"]',
            'except = ["deferred_findings.yaml", ".history", "no-such-entry"]',
            1,
        ),
    )
    done = run_check("--only", SUBJECT, "--state", "absent", registry=registry)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "MALFORMED DEMONSTRATION" in done.stdout
    assert "an exclusion that excludes nothing" in done.stdout


def test_the_count_is_reported_with_a_denominator_and_carries_no_target():
    """`denominator_rule`. The product of this command is a count, and a count
    with no denominator beside it is the shape this project has been bitten by
    repeatedly. There is deliberately no threshold on the ratio: a target on a
    repair count before the check existed would be `MF-020`."""

    done = run_check("--contract-only", "--format", "json")
    assert done.returncode == 1, done.stderr
    report = json.loads(done.stdout)
    counts = report["counts"]
    assert counts["instruments"] == report["instruments"] > 0
    buckets = ("satisfied", "declared_not_executed", "partial", "waived_rows",
               "without_contract", "refused")
    assert sum(counts[b] for b in buckets) == report["selected"]
    text = run_check("--contract-only").stdout
    assert "instruments in the register" in text
    assert "The first six sum to `selected`" in text
    assert "No target is set on that ratio" in text


def test_a_PARTIAL_run_can_never_report_SATISFIED():
    """The empty-selection sub-shape, one level in.

    `--state` exists so a demonstration costing 27 seconds an invocation can be
    checked one state at a time. Two of this command's checks -- "all three
    reproduce" and "no two states collapse" -- are properties of the SET, so a
    subset that answered with the whole set's word would be a smaller run
    reporting a bigger result. It reports PARTIAL and exits UNDECIDED instead.
    """

    done = run_check("--only", SELF, "--state", "absent")
    assert done.returncode == 2, done.stdout + done.stderr
    assert "PARTIAL (absent)" in done.stdout
    assert "NOT EVERY CONTRACT WAS FULLY EXECUTED" in done.stdout
    full = run_check("--only", SELF)
    assert full.returncode == 0, full.stdout + full.stderr
    assert "SATISFIED" in full.stdout


def test_contract_only_over_a_clean_register_is_UNDECIDED_not_PASS(tmp_path):
    """`--contract-only` reads the TOML and executes nothing.

    A register whose every selected row declares a well-formed contract would
    otherwise exit 0 from a run that never started an instrument -- a declaration
    answering for a demonstration, which is the shape `FI-02` exists to refuse.
    """

    done = run_check("--contract-only", "--only", SELF)
    assert done.returncode == 2, done.stdout + done.stderr
    assert "DECLARED (not executed)" in done.stdout
    assert "NOT EVERY CONTRACT WAS FULLY EXECUTED" in done.stdout


# ---------------------------------------------------------------------------
# The doctrine boundary, executed
# ---------------------------------------------------------------------------


# WIDENED BY `SS-06` UNDER `SS-02-DF-09`, WHICH WAS RIGHT ABOUT BOTH GUARDS.
#
# An independent reviewer of PR #284, instructed to refute, found that these two
# tests were NARROWER THAN THE CLAIMS THE PR CITED THEM FOR. The clause held --
# by inspection -- but not because these tests established it, and a guard cited
# for more than it computes is the same shape as a check that cannot fail.
# `SS-06`'s remit was to widen them or to file that they cannot be widened
# honestly; measured at `8dd0442`, they can:
#
#   * the caller search matched the LITERAL `absent-input` under `scripts/`
#     only, so `from score_tools import cmd_absent_input` -- the obvious way a
#     close path would actually call it -- evaded it, and `skill-scripts/`,
#     `templates/`, `test_graph/` and `spec_double_compiler/` were outside the
#     directory it walked. Widened to five program surfaces and three
#     spellings: ZERO hits, so the guard now passes for a reason rather than by
#     construction.
#   * the register search read `argv` and nothing else. `cwd`, `env`,
#     `stage.from`, `stage.to`, `link.from`, `link.to`, `write.file` and
#     `remove` all name paths, and `link.from` in particular decides WHICH TREE
#     A DEMONSTRATION REACHES INTO -- it is `.` in THREE OF THE SIX LINK
#     ENTRIES the register ships, which occur in 3 of its 9 declared states.
#     (An earlier version of this comment said "three of the six shipped
#     states"; there are NINE shipped states across three contracted
#     instruments, and 6 was the link-entry count. Corrected by the reviewer of
#     PR #286.) Widened to every field `_absent_stage` reads.
#
# STATED LIMIT, because widening does not remove it: a text search cannot see a
# call assembled at runtime, dispatched through a registry, or spelled by a
# shell fragment. A clean result here is a FLOOR, never a proof, and the clause
# it supports is still established by reading as well as by this.

#: Program surfaces -- where a close or promotion path can live. `tests/` is
#: excluded because a test referencing the check is the check being tested, and
#: `examples/validation/scorecards/` because that is where it is DEFINED.
PROGRAM_SURFACES = ("scripts", "skill-scripts", "templates", "test_graph",
                    "spec_double_compiler")
#: Every spelling a caller can use. The hyphen is the CLI subcommand; the
#: underscores are the import and the function.
CALLER_TOKENS = ("absent-input", "absent_input", "cmd_absent_input")
CALLER_SUFFIXES = (".py", ".sh", ".kts", ".toml", ".json", ".yaml", ".yml")


def _code_only(path, text: str) -> str:
    """A `.py` file with COMMENTS AND DOCSTRINGS REMOVED. `SS-05-DF-07`.

    THIS GUARD ACQUIRED THE SHAPE IT GUARDS. The search below is a SUBSTRING
    MATCH OVER RAW SOURCE TEXT, so it cannot tell a CALL from a MENTION. `SS-05`
    repaired six absent-input instances and cited `absent-input` by name in the
    comments explaining each repair, in `scripts/disposition.py` and
    `scripts/generate_python.py` -- two program surfaces -- and this test went RED
    reporting them as callers wiring the check into a close path. NOTHING WAS
    WIRED. The guard's claim was still TRUE and it reported a violation anyway: a
    FALSE REFUSAL by a recogniser bound to surface form, which is the same class
    as `CA-08-DF-01` (a recogniser bound by sentence form) and `SS-00-DF-03` (a
    keyword matcher over harness prose).

    Rewording the comments would have been editing the artifact to make the check
    pass. Repairing the check to measure the property it states is the other
    option and it is this one. The guard is now STRICTLY STRONGER on its stated
    claim, and `test_the_gate_guard_still_catches_a_real_caller` demonstrates that
    it still catches a genuine wiring.

    NON-`.py` FILES ARE RETURNED UNCHANGED: a shell fragment or a TOML value is
    where a real wiring hides, and the stated limit above already says a clean
    result is a floor. AN UNTOKENISABLE FILE IS ALSO RETURNED WHOLE -- unreadable
    is not clean, and the conservative direction is the one this rule requires.
    """
    if path.suffix != ".py":
        return text
    import ast

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return text
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef,
                             ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc:
                # Blank the docstring in place, keeping every other node intact.
                node.body[0].value.value = ""
    # `ast.unparse` drops comments by construction, which is the other half.
    return ast.unparse(tree)


def test_the_check_gates_nothing():
    """Clause (e): NO NEW GATE OVER SUBJECT-PROGRAM CONTENT.

    The check is in the permitted population -- a static check over this
    project's own record and metadata, 3 catches : 1 false refusal -- and it
    stays there by reading one file and being wired into no close path. A
    reference to it from a PROGRAM SURFACE, which carries the close and
    promotion paths, would be it becoming a gate.

    `SS-02-DF-09`: this used to walk one directory for one spelling.
    """

    searched: list[str] = []
    callers: list[str] = []
    for surface in PROGRAM_SURFACES:
        root = REPO_ROOT / surface
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix not in CALLER_SUFFIXES:
                continue
            searched.append(path.relative_to(REPO_ROOT).as_posix())
            text = path.read_text(encoding="utf-8", errors="ignore")
            # `SS-05-DF-07`: a MENTION is not a CALL. See `_code_only`.
            text = _code_only(path, text)
            if any(token in text for token in CALLER_TOKENS):
                callers.append(path.relative_to(REPO_ROOT).as_posix())

    # ABSENT INPUT: "swept nothing" and "found nothing" are different answers,
    # and a guard that reports the second when it means the first passes
    # forever. `score_tools._finding_ids` is the worked shape of exactly this.
    assert len(searched) > 50, (
        f"the caller search read {len(searched)} files across {PROGRAM_SURFACES}. "
        f"A search that reaches almost nothing cannot certify that nothing "
        f"references the check; that is UNDECIDED, not clean."
    )
    assert callers == [], (
        f"{callers} reference the absent-input check ({CALLER_TOKENS}). It reads "
        f"this project's own instrument register and decides nothing about an "
        f"adopter's code; wiring it into a close or promotion path makes it the "
        f"gate the static-gates doctrine refuses."
    )


def test_the_gate_guard_still_catches_a_real_caller(tmp_path):
    """NON-VACUITY FOR `SS-05-DF-07`'s REPAIR, and it is the whole risk in it.

    `test_the_check_gates_nothing` stopped matching comments and docstrings. A
    narrowing that ALSO stopped matching real callers would turn a guard into a
    formality and satisfy itself forever -- which is the vacuous-pass shape this
    whole file is about, acquired while repairing a false refusal.

    So: four subjects, all `.py`, run through the same `_code_only` the guard
    uses. Three are genuine wirings in three different spellings and MUST still
    be found; one is the comment-only mention that caused the false refusal and
    MUST NOT be.
    """
    real_import = tmp_path / "close_path_a.py"
    real_import.write_text(
        "from score_tools import cmd_absent_input\n\n"
        "def close():\n    return cmd_absent_input([])\n",
        encoding="utf-8")

    real_subprocess = tmp_path / "close_path_b.py"
    real_subprocess.write_text(
        "import subprocess\n\n"
        "def close():\n"
        "    subprocess.run(['python', 'score_tools.py', 'absent-input'])\n",
        encoding="utf-8")

    real_attribute = tmp_path / "close_path_c.py"
    real_attribute.write_text(
        "import score_tools\n\n"
        "def close():\n    return score_tools.absent_input()\n",
        encoding="utf-8")

    mention_only = tmp_path / "repaired_module.py"
    mention_only.write_text(
        '"""Repaired under the absent-input rule SS-02 landed."""\n\n'
        "# CA-10-DF-99, repaired by SS-05. The absent_input class in one line:\n"
        "# cmd_absent_input is the check; this module does not call it.\n"
        "def unrelated():\n    return 1\n",
        encoding="utf-8")

    def hits(path):
        return any(token in _code_only(path, path.read_text(encoding="utf-8"))
                   for token in CALLER_TOKENS)

    assert hits(real_import), "a real import stopped being caught"
    assert hits(real_subprocess), "a real subprocess call stopped being caught"
    assert hits(real_attribute), "a real attribute call stopped being caught"
    assert not hits(mention_only), (
        "the comment-only mention is still reported as a caller; the repair did "
        "not take"
    )

    # And the un-narrowed search DOES flag the mention, which is the finding:
    # without `_code_only` this file is indistinguishable from the three above.
    assert any(token in mention_only.read_text(encoding="utf-8")
               for token in CALLER_TOKENS)


#: Every field of a state spec that can name a path, taken from what
#: `score_tools._absent_stage` actually READS rather than from what the shipped
#: contracts happen to use today.
#:
#: `SS-02-DF-09` named `stage.from` explicitly and the FIRST version of this
#: widening still missed it, along with `stage.to` and `remove` -- so the guard
#: went from one field to five while the reviewer's own example stayed outside
#: it. Caught by the independent reviewer of PR #286 against
#: `score_tools.py:4686` and `:4721`. The list is now derived from that staging
#: function's own `spec.get(...)` calls, which is the only source for it that
#: cannot drift away from the code.
PATH_BEARING = ("argv", "cwd", "env", "stage", "link", "write", "remove")


def paths_declared(spec: dict) -> list[tuple[str, str]]:
    """(field, value) for every path a state spec can reach through.

    Returns a LIST, and an EMPTY one means "this state declares no path",
    which the caller distinguishes from "this state was never read". The two
    answers are the whole subject of this file and they stay separable here.
    """
    out: list[tuple[str, str]] = []
    for part in spec.get("argv", []):
        out.append(("argv", str(part)))
    if "cwd" in spec:
        out.append(("cwd", str(spec["cwd"])))
    for name, value in (spec.get("env") or {}).items():
        out.append((f"env.{name}", str(value)))
    # `stage` COPIES out of the repository into the throwaway tree, `link`
    # SYMLINKS into it. Both name a repository-relative source, and `stage.from`
    # is the field `SS-02-DF-09` named first.
    for entry in spec.get("stage", []):
        out.append(("stage.from", str(entry.get("from", ""))))
        out.append(("stage.to", str(entry.get("to", ""))))
    for entry in spec.get("link", []):
        out.append(("link.from", str(entry.get("from", ""))))
        out.append(("link.to", str(entry.get("to", ""))))
    for entry in spec.get("write", []):
        out.append(("write.file", str(entry.get("file", ""))))
    # `remove` is a bare list of tree-relative paths deleted inside the staged
    # tree. Read as a path too: an absolute one would delete outside that tree.
    for relative in spec.get("remove", []):
        out.append(("remove", str(relative)))
    return out


def test_the_register_is_the_only_thing_the_check_reads(register):
    """Scoped to this project's own instrument register, by construction.

    Every path a contract can reach through -- `argv`, `cwd`, every `env` value,
    every `stage.from`/`stage.to`, every `link.from`/`link.to`, every
    `write.file` and every `remove` entry -- names either the repository
    (`{repo}`), the throwaway tree the state was staged into (`{tree}`), or a
    path relative to one of those. Nothing points at a subject program and no
    field `_absent_stage` reads would let it.

    `SS-02-DF-09`: this used to inspect `argv` alone, while `link.from` is the
    field that decides which tree a demonstration reaches into. The widening
    then missed `stage.from`, `stage.to` and `remove` until the reviewer of
    PR #286 checked it against `score_tools._absent_stage` itself.
    """

    contracted = [r for r in register["instrument"] if "absent_input" in r]
    assert contracted, "no instrument declares a contract -- this test would be vacuous"
    checked = 0
    for entry in contracted:
        for state in ("absent", "unreadable", "empty"):
            spec = entry["absent_input"][state]
            declared = paths_declared(spec)
            assert declared, (
                f"{entry['id']}/{state}: declares no path in any of "
                f"{PATH_BEARING}; every shipped state names at least argv and cwd"
            )
            for field, value in declared:
                checked += 1
                assert not value.startswith("/") or value == sys.executable or "{" in value, (
                    f"{entry['id']}/{state}.{field}: absolute path {value!r} "
                    f"outside the repository and outside the staged tree"
                )
                assert not value.startswith("~") and ".." not in PurePosixPath(value).parts, (
                    f"{entry['id']}/{state}.{field}: {value!r} escapes the "
                    f"repository and the staged tree"
                )
    assert checked > len(contracted) * 3, (
        f"only {checked} path fields were inspected across {len(contracted)} "
        f"contracted instruments; this guard is reading less than it claims"
    )


def test_the_path_reader_sees_every_field_and_not_only_argv():
    """`SS-02-DF-09` pinned in both directions, on a synthetic spec.

    The guard above passes today because the shipped contracts are clean. That
    is exactly the state the narrow version was in, so the discriminating power
    is demonstrated here instead of assumed: a spec whose `argv` is impeccable
    and whose `link.from` reaches out of the tree must be SEEN.
    """
    spec = {
        "argv": ["{python}", "{repo}/examples/validation/scorecards/score_tools.py"],
        "cwd": "{repo}",
        "env": {"SCORECARD_REPO_ROOT": "{tree}"},
        "link": [{"from": "/Users/someone/their-app", "to": "."}],
        "write": [{"file": "specs/deferred_findings.yaml"}],
    }
    fields = dict(paths_declared(spec))
    assert "link.from" in fields and fields["link.from"] == "/Users/someone/their-app"
    assert {"argv", "cwd", "env.SCORECARD_REPO_ROOT", "link.to", "write.file"} <= set(fields)
    offending = [(f, v) for f, v in paths_declared(spec)
                 if v.startswith("/") and v != sys.executable and "{" not in v]
    assert offending == [("link.from", "/Users/someone/their-app")]
    # And the empty answer stays distinguishable from a clean one.
    assert paths_declared({}) == []
