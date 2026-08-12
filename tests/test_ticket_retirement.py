from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.close_tickets import close_ticket_workflow, validate_ticket_plan_closed
from scripts.spec_evolution import (
    canonical_retirement_receipt,
    create_ticket_history_entry,
    create_ticket_retirement_entry,
    validate_retirement_declaration,
)


WORKFLOW = "retirement-workflow"
TICKET = "RET-001"


def retirement_mapping(*, resolution: str = "carried") -> dict[str, object]:
    mapping: dict[str, object] = {
        "schedule_revision": 4,
        "resolution": resolution,
        "reason": "Owner moved this work out of the current workflow.",
        "decided_by": "project-owner",
        "decided_at": "2026-08-12T12:00:00Z",
        "receipt": (
            f"specs/.history/{WORKFLOW}/retired-ticket-000-{TICKET}/manifest.json"
        ),
        "affected_goals": [],
    }
    if resolution == "carried":
        mapping.update(
            {
                "successor_issue": "https://github.com/example/project/issues/42",
                "successor_workflow": "successor-workflow",
            }
        )
    return mapping


def plan_mapping(*, retirement: dict[str, object] | None = None) -> dict[str, object]:
    return {
        "name": WORKFLOW,
        "schedule_revision": 4,
        "tickets": [
            {
                "id": TICKET,
                "title": "Retired fixture ticket",
                "status": "retired",
                "retirement": retirement or retirement_mapping(),
            }
        ],
    }


def render_plan(plan: dict[str, object]) -> str:
    ticket = plan["tickets"][0]
    retirement = ticket["retirement"]
    lines = [
        f"name: {plan['name']}",
        f"schedule_revision: {plan['schedule_revision']}",
        "tickets:",
        f"  - id: {ticket['id']}",
        f"    title: {ticket['title']}",
        f"    status: {ticket['status']}",
        "    retirement:",
        f"      schedule_revision: {retirement['schedule_revision']}",
        f"      resolution: {retirement['resolution']}",
        f"      reason: \"{retirement['reason']}\"",
        f"      decided_by: {retirement['decided_by']}",
        f"      decided_at: \"{retirement['decided_at']}\"",
        f"      receipt: {retirement['receipt']}",
    ]
    if "successor_issue" in retirement:
        lines.append(f"      successor_issue: {retirement['successor_issue']}")
    if "successor_workflow" in retirement:
        lines.append(f"      successor_workflow: {retirement['successor_workflow']}")
    lines.append("      affected_goals: []")
    return "\n".join(lines) + "\n"


def write_plan(repo_root: Path, plan: dict[str, object] | None = None) -> Path:
    path = repo_root / "specs" / "desired_program_model" / "ticket_plan.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_plan(plan or plan_mapping()), encoding="utf-8")
    return path


def run_cli(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "tla_spec_dev.py"), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def test_retire_ticket_writes_distinct_no_claim_receipt_and_archives_unaccepted_work(
    tmp_path: Path,
) -> None:
    plan_path = write_plan(tmp_path)
    project_current = tmp_path / "specs" / "current"
    project_current.mkdir(parents=True)
    sentinel = project_current / "unchanged.txt"
    sentinel.write_text("project-current\n", encoding="utf-8")
    active = tmp_path / "specs" / "tickets" / TICKET
    (active / "current").mkdir(parents=True)
    (active / "desired").mkdir()
    (active / "current" / "state.txt").write_text("current\n", encoding="utf-8")
    (active / "desired" / "state.txt").write_text("different desired\n", encoding="utf-8")

    result = create_ticket_retirement_entry(
        repo_root=tmp_path,
        spec_root=Path("specs"),
        ticket_ref=TICKET,
    )
    manifest_path = result.entry_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert result.entry_dir == (
        tmp_path / "specs" / ".history" / WORKFLOW / f"retired-ticket-000-{TICKET}"
    )
    assert manifest["kind"] == "ticket-retirement"
    assert manifest["entry_kind"] == "ticket-retirement"
    assert manifest["semantic_promotion"] == {"performed": False}
    assert manifest["validation"] == {"claimed": False}
    assert manifest["promotion"] is None
    assert manifest["complexity_ledger"] is None
    assert manifest["snapshots"] == []
    assert manifest["results"] == []
    assert manifest["retirement"] == retirement_mapping()
    assert manifest["ticket_workdir"]["accepted"] is False
    assert not active.exists()
    assert (result.entry_dir / "ticket" / "desired" / "state.txt").read_text(
        encoding="utf-8"
    ) == "different desired\n"
    assert sentinel.read_text(encoding="utf-8") == "project-current\n"
    assert not (tmp_path / "specs" / "results" / "complexity_ledger.json").exists()
    assert "specs/desired_program_model/ticket_plan.yaml" in result.git_add_command
    assert validate_ticket_plan_closed(plan_path, repo_root=tmp_path) == []


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (
            lambda plan, retirement: retirement.update(schedule_revision=5),
            "is newer than ticket plan schedule_revision",
        ),
        (
            lambda plan, retirement: retirement.update(reason=""),
            "retirement.reason must be a non-empty string",
        ),
        (
            lambda plan, retirement: retirement.pop("successor_issue"),
            "carried retirement requires non-empty retirement.successor_issue",
        ),
        (
            lambda plan, retirement: retirement.update(receipt="somewhere/else.json"),
            "retirement.receipt must be the canonical path",
        ),
    ],
)
def test_retirement_declaration_refuses_incomplete_or_noncanonical_owner_decisions(
    tmp_path: Path, mutate, expected: str
) -> None:
    plan = plan_mapping()
    ticket = plan["tickets"][0]
    retirement = ticket["retirement"]
    mutate(plan, retirement)
    _, expected_receipt = canonical_retirement_receipt(
        tmp_path,
        tmp_path / "specs",
        WORKFLOW,
        0,
        ticket,
    )

    errors = validate_retirement_declaration(
        plan=plan,
        ticket=ticket,
        index=0,
        expected_receipt=expected_receipt,
    )

    assert expected in "\n".join(errors)


