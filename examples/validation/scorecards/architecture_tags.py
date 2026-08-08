#!/usr/bin/env python3
"""The `effect_boundary` axis: one architecture tag, and what it may refuse.

RD-05, implementing `references/architecture_tags.md` (RD-04's design). Read
that file first -- the measurement behind every number here is
`specs/results/scorecards/reading-discipline/GOAL-tags-earn-their-place/RD-04/`.

WHAT THIS IS FOR. `R-H1` has carried two comparability axes -- same example,
unchanged instrument. Architecture is a third and has been handled by prose
telling readers that a deliberately incoherent fixture is *supposed* to score
low on D3. This makes that third axis a computed field, so an
architecture-scoped claim can be refused the way an example-scoped one is.

THE TRAP, AND THE THREE THINGS THAT KEEP IT SHUT.

  1. REFUSAL AUTHORITY IS PER DIMENSION. Over 34 cards of `ab_quota_ledger`,
     D3 separates disjointly and D1, D2, D4 and D5 all overlap. So the tag may
     annotate a D3 comparison and HAS NO AUTHORITY ANYWHERE ELSE. Authority is
     keyed on `(dimension, value-pair)` and re-derived from the cards on every
     `audit`; a value pair with no demonstrated separation on a dimension
     cannot excuse a comparison on it.

  2. AN `INCOMPARABLE` PAIR PRINTS BOTH SCORES. The verdict annotates the
     PAIR. It never touches a row, and `ABSENT`, `UNDERIVABLE` and
     `INCOMPARABLE` are three distinct states with three distinct counters. A
     tag that removes a row has become the thing this epic exists to prevent --
     this repository has already shipped a construct that erased a demonstrated
     kill with `verified: true, green: true, exit 0`.

  3. DERIVATION OVER DECLARATION, AND EVERYTHING UNRESOLVED FAILS OPEN. Only
     the DERIVED value refuses. `UNDERIVABLE` and `UNDEMONSTRATED` are the two
     ways the tag says nothing and they are always comparable. A derivation /
     declaration disagreement fails open and is reported as `TAG-DISPUTED`; it
     is never corrected and blocks nothing.

WHAT THIS IS NOT. It is not a gate. It refuses nothing about any artifact, no
close path consults it, and it neither proposes a boundary nor scores one. It
reads WHERE THE BOUNDARY ALREADY IS from figures `scripts/code_complexity.py`
already prints, and the epic charter's §6b ruling is what licenses that:
choosing a boundary is `CD-01`'s forbidden move, observing one is the
thermometer's entire job. `tests/test_code_complexity.py` states the invariant
in those terms and this file is scanned by it like any other -- it is NOT on
the exemption list, and `test_the_derivation_observes_and_never_refuses` pins
that it reads figures and refuses on none of them.

  python3 examples/validation/scorecards/architecture_tags.py derive
  python3 examples/validation/scorecards/architecture_tags.py table
  python3 examples/validation/scorecards/architecture_tags.py drift
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import tomllib

HERE = pathlib.Path(__file__).resolve()
REPO_ROOT = HERE.parents[3]
DEFAULT_SUBJECTS = HERE.parent / "subjects.toml"
DEFAULT_SCORECARD_ROOT = REPO_ROOT / "specs/results/scorecards"
COMPLEXITY = "scripts/code_complexity.py"

DIMS = ("D1", "D2", "D3", "D4", "D5")

#: The axis. ONE. `references/architecture_tags.md` §2 -- language, framework,
#: layering vocabulary, DI style, port count and test-suite architecture were
#: all rejected there for having zero demonstrated separations across 49 cards.
AXIS = "effect_boundary"

#: The two values that may refuse anything, and they are NOMINAL. Neither is
#: better than the other; nothing here sorts, sums or prefers one. The moment
#: one is better the tag is a target and `MF-020` applies -- a tag moving is not
#: evidence the design improved.
VALUES = ("effectful", "ports-and-adapters")

#: The two ways the tag says nothing. Saying nothing must never be worth more
#: than saying something, so both are ALWAYS COMPARABLE.
UNDERIVABLE = "UNDERIVABLE:"
UNDEMONSTRATED = "UNDEMONSTRATED:"

#: RD-04 §9.2, and it is printed rather than buried because RD-04 asked for
#: that in as many words. THIS NUMBER IS NOT MEASURED. The observed values are
#: 0.100-0.125 against 1.000 -- a chasm -- so any threshold in that interval
#: gives the same answer on every subject in the record, and NO ARTIFACT
#: ANYWHERE NEAR THE BOUNDARY HAS EVER BEEN MEASURED. Filed as `RD-04-DF-04`.
#: The first artifact that lands near it is the one that decides the clause.
STATE_COLOCATION_MAX = 0.5

#: The dimension whose citations SCOPE-DRIFT reads. D3 is the only dimension
#: the axis has authority on, so it is the only one where citing outside the
#: declared scope changes what a comparison means.
DRIFT_DIM = "D3"


# --------------------------------------------------------------------------
# the declared scopes
# --------------------------------------------------------------------------

def load_subjects(path: pathlib.Path | None = None) -> dict:
    """The declared subjects. Nothing here is computed -- see `subjects.toml`."""
    path = path or DEFAULT_SUBJECTS
    data = tomllib.loads(path.read_text())
    subjects = {}
    for name, entry in (data.get("subject") or {}).items():
        subjects[name] = {
            "name": name,
            "example": entry["example"],
            "scope": list(entry["scope"]),
            "declared": entry.get("declared_effect_boundary"),
            "labels": [tuple(x) for x in entry.get("labels", [])],
        }
    return subjects


# --------------------------------------------------------------------------
# 1. derivation -- the tag is COMPUTED, from figures already printed
# --------------------------------------------------------------------------

def measure(scope: list[str], root: pathlib.Path = REPO_ROOT) -> dict | None:
    """Run the SHIPPED complexity instrument over a declared scope.

    Nothing new is measured and no new instrument ships. `None` means the
    instrument could not report on this scope at all, which the caller turns
    into `UNDERIVABLE` -- a refusal to derive, never a fallback to a value.
    """
    args = [sys.executable, str(root / COMPLEXITY)]
    args += [str(root / p) for p in scope]
    args += ["--json"]
    proc = subprocess.run(args, capture_output=True, text=True, cwd=str(root))
    unreadable = proc.returncode != 0 or not proc.stdout.strip()
    if unreadable:
        return None
    return json.loads(proc.stdout)


def derive(record: dict) -> tuple[str, dict]:
    """The derivation predicate, over `role = code` modules of the scope.

    Returns `(value, facts)`. THIS FUNCTION PRODUCES A LABEL AND NOTHING ELSE.
    It has no exit path, raises nothing, asserts nothing and decides nothing
    about the tree it read -- see the module docstring on §6b.

    `ports-and-adapters` requires ALL THREE clauses, each one a figure the
    shipped instrument already prints:

      (a) a seam declared OFF the effect surface -- some code module declares an
          interface and makes no effectful call. A `Protocol` declared next to
          the file writer is the same coupling with an extra file.
      (b) the state does not live where the effects are -- the fraction of
          `instance_state` sitting in effectful modules is under
          `STATE_COLOCATION_MAX`.
      (c) a second implementation is PRESENT, not promised -- at least one
          effectful code module and at least one stateful, non-effectful,
          non-interface one. A port with one implementation has never been
          swapped and nobody knows whether it can be.

    Otherwise `effectful`. IMPORT TOPOLOGY IS DELIBERATELY NOT A CLAUSE:
    `ex5_pipeline_divergent` carries one declared interface and 18 internal
    import edges and was scored D3 = 1 by both blind judges, so it is the
    demonstrated failing input for `declared_interfaces >= 1` as a whole
    predicate.

    It also deliberately does NOT try to tell a FOLLOWED boundary from a
    declared-and-diverged one. That is what D3 anchors 1 and 2 score, and a tag
    that could make the distinction would be doing the dimension's job.
    """
    mods = [m for m in record.get("modules", []) if m.get("role") == "code"]
    facts: dict = {"state_colocation_max": STATE_COLOCATION_MAX}

    parsed = (record.get("completeness") or {}).get("parsed_fraction")
    facts["parsed_fraction"] = parsed
    incomplete = parsed is not None and parsed < 1.0
    if incomplete:
        # Every non-Python subject lands here too: the walk is a Python AST
        # walk and everything else is unparsed. RD-04 §9.5, untested against
        # any other language, and the right default -- an unparsed subject is
        # comparable to everything.
        facts["note"] = "not every module in the declared scope parsed"
        return UNDERIVABLE + "unparsed", facts

    eff = [m for m in mods if m.get("effectful_calls", 0) > 0]
    ifaces = [m for m in mods if m.get("declared_interfaces", 0) > 0]
    total_state = sum(m.get("instance_state", 0) for m in mods)
    state_in_eff = sum(m.get("instance_state", 0) for m in eff)

    facts["code_modules"] = len(mods)
    facts["modules_with_effectful_calls"] = len(eff)
    facts["declared_interfaces"] = sum(m.get("declared_interfaces", 0) for m in mods)
    facts["instance_state"] = total_state
    facts["instance_state_in_effectful_modules"] = state_in_eff
    facts["state_colocation"] = (
        None if total_state == 0 else round(state_in_eff / total_state, 3))
    facts["iface_modules_with_no_effects"] = sorted(
        m["path"] for m in ifaces if m.get("effectful_calls", 0) == 0)

    if not eff:
        # No outside world is touched anywhere in the code role, so D3's
        # anchor 3 has no referent here and NEITHER value can be asserted.
        # This is the `pure` candidate; it is returned as a refusal to derive
        # rather than as a third value, because nothing in the record
        # demonstrates it changes a score (RD-04 §9.3, n = 1 in two of three
        # cells). Reported as a refusal, never as `effectful`.
        return UNDERIVABLE + "no-effect-surface", facts

    clause_a = bool(facts["iface_modules_with_no_effects"])
    coloc = facts["state_colocation"]
    clause_b = coloc is not None and coloc < STATE_COLOCATION_MAX
    second_impl = [m for m in mods
                   if m.get("effectful_calls", 0) == 0
                   and m.get("instance_state", 0) > 0
                   and m.get("declared_interfaces", 0) == 0]
    clause_c = bool(second_impl)
    facts["clause_a_seam_declared_off_the_effect_surface"] = clause_a
    facts["clause_b_state_not_colocated_with_effects"] = clause_b
    facts["clause_c_second_implementation_present"] = clause_c

    ported = clause_a and clause_b and clause_c
    return ("ports-and-adapters" if ported else "effectful"), facts


def has_authority(value: str | None) -> bool:
    """Can this value ever refuse anything? Only the two demonstrated ones."""
    return value in VALUES


def agreement_of(derived: str, declared: str | None) -> str:
    """`agree`, `TAG-DISPUTED`, or `UNDERIVABLE`. All three FAIL OPEN.

    THE DERIVED VALUE ALWAYS WINS AND A REFUSAL TO DERIVE ALWAYS FAILS OPEN.
    An author who has seen the numbers can edit a declaration; they cannot edit
    `instance_state_in_effectful_modules` without moving the state out of the
    effectful module, which is the work D3 measures. `TAG-DISPUTED` is never
    corrected and never blocks anything -- it is a prompt to go and look.
    """
    undecided = not has_authority(derived)
    if undecided:
        return "UNDERIVABLE"
    if declared == derived:
        return "agree"
    return "TAG-DISPUTED"


def derive_subjects(subjects: dict, root: pathlib.Path = REPO_ROOT) -> dict:
    """Derive every declared subject. Re-run from the tree, never cached."""
    out = {}
    for name, s in sorted(subjects.items()):
        record = measure(s["scope"], root)
        missing = record is None
        if missing:
            out[name] = {"subject": name, "example": s["example"],
                         "derived": UNDERIVABLE + "unmeasurable",
                         "declared": s["declared"], "agreement": "UNDERIVABLE",
                         "facts": {"note": "the instrument could not report on this scope"}}
            continue
        value, facts = derive(record)
        out[name] = {"subject": name, "example": s["example"], "derived": value,
                     "declared": s["declared"],
                     "agreement": agreement_of(value, s["declared"]), "facts": facts}
    return out


# --------------------------------------------------------------------------
# 2. the cards
# --------------------------------------------------------------------------

def card_rows(scorecard_root: pathlib.Path = DEFAULT_SCORECARD_ROOT) -> list[dict]:
    rows = []
    for path in sorted(scorecard_root.glob("*/*/*/scorecard.json")):
        card = json.loads(path.read_text())
        parts = path.relative_to(scorecard_root).parts
        model = str((card.get("judge") or {}).get("model") or "")
        tier = "opus" if "opus" in model else ("sonnet" if "sonnet" in model else "?")
        rows.append({
            "path": path,
            "round": parts[0],
            "example": parts[1],
            "run": parts[2],
            "key": f"{parts[0]}/{parts[1]}/{parts[2]}",
            "arm": card.get("arm"),
            "tier": (card.get("judge") or {}).get("tier") or tier,
            "scores": {d: (card.get("dimensions") or {}).get(d, {}).get("score")
                       for d in DIMS},
            "citations": {d: list((card.get("dimensions") or {}).get(d, {}).get(
                "citations") or []) for d in DIMS},
            "declared_subject": (card.get("subject") or {}).get("name"),
            "status": card.get("status", "filled"),
        })
    return rows


def subject_of(row: dict, subjects: dict) -> str | None:
    """Which declared subject did this card score?

    A card written from RD-05 onward says so itself. For every card sealed
    before that, the mapping is the `labels` list in `subjects.toml` -- a
    sealed card is never edited, so the attribution lives beside them.
    """
    named = row.get("declared_subject")
    if named in subjects:
        return named
    for name, s in subjects.items():
        if s["example"] != row["example"]:
            continue
        for round_dir, arm in s["labels"]:
            if row["round"] == round_dir and (arm == "" or row["arm"] == arm):
                return name
    return None


# --------------------------------------------------------------------------
# 3. the demonstration table -- how a value earns its place
# --------------------------------------------------------------------------
#
# EARN-ITS-PLACE IS A DELETION RULE, NOT A PROMOTION RULE, and RD-04 §7.2 is
# emphatic about it. As a deletion rule it is correct and cheap: a value with
# no separation anywhere in the record cannot be doing comparability work,
# whatever the argument for it. As a promotion rule it establishes CORRELATION
# and calls it authority -- nothing forces the separation to be CAUSED by the
# value, so a value that passes is ADMITTED, NOT PROVEN, and carries its
# confounds forward on its row.
#
# Three things it cannot see, all three real in this record: it cannot detect a
# CEILING (a value that changes a reachable maximum without changing an
# observed score), it cannot see a value occurring in ONE example, and a `does
# not separate` verdict can be ENTAILED rather than measured. The third is
# computed below and printed beside every such verdict.

def _ranges(rows: list[dict], subj_tag: dict, subjects: dict,
            example: str, dim: str, tag: str, tier: str | None = None) -> list[int]:
    out = []
    for r in rows:
        if r["example"] != example or r["status"] == "unfilled":
            continue
        if tier is not None and r["tier"] != tier:
            continue
        name = subject_of(r, subjects)
        if name is None or subj_tag.get(name, {}).get("derived") != tag:
            continue
        score = r["scores"].get(dim)
        if isinstance(score, int):
            out.append(score)
    return sorted(out)


def demonstration_table(rows: list[dict], derived: dict, subjects: dict) -> list[dict]:
    """Re-derive, from the cards, which `(dimension, value-pair)` separates.

    A pair separates on a dimension only if two subjects OF THE SAME EXAMPLE
    carrying those two values score in DISJOINT ranges on it. Within one
    example because `R-H2` forbids comparing across examples and a taxonomy is
    not exempt from the reading rules it serves.

    Every entry -- separating or not -- carries the population's observed range
    and a `null_entailed` flag. RD-04's rule, carried here: a `does not
    separate` verdict on a dimension that took ONE value across the whole
    population reports the EXAMPLE, not the tag, and a null result that could
    not have come out otherwise is not a null result.
    """
    examples = sorted({r["example"] for r in rows})
    entries: list[dict] = []
    for example in examples:
        present = sorted({derived[n]["derived"]
                          for r in rows
                          for n in [subject_of(r, subjects)]
                          if n is not None and n in derived
                          and r["example"] == example and r["status"] != "unfilled"})
        authoritative = [v for v in present if has_authority(v)]
        for i, tag_a in enumerate(authoritative):
            for tag_b in authoritative[i + 1:]:
                for dim in DIMS:
                    a = _ranges(rows, derived, subjects, example, dim, tag_a)
                    b = _ranges(rows, derived, subjects, example, dim, tag_b)
                    thin = not a or not b
                    if thin:
                        continue
                    separates = max(a) < min(b) or max(b) < min(a)
                    # THE POPULATION IS THE COMPARISON'S OWN POPULATION -- the
                    # cards that map to a subject of this example. A card
                    # outside the comparison cannot make a separation possible
                    # inside it, so counting one would turn an entailed null
                    # into a "measured" one, which is the exact error this
                    # column exists to catch.
                    population = sorted({r["scores"][dim] for r in rows
                                         if r["example"] == example
                                         and subject_of(r, subjects) is not None
                                         and isinstance(r["scores"].get(dim), int)})
                    tiers = []
                    for tier in ("opus", "sonnet"):
                        ta = _ranges(rows, derived, subjects, example, dim, tag_a, tier)
                        tb = _ranges(rows, derived, subjects, example, dim, tag_b, tier)
                        measured = bool(ta) and bool(tb)
                        if measured:
                            tiers.append(tier)
                    entries.append({
                        "id": f"{AXIS}-{example}-{dim}-{tag_a}-vs-{tag_b}",
                        "axis": AXIS,
                        "example": example,
                        "dimension": dim,
                        "values": [tag_a, tag_b],
                        "separates": separates,
                        "ranges": {tag_a: [min(a), max(a)], tag_b: [min(b), max(b)]},
                        "n": {tag_a: len(a), tag_b: len(b)},
                        "population_values": population,
                        "null_entailed": (not separates) and len(population) < 2,
                        "tiers_measured": tiers,
                    })
    return entries


def authority(entries: list[dict]) -> dict[tuple[str, frozenset], dict]:
    """`(dimension, {value, value})` -> the entry that grants the refusal.

    ONLY separating entries appear. A4 -- spread the earned refusal across the
    other four dimensions -- is defeated here and nowhere else: the key carries
    the dimension, so a separation on D3 grants nothing on D1.
    """
    out = {}
    for e in entries:
        if e["separates"]:
            out[(e["dimension"], frozenset(e["values"]))] = e
    return out


def same_tag_controls(rows: list[dict], derived: dict, subjects: dict) -> list[dict]:
    """The control the bare earn-its-place rule does not state and needs.

    Two subjects of the same example carrying the SAME derived value must NOT
    separate on the dimension claimed. Without it, a separation between any two
    artifacts counts -- and any two artifacts differ in something.
    """
    by_subject: dict[str, dict[str, list[int]]] = {}
    for r in rows:
        name = subject_of(r, subjects)
        if name is None or r["status"] == "unfilled":
            continue
        s = by_subject.setdefault(name, {})
        for d in DIMS:
            if isinstance(r["scores"].get(d), int):
                s.setdefault(d, []).append(r["scores"][d])
    out = []
    names = sorted(by_subject)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            unrelated = (subjects[a]["example"] != subjects[b]["example"]
                         or derived[a]["derived"] != derived[b]["derived"]
                         or not has_authority(derived[a]["derived"]))
            if unrelated:
                continue
            for d in DIMS:
                sa, sb = sorted(by_subject[a].get(d, [])), sorted(by_subject[b].get(d, []))
                if not sa or not sb:
                    continue
                separates = max(sa) < min(sb) or max(sb) < min(sa)
                out.append({"example": subjects[a]["example"], "a": a, "b": b,
                            "value": derived[a]["derived"], "dimension": d,
                            "ranges": {a: [min(sa), max(sa)], b: [min(sb), max(sb)]},
                            "separates": separates,
                            "verdict": "control FAILS" if separates else "control holds"})
    return out


# --------------------------------------------------------------------------
# 4. comparability -- and the printing rule that keeps it honest
# --------------------------------------------------------------------------

COMPARABLE = "comparable"
INCOMPARABLE = "INCOMPARABLE"
ABSENT = "ABSENT"


def verdict(dim: str, tag_a: str, tag_b: str,
            table: dict[tuple[str, frozenset], dict]) -> tuple[str, str]:
    """`(state, reason)` for one dimension of one pair of subjects.

    FOUR STATES, FOUR COUNTERS, ONE PRINTING RULE, and the printing rule is
    the invariant: BOTH SCORE SETS ARE PRINTED IN EVERY STATE. The verdict
    annotates the pair; it never touches a row. `ABSENT`, `UNDERIVABLE` and
    `INCOMPARABLE` are distinct because a missing row and an incomparable one
    are not the same claim.
    """
    for tag in (tag_a, tag_b):
        if not has_authority(tag):
            why = "UNDERIVABLE" if tag.startswith(UNDERIVABLE) else "UNDEMONSTRATED"
            return COMPARABLE, (f"{why} on one side ({tag}) -- a tag that could not be "
                                f"derived says nothing, and saying nothing may not buy "
                                f"more than saying something")
    if tag_a == tag_b:
        return COMPARABLE, f"same derived {AXIS} ({tag_a})"
    entry = table.get((dim, frozenset((tag_a, tag_b))))
    if entry is None:
        return COMPARABLE, (f"{tag_a}/{tag_b} has demonstrated no separation on {dim}, so "
                            f"a 'different architecture' objection is not available here")
    return INCOMPARABLE, (f"{AXIS}: {tag_a}/{tag_b}, demonstrated on {dim}, table row "
                          f"`{entry['id']}`, tiers measured {entry['tiers_measured']}")


def compare(rows: list[dict], derived: dict, subjects: dict, example: str,
            subject_a: str, subject_b: str,
            table: dict[tuple[str, frozenset], dict]) -> list[dict]:
    """Every dimension of one pair. Both score sets on every row, always."""
    out = []
    tag_a = derived[subject_a]["derived"]
    tag_b = derived[subject_b]["derived"]
    for dim in DIMS:
        a = sorted(r["scores"][dim] for r in rows
                   if subject_of(r, subjects) == subject_a
                   and isinstance(r["scores"].get(dim), int))
        b = sorted(r["scores"][dim] for r in rows
                   if subject_of(r, subjects) == subject_b
                   and isinstance(r["scores"].get(dim), int))
        if not a and not b:
            out.append({"dimension": dim, "scores_a": [], "scores_b": [],
                        "state": ABSENT, "reason": "no card exists on either side"})
            continue
        state, reason = verdict(dim, tag_a, tag_b, table)
        if not a or not b:
            state, reason = ABSENT, "no card exists on one side; counted, never dropped"
        out.append({"dimension": dim, "scores_a": a, "scores_b": b,
                    "state": state, "reason": reason})
    return out


# --------------------------------------------------------------------------
# 5. SCOPE-DRIFT -- attack A5, computed from sealed cards
# --------------------------------------------------------------------------

def scope_drift(rows: list[dict], subjects: dict) -> list[dict]:
    """Cards whose D3 citations fall predominantly OUTSIDE their declared scope.

    Not hypothetical: it is what produced `toolchain_removal` D3 = 4 on a card
    whose every citation is to a fixture. A scope change is not an architecture
    change and must never be read as one.

    Attribution is mechanical -- count how many of the card's own D3 citations
    name each declared scope OF THE SAME EXAMPLE, and report the card when the
    winner is not the subject it was attributed to. No card is edited and no
    judging is redone.

    KNOWN LIMIT, stated rather than discovered later. The count is over the
    scope's LAST PATH SEGMENT, because a judge writes `after/scripts/x.py:9`
    and `<TREES>/after/scripts/x.py:9` for the same file and neither is rooted
    at the repository. Two declared scopes sharing a basename would therefore
    collide, and a citation to `skill-scripts/` counts toward `scripts/`. It is
    RD-04's own method, reproduced so its §4.2 decomposition re-derives here.
    """
    out = []
    for r in rows:
        name = subject_of(r, subjects)
        if name is None or r["status"] == "unfilled":
            continue
        cites = " ".join(str(c) for c in (r["citations"].get(DRIFT_DIM) or []))
        siblings = {n: s for n, s in subjects.items() if s["example"] == r["example"]}
        counts = {}
        for other, s in siblings.items():
            counts[other] = sum(cites.count(p.rstrip("/").split("/")[-1] + "/")
                                for p in s["scope"])
        located = any(counts.values())
        if not located:
            continue
        best = max(counts, key=lambda k: (counts[k], k == name))
        drifted = best != name
        if drifted:
            out.append({"card": r["key"], "arm": r["arm"], "tier": r["tier"],
                        "declared_subject": name, "cited_subject": best,
                        "dimension": DRIFT_DIM, "score": r["scores"].get(DRIFT_DIM),
                        "citation_counts": counts,
                        "verdict": "SCOPE-DRIFT"})
    return out


# --------------------------------------------------------------------------
# CLI. Every command prints; none of them refuses anything.
# --------------------------------------------------------------------------

def _load_all(root: pathlib.Path, scorecards: pathlib.Path):
    subjects = load_subjects()
    derived = derive_subjects(subjects, root)
    rows = card_rows(scorecards)
    return subjects, derived, rows


def render_derive(subjects: dict, derived: dict) -> str:
    out = [f"# {AXIS} -- derived over {len(subjects)} declared scope(s)",
           f"# state_colocation threshold = {STATE_COLOCATION_MAX} "
           f"(RD-04 §9.2: CHOSEN, NOT MEASURED -- `RD-04-DF-04`)", ""]
    decided = 0
    for name in sorted(derived):
        d = derived[name]
        f = d["facts"]
        decided += 1 if has_authority(d["derived"]) else 0
        out.append(f"{name:24s} derived={d['derived']:34s} declared={str(d['declared']):20s}"
                   f" {d['agreement']}")
        out.append(f"{'':24s}   iface={f.get('declared_interfaces')} "
                   f"eff_mods={f.get('modules_with_effectful_calls')}/{f.get('code_modules')} "
                   f"state_coloc={f.get('state_colocation')}")
    out.append("")
    out.append(f"{decided} of {len(derived)} subject(s) decided; "
               f"{len(derived) - decided} refused. A refusal is REPORTED as a refusal and "
               f"is comparable to everything.")
    return "\n".join(out)


def render_table(entries: list[dict], controls: list[dict]) -> str:
    out = ["# demonstration table -- re-derived from the cards, never declared", ""]
    out.append("Refusal authority is keyed on (dimension, value-pair). A separation on one")
    out.append("dimension grants NOTHING on the other four.")
    out.append("")
    for e in entries:
        pair = "/".join(e["values"])
        rng = "  ".join(f"{v} {e['ranges'][v]} n={e['n'][v]}" for v in e["values"])
        if e["separates"]:
            out.append(f"  SEPARATES        {e['example']} {e['dimension']} {pair}: {rng}"
                       f"  tiers_measured={e['tiers_measured']}")
        else:
            mark = "  NULL-ENTAILED" if e["null_entailed"] else ""
            out.append(f"  does not separate {e['example']} {e['dimension']} {pair}: {rng}"
                       f"  population took {e['population_values']}{mark}")
    granted = [e for e in entries if e["separates"]]
    out.append("")
    out.append(f"{len(granted)} of {len(entries)} (dimension, value-pair) cell(s) grant a "
               f"refusal.")
    out.append("")
    out.append("## same-tag control -- two subjects, same example, SAME derived value")
    for c in controls:
        out.append(f"  {c['verdict']:14s} {c['example']} {c['dimension']} {c['a']}/{c['b']} "
                   f"({c['value']}): {c['ranges'][c['a']]} vs {c['ranges'][c['b']]}")
    if not controls:
        out.append("  none available -- no example has two subjects of the same value")
    return "\n".join(out)


def render_drift(drifts: list[dict], rows: int) -> str:
    out = [f"# SCOPE-DRIFT over {rows} card(s) -- attack A5, computed", ""]
    for d in drifts:
        out.append(f"  SCOPE-DRIFT  {d['card']} (arm {d['arm']}, {d['tier']}) "
                   f"{d['dimension']} = {d['score']}")
        out.append(f"               attributed to `{d['declared_subject']}`, its own "
                   f"{d['dimension']} citations name `{d['cited_subject']}` "
                   f"{d['citation_counts']}")
    if not drifts:
        out.append("  none")
    out.append("")
    out.append(f"{len(drifts)} card(s) cite predominantly outside their declared scope. "
               f"A scope change is not an architecture change.")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="architecture_tags.py", description=__doc__)
    ap.add_argument("command", choices=["derive", "table", "drift", "compare", "json"])
    ap.add_argument("--root", default=str(REPO_ROOT))
    ap.add_argument("--scorecards", default=str(DEFAULT_SCORECARD_ROOT))
    ap.add_argument("--example", default=None)
    ap.add_argument("--subjects", nargs=2, default=None, metavar=("A", "B"))
    args = ap.parse_args(argv)

    root = pathlib.Path(args.root)
    subjects, derived, rows = _load_all(root, pathlib.Path(args.scorecards))

    if args.command == "derive":
        print(render_derive(subjects, derived))
        return 0
    entries = demonstration_table(rows, derived, subjects)
    if args.command == "table":
        print(render_table(entries, same_tag_controls(rows, derived, subjects)))
        return 0
    if args.command == "drift":
        print(render_drift(scope_drift(rows, subjects), len(rows)))
        return 0
    if args.command == "compare":
        a, b = args.subjects
        example = args.example or subjects[a]["example"]
        table = authority(entries)
        for line in compare(rows, derived, subjects, example, a, b, table):
            print(f"{line['dimension']}  {a} {line['scores_a']}   {b} {line['scores_b']}"
                  f"   {line['state']} ({line['reason']})")
        return 0
    print(json.dumps({"derived": derived, "table": entries,
                      "controls": same_tag_controls(rows, derived, subjects),
                      "scope_drift": scope_drift(rows, subjects)},
                     indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
