#!/usr/bin/env python3
"""Close-out skill-feedback loop (MF-017).

`references/migration.md` Phase 6 requires a retro at close-out covering what the
skill could not express: surviving mutants, unmodelable effects, budget values
that had to move, and profile/schema/CLI workarounds. Until now that retro was a
prose instruction, so the knowledge evaporated in chat.

This module mechanizes it. Every close-out (ticket close and workflow close)
ensures ``<spec-root>/results/skill_feedback.md`` exists, appends a close-scoped
entry to it, and reports the *filing status* of every finding recorded there so
the append-only history entry can record whether feedback was filed and where.

Design constraints that shaped the format:

* **Accumulating, never clobbered.** The document is written once from the
  template and thereafter only appended to. A close-out must never destroy a
  previously filled-in finding -- that is the same failure class as the
  promotion defect this repository already shipped (GitHub #22).
* **Machine-readable findings.** Each finding is a ``- key: value`` block so the
  close path can derive filing status mechanically rather than trusting prose.
  No YAML dependency: this runs inside the close path, which must not acquire
  new imports.
* **Fields shaped by real findings, not a generic form.** The per-category
  fields exist because this epic already produced findings of each shape (see
  the worked examples in the emitted template). A free-text box would have lost
  every one of them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SKILL_FEEDBACK_FILENAME = "skill_feedback.md"
RESULTS_DIRNAME = "results"

#: The four prompt sections required by references/migration.md Phase 6 and by
#: tickets/017-skill-feedback-loop.md. The slugs are the accepted ``category:``
#: values on a finding; the titles are the emitted section headings.
PROMPT_SECTIONS: tuple[tuple[str, str], ...] = (
    ("surviving-mutants", "Surviving mutants"),
    ("unmodelable-effects", "Unmodelable effects"),
    ("budget-and-metric", "Budget adjustments and metric calibration"),
    ("profile-schema-cli", "Profile, schema, and CLI workarounds"),
)

CATEGORY_SLUGS = tuple(slug for slug, _ in PROMPT_SECTIONS)

#: How badly the inadequacy hurt the migration that found it. ``silent-data-loss``
#: and ``wrong-result`` exist because this epic produced one of each and neither
#: is describable as "friction".
SEVERITIES = (
    "blocks-migration",
    "silent-data-loss",
    "wrong-result",
    "manual-workaround",
    "friction",
)

#: Where the inadequacy actually lives. This field exists because the epic's
#: most expensive finding (the incommensurable bound gate) was a *spec* error
#: with a correct implementation -- filing it against the code would have been
#: filed in the wrong place.
ROOT_CAUSES = ("tool", "spec", "target", "unknown")

#: Declared disposition of a close-out entry. ``none-found`` is a first-class
#: answer -- silence is not, for the same reason the standing complexity
#: objective requires "searched, found none" rather than an empty section.
FEEDBACK_STATUSES = ("unreviewed", "none-found", "items-recorded")

FEEDBACK_REPO = "spec-double-compiler / tla-spec-dev"

_FIELD_RE = re.compile(r"^-\s+([a-z_]+):\s*(.*)$")
_FINDING_RE = re.compile(r"^###\s+(SF-\d+)\b\s*(?:[-—]\s*)?(.*)$")
_ENTRY_RE = re.compile(r"^##\s+Close-out\s+(.*)$")
_URL_RE = re.compile(r"https?://\S+|#\d+\b")

_UNFILLED = {"", "tbd", "todo", "(none yet)", "none yet", "-", "n/a"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def results_dir(specs_dir: Path) -> Path:
    return specs_dir / RESULTS_DIRNAME


def skill_feedback_path(specs_dir: Path) -> Path:
    return results_dir(specs_dir) / SKILL_FEEDBACK_FILENAME


def is_unfilled(value: str) -> bool:
    return value.strip().lower() in _UNFILLED


@dataclass
class Finding:
    """One recorded tool inadequacy."""

    id: str
    title: str
    fields: dict[str, str] = field(default_factory=dict)

    @property
    def category(self) -> str:
        return self.fields.get("category", "").strip()

    @property
    def status(self) -> str:
        return self.fields.get("status", "").strip().lower()

    @property
    def recommendation(self) -> str:
        return self.fields.get("recommendation", "").strip()

    @property
    def reference(self) -> str | None:
        """The ticket/PR this finding was filed as, if any."""
        if is_unfilled(self.recommendation):
            return None
        match = _URL_RE.search(self.recommendation)
        return match.group(0) if match else None

    @property
    def filed(self) -> bool:
        return self.status == "filed" and self.reference is not None

    @property
    def needs_filing(self) -> bool:
        """Findings that are neither filed nor explicitly declined."""
        return self.status not in {"filed", "wontfix"} or (self.status == "filed" and self.reference is None)

    def to_record(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "severity": self.fields.get("severity", ""),
            "root_cause": self.fields.get("root_cause", ""),
            "target": self.fields.get("target", ""),
            "observed_on": self.fields.get("observed_on", ""),
            "evidence": self.fields.get("evidence", ""),
            "status": self.status,
            "recommendation": self.recommendation,
            "reference": self.reference,
            "filed": self.filed,
        }


@dataclass
class CloseOutEntry:
    heading: str
    fields: dict[str, str] = field(default_factory=dict)

    @property
    def declared_status(self) -> str:
        return self.fields.get("feedback_status", "").strip().lower()


def parse_findings(text: str) -> list[Finding]:
    findings: list[Finding] = []
    current: Finding | None = None
    for line in text.splitlines():
        heading = _FINDING_RE.match(line.strip())
        if heading:
            current = Finding(id=heading.group(1), title=heading.group(2).strip())
            findings.append(current)
            continue
        if line.startswith("#"):
            current = None
            continue
        if current is None:
            continue
        pair = _FIELD_RE.match(line.strip())
        if pair:
            current.fields[pair.group(1)] = pair.group(2).strip()
    return [item for item in findings if not item.id.startswith("SF-000")]


def parse_close_out_entries(text: str) -> list[CloseOutEntry]:
    entries: list[CloseOutEntry] = []
    current: CloseOutEntry | None = None
    for line in text.splitlines():
        heading = _ENTRY_RE.match(line.strip())
        if heading:
            current = CloseOutEntry(heading=heading.group(1).strip())
            entries.append(current)
            continue
        if line.startswith("#") and not line.startswith("###"):
            current = None
            continue
        if current is None:
            continue
        pair = _FIELD_RE.match(line.strip())
        if pair and pair.group(1) not in current.fields:
            current.fields[pair.group(1)] = pair.group(2).strip()
    return entries


def filing_status(text: str) -> dict[str, Any]:
    """Derive whether feedback was filed, and where, from the document itself."""
    findings = parse_findings(text)
    entries = parse_close_out_entries(text)
    filed = [item for item in findings if item.filed]
    unfiled = [item for item in findings if item.needs_filing]
    declared = entries[-1].declared_status if entries else ""
    if findings:
        resolved = not unfiled
    else:
        resolved = declared == "none-found"
    return {
        "declared_status": declared or "unreviewed",
        "findings_total": len(findings),
        "findings_filed": len(filed),
        "findings_unfiled": [item.id for item in unfiled],
        "filed": bool(filed),
        "resolved": resolved,
        "filed_where": [item.reference for item in filed],
        "findings": [item.to_record() for item in findings],
        "close_out_entries": len(entries),
    }


def render_template() -> str:
    """The living feedback document, written once and thereafter appended to."""
    sections = "\n".join(f"- `{slug}` — {title}" for slug, title in PROMPT_SECTIONS)
    return f"""# Skill feedback — {FEEDBACK_REPO}