def test_success_close_cannot_promote_a_retired_ticket_even_with_allow_open(
    tmp_path: Path,
) -> None:
    write_plan(tmp_path)

    with pytest.raises(SystemExit) as error:
        create_ticket_history_entry(
            repo_root=tmp_path,
            spec_root=Path("specs"),
            ticket_ref=TICKET,
            summary="must not close",
            result_paths=[],
            allow_open=True,
        )

    assert "is retired" in str(error.value)
    assert "cannot promote" in str(error.value)
    assert not (tmp_path / "specs" / ".history" / WORKFLOW).exists()


def test_workflow_close_requires_the_exact_retirement_receipt(tmp_path: Path) -> None:
    plan_path = write_plan(tmp_path)
    missing_errors = validate_ticket_plan_closed(plan_path, repo_root=tmp_path)
    assert "retirement receipt is missing" in "\n".join(missing_errors)

    result = create_ticket_retirement_entry(
        repo_root=tmp_path,
        spec_root=Path("specs"),
        ticket_ref=TICKET,
    )
    manifest_path = result.entry_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["validation"] = {"claimed": True}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    tampered_errors = validate_ticket_plan_closed(plan_path, repo_root=tmp_path)
    assert "field 'validation' does not match the canonical value" in "\n".join(
        tampered_errors
    )


def test_workflow_close_dry_run_accepts_an_exact_retirement_receipt(tmp_path: Path) -> None:
    write_plan(tmp_path)
    create_ticket_retirement_entry(
        repo_root=tmp_path,
        spec_root=Path("specs"),
        ticket_ref=TICKET,
    )
    for name in ("program_model", "current", "desired_program_model"):
        model_dir = tmp_path / "specs" / name
        model_dir.mkdir(parents=True, exist_ok=True)
        (model_dir / "Program.tla").write_text("---- MODULE Program ----\n====\n", encoding="utf-8")
        (model_dir / "MC.cfg").write_text("SPECIFICATION Spec\n", encoding="utf-8")
    # Recreate the planning file after desired_program_model was populated.
    write_plan(tmp_path)

    removed = close_ticket_workflow(tmp_path, Path("specs"), dry_run=True)

    assert removed == [
        tmp_path / "specs" / "current",
        tmp_path / "specs" / "desired_program_model",
    ]


def test_later_schedule_revision_does_not_invalidate_a_sealed_retirement(
    tmp_path: Path,
) -> None:
    plan_path = write_plan(tmp_path)
    create_ticket_retirement_entry(
        repo_root=tmp_path,
        spec_root=Path("specs"),
        ticket_ref=TICKET,
    )
    plan = plan_mapping()
    plan["schedule_revision"] = 5
    plan_path.write_text(render_plan(plan), encoding="utf-8")

    assert validate_ticket_plan_closed(plan_path, repo_root=tmp_path) == []


