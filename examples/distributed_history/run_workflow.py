#!/usr/bin/env python3
"""Replay a two-ticket distributed spec workflow with append-only history."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import stat
from pathlib import Path


EXAMPLE_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_DIR.parents[1]
SCRIPTS = REPO_ROOT / "scripts"
SPECS = EXAMPLE_DIR / "specs"
WORKFLOW = "distributed-fulfillment-history"
MODULE = "DistributedFulfillment"


BASELINE_TLA = r"""----------------------------- MODULE DistributedFulfillment -----------------------------
EXTENDS Naturals, FiniteSets, TLC

CONSTANTS
  Orders,
  NoReason

VARIABLES
  accepted,
  result

vars == << accepted, result >>

Init ==
  /\ accepted = {}
  /\ result = [accepted |-> TRUE, reason |-> NoReason]

\* @command AcceptOrder
\* @result AcceptOrderResult
AcceptOrder(o) ==
  /\ o \notin accepted
  /\ accepted' = accepted \cup {o}
  /\ result' = [accepted |-> TRUE, reason |-> NoReason]

\* @command RejectDuplicateOrder
\* @result AcceptOrderResult
RejectDuplicateOrder(o) ==
  /\ o \in accepted
  /\ UNCHANGED accepted
  /\ result' = [accepted |-> FALSE, reason |-> "DUPLICATE"]

Next ==
  \E o \in Orders:
    AcceptOrder(o) \/ RejectDuplicateOrder(o)

\* @invariant AcceptedOrdersAreKnown
AcceptedOrdersAreKnown ==
  accepted \subseteq Orders

Spec ==
  Init /\ [][Next]_vars

=============================================================================
"""


TICKET1_TLA = r"""----------------------------- MODULE DistributedFulfillment -----------------------------
EXTENDS Naturals, FiniteSets, TLC

CONSTANTS
  Orders,
  NoReason

VARIABLES
  accepted,
  outbox,
  topic,
  result

vars == << accepted, outbox, topic, result >>

Init ==
  /\ accepted = {}
  /\ outbox = {}
  /\ topic = {}
  /\ result = [accepted |-> TRUE, reason |-> NoReason]

\* @command AcceptOrder
\* @result AcceptOrderResult
AcceptOrder(o) ==
  /\ o \notin accepted
  /\ accepted' = accepted \cup {o}
  /\ outbox' = outbox \cup {o}
  /\ UNCHANGED topic
  /\ result' = [accepted |-> TRUE, reason |-> NoReason]

\* @command RejectDuplicateOrder
\* @result AcceptOrderResult
RejectDuplicateOrder(o) ==
  /\ o \in accepted
  /\ UNCHANGED << accepted, outbox, topic >>
  /\ result' = [accepted |-> FALSE, reason |-> "DUPLICATE"]

\* @command PublishOutbox
\* @result PublishOutboxResult
PublishOutbox(o) ==
  /\ o \in outbox
  /\ topic' = topic \cup {o}
  /\ UNCHANGED << accepted, outbox, result >>

Next ==
  \E o \in Orders:
    AcceptOrder(o) \/ RejectDuplicateOrder(o) \/ PublishOutbox(o)

\* @invariant AcceptedOrdersAreKnown
AcceptedOrdersAreKnown ==
  accepted \subseteq Orders

\* @invariant OutboxOnlyContainsAcceptedOrders
OutboxOnlyContainsAcceptedOrders ==
  outbox \subseteq accepted

\* @invariant PublishedOrdersWereAccepted
PublishedOrdersWereAccepted ==
  topic \subseteq accepted

Spec ==
  Init /\ [][Next]_vars

=============================================================================
"""


FINAL_TLA = r"""----------------------------- MODULE DistributedFulfillment -----------------------------
EXTENDS Naturals, FiniteSets, TLC

CONSTANTS
  Orders,
  NoReason

VARIABLES
  accepted,
  outbox,
  topic,
  projected,
  acked,
  result

vars == << accepted, outbox, topic, projected, acked, result >>

