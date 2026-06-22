from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class CaseRunResult:
    output: Any = None
    after: Any = None
    semantic_output: Any = None


@dataclass
class AdapterBatchContext:
    kind: str
    cases: list[Any]
    work_dir: Path
    mapping: Any
    shared: dict[str, Any]


@dataclass
class AdapterCaseContext:
    kind: str
    case: Any
    work_dir: Path
    mapping: Any
    shared: dict[str, Any]
    result: CaseRunResult | None = None
    error: BaseException | None = None


@dataclass
class ProjectedStateAssertionContext:
    kind: str
    case: Any
    work_dir: Path
    mapping: Any
    shared: dict[str, Any]
    result: CaseRunResult | None
    expected: Any = None
    actual: Any = None


@runtime_checkable
class CaseAdapter(Protocol):
    def run(self, case: Any, work_dir: Path | None = None) -> CaseRunResult | dict[str, Any] | None:
        ...


def load_object(path: str) -> Any:
    module_name, sep, object_name = path.partition(":")
    if not sep:
        raise ValueError(f"adapter path must be module:object, got {path!r}")
    module = importlib.import_module(module_name)
    obj: Any = module
    for part in object_name.split("."):
        obj = getattr(obj, part)
    return obj


def instantiate(obj: Any) -> Any:
    if isinstance(obj, type):
        return obj()
    if callable(obj) and not hasattr(obj, "run"):
        return obj()
    return obj


def normalize_result(result: Any) -> CaseRunResult:
    if result is None:
        return CaseRunResult()
    if isinstance(result, CaseRunResult):
        return result
    if isinstance(result, dict):
        return CaseRunResult(
            output=result.get("output"),
            after=result.get("after"),
            semantic_output=result.get("semantic_output"),
        )
    return CaseRunResult(
        output=getattr(result, "output", None),
        after=getattr(result, "after", None),
        semantic_output=getattr(result, "semantic_output", None),
    )


def call_adapter(adapter: Any, case: Any, work_dir: Path | None = None) -> CaseRunResult:
    validate = getattr(adapter, "validate", None)
    if validate is not None:
        validate(case)
    run = getattr(adapter, "run", None)
    if run is None:
        raise TypeError(f"adapter {adapter!r} does not define run(case, ...)")
    try:
        result = run(case, work_dir=work_dir)
    except TypeError as exc:
        if "work_dir" not in str(exc):
            raise
        result = run(case)
    return normalize_result(result)


def adapter_accepts_case(adapter: Any, case: Any) -> tuple[bool, str | None]:
    can_run = getattr(adapter, "can_run", None)
    if can_run is not None:
        accepted = can_run(case)
        if isinstance(accepted, tuple):
            return bool(accepted[0]), None if len(accepted) < 2 else str(accepted[1])
        return bool(accepted), None
    validate = getattr(adapter, "validate", None)
    if validate is not None:
        try:
            validate(case)
        except Exception as exc:
            return False, str(exc)
    return True, None


def project_expected_output(projector: Any, case: Any) -> Any:
    try:
        return projector(case)
    except TypeError as exc:
        if "positional" not in str(exc) and "argument" not in str(exc):
            raise
        return projector(case.before, case.input, case.after, case.output)


def assert_case_result(
    *,
    case: Any,
    result: CaseRunResult,
    projector: Any | None = None,
) -> None:
    if result.output is not None and result.output != case.output:
        raise AssertionError(f"adapter output mismatch for {case.name}: {result.output!r} != {case.output!r}")
    if result.after is not None and result.after != case.after:
        raise AssertionError(f"adapter after-state mismatch for {case.name}")
    if projector is not None:
        expected = project_expected_output(projector, case)
        if result.semantic_output != expected:
            raise AssertionError(
                f"adapter semantic output mismatch for {case.name}: {result.semantic_output!r} != {expected!r}"
            )