def test_retirement_receipt_validation_is_independent_of_process_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan_path = write_plan(tmp_path)
    create_ticket_retirement_entry(
        repo_root=tmp_path,
        spec_root=Path("specs"),
        ticket_ref=TICKET,
    )
    other_cwd = tmp_path / "unrelated-cwd"
    other_cwd.mkdir()
    monkeypatch.chdir(other_cwd)

    assert validate_ticket_plan_closed(plan_path, repo_root=tmp_path) == []


@pytest.mark.parametrize("ticket_root", [Path("../outside"), Path("/tmp/outside")])
def test_retirement_ticket_root_must_stay_below_the_spec_root(
    tmp_path: Path, ticket_root: Path
) -> None:
    write_plan(tmp_path)

    with pytest.raises(SystemExit) as error:
        create_ticket_retirement_entry(
            repo_root=tmp_path,
            spec_root=Path("specs"),
            ticket_ref=TICKET,
            ticket_root=ticket_root,
        )

    assert "beneath the spec root" in str(error.value)
    assert not (tmp_path / "specs" / ".history" / WORKFLOW).exists()


def test_retirement_rolls_an_active_workspace_back_when_receipt_write_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_plan(tmp_path)
    active = tmp_path / "specs" / "tickets" / TICKET
    active.mkdir(parents=True)
    (active / "sentinel.txt").write_text("must return\n", encoding="utf-8")

    def fail_manifest(*_args, **_kwargs):
        raise OSError("receipt write failed")

    monkeypatch.setattr("scripts.spec_evolution.write_manifest", fail_manifest)
    with pytest.raises(OSError, match="receipt write failed"):
        create_ticket_retirement_entry(
            repo_root=tmp_path,
            spec_root=Path("specs"),
            ticket_ref=TICKET,
        )

    assert (active / "sentinel.txt").read_text(encoding="utf-8") == "must return\n"
    history_root = tmp_path / "specs" / ".history" / WORKFLOW
    assert not (history_root / f"retired-ticket-000-{TICKET}").exists()
    assert not list(history_root.glob(".retire-*"))


def test_retirement_refuses_a_symlink_ticket_workspace_without_mutation(
    tmp_path: Path,
) -> None:
    write_plan(tmp_path)
    real_workspace = tmp_path / "specs" / "real-workspace"
    real_workspace.mkdir(parents=True)
    sentinel = real_workspace / "sentinel.txt"
    sentinel.write_text("must remain\n", encoding="utf-8")
    active = tmp_path / "specs" / "tickets" / TICKET
    active.parent.mkdir(parents=True)
    active.symlink_to(real_workspace, target_is_directory=True)

    with pytest.raises(SystemExit, match="symbolic-link ticket workspace"):
        create_ticket_retirement_entry(
            repo_root=tmp_path,
            spec_root=Path("specs"),
            ticket_ref=TICKET,
        )

    assert active.is_symlink()
    assert sentinel.read_text(encoding="utf-8") == "must remain\n"
    assert not (tmp_path / "specs" / ".history" / WORKFLOW).exists()


def test_retirement_receipt_rejects_extra_manifest_fields_and_summary_tampering(
    tmp_path: Path,
) -> None:
    plan_path = write_plan(tmp_path)
    result = create_ticket_retirement_entry(
        repo_root=tmp_path,
        spec_root=Path("specs"),
        ticket_ref=TICKET,
    )
    manifest_path = result.entry_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["looks_harmless"] = True
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (result.entry_dir / "summary.md").write_text("retired\n", encoding="utf-8")

    errors = "\n".join(validate_ticket_plan_closed(plan_path, repo_root=tmp_path))
    assert "schema mismatch" in errors
    assert "summary does not match the canonical receipt text" in errors


