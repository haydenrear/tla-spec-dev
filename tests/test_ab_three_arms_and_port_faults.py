"""PA-01: the third arm, the port-aware catalogue, and the sealed predictions.

Every declaration this ticket adds ships with something that checks it against
behaviour, **using the shipped builders**, so a rename fails a test instead of
silently orphaning the declaration. The plan's `declaration_executability_rule`
exists because five declaration/behaviour mismatches were shipped in five
consecutive attempts by three authors, in both directions, and because a test
written for that very class passed vacuously by reading the wrong key.

So this file imports `examples/validation/ab/check_catalogue.py` and uses ITS
constants and ITS functions rather than restating them. Nothing here is a gate:
the epic's `no_new_gates_rule` bans a new blocking check in the product, and
these are tests of a fixture.

Three declarations are under test.

1. **Three arms exist, and arm C is length-matched to arm B in unique content
   while asking for nothing architectural.** The measure is the shipped one --
   the same one that produced the predecessor's sealed "6.6x longer" -- so a
   number here is comparable with that record rather than merely similar.

2. **The catalogue seeds at least two faults INSIDE an adapter
   implementation,** on both sides of one port, each occurring exactly once and
   applying/reverting byte-identically.

3. **A composition point actually wires the fake.** This is the one that would
   have caught `BA-B14`. An adapter with nothing pointing at it is verified by
   nothing, and a catalogue row seeded into it measures nothing.
"""

from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
AB = REPO_ROOT / "examples" / "validation" / "ab"
PREDICTIONS = REPO_ROOT / "examples" / "validation" / "PREDICTIONS-PA.md"


