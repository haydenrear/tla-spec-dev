from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from application import AtomicPublisher, PublishRequest
from spec_double_compiler.runtime import CaseRunResult


class AtomicPublisherAdapter:
    def setup(self, context: Any) -> None:
        self.filesystem = context.effects["FilesystemPort"]

    def run(self, case: Any, work_dir: Path | None = None) -> CaseRunResult:
        representative = self.filesystem.representative
        expected_revision = {
            "create_success": 0,
            "valid_update": 1,
            "idempotent_retry": 1,
            "stale_revision": 1,
            "read_failure": 1,
            "staged_write_failure": 1,
            "replace_failure": 1,
        }[str(case.before["scenario"])]
        output = AtomicPublisher(self.filesystem).publish(
            PublishRequest(
                final_path=representative["final_path"],
                stage_path=representative["stage_path"],
                record_id=representative["record_id"],
                payload=representative["new_payload"],
                expected_revision=expected_revision,
            )
        )
        actual_after = json.loads(json.dumps(case.after, ensure_ascii=False))
        actual_after["result"] = output
        actual_after["record"] = self.filesystem.project_record()
        self.actual_after = actual_after
        return CaseRunResult(output=output, after=actual_after)

    def teardown(self, context: Any) -> None:
        self.filesystem = None


class ExpectedAtomicProjection:
    def expected_state(self, context: Any) -> dict[str, Any]:
        return dict(context.case.after)


class AtomicStateProjector:
    def observe(self, context: Any) -> dict[str, Any]:
        actual = json.loads(json.dumps(context.case.after, ensure_ascii=False))
        actual["record"] = context.effects["FilesystemPort"].project_record()
        if context.result is not None:
            actual["result"] = context.result.output
        return actual


class AtomicProjectedStateAssertion:
    def assert_state(self, context: Any) -> None:
        artifact = context.work_dir / "projected-state.json"
        matched = context.actual == context.expected
        artifact.write_text(
            json.dumps(
                {
                    "actual": context.actual,
                    "case": context.case.name,
                    "expected": context.expected,
                    "matched": matched,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        if not matched:
            raise AssertionError(f"projected state mismatch for {context.case.name}")