Init ==
  /\ accepted = {}
  /\ outbox = {}
  /\ topic = {}
  /\ projected = {}
  /\ acked = {}
  /\ result = [accepted |-> TRUE, reason |-> NoReason]

\* @command AcceptOrder
\* @result AcceptOrderResult
AcceptOrder(o) ==
  /\ o \notin accepted
  /\ accepted' = accepted \cup {o}
  /\ outbox' = outbox \cup {o}
  /\ UNCHANGED << topic, projected, acked >>
  /\ result' = [accepted |-> TRUE, reason |-> NoReason]

\* @command RejectDuplicateOrder
\* @result AcceptOrderResult
RejectDuplicateOrder(o) ==
  /\ o \in accepted
  /\ UNCHANGED << accepted, outbox, topic, projected, acked >>
  /\ result' = [accepted |-> FALSE, reason |-> "DUPLICATE"]

\* @command PublishOutbox
\* @result PublishOutboxResult
PublishOutbox(o) ==
  /\ o \in outbox
  /\ topic' = topic \cup {o}
  /\ UNCHANGED << accepted, outbox, projected, acked, result >>

\* @command ProjectShipment
\* @result ProjectShipmentResult
ProjectShipment(o) ==
  /\ o \in topic
  /\ projected' = projected \cup {o}
  /\ acked' = acked \cup {o}
  /\ UNCHANGED << accepted, outbox, topic, result >>

Next ==
  \E o \in Orders:
    AcceptOrder(o)
    \/ RejectDuplicateOrder(o)
    \/ PublishOutbox(o)
    \/ ProjectShipment(o)

\* @invariant AcceptedOrdersAreKnown
AcceptedOrdersAreKnown ==
  accepted \subseteq Orders

\* @invariant OutboxOnlyContainsAcceptedOrders
OutboxOnlyContainsAcceptedOrders ==
  outbox \subseteq accepted

\* @invariant PublishedOrdersWereAccepted
PublishedOrdersWereAccepted ==
  topic \subseteq accepted

\* @invariant ProjectedOrdersWerePublished
ProjectedOrdersWerePublished ==
  projected \subseteq topic

\* @invariant AckedOrdersWereProjected
AckedOrdersWereProjected ==
  acked \subseteq projected

Spec ==
  Init /\ [][Next]_vars

=============================================================================
"""


BASELINE_CFG = """SPECIFICATION Spec

CONSTANTS
  Orders = {o1, o2}
  NoReason = NoReason

INVARIANTS
  AcceptedOrdersAreKnown
"""


TICKET1_CFG = """SPECIFICATION Spec

CONSTANTS
  Orders = {o1, o2}
  NoReason = NoReason

INVARIANTS
  AcceptedOrdersAreKnown
  OutboxOnlyContainsAcceptedOrders
  PublishedOrdersWereAccepted
"""


FINAL_CFG = """SPECIFICATION Spec

CONSTANTS
  Orders = {o1, o2}
  NoReason = NoReason

INVARIANTS
  AcceptedOrdersAreKnown
  OutboxOnlyContainsAcceptedOrders
  PublishedOrdersWereAccepted
  ProjectedOrdersWerePublished
  AckedOrdersWereProjected
"""


def manifest(model_role: str, actions: list[str]) -> str:
    rendered_actions = "\n".join(f"  - {action}" for action in actions)
    return f"""module: {MODULE}
package: distributed_fulfillment_cases

status:
  model_role: {model_role}
  workflow: {WORKFLOW}
  evidence: specs/results

case_codegen:
  style: explicit_transition_cases

state_fields:
  - accepted
  - outbox
  - topic
  - projected
  - acked

actions:
{rendered_actions}

ports: {{}}
adapters: case_adapters.toml
"""


def ticket_plan(dist_001_status: str, dist_002_status: str) -> str:
    return f"""version: 1
name: {WORKFLOW}
status:
  workflow: {WORKFLOW}
  phase: implementation
  active_ticket: DIST-002

planning_rules:
  current_model_rule: current is the whole implemented program, not a ticket projection.
  history_rule: close each done ticket into specs/.history/{WORKFLOW}/.

