"""SS-05. THE ONE INSTANCE OF THE ABSENT-INPUT CLASS THAT LEAVES THIS REPOSITORY.

`CA-10-DF-21`. `generate_python.render_validators` emitted
`def validate_state(state) -> None: return None` whenever `invariants:` was
absent, nulled, or an empty list. That function is the spec double's STATE
ORACLE: `explain_state_failure` returns `""` for every state through it,
`validate_trace` opens by calling it, and every generated contract test and
Hypothesis strategy runs through it. `extract_spec_manifest.validate_manifest`
does not list `invariants` among its required keys, so generation exited 0 with
ZERO ERRORS and nothing anywhere said the double had no oracle.

It is not a defect in this repository's record. It is a defect the toolchain
SCAFFOLDS INTO EVERY REPOSITORY IT TOUCHES.

THREE STATES, NOT TWO, and each is asserted separately here, because a fallback
that merely moves the false PASS to a rarer input has not fixed the class:

    absent      the `invariants:` key is not in the manifest at all
    unreadable  the key is there and did not read as a list of names
    empty       the key is there, parses perfectly, and names nothing

The correct answer to all three is A REFUSAL. `pass` is not available: an oracle
that accepts every state is not a weaker check, it is no check.

THE SUBJECTS ARE REAL, per `R1`. `ex4_pipeline_coherent` and `reminder_worker`
are the two shipped examples the record names, `atomic_publisher` is the third
this ticket's re-measurement found, and `legacy_payment_http` is the CONTROL --
it declares its invariants, has no `invariant_templates`, and has always shipped
the refusing form, which is why the refusal is known to be livable rather than
hoped to be.

NON-VACUITY. Every assertion below would fail against the code as it shipped at
`f45a245`: the pre-repair `validate_state` body is the literal line
`    return None`, and `test_the_pre_repair_body_is_gone_from_every_live_package`
pins that no live generated package still carries it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_python as gp  # noqa: E402
from extract_spec_manifest import load_manifest, validate_manifest  # noqa: E402

#: Every live manifest in this tree that renders a state class. The frozen
#: measurement copy under `specs/results/**/measure/` is deliberately NOT here:
#: `instruments.toml` declares that population out of scope and re-running one is
#: not a property of the toolchain.
LIVE_MANIFESTS = {
    "ex4_pipeline_coherent":
        "examples/validation/ex4_pipeline_coherent/specs/program_model/spec_manifest.yaml",
    "reminder_worker":
        "examples/effect_providers/reminder_worker/specs/program_model/spec_manifest.yaml",
    "atomic_publisher":
        "examples/effect_providers/atomic_publisher/specs/program_model/spec_manifest.yaml",
    "legacy_payment_http":
        "examples/effect_providers/legacy_payment_http/specs/program_model/spec_manifest.yaml",
}

#: The four live generated packages. `ex5_pipeline_divergent` has no manifest of
#: its own -- it is `ex4`'s architecture twin and its package is generated from
#: `ex4`'s manifest -- so it is listed here and not above.
LIVE_PACKAGES = [
    "examples/validation/ex4_pipeline_coherent/generated/pipeline_contract/validators.py",
    "examples/validation/ex5_pipeline_divergent/generated/pipeline_contract/validators.py",
    "examples/effect_providers/reminder_worker/generated/reminder_contract/validators.py",
    "examples/effect_providers/atomic_publisher/specs/program_model/generated/"
    "atomic_publisher_contract/validators.py",
]


def _validate_state_body(manifest_path: Path) -> str:
    manifest = load_manifest(manifest_path)
    rendered = gp.render_validators(manifest, manifest_path)
    start = rendered.index("def validate_state")
    return rendered[start:rendered.index("def explain_state_failure")]


# ---------------------------------------------------------------------------
# The three states, on a real manifest each
# ---------------------------------------------------------------------------


def test_an_absent_invariants_key_refuses_and_says_it_is_absent(tmp_path) -> None:
    """State 1. The subject is `ex4_pipeline_coherent`'s real manifest, whose
    `Pipeline.cfg` hands TLC THREE invariants while the manifest names none."""
    path = ROOT / LIVE_MANIFESTS["ex4_pipeline_coherent"]
    manifest = load_manifest(path)
    manifest.pop("invariants", None)

    assert gp.invariants_absence_state(manifest) == gp.INVARIANTS_ABSENT
    body = gp.no_state_oracle_body(gp.INVARIANTS_ABSENT, path)
    assert "raise NotImplementedError" in body
    assert gp.NO_STATE_ORACLE in body
    assert "[absent]" in body
    assert "return None" not in body


def test_an_unreadable_invariants_key_refuses_in_DIFFERENT_WORDS() -> None:
    """State 2. `invariants:` written with no value parses to `None`.

    It must NOT answer in the empty state's words: `SS-01-DF-04` is the whole
    reason three states exist rather than two.
    """
    manifest = {"invariants": None}
    assert gp.invariants_absence_state(manifest) == gp.INVARIANTS_UNREADABLE

    path = ROOT / LIVE_MANIFESTS["reminder_worker"]
    unreadable = gp.no_state_oracle_body(gp.INVARIANTS_UNREADABLE, path)
    empty = gp.no_state_oracle_body(gp.INVARIANTS_EMPTY, path)
    absent = gp.no_state_oracle_body(gp.INVARIANTS_ABSENT, path)
    assert unreadable != empty != absent != unreadable, (
        "two absent-input states answering in identical words is the defect "
        "SS-07-DF-08, SS-06-DF-05 and SS-01-DF-04 are all instances of"
    )


def test_an_empty_invariants_list_refuses_rather_than_accepting_every_state() -> None:
    """State 3, THE ONE THAT MATTERS MOST, because it is the one that looks
    innocent. `reminder_worker` and `atomic_publisher` both ship
    `invariants: []` while their `.cfg`s hand TLC two invariants each."""
    assert gp.invariants_absence_state({"invariants": []}) == gp.INVARIANTS_EMPTY

    for name in ("reminder_worker", "atomic_publisher"):
        path = ROOT / LIVE_MANIFESTS[name]
        manifest = load_manifest(path)
        manifest["invariants"] = []
        assert gp.invariants_absence_state(manifest) == gp.INVARIANTS_EMPTY


def test_a_declared_invariant_still_generates_an_oracle() -> None:
    """The non-vacuity guard on the repair itself: a manifest that DOES name
    invariants must still get calls, or the repair has refused everything and
    proved nothing. `legacy_payment_http` is the control."""
    body = _validate_state_body(ROOT / LIVE_MANIFESTS["legacy_payment_http"])
    assert "validate_type_invariant(state)" in body
    assert "validate_result_invariant(state)" in body
    assert gp.NO_STATE_ORACLE not in body


# ---------------------------------------------------------------------------
# The shipped artifacts
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("relative", sorted(LIVE_PACKAGES))
def test_the_pre_repair_body_is_gone_from_every_live_package(relative: str) -> None:
    """`def validate_state(...): return None` was shipped in 13 tracked files.

    Nine of them are frozen or sealed -- five evidence copies under
    `reminder_worker/evidence/validation-runs/`, three under `specs/.history/`
    which `R-H4` seals, and one under `hexagonal-prompting/measure/` -- and are
    LEFT EXACTLY AS THEY ARE. These four are live and are regenerated.
    """
    text = (ROOT / relative).read_text(encoding="utf-8")
    start = text.index("def validate_state")
    body = text[start:text.index("def explain_state_failure")]
    assert "return None" not in body, (
        f"{relative} still ships a state oracle that accepts every state"
    )


@pytest.mark.parametrize("name", sorted(LIVE_MANIFESTS))
def test_every_live_manifest_now_names_the_invariants_its_cfg_names(name: str) -> None:
    """The examples half of the repair.

    Repairing the generator alone would leave the shipped examples refusing
    correctly and checking nothing, which is honest but is not a fixed example.
    Each manifest now declares the invariant names its own `.cfg` hands TLC.
    """
    path = ROOT / LIVE_MANIFESTS[name]
    manifest = load_manifest(path)
    declared = manifest.get("invariants")
    assert declared, f"{name} still declares no invariants"

    cfgs = sorted(path.parent.glob("*.cfg"))
    assert cfgs, f"{name} has no .cfg to compare against"
    from_cfg: set[str] = set()
    for cfg in cfgs:
        for line in cfg.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            for keyword in ("INVARIANTS ", "INVARIANT "):
                if stripped.startswith(keyword):
                    from_cfg.update(stripped[len(keyword):].split())
                    break
    assert from_cfg, f"{name}'s .cfg files declare no INVARIANT"
    assert set(map(str, declared)) == from_cfg, (
        f"{name}: manifest declares {sorted(map(str, declared))} and its .cfg "
        f"declares {sorted(from_cfg)} -- a double whose oracle differs from the "
        f"model's is not a double of that model"
    )


def test_validate_manifest_still_reports_zero_errors_and_that_is_FILED_NOT_FIXED() -> None:
    """WHAT THIS REPAIR DOES NOT DO, asserted so it cannot be over-read.

    `extract_spec_manifest.validate_manifest` still does not list `invariants`
    among its required keys, so a manifest with no invariants at all is still
    reported as having ZERO ERRORS at validation time and only refuses later, at
    generation. `extract_spec_manifest.py` is outside `SS-05`'s conflict keys;
    that half is filed as `SS-05-DF-02`, not repaired here, and this test exists
    so the gap is executed rather than remembered.
    """
    path = ROOT / LIVE_MANIFESTS["ex4_pipeline_coherent"]
    manifest = load_manifest(path)
    manifest.pop("invariants", None)
    assert validate_manifest(manifest, path) == [], (
        "validate_manifest now reports the missing invariants -- if this fails, "
        "SS-05-DF-02 has been repaired and this test should become its "
        "regression pin rather than its disclosure"
    )
