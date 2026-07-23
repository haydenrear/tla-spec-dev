"""Agent-authored effect provider for taskq's persistence boundary.

TaskStorePort is the one real effect boundary taskq crosses: the JSON task
map in taskq.json (path chosen via TASKQ_STATE). For each generated case and
deterministic fuzz iteration the provider:

- owns a concrete state file under the point-qualified work_dir, choosing
  deterministic representatives from ``context.derived_seed`` (directory
  flavor: plain/spaces/unicode/nested; and, for an empty modeled before
  state, whether the file exists as ``{}`` or is absent -- both are valid
  concrete representations of "no tasks");
- materializes the modeled ``case.before`` task map into that file on scope
  entry;
- yields a binding implementing the generated TaskStorePort Protocol
  (explicit injection; the spec-unit adapter points TASKQ_STATE at
  ``binding.state_file`` and runs the real CLI);
- on scope exit asserts CONTENT: the persisted task map must equal the
  modeled after-state exactly (which for rejection actions also asserts
  no-write-on-error), every persisted status must be a real taskq status,
  and the persisted map must respect the running cap of 2;
- always cleans up its file tree; cleanup failures stay visible and an
  application failure is never suppressed.

The provider never mutates the generated case: ``case.after`` is the oracle.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from random import Random
from typing import Any

from spec_double_compiler.runtime import EffectProviderContext
from taskq_program_cases.types import LoadTasksResult, PersistTasks, PersistTasksResult

VALID_STATUSES = {"pending", "running", "done"}
MAX_RUNNING = 2

DIRECTORY_FLAVORS = ["plain", "dir with spaces", "unicodé-δ", "nested/deep/dir"]


class ProviderContentAssertionError(AssertionError):
    pass


class TaskStoreBinding:
    """Implements the generated TaskStorePort against one real JSON file."""

    def __init__(self, context: EffectProviderContext) -> None:
        self.context = context
        rng = Random(context.derived_seed)
        flavor = rng.choice(DIRECTORY_FLAVORS)
        self.root = Path(context.work_dir) / "taskq-store"
        self.state_file = self.root / flavor / "taskq.json"
        self.represent_empty_as_file = rng.choice([True, False])
        self.before_tasks = {str(k): str(v) for k, v in dict(context.case.before["tasks"]).items()}
        self.expected_after = {str(k): str(v) for k, v in dict(context.case.after["tasks"]).items()}

    # --- generated TaskStorePort Protocol ---------------------------------

    def load(self) -> LoadTasksResult:
        return LoadTasksResult(tasks=self._read())

    def persist(self, command: PersistTasks) -> PersistTasksResult:
        self._write(dict(command.tasks))
        return PersistTasksResult(persisted=True)

    # --- lifecycle --------------------------------------------------------

    def __enter__(self) -> "TaskStoreBinding":
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        if self.before_tasks or self.represent_empty_as_file:
            self._write(self.before_tasks)
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool:
        content_error: BaseException | None = None
        if exc_type is None:
            actual = self._read()
            point = (
                f"case {self.context.case.name!r} action {self.context.action!r} "
                f"iteration {self.context.iteration} derived_seed {self.context.derived_seed}"
            )
            if actual != self.expected_after:
                content_error = ProviderContentAssertionError(
                    "persisted task map does not match the modeled after-state: "
                    f"persisted {actual!r} != modeled {self.expected_after!r} ({point})"
                )
            elif not set(actual.values()) <= VALID_STATUSES:
                content_error = ProviderContentAssertionError(
                    f"persisted statuses outside taskq STATES: {actual!r} ({point})"
                )
            elif sum(1 for status in actual.values() if status == "running") > MAX_RUNNING:
                content_error = ProviderContentAssertionError(
                    f"persisted map violates the running cap of {MAX_RUNNING}: {actual!r} ({point})"
                )
        cleanup_error: BaseException | None = None
        try:
            if self.root.exists():
                shutil.rmtree(self.root)
        except BaseException as raised:  # keep cleanup failures visible
            cleanup_error = raised
        if cleanup_error is not None:
            cleanup_failure = ProviderContentAssertionError(
                f"provider cleanup failed: {type(cleanup_error).__name__}: {cleanup_error}"
            )
            if content_error is not None:
                raise ExceptionGroup(
                    "provider content and cleanup failures", [content_error, cleanup_failure]
                ) from cleanup_error
            raise cleanup_failure from cleanup_error
        if content_error is not None:
            raise content_error
        return False  # never suppress an application failure

    # --- concrete representation ------------------------------------------

    def _read(self) -> dict[str, str]:
        if not self.state_file.exists():
            return {}
        return {str(k): str(v) for k, v in json.loads(self.state_file.read_text(encoding="utf-8")).items()}

    def _write(self, tasks: dict[str, str]) -> None:
        self.state_file.write_text(json.dumps(tasks, indent=2, sort_keys=True), encoding="utf-8")


class TaskStoreScope:
    def __init__(self, context: EffectProviderContext) -> None:
        self.binding = TaskStoreBinding(context)

    def __enter__(self) -> TaskStoreBinding:
        return self.binding.__enter__()

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool:
        return self.binding.__exit__(exc_type, exc, traceback)


class TaskStoreProvider:
    def bind(self, context: EffectProviderContext) -> TaskStoreScope:
        return TaskStoreScope(context)


taskq_store_provider = TaskStoreProvider()