tickets:
  - id: DIST-001
    title: "Add durable order outbox"
    status: {dist_001_status}
    depends_on: []
    objective: "Accepted orders are persisted to a durable outbox before downstream publishing is considered complete."
    desired_actions:
      - AcceptOrder
      - PublishOutbox
    current_increment:
      model_state:
        - outbox
        - topic
      model_actions:
        - PublishOutbox
      adapters:
        - OutboxPublisherAdapter
      unit_tests:
        - python -m pytest specs/current/tests
    acceptance:
      commands:
        - scripts/run_tlc.sh specs/current/DistributedFulfillment.tla specs/current/MC.cfg
      evidence:
        - specs/results/dist-001-tlc.txt

  - id: DIST-002
    title: "Project published orders idempotently"
    status: {dist_002_status}
    depends_on:
      - DIST-001
    objective: "A worker consumes published order events, updates the shipment projection, and records acknowledgement only after projection."
    desired_actions:
      - ProjectShipment
    current_increment:
      model_state:
        - projected
        - acked
      model_actions:
        - ProjectShipment
      adapters:
        - ShipmentProjectionWorkerAdapter
      unit_tests:
        - python -m pytest specs/current/tests
    acceptance:
      commands:
        - scripts/run_tlc.sh specs/current/DistributedFulfillment.tla specs/current/MC.cfg
      evidence:
        - specs/results/dist-002-tlc.txt
"""


DESIRED_STATE = f"""version: 1
name: distributed-fulfillment-desired-state
workflow: {WORKFLOW}
canonical_tla_module: {MODULE}
ticket_plan: ticket_plan.yaml

distributed_boundaries:
  api:
    state: accepted
    actions:
      - AcceptOrder
      - RejectDuplicateOrder
  durable_outbox:
    state: outbox
    actions:
      - PublishOutbox
  broker_topic:
    state: topic
  projection_worker:
    state:
      - projected
      - acked
    actions:
      - ProjectShipment
"""


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def make_tree_writable(path: Path) -> None:
    if not path.exists():
        return
    for child in sorted(path.rglob("*"), key=lambda item: len(item.parts), reverse=True):
        if child.is_symlink():
            continue
        mode = child.stat().st_mode
        child.chmod(mode | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)


def write_model(directory: Path, tla: str, cfg: str, manifest_text: str) -> None:
    write(directory / f"{MODULE}.tla", tla)
    write(directory / "MC.cfg", cfg)
    write(directory / "spec_manifest.yaml", manifest_text)


def write_readmes() -> None:
    write(
        SPECS / "program_model" / "README.md",
        """# Program Model

Accepted distributed fulfillment model. After the example workflow closes, this
is the final promoted model.
""",
    )
    write(
        SPECS / "current" / "README.md",
        """# Current Model

Whole-program model of the distributed fulfillment behavior implemented so far
in the active workflow.
""",
    )
    write(
        SPECS / "desired_program_model" / "README.md",
        """# Desired Program Model

