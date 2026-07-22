from __future__ import annotations

import errno
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from application import AtomicPublisher, PublishRequest, canonical_record
from atomic_publisher_contract.types import (
    DeleteFile,
    DeleteFileResult,
    ReadFile,
    ReadFileResult,
    ReplaceFile,
    ReplaceFileResult,
    WriteFile,
    WriteFileResult,
)


SCENARIOS = (
    "create_success",
    "valid_update",
    "idempotent_retry",
    "stale_revision",
    "read_failure",
    "staged_write_failure",
    "replace_failure",
)
BASELINE_SCENARIOS = (
    "create_success",
    "valid_update",
    "stale_revision",
    "staged_write_failure",
)


class RealFilesystem:
    """Small typed adapter over a real TemporaryDirectory."""

    def __init__(self, root: Path, scenario: str) -> None:
        self.root = root
        self.final_path = str(root / "unicode space Ω" / "record.json")
        self.stage_path = str(root / "unicode space Ω" / ".record.stage")
        Path(self.final_path).parent.mkdir(parents=True, exist_ok=True)
        self.scenario = scenario
        self.events: list[str] = []
        self.record_id = "real id 終端"
        self.old_payload = "old réel"
        self.new_payload = "new payload 🧪"
        self._materialize_before()

    def read(self, command: ReadFile) -> ReadFileResult:
        if self.scenario == "read_failure":
            self.events.append("read_error")
            raise PermissionError(errno.EACCES, "real adapter injected read denial")
        path = Path(command.path)
        if not path.exists():
            self.events.append("read_missing")
            raise FileNotFoundError(command.path)
        self.events.append("read_found")
        return ReadFileResult(path.read_bytes())

    def write(self, command: WriteFile) -> WriteFileResult:
        role = "stage_write" if command.path == self.stage_path else "write_final"
        if self.scenario == "staged_write_failure":
            self.events.append(f"{role}_error")
            raise OSError(errno.ENOSPC, "real adapter injected full disk")
        self.events.append(role)
        Path(command.path).write_bytes(command.data)
        return WriteFileResult(True)

    def replace(self, command: ReplaceFile) -> ReplaceFileResult:
        normal = command.source == self.stage_path and command.target == self.final_path
        label = "replace" if normal else "replace_reversed"
        if self.scenario == "replace_failure":
            self.events.append(f"{label}_error")
            raise PermissionError(errno.EACCES, "real adapter injected replace denial")
        self.events.append(label)
        os.replace(command.source, command.target)
        return ReplaceFileResult(True)

    def delete(self, command: DeleteFile) -> DeleteFileResult:
        self.events.append("delete")
        path = Path(command.path)
        if not path.exists():
            raise FileNotFoundError(command.path)
        path.unlink()
        return DeleteFileResult(True)

    def project_record(self) -> dict[str, Any]:
        path = Path(self.final_path)
        if not path.exists():
            return {"exists": False, "id": "none", "payload": "none", "revision": 0}
        try:
            value = json.loads(path.read_bytes().decode("utf-8"))
        except Exception:
            return {"exists": True, "id": "invalid", "payload": "invalid", "revision": -1}
        return {
            "exists": True,
            "id": "record" if value.get("id") == self.record_id else f"unexpected:{value.get('id', '<missing>')}",
            "payload": (
                "new"
                if value.get("payload") == self.new_payload
                else "old"
                if value.get("payload") == self.old_payload
                else f"unexpected:{value.get('payload', '<missing>')}"
            ),
            "revision": value.get("revision", -1),
        }

    def request(self) -> PublishRequest:
        expected_revision = 0 if self.scenario == "create_success" else 1
        return PublishRequest(
            final_path=self.final_path,
            stage_path=self.stage_path,
            record_id=self.record_id,
            payload=self.new_payload,
            expected_revision=expected_revision,
        )

    def _materialize_before(self) -> None:
        if self.scenario == "create_success":
            return
        revision = 2 if self.scenario == "stale_revision" else 1
        payload = self.new_payload if self.scenario == "idempotent_retry" else self.old_payload
        Path(self.final_path).write_bytes(canonical_record(self.record_id, payload, revision))


