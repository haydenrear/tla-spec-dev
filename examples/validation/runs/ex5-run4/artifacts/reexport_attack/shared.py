"""Shared cross-package helpers, re-exported through the generated contract."""
from __future__ import annotations

from typing import Any

_TARGETS = {
    "Journal": ("pipeline.ledger.journal", "Journal"),
    "format_entry": ("pipeline.ledger.journal", "format_entry"),
    "Inbox": ("pipeline.ingest.inbox", "Inbox"),
    "Dispatcher": ("pipeline.dispatch.delivery", "Dispatcher"),
}

__all__ = list(_TARGETS)


def __getattr__(name: str) -> Any:
    import importlib

    if name in _TARGETS:
        mod, attr = _TARGETS[name]
        return getattr(importlib.import_module(mod), attr)
    raise AttributeError(name)