Target two-ticket distributed fulfillment workflow. Ticket details live in
ticket_plan.yaml.
""",
    )


def write_results(name: str, content: str) -> Path:
    path = SPECS / "results" / name
    write(path, content)
    return path


def assert_history() -> None:
    history = SPECS / ".history" / WORKFLOW
    expected = [
        history / "ticket-000-DIST-001" / "manifest.json",
        history / "ticket-001-DIST-002" / "manifest.json",
        history / "closed-snapshot" / "manifest.json",
    ]
    for path in expected:
        if not path.exists():
            raise AssertionError(f"missing history manifest: {path}")

    ticket_1 = json.loads(expected[0].read_text(encoding="utf-8"))
    ticket_2 = json.loads(expected[1].read_text(encoding="utf-8"))
    closed = json.loads(expected[2].read_text(encoding="utf-8"))

    assert ticket_1["kind"] == "ticket"
    assert ticket_1["ticket_id"] == "DIST-001"
    assert ticket_2["kind"] == "ticket"
    assert ticket_2["ticket_id"] == "DIST-002"
    assert closed["kind"] == "workflow-close"
    for manifest in [ticket_1, ticket_2, closed]:
        assert "commit_recommendation" in manifest
        assert "history_policy" in manifest
    assert not (SPECS / "current").exists()
    assert not (SPECS / "desired_program_model").exists()
    assert (SPECS / "program_model" / f"{MODULE}.tla").exists()
    assert (history / "closed-snapshot" / "snapshots" / "current" / f"{MODULE}.tla").exists()
    assert (history / "closed-snapshot" / "snapshots" / "desired_program_model" / "ticket_plan.yaml").exists()


def main() -> int:
    if SPECS.exists():
        make_tree_writable(SPECS)
        shutil.rmtree(SPECS)

    run(
        [
            sys.executable,
            str(SCRIPTS / "onboard_program_model.py"),
            "--repo-root",
            str(EXAMPLE_DIR),
            "--spec-root",
            "specs",
            "--name",
            MODULE,
        ]
    )
    write_model(
        SPECS / "program_model",
        BASELINE_TLA,
        BASELINE_CFG,
        manifest("accepted_program_model", ["AcceptOrder", "RejectDuplicateOrder"]),
    )

    run(
        [
            sys.executable,
            str(SCRIPTS / "new_ticket_workflow.py"),
            "DIST-001",
            "Add durable order outbox",
            "--repo-root",
            str(EXAMPLE_DIR),
            "--spec-root",
            "specs",
            "--force",
        ]
    )
    write_readmes()

    write_model(
        SPECS / "desired_program_model",
        FINAL_TLA,
        FINAL_CFG,
        manifest("desired_program_model", ["AcceptOrder", "RejectDuplicateOrder", "PublishOutbox", "ProjectShipment"]),
    )
    write(SPECS / "desired_program_model" / "desired_state.yaml", DESIRED_STATE)
    write(SPECS / "desired_program_model" / "ticket_plan.yaml", ticket_plan("done", "next"))
    write_model(
        SPECS / "current",
        TICKET1_TLA,
        TICKET1_CFG,
        manifest("current_after_DIST_001", ["AcceptOrder", "RejectDuplicateOrder", "PublishOutbox"]),
    )
    result_1 = write_results(
        "dist-001-tlc.txt",
        "DIST-001 evidence: TLC and adapter checks passed for durable outbox publish semantics.",
    )
    run(
        [
            sys.executable,
            str(SCRIPTS / "close-ticket.py"),
            "DIST-001",
            "--repo-root",
            str(EXAMPLE_DIR),
            "--spec-root",
            "specs",
            "--summary",
            "Accepted orders now create durable outbox records and publish them to the modeled broker topic.",
            "--result",
            str(result_1),
        ]
    )

    write(SPECS / "desired_program_model" / "ticket_plan.yaml", ticket_plan("done", "done"))
    write_model(
        SPECS / "current",
        FINAL_TLA,
        FINAL_CFG,
        manifest("current_after_DIST_002", ["AcceptOrder", "RejectDuplicateOrder", "PublishOutbox", "ProjectShipment"]),
    )
    result_2 = write_results(
        "dist-002-tlc.txt",
        "DIST-002 evidence: TLC and adapter checks passed for idempotent projection and acknowledgement semantics.",
    )
    run(
        [
            sys.executable,
            str(SCRIPTS / "close-ticket.py"),
            "DIST-002",
            "--repo-root",
            str(EXAMPLE_DIR),
            "--spec-root",
            "specs",
            "--summary",
            "Published orders are projected idempotently before acknowledgement is recorded.",
            "--result",
            str(result_2),
        ]
    )

    write_model(
        SPECS / "program_model",
        FINAL_TLA,
        FINAL_CFG,
        manifest("accepted_program_model", ["AcceptOrder", "RejectDuplicateOrder", "PublishOutbox", "ProjectShipment"]),
    )
    run(
        [
            sys.executable,
            str(SCRIPTS / "close_tickets.py"),
            "--repo-root",
            str(EXAMPLE_DIR),
            "--spec-root",
            "specs",
            "--summary",
            "Promoted the two-ticket distributed fulfillment workflow into the accepted program model.",
        ]
    )

    assert_history()
    print(f"distributed history workflow example generated at {EXAMPLE_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
