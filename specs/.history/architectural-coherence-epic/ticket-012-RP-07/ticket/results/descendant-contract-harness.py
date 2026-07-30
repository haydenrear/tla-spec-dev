"""Mimic the test-graph executor's descendant contract around an arbitrary command.

Spawns argv, polls the process table accumulating every descendant PID ever
observed, and after the launcher exits reports which of them are still alive.
"""
from __future__ import annotations

import os
import subprocess
import sys
import threading
import time


def snapshot():
    out = subprocess.run(
        ["ps", "-eo", "pid=,ppid=,args="], capture_output=True, text=True
    ).stdout
    table = {}
    for line in out.splitlines():
        parts = line.split(None, 2)
        if len(parts) < 2:
            continue
        try:
            pid, ppid = int(parts[0]), int(parts[1])
        except ValueError:
            continue
        table[pid] = (ppid, parts[2] if len(parts) > 2 else "")
    return table


def descendants(table, root):
    children = {}
    for pid, (ppid, _) in table.items():
        children.setdefault(ppid, []).append(pid)
    seen, stack = set(), list(children.get(root, []))
    while stack:
        pid = stack.pop()
        if pid in seen:
            continue
        seen.add(pid)
        stack.extend(children.get(pid, []))
    return seen


def main():
    argv = sys.argv[1:]
    cwd = os.environ.get("PROBE_CWD")
    log = open(os.environ.get("PROBE_LOG", "/dev/null"), "wb")
    proc = subprocess.Popen(argv, cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
    observed = {}
    stop = threading.Event()

    def poll():
        while not stop.is_set():
            table = snapshot()
            for pid in descendants(table, proc.pid):
                observed.setdefault(pid, table[pid][1])
            time.sleep(0.15)

    t = threading.Thread(target=poll, daemon=True)
    t.start()
    code = proc.wait()
    stop.set()
    t.join(timeout=2)

    table = snapshot()
    alive = {pid: cmd for pid, cmd in observed.items() if pid in table}
    print(f"launcher exit={code} observed_descendants={len(observed)}")
    print(f"LIVE AFTER EXIT: {len(alive)}")
    for pid, cmd in alive.items():
        print(f"  {pid}: {cmd[:160]}")
    return 0 if not alive else 3


if __name__ == "__main__":
    sys.exit(main())