def successful_terminal_fixture(tmp_path: Path) -> tuple[Path, Path]:
    specs = tmp_path / "specs"
    for name in ("program_model", "current", "desired_program_model"):
        model_dir = specs / name
        model_dir.mkdir(parents=True, exist_ok=True)
        (model_dir / "Program.tla").write_text("---- MODULE Program ----\n====\n", encoding="utf-8")
        (model_dir / "MC.cfg").write_text("SPECIFICATION Spec\n", encoding="utf-8")
    desired = specs / "desired_program_model"
    plan = plan_mapping()
    plan["tickets"].append(
        {
            "id": "FINAL-001",
            "title": "Terminal evaluation",
            "status": "done",
            "promotion_order": 20,
        }
    )
    plan_path = desired / "ticket_plan.yaml"
    plan_path.write_text(
        render_plan(plan).rstrip()
        + "\n"
        + "  - id: FINAL-001\n"
        + "    title: Terminal evaluation\n"
        + "    status: done\n"
        + "    promotion_order: 20\n",
        encoding="utf-8",
    )
    create_ticket_retirement_entry(
        repo_root=tmp_path,
        spec_root=Path("specs"),
        ticket_ref=TICKET,
    )
    receipt = specs / ".history" / WORKFLOW / "ticket-001-FINAL-001"
    snapshot = receipt / "snapshots" / "desired_program_model"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    import shutil

    shutil.copytree(desired, snapshot)
    receipt_manifest = {
        "kind": "ticket",
        "workflow_name": WORKFLOW,
        "ticket_index": 1,
        "ticket_id": "FINAL-001",
        "ticket_status": "done",
        "guard_weakening": {"weakened": False},
        "accept_new": False,
        "snapshots": [
            {
                "role": "desired_program_model",
                "snapshot": str(snapshot.relative_to(tmp_path)),
            }
        ],
    }
    (receipt / "manifest.json").write_text(
        json.dumps(receipt_manifest, indent=2) + "\n", encoding="utf-8"
    )
    return plan_path, snapshot


def test_retired_accept_new_uses_terminal_delivered_snapshot_as_its_authority(
    tmp_path: Path,
) -> None:
    successful_terminal_fixture(tmp_path)

    removed = close_ticket_workflow(
        tmp_path, Path("specs"), dry_run=True, accept_new=True
    )

    assert removed == [
        tmp_path / "specs" / "current",
        tmp_path / "specs" / "desired_program_model",
    ]
    assert (tmp_path / "specs" / "desired_program_model").is_dir()


def test_retired_accept_new_refuses_desired_state_changed_after_terminal_close(
    tmp_path: Path,
) -> None:
    plan_path, _ = successful_terminal_fixture(tmp_path)
    plan_path.write_text(plan_path.read_text(encoding="utf-8") + "tampered: true\n", encoding="utf-8")

    with pytest.raises(SystemExit) as error:
        close_ticket_workflow(tmp_path, Path("specs"), dry_run=True, accept_new=True)

    assert "terminal ticket desired snapshot differs: ticket_plan.yaml" in str(error.value)


def test_retired_accept_new_refuses_a_tampered_terminal_snapshot_path(
    tmp_path: Path,
) -> None:
    _, snapshot = successful_terminal_fixture(tmp_path)
    manifest_path = snapshot.parents[1] / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["snapshots"][0]["snapshot"] = "specs/desired_program_model"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(SystemExit) as error:
        close_ticket_workflow(tmp_path, Path("specs"), dry_run=True, accept_new=True)

    assert "desired snapshot is not the canonical" in str(error.value)


def test_retire_ticket_cli_uses_the_first_class_no_promotion_path(tmp_path: Path) -> None:
    write_plan(tmp_path)

    result = run_cli("--spec-root", "specs", "retire", "ticket", TICKET, cwd=tmp_path)

    receipt = (
        tmp_path
        / "specs"
        / ".history"
        / WORKFLOW
        / f"retired-ticket-000-{TICKET}"
        / "manifest.json"
    )
    assert result.returncode == 0, result.stderr
    assert "recorded spec history entry" in result.stdout
    assert "record ticket retirement" in result.stdout
    assert receipt.exists()


def test_direct_disposition_status_is_not_a_terminal_retirement(tmp_path: Path) -> None:
    plan = plan_mapping()
    plan["tickets"][0]["status"] = "carried"
    plan_path = write_plan(tmp_path, plan)

    errors = validate_ticket_plan_closed(plan_path, repo_root=tmp_path)

    assert errors == [f"ticket {TICKET} is not closed: status=carried"]


def write_delivered_plan(repo_root: Path) -> Path:
    path = repo_root / "specs" / "desired_program_model" / "ticket_plan.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"name: {WORKFLOW}\n"
        "schedule_revision: 1\n"
        "tickets:\n"
        "  - id: DONE-001\n"
        "    title: Delivered fixture\n"
        "    status: done\n",
        encoding="utf-8",
    )
    return path


