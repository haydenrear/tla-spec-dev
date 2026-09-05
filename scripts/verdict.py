#!/usr/bin/env python3
"""A machine-readable verdict, so nothing has to match on a sentence.

**41 of the instrument registry's 103 demonstration slots assert on literal
output strings**, and **13 of the 29 failures it reports today are pure prose
drift** -- `corpus_diagnostics.py` moved from *"Every component is within cap"*
to *"Every {scope} is within cap"*, the scope became `action`, and a
demonstration that had been correct for months began reporting the instrument
broken. The instrument was not broken. Nobody had said anything false. The
coupling was a sentence.

That coupling is the largest defect generator in this project's record:
`UNMODELED/yaml-parser` is 7 findings in a hand-rolled parser,
`UNMODELED/agent-harness` is 2 in hand-rolled shell parsing, `G-11` is a stale
line-number reference, and the instrument registry is the rest. **One part of the
system prints prose; another part matches on it.**

So a gate states its verdict as data:

```json
{"schema_version": 1, "instrument": "corpus-diagnostics",
 "verdict": "fail", "reason": "over_cap", "detail": {"cap": 50, "worst": 200}}
```

`verdict` is the outcome. **`reason` is the load-bearing field**: a stable
snake_case code naming WHY, which a demonstration can assert against and which
survives every rewording of the prose beside it. `detail` is free-form numbers
for a reader; nothing should assert on its shape.

Prose does not go away and should not: the sentence a person reads when a gate
refuses is this project's best work, and `#301`'s remedy text is a finding of
its own. What changes is that **no automated consumer reads it.**
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

#: Only two outcomes. `UNDECIDED` deliberately absent: a gate that could not
#: measure something reports `fail` with a reason saying so, because `SS-02`'s
#: rule is that an absent input is never a PASS, and a third value invites a
#: consumer to treat it as one.
VERDICTS = ("pass", "fail")


@dataclass(frozen=True)
class Verdict:
    """What a gate decided, in a form nothing has to parse out of English."""

    instrument: str
    verdict: str
    reason: str
    detail: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.verdict not in VERDICTS:
            raise ValueError(f"verdict must be one of {VERDICTS}, got {self.verdict!r}")
        if not self.reason or self.reason != self.reason.strip():
            raise ValueError(f"reason must be a non-empty stable code, got {self.reason!r}")
        if any(ch.isupper() or ch.isspace() for ch in self.reason):
            # A reason with spaces or capitals is a sentence wearing a field
            # name, and it will drift exactly like the sentences this exists to
            # replace.
            raise ValueError(
                f"reason must be a stable snake_case code, not prose: {self.reason!r}"
            )

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "instrument": self.instrument,
            "verdict": self.verdict,
            "reason": self.reason,
            "detail": self.detail,
        }

    def write(self, path: Path | str | None) -> None:
        """Write the verdict, if a path was asked for. A no-op otherwise.

        Gates call this unconditionally with whatever `--verdict-json` held, so
        that emitting a verdict never becomes a branch a caller has to remember.
        """
        if not path:
            return
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.as_dict(), indent=2) + "\n", encoding="utf-8")


def read(path: Path | str) -> dict[str, Any]:
    """Read a verdict file, refusing anything that is not one.

    Refuses rather than returning a default: a consumer that silently treats an
    unreadable verdict as absent turns a broken gate into a quiet pass, which is
    the failure this whole file exists to remove.
    """
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    for key in ("schema_version", "instrument", "verdict", "reason"):
        if key not in payload:
            raise ValueError(f"{path}: not a verdict document, missing {key!r}")
    if payload["verdict"] not in VERDICTS:
        raise ValueError(f"{path}: verdict {payload['verdict']!r} is not one of {VERDICTS}")
    return payload


def add_verdict_argument(parser: Any) -> Any:
    """`--verdict-json PATH`, spelled the same way by every gate."""
    parser.add_argument(
        "--verdict-json",
        metavar="PATH",
        help="Write this run's verdict as JSON: {verdict, reason, detail}. "
             "The `reason` is a stable code an instrument can assert against "
             "without matching on the prose.",
    )
    return parser
