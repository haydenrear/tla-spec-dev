from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from spec_double_compiler.runtime import CaseRunResult


PROJECT_ROOT = Path(__file__).resolve().parent
SPEC_GENERATED = PROJECT_ROOT / "specs" / "program_model" / "generated"


class AtomicPublisherCliAdapter:
    """Drive the application through a subprocess and observable files only."""

    def run(self, case: Any, work_dir: Path | None = None) -> CaseRunResult:
        if work_dir is None:
            raise ValueError("CLI adapter requires a case work directory")
        root = work_dir / "cli-filesystem"
        result_path = work_dir / "cli-result.json"
        env = os.environ.copy()
        python_path = os.pathsep.join([str(SPEC_GENERATED), str(PROJECT_ROOT)])
        env["PYTHONPATH"] = python_path + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "atomic_cli.py"),
                "--root",
                str(root),
                "--scenario",
                str(case.before["scenario"]),
                "--result",
                str(result_path),
            ],
            cwd=PROJECT_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
        if completed.returncode != 0:
            raise AssertionError(
                f"atomic CLI failed with {completed.returncode}: {completed.stdout}\n{completed.stderr}"
            )
        payload = json.loads(result_path.read_text(encoding="utf-8"))
        return CaseRunResult(output=payload["output"])


class ExpectedCliProjection:
    def expected_state(self, context: Any) -> dict[str, Any]:
        return dict(context.case.after)


class AtomicPublisherCliProjector:
    def observe(self, context: Any) -> dict[str, Any]:
        payload = json.loads((context.work_dir / "cli-result.json").read_text(encoding="utf-8"))
        actual = json.loads(json.dumps(context.case.after, ensure_ascii=False))
        actual["record"] = payload["record"]
        actual["result"] = payload["output"]
        actual["trace"] = payload["trace"]
        return actual


class AtomicCliAssertion:
    def assert_state(self, context: Any) -> None:
        if context.actual != context.expected:
            raise AssertionError(
                f"atomic CLI projected state mismatch for {context.case.name}: "
                f"{context.actual!r} != {context.expected!r}"
            )