def _load_check_catalogue():
    """Import the SHIPPED harness. Not a copy of it -- a rename must fail."""
    spec = importlib.util.spec_from_file_location(
        "_ab_check_catalogue", AB / "check_catalogue.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


cc = _load_check_catalogue()


@pytest.fixture(scope="module")
def rows() -> list[dict]:
    _, raw_rows, _ = cc.load_catalogue(AB / "seeded_faults.toml")
    return raw_rows


# -- 1. the three arms -----------------------------------------------------


def test_three_arms_exist_as_three_prompt_files():
    for arm in cc.ARMS:
        assert cc.arm_prompt(arm).is_file(), f"{arm} has no PROMPT.md"
    assert len(cc.ARMS) == 3


def test_no_arm_is_another_arm_with_a_section_removed():
    """Independent prompts, not one prompt with the treatment switched off."""
    lines = {arm: cc.distinct_lines(cc.arm_prompt(arm)) for arm in cc.ARMS}
    for one in cc.ARMS:
        for other in cc.ARMS:
            if one != other:
                assert not lines[one] <= lines[other], (
                    f"{one} is a strict subset of {other}"
                )


def test_arm_c_is_length_matched_to_arm_b_in_unique_content():
    """Measured against arm A, the arm both long arms are long RELATIVE TO."""
    control = cc.arm_prompt("arm_a")
    b_unique = len(cc.unique_content(cc.arm_prompt("arm_b"), control))
    c_unique = len(cc.unique_content(cc.arm_prompt("arm_c"), control))

    # The confound arm C exists to settle, re-derived rather than quoted: the
    # predecessor's sealed number is "arm B is 6.6x arm A in unique content".
    a_unique = len(cc.unique_content(control, cc.arm_prompt("arm_b")))
    assert b_unique / a_unique > 6, (
        "arm B is no longer 6.6x arm A; the confound arm C controls for has "
        "changed and the match below is matching the wrong thing"
    )

    ratio = c_unique / b_unique
    assert abs(ratio - 1) <= cc.LENGTH_MATCH_TOLERANCE, (
        f"arm C unique content is {c_unique} lines against arm B's {b_unique} "
        f"({ratio:.3f}x), outside +/-{cc.LENGTH_MATCH_TOLERANCE:.0%}. A control "
        f"that is not length-matched cannot separate 'hexagonal helped' from "
        f"'a longer ask helped'."
    )


def test_arm_c_asks_for_nothing_architectural():
    control = cc.arm_prompt("arm_a")
    hits = cc.architectural_hits(cc.unique_content(cc.arm_prompt("arm_c"), control))
    assert hits == [], (
        "arm C's unique content asks for structure: "
        + "; ".join(f"[{word}] {line}" for word, line in hits)
    )


def test_the_vocabulary_probe_is_not_vacuous():
    """The lesson of the test that passed by reading the wrong key.

    A probe that finds nothing anywhere proves nothing about arm C. Arm B is
    the positive control for the probe itself: it is the arm that unarguably
    does ask for structure, so the probe must fire on it.
    """
    control = cc.arm_prompt("arm_a")
    b_hits = cc.architectural_hits(cc.unique_content(cc.arm_prompt("arm_b"), control))
    assert len(b_hits) >= 10, (
        f"the architectural vocabulary probe found only {len(b_hits)} line(s) in "
        f"arm B's unique content. Arm B is the hexagonal ask; a probe blind to it "
        f"says nothing about arm C's zero."
    )


def test_arm_c_carries_its_slot_markers():
    body = cc.arm_prompt("arm_c").read_text(encoding="utf-8")
    assert "PA-01-SLOT:BEGIN" in body and "PA-01-SLOT:END" in body


def test_arms_a_and_b_are_not_edited_by_this_ticket():
    """Comparability across the epic boundary is a property of the BYTES.

    The predecessor's reading rule: a row is comparable only on the same
    example AND across an unchanged instrument. These two prompts produced the
    sealed HP numbers, so PA-01 leaves them alone and records the cost
    (PA-01-DF-02) rather than fixing it mid-comparison.
    """
    for arm, marker in (("arm_a", "control arm"), ("arm_b", "HP-02-SLOT:BEGIN")):
        assert marker in cc.arm_prompt(arm).read_text(encoding="utf-8")
    # The stale text is DECLARED. If somebody quietly repairs it, this fails and
    # the instrument change gets named instead of slipping through.
    assert "two-arm comparison" in cc.arm_prompt("arm_b").read_text(encoding="utf-8")
    assert "PA-01-DF-02" in PREDICTIONS.read_text(encoding="utf-8")


# -- 2. the port-aware catalogue -------------------------------------------


def test_the_catalogue_seeds_faults_inside_an_adapter_implementation(rows):
    claimed = cc.adapter_internal_rows(rows)
    assert len(claimed) >= cc.MIN_ADAPTER_INTERNAL, (
        f"{len(claimed)} adapter-internal mutant(s); at least "
        f"{cc.MIN_ADAPTER_INTERNAL} required"
    )
    for row in claimed:
        assert row["path"] in cc.ADAPTER_IMPLEMENTATIONS, (
            f"{row['id']} claims adapter_internal but sits at {row['path']}"
        )


def test_the_adapter_internal_pair_straddles_the_port(rows):
    """One semantic, both sides. The DIFFERENCE between the rows is the finding.

    A catalogue with every adapter-internal row on one side of the port
    measures how hard a fault is, not how large the unreached region is.
    """
    sides = {row["path"] for row in cc.adapter_internal_rows(rows)}
    assert len(sides) >= 2, f"all adapter-internal mutants sit in {sides}"


def test_every_declared_adapter_implementation_exists(rows):
    """A rename fails HERE, rather than orphaning the declaration silently."""
    for adapter in cc.ADAPTER_IMPLEMENTATIONS:
        assert (AB / adapter).is_file(), f"declared adapter {adapter} does not exist"
    seeded = {row["path"] for row in cc.adapter_internal_rows(rows)}
    assert seeded <= set(cc.ADAPTER_IMPLEMENTATIONS)


def test_a_row_in_an_adapter_must_declare_the_adapter_class(rows):
    """The other direction, which is the one that under-counts a class row."""
    for row in rows:
        if row.get("path") in cc.ADAPTER_IMPLEMENTATIONS:
            assert row.get("fault_class") == "adapter_internal", (
                f"{row['id']} is seeded in an adapter but declares "
                f"{row.get('fault_class')!r}"
            )


def test_every_adapter_internal_mutant_occurs_exactly_once_and_reverts(rows, tmp_path):
    """The load-bearing catalogue property, re-asserted for the new rows.

    A pattern occurring twice seeds two faults and reports them as one; a
    pattern occurring zero times seeds nothing and reports a survivor.
    """
    for row in cc.adapter_internal_rows(rows) + [
        r for r in rows if str(r.get("control_role", "")).startswith("positive")
    ]:
        target = AB / row["path"]
        original = target.read_text(encoding="utf-8")
        assert original.count(row["find"]) == 1, (
            f"{row['id']}: `find` occurs {original.count(row['find'])} time(s)"
        )
        patched = original.replace(row["find"], row["replace"], 1)
        assert patched != original
        scratch = tmp_path / Path(row["path"]).name
        scratch.write_text(patched, encoding="utf-8")
        scratch.write_text(original, encoding="utf-8")
        assert scratch.read_text(encoding="utf-8") == original
        assert target.read_text(encoding="utf-8") == original, (
            f"{row['id']}: the fixture was not left byte-identical"
        )


def test_the_ports_tree_has_its_own_positive_control(rows):
    """Otherwise a column of survivors is indistinguishable from a dead column.

    FI-01 changed "exactly one per tree" to "at least one per tree", and the
    strength moved rather than left: what a tree needs is a control that CAN GO
    RED, which `tests/test_falsifiable_controls.py` asserts by probing. One
    broken control satisfied "exactly one" and that is the state PA-06-DF-07
    found. `reference_ports` now carries two -- `PA-M14`, kept in the record
    with its INERT verdict, and `FI-M15`, which holds -- because deleting a
    broken control to keep a count at one is how a measured defect disappears.
    """
    trees: dict[str, int] = {}
    for row in rows:
        tree = str(row.get("path", "")).split("/")[0]
        trees.setdefault(tree, 0)
        if str(row.get("control_role", "")).startswith("positive"):
            trees[tree] += 1
    assert len(trees) >= 2, (
        f"only {len(trees)} anchor tree(s): {sorted(trees)}. A single flat tree "
        f"contains no adapter, so the adapter-internal class cannot be expressed "
        f"in it and a zero for that class would say nothing."
    )
    for tree, count in trees.items():
        assert count >= 1, f"anchor tree {tree!r} has {count} positive control(s)"


def test_the_catalogue_declares_what_is_not_seeded():
    """"Not seeded" and "not caught" are different results and must stay so."""
    text = (AB / "seeded_faults.toml").read_text(encoding="utf-8")
    assert "CLASSES DELIBERATELY NOT SEEDED" in text
    for omission in ("CONCURRENCY", "CROSS-PROCESS", "COMPOSITION POINT",
                     "EQUIVALENT MUTANT"):
        assert omission in text, f"{omission} omission is not declared with a reason"


# -- 3. a composition point actually wires the fake ------------------------


PORTS = AB / "reference_ports"


def _load_wiring(module_name: str):
    """Import a composition point from the ports tree, in process."""
    saved_path = list(sys.path)
    saved_modules = {
        name: sys.modules[name]
        for name in ("domain", "journal_file", "journal_memory",
                     "quota_ledger", "quota_ledger_fake")
        if name in sys.modules
    }
    for name in saved_modules:
        del sys.modules[name]
    sys.path.insert(0, str(PORTS))
    try:
        spec = importlib.util.spec_from_file_location(
            module_name, PORTS / f"{module_name}.py"
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = saved_path
        for name in list(sys.modules):
            if name in ("domain", "journal_file", "journal_memory",
                        "quota_ledger", "quota_ledger_fake"):
                del sys.modules[name]
        sys.modules.update(saved_modules)


def _observable(ledger, quotas):
    return (
        {t: ledger.available(t) for t in quotas},
        {t: ledger.committed(t) for t in quotas},
        {t: ledger.is_closed(t) for t in quotas},
        list(ledger.outstanding_ids()),
        list(ledger.ledger_lines()),
    )


def _drive(ledger):
    """A scripted sequence touching every command and both ledger line kinds."""
    first = ledger.reserve("acme", 3).reservation_id
    second = ledger.reserve("acme", 2).reservation_id
    third = ledger.reserve("globex", 1).reservation_id
    ledger.commit(first)
    ledger.release(second)
    ledger.commit(third)
    ledger.close_tenant("globex")
    return ledger


def test_a_composition_point_wires_the_fake(tmp_path):
    """The four lines nobody wrote for a whole epic.

    `BA-B14`: a fault in the treatment arm's in-memory adapter survived every
    instrument, because no composition point pointed at it and therefore
    nothing executed a line of it. This asserts that such a composition point
    exists and works -- not that it is documented.
    """
    fake = _load_wiring("quota_ledger_fake")
    ledger = _drive(fake.QuotaLedger({"acme": 10, "globex": 4}, tmp_path / "unused.txt"))
    assert ledger.ledger_lines() == ["COMMIT acme 3 3", "COMMIT globex 1 1", "CLOSE globex 1"]
    # The path is accepted and unused: durability is the object's lifetime.
    assert not (tmp_path / "unused.txt").exists()


def test_both_wirings_of_one_domain_agree_on_the_feature(tmp_path):
    """The fake is a working implementation of the port, not a recorder.

    Note what this does NOT do: it does not stand in for the shared suite. Two
    wirings of one domain agree with each other even when the domain is wrong,
    so agreement is necessary and worth nothing on its own. The suite asserts
    EXPECTED VALUES against both wirings; that is the instrument. This test
    only establishes that the fake is substitutable at all.
    """
    quotas = {"acme": 10, "globex": 4}
    real = _load_wiring("quota_ledger")
    fake = _load_wiring("quota_ledger_fake")
    real_obs = _observable(_drive(real.QuotaLedger(dict(quotas), tmp_path / "l.txt")), quotas)
    fake_obs = _observable(_drive(fake.QuotaLedger(dict(quotas), tmp_path / "u.txt")), quotas)
    assert real_obs == fake_obs


def test_the_domain_imports_neither_adapter():
    """The port is structural or it is a folder.

    Read from the source rather than trusted from a docstring: if the domain
    imports a concrete adapter, the fake is not swappable and every row seeded
    behind the port is measuring something else.
    """
    domain = (PORTS / "domain.py").read_text(encoding="utf-8")
    for adapter in ("journal_file", "journal_memory"):
        assert f"import {adapter}" not in domain, (
            f"domain.py imports {adapter}; the port is not structural"
        )


def test_each_adapter_is_wired_by_exactly_one_composition_point():
    """Every declared adapter is REACHED, and the wiring is not duplicated."""
    wirings = {"quota_ledger": "journal_file", "quota_ledger_fake": "journal_memory"}
    for module, adapter in wirings.items():
        source = (PORTS / f"{module}.py").read_text(encoding="utf-8")
        assert f"from {adapter} import" in source, (
            f"{module}.py does not wire {adapter}; a declared adapter with no "
            f"composition point is verified by nothing -- BA-B14 exactly"
        )
        other = next(a for m, a in wirings.items() if m != module)
        assert f"from {other} import" not in source


def test_a_fault_seeded_in_the_fake_is_reachable_only_through_the_fake(rows, tmp_path):
    """PA-M12, applied in memory. The measurement, not a description of it.

    This is the whole PA-01 claim executed: the SAME fault, in the fake, is
    invisible to a reader driving the real wiring and plainly visible to the
    identical sequence driving the fake one. If the two columns ever agree, the
    catalogue's adapter-internal rows have stopped measuring the region they
    were seeded into and PA-06 must be told before it reports kills.
    """
    row = next(r for r in rows if r["id"].startswith("PA-M12"))
    target = PORTS / Path(row["path"]).name
    original = target.read_text(encoding="utf-8")
    assert original.count(row["find"]) == 1
    quotas = {"acme": 10, "globex": 4}
    try:
        target.write_text(original.replace(row["find"], row["replace"], 1), encoding="utf-8")
        real = _load_wiring("quota_ledger")
        fake = _load_wiring("quota_ledger_fake")
        real_lines = _drive(real.QuotaLedger(dict(quotas), tmp_path / "l.txt")).ledger_lines()
        fake_lines = _drive(fake.QuotaLedger(dict(quotas), tmp_path / "u.txt")).ledger_lines()
    finally:
        target.write_text(original, encoding="utf-8")
    assert target.read_text(encoding="utf-8") == original
    assert any(line.startswith("CLOSE") for line in real_lines), (
        "the fake-side fault reached the real wiring; the two adapters are not "
        "independent and the blind-region measurement is void"
    )
    assert not any(line.startswith("CLOSE") for line in fake_lines), (
        "PA-M12 did not change what the fake wiring reports; the mutant is "
        "equivalent and its survival elsewhere would say nothing"
    )


# -- the positive control does a control's job -----------------------------

#: The sealed EVAL-RERUN arm trees. Real programs, in this repository, that a
#: probe can be pointed at -- which is why the non-vacuity test below can use a
#: measured BROKEN rather than a constructed one.
RERUN_ARMS = REPO_ROOT / "specs/results/scorecards/hexagonal-prompting-rerun/arms"


def _positive_controls(rows):
    return [r for r in rows if str(r.get("control_role", "")).startswith("positive")]


def test_every_positive_control_is_probed_against_the_property_it_declares(rows):
    """Run, not asserted -- and since FI-01 the verdict is not assumed GREEN.

    This test used to assert `HOLDS` for every positive control. It passed, and
    it was worth nothing: the probe was one-sided, so it returned `HOLDS` for a
    no-op (`PA-06-DF-07 b`). With both halves running, `PA-M14` on
    `reference_ports` is measured **INERT** -- invisible after one accepted
    reserve as well as before one -- and R2 says that is REPORTED, never made
    green. So what is asserted here is the thing that is actually true and
    load-bearing: every declared control is probed against the property it
    declares, and the measured verdicts are pinned so a change to either has to
    come here and say so.
    """
    measured = {}
    for row in _positive_controls(rows):
        tree_name = str(row["path"]).split("/")[0]
        inner = str(row["path"])[len(tree_name) + 1:]
        declared, problems = cc.resolve_control_properties(AB / "seeded_faults.toml")
        assert not problems, problems
        prop = declared[str(row["id"])]
        verdict, detail = cc.probe_control_property(
            AB / tree_name, "quota_ledger", inner, row["find"], row["replace"], prop
        )
        measured[str(row["id"])] = (tree_name, verdict)
        assert verdict != "ERROR", f"{row['id']} on {tree_name}: {detail}"

    assert measured == {
        "M07-positive-control-wrong-hold": ("reference", "HOLDS"),
        # RED, and kept. PA-M14 records `amount + 1` on the reservation; no
        # query exposes a reservation's amount and this tree STORES `available`,
        # so ONE accepted reserve moves nothing. Every generated corpus case is
        # single-action.
        "PA-M14-positive-control-accepted-hold-too-large": ("reference_ports", "INERT"),
        "FI-M15-positive-control-commit-total-too-large": ("reference_ports", "HOLDS"),
    }, measured


def test_the_control_property_probe_is_not_vacuous():
    """The other half, and the half that matters.

    A probe that returns HOLDS for everything proves nothing about the controls
    it passes. The negative case is not constructed for this test: it is M07's
    sealed semantic re-anchored onto arm B's sealed tree, which is the exact
    configuration EVAL-RERUN's adversarial channel found by building a corpus
    with every `Reserve` case deleted. If this ever reports HOLDS, the probe has
    stopped measuring the property and every PASS above is unreadable.
    """
    verdict, detail = cc.probe_control_property(
        RERUN_ARMS / "arm_b",
        "quota_ledger",
        "quota_ledger/domain.py",
        "        return sum(held.amount for held in self._holdings(tenant))",
        "        return sum(held.amount for held in self._holdings(tenant)) + 1  # MUTANT M07",
    )
    assert verdict == "BROKEN", (
        f"arm B's M07 probed {verdict} ({detail}). It is measured BROKEN: arm B "
        f"derives available(), so the fault is present from construction. A probe "
        f"that passes it is not measuring the accept-path property."
    )


def test_the_repaired_semantic_holds_on_the_arm_that_broke_the_old_one():
    """The repair, checked against the tree that motivated it."""
    verdict, detail = cc.probe_control_property(
        RERUN_ARMS / "arm_b",
        "quota_ledger",
        "quota_ledger/domain.py",
        "        self._outstanding[reservation_id] = Reservation(tenant, amount)",
        "        self._outstanding[reservation_id] = Reservation(tenant, amount + 1)  # PROBE",
    )
    assert verdict == "HOLDS", f"the accept-path semantic is {verdict} on arm B: {detail}"


def test_positive_controls_do_not_share_a_role_string(rows):
    """EVAL-RERUN-DF-03: arm B's catalogue carried arm A's role string verbatim
    over a mutant arm B's own data contradicted. Copied role strings are how a
    control stops being about the thing it guards."""
    roles = [str(r.get("control_role", "")) for r in _positive_controls(rows)]
    assert len(set(roles)) == len(roles), "two positive controls share a role string"


def test_every_positive_control_declares_a_property_the_probe_can_execute(rows):
    """Declared in a side table, because M07 is sealed and is not amended.

    A property NAME that the probe does not implement is a declaration nothing
    executes, which is the shape this repository has shipped five times.
    """
    declared, problems = cc.resolve_control_properties(AB / "seeded_faults.toml")
    assert not problems, problems
    for row in _positive_controls(rows):
        name = declared.get(str(row["id"]))
        assert name in cc.CONTROL_PROPERTIES, (
            f"{row['id']} declares {name!r}, which the probe cannot execute; "
            f"known: {sorted(cc.CONTROL_PROPERTIES)}"
        )


def test_m07_is_neither_deleted_nor_excused(rows):
    """The audit says arm B's M07 is not a control. It does not say it is gone.

    M07 still runs, is still seeded exactly as the sealed catalogue declares it,
    and is still scored in its class row. A catalogue that deleted a row after
    finding it inconvenient would be doing the thing EVAL-SUPPRESS caught.
    """
    m07 = next(r for r in rows if r["id"] == "M07-positive-control-wrong-hold")
    assert m07["find"] == "        self._available[tenant] -= amount"
    assert m07["fault_class"] == "wrong_value"
    assert str(m07["control_role"]).startswith("positive")
    text = (AB / "seeded_faults.toml").read_text(encoding="utf-8")
    assert "[pa_measured_control_audit]" in text
    assert "does not license deleting, re-seeding or excusing M07" in text


# -- the sealed predictions ------------------------------------------------


def test_predictions_are_committed_with_at_least_three_negatives():
    assert PREDICTIONS.is_file(), "PREDICTIONS-PA.md is not committed"
    text = PREDICTIONS.read_text(encoding="utf-8")
    negatives = [
        line for line in text.splitlines()
        if line.startswith("### N") and " — " in line
    ]
    assert len(negatives) >= 3, (
        f"{len(negatives)} negative prediction(s); at least 3 required. A round "
        f"where every prediction passes has measured nothing."
    )
    # Each negative must name the instrument that settles it, or it is an
    # opinion, and an opinion cannot be wrong in a way anyone notices.
    for block in text.split("### N")[1:]:
        head = block.split("### ")[0]
        assert "**Instrument:**" in head, f"negative prediction without an instrument:\n{head[:120]}"
        assert "**Direction:**" in head, f"negative prediction without a direction:\n{head[:120]}"


def test_the_predictions_record_the_measured_length_match():
    """A sealed prediction about arm C that does not carry the number it was
    sealed against cannot be scored later against a changed arm C."""
    text = PREDICTIONS.read_text(encoding="utf-8")
    control = cc.arm_prompt("arm_a")
    b_unique = len(cc.unique_content(cc.arm_prompt("arm_b"), control))
    c_unique = len(cc.unique_content(cc.arm_prompt("arm_c"), control))
    assert f"**{b_unique} lines**" in text, "arm B's measured unique-content count is not sealed"
    assert f"**{c_unique} lines**" in text, "arm C's measured unique-content count is not sealed"


def test_nothing_added_here_refuses_anything_in_the_product():
    """`no_new_gates_rule`, checked rather than promised.

    The harness may exit non-zero about its own fixture. What it may not do is
    grow a flag that lets a survivor or a sub-floor rate pass, which is the
    degeneracy `scripts/kill_test.py` scans for.
    """
    catalogue = (AB / "seeded_faults.toml").read_text(encoding="utf-8")
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import kill_test  # noqa: PLC0415

    for key in kill_test.SUPPRESSION_KEYS:
        assert f"\n{key} =" not in catalogue and f"[[{key}]]" not in catalogue, (
            f"the catalogue grew a suppression-shaped key {key!r}"
        )
    _ = copy.copy(kill_test.SUPPRESSION_KEYS)
