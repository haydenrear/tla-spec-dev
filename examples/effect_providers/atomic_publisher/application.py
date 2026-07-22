from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from atomic_publisher_contract.ports import FilesystemPort
from atomic_publisher_contract.types import (
    DeleteFile,
    ReadFile,
    ReplaceFile,
    WriteFile,
)


MUTANTS = {f"AP-{index:02d}" for index in range(1, 13)}


@dataclass(frozen=True)
class PublishRequest:
    final_path: str
    stage_path: str
    record_id: str
    payload: str
    expected_revision: int


def canonical_record(record_id: str, payload: str, revision: int) -> bytes:
    """The byte-level contract: UTF-8, sorted keys, and no incidental spaces."""

    value = {"id": record_id, "payload": payload, "revision": revision}
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


class AtomicPublisher:
    def __init__(self, filesystem: FilesystemPort) -> None:
        self._filesystem = filesystem

    def publish(self, request: PublishRequest) -> dict[str, Any]:
        mutant = _selected_mutant()
        existing: dict[str, Any] | None
        try:
            existing_bytes = self._filesystem.read(ReadFile(request.final_path)).data
            existing = json.loads(existing_bytes.decode("utf-8"))
        except FileNotFoundError:
            existing = None
        except OSError:
            if mutant == "AP-05":
                existing = None
            else:
                return _result("read_error", 0)

        current_revision = int(existing["revision"]) if existing is not None else 0
        stale_mutation = False
        if existing is not None:
            if (
                existing.get("id") == request.record_id
                and existing.get("payload") == request.payload
                and current_revision == request.expected_revision
            ):
                return _result("success", current_revision, idempotent=True)
            if current_revision != request.expected_revision:
                if mutant != "AP-04":
                    return _result("stale_revision", current_revision)
                stale_mutation = True

        next_revision = current_revision + 1
        if mutant == "AP-03" and existing is not None:
            next_revision += 1

        encoded_id = request.record_id
        encoded_payload: str | None = request.payload
        if mutant == "AP-02":
            encoded_id = request.record_id[:-1]
        if mutant == "AP-01":
            encoded_payload = None
        data = _mutated_canonical_record(encoded_id, encoded_payload, next_revision)

        try:
            if mutant == "AP-09":
                self._filesystem.write(WriteFile(request.final_path, data))
                return _result("success", next_revision)
            if mutant == "AP-12":
                Path(request.stage_path).write_bytes(data)
            else:
                self._filesystem.write(WriteFile(request.stage_path, data))
            if mutant == "AP-11":
                self._filesystem.write(WriteFile(request.stage_path, data))
        except OSError:
            if mutant == "AP-08":
                self._delete_final(request.final_path)
            if mutant == "AP-06":
                return _result("success", next_revision)
            return _result("write_error", current_revision)

        try:
            if mutant == "AP-10":
                self._filesystem.replace(ReplaceFile(request.final_path, request.stage_path))
            else:
                self._filesystem.replace(ReplaceFile(request.stage_path, request.final_path))
        except OSError:
            if mutant == "AP-08":
                self._delete_final(request.final_path)
            if mutant == "AP-07":
                return _result("success", next_revision)
            return _result("replace_error", current_revision)
        if stale_mutation:
            return _result("stale_revision", current_revision)
        return _result("success", next_revision)

    def _delete_final(self, final_path: str) -> None:
        try:
            self._filesystem.delete(DeleteFile(final_path))
        except FileNotFoundError:
            pass


def _selected_mutant() -> str | None:
    value = os.environ.get("ATOMIC_PUBLISHER_MUTANT") or None
    if value is not None and value not in MUTANTS:
        raise ValueError(f"unknown atomic publisher mutant {value!r}")
    return value


def _mutated_canonical_record(record_id: str, payload: str | None, revision: int) -> bytes:
    value: dict[str, Any] = {"id": record_id, "revision": revision}
    if payload is not None:
        value["payload"] = payload
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _result(status: str, revision: int, *, idempotent: bool = False) -> dict[str, Any]:
    return {"idempotent": idempotent, "revision": revision, "status": status}