`references/migration.md` Phase 6: a migration is not done when the models
converge. It is done when everything the skill **could not express** has been
turned into a concrete recommendation against the skill repository. The skill
improves only through what real migrations fail to express.

This file is **append-only by convention**. Close-out creates it once and
thereafter only appends. Never rewrite or delete an existing finding — a filled
finding is evidence.

## How to use this file

1. At each close-out the CLI appends a `## Close-out …` entry below.
2. Fill in that entry's `feedback_status`, then record one `### SF-NNN` finding
   per thing the skill could not express.
3. **Turn every finding into a ticket or PR against the spec-double-compiler
   repository** — that is the point of this file, not the record-keeping:

   ```
   gh issue create --repo haydenrear/tla-spec-dev \\
     --title "<SF-NNN one-line title>" --body-file <extract of the finding>
   ```

   Then set `recommendation:` to the resulting URL and `status: filed`.
4. If you looked and there was genuinely nothing, set
   `feedback_status: none-found`. **Silence is not an answer** — an unreviewed
   entry is recorded as unresolved in the close history.

## The four prompt categories

{sections}

## Finding format

Every finding is a `### SF-NNN` heading followed by `- key: value` lines. The
close path parses these, so keep the shape.

Fields required on every finding:

- `category:` one of {", ".join(f"`{slug}`" for slug in CATEGORY_SLUGS)}
- `target:` the exact tool surface that proved inadequate — command, script
  path and function, budget key, profile rule, or manifest field. Not "the CLI".
