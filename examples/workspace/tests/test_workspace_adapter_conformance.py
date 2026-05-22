from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "generated"))

from workspace_spec.contract_tests import assert_workspace_port_conformance
from workspace_spec.traces import TRACE_FREE_USER_LIMIT_REACHED
from workspace_spec.types import CreateWorkspace, CreateWorkspaceResult, WorkspaceState


class InMemoryWorkspaceAdapter:
    """Tiny production-adapter stand-in used to demonstrate conformance."""

    def __init__(self, state: WorkspaceState):
        self._state = state

    def snapshot(self) -> WorkspaceState:
        return self._state

    def create_workspace(self, command: CreateWorkspace) -> CreateWorkspaceResult:
        owned = self._state.owned[command.user_id]
        limit = self._state.limits[command.user_id]

        if len(owned) >= limit:
            return CreateWorkspaceResult(
                accepted=False,
                reason="WORKSPACE_LIMIT_REACHED",
            )

        self._state = WorkspaceState(
            owned={
                **self._state.owned,
                command.user_id: owned | frozenset({command.workspace_id}),
            },
            limits=self._state.limits,
        )
        return CreateWorkspaceResult(accepted=True)


def adapter_factory(initial_state: WorkspaceState) -> InMemoryWorkspaceAdapter:
    return InMemoryWorkspaceAdapter(initial_state)


def initial_state() -> WorkspaceState:
    return WorkspaceState(
        owned={"u1": frozenset(), "u2": frozenset()},
        limits={"u1": 1, "u2": 2},
    )


def test_workspace_adapter_conforms_to_spec_double() -> None:
    assert_workspace_port_conformance(
        adapter_factory=adapter_factory,
        initial_state=initial_state(),
        commands=TRACE_FREE_USER_LIMIT_REACHED,
    )


if __name__ == "__main__":
    test_workspace_adapter_conforms_to_spec_double()