def write_delivered_receipt(
    repo_root: Path,
    entry: str,
    *,
    ticket_index: int = 0,
    ticket_id: str = "DONE-001",
    ticket_status: str = "done",
) -> Path:
    receipt = repo_root / "specs" / ".history" / WORKFLOW / entry / "manifest.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(
        json.dumps(
            {
                "kind": "ticket",
                "workflow_name": WORKFLOW,
                "ticket_index": ticket_index,
                "ticket_id": ticket_id,
                "ticket_status": ticket_status,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return receipt


def test_delivered_ticket_requires_one_successful_close_receipt(tmp_path: Path) -> None:
    plan_path = write_delivered_plan(tmp_path)

    errors = validate_ticket_plan_closed(plan_path, repo_root=tmp_path)

    assert "exactly one successful close receipt" in "\n".join(errors)
    assert "found 0" in "\n".join(errors)


def test_delivered_ticket_refuses_multiple_successful_close_receipts(
    tmp_path: Path,
) -> None:
    plan_path = write_delivered_plan(tmp_path)
    write_delivered_receipt(tmp_path, "ticket-000-DONE-001")
    write_delivered_receipt(tmp_path, "custom-duplicate")

    errors = validate_ticket_plan_closed(plan_path, repo_root=tmp_path)

    assert "exactly one successful close receipt" in "\n".join(errors)
    assert "found 2" in "\n".join(errors)


def test_delivered_ticket_refuses_a_wrong_ordinal_receipt(tmp_path: Path) -> None:
    plan_path = write_delivered_plan(tmp_path)
    write_delivered_receipt(tmp_path, "ticket-000-DONE-001", ticket_index=1)

    errors = validate_ticket_plan_closed(plan_path, repo_root=tmp_path)

    assert "wrong immutable ordinal" in "\n".join(errors)


def test_repository_canonical_delivered_plan_has_matching_close_receipts() -> None:
    plan_path = ROOT / "specs" / "desired_program_model" / "ticket_plan.yaml"

    assert validate_ticket_plan_closed(plan_path, repo_root=ROOT) == []


def test_success_close_refuses_to_resurrect_an_exactly_retired_ticket(
    tmp_path: Path,
) -> None:
    plan_path = write_plan(tmp_path)
    retirement = create_ticket_retirement_entry(
        repo_root=tmp_path,
        spec_root=Path("specs"),
        ticket_ref=TICKET,
    )
    resurrected = plan_mapping()
    resurrected["tickets"][0]["status"] = "done"
    plan_path.write_text(render_plan(resurrected), encoding="utf-8")

    with pytest.raises(SystemExit, match="already has an immutable retirement receipt"):
        create_ticket_history_entry(
            repo_root=tmp_path,
            spec_root=Path("specs"),
            ticket_ref=TICKET,
            summary="must not resurrect",
            result_paths=[],
            entry_name="resurrected-close",
        )

    assert retirement.entry_dir.is_dir()
    assert not (
        tmp_path / "specs" / ".history" / WORKFLOW / "resurrected-close"
    ).exists()
    assert not (tmp_path / "specs" / "results" / "complexity_ledger.json").exists()


def test_workflow_validation_rejects_delivered_status_after_retirement(
    tmp_path: Path,
) -> None:
    plan_path = write_plan(tmp_path)
    create_ticket_retirement_entry(
        repo_root=tmp_path,
        spec_root=Path("specs"),
        ticket_ref=TICKET,
    )
    resurrected = plan_mapping()
    resurrected["tickets"][0]["status"] = "done"
    plan_path.write_text(render_plan(resurrected), encoding="utf-8")

    errors = "\n".join(validate_ticket_plan_closed(plan_path, repo_root=tmp_path))

    assert "delivered status conflicts with its immutable retirement receipt" in errors


def test_workflow_validation_rejects_retired_status_after_successful_close(
    tmp_path: Path,
) -> None:
    plan_path = write_plan(tmp_path)
    write_delivered_receipt(
        tmp_path,
        "custom-success",
        ticket_id=TICKET,
    )

    errors = "\n".join(validate_ticket_plan_closed(plan_path, repo_root=tmp_path))

    assert "retired status conflicts with its prior successful-close receipt" in errors


def test_workflow_validation_rejects_coexisting_terminal_receipt_kinds(
    tmp_path: Path,
) -> None:
    plan_path = write_plan(tmp_path)
    create_ticket_retirement_entry(
        repo_root=tmp_path,
        spec_root=Path("specs"),
        ticket_ref=TICKET,
    )
    write_delivered_receipt(
        tmp_path,
        "custom-success",
        ticket_id=TICKET,
    )

    errors = "\n".join(validate_ticket_plan_closed(plan_path, repo_root=tmp_path))

    assert "both successful-close and retirement receipts" in errors
