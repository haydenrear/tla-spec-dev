#!/usr/bin/env python3
"""MF-019 -- mechanize the standing objective: complexity minimization under behavior retention.

This module turns what the modular-fuzzing epic did by hand for eleven tickets
into a gate on the close path. Three things are mechanized:

1. **The ledger.** ``analyze complexity`` metrics (plus a TLC report when one is
   supplied) are recorded as an append-only entry per ticket close and workflow
   close, alongside budget utilization.

2. **The delta, reported jointly with retention evidence.** A complexity number
   on its own is meaningless -- it can always be lowered by deleting behavior.
   The delta is therefore never recorded without the retention constraint set,
   and the two are evaluated together.

3. **The refinement loop.** Every close carries either an approved
   recommendation with evidence, or an explicit "searched, found none" record.
   Silence is not an acceptable substitute for either.

DESIGN NOTE -- WHY THE ENTRY HAS AN OPEN NARRATIVE SECTION.
The eleven manual ledgers under specs/.history/modular-fuzzing-epic/ do not
share a schema. They recorded, variously: per-part attribution of a delta to
two independent changes (MF-022), per-value TLC reachability proofs (MF-016),
outdegree distribution and bound density (MF-025), complexity measured in lines
of code and persisted fields (MF-021), negotiated-budget provenance and its
propagation across trees (MF-027), a missed-target root-cause analysis that
retro-corrected a prior ticket's figure (MF-020), and a dedicated
domain-cardinality justification section (MF-013). Several recorded findings
about the *tooling* rather than the model.

A schema tight enough to validate all of that would have to be loose enough to
mean nothing. So the machine-checked core is deliberately narrow -- exactly the
fields the gates need -- and every entry additionally REQUIRES a narrative
document, which is preserved verbatim and never parsed. Constraining the
narrative to fit the core would have trimmed the ledger format to fit the
mechanism, which is the failure mode the standing objective exists to prevent.

GOVERNING RULES (references/architecture_tractability.md, "No Degenerate
Escapes"). A rule with an escape hatch is not a rule.

- An increase requires a recorded justification naming the new essential
  behavior. That is documentation of real behavior, NOT a bypass: it does not
  suppress the increase, silence a finding, or let a decrease through. It is
  recorded and reported either way.
- A decrease accompanied by degraded retention evidence is REJECTED at close.
  It is not recorded as an improvement and there is no flag to record it as one.
- A decrease whose retention evidence is ABSENT or UNVERIFIED is also rejected.
  A check that silently passes when its input is missing is not a check. This
  is the specific degeneracy the 2026-07-18 audit found across this epic.
- ``unobservable`` IS NOT ``clean``. MF-027 changed the effect oracle to refuse
  targets it cannot see rather than reporting them clean. Treating an
  unobservable result as passing retention here would rebuild exactly the
  silence MF-027 removed, one layer up.
- A generated-states drop at constant distinct states and constant depth is a
  RED FLAG, not a win. MF-020 withdrew a projected -13.1% reduction that turned
  out to require deleting a legitimate idempotent re-fire transition; the
  distinct-state gate was structurally blind to it because a deleted self-loop
  returns to an already-known state. Detection is delegated to MF-011's
  ``compare_tlc_reports`` rather than reimplemented.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:  # pragma: no cover - import shim for direct script execution
    from . import analyze_complexity
except ImportError:  # pragma: no cover
    import analyze_complexity

try:  # pragma: no cover
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


LEDGER_SCHEMA_VERSION = 1

# The doctrine's three-member retention constraint set. A complexity delta is
# only meaningful under these constraints, so all three are always evaluated.
# They are named for the tickets that built them: kill rate (MF-016), effect
# conformance (MF-013/MF-027), external coverage (MF-015).
RETENTION_MEMBERS = ("kill_rate", "effect_conformance", "external_coverage")

# Verdict classification. Anything not explicitly listed as RETAINED is treated
# as not-retained: an unrecognized verdict is never assumed to be good news.
# This is MF-027's polarity lesson -- grant the pass only on positive evidence,
# so every status nobody enumerated refuses rather than silently passing.
RETAINED_VERDICTS = {
    "kill_rate": {"pass"},
    "effect_conformance": {"clean"},
    "external_coverage": {"pass", "complete"},
}

# Verdicts that positively indicate degradation, as opposed to absence of
# evidence. Both block a decrease; they are distinguished only so the report
# can say which one happened.
DEGRADED_VERDICTS = {
    "kill_rate": {"below_floor", "incomplete_catalog", "fail"},
    # "unobservable" sits here deliberately. See the module docstring.
    "effect_conformance": {"gaps", "dead_surface", "unobservable", "fail"},
    "external_coverage": {"gaps", "incomplete", "fail"},
}

UNVERIFIED_VERDICTS = {"unknown", "deferred", "not_run", "n/a", "na", ""}

# Sentinel the scaffolded template carries. It must fail every gate it touches,
# so an unfilled template can never be closed through.
TEMPLATE_SENTINEL = "TODO"

# Metrics whose growth counts as a complexity increase. Deliberately the
# representation-size and reachable-size measures, not counts of files or tests.
DELTA_METRICS = (
    "variables",
    "actions",
    "bound",
    "distinct_states",
    "generated_states",
    "depth",
)

# The subset that decides the delta DIRECTION. Generated states are excluded on
# purpose: MF-020 showed a generated-states drop can be a deleted transition
# rather than a reduction, so it is reported and red-flagged but never on its
# own evidence of an improvement.
DIRECTION_METRICS = ("variables", "bound", "distinct_states")


class LedgerError(Exception):
    """Raised when the ledger gate refuses a close."""


@dataclass
class RetentionMember:
    name: str
    status: str
    evidence: str = ""
    value: Any = None

    @property
    def normalized(self) -> str:
        return str(self.status or "").strip().lower()

    @property
    def retained(self) -> bool:
        return self.normalized in RETAINED_VERDICTS.get(self.name, set())

    @property
    def degraded(self) -> bool:
        return self.normalized in DEGRADED_VERDICTS.get(self.name, set())

    @property
    def unverified(self) -> bool:
        """Absent, unknown, deferred -- or any verdict nobody enumerated."""
        return not self.retained and not self.degraded

    def describe(self) -> str:
        if self.retained:
            return f"{self.name}={self.status} (retained)"
        if self.degraded:
            extra = ""
            if self.name == "effect_conformance" and self.normalized == "unobservable":
                extra = " -- unobservable IS NOT clean (MF-027)"
            return f"{self.name}={self.status} (DEGRADED){extra}"
        return f"{self.name}={self.status or '(absent)'} (UNVERIFIED)"


@dataclass
class RefinementRecord:
    """Either an approved recommendation with evidence, or 'searched, found none'."""

    searched: bool = False
    outcome: str = ""  # "found" | "none"
    detail: str = ""
    measured: bool = False
    applied: bool = False
    approved_by: str = ""

    @property
    def found(self) -> bool:
        return str(self.outcome or "").strip().lower() == "found"

    @property
    def none(self) -> bool:
        return str(self.outcome or "").strip().lower() == "none"


@dataclass
class LedgerVerdict:
    entry: dict[str, Any]
    errors: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def rejected(self) -> bool:
        return bool(self.errors)

    @property
    def verdict(self) -> str:
        return "rejected" if self.rejected else "recorded"


# --------------------------------------------------------------------------
# Metric collection
# --------------------------------------------------------------------------


def collect_metrics(
    tla_path: Path,
    cfg_path: Path,
    manifest_path: Path | None = None,
    tlc_report: Path | None = None,
) -> dict[str, Any]:
    """Ledger-format metrics from ``analyze complexity`` plus an optional TLC report.

    The static figures are always MEASURED from the spec and cfg. The reachable
    figures come from a real TLC run when one is supplied and are left null
    otherwise -- never estimated, never carried forward from a previous entry.
    """
    analysis = analyze_complexity.analyze(tla_path, cfg_path, manifest_path)
    metrics: dict[str, Any] = {
        "variables": len(analysis.variables),
        "actions": len(analysis.actions),
        "bound": analysis.bound,
        "modularity": analysis.modularity_score,
        "distinct_states": None,
        "generated_states": None,
        "depth": None,
        "gate_passed": analysis.gate_passed,
        "gate_violations": list(analysis.violations),
    }
    if tlc_report is not None and Path(tlc_report).exists():
        report = analyze_complexity.parse_tlc_report(Path(tlc_report).read_text(encoding="utf-8"))
        metrics["distinct_states"] = report.distinct
        metrics["generated_states"] = report.generated
        metrics["depth"] = report.depth
        metrics["tlc_report"] = str(tlc_report)
    budgets = analysis.budgets or {}
    metrics["budget_utilization"] = _budget_utilization(metrics, budgets)
    return metrics


def _budget_utilization(metrics: dict[str, Any], budgets: dict[str, Any]) -> dict[str, Any]:
    """Percent-of-cap for each hard cap, in the form the manual ledgers used."""
    utilization: dict[str, Any] = {}
    pairs = (
        ("max_state_space_bound", "bound"),
        ("max_distinct_states", "distinct_states"),
    )
    for budget_key, metric_key in pairs:
        cap = budgets.get(budget_key)
        used = metrics.get(metric_key)
        if not isinstance(cap, int) or cap <= 0 or not isinstance(used, int):
            continue
        utilization[budget_key] = {
            "cap": cap,
            "used": used,
            "percent": round(used / cap * 100, 1),
            "within_cap": used <= cap,
        }
    return utilization


# --------------------------------------------------------------------------
# Ledger persistence (append-only)
# --------------------------------------------------------------------------


def ledger_path(specs_dir: Path) -> Path:
    """The append-only ledger is MACHINE-written, so it is JSON.

    The human-written *input* document is YAML, because a person fills it in.
    The ledger itself is only ever produced and consumed by this module, and
    JSON round-trips losslessly with no optional dependency -- which matters
    because the spec-unit runner invokes pytest without pyyaml. Writing YAML
    here and reading it back through a subset parser was a real defect: the
    first close wrote a document the second close could not read.
    """
    return Path(specs_dir) / "results" / "complexity_ledger.json"


def load_ledger(path: Path) -> dict[str, Any]:
    if not Path(path).exists():
        return {"schema_version": LEDGER_SCHEMA_VERSION, "entries": []}
    text = Path(path).read_text(encoding="utf-8")
    data = json.loads(text) if text.strip() else None
    if not isinstance(data, dict):
        return {"schema_version": LEDGER_SCHEMA_VERSION, "entries": []}
    data.setdefault("entries", [])
    return data


def _load_structured(text: str) -> Any:
    """Parse a ledger document with or without PyYAML installed.

    The spec-unit runner invokes pytest without pyyaml, so a JSON-only fallback
    would raise on a YAML ledger -- and a fallback that fails on the real input
    format is a check that disables itself under a condition nobody chose. The
    repository already ships a pure-Python subset parser for exactly this; reuse
    it rather than adding a dependency or a second parser.
    """
    if yaml is not None:
        return yaml.safe_load(text)
    try:  # pragma: no cover - exercised only without pyyaml
        from .extract_spec_manifest import parse_simple_yaml
    except ImportError:  # pragma: no cover
        from extract_spec_manifest import parse_simple_yaml
    return parse_simple_yaml(text)


def _dump_ledger(data: Any) -> str:
    return json.dumps(data, indent=2, default=str) + "\n"


def previous_entry(ledger: dict[str, Any]) -> dict[str, Any] | None:
    entries = [e for e in ledger.get("entries", []) if isinstance(e, dict)]
    # Only entries that were actually RECORDED form the baseline. A rejected
    # close must not become the reference point for the next one, or a
    # rejection would quietly reset the baseline it was rejected against.
    recorded = [e for e in entries if e.get("verdict") != "rejected"]
    return recorded[-1] if recorded else None


def append_entry(path: Path, entry: dict[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ledger = load_ledger(path)
    ledger["schema_version"] = LEDGER_SCHEMA_VERSION
    ledger.setdefault("entries", []).append(entry)
    path.write_text(_dump_ledger(ledger), encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Delta
# --------------------------------------------------------------------------


def compute_delta(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    """Metric-by-metric delta against the previous recorded entry."""
    delta: dict[str, Any] = {"previous_scope_id": None, "metrics": {}, "direction": "baseline"}
    if previous is None:
        delta["note"] = "no previous ledger entry; this entry establishes the baseline"
        return delta
    delta["previous_scope_id"] = previous.get("scope_id")
    previous_metrics = previous.get("metrics", {}) or {}
    directions: list[str] = []
    for key in DELTA_METRICS:
        before = previous_metrics.get(key)
        after = current.get(key)
        if not isinstance(before, int) or not isinstance(after, int):
            delta["metrics"][key] = {"before": before, "after": after, "delta": None}
            continue
        change = after - before
        entry: dict[str, Any] = {"before": before, "after": after, "delta": change}
        if before:
            entry["percent"] = round(change / before * 100, 1)
        delta["metrics"][key] = entry
        if key in DIRECTION_METRICS and change:
            directions.append("increase" if change > 0 else "decrease")
    if not directions:
        delta["direction"] = "zero"
    elif "increase" in directions and "decrease" in directions:
        delta["direction"] = "mixed"
    else:
        delta["direction"] = directions[0]
    return delta


def _tlc_reports(previous: dict[str, Any] | None, current: dict[str, Any]) -> tuple[Any, Any]:
    before = analyze_complexity.TlcReport()
    after = analyze_complexity.TlcReport()
    if previous:
        pm = previous.get("metrics", {}) or {}
        before.generated = pm.get("generated_states")
        before.distinct = pm.get("distinct_states")
        before.depth = pm.get("depth")
    after.generated = current.get("generated_states")
    after.distinct = current.get("distinct_states")
    after.depth = current.get("depth")
    return before, after


# --------------------------------------------------------------------------
# Input parsing
# --------------------------------------------------------------------------


def parse_retention(raw: dict[str, Any] | None) -> dict[str, RetentionMember]:
    """Every member of the constraint set is always present in the result.

    A member the input omits becomes an explicitly UNVERIFIED member rather
    than a missing key, so that no gate can be skipped by leaving a field out.
    """
    raw = raw if isinstance(raw, dict) else {}
    members: dict[str, RetentionMember] = {}
    for name in RETENTION_MEMBERS:
        value = raw.get(name)
        if isinstance(value, dict):
            status = str(value.get("status", "") or "")
            if TEMPLATE_SENTINEL in status:
                status = ""
            members[name] = RetentionMember(
                name=name,
                status=status,
                evidence=str(value.get("evidence", "") or ""),
                value=value.get("value"),
            )
        elif isinstance(value, str):
            status = "" if TEMPLATE_SENTINEL in value else value
            members[name] = RetentionMember(name=name, status=status)
        else:
            members[name] = RetentionMember(name=name, status="")
    return members


def parse_refinement(raw: dict[str, Any] | None) -> RefinementRecord:
    raw = raw if isinstance(raw, dict) else {}
    outcome = str(raw.get("outcome", "") or "").strip().lower()
    if TEMPLATE_SENTINEL.lower() in outcome:
        outcome = ""
    detail = str(raw.get("detail", "") or "")
    if TEMPLATE_SENTINEL in detail:
        detail = ""
    return RefinementRecord(
        searched=bool(raw.get("searched", False)),
        outcome=outcome,
        detail=detail,
        measured=bool(raw.get("measured", False)),
        applied=bool(raw.get("applied", False)),
        approved_by=str(raw.get("approved_by", "") or ""),
    )


def load_input(path: Path) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise LedgerError(
            f"complexity ledger input not found: {path}\n"
            "The standing objective is mechanized as a required close-out step. "
            "`open ticket` scaffolds this file; fill it in before closing."
        )
    data = _load_structured(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise LedgerError(f"complexity ledger input is not a mapping: {path}")
    return data


# --------------------------------------------------------------------------
# The gate
# --------------------------------------------------------------------------


def evaluate(
    *,
    scope: str,
    scope_id: str,
    workflow: str,
    metrics: dict[str, Any],
    ledger_input: dict[str, Any],
    previous: dict[str, Any] | None,
) -> LedgerVerdict:
    """Build the ledger entry and run every gate. Errors mean the close is refused."""
    errors: list[str] = []
    notes: list[str] = []

    delta = compute_delta(previous, metrics)
    direction = delta["direction"]
    retention = parse_retention(ledger_input.get("retention"))
    refinement = parse_refinement(ledger_input.get("refinement"))
    justification = str(ledger_input.get("justification", "") or "").strip()
    if TEMPLATE_SENTINEL in justification:
        justification = ""
    narrative = str(ledger_input.get("narrative", "") or "").strip()
    if TEMPLATE_SENTINEL in narrative:
        narrative = ""

    degraded = [m for m in retention.values() if m.degraded]
    unverified = [m for m in retention.values() if m.unverified]

    # ---- Gate 1: an increase requires a recorded justification --------------
    # Documentation of real behavior, not a bypass: the increase is recorded and
    # reported whether or not a justification exists. What the justification
    # buys is the close, never the erasure of the number.
    if direction in {"increase", "mixed"} and not justification:
        grew = [
            f"{k} {v['before']} -> {v['after']}"
            for k, v in delta["metrics"].items()
            if k in DIRECTION_METRICS and isinstance(v.get("delta"), int) and v["delta"] > 0
        ]
        errors.append(
            "complexity INCREASED ("
            + "; ".join(grew)
            + ") with no recorded justification. Record `justification:` naming the "
            "NEW ESSENTIAL BEHAVIOR the added representation carries. There is no "
            "flag that skips this."
        )

    # ---- Gate 2: a decrease with degraded retention is REJECTED -------------
    # Not downgraded to a warning, not recorded as an improvement with a note.
    # This is the anti-gaming rule: complexity is trivially reducible by
    # deleting behavior, so a reduction is only real if behavior was retained.
    if direction in {"decrease", "mixed"} and degraded:
        errors.append(
            "REJECTED -- complexity decreased while retention evidence is DEGRADED: "
            + "; ".join(m.describe() for m in degraded)
            + ". A reduction bought by dropping a boundary is not a reduction. "
            "Restore the retention evidence, or withdraw the reduction."
        )

    # ---- Gate 3: a decrease with unverified retention is also REJECTED ------
    # The audit's core finding was checks that pass when their input is absent.
    # An unmeasured constraint cannot witness retention, so it cannot license a
    # claimed reduction either.
    if direction in {"decrease", "mixed"} and unverified:
        errors.append(
            "REJECTED -- complexity decreased but retention evidence is UNVERIFIED: "
            + "; ".join(m.describe() for m in unverified)
            + ". A decrease is only reportable JOINTLY with retention evidence from "
            "the same run. Absent evidence is not passing evidence."
        )

    # ---- Gate 4: the self-loop red flag (MF-020) ---------------------------
    # Delegated to MF-011's comparator rather than reimplemented.
    before_report, after_report = _tlc_reports(previous, metrics)
    tlc_findings = analyze_complexity.compare_tlc_reports(before_report, after_report)
    red_flags = [f for f in tlc_findings if f.get("level") == "RED FLAG"]
    transition_diff = str(ledger_input.get("transition_diff", "") or "").strip()
    if TEMPLATE_SENTINEL in transition_diff:
        transition_diff = ""
    if red_flags:
        if not transition_diff:
            errors.append(
                "REJECTED -- "
                + " ".join(f["message"] for f in red_flags)
                + " Record `transition_diff:` with the inspected transition-level diff "
                "showing which transitions were removed and why each removal is a "
                "re-representation rather than a deleted behavior."
            )
        else:
            notes.append(
                "generated-states drop at constant distinct states accepted on the "
                f"recorded transition diff: {transition_diff}"
            )
    for finding in tlc_findings:
        if finding.get("level") in {"OK", "INFO", "NOTE"}:
            notes.append(f"{finding['level']}: {finding['message']}")

    # ---- Gate 5: the refinement loop record is required --------------------
    # Silence is not an acceptable substitute for "searched, found none".
    if not refinement.searched:
        errors.append(
            "REJECTED -- no recursive refinement record. Every close carries either an "
            "approved recommendation with evidence, or an explicit 'searched, found "
            "none'. Set `refinement.searched: true` and record the outcome."
        )
    elif not (refinement.found or refinement.none):
        errors.append(
            "REJECTED -- refinement record has no outcome. Set `refinement.outcome` to "
            "`found` (with detail and evidence) or `none` (searched, found none)."
        )
    elif refinement.found and not refinement.detail:
        errors.append(
            "REJECTED -- refinement outcome is `found` with no detail. Record what was "
            "found, whether it was MEASURED or PROJECTED, and the evidence."
        )
    if refinement.applied and not refinement.approved_by:
        errors.append(
            "REJECTED -- a refinement recommendation was APPLIED without a recorded "
            "approver. Refinement recommendations are advisory and user-approved, "
            "never auto-applied."
        )

    # ---- Gate 6: the narrative is required ---------------------------------
    # The machine-checked core is narrow by design; the narrative is where the
    # ledger actually says what happened. Requiring it is what keeps the
    # mechanization from silently narrowing the record.
    if not narrative:
        errors.append(
            "REJECTED -- no `narrative:` recorded. The ledger's machine-checked core is "
            "deliberately narrow; the narrative carries the reasoning, the measured "
            "alternatives, and any finding the core cannot express."
        )

    # Report the delta jointly with retention, ALWAYS -- including when the
    # delta is zero and no gate fired. The joint reporting is the doctrine.
    entry = {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "scope": scope,
        "scope_id": scope_id,
        "workflow": workflow,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "delta": delta,
        "justification": justification,
        "retention": {
            name: {
                "status": member.status,
                "classification": (
                    "retained" if member.retained else "degraded" if member.degraded else "unverified"
                ),
                "evidence": member.evidence,
                "value": member.value,
            }
            for name, member in retention.items()
        },
        "retention_summary": [m.describe() for m in retention.values()],
        "refinement": {
            "searched": refinement.searched,
            "outcome": refinement.outcome,
            "detail": refinement.detail,
            "measured": refinement.measured,
            "applied": refinement.applied,
            "approved_by": refinement.approved_by,
        },
        "transition_diff": transition_diff,
        "narrative": narrative,
        "tlc_findings": tlc_findings,
        "notes": notes,
        "errors": errors,
        "verdict": "rejected" if errors else "recorded",
    }
    return LedgerVerdict(entry=entry, errors=errors, notes=notes)


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


def render_report(verdict: LedgerVerdict) -> str:
    entry = verdict.entry
    lines: list[str] = []
    lines.append("complexity ledger -- standing objective (MF-019)")
    lines.append(f"  scope:    {entry['scope']} {entry['scope_id']}")
    metrics = entry["metrics"]
    lines.append(
        "  measured: variables={variables} actions={actions} bound={bound:,}".format(**metrics)
    )
    if isinstance(metrics.get("distinct_states"), int):
        lines.append(
            "            distinct={distinct_states:,} generated={generated_states:,} "
            "depth={depth}".format(**metrics)
        )
    for key, util in (metrics.get("budget_utilization") or {}).items():
        flag = "within cap" if util["within_cap"] else "OVER CAP"
        lines.append(f"            {key}: {util['used']:,} / {util['cap']:,} ({util['percent']}%, {flag})")

    delta = entry["delta"]
    lines.append(f"  delta:    direction={delta['direction']} (vs {delta.get('previous_scope_id') or 'baseline'})")
    for key, change in delta.get("metrics", {}).items():
        if isinstance(change.get("delta"), int) and change["delta"]:
            percent = f" ({change['percent']:+}%)" if "percent" in change else ""
            lines.append(f"            {key}: {change['before']:,} -> {change['after']:,} = {change['delta']:+,}{percent}")

    # Retention is printed next to the delta, never separately. The adjacency is
    # the point: a delta read without it is the number the doctrine forbids.
    lines.append("  retention (joint requirement -- a delta is meaningless without it):")
    for line in entry["retention_summary"]:
        lines.append(f"            {line}")

    refinement = entry["refinement"]
    if refinement["outcome"] == "none":
        lines.append("  refinement: searched, found none")
    elif refinement["outcome"] == "found":
        applied = "APPLIED" if refinement["applied"] else "NOT applied (advisory, owner approval required)"
        lines.append(f"  refinement: found -- {applied}")
        lines.append(f"            {refinement['detail']}")
    else:
        lines.append("  refinement: (missing)")

    for note in entry.get("notes", []):
        lines.append(f"  note:     {note}")
    if verdict.rejected:
        lines.append("")
        lines.append("  VERDICT: REJECTED -- close refused:")
        for error in verdict.errors:
            lines.append(f"    - {error}")
    else:
        lines.append("  VERDICT: recorded")
    return "\n".join(lines) + "\n"


TEMPLATE = """\
# Complexity ledger input -- MF-019 standing objective.
#
# `close ticket` refuses until this is filled in. That refusal is the mechanism:
# the standing objective is a required close-out step, not a stance.
#
# The delta is computed for you from `analyze complexity` and the TLC report.
# What you supply is the part a tool cannot know: whether behavior was retained,
# what the refinement search found, and why any increase is essential.

