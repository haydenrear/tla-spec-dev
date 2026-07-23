#!/usr/bin/env python3
"""taskq -- a tiny task queue CLI.

Tasks move pending -> running -> done. At most two tasks run at once.
State persists in taskq.json next to this file (or TASKQ_STATE if set).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

MAX_RUNNING = 2
STATES = ("pending", "running", "done")


def state_path() -> Path:
    return Path(os.environ.get("TASKQ_STATE", Path(__file__).parent / "taskq.json"))


def load() -> dict[str, str]:
    path = state_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save(tasks: dict[str, str]) -> None:
    state_path().write_text(json.dumps(tasks, indent=2, sort_keys=True))


def add(tasks: dict[str, str], name: str) -> str:
    if name in tasks:
        return f"error: task {name!r} already exists"
    tasks[name] = "pending"
    return f"added {name}"


def start(tasks: dict[str, str], name: str) -> str:
    if tasks.get(name) != "pending":
        return f"error: task {name!r} is not pending"
    if sum(1 for s in tasks.values() if s == "running") >= MAX_RUNNING:
        return "error: too many running tasks"
    tasks[name] = "running"
    return f"started {name}"


def finish(tasks: dict[str, str], name: str) -> str:
    if tasks.get(name) != "running":
        return f"error: task {name!r} is not running"
    tasks[name] = "done"
    return f"finished {name}"


def listing(tasks: dict[str, str]) -> str:
    if not tasks:
        return "(empty)"
    return "\n".join(f"{name}: {status}" for name, status in sorted(tasks.items()))


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: taskq.py add|start|finish|list [name]")
        return 2
    command, args = argv[0], argv[1:]
    tasks = load()
    if command == "list":
        print(listing(tasks))
        return 0
    if command not in ("add", "start", "finish") or len(args) != 1:
        print("usage: taskq.py add|start|finish|list [name]")
        return 2
    result = {"add": add, "start": start, "finish": finish}[command](tasks, args[0])
    print(result)
    if result.startswith("error:"):
        return 1
    save(tasks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