- `observed_on:` the real repository/module/ticket it was run against. A finding
  without a real target is a wish, not evidence.
- `evidence:` a durable path (command output, TLC log, report) — not prose.
- `severity:` one of {", ".join(f"`{s}`" for s in SEVERITIES)}
- `root_cause:` one of {", ".join(f"`{s}`" for s in ROOT_CAUSES)} — whether the
  tool's code, its specification, or the target under migration was at fault.
  A correct implementation of a wrong spec is `spec`; filing it against the
  code files it in the wrong place.
- `workaround_applied:` what the migration had to do to proceed, or `none`.
- `recommendation:` `ticket <url>` or `PR <url>` against {FEEDBACK_REPO}
- `status:` `open`, `filed`, or `wontfix`

Category-specific fields, so the common cases are structured rather than prose:

- `surviving-mutants` — `mutant:`, `operator:`, `location:`, `why_unreached:`
  (which generator, strategy, or profile rule could not reach it)
- `unmodelable-effects` — `effect:`, `why_not_port_state:`, `modeled_as:`
  (or `unmodeled`)
- `budget-and-metric` — `budget_key:`, `default_value:`, `value_used:`,
  `gated_quantity:` vs `measured_quantity:` (name both when a gate compares
  quantities that are not commensurable), `metric_blind_spot:` (what a passing
  metric failed to notice)
- `profile-schema-cli` — `surface:`, `forced_workaround:`, `data_loss:`
  (`yes`/`no`)

## Worked examples

These are real findings this epic produced *before* this template existed. They
are the calibration for what a good finding looks like; they are recorded here
as `SF-000x` examples and are excluded from filing status.

### SF-000a — Projected complexity reduction required deleting real behavior
- category: budget-and-metric
- target: scripts/analyze_complexity.py — projected-reduction reporting
- observed_on: tla-spec-dev @ MF-020 (ticket_phase ordinal collapse)
- evidence: specs/.history/modular-fuzzing-epic/ticket-*-MF-020/
- severity: wrong-result
- root_cause: tool
- gated_quantity: distinct reachable states
- measured_quantity: generated states
- metric_blind_spot: deleted self-loops. Reproducing the projected -13.1%
  required tightening a guard from `>= 2` to `= 2`, deleting a legitimate
  idempotent re-fire transition. The distinct-state gate is structurally blind
  to that, so a behavior deletion scored as a re-representation win.
- workaround_applied: projection withdrawn by hand after transition-level diff
- recommendation: ticket (example only)
- status: wontfix

### SF-000b — Promotion destroyed files unique to specs/current
- category: profile-schema-cli
- target: scripts/spec_evolution.py::replace_tree (ticket-close promotion)
- observed_on: tla-spec-dev @ MF-012, MF-020, MF-021
- evidence: tests/test_promotion_preserves_current.py
- severity: silent-data-loss
- root_cause: tool
- surface: `tla-spec-dev close ticket` promotion step
- forced_workaround: restore deleted regression tests from git history
- data_loss: yes
- recommendation: ticket https://github.com/haydenrear/tla-spec-dev/issues/22
- status: filed

### SF-000c — PATH wrapper ran pre-epic code for an entire epic
- category: profile-schema-cli
- target: `tla-spec-dev` PATH wrapper -> ~/.skill-manager/skills/spec-double-compiler
- observed_on: tla-spec-dev @ modular-fuzzing epic (all tickets)
- evidence: specs/desired_program_model/ticket_plan.yaml (toolchain_rule)
- severity: wrong-result
- root_cause: tool
- surface: skill installation / PATH shim
- forced_workaround: pin every lifecycle command to
  `python3 scripts/tla_spec_dev.py --spec-root specs ...`
- data_loss: yes — the stale wrapper is why the promotion defect fired three
  times, including once after its fix had merged
- recommendation: ticket (example only)
- status: wontfix

