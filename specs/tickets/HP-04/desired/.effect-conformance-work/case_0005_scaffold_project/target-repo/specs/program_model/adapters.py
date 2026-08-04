"""Adapters for the CliProject program model.

This file carries BOTH executable views. Neither is optional:

- Spec-unit adapters (internal view) drive real internal boundaries for cases
  generated from Internal.tla. Mapped by ``case_adapters.toml``.
- Test Graph adapters (external view) drive the real public surface for cases
  generated from External.tla, then project observed state back into the model
  shape so it can be compared with the generated expected state. Mapped by
  ``testgraph_bindings.yml``.

Read ``references/testgraph_adapters.md`` for the hook order and the
projected-state assertion contract. The worked reference implementation is
``examples/distributed_history/specs/program_model/adapters.py``.

SCAFFOLD: every ``apply``/``observe`` below raises NotImplementedError. Replace
each one with a call into this repository's real boundary. The class names here
must stay in sync with ``case_adapters.toml`` and ``testgraph_bindings.yml``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from spec_double_compiler.runtime import CaseRunResult


def _state(value: Any) -> dict[str, Any]:
    return json.loads(json.dumps(value, sort_keys=True))


# ---------------------------------------------------------------------------
# Spec-unit adapters (internal view) -> case_adapters.toml
#
# Hook order per batch: setup_all -> (run per case) -> teardown_all.
# `run` materializes case.before, applies one internal action, and returns the
# observed output plus the resulting state in the model's shape.
# ---------------------------------------------------------------------------


class _InternalAdapter:
    def setup_all(self, context: Any) -> None:
        """Suite-wide internal setup: open a store, clear shared tables."""

    def teardown_all(self, context: Any) -> None:
        """Suite-wide internal teardown."""

    def run(self, case: Any, work_dir: Path | None = None) -> CaseRunResult:
        store = self.load(case.before)
        output = self.apply(store, case.input.params)
        return CaseRunResult(output=output, after=self.snapshot(store))

    def load(self, before: dict[str, Any]) -> Any:
        """Materialize the generated `before` state in the real component."""
        raise NotImplementedError(
            "load the TLA `before` state into this repository's internal component"
        )

    def snapshot(self, store: Any) -> dict[str, Any]:
        """Observe the real component and return it in the Internal.tla shape."""
        raise NotImplementedError(
            "project this repository's internal state back into the Internal.tla shape"
        )

    def apply(self, store: Any, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class RegisterActorInternalAdapter(_InternalAdapter):
    def apply(self, store: Any, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("call the real RegisterActor boundary")


class AcceptRecordInternalAdapter(_InternalAdapter):
    def apply(self, store: Any, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("call the real AcceptRecord boundary")


class PublishRecordInternalAdapter(_InternalAdapter):
    def apply(self, store: Any, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("call the real PublishRecord boundary")


# ---------------------------------------------------------------------------
# Test Graph adapters (external view) -> testgraph_bindings.yml
#
# Hook order per batch:
#   setup_all -> for each case: setup -> run -> projected-state assertion ->
#   teardown -> ... -> teardown_all
#
# `setup` must establish the abstract pre-state before each case. That is what
# makes leftover residue from a previous case visible instead of silently
# passing.
# ---------------------------------------------------------------------------


class _ExternalAdapter:
    def setup_all(self, context: Any) -> None:
        """Suite-wide external setup: start/await the app, reset shared state.

        For an HTTP service: wait for health, reset the deployment.
        For a CLI: create the workspace root.
        """

    def teardown_all(self, context: Any) -> None:
        """Suite-wide external teardown."""

    def setup(self, context: Any) -> None:
        """Load `context.case.before` into the real system before each case."""
        raise NotImplementedError(
            "materialize the TLA `before` state on the real public surface "
            "(debug/admin endpoint, fixture files, seeded DB, ...)"
        )

    def teardown(self, context: Any) -> None:
        """Clear per-case state so the next case starts from its own `before`."""

    def run(self, case: Any, work_dir: Path | None = None) -> CaseRunResult:
        return CaseRunResult(output=self.apply(case.input.params))

    def apply(self, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class RegisterActorExternalAdapter(_ExternalAdapter):
    def apply(self, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("drive the real public RegisterActor surface")


class AcceptRecordExternalAdapter(_ExternalAdapter):
    def apply(self, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("drive the real public AcceptRecord surface")


class PublishWorkerExternalAdapter(_ExternalAdapter):
    def apply(self, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("drive the real public publish-worker surface")


# ---------------------------------------------------------------------------
# Projected-state assertion (external view)
#
# expected = ExpectedProgramProjection.expected_state(context)  (from case.after)
# actual   = ProgramStateProjector.observe(context)             (from real system)
# compare  = ProjectedStateAssertion.assert_state(context)
# ---------------------------------------------------------------------------


class ExpectedProgramProjection:
    def expected_state(self, context: Any) -> dict[str, Any]:
        return _visible_projection(context.case.after)


class ProgramStateProjector:
    def observe(self, context: Any) -> dict[str, Any]:
        raise NotImplementedError(
            "observe the real system's externally visible state and pass it "
            "through _visible_projection so it can be compared with case.after"
        )


class ProjectedStateAssertion:
    def assert_state(self, context: Any) -> None:
        expected = _state(context.expected)
        actual = _state(context.actual)
        artifact = context.work_dir / "program-state.json"
        payload = {
            "case": context.case.name,
            "action": context.case.input.action,
            "params": dict(context.case.input.params),
            "expected_program_state": expected,
            "actual_projected_program_state": actual,
            "adapter_result": _case_result_payload(context.result),
            "matched": actual == expected,
        }
        artifact.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if actual != expected:
            raise AssertionError(
                f"projected program state mismatch for {context.case.name}; wrote {artifact}"
            )


def _visible_projection(state: dict[str, Any]) -> dict[str, Any]:
    """Keep only what a caller can actually observe.

    Both the expected projection and the live projector go through this, so the
    two sides are always compared in the same shape. Drop internal bookkeeping
    the public surface does not expose.
    """
    return {
        "owners": sorted(state.get("owners", [])),
        "records": dict(state.get("records", {})),
        "projections": dict(state.get("projections", {})),
    }


def _case_result_payload(result: CaseRunResult | None) -> dict[str, Any] | None:
    if result is None:
        return None
    return {
        "output": result.output,
        "after": result.after,
        "semantic_output": result.semantic_output,
    }
