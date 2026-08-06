"""A wrapped comment inside VARIABLES/CONSTANTS must not truncate the block.

Found closing the meta-orchestrator `live-stream-evals` workflow. The close
refused with:

    External.cfg assigns CONSTANT TracerConfigured, which External.tla does not
    declare
    External.cfg assigns CONSTANT Branched, which External.tla does not declare

Both messages were false. `Core.tla` declares both, `External` reaches them
through EXTENDS, and TLC had been model-checking the pair successfully for the
whole epic. What actually happened is that `parse_declaration_block` stopped
early, so the resolved constant set was short by two -- and the caller reported
the shortfall as a fault in the CONFIG.

The mechanism is `strip_comments` meeting a comment that wraps:

    CONSTANTS
      Orchestrator,    \\* meta-orchestrator itself: the principal that
                       \\* OWNS the kickoff and control streams
      TracerConfigured,\\* ...
      Branched         \\* ...

The continuation line holds nothing but a comment, so stripping leaves a BLANK
line in the middle of the declaration, and a blank line ended the block.

The fix reads the syntax rather than the whitespace: TLA+ separates declared
names with commas, so buffered content ending in a comma promises another name
and the declaration cannot have ended. A blank line is skipped while that
promise is outstanding and still ends the block otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.analyze_complexity import (  # noqa: E402
    parse_declaration_block,
    strip_comments,
)

WRAPPED = """\
---- MODULE Core ----
CONSTANTS
  Agents,        \\* swarm agent names
  Entrypoint,    \\* the only kickoff target
  Orchestrator,  \\* the control-plane principal that
                 \\* OWNS the kickoff and control streams
  TracerConfigured,\\* TRUE iff a tracer block is declared
  Branched       \\* TRUE iff created by branch_topology.py
                 \\*
                 \\* A CONSTANT rather than an action parameter, and the
                 \\* distinction is deliberate.

ASSUME Agents /= {}
====
"""

UNWRAPPED = """\
---- MODULE Core ----
CONSTANTS
  Agents,
  Entrypoint,
  Orchestrator,
  TracerConfigured,
  Branched

ASSUME Agents /= {}
====
"""

EXPECTED = ["Agents", "Entrypoint", "Orchestrator", "TracerConfigured", "Branched"]


def test_a_wrapped_comment_does_not_truncate_the_declaration() -> None:
    """THE DEFECT. Before the fix this returned the first three names."""
    assert parse_declaration_block(strip_comments(WRAPPED), "CONSTANT") == EXPECTED


def test_wrapped_and_unwrapped_declare_the_same_names() -> None:
    """Comments are not syntax. Two modules that differ only in prose must
    resolve identically, or the analyzer is measuring formatting."""
    assert parse_declaration_block(
        strip_comments(WRAPPED), "CONSTANT"
    ) == parse_declaration_block(strip_comments(UNWRAPPED), "CONSTANT")


def test_a_trailing_comment_block_after_the_last_name_is_not_swallowed() -> None:
    """The last name carries no comma, so its wrapped comment ends the block.

    `Branched` is followed by four more comment lines and then `ASSUME`. Nothing
    from those lines may become a declared name.
    """
    names = parse_declaration_block(strip_comments(WRAPPED), "CONSTANT")
    assert "ASSUME" not in names
    assert names[-1] == "Branched"


def test_the_same_holds_for_variables() -> None:
    text = """\
---- MODULE M ----
VARIABLES
  runner,      \\* the runner process, as status observes it
               \\* from runner/pid and runner/exit-code
  tracerLife

Init == TRUE
====
"""
    assert parse_declaration_block(strip_comments(text), "VARIABLE") == [
        "runner",
        "tracerLife",
    ]


# ---------------------------------------------------------------------------
# Negative controls: a blank line must STILL end a finished declaration
# ---------------------------------------------------------------------------


def test_a_blank_line_still_ends_a_completed_declaration() -> None:
    """The half that keeps the fix honest.

    If blank lines simply stopped ending the block, the parser would run on into
    whatever followed and collect names that were never declared.
    """
    text = """\
---- MODULE M ----
CONSTANTS
  Agents,
  Entrypoint

SomeOperator == 1
Another == 2
====
"""
    assert parse_declaration_block(strip_comments(text), "CONSTANT") == [
        "Agents",
        "Entrypoint",
    ]


def test_a_second_declaration_after_a_gap_is_not_absorbed() -> None:
    text = """\
---- MODULE M ----
CONSTANTS
  Agents

VARIABLES
  runner
====
"""
    assert parse_declaration_block(strip_comments(text), "CONSTANT") == ["Agents"]