### SF-000d — Bound gate compared incommensurable quantities
- category: budget-and-metric
- target: scripts/analyze_complexity.py — state-space bound gate
- observed_on: tla-spec-dev @ MF-011
- evidence: specs/.history/modular-fuzzing-epic/ticket-*-MF-011/
- severity: blocks-migration
- root_cause: spec
- budget_key: max_distinct_states
- default_value: 50000
- value_used: new `max_state_space_bound` added (MF-022)
- gated_quantity: static state-space upper bound (1,179,648)
- measured_quantity: actual reachable distinct states (2,923)
- metric_blind_spot: a ~400x over-approximation failed a model 17x *under* its
  own budget; the tool's own recommended optimum still failed the gate.
- workaround_applied: none — gate reported its own failure rather than tuning
- recommendation: ticket https://github.com/haydenrear/tla-spec-dev/issues/28
- status: filed

---
"""


def render_close_out_entry(
    *,
    scope: str,
    scope_id: str,
    workflow: str,
    summary: str,
    deferred: list[str] | None = None,
) -> str:
    lines = [
        "",
        f"## Close-out {scope} {scope_id}",
        "",
        f"- close_scope: {scope}",
        f"- close_id: {scope_id}",
        f"- workflow: {workflow}",
        f"- closed_at: {_now()}",
        f"- summary: {summary or '(none given)'}",
        "- feedback_status: unreviewed",
    ]
    for item in deferred or []:
        lines.append(f"- deferred_validation: {item}")
    lines.extend(
        [
            "",
            "Set `feedback_status` to `none-found` or `items-recorded`, then record"
            " findings as `### SF-NNN` blocks below using the field list above.",
            "Every finding must become a ticket or PR against"
            f" {FEEDBACK_REPO}; put its URL in `recommendation:` and set `status: filed`.",
            "",
        ]
    )
    return "\n".join(lines)


def emit_skill_feedback(
    specs_dir: Path,
    *,
    scope: str,
    scope_id: str,
    workflow: str = "",
    summary: str = "",
    deferred: list[str] | None = None,
) -> dict[str, Any]:
    """Ensure the feedback document exists, append this close-out, report filing status.

    Returns the record embedded in the close-out history manifest. The document
    is created from the template only when absent; existing content is never
    rewritten.
    """
    path = skill_feedback_path(specs_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    template_emitted = not path.exists()
    if template_emitted:
        path.write_text(render_template(), encoding="utf-8")
    existing = path.read_text(encoding="utf-8")
    entry = render_close_out_entry(
        scope=scope,
        scope_id=scope_id,
        workflow=workflow,
        summary=summary,
        deferred=deferred,
    )
    if not existing.endswith("\n"):
        existing += "\n"
    path.write_text(existing + entry, encoding="utf-8")

    status = filing_status(path.read_text(encoding="utf-8"))
    record: dict[str, Any] = {
        "role": "skill_feedback",
        "path": str(path),
        "template_emitted": template_emitted,
        "close_out_entry": f"Close-out {scope} {scope_id}",
        "prompt_sections": [slug for slug, _ in PROMPT_SECTIONS],
        "feedback_repository": FEEDBACK_REPO,
        "deferred_validation": list(deferred or []),
    }
    record.update(status)
    return record


def print_skill_feedback_report(record: dict[str, Any] | None) -> None:
    """Never stay silent about the retro: say what was filed and what was not."""
    if not record:
        return
    print(f"skill feedback -> {record['path']}")
    if record.get("template_emitted"):
        print(f"  emitted template with {len(record['prompt_sections'])} prompt sections:"
              f" {', '.join(record['prompt_sections'])}")
    print(f"  appended entry: {record['close_out_entry']}")
    total = record.get("findings_total", 0)
    declared = record.get("declared_status", "unreviewed")
    if record.get("resolved"):
        if total:
            print(f"  feedback FILED: {record['findings_filed']}/{total} finding(s)")
            for where in record.get("filed_where", []):
                print(f"    -> {where}")
        else:
            print("  feedback status: none-found (searched, nothing to file)")
    else:
        print(f"  feedback NOT yet filed: declared_status={declared}, {total} finding(s) recorded")
        for unfiled in record.get("findings_unfiled", []):
            print(f"    ! {unfiled} has no ticket/PR against {record['feedback_repository']}")
        print("  fill in the close-out entry and file each finding before the workflow closes")
