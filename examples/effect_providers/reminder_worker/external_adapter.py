"""Drive the reminder worker through its public process boundary."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from spec_double_compiler.runtime import CaseRunResult


PROJECT_ROOT = Path(__file__).resolve().parent
GENERATED_ROOT = PROJECT_ROOT / "specs" / "generated"


class ReminderProcessAdapter:
    def run(self, case: Any, work_dir: Path | None = None) -> CaseRunResult:
        if work_dir is None:
            raise ValueError("process adapter requires a case work directory")
        result_path = work_dir / "process-result.json"
        environment = os.environ.copy()
        environment.pop("REMINDER_MUTANT", None)
        generated_root = Path(
            environment.get("REMINDER_GENERATED_ROOT", str(GENERATED_ROOT))
        ).resolve()
        python_path = os.pathsep.join((str(generated_root), str(PROJECT_ROOT)))
        if environment.get("PYTHONPATH"):
            python_path += os.pathsep + environment["PYTHONPATH"]
        environment["PYTHONPATH"] = python_path
        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "reminder_cli.py"),
                "--root",
                str(work_dir / "process-state"),
                "--scenario",
                str(case.before["scenario"]),
                "--result",
                str(result_path),
            ],
            cwd=PROJECT_ROOT,
            env=environment,
            text=True,
            capture_output=True,
            timeout=10,
        )
        if completed.returncode != 0:
            raise AssertionError(
                f"reminder process failed with {completed.returncode}: "
                f"{completed.stdout}\n{completed.stderr}"
            )
        payload = json.loads(result_path.read_text(encoding="utf-8"))
        return CaseRunResult(output=payload["output"], after=payload["after"])