def expected_output(scenario: str) -> dict[str, Any]:
    values = {
        "create_success": ("success", 1, False),
        "valid_update": ("success", 2, False),
        "idempotent_retry": ("success", 1, True),
        "stale_revision": ("stale_revision", 2, False),
        "read_failure": ("read_error", 0, False),
        "staged_write_failure": ("write_error", 1, False),
        "replace_failure": ("replace_error", 1, False),
    }
    status, revision, idempotent = values[scenario]
    return {"idempotent": idempotent, "revision": revision, "status": status}


def expected_record(scenario: str) -> dict[str, Any]:
    if scenario == "create_success":
        return {"exists": True, "id": "record", "payload": "new", "revision": 1}
    if scenario == "valid_update":
        return {"exists": True, "id": "record", "payload": "new", "revision": 2}
    revision = 2 if scenario == "stale_revision" else 1
    payload = "new" if scenario == "idempotent_retry" else "old"
    return {"exists": True, "id": "record", "payload": payload, "revision": revision}


def expected_trace(scenario: str) -> list[str]:
    return {
        "create_success": ["read_missing", "stage_write", "replace"],
        "valid_update": ["read_found", "stage_write", "replace"],
        "idempotent_retry": ["read_found"],
        "stale_revision": ["read_found"],
        "read_failure": ["read_error"],
        "staged_write_failure": ["read_found", "stage_write_error"],
        "replace_failure": ["read_found", "stage_write", "replace_error"],
    }[scenario]


def run_real_filesystem_conformance() -> dict[str, Any]:
    previous = os.environ.pop("ATOMIC_PUBLISHER_MUTANT", None)
    rows: list[dict[str, Any]] = []
    try:
        for scenario in SCENARIOS:
            temp_path: str
            with tempfile.TemporaryDirectory(prefix="atomic-real-conformance-") as raw_root:
                temp_path = raw_root
                filesystem = RealFilesystem(Path(raw_root), scenario)
                output = AtomicPublisher(filesystem).publish(filesystem.request())
                actual_record = filesystem.project_record()
                row = {
                    "actual_output": output,
                    "actual_record": actual_record,
                    "actual_trace": filesystem.events,
                    "expected_output": expected_output(scenario),
                    "expected_record": expected_record(scenario),
                    "expected_trace": expected_trace(scenario),
                    "scenario": scenario,
                }
                row["matched"] = (
                    row["actual_output"] == row["expected_output"]
                    and row["actual_record"] == row["expected_record"]
                    and row["actual_trace"] == row["expected_trace"]
                )
                rows.append(row)
            if Path(temp_path).exists():
                raise AssertionError(f"TemporaryDirectory leaked after {scenario}: {temp_path}")
    finally:
        if previous is not None:
            os.environ["ATOMIC_PUBLISHER_MUTANT"] = previous
    if not all(row["matched"] for row in rows):
        raise AssertionError(f"real filesystem conformance failed: {rows!r}")
    return {"cleanup": "green", "outcomes": rows, "verdict": "green"}


def run_hand_written_baseline(mutants: list[str]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    previous = os.environ.get("ATOMIC_PUBLISHER_MUTANT")
    try:
        for mutant in mutants:
            os.environ["ATOMIC_PUBLISHER_MUTANT"] = mutant
            detectors: set[str] = set()
            for scenario in BASELINE_SCENARIOS:
                with tempfile.TemporaryDirectory(prefix="atomic-hand-baseline-") as raw_root:
                    filesystem = RealFilesystem(Path(raw_root), scenario)
                    output = AtomicPublisher(filesystem).publish(filesystem.request())
                    if output != expected_output(scenario):
                        detectors.add("tla_output")
                    if filesystem.project_record() != expected_record(scenario):
                        detectors.add("tla_projected_state")
                    if filesystem.events != expected_trace(scenario):
                        detectors.add("hand_protocol_assertion")
            results.append(
                {
                    "mutant_id": mutant,
                    "triggered_detectors": sorted(detectors),
                    "verdict": "killed" if detectors else "survived",
                }
            )
    finally:
        if previous is None:
            os.environ.pop("ATOMIC_PUBLISHER_MUTANT", None)
        else:
            os.environ["ATOMIC_PUBLISHER_MUTANT"] = previous
    killed = sum(row["verdict"] == "killed" for row in results)
    return {
        "killed": killed,
        "mutants": results,
        "scenarios": list(BASELINE_SCENARIOS),
        "score": f"{killed}/{len(results)}",
    }
