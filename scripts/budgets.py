#!/usr/bin/env python3
"""Per-program complexity and case budgets.

Budgets are program state, not prose. `tla-spec-dev scaffold project` and
`tla-spec-dev scaffold workflow` emit a ``budgets:`` block into the generated
`spec_manifest.yaml` with the documented defaults, and the scaffold output
instructs the agent to propose those defaults to the user, ask which to adjust
for this program, and record a one-line rationale per changed value.

Downstream gates (`analyze complexity`, case generation, the adapter runner,
the mutation kill test) read their thresholds through :func:`load_budgets`,
which falls back to the documented defaults with a warning when the block is
missing.

The defaults here are the single source of truth for the values documented in
``references/modular_fuzzing.md``; keep the two in sync.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Documented defaults -- see references/modular_fuzzing.md "Budgets".
DEFAULT_BUDGETS: dict[str, Any] = {
    "tlc_seconds": 120,
    "max_distinct_states": 50000,
    "max_state_space_bound": 1000000,
    "max_internal_cases_per_component": 200,
    "max_external_cases_per_action": 50,
    "kill_rate_floor": 0.8,
    "max_component_variables": 6,
    "max_component_actions": 8,
    "max_symmetric_instances": 2,
}

# One-line explanation per budget, emitted as a trailing comment so the agent
# and the user can negotiate values without opening the reference.
BUDGET_COMMENTS: dict[str, str] = {
    "tlc_seconds": "hard external timeout per TLC run",
    "max_distinct_states": "reachable states TLC may find, per component model",
    "max_state_space_bound": "static declared-representation ceiling; see modular_fuzzing.md",
    "max_internal_cases_per_component": "spec-unit case cap per component",
    "max_external_cases_per_action": "Test Graph case cap per external action",
    "kill_rate_floor": "minimum mutation kill rate",
    "max_component_variables": "component-size heuristic",
    "max_component_actions": "component-size heuristic",
    "max_symmetric_instances": "component-size heuristic",
}

BUDGET_KEYS: tuple[str, ...] = tuple(DEFAULT_BUDGETS)


def budgets_block(indent: str = "  ") -> str:
    """Render the ``budgets:`` YAML block with documented defaults.

    The block is emitted by both scaffold commands so that every onboarded
    program starts with budgets as manifest state.
    """
    lines = ["budgets:"]
    width = max(len(key) for key in BUDGET_KEYS) + 2
    for key in BUDGET_KEYS:
        value = DEFAULT_BUDGETS[key]
        entry = f"{indent}{key}: {value}"
        comment = BUDGET_COMMENTS[key]
        pad = " " * max(1, width + len(indent) + 8 - len(entry))
        lines.append(f"{entry}{pad}# {comment}")
    lines.append(f"{indent}source: defaults")
    lines.append(f"{indent}rationale: {{}}")
    return "\n".join(lines) + "\n"


def budget_prompt(manifest_path: str) -> str:
    """Scaffold output telling the agent to negotiate budgets with the user.

    Returned as text rather than printed so both scaffold commands and the
    spec-unit adapters can assert on exactly the same instruction.
    """
    rows = "\n".join(
        f"      {key}: {DEFAULT_BUDGETS[key]}  ({BUDGET_COMMENTS[key]})" for key in BUDGET_KEYS
    )
    return (
        "\nBUDGETS -- negotiate these with the user before modeling.\n"
        f"A budgets: block was written to {manifest_path} with the documented defaults:\n\n"
        f"{rows}\n\n"
        "  1. Propose these defaults to the user.\n"
        "  2. Ask which to adjust for this program.\n"
        "  3. Record a one-line rationale under budgets.rationale for each changed value,\n"
        "     and set budgets.source to negotiated once agreed.\n\n"
        "Budgets are hard gates, not aspirations: analyze complexity, case generation,\n"
        "the adapter runner, and the mutation kill test all read them from this manifest.\n"
        "See references/modular_fuzzing.md 'Budgets'.\n"
    )


def _read_manifest(manifest_path: Path) -> dict[str, Any] | None:
    """Load a spec manifest, or return None when it cannot be read.

    Reuses ``extract_spec_manifest.load_manifest``, which already falls back to
    the repository's minimal YAML parser when PyYAML is unavailable.
    """
    if not manifest_path.is_file():
        return None
    try:
        from scripts.extract_spec_manifest import load_manifest
    except ImportError:  # direct-script import, where sys.path[0] is scripts/
        from extract_spec_manifest import load_manifest  # type: ignore[no-redef]
    try:
        loaded = load_manifest(manifest_path)
    except Exception:
        return None
    return loaded if isinstance(loaded, dict) else None


def _coerce(key: str, value: Any, *, warn: bool, stream: Any) -> Any:
    """Coerce a manifest budget to the numeric type of its default.

    Budgets are compared numerically by every gate. The repository's minimal
    YAML fallback parser does not recognise floats, so ``kill_rate_floor: 0.8``
    can arrive as the string ``"0.8"``; comparing that against a float raises.
    Coerce to the default's type and fall back on anything non-numeric.
    """
    default = DEFAULT_BUDGETS[key]
    target = type(default)
    if isinstance(value, target) and not isinstance(value, bool):
        return value
    try:
        return target(value)
    except (TypeError, ValueError):
        if warn:
            print(
                f"warning: budget {key}={value!r} is not a valid {target.__name__}; "
                f"using documented default {default}",
                file=stream,
            )
        return default


def load_budgets(
    manifest_path: Path | str,
    *,
    warn: bool = True,
    stream: Any = None,
) -> dict[str, Any]:
    """Read budgets from a spec manifest, falling back to documented defaults.

    A missing manifest, a missing ``budgets:`` block, or a missing individual
    key each fall back to the documented default and emit a warning, so a gate
    never silently runs on an unstated threshold.
    """
    stream = sys.stderr if stream is None else stream
    path = Path(manifest_path)
    budgets = dict(DEFAULT_BUDGETS)

    manifest = _read_manifest(path)
    if manifest is None:
        if warn:
            print(
                f"warning: no readable spec manifest at {path}; "
                "using documented default budgets (references/modular_fuzzing.md)",
                file=stream,
            )
        return budgets

    block = manifest.get("budgets")
    if not isinstance(block, dict):
        if warn:
            print(
                f"warning: no budgets block in {path}; "
                "using documented default budgets (references/modular_fuzzing.md). "
                "Run tla-spec-dev scaffold project to emit one, or add it by hand.",
                file=stream,
            )
        return budgets

    missing: list[str] = []
    for key in BUDGET_KEYS:
        if key in block and block[key] is not None:
            budgets[key] = _coerce(key, block[key], warn=warn, stream=stream)
        else:
            missing.append(key)

    if missing and warn:
        print(
            f"warning: budgets block in {path} is missing {', '.join(missing)}; "
            "using documented defaults for those keys",
            file=stream,
        )
    return budgets
