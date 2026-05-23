from __future__ import annotations

from pathlib import Path


class WorkspaceCaseAdapter:
    """Example whole-program adapter for TLC-derived state graph cases."""

    def validate(self, case) -> None:
        if "Create" not in case.labels:
            raise AssertionError(f"unsupported case labels: {sorted(case.labels)}")

    def run(self, case, work_dir: Path):
        work_dir.mkdir(parents=True, exist_ok=True)
        return {"output": case.output, "after": case.after}
