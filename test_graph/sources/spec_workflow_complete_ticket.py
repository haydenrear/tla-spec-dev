# /// script
# requires-python = ">=3.10"
# dependencies = ["testgraphsdk"]
#
# [tool.uv.sources]
# testgraphsdk = { path = "../sdk/python", editable = true }
# ///
from __future__ import annotations

from pathlib import Path

from testgraphsdk import NodeResult, NodeSpec, node, procs


SPEC = (
    NodeSpec("spec.workflow.complete")
    .kind("action")
    .depends_on("spec.workflow.start")
    .tags("spec-workflow", "git")
    .timeout("60s")
    .side_effects("filesystem:writes", "git:writes")
)


FINISHED_TLA = """----------------------------- MODULE ProgramModel -----------------------------
EXTENDS TLC

VARIABLES accepted, lastAction

vars == <<accepted, lastAction>>

Init ==
  /\\ accepted = FALSE
  /\\ lastAction = "Init"

CompleteTicket ==
  /\\ accepted' = TRUE
  /\\ lastAction' = "CompleteTicket"

Next == CompleteTicket

Spec == Init /\\ [][Next]_vars

AcceptedBoolean == accepted \\in BOOLEAN

=============================================================================
"""

ADAPTER = '''"""Ticket-local spec-unit adapter carried into project current on close."""

ACTION_NAME = "CompleteTicket"


def apply(case):
    return {"status": "accepted", "case": getattr(case, "name", "unknown")}
'''

ADAPTER_TEST = """from adapters.unit.complete_ticket_adapter import ACTION_NAME


def test_complete_ticket_adapter_declares_action():
    assert ACTION_NAME == "CompleteTicket"
"""

TESTGRAPH_BINDINGS = """actions:
  CompleteTicketExternal:
    layer: external
    controllability: e2e_direct
    adapter: ticket.adapters.CompleteTicketExternalAdapter
    assertion: ticket.assertions.ProjectedStateAssertion
"""

TESTGRAPH_NODE = """# Placeholder external adapter node produced by the ticket workflow.
ACTION = "CompleteTicketExternal"
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@node(SPEC)
def main(ctx):
    repo = Path(ctx.get("spec.workflow.repo", "repoPath") or "")
    ticket_id = ctx.get("spec.workflow.repo", "ticketId") or "FLOW-1"
    ticket_dir = Path(ctx.get("spec.workflow.start", "ticketDir") or repo / "specs" / "tickets" / ticket_id)

    for model_dir in (ticket_dir / "desired", ticket_dir / "current"):
        write_text(model_dir / "ProgramModel.tla", FINISHED_TLA)
        write_text(model_dir / "adapters" / "unit" / "complete_ticket_adapter.py", ADAPTER)
        write_text(model_dir / "tests" / "test_complete_ticket_adapter.py", ADAPTER_TEST)

    write_text(ticket_dir / "testgraph" / "bindings.yml", TESTGRAPH_BINDINGS)
    write_text(ticket_dir / "test_graph" / "sources" / "complete_ticket_external.py", TESTGRAPH_NODE)
    write_text(ticket_dir / "results" / "tlc.txt", "TLC passed for FLOW-1\n")

    ticket_plan = repo / "specs" / "desired_program_model" / "ticket_plan.yaml"
    plan_text = ticket_plan.read_text(encoding="utf-8")
    updated = plan_text.replace("status: next", "status: done", 1)
    ticket_plan.write_text(updated, encoding="utf-8")

    result = NodeResult.pass_(SPEC.id)
    for label, argv in [
        ("git-add", ["git", "add", "."]),
        ("git-commit", ["git", "commit", "-m", "complete ticket desired and current"]),
    ]:
        record = procs.run(ctx, label, argv, cwd=repo)
        result.process(record).assertion(f"{label} succeeded", record.exit_code == 0)

    desired_tla = ticket_dir / "desired" / "ProgramModel.tla"
    current_tla = ticket_dir / "current" / "ProgramModel.tla"
    return (
        result
        .assertion("ticket plan marked done", "status: done" in updated)
        .assertion("desired updated first-class", "CompleteTicket" in desired_tla.read_text(encoding="utf-8"))
        .assertion("current matches desired", current_tla.read_text(encoding="utf-8") == desired_tla.read_text(encoding="utf-8"))
        .assertion("ticket spec adapter written", (ticket_dir / "desired" / "adapters" / "unit" / "complete_ticket_adapter.py").is_file())
        .assertion("ticket Test Graph binding written", (ticket_dir / "testgraph" / "bindings.yml").is_file())
        .artifact("ticket-plan", str(ticket_plan))
    )


if __name__ == "__main__":
    main()
