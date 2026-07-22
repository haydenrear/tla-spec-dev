"""Domain-neutral deterministic support for repository effect providers."""

from __future__ import annotations

import hashlib
import json


EFFECT_SEED_VERSION = "tla-spec-dev/effect-seed/v1"


def derive_effect_seed(root_seed: int, case_name: str, iteration: int, port_name: str) -> int:
    """Return the versioned, process-independent seed for one bound port.

    JSON supplies an unambiguous UTF-8 framing; SHA-256 avoids Python's salted
    ``hash()`` and makes the protocol stable across processes and platforms.
    The first 128 digest bits are ample for project-local ``random.Random``.
    """

    payload = json.dumps(
        [EFFECT_SEED_VERSION, int(root_seed), str(case_name), int(iteration), str(port_name)],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:16], "big")
