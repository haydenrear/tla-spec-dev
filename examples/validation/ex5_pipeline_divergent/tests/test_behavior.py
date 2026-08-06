"""Behavioral conformance to Pipeline.tla.

This file is BYTE-IDENTICAL in ex4_pipeline_coherent and ex5_pipeline_divergent.
Both must pass. If a fix to the divergent twin's structure changes what this
file asserts, the fix changed behavior, and EV-02 scores that as a failure of
the fix, not a success of the check.

    python3 -m pytest examples/validation/ex4_pipeline_coherent/tests -q
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from driver import Pipeline  # noqa: E402

ITEMS = ["i1", "i2"]


def test_init_matches_model_init() -> None:
    p = Pipeline(ITEMS)
    assert p.state() == {
        "inbox": ["i1", "i2"],
        "accepted": [],
        "queue": [],
        "delivered": [],
        "failed": [],
        "ledger": [],
    }


def test_accept_moves_inbox_to_accepted() -> None:
    p = Pipeline(ITEMS)
    assert p.accept("i1") is True
    assert p.state()["inbox"] == ["i2"]
    assert p.state()["accepted"] == ["i1"]
    assert p.accept("i1") is False


def test_enqueue_requires_accepted_and_is_idempotent() -> None:
    p = Pipeline(ITEMS)
    assert p.enqueue("i1") is False
    p.accept("i1")
    assert p.enqueue("i1") is True
    assert p.enqueue("i1") is False
    assert p.state()["queue"] == ["i1"]


def test_deliver_moves_queue_to_delivered() -> None:
    p = Pipeline(ITEMS)
    p.accept("i1")
    p.enqueue("i1")
    assert p.deliver("i1") is True
    assert p.state()["queue"] == []
    assert p.state()["delivered"] == ["i1"]
    assert p.deliver("i1") is False


def test_fail_moves_delivered_to_failed_and_excludes() -> None:
    p = Pipeline(ITEMS)
    p.accept("i1")
    p.enqueue("i1")
    p.deliver("i1")
    assert p.fail("i1") is True
    assert p.state()["delivered"] == []
    assert p.state()["failed"] == ["i1"]
    assert p.fail("i1") is False
    assert set(p.state()["delivered"]) & set(p.state()["failed"]) == set()


def test_failed_item_cannot_be_redelivered() -> None:
    p = Pipeline(ITEMS)
    p.accept("i1")
    p.enqueue("i1")
    p.deliver("i1")
    p.fail("i1")
    p.enqueue("i1")
    assert p.deliver("i1") is False


def test_record_requires_delivered_and_is_append_only() -> None:
    p = Pipeline(ITEMS)
    assert p.record("i1") is False
    p.accept("i1")
    p.enqueue("i1")
    p.deliver("i1")
    assert p.record("i1") is True
    assert p.record("i1") is False
    assert p.state()["ledger"] == ["i1"]
    ledger = set(p.state()["ledger"])
    assert ledger <= set(p.state()["delivered"]) | set(p.state()["failed"])


def test_two_item_interleaving() -> None:
    p = Pipeline(ITEMS)
    for item in ITEMS:
        p.accept(item)
        p.enqueue(item)
    p.deliver("i2")
    p.record("i2")
    p.deliver("i1")
    p.fail("i1")
    assert p.state() == {
        "inbox": [],
        "accepted": ["i1", "i2"],
        "queue": [],
        "delivered": ["i2"],
        "failed": ["i1"],
        "ledger": ["i2"],
    }