# Retention evidence -- the doctrine's three-member constraint set. A complexity
# DECREASE is REJECTED unless all three are retained. Absent or unknown evidence
# does NOT pass: an unmeasured constraint cannot witness retention.
#
#   kill_rate:           pass | below_floor | incomplete_catalog   (MF-016)
#   effect_conformance:  clean | gaps | dead_surface | unobservable (MF-013/MF-027)
#   external_coverage:   pass | gaps | incomplete                  (MF-015)
#
# NOTE: `unobservable` IS NOT `clean`. MF-027 made the effect oracle refuse
# targets it cannot see; treating that as passing here would rebuild the silence.
retention:
  kill_rate:
    status: "TODO"
    evidence: "TODO -- path to the kill-test report"
  effect_conformance:
    status: "TODO"
    evidence: "TODO -- path to the effect-conformance report"
  external_coverage:
    status: "TODO"
    evidence: "TODO -- path to the external coverage report"

# Required if complexity INCREASED. Name the new essential behavior the added
# representation carries. This documents real behavior; it does not waive the
# increase, which is recorded and reported either way.
justification: ""

# The recursive refinement loop -- REQUIRED at every close.
# Either an approved recommendation with evidence, or "searched, found none".
# Recommendations are advisory and user-approved, never auto-applied.
refinement:
  searched: false
  outcome: "TODO -- found | none"
  detail: ""
  measured: false      # true only if a real TLC run produced the figure
  applied: false       # if true, approved_by is required
  approved_by: ""

# Required only if a generated-states drop at constant distinct states is
# detected. That is a RED FLAG (deleted self-loop, MF-020), not a win -- record
# the inspected transition-level diff here to accept it.
transition_diff: ""

# REQUIRED. The narrative ledger: reasoning, measured alternatives, findings the
# machine-checked core above cannot express. Path to a document, or prose.
narrative: "TODO"
"""


def write_template(path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(TEMPLATE, encoding="utf-8")
    return path
