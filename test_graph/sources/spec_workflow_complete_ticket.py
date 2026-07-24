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
    .side_effects("fs:tmp")
)


# A ticket that changes behavior touches BOTH views: the internal transition and
# the external projection a caller can observe. The new external action must also
# be mapped in testgraph_bindings.yml or it generates no Test Graph case.
INTERNAL_ACTION = """
\\* @action CompleteTicket
\\* @layer internal
\\* @controllability unit_direct
CompleteTicket ==
  /\\ lastInternalAction' = [name |-> "CompleteTicket", params |-> <<>>]
  /\\ UNCHANGED <<owners, records, outbox, projections>>
"""

EXTERNAL_ACTION = """
\\* @action SubmitCompleteTicket
\\* @layer external
\\* @controllability e2e_direct
SubmitCompleteTicket(c) ==
  /\\ c \\in Clients
  /\\ CompleteTicket
  /\\ UNCHANGED responses
  /\\ MarkExternal("SubmitCompleteTicket", [client |-> c])
"""

ACTIONS_ENTRIES = """  CompleteTicket:
    layer: internal
    controllability: unit_direct
    generates:
      - spec_unit
  SubmitCompleteTicket:
    layer: external
    controllability: e2e_direct
    generates:
      - testgraph
"""

BINDING_ENTRY = """  SubmitCompleteTicket:
    view: external
    layer: external
    controllability: e2e_direct
    kind: program-external
    adapter: specs.program_model.adapters:RegisterActorExternalAdapter
    projector: specs.program_model.adapters:ProgramStateProjector
    expected_projection: specs.program_model.adapters:ExpectedProgramProjection
    assertion: specs.program_model.adapters:ProjectedStateAssertion
"""


def append_before_terminator(path: Path, addition: str) -> None:
    """Insert a definition before a TLA+ module's trailing ==== line."""
    lines = path.read_text(encoding="utf-8").rstrip("\n").split("\n")
    while lines and not lines[-1].startswith("===="):
        lines.pop()
    terminator = lines.pop() if lines else "=" * 77
    body = "\n".join(lines).rstrip("\n")
    path.write_text(f"{body}\n{addition}\n{terminator}\n", encoding="utf-8")

ADAPTER = '''"""Ticket-local spec-unit adapter carried into project current on close."""

ACTION_NAME = "CompleteTicket"


def apply(case):
    return {"status": "accepted", "case": getattr(case, "name", "unknown")}
'''

ADAPTER_TEST = """from spec_adapters.complete_ticket_adapter import ACTION_NAME


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
        append_before_terminator(model_dir / "Internal.tla", INTERNAL_ACTION)
        append_before_terminator(model_dir / "External.tla", EXTERNAL_ACTION)

        actions = model_dir / "actions.yml"
        actions.write_text(actions.read_text(encoding="utf-8") + ACTIONS_ENTRIES, encoding="utf-8")

        # A new external action is not done until it is mapped for the Test Graph.
        bindings = model_dir / "testgraph_bindings.yml"
        bindings.write_text(bindings.read_text(encoding="utf-8") + BINDING_ENTRY, encoding="utf-8")

        write_text(model_dir / "spec_adapters" / "complete_ticket_adapter.py", ADAPTER)
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

    def read(view: str, name: str) -> str:
        return (ticket_dir / view / name).read_text(encoding="utf-8")

    views_match = all(
        read("current", name) == read("desired", name)
        for name in ("Internal.tla", "External.tla", "actions.yml", "testgraph_bindings.yml")
    )
    return (
        result
        .assertion("ticket plan marked done", "status: done" in updated)
        .assertion("desired internal view updated first-class", "CompleteTicket" in read("desired", "Internal.tla"))
        .assertion("desired external view updated first-class", "SubmitCompleteTicket" in read("desired", "External.tla"))
        .assertion("new external action mapped for Test Graph", "SubmitCompleteTicket" in read("desired", "testgraph_bindings.yml"))
        .assertion("current matches desired across both views", views_match)
        .assertion("ticket spec adapter written", (ticket_dir / "desired" / "spec_adapters" / "complete_ticket_adapter.py").is_file())
        .assertion("ticket Test Graph binding written", (ticket_dir / "testgraph" / "bindings.yml").is_file())
        .artifact("ticket-plan", str(ticket_plan))
    )


if __name__ == "__main__":
    main()
