#!/usr/bin/env python3
"""The seeded-fault catalogue parser and the suppression-key scanner.

WHAT THIS MODULE USED TO BE, AND WHY THE REST OF IT IS GONE (`CA-04`)
--------------------------------------------------------------------
This file was oracle 4, the mutation kill test: it seeded one fault per
declared port and one per model invariant, ran the distilled corpus against
each, and gated the resulting kill rate against ``kill_rate_floor``. That gate
was **the last hard static gate in this repository** and it has been removed,
together with ``scripts/run_kill_test.py``, the ``RunKillTest`` action of
``TlaSpecDevCli.tla``, its adapter, and the ``kill_mutants.toml`` catalogues.

The finding behind the removal is `RM-03-DF-05`, which identified this cut and
declined it because it was a model delta in a ticket that declared none:

    "THE ONE HARD STATIC GATE LEFT IN THIS REPOSITORY IS A SPECIFIED ACTION OF
    THE MODEL, SO REMOVING IT IS A MODEL DELTA AND RM-03 DECLARES NONE. ...
    Every candidate RM-03 examined disclaims gatehood in its own docstring
    except one: `scripts/kill_test.py`, whose `kill_rate_floor` is described
    there as 'a hard gate, and the load-bearing one'."

`RM-03-DF-05`'s own `suggested_fix` asked for exactly the ticket that made this
cut: *"Open it as its own ticket against the CLI model."* The standing evidence
that the lever is dead is the epic record's *"static gates catch nothing --
seven epics, zero bugs caught by a static check"*.

WHAT SURVIVES HERE, AND WHY IT IS NOT THE GATE
----------------------------------------------
Two things, both of which are **read by the A/B evaluation machinery** rather
than by any gate, and neither of which computes or enforces a rate:

* :func:`load_catalog` / :func:`parse_mutants` -- the shipped catalogue parser.
  ``examples/validation/ab/check_catalogue.py`` loads every seeded-fault
  catalogue "via the SHIPPED parser" so the A/B catalogues cannot drift from
  the format the toolchain actually reads.
* :data:`SUPPRESSION_KEYS` / :func:`scan_for_suppression` -- the tripwire for
  keys that would let a survivor or a failed cell disappear.
  ``examples/validation/ab/eval/run_controls.py`` imports it at module scope
  and scans every catalogue it is handed (EVAL-SUPPRESS), so the eval's own
  ``[[limitation]]`` and ``[[retired_control]]`` constructs are enumerated by
  one scanner against one list.

**This surface was retained deliberately and the reason was measured, not
assumed.** `CA-04` parked this file and ran the two consumers: `run_controls.py`
died at module scope with ``ModuleNotFoundError: No module named
'scripts.kill_test'``, and `check_catalogue.py` went from *"Catalogue integrity
holds"* to the same error. `run_controls.py` is the driver `RD-03` used to
produce the model-derived instrument columns whose **zero unique kills across
six trees, against four the other way** is one of the four load-bearing
disproofs on the record. Deleting this module wholesale would have left that
disproof readable but **no longer re-derivable** -- the failure `CA-02` made
with ``repriced_history.py`` one ticket earlier.

Nothing here is a gate. Nothing here has an exit code. Suppression-shaped keys
are reported and honored never, which is a report, not a refusal.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BOUNDARY_PORT = "port"
BOUNDARY_INVARIANT = "invariant"
BOUNDARY_KINDS = (BOUNDARY_PORT, BOUNDARY_INVARIANT)

#: Keys that would, if honored, let a survivor or a sub-floor rate pass. They
#: are scanned for, reported loudly, and honored never -- the same treatment
#: MF-013/MF-027 gave gap suppression. Listing them here is not a feature; it
#: is a tripwire, so an attempt to add degeneracy shows up in the evidence.
SUPPRESSION_KEYS = frozenset(
    {
        "accept_survivor",
        "accept_survivors",
        "accepted_survivor",
        "allow_below_floor",
        "allow_survivor",
        "allow_survivors",
        "expected_to_survive",
        "ignore_survivor",
        "justification",
        "known_survivor",
        # EVAL-SUPPRESS. The A/B eval's control record
        # (`examples/validation/ab/eval/controls.toml`) introduced a second
        # family of suppression: `[[limitation]]` declares that an instrument
        # cannot decide a mutant, and `[[retired_control]]` declares that a
        # control's own declaration was falsified. Both are CHECKED constructs
        # -- a limitation must name a witness the run verifies against its own
        # executability counts, and since EVAL-SUPPRESS neither may convert a
        # demonstrated KILL -- but until then neither appeared on any
        # suppression list, so a reader auditing this file for "what can make a
        # survivor or a kill disappear" would not have found the one mechanism
        # that could (EVAL-RERUN-DF-02). Listing them changes nothing about how
        # they are honored, which is: on evidence, never on the say-so of the
        # key. It makes them visible in `ignored_suppression_keys` and, via
        # `scan_for_suppression`, in every artifact `run_controls.py` writes.
        "limitation",
        "limitation_on",
        "not_decidable",
        "override",
        "retired_control",
        "skip",
        # Listed so the scan enumerates each declared limitation INSTANCE
        # (`limitation[0].witness_ran_must_be`) and not merely the fact that
        # the file uses the construct. It is also literally a key that, if
        # honored on its say-so instead of checked against the run's own
        # counts, lets a cell pass -- which is this list's own definition.
        "witness_ran_must_be",
        "skip_kill_test",
        "survivor_ok",
        "suppress",
        "tolerate",
        "waiver",
        "waived",
        "xfail",
    }
)


class KillTestCatalogError(Exception):
    """The mutant catalog is malformed. Always an exit-2 refusal."""


# --------------------------------------------------------------------------
# Mutants
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Mutant:
    """One seeded fault at one modeled boundary.

    ``find``/``replace`` is a literal, reviewable text substitution in a real
    production source file. It is deliberately not a random AST perturbation:
    a kill test whose mutants nobody can read produces survivors nobody can
    act on, and the survivor's whole value here is that it points somewhere.

    ``refine_variable`` and ``refine_action`` are the pointer. They name the
    model element that OWNS this boundary, so a survivor reads as "refine
    this variable / this action", not as a decimal that dropped.
    """

    id: str
    boundary_kind: str
    boundary_ref: str
    path: str
    find: str
    replace: str
    description: str
    refine_variable: str
    refine_action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "boundary_kind": self.boundary_kind,
            "boundary_ref": self.boundary_ref,
            "path": self.path,
            "find": self.find,
            "replace": self.replace,
            "description": self.description,
            "refine_variable": self.refine_variable,
            "refine_action": self.refine_action,
        }

    @property
    def boundary(self) -> tuple[str, str]:
        return (self.boundary_kind, self.boundary_ref)


REQUIRED_MUTANT_FIELDS = (
    "id",
    "boundary_kind",
    "boundary_ref",
    "path",
    "find",
    "replace",
    "description",
    "refine_variable",
    "refine_action",
)


def parse_mutants(raw: Any, *, source: str = "<catalog>") -> tuple[list[Mutant], list[str]]:
    """Build mutants from parsed catalog data.

    Returns ``(mutants, ignored_suppression_keys)``. Every field in
    :data:`REQUIRED_MUTANT_FIELDS` is required. Nothing is defaulted -- a
    mutant that omits ``refine_variable`` cannot point at anything when it
    survives, and a mutant that omits ``boundary_ref`` cannot be counted
    toward coverage, so both are refusals rather than shrugs.
    """

    if not isinstance(raw, dict):
        raise KillTestCatalogError(f"{source}: catalog root must be a mapping")
    entries = raw.get("mutants")
    if not isinstance(entries, list) or not entries:
        raise KillTestCatalogError(
            f"{source}: catalog declares no mutants. An empty catalog is not a passing kill "
            f"test -- seed one fault per declared port and one per invariant."
        )

    suppressions = sorted(_scan_for_suppression(raw))
    mutants: list[Mutant] = []
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise KillTestCatalogError(f"{source}: mutant #{index} is not a mapping")
        missing = [key for key in REQUIRED_MUTANT_FIELDS if not entry.get(key)]
        if missing:
            raise KillTestCatalogError(
                f"{source}: mutant #{index} ({entry.get('id', '<no id>')}) is missing required "
                f"field(s) {', '.join(missing)}. Every field is required: a mutant that cannot "
                f"name the variable and action to refine is useless when it survives."
            )
        kind = str(entry["boundary_kind"])
        if kind not in BOUNDARY_KINDS:
            raise KillTestCatalogError(
                f"{source}: mutant {entry['id']} has boundary_kind {kind!r}; "
                f"expected one of {', '.join(BOUNDARY_KINDS)}"
            )
        mutant_id = str(entry["id"])
        if mutant_id in seen:
            raise KillTestCatalogError(f"{source}: duplicate mutant id {mutant_id!r}")
        seen.add(mutant_id)
        mutants.append(
            Mutant(
                id=mutant_id,
                boundary_kind=kind,
                boundary_ref=str(entry["boundary_ref"]),
                path=str(entry["path"]),
                find=str(entry["find"]),
                replace=str(entry["replace"]),
                description=str(entry["description"]),
                refine_variable=str(entry["refine_variable"]),
                refine_action=str(entry["refine_action"]),
            )
        )
    return mutants, suppressions


def scan_for_suppression(node: Any, prefix: str = "") -> set[str]:
    """Public entry point for anything else that loads a catalog-shaped file.

    `examples/validation/ab/eval/run_controls.py` calls this on every catalogue
    it is given, so the eval's own `[[limitation]]` and `[[retired_control]]`
    constructs are enumerated in the run artifact by the same scanner and
    against the same list as the kill test's own (EVAL-SUPPRESS). One list, one
    scanner, one place to look.
    """

    return _scan_for_suppression(node, prefix)


def _scan_for_suppression(node: Any, prefix: str = "") -> set[str]:
    """Collect suppression-shaped keys anywhere in the catalog.

    They are never honored. Reporting them is the point: an attempt to add a
    waiver becomes visible in the evidence rather than becoming behavior.
    """

    found: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            dotted = f"{prefix}.{key}" if prefix else str(key)
            if str(key).lower() in SUPPRESSION_KEYS:
                found.add(dotted)
            found |= _scan_for_suppression(value, dotted)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found |= _scan_for_suppression(value, f"{prefix}[{index}]")
    return found


def load_catalog(path: Path) -> tuple[list[Mutant], list[str]]:
    """Load a TOML mutant catalog."""

    path = Path(path)
    if not path.is_file():
        raise KillTestCatalogError(
            f"no mutant catalog at {path}. The kill test has no fault to seed, which is not "
            f"the same as a program with no faults -- declare the catalog."
        )
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
        try:
            import tomli as tomllib  # type: ignore[no-redef]
        except ModuleNotFoundError as exc:
            # Deliberately NOT the simple-parser fallback that
            # run_generated_case_adapters uses for adapter mappings. Mutant
            # catalogs contain multi-line literals, and a parser that silently
            # dropped the entries it could not read would hand back a smaller
            # catalog that still looked complete -- the exact coverage drift
            # this module exists to prevent. Refuse instead.
            raise KillTestCatalogError(
                f"no TOML parser available on {sys.executable} (Python "
                f"{sys.version_info.major}.{sys.version_info.minor}). The mutant catalog is "
                f"not parsed with the simple fallback parser used for adapter mappings, "
                f"because a partially-read catalog would under-report the required boundary "
                f"set and report a complete kill test over a surface it never covered. "
                f"Run this command on Python 3.11+ or install `tomli`."
            ) from exc
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - surfaced as a refusal
        raise KillTestCatalogError(f"{path}: could not parse catalog: {exc}") from exc
    return parse_mutants(raw, source=str(path))
