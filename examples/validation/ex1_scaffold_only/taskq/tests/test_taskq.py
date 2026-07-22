import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import taskq


def test_add_then_start_then_finish():
    tasks = {}
    assert taskq.add(tasks, "a") == "added a"
    assert taskq.start(tasks, "a") == "started a"
    assert taskq.finish(tasks, "a") == "finished a"
    assert tasks == {"a": "done"}


def test_duplicate_add_rejected():
    tasks = {"a": "pending"}
    assert taskq.add(tasks, "a").startswith("error:")


def test_start_requires_pending():
    tasks = {"a": "done"}
    assert taskq.start(tasks, "a").startswith("error:")
    assert taskq.start(tasks, "missing").startswith("error:")


def test_running_cap_enforced():
    tasks = {"a": "pending", "b": "pending", "c": "pending"}
    assert taskq.start(tasks, "a") == "started a"
    assert taskq.start(tasks, "b") == "started b"
    assert taskq.start(tasks, "c") == "error: too many running tasks"


def test_finish_requires_running():
    tasks = {"a": "pending"}
    assert taskq.finish(tasks, "a").startswith("error:")


def test_listing_sorted():
    tasks = {"b": "pending", "a": "done"}
    assert taskq.listing(tasks) == "a: done\nb: pending"
