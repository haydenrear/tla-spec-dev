#!/usr/bin/env python3
"""Corpus diagnostics and hard case caps (MF-014).

**Nothing in this module ever removes a case.**

There is deliberately no selection, sampling, distillation, trimming, or
truncation API here, and no caller is given one. Every function takes the
complete corpus and returns a *report about* it. The corpus that goes into
:func:`analyze_corpus` is byte-for-byte the corpus that gets written out,
whether the gate passes or fails.

That is the whole point of the ticket. Filtering cases to fit a budget
under-represents the program, which the standing objective in
``references/architecture_tractability.md`` forbids outright, and the
``kill_rate_floor`` does not make it safe: the mutation kill test seeds one
fault per port and per invariant, so it only *samples* for damage. A dropped
case that no mutant happens to probe is invisible to it. A recorded deletion
is still a deletion.

So the case caps -- ``max_internal_cases_per_component`` and
``max_external_cases_per_action`` -- are **hard gates**, in exactly the shape
MF-011 gave the state-space bound: over budget prints a report and exits
nonzero. It does not trim. There are two legitimate responses, and neither
one deletes anything:

1. **Redesign.** A lopsided corpus is evidence about the representation,
   not noise to clean up. A model emitting two hundred near-identical cases
   for one action and two for another is enumerating redundancy:
   interchangeable values, an unconstrained ordering, or an action enabled
   across many equivalent states. The corpus is the symptom; the diagram is
   the defect. This module's job is to measure which of those three it is,
   from what actually varies across the redundant group, and then ask the
   question: can the architecture be redesigned to make the program simpler,
   so the redundancy is never generated? That judgment belongs to the
   reader, made with the complexity descriptor (``analyze complexity``) and
   ``references/complexity_intuition.md``.
2. **Raise the cap**, with a recorded one-line rationale. Caps are
   per-program and negotiable like every other budget. That is an explicit,
   reviewable decision, and :func:`accept_path_snippet` prints the exact
   manifest edit that makes it. Silent trimming is not an option and does not
   exist in this file.

Labelers survive from ticket 003, repurposed from selection criteria to
**diagnostic strata**. Their output describes the distribution; it never
chooses which cases live. Named regression traces are likewise always
retained -- trivially so, because nothing is ever dropped -- and are reported
separately so that fact is visible rather than merely true.

The failure output states findings and asks a REDESIGN QUESTION; it never
prescribes a move and nothing is ever auto-applied. The judgment inputs are
the complexity descriptor (``analyze complexity``) and
``references/complexity_intuition.md``: take this complexity descriptor to
consider how to refactor complexity out of the app.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

try:
    from .budgets import load_budgets
except ImportError:  # pragma: no cover - direct script execution
    from budgets import load_budgets  # type: ignore[no-redef]


# The cap that applies to a corpus depends on the view it was generated for.
# Internal cases are capped per component (the case package as a whole);
# external cases are capped per public action.
CAP_BUDGET_FOR_VIEW: dict[str, str] = {
    "internal": "max_internal_cases_per_component",
    "external": "max_external_cases_per_action",
}
CAP_SCOPE_FOR_VIEW: dict[str, str] = {
    "internal": "component",
    "external": "action",
}

# A stratum with no labeler-supplied class is still a stratum; it is reported
# under this name rather than dropped from the table.
UNLABELED = "(unlabeled)"

# Label prefix marking a promoted counterexample, Hypothesis failure, or
# production bug. These are always retained. So is everything else, but these
# are called out so the guarantee is visible in the report.
REGRESSION_LABEL_PREFIX = "regression"

# A stratum counts as starved when it holds this fraction or less of the
# dominant stratum's cases.
STARVED_FRACTION = 0.05

# How many varying fields the report names before it stops listing.
MAX_VARYING_FIELDS = 8

# The over-cap failure output ends with this question, never a prescribed
# move. The gate measures; the reader judges, with the complexity descriptor
# and the intuition doc as the judgment inputs (CD-04, resolving VAL-13).
REDESIGN_QUESTION = (
    "REDESIGN QUESTION: can the architecture be redesigned to make the\n"
    "program simpler, so these cases are never generated? That judgment is\n"
    "yours, not this tool's: take the complexity descriptor\n"
    "(`tla-spec-dev analyze complexity`) together with\n"
    "references/complexity_intuition.md and consider how to refactor\n"
    "complexity out of the app. Nothing is prescribed here, and nothing is\n"
    "applied automatically."
)


# --------------------------------------------------------------------------
# Case access
#
# Generated case objects and exported trace dicts have slightly different
# shapes. These readers accept either so the same diagnostics run over a
# generated package and over a directory of exported Test Graph traces.
# --------------------------------------------------------------------------


def case_action(case: Any) -> str:
    """The action name a case exercises."""
    if isinstance(case, dict):
        steps = case.get("steps") or [{}]
        return str(steps[0].get("action", "?"))
    edge = getattr(case, "edge", None)  # PreparedCase, pre-render
    if edge is not None:
        return str(edge.action)
    return str(case.input.action)


def case_labels(case: Any) -> tuple[str, ...]:
    """Every label on a case, sorted for stable reporting."""
    if isinstance(case, dict):
        steps = case.get("steps") or [{}]
        raw = (steps[0].get("raw") or {}).get("labels", ())
    else:
        raw = getattr(case, "labels", ())
    return tuple(sorted(str(label) for label in raw))


def case_name(case: Any) -> str:
    if isinstance(case, dict):
        return str(case.get("trace_id", "?"))
    return str(getattr(case, "name", "?"))


def case_params(case: Any) -> dict[str, Any]:
    if isinstance(case, dict):
        steps = case.get("steps") or [{}]
        params = steps[0].get("params") or {}
    elif getattr(case, "edge", None) is not None:  # PreparedCase, pre-render
        params = getattr(case, "params", {}) or {}
    else:
        params = getattr(case.input, "params", {}) or {}
    return dict(params) if isinstance(params, dict) else {}


def case_before(case: Any) -> dict[str, Any]:
    if isinstance(case, dict):
        steps = case.get("steps") or [{}]
        return dict(steps[0].get("pre") or {})
    return dict(getattr(case, "before", {}) or {})


def case_after(case: Any) -> dict[str, Any]:
    if isinstance(case, dict):
        steps = case.get("steps") or [{}]
        return dict(steps[0].get("post") or {})
    return dict(getattr(case, "after", {}) or {})


def case_source_node(case: Any) -> str:
    if isinstance(case, dict):
        steps = case.get("steps") or [{}]
        return str((steps[0].get("raw") or {}).get("source_node", ""))
    edge = getattr(case, "edge", None)  # PreparedCase, pre-render
    if edge is not None:
        return str(edge.source)
    return str(getattr(case.input, "source_node", ""))


def label_classes(case: Any) -> tuple[str, ...]:
    """Labeler-supplied strata for a case, excluding its own action name.

    The generator always labels a case with its action, which carries no
    stratifying information beyond the action axis the report already has.
    What is left is what a labeler contributed -- the diagnostic strata.
    """
    action = case_action(case)
    classes = tuple(label for label in case_labels(case) if label != action)
    return classes or (UNLABELED,)


def is_regression_case(case: Any) -> bool:
    """A promoted counterexample / Hypothesis failure / production bug."""
    return any(
        label == REGRESSION_LABEL_PREFIX or label.startswith(f"{REGRESSION_LABEL_PREFIX}:")
        for label in case_labels(case)
    )


# --------------------------------------------------------------------------
# Report data
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Stratum:
    """One ``(action, label class)`` cell of the distribution."""

    action: str
    label_class: str
    count: int

    @property
    def key(self) -> str:
        return f"{self.action} / {self.label_class}"


@dataclass(frozen=True)
class VaryingField:
    """One field that differs across a redundant group, and by how much."""

    field: str
    distinct: int
    total: int
    examples: tuple[str, ...]
    permutation_family: bool = False

    @property
    def saturating(self) -> bool:
        """The field takes a distinct value in (almost) every case.

        A field that is unique per case is the field the redundancy is being
        enumerated over.
        """
        return self.total > 1 and self.distinct >= max(2, int(self.total * 0.9))


@dataclass(frozen=True)
class RedundantGroup:
    """An over-cap group, with the evidence about why it is over cap."""

    scope: str
    key: str
    count: int
    cap: int
    strata: tuple[Stratum, ...]
    dominant: tuple[Stratum, ...]
    starved: tuple[Stratum, ...]
    varying: tuple[VaryingField, ...]
    constant_fields: tuple[str, ...]
    distinct_change_shapes: int
    distinct_source_states: int
    cause: str
    cause_evidence: tuple[str, ...]

    @property
    def overage(self) -> int:
        return self.count - self.cap


@dataclass(frozen=True)
class CorpusReport:
    """The complete diagnostic picture. Contains no cases, only counts."""

    view: str
    cap_budget: str
    cap: int
    scope: str
    total_cases: int
    group_counts: dict[str, int]
    strata: tuple[Stratum, ...]
    over_cap: tuple[RedundantGroup, ...]
    regression_cases: tuple[str, ...]
    manifest_path: Path | None = None
    source: str = ""

    #: `CA-10-DF-19`, second entrance, repaired by `SS-05`. WHERE THE CAP CAME
    #: FROM, carried alongside the cap itself.
    #:
    #: `analyze_corpus` called `load_budgets(Path("__missing__"), warn=False)` when
    #: the upward walk found no `spec_manifest.yaml`, which SUPPRESSES
    #: `budgets.py`'s own *"no readable spec manifest"* warning on exactly the
    #: path where it is load-bearing. The report then printed
    #: `cap max_external_cases_per_action = 50` with nothing saying the 50 was a
    #: documented default rather than the project's negotiated 10. A number whose
    #: provenance is not on the page is read as measured.
    #:
    #: `False` means the caps are DOCUMENTED DEFAULTS and no manifest was found.
    cap_from_manifest: bool = True

    @property
    def passed(self) -> bool:
        return not self.over_cap


# --------------------------------------------------------------------------
# Distribution
# --------------------------------------------------------------------------


def group_key_for(case: Any, scope: str) -> str:
    """The unit the cap applies to: one component, or one action."""
    return case_action(case) if scope == "action" else "component"


def distribution(cases: Sequence[Any]) -> tuple[Stratum, ...]:
    """Count per ``(action, label class)`` over the whole corpus.

    A case with several label classes is counted in each of them, because the
    question the table answers is "how many cases does this stratum contain",
    not "how do the cases partition".
    """
    counts: dict[tuple[str, str], int] = {}
    for case in cases:
        action = case_action(case)
        for label_class in label_classes(case):
            counts[(action, label_class)] = counts.get((action, label_class), 0) + 1
    return tuple(
        sorted(
            (Stratum(action=a, label_class=c, count=n) for (a, c), n in counts.items()),
            key=lambda s: (-s.count, s.action, s.label_class),
        )
    )


def dominant_and_starved(
    strata: Sequence[Stratum],
) -> tuple[tuple[Stratum, ...], tuple[Stratum, ...]]:
    """Split strata into the ones carrying the corpus and the ones starved.

    Dominant strata are those at or above the mean; starved strata are those
    holding ``STARVED_FRACTION`` or less of the largest stratum. A starved
    stratum is the interesting half of the signal: it says the model is
    spending its enumeration budget somewhere other than on that behavior.
    """
    if not strata:
        return (), ()
    largest = max(s.count for s in strata)
    mean = sum(s.count for s in strata) / len(strata)
    threshold = max(1, math.floor(largest * STARVED_FRACTION))
    dominant = tuple(s for s in strata if s.count >= mean and s.count > threshold)
    starved = tuple(s for s in strata if s.count <= threshold)
    return dominant, starved


# --------------------------------------------------------------------------
# What varies across the redundant group
#
# This is the actionable part. Which fields differ across a group of
# near-identical cases tells you which of the three moves the diagram needs.
# --------------------------------------------------------------------------


def _stable_repr(value: Any) -> str:
    if isinstance(value, dict):
        return "{" + ", ".join(f"{k}={_stable_repr(v)}" for k, v in sorted(value.items(), key=lambda i: str(i[0]))) + "}"
    if isinstance(value, (set, frozenset)):
        return "{" + ", ".join(sorted(_stable_repr(v) for v in value)) + "}"
    if isinstance(value, (list, tuple)):
        return "<" + ", ".join(_stable_repr(v) for v in value) + ">"
    return repr(value)


def _flatten(prefix: str, value: Any, out: dict[str, Any]) -> None:
    """Flatten a nested state/param mapping into dotted field paths."""
    if isinstance(value, dict) and value:
        for key, inner in sorted(value.items(), key=lambda i: str(i[0])):
            _flatten(f"{prefix}.{key}", inner, out)
        return
    out[prefix] = value


def case_fields(case: Any) -> dict[str, Any]:
    """Every SEMANTIC field of a case, as dotted paths.

    Deliberately excludes ``source_node``: a TLC node id is an identity, unique
    by construction, so listing it as the most-varying field is noise that
    crowds out the fields a reader can act on. How many distinct source states
    a group has is still reported -- as abstraction evidence, where it means
    something -- rather than as a varying field.
    """
    out: dict[str, Any] = {}
    _flatten("params", case_params(case), out)
    _flatten("before", case_before(case), out)
    _flatten("after", case_after(case), out)
    return out


def change_shape(case: Any) -> str:
    """The *names* of the fields a case changes, ignoring their values.

    Two cases with the same change shape do the same thing structurally. A
    group with exactly one change shape but many distinct before-states is an
    action enabled across many equivalent states.
    """
    before = case_before(case)
    after = case_after(case)
    changed = sorted(
        f for f in set(before) | set(after) if before.get(f) != after.get(f)
    )
    return ",".join(changed)


def _is_permutation_family(values: Sequence[Any]) -> bool:
    """Do these values differ only in the order of the same elements?

    That is the fingerprint of an unconstrained ordering: TLC enumerated every
    interleaving of the same multiset because nothing in the diagram said the
    order was irrelevant.
    """
    sequences = [v for v in values if isinstance(v, (list, tuple))]
    if len(sequences) < 2 or len(sequences) != len(values):
        return False
    multisets = {tuple(sorted(_stable_repr(item) for item in seq)) for seq in sequences}
    orderings = {tuple(_stable_repr(item) for item in seq) for seq in sequences}
    return len(multisets) == 1 and len(orderings) > 1


def varying_fields(cases: Sequence[Any]) -> tuple[tuple[VaryingField, ...], tuple[str, ...]]:
    """What differs across a group, and what is held constant."""
    if not cases:
        return (), ()
    per_field: dict[str, list[Any]] = {}
    for case in cases:
        for name, value in case_fields(case).items():
            per_field.setdefault(name, []).append(value)

    varying: list[VaryingField] = []
    constant: list[str] = []
    total = len(cases)
    for name, values in sorted(per_field.items()):
        rendered = [_stable_repr(v) for v in values]
        distinct = sorted(set(rendered))
        if len(distinct) <= 1:
            constant.append(name)
            continue
        varying.append(
            VaryingField(
                field=name,
                distinct=len(distinct),
                total=total,
                examples=tuple(distinct[:3]),
                permutation_family=_is_permutation_family(values),
            )
        )
    varying.sort(key=lambda v: (-v.distinct, v.field))
    return tuple(varying), tuple(constant)


def classify_cause(
    cases: Sequence[Any],
    varying: Sequence[VaryingField],
    distinct_change_shapes: int,
    distinct_source_states: int = 0,
) -> tuple[str, tuple[str, ...]]:
    """Name the representation pattern behind a redundant group.

    Returns ``(cause, evidence)``. Both are measurements: the cause names the
    redundancy fingerprint the group matched, and the evidence lists the
    observations that matched it. Nothing here prescribes a fix -- what to do
    about the pattern, if anything, is the reader's redesign judgment, made
    with the complexity descriptor and ``references/complexity_intuition.md``.
    """
    total = len(cases)
    params_vary = [v for v in varying if v.field.startswith("params.")]
    state_vary = [v for v in varying if v.field.startswith(("before.", "after."))]
    permuting = [v for v in varying if v.permutation_family]

    # A parameter sweep is usually a CROSS PRODUCT: no single parameter is
    # distinct per case, but the tuple of them is. Measure the joint value,
    # otherwise a client x sku sweep reads as two unremarkable fields.
    joint_params = {
        tuple(sorted((k, _stable_repr(v)) for k, v in case_params(c).items())) for c in cases
    }
    joint_params_saturating = total > 1 and len(joint_params) >= max(2, int(total * 0.9))

    # 1. Unconstrained ordering. The most specific fingerprint: the same
    #    elements in different orders. Check it first.
    if permuting:
        fields = ", ".join(v.field for v in permuting[:3])
        return (
            "unconstrained ordering",
            (
                f"{len(permuting)} field(s) vary only by element order: {fields}",
                f"every value is a permutation of the same multiset across {total} cases",
                "TLC enumerated each interleaving because nothing declares the order irrelevant",
            ),
        )

    # 2. Interchangeable values. Parameters sweep a domain while the
    #    structural shape of the transition stays fixed.
    if params_vary and joint_params_saturating and distinct_change_shapes <= max(1, total // 10):
        fields = ", ".join(f"{v.field} ({v.distinct} values)" for v in params_vary[:3])
        return (
            "interchangeable values",
            (
                f"parameter(s) sweep a domain while the transition shape is fixed: {fields}",
                f"{len(joint_params)} distinct parameter combinations across {total} cases",
                f"{distinct_change_shapes} distinct change shape(s) across {total} cases",
                "the cases differ in which value was chosen, not in what the action does",
            ),
        )

    # 3. Action enabled across many equivalent states. One structural
    #    behavior, replayed from every reachable before-state.
    if state_vary and distinct_change_shapes <= max(1, total // 10):
        fields = ", ".join(f"{v.field} ({v.distinct} values)" for v in state_vary[:3])
        return (
            "action enabled across equivalent states",
            (
                f"{distinct_change_shapes} distinct change shape(s) across {total} cases",
                f"but the before-state varies widely: {fields}",
                f"{distinct_source_states} distinct source states in the reachable graph",
                "the action does one thing, generated once per reachable state that enables it",
            ),
        )

    fields = ", ".join(v.field for v in varying[:3]) or "nothing"
    return (
        "unclassified",
        (
            f"{distinct_change_shapes} distinct change shape(s) across {total} cases",
            f"most-varying field(s): {fields}",
            "the group does not match the ordering, symmetry, or abstraction fingerprint",
        ),
    )


# --------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------


def analyze_corpus(
    cases: Sequence[Any],
    *,
    view: str,
    manifest_path: Path | str | None = None,
    budgets: dict[str, Any] | None = None,
    source: str = "",
    warn: bool = True,
) -> CorpusReport:
    """Measure a corpus against its cap. Returns a report; drops nothing.

    ``cases`` is the COMPLETE corpus. This function does not accept a
    selection, does not apply one, and does not return cases. Callers gate on
    ``report.passed`` and either fix the diagram or raise the cap.
    """
    if view not in CAP_BUDGET_FOR_VIEW:
        raise ValueError(f"unsupported view {view!r}; expected one of {sorted(CAP_BUDGET_FOR_VIEW)}")
    cap_budget = CAP_BUDGET_FOR_VIEW[view]
    scope = CAP_SCOPE_FOR_VIEW[view]

    # `CA-10-DF-19`, second entrance, repaired by `SS-05`. The `warn=False` on the
    # no-manifest branch silenced `budgets.py`'s own "no readable spec manifest"
    # warning at exactly the point where it is load-bearing, and the report then
    # printed the documented default as though it had been read from the project.
    # The suppression stays -- `budgets.py` is outside this ticket's conflict keys
    # and duplicating its warning here would double-report for callers that pass a
    # manifest -- but the FACT now travels with the number, in the report, on the
    # page, where the verdict is read.
    cap_from_manifest = True
    if budgets is None:
        if manifest_path:
            budgets = load_budgets(manifest_path, warn=warn)
        else:
            budgets = load_budgets(Path("__missing__"), warn=False)
            cap_from_manifest = False
    cap = int(budgets[cap_budget])

    groups: dict[str, list[Any]] = {}
    for case in cases:
        groups.setdefault(group_key_for(case, scope), []).append(case)

    over: list[RedundantGroup] = []
    for key in sorted(groups, key=lambda k: (-len(groups[k]), k)):
        members = groups[key]
        if len(members) <= cap:
            continue
        strata = distribution(members)
        dominant, starved = dominant_and_starved(strata)
        varying, constant = varying_fields(members)
        shapes = len({change_shape(c) for c in members})
        sources = len({case_source_node(c) for c in members})
        cause, evidence = classify_cause(members, varying, shapes, sources)
        over.append(
            RedundantGroup(
                scope=scope,
                key=key,
                count=len(members),
                cap=cap,
                strata=strata,
                dominant=dominant,
                starved=starved,
                varying=varying[:MAX_VARYING_FIELDS],
                constant_fields=constant,
                distinct_change_shapes=shapes,
                distinct_source_states=sources,
                cause=cause,
                cause_evidence=evidence,
            )
        )

    return CorpusReport(
        view=view,
        cap_budget=cap_budget,
        cap=cap,
        scope=scope,
        total_cases=len(cases),
        group_counts={k: len(v) for k, v in groups.items()},
        strata=distribution(cases),
        over_cap=tuple(over),
        regression_cases=tuple(sorted(case_name(c) for c in cases if is_regression_case(c))),
        manifest_path=Path(manifest_path) if manifest_path else None,
        source=source,
        cap_from_manifest=cap_from_manifest,
    )


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


def accept_path_snippet(report: CorpusReport) -> str:
    """The exact manifest edit that raises the cap, with its rationale slot.

    This is the "accept" path, and it is deliberately the easiest thing in the
    failure output to act on. Raising a cap is a legitimate, reviewable
    decision recorded in program state. Deleting cases is not a decision the
    tool offers at all.
    """
    needed = max((g.count for g in report.over_cap), default=report.cap)
    where = report.manifest_path or Path("<spec-dir>/spec_manifest.yaml")
    return (
        f"ACCEPT PATH -- raise the cap, with a rationale, in {where}:\n"
        "\n"
        "  budgets:\n"
        f"    {report.cap_budget}: {needed}    # was {report.cap}\n"
        "    source: negotiated\n"
        "    rationale:\n"
        f"      {report.cap_budget}: \"<one line: why this program genuinely needs "
        f"{needed} cases per {report.scope}>\"\n"
        "\n"
        "That is an explicit, reviewable decision recorded in program state.\n"
        "There is no trimming option, opt-in or otherwise: cases are never\n"
        "dropped, filtered, sampled, or truncated to fit a budget."
    )


def _stratum_table(
    strata: Sequence[Stratum], indent: str = "  ", total: int | None = None
) -> list[str]:
    """Render a stratum table. Percentages are relative to ``total``.

    Callers rendering a SUBSET (the dominant strata, say) must pass the whole
    corpus total, otherwise a starved stratum renders as a large share of the
    starved subset and reads as the opposite of what it is.
    """
    if not strata:
        return [f"{indent}(none)"]
    width = max(len(s.key) for s in strata)
    total = total if total is not None else sum(s.count for s in strata)
    total = total or 1
    return [
        f"{indent}{s.key.ljust(width)}  {s.count:>6}  {s.count * 100.0 / total:5.1f}%"
        for s in strata
    ]


def render_report(report: CorpusReport) -> str:
    """The full diagnostic report, pass or fail."""
    lines: list[str] = []
    verdict = "PASS" if report.passed else "FAIL"
    lines.append(
        f"corpus gate {verdict}: {report.total_cases} {report.view} case(s), cap "
        f"{report.cap_budget} = {report.cap} per {report.scope}"
    )
    if not report.cap_from_manifest:
        # `CA-10-DF-19`, second entrance. The cap is a DOCUMENTED DEFAULT and the
        # page now says so, next to the number, rather than presenting it as the
        # project's negotiated threshold.
        lines.append(
            f"cap provenance: DOCUMENTED DEFAULT -- no spec_manifest.yaml was "
            f"found above this corpus, so {report.cap_budget} = {report.cap} is "
            f"the fallback in references/modular_fuzzing.md and NOT this "
            f"project's negotiated cap. A verdict against a default is a verdict "
            f"about the default (CA-10-DF-19)."
        )
    if report.source:
        lines.append(f"source: {report.source}")
    lines.append("")

    lines.append(f"Distribution per (action, label class) -- {len(report.strata)} stratum/strata:")
    lines.extend(_stratum_table(report.strata))
    lines.append("")

    # The dominant/starved split across the WHOLE corpus. This is where the
    # lopsidedness shows: one action at 200 cases beside another at 2 is the
    # signal, and it is invisible inside any single over-cap group.
    corpus_total = sum(s.count for s in report.strata)
    corpus_dominant, corpus_starved = dominant_and_starved(report.strata)
    if corpus_dominant or corpus_starved:
        lines.append("Strata that DOMINATE the corpus:")
        lines.extend(_stratum_table(corpus_dominant, total=corpus_total))
        lines.append("")
        lines.append("Strata that are STARVED:")
        lines.extend(_stratum_table(corpus_starved, total=corpus_total))
        if corpus_dominant and corpus_starved:
            ratio = corpus_dominant[0].count / max(1, corpus_starved[-1].count)
            lines.append("")
            lines.append(
                f"  Skew: {corpus_dominant[0].key} holds {ratio:.0f}x the cases of "
                f"{corpus_starved[-1].key}."
            )
            lines.append(
                "  A starved stratum is the interesting half: the model is spending its"
            )
            lines.append(
                "  enumeration budget somewhere other than on that behavior."
            )
        lines.append("")

    if report.regression_cases:
        lines.append(
            f"Named regression traces (always retained): {len(report.regression_cases)}"
        )
        for name in report.regression_cases[:10]:
            lines.append(f"  {name}")
        lines.append("")

    if report.passed:
        lines.append(
            f"Every {report.scope} is within cap. Largest: "
            + ", ".join(
                f"{k}={v}"
                for k, v in sorted(report.group_counts.items(), key=lambda i: -i[1])[:3]
            )
        )
        lines.append("")
        lines.append("No case was dropped, filtered, sampled, or truncated.")
        return "\n".join(lines)

    lines.append(
        "corpus gate FAIL -- this corpus exceeds its manifest cap. Nothing was"
    )
    lines.append(
        "trimmed: the full corpus was written, and this gate refuses instead."
    )
    lines.append("")
    lines.append(
        "A lopsided corpus is evidence about the REPRESENTATION, not noise to"
    )
    lines.append(
        "clean up. The corpus is the symptom; the diagram is the defect."
    )
    lines.append("")

    for group in report.over_cap:
        lines.append(f"--- {group.scope} {group.key}: {group.count} cases, cap {group.cap} (over by {group.overage})")
        lines.append("")
        # Only worth splitting when the group actually spans several label
        # classes; a single-stratum group would render a full table and an
        # empty one, saying nothing.
        if len(group.strata) > 1:
            lines.append("  Strata within this group that DOMINATE:")
            lines.extend(_stratum_table(group.dominant, indent="    ", total=group.count))
            lines.append("")
            lines.append("  Strata within this group that are STARVED:")
            lines.extend(_stratum_table(group.starved, indent="    ", total=group.count))
            lines.append("")
        else:
            lines.append(f"  Single stratum: {group.strata[0].key}")
            lines.append("")
        lines.append("  What VARIES across the redundant group:")
        if group.varying:
            width = max(len(v.field) for v in group.varying)
            for v in group.varying:
                mark = "  <- permutations of one multiset" if v.permutation_family else ""
                saturating = "  <- distinct per case" if v.saturating and not v.permutation_family else ""
                lines.append(
                    f"    {v.field.ljust(width)}  {v.distinct:>5} distinct / {v.total} cases"
                    f"{mark}{saturating}"
                )
                lines.append(f"    {' ' * width}  e.g. {'; '.join(v.examples)}")
        else:
            lines.append("    (nothing varies -- the cases are identical)")
        lines.append("")
        if group.constant_fields:
            shown = ", ".join(group.constant_fields[:6])
            more = f" (+{len(group.constant_fields) - 6} more)" if len(group.constant_fields) > 6 else ""
            lines.append(f"  Held CONSTANT across the group: {shown}{more}")
            lines.append("")
        lines.append(f"  Likely cause: {group.cause}")
        for item in group.cause_evidence:
            lines.append(f"    - {item}")
        lines.append("")

    lines.append(
        "The measurements above are the finding. This gate prescribes nothing"
    )
    lines.append("and applies nothing; it refuses, and leaves the judgment to you.")
    lines.append("")
    lines.append(REDESIGN_QUESTION)
    lines.append("")
    lines.append("Two ways forward, and neither deletes a case:")
    lines.append("")
    lines.append("  1. REDESIGN so the redundant cases are never generated -- if,")
    lines.append("     taking the descriptor and references/complexity_intuition.md")
    lines.append("     as the judgment inputs, you conclude the architecture can be")
    lines.append("     made simpler.")
    lines.append("")
    lines.append("  2. " + accept_path_snippet(report).replace("\n", "\n     "))
    return "\n".join(lines)


def gate_report(
    cases: Sequence[Any],
    *,
    view: str,
    manifest_path: Path | str | None = None,
    budgets: dict[str, Any] | None = None,
    source: str = "",
    warn: bool = True,
) -> tuple[bool, str]:
    """Run the cap gate. Returns ``(passed, message)``.

    Deliberately the same shape as ``analyze_complexity.gate_report`` so the
    two hard gates read identically at every call site.
    """
    report = analyze_corpus(
        cases, view=view, manifest_path=manifest_path, budgets=budgets, source=source, warn=warn
    )
    return report.passed, render_report(report)


def enforce_case_cap(
    cases: Sequence[Any],
    *,
    view: str,
    manifest_path: Path | str | None,
    source: str,
    stream: Any = None,
) -> None:
    """Hard gate: print and raise ``SystemExit(2)`` when over cap.

    Called AFTER the full corpus has been written. The corpus on disk is
    complete whether this passes or fails -- failing the gate never removes
    anything, it only refuses to call the result acceptable.
    """
    import sys as _sys

    stream = _sys.stderr if stream is None else stream
    passed, message = gate_report(
        cases, view=view, manifest_path=manifest_path, source=source
    )
    if passed:
        print(message)
        return
    print(message, file=stream)
    print("", file=stream)
    print(
        "REFUSING to accept this corpus. Fix the diagram, or raise the cap with a\n"
        "recorded rationale. There is no override that trims cases.",
        file=stream,
    )
    raise SystemExit(2)


# --------------------------------------------------------------------------
# CLI: `tla-spec-dev analyze corpus`
# --------------------------------------------------------------------------

EXIT_OK = 0
EXIT_OVER_CAP = 1
EXIT_USAGE = 2


def add_arguments(parser: Any) -> Any:
    parser.add_argument(
        "cases_dir",
        type=Path,
        help="Generated case package directory, or a directory of exported trace JSON files.",
    )
    parser.add_argument(
        "--view",
        choices=sorted(CAP_BUDGET_FOR_VIEW),
        help="Which cap applies. Defaults to the package's own SOURCE_VIEW.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="spec_manifest.yaml supplying the caps. Defaults to the nearest one above the package.",
    )
    return parser


# Generated packages land under a per-view directory; older packages predate
# the SOURCE_VIEW constant, so the directory and the cases themselves are the
# fallback signals. Getting this wrong would apply the wrong cap silently.
VIEW_FOR_OUTPUT_DIR = {"spec-unit": "internal", "spec_unit": "internal", "testgraph": "external"}


def infer_view(cases_dir: Path, cases: Sequence[Any]) -> str | None:
    """Infer which cap applies when the package does not declare SOURCE_VIEW."""
    for case in cases:
        for attr in ("view", "layer"):
            value = getattr(case, attr, None)
            if value in CAP_BUDGET_FOR_VIEW:
                return str(value)
    for part in [cases_dir.name, *(p.name for p in cases_dir.parents)]:
        if part in VIEW_FOR_OUTPUT_DIR:
            return VIEW_FOR_OUTPUT_DIR[part]
    return None


def load_corpus(cases_dir: Path) -> tuple[list[Any], str | None]:
    """Load a corpus from a generated package or a directory of traces.

    Returns every case. There is no selection parameter, by design.
    """
    import json
    import sys as _sys

    cases_dir = Path(cases_dir)
    if (cases_dir / "cases.py").is_file():
        parent = str(cases_dir.parent.resolve())
        if parent not in _sys.path:
            _sys.path.insert(0, parent)
        try:
            from .run_generated_case_adapters import load_cases
        except ImportError:  # pragma: no cover - direct script execution
            from run_generated_case_adapters import load_cases  # type: ignore[no-redef]
        module = load_cases(cases_dir)
        cases = list(module.CASES)
        # `CA-10-DF-19` / `CA-06-DF-05`, repaired by `SS-05`. AN EMPTY GENERATED
        # PACKAGE USED TO BE ACCEPTED WHILE AN EMPTY TRACE DIRECTORY EIGHT LINES
        # BELOW REFUSED. `cases.py` carrying `CASES = []` returned `[]`, the cap
        # comparison then held vacuously, and the gate printed
        # `corpus gate PASS: 0 internal case(s)` at exit 0. That asymmetry is the
        # sink `CA-06-DF-01` drained into: the generator emitted `CASES = []` and
        # this accepted it. The refusal to copy was already in this same
        # function, and this is the copy.
        if not cases:
            raise SystemExit(
                f"UNDECIDED [empty]: {cases_dir}/cases.py declares CASES = [] -- "
                f"zero cases. `corpus gate PASS: 0 case(s)` would be a cap "
                f"satisfied by a corpus that was never generated. Nothing was "
                f"measured, so nothing is over cap and nothing is under it "
                f"(CA-06-DF-05 / CA-10-DF-19, and this is the same refusal an "
                f"empty TRACE directory has always given)."
            )
        return cases, getattr(module, "SOURCE_VIEW", None) or infer_view(cases_dir, cases)

    traces = sorted(p for p in cases_dir.glob("*.json") if p.name != "manifest.json")
    if not traces:
        raise SystemExit(f"ERROR: no generated cases or trace JSON files in {cases_dir}")
    loaded = [json.loads(p.read_text(encoding="utf-8")) for p in traces]
    view = loaded[0].get("view") if loaded else None
    return loaded, view


def run(args: Any) -> int:
    cases_dir = Path(args.cases_dir).resolve()
    if not cases_dir.is_dir():
        print(f"ERROR: case directory not found: {cases_dir}", file=__import__("sys").stderr)
        return EXIT_USAGE

    cases, package_view = load_corpus(cases_dir)
    # `CA-10-DF-19`, third entrance, repaired by `SS-05`. THIS READ
    # `args.view or package_view or "internal"`. `infer_view` returns `None` when
    # the package declares no `SOURCE_VIEW` and no directory name matches, so an
    # EXTERNAL corpus fell through to the INTERNAL cap -- 200 instead of 50 -- and
    # a 120-case external corpus PASSED AT FOUR TIMES ITS REAL CAP. The default
    # was silent and it was applied at exactly the point where it decides the
    # verdict. An unattributable corpus has no cap, so it gets no verdict.
    view = args.view or package_view
    if view is None:
        print(
            f"UNDECIDED [empty]: {cases_dir} declares no SOURCE_VIEW, no case "
            f"carries a `view`/`layer`, and no directory on its path names one, "
            f"so WHICH CAP APPLIES IS UNKNOWN. `internal` is capped by "
            f"`{CAP_BUDGET_FOR_VIEW['internal']}` and `external` by "
            f"`{CAP_BUDGET_FOR_VIEW['external']}`, the two differ, and defaulting "
            f"to `internal` gated external corpora at four times their real cap "
            f"(CA-10-DF-19). Pass --view explicitly.",
            file=__import__("sys").stderr,
        )
        return EXIT_USAGE
    if view not in CAP_BUDGET_FOR_VIEW:
        print(f"ERROR: unsupported view {view!r}", file=__import__("sys").stderr)
        return EXIT_USAGE

    manifest = Path(args.manifest).resolve() if args.manifest else None
    if manifest is None:
        for parent in [cases_dir, *cases_dir.parents]:
            candidate = parent / "spec_manifest.yaml"
            if candidate.is_file():
                manifest = candidate
                break

    report = analyze_corpus(
        cases, view=view, manifest_path=manifest, source=str(cases_dir)
    )
    print(render_report(report))
    return EXIT_OK if report.passed else EXIT_OVER_CAP


def main() -> int:  # pragma: no cover - exercised through the CLI
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser)
    return run(parser.parse_args())


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
