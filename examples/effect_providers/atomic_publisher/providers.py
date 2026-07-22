from __future__ import annotations

import errno
import hashlib
import json
import random
import shutil
import time
from pathlib import Path
from typing import Any

from application import canonical_record
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


ACTIVE_BINDINGS = 0


class ProviderContractViolation(AssertionError):
    pass


class PassiveBypassDetected(ProviderContractViolation):
    pass


class AtomicFilesystemBinding:
    def __init__(self, context: Any) -> None:
        self.context = context
        self.started = time.perf_counter()
        self.rng = random.Random(context.derived_seed)
        component = self.rng.choice(
            ["space heavy", "unicodé-δ", "emoji-🧪", "nested name"]
        )
        self.root = context.work_dir / "provider-root" / component
        self.final_path = str(self.root / "record.json")
        self.stage_path = str(self.root / ".record.stage")
        self.path_component = component
        self.record_id = self.rng.choice(
            ["order Ω", "record-δ", "id with spaces", "終端-🧪"]
        )
        self.old_payload = self.rng.choice(
            ["old value", "ancien-ç", "以前", "old\nline"]
        )
        self.new_payload = self.rng.choice(
            ["new value", "nouveau-δ", "更新 🧪", "new\tvalue"]
        )
        self.files: dict[str, bytes] = {}
        self.events: list[dict[str, Any]] = []
        self._physical_before: set[str] = set()
        self._configure_before_state()
        self._configure_fault()
        for index in self.rng.sample(range(20), k=3):
            path = str(self.root / f"unrelated-{index:02d}.json")
            self.files[path] = f"unrelated:{index}".encode("utf-8")

    @property
    def representative(self) -> dict[str, Any]:
        return {
            "final_path": self.final_path,
            "stage_path": self.stage_path,
            "record_id": self.record_id,
            "old_payload": self.old_payload,
            "new_payload": self.new_payload,
            "path_component": self.path_component,
        }

    def read(self, command: ReadFile) -> ReadFileResult:
        if command.path != self.final_path:
            self._event("read_unexpected", command.path)
            raise AssertionError(f"read from unexpected path {command.path!r}")
        if self.read_error is not None:
            self._event("read_error", command.path, error=type(self.read_error).__name__)
            raise self.read_error
        if command.path not in self.files:
            self._event("read_missing", command.path)
            raise FileNotFoundError(command.path)
        self._event("read_found", command.path)
        return ReadFileResult(self.files[command.path])

    def write(self, command: WriteFile) -> WriteFileResult:
        role = self._role(command.path)
        label = "stage_write" if role == "stage" else "write_final"
        if self.write_error is not None:
            self._event(f"{label}_error", command.path, data=command.data, error=type(self.write_error).__name__)
            raise self.write_error
        self._event(label, command.path, data=command.data)
        self.files[command.path] = bytes(command.data)
        return WriteFileResult(True)

    def replace(self, command: ReplaceFile) -> ReplaceFileResult:
        source_role = self._role(command.source)
        target_role = self._role(command.target)
        label = "replace" if (source_role, target_role) == ("stage", "final") else "replace_reversed"
        if self.replace_error is not None:
            self._event(f"{label}_error", command.source, target=command.target, error=type(self.replace_error).__name__)
            raise self.replace_error
        self._event(label, command.source, target=command.target)
        if command.source not in self.files:
            raise FileNotFoundError(command.source)
        self.files[command.target] = self.files.pop(command.source)
        return ReplaceFileResult(True)

    def delete(self, command: DeleteFile) -> DeleteFileResult:
        self._event(f"delete_{self._role(command.path)}", command.path)
        if command.path not in self.files:
            raise FileNotFoundError(command.path)
        del self.files[command.path]
        return DeleteFileResult(True)

    def project_record(self) -> dict[str, Any]:
        raw = self.files.get(self.final_path)
        if raw is None:
            return {"exists": False, "id": "none", "payload": "none", "revision": 0}
        try:
            value = json.loads(raw.decode("utf-8"))
        except Exception:
            return {"exists": True, "id": "invalid", "payload": "invalid", "revision": -1}
        record_id = "record" if value.get("id") == self.record_id else f"unexpected:{value.get('id', '<missing>')}"
        payload_value = value.get("payload", "<missing>")
        if payload_value == self.new_payload:
            payload = "new"
        elif payload_value == self.old_payload:
            payload = "old"
        else:
            payload = f"unexpected:{payload_value}"
        revision = value.get("revision", -1)
        return {
            "exists": True,
            "id": record_id,
            "payload": payload,
            "revision": revision,
        }

    def __enter__(self) -> "AtomicFilesystemBinding":
        global ACTIVE_BINDINGS
        self.root.mkdir(parents=True, exist_ok=True)
        self._physical_before = self._physical_files()
        ACTIVE_BINDINGS += 1
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool:
        global ACTIVE_BINDINGS
        physical_after = self._physical_files()
        bypass_paths = sorted(physical_after - self._physical_before)
        expected_trace = list(self.context.case.after["trace"])
        actual_trace = [str(event["event"]) for event in self.events]
        local_error: BaseException | None = None
        if bypass_paths:
            relative_bypass_paths = [self._relative_path(path) for path in bypass_paths]
            local_error = PassiveBypassDetected(
                "physical filesystem bypass outside FilesystemPort: "
                f"{relative_bypass_paths}"
            )
        elif self.stage_path in self.files:
            local_error = ProviderContractViolation(
                "staging file remains after publisher returned"
            )
        elif actual_trace != expected_trace:
            local_error = ProviderContractViolation(
                f"filesystem protocol mismatch: expected {expected_trace!r}, actual {actual_trace!r}"
            )

        transcript_digest = self.transcript_digest()
        lifecycle_root = self.root.parent
        cleanup_error: BaseException | None = None
        try:
            if lifecycle_root.exists():
                shutil.rmtree(lifecycle_root)
        except BaseException as exc:
            cleanup_error = exc
        remaining_paths = []
        if lifecycle_root.exists():
            remaining_paths = [
                str(path.relative_to(self.context.work_dir))
                for path in (lifecycle_root, *sorted(lifecycle_root.rglob("*")))
            ]
        ACTIVE_BINDINGS -= 1
        payload = {
            "action": self.context.action,
            "case": self.context.case.name,
            "choice": {
                "path_component": self.path_component,
                "record_id": self.record_id,
                "old_payload": self.old_payload,
                "new_payload": self.new_payload,
                "read_error": type(self.read_error).__name__ if self.read_error else None,
                "write_error": type(self.write_error).__name__ if self.write_error else None,
                "replace_error": type(self.replace_error).__name__ if self.replace_error else None,
            },
            "derived_seed": self.context.derived_seed,
            "duration_ms": round((time.perf_counter() - self.started) * 1000.0, 6),
            "events": self.events,
            "iteration": self.context.iteration,
            "leaked_paths": remaining_paths,
            "bypass_paths_detected": [self._relative_path(path) for path in bypass_paths],
            "provider_state_after_run": (
                "clean"
                if ACTIVE_BINDINGS == 0 and not remaining_paths
                else f"active:{ACTIVE_BINDINGS};remaining:{len(remaining_paths)}"
            ),
            "root_seed": self.context.root_seed,
            "transcript_digest": transcript_digest,
        }
        print("ATOMIC_POINT " + json.dumps(payload, ensure_ascii=False, sort_keys=True), flush=True)
        if cleanup_error is not None:
            cleanup_failure = ProviderContractViolation(
                f"provider cleanup failed with remaining paths {remaining_paths!r}: "
                f"{type(cleanup_error).__name__}: {cleanup_error}"
            )
            if local_error is not None:
                raise ExceptionGroup(
                    "provider semantic and cleanup failures",
                    [local_error, cleanup_failure],
                ) from cleanup_error
            raise cleanup_failure from cleanup_error
        if remaining_paths:
            cleanup_failure = ProviderContractViolation(
                f"provider cleanup left paths behind: {remaining_paths!r}"
            )
            if local_error is not None:
                raise ExceptionGroup(
                    "provider semantic and cleanup failures",
                    [local_error, cleanup_failure],
                )
            raise cleanup_failure
        if local_error is not None:
            raise local_error
        return False

    def transcript_digest(self) -> str:
        canonical = {
            "case": self.context.case.name,
            "choice": self.representative | {
                "final_path": "final",
                "stage_path": "stage",
            },
            "derived_seed": self.context.derived_seed,
            "events": self.events,
            "iteration": self.context.iteration,
        }
        encoded = json.dumps(
            canonical,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def _configure_before_state(self) -> None:
        record = dict(self.context.case.before["record"])
        if not record["exists"]:
            return
        payload = self.new_payload if record["payload"] == "new" else self.old_payload
        self.files[self.final_path] = canonical_record(
            self.record_id,
            payload,
            int(record["revision"]),
        )

    def _configure_fault(self) -> None:
        scenario = str(self.context.case.before["scenario"])
        self.read_error = None
        self.write_error = None
        self.replace_error = None
        if scenario == "read_failure":
            self.read_error = self.rng.choice(
                [PermissionError(errno.EACCES, "modeled read denied"), OSError(errno.EIO, "modeled read I/O failure")]
            )
        elif scenario == "staged_write_failure":
            self.write_error = self.rng.choice(
                [PermissionError(errno.EACCES, "modeled stage denied"), OSError(errno.ENOSPC, "modeled stage full")]
            )
        elif scenario == "replace_failure":
            self.replace_error = self.rng.choice(
                [PermissionError(errno.EACCES, "modeled replace denied"), OSError(errno.EIO, "modeled replace I/O failure")]
            )

    def _event(self, event: str, path: str, *, data: bytes | None = None, **extra: Any) -> None:
        row: dict[str, Any] = {"event": event, "path": self._role(path)}
        if data is not None:
            row["bytes_sha256"] = hashlib.sha256(data).hexdigest()
            row["bytes_length"] = len(data)
        for key, value in sorted(extra.items()):
            row[key] = self._role(value) if key == "target" else value
        self.events.append(row)

    def _role(self, path: str) -> str:
        if path == self.final_path:
            return "final"
        if path == self.stage_path:
            return "stage"
        return f"other:{Path(path).name}"

    def _physical_files(self) -> set[str]:
        if not self.root.exists():
            return set()
        return {str(path) for path in self.root.rglob("*") if path.is_file()}

    def _relative_path(self, path: str) -> str:
        try:
            return str(Path(path).relative_to(self.root))
        except ValueError:
            return path


class AtomicFilesystemScope:
    def __init__(self, context: Any) -> None:
        self.binding = AtomicFilesystemBinding(context)

    def __enter__(self) -> AtomicFilesystemBinding:
        return self.binding.__enter__()

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool:
        return self.binding.__exit__(exc_type, exc, traceback)


class AtomicFilesystemProvider:
    def bind(self, context: Any) -> AtomicFilesystemScope:
        return AtomicFilesystemScope(context)


filesystem_provider = AtomicFilesystemProvider()
