from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "generated"))

from workspace_spec.fake import WorkspaceSpecDouble
from workspace_spec.traces import TRACE_FREE_USER_LIMIT_REACHED
from workspace_spec.types import CreateWorkspace, WorkspaceState
from workspace_spec.validators import validate_state, validate_trace


def initial_state() -> WorkspaceState:
    return WorkspaceState(
        owned={"u1": frozenset(), "u2": frozenset()},
        limits={"u1": 1, "u2": 2},
    )


def test_create_workspace_accepts_until_limit() -> None:
    fake = WorkspaceSpecDouble(initial_state())

    result = fake.create_workspace(CreateWorkspace(user_id="u1", workspace_id="w1"))

    assert result.accepted
    assert result.reason is None
    assert fake.snapshot().owned["u1"] == frozenset({"w1"})
    validate_state(fake.snapshot())


def test_create_workspace_rejects_above_limit() -> None:
    fake = WorkspaceSpecDouble(initial_state())

    assert fake.create_workspace(CreateWorkspace(user_id="u1", workspace_id="w1")).accepted
    before = fake.snapshot()
    result = fake.create_workspace(CreateWorkspace(user_id="u1", workspace_id="w2"))

    assert not result.accepted
    assert result.reason == "WORKSPACE_LIMIT_REACHED"
    assert fake.snapshot() == before
    validate_state(fake.snapshot())


def test_generated_trace_replays() -> None:
    fake = WorkspaceSpecDouble(initial_state())

    validate_trace(initial_state(), TRACE_FREE_USER_LIMIT_REACHED, fake)


if __name__ == "__main__":
    test_create_workspace_accepts_until_limit()
    test_create_workspace_rejects_above_limit()
    test_generated_trace_replays()
