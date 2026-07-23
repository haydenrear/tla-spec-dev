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
- CD-09 RETENTION-BASIS AMENDMENT (owner-approved 2026-07-22). A complexity
  DECREASE is licensed by the VALIDATED-REFACTOR basis (the CD-02 definition):
  TLC green on the model BEFORE and AFTER the change, behavior tests green,
  a recorded before/after descriptor comparison, and -- when the red flag
  below fires -- an inspected transition-level diff. A decrease any of whose
  validated-refactor members is DEGRADED, ABSENT, or UNVERIFIED is REJECTED
  at close: a check that silently passes when its input is missing is not a
  check (the 2026-07-18 audit's core finding), and there is no flag to record
  a rejected decrease as an improvement.
- The fuzzing-era retention members -- kill_rate (MF-016), effect_conformance
  (MF-013/MF-027), external_coverage (MF-015) -- remain RECORDED at every
  close but no longer gate a decrease. They were demoted to EXPERIMENTAL by
  the 2026-07-21 ship-scanner/drop-fuzzing pivot after MF-038 measured kill
  0.31 against floor 0.8 with 0 of 9 content bugs caught: an oracle not
  validated to catch bugs cannot license or refuse anything. ``not_run`` is
  the honest record for them, and it stays visible in every entry and report
  -- non-gating is not unrecorded.
- ``unobservable`` IS NOT ``clean``. MF-027 changed the effect oracle to refuse
  targets it cannot see rather than reporting them clean. The member keeps its
  DEGRADED classification in the record for exactly that reason, even though
  it no longer gates.
- A generated-states drop at constant distinct states and constant depth is a
  RED FLAG, not a win. MF-020 withdrew a projected -13.1% reduction that turned
  out to require deleting a legitimate idempotent re-fire transition; the
  distinct-state gate was structurally blind to it because a deleted self-loop
  returns to an already-known state. Detection is delegated to MF-011's
  ``compare_tlc_reports`` rather than reimplemented. CD-09 keeps this gate
  EXACTLY as it was: the transition-diff obligation is part of the
  validated-refactor basis, not softened by it.
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

# The fuzzing-era retention members, named for the tickets that built them:
# kill rate (MF-016), effect conformance (MF-013/MF-027), external coverage
# (MF-015). CD-09 (owner-approved 2026-07-22): all three are still RECORDED at
# every close -- `not_run` is the honest post-pivot value -- but they no longer
# gate a decrease; the validated-refactor basis below does.
RETENTION_MEMBERS = ("kill_rate", "effect_conformance", "external_coverage")

# CD-09 -- the validated-refactor basis (the CD-02 definition). This is what
# licenses a complexity DECREASE: the model checks green before AND after the
# change, the behavior tests are green, and the before/after descriptor
# comparison is recorded. The fourth obligation of the basis -- the inspected
# transition-level diff -- is enforced by the red-flag gate (MF-020), which
# this amendment keeps exactly as it was.
VALIDATED_REFACTOR_MEMBERS = (
    "tlc_before",
    "tlc_after",
    "behavior_tests",
    "descriptor_comparison",
)

# Verdict classification. Anything not explicitly listed as RETAINED is treated
# as not-retained: an unrecognized verdict is never assumed to be good news.
# This is MF-027's polarity lesson -- grant the pass only on positive evidence,
# so every status nobody enumerated refuses rather than silently passing.
RETAINED_VERDICTS = {
    "kill_rate": {"pass"},
    "effect_conformance": {"clean"},
    "external_coverage": {"pass", "complete"},
    # CD-09 validated-refactor members. `recorded` (not `pass`) for the
    # descriptor comparison on purpose: the comparison is a document, and what
    # the gate requires is that it EXISTS from this run -- the delta judgment
    # is the ledger's, not the input's.
    "tlc_before": {"green", "pass"},
    "tlc_after": {"green", "pass"},
    "behavior_tests": {"green", "pass"},
    "descriptor_comparison": {"recorded"},
}

# Verdicts that positively indicate degradation, as opposed to absence of
# evidence. Both block a decrease; they are distinguished only so the report
# can say which one happened.
DEGRADED_VERDICTS = {
    "kill_rate": {"below_floor", "incomplete_catalog", "fail"},
    # "unobservable" sits here deliberately. See the module docstring.
    "effect_conformance": {"gaps", "dead_surface", "unobservable", "fail"},
    "external_coverage": {"gaps", "incomplete", "fail"},
    # CD-09 validated-refactor members: a red TLC run, red behavior tests, or a
    # comparison recorded against the wrong models are positive evidence of a
    # broken refactor, distinguished from mere absence only so the report can
    # say which happened.
    "tlc_before": {"fail", "error", "red"},
    "tlc_after": {"fail", "error", "red"},
    "behavior_tests": {"fail", "error", "red"},
    "descriptor_comparison": {"stale", "mismatch", "fail"},
}

UNVERIFIED_VERDICTS = {"unknown", "deferred", "not_run", "n/a", "na", ""}

# MF-026 -- the coverage audit gate. The four oracles check FIDELITY of what is
# modeled; the coverage audit checks COMPLETENESS. Neither implies the other, so
# the ledger records the audit verdict separately from the retention set.
#
# Recorded at EVERY close, including ticket closes where the audit has not run.
# That is the point: the audit is an end-of-epic step, so most ticket closes
# legitimately carry `not_run` -- but an epic that reached its workflow close
# without ever running it must be VISIBLE rather than silent. Omitting the block
# is never treated as passing.
COVERAGE_AUDIT_VERDICTS = {
    "pass": "no in-scope gaps",
    "fail": "in-scope gaps -- model it or change the program",
    "incomplete": "surface not fully walked -- NOT a pass",
    "not_run": "audit has not been run for this scope",
}

# Only `pass` is a pass. `incomplete` sits with `fail` deliberately: a sweep that
# did not walk the surface carries no information about it, and promoting that to
# a pass would dress an absence of evidence as a measurement (MF-027's lesson).
COVERAGE_AUDIT_PASSING = {"pass"}

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
class CoverageAuditRecord:
    """MF-026 -- the completeness gate's verdict, recorded at every close.

    Absence is recorded as ``not_run`` rather than dropped. A missing block is
    not an omission the ledger forgives; it is the visible fact that the epic
    has not yet run the audit.
    """

    status: str = "not_run"
    report: str = ""
    in_scope_gaps: Any = None
    scope_source: str = ""

    @property
    def normalized(self) -> str:
        value = str(self.status or "").strip().lower()
        return value if value in COVERAGE_AUDIT_VERDICTS else "not_run"

    @property
    def passing(self) -> bool:
        return self.normalized in COVERAGE_AUDIT_PASSING

    def describe(self) -> str:
        note = COVERAGE_AUDIT_VERDICTS[self.normalized]
        flag = "" if self.passing else "  <-- does not pass"
        return f"coverage_audit={self.normalized} ({note}){flag}"


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


def _parse_members(raw: dict[str, Any] | None, names: tuple[str, ...]) -> dict[str, RetentionMember]:
    """Every member of a constraint set is always present in the result.

    A member the input omits becomes an explicitly UNVERIFIED member rather
    than a missing key, so that no gate can be skipped by leaving a field out.
    """
    raw = raw if isinstance(raw, dict) else {}
    members: dict[str, RetentionMember] = {}
    for name in names:
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


def parse_retention(raw: dict[str, Any] | None) -> dict[str, RetentionMember]:
    """The fuzzing-era members -- recorded at every close, non-gating (CD-09)."""
    return _parse_members(raw, RETENTION_MEMBERS)


def parse_validated_refactor(raw: dict[str, Any] | None) -> dict[str, RetentionMember]:
    """CD-09 -- the validated-refactor basis that licenses a decrease."""
    return _parse_members(raw, VALIDATED_REFACTOR_MEMBERS)


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


def parse_coverage_audit(raw: dict[str, Any] | None) -> CoverageAuditRecord:
    """An absent or template-sentinel block becomes an explicit ``not_run``.

    Never a missing key, and never an assumed pass -- same polarity as the
    retention set: the verdict is granted only on positive evidence.
    """
    raw = raw if isinstance(raw, dict) else {}
    status = str(raw.get("status", "") or "").strip()
    if TEMPLATE_SENTINEL in status:
        status = ""
    report = str(raw.get("report", "") or "")
    if TEMPLATE_SENTINEL in report:
        report = ""
    scope_source = str(raw.get("scope_source", "") or "")
    if TEMPLATE_SENTINEL in scope_source:
        scope_source = ""
    return CoverageAuditRecord(
        status=status or "not_run",
        report=report,
        in_scope_gaps=raw.get("in_scope_gaps"),
        scope_source=scope_source,
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
    validated_refactor = parse_validated_refactor(ledger_input.get("validated_refactor"))
    refinement = parse_refinement(ledger_input.get("refinement"))
    coverage_audit = parse_coverage_audit(ledger_input.get("coverage_audit"))
    justification = str(ledger_input.get("justification", "") or "").strip()
    if TEMPLATE_SENTINEL in justification:
        justification = ""
    narrative = str(ledger_input.get("narrative", "") or "").strip()
    if TEMPLATE_SENTINEL in narrative:
        narrative = ""

    fuzz_not_retained = [m for m in retention.values() if not m.retained]
    vr_degraded = [m for m in validated_refactor.values() if m.degraded]
    vr_unverified = [m for m in validated_refactor.values() if m.unverified]

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

    # ---- Gate 2 (CD-09): a decrease with a DEGRADED validated-refactor ------
    # member is REJECTED. Not downgraded to a warning, not recorded as an
    # improvement with a note. This is the anti-gaming rule: complexity is
    # trivially reducible by deleting behavior, so a reduction is only real if
    # the refactor was validated -- TLC green before/after, behavior tests
    # green, before/after descriptors compared.
    if direction in {"decrease", "mixed"} and vr_degraded:
        errors.append(
            "REJECTED -- complexity decreased while validated-refactor evidence is DEGRADED: "
            + "; ".join(m.describe() for m in vr_degraded)
            + ". A reduction that breaks the model check, the behavior tests, or the "
            "descriptor record is not a reduction. Restore the evidence, or withdraw "
            "the reduction."
        )

    # ---- Gate 3 (CD-09): a decrease with an unverified basis also REJECTS ---
    # The audit's core finding was checks that pass when their input is absent.
    # An unmeasured member of the validated-refactor basis cannot witness
    # retention, so it cannot license a claimed reduction either.
    if direction in {"decrease", "mixed"} and vr_unverified:
        errors.append(
            "REJECTED -- complexity decreased but the validated-refactor basis is UNVERIFIED: "
            + "; ".join(m.describe() for m in vr_unverified)
            + ". A decrease is licensed only by the validated-refactor evidence set from "
            "the same run (`validated_refactor:` -- tlc_before, tlc_after, behavior_tests, "
            "descriptor_comparison). Absent evidence is not passing evidence."
        )

    # ---- The fuzzing-era members: recorded, visible, NON-GATING (CD-09) -----
    # Demoted by the 2026-07-21 pivot (kill 0.31 vs floor 0.8; 0/9 content
    # bugs). `not_run` is the honest record. Visibility without gating: a
    # decrease that proceeds past them says so in the report.
    if direction in {"decrease", "mixed"} and fuzz_not_retained:
        notes.append(
            "decrease proceeds past non-gating experimental retention members (CD-09): "
            + "; ".join(m.describe() for m in fuzz_not_retained)
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

    # ---- Gate 6: the coverage audit (MF-026) -------------------------------
    # Scope-sensitive by design, and the asymmetry is deliberate.
    #
    # The audit is an END-OF-EPIC step -- it runs after every mechanism ticket
    # has landed and before final integration. So a ticket close carrying
    # `not_run` is the normal, correct case, and failing it there would force
    # every ticket to run a whole-epic audit or to fake a verdict. Both are
    # worse than recording the absence.
    #
    # At WORKFLOW close the epic is over, and there is no later opportunity. A
    # missing or failing audit refuses, exactly like every other gate here: a
    # check that silently passes when its input is absent is not a check.
    #
    # `incomplete` refuses alongside `fail`. A sweep that did not walk the
    # surface carries no information about it; promoting that to a pass would
    # dress an absence of evidence as a measurement.
    if scope == "workflow" and not coverage_audit.passing:
        errors.append(
            "REJECTED -- coverage audit (MF-026) verdict is "
            f"`{coverage_audit.normalized}`: {COVERAGE_AUDIT_VERDICTS[coverage_audit.normalized]}. "
            "The four oracles check FIDELITY of what is modeled and are all bounded to "
            "it; unmodeled surface is invisible to every one of them while they report "
            "green. Run `prompts/coverage_audit.md` and record `coverage_audit.status: "
            "pass` with its report path. In-scope gaps are closed by modeling them or "
            "changing the program -- there is no justified/accept-as-is disposition."
        )
    elif not coverage_audit.passing:
        # Recorded and printed, never silently dropped: an epic that never ran
        # the audit must be legible from the ledger alone.
        notes.append(
            f"coverage audit not yet run for this scope ({coverage_audit.normalized}) -- "
            "MF-026 is an end-of-epic gate and is REQUIRED before workflow close."
        )

    # ---- Gate 7: the narrative is required ---------------------------------
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
        # CD-09: the basis that licenses a decrease, recorded jointly with the
        # delta exactly as the fuzzing members always were.
        "validated_refactor": {
            name: {
                "status": member.status,
                "classification": (
                    "retained" if member.retained else "degraded" if member.degraded else "unverified"
                ),
                "evidence": member.evidence,
                "value": member.value,
            }
            for name, member in validated_refactor.items()
        },
        "validated_refactor_summary": [m.describe() for m in validated_refactor.values()],
        "refinement": {
            "searched": refinement.searched,
            "outcome": refinement.outcome,
            "detail": refinement.detail,
            "measured": refinement.measured,
            "applied": refinement.applied,
            "approved_by": refinement.approved_by,
        },
        "coverage_audit": {
            "status": coverage_audit.normalized,
            "passing": coverage_audit.passing,
            "report": coverage_audit.report,
            "in_scope_gaps": coverage_audit.in_scope_gaps,
            "scope_source": coverage_audit.scope_source,
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
    # CD-01 (F3): the bound is None when no variable domain could be resolved --
    # an explicit unknown, rendered as such, never a silent 1.
    bound = metrics.get("bound")
    bound_text = f"{bound:,}" if isinstance(bound, int) else "unknown"
    lines.append(
        "  measured: variables={variables} actions={actions} bound={bound}".format(
            variables=metrics.get("variables"),
            actions=metrics.get("actions"),
            bound=bound_text,
        )
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

    # The licensing basis is printed next to the delta, never separately. The
    # adjacency is the point: a delta read without it is the number the
    # doctrine forbids. CD-09: the validated-refactor basis licenses a
    # decrease; the fuzzing-era members are recorded below it, non-gating.
    lines.append("  validated-refactor basis (joint requirement -- licenses a decrease, CD-09):")
    for line in entry.get("validated_refactor_summary", []):
        lines.append(f"            {line}")
    lines.append("  retention (fuzzing-era, experimental -- recorded, non-gating since CD-09):")
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

    # Completeness is printed next to fidelity, always -- including `not_run`.
    # The four oracles above are all bounded to what is modeled; this line is
    # the only one that speaks to what is not.
    audit = entry.get("coverage_audit") or {}
    audit_status = audit.get("status", "not_run")
    audit_flag = "" if audit.get("passing") else "  <-- does not pass"
    lines.append(f"  coverage audit (completeness, MF-026): {audit_status}{audit_flag}")
    if audit.get("report"):
        lines.append(f"            report: {audit['report']}")

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

# Validated-refactor basis -- CD-09 (owner-approved 2026-07-22). This is what
# LICENSES a complexity DECREASE: TLC green on the model before AND after the
# change, behavior tests green, and the before/after descriptor comparison
# recorded. Absent, unknown, or degraded evidence REJECTS a decrease: an
# unmeasured constraint cannot witness retention. (The fourth obligation, the
# inspected transition-level diff, is `transition_diff:` below and is demanded
# whenever the MF-020 red flag fires.)
#
#   tlc_before:            green | fail        -- TLC on the pre-change model
#   tlc_after:             green | fail        -- TLC on the post-change model
#   behavior_tests:        pass | fail         -- the repository behavior tests
#   descriptor_comparison: recorded            -- before/after descriptor doc
validated_refactor:
  tlc_before:
    status: "TODO"
    evidence: "TODO -- path to the pre-change TLC output"
  tlc_after:
    status: "TODO"
    evidence: "TODO -- path to the post-change TLC output"
  behavior_tests:
    status: "TODO"
    evidence: "TODO -- path to the behavior-test output"
  descriptor_comparison:
    status: "TODO"
    evidence: "TODO -- path to the before/after descriptor comparison"

# Fuzzing-era retention members -- RECORDED at every close, non-gating since
# CD-09. Demoted to EXPERIMENTAL by the 2026-07-21 pivot (MF-038: kill 0.31 vs
# floor 0.8, 0/9 content bugs caught). `not_run` is the honest value; fill in a
# measured verdict only when one of them actually ran.
#
#   kill_rate:           pass | below_floor | incomplete_catalog | not_run   (MF-016)
#   effect_conformance:  clean | gaps | dead_surface | unobservable | not_run (MF-013/MF-027)
#   external_coverage:   pass | gaps | incomplete | not_run                  (MF-015)
#
# NOTE: `unobservable` IS NOT `clean`. MF-027 made the effect oracle refuse
# targets it cannot see; the record keeps that distinction even though the
# member no longer gates.
retention:
  kill_rate:
    status: "not_run"
    evidence: ""
  effect_conformance:
    status: "not_run"
    evidence: ""
  external_coverage:
    status: "not_run"
    evidence: ""

# Coverage audit -- MF-026. The completeness gate, distinct from the three
# retention members above, which are all FIDELITY measures bounded to what is
# already modeled. Unmodeled surface is invisible to every one of them.
#
#   status: pass | fail | incomplete | not_run
#
# `not_run` is the CORRECT value at a ticket close: the audit is an end-of-epic
# step, run after the mechanism tickets land and before final integration. It is
# recorded and reported either way so that an epic which skipped it is visible.
# At WORKFLOW close anything but `pass` REFUSES -- and `incomplete` IS NOT
# `pass`, because a sweep that did not walk the surface says nothing about it.
#
# Procedure: prompts/coverage_audit.md   Doctrine: references/coverage_audit.md
coverage_audit:
  status: "not_run"
  report: ""          # path to the filled templates/coverage_audit_report.md
  in_scope_gaps: null # count; in-scope gaps are HARD -- model it or change the program
  scope_source: ""    # plan file:lines the declared scope was READ from, never chosen

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
