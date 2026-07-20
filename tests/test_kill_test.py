"""MF-016: unit tests for oracle 4, the mutation kill test.

Kill-test RUNS over a real distilled corpus are deferred epic-wide to MF-023.
These tests therefore validate the MECHANISM -- coverage derivation, the
floor gate, the refusal to score a partial experiment, seeding safety, the
refinement pointers, and the abstraction validator -- using synthetic mutants
and fixture spec trees. What they deliberately do NOT prove is that this
repository's real corpus actually kills the real catalog's 19 mutants. That
is an empirical claim and only a real run can make it; see
``specs/tickets/MF-016/results/DEFERRED-TO-MF-023.md``.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.kill_test import (  # noqa: E402
    EXIT_BELOW_FLOOR,
    EXIT_PASS,
    EXIT_USAGE,
    VERDICT_BELOW_FLOOR,
    VERDICT_INCOMPLETE_CATALOG,
    VERDICT_NO_CONTROL,
    VERDICT_PASS,
    VERDICT_REGRESSED,
    KillTestCatalogError,
    Mutant,
    compare_reports,
    declared_invariants,
    declared_ports,
    load_catalog,
    missing_boundaries,
    parse_mutants,
    required_boundaries,
    run_kill_test,
    seeded,
)

MANIFEST = """\
module: Demo
budgets:
  kill_rate_floor: 0.8
effects:
  components:
    DemoPort:
      ports:
        alpha:
          type: filesystem.write
          target: "**/a/**"
        beta:
          type: process.spawn
          target: "*b*"
"""

CFG = """\
SPECIFICATION Spec

CONSTANTS
  Xs = {x}

INVARIANTS
  TypeInvariant
  SomethingHolds
"""


def make_spec_dir(tmp_path: Path, *, manifest: str = MANIFEST, cfg: str = CFG) -> Path:
    spec_dir = tmp_path / "spec"
    spec_dir.mkdir()
    (spec_dir / "spec_manifest.yaml").write_text(manifest, encoding="utf-8")
    (spec_dir / "MC.cfg").write_text(cfg, encoding="utf-8")
    return spec_dir


def make_mutant(
    ident: str,
    kind: str,
    ref: str,
    *,
    path: str = "src.py",
    find: str = "GOOD",
    variable: str = "some_var",
    action: str = "SomeAction",
) -> Mutant:
    return Mutant(
        id=ident,
        boundary_kind=kind,
        boundary_ref=ref,
        path=path,
        find=find,
        replace="BAD",
        description=f"fault at {ref}",
        refine_variable=variable,
        refine_action=action,
    )


def full_catalog() -> list[Mutant]:
    """One mutant per port and per invariant in the fixture spec."""

    return [
        make_mutant("m-alpha", "port", "alpha"),
        make_mutant("m-beta", "port", "beta"),
        make_mutant("m-type", "invariant", "TypeInvariant"),
        make_mutant("m-holds", "invariant", "SomethingHolds"),
    ]


def runner_killing(*ids: str, control_green: bool = True):
    """A case runner that kills exactly the named mutants.

    ``mutant is None`` is the control run: it reports "failed" only when
    ``control_green`` is False.
    """

    wanted = set(ids)

    def run(mutant: Mutant | None) -> tuple[bool, list[str], str]:
        if mutant is None:
            return (not control_green), [], "control"
        killed = mutant.id in wanted
        return killed, ["case-0"] if killed else [], "synthetic"

    return run


def kill_all(mutant: Mutant | None) -> tuple[bool, list[str], str]:
    if mutant is None:
        return False, [], "control"  # control is green
    return True, ["case-0"], "synthetic"


# ---------------------------------------------------------------------------
# Coverage is derived from the declarations, not promised by the catalog
# ---------------------------------------------------------------------------


class TestCoverageIsComputedFromTheDeclarations:
    def test_ports_come_from_the_manifest(self, tmp_path: Path) -> None:
        spec_dir = make_spec_dir(tmp_path)
        assert declared_ports(spec_dir / "spec_manifest.yaml") == ["alpha", "beta"]

    def test_invariants_come_from_the_tlc_config(self, tmp_path: Path) -> None:
        spec_dir = make_spec_dir(tmp_path)
        assert declared_invariants(spec_dir / "MC.cfg") == ["TypeInvariant", "SomethingHolds"]

    def test_required_boundaries_are_one_per_port_and_one_per_invariant(
        self, tmp_path: Path
    ) -> None:
        spec_dir = make_spec_dir(tmp_path)
        assert required_boundaries(spec_dir) == [
            ("port", "alpha"),
            ("port", "beta"),
            ("invariant", "TypeInvariant"),
            ("invariant", "SomethingHolds"),
        ]

    def test_a_newly_declared_port_makes_a_previously_complete_catalog_incomplete(
        self, tmp_path: Path
    ) -> None:
        """The obligation cannot drift behind the model.

        This is the whole point of deriving coverage every run rather than
        documenting a rule. Adding a port to the manifest immediately breaks
        the kill test until somebody seeds a fault for it.
        """

        spec_dir = make_spec_dir(tmp_path)
        catalog = full_catalog()
        assert missing_boundaries(catalog, required_boundaries(spec_dir)) == []

        manifest = (spec_dir / "spec_manifest.yaml").read_text(encoding="utf-8")
        manifest += '        gamma:\n          type: network.http\n          target: "*"\n'
        (spec_dir / "spec_manifest.yaml").write_text(manifest, encoding="utf-8")

        assert missing_boundaries(catalog, required_boundaries(spec_dir)) == [("port", "gamma")]

    def test_a_newly_added_invariant_makes_a_previously_complete_catalog_incomplete(
        self, tmp_path: Path
    ) -> None:
        spec_dir = make_spec_dir(tmp_path)
        catalog = full_catalog()
        cfg = (spec_dir / "MC.cfg").read_text(encoding="utf-8") + "  NewlyAdded\n"
        (spec_dir / "MC.cfg").write_text(cfg, encoding="utf-8")

        assert missing_boundaries(catalog, required_boundaries(spec_dir)) == [
            ("invariant", "NewlyAdded")
        ]


# ---------------------------------------------------------------------------
# A partial experiment yields no number
# ---------------------------------------------------------------------------


class TestAPartialExperimentIsRefusedRatherThanScored:
    def test_uncovered_boundary_yields_incomplete_catalog(self, tmp_path: Path) -> None:
        spec_dir = make_spec_dir(tmp_path)
        catalog = full_catalog()[:-1]  # drop the SomethingHolds mutant
        report = run_kill_test(
            spec_dir=spec_dir, catalog=catalog, runner=kill_all, root=tmp_path, warn=False
        )
        assert report.verdict == VERDICT_INCOMPLETE_CATALOG
        assert report.ok is False
        assert report.exit_code == EXIT_USAGE

    def test_no_kill_rate_is_computed_over_a_partial_catalog(self, tmp_path: Path) -> None:
        """Not 0.0 and not 1.0 -- None.

        Reporting any number here would assert something the run has no
        evidence for, which is the defect MF-027 removed from the effect
        oracle when it stopped calling unobserved targets clean.
        """

        spec_dir = make_spec_dir(tmp_path)
        report = run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog()[:-1],
            runner=kill_all,
            root=tmp_path,
            warn=False,
        )
        assert report.kill_rate is None

    def test_an_incomplete_catalog_does_not_run_the_mutants_it_does_have(
        self, tmp_path: Path
    ) -> None:
        spec_dir = make_spec_dir(tmp_path)
        calls: list[str] = []

        def counting(mutant: Mutant) -> tuple[bool, list[str], str]:
            calls.append(mutant.id)
            return True, [], ""

        run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog()[:-1],
            runner=counting,
            root=tmp_path,
            warn=False,
        )
        assert calls == []

    def test_killing_every_mutant_in_a_partial_catalog_still_does_not_pass(
        self, tmp_path: Path
    ) -> None:
        """A perfect score on a partial surface is the exact degeneracy to block."""

        spec_dir = make_spec_dir(tmp_path)
        report = run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog()[:1],
            runner=kill_all,
            root=tmp_path,
            warn=False,
        )
        assert report.ok is False
        assert report.verdict == VERDICT_INCOMPLETE_CATALOG


# ---------------------------------------------------------------------------
# The floor gate
# ---------------------------------------------------------------------------


class TestTheFloorGateFailsBelowFloorWithNoWaiver:
    def test_rate_at_or_above_floor_passes(self, tmp_path: Path) -> None:
        spec_dir = make_spec_dir(tmp_path)
        report = run_kill_test(
            spec_dir=spec_dir, catalog=full_catalog(), runner=kill_all, root=tmp_path, warn=False
        )
        assert report.kill_rate == 1.0
        assert report.verdict == VERDICT_PASS
        assert report.ok is True
        assert report.exit_code == EXIT_PASS

    def test_rate_below_floor_fails(self, tmp_path: Path) -> None:
        spec_dir = make_spec_dir(tmp_path)
        report = run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog(),
            runner=runner_killing("m-alpha", "m-beta"),  # 2/4 = 0.5 < 0.8
            root=tmp_path,
            warn=False,
        )
        assert report.kill_rate == 0.5
        assert report.verdict == VERDICT_BELOW_FLOOR
        assert report.ok is False
        assert report.exit_code == EXIT_BELOW_FLOOR

    def test_exactly_at_the_floor_passes(self, tmp_path: Path) -> None:
        """0.8 meets a floor of 0.8. The comparison is ``<``, not ``<=``."""

        spec_dir = make_spec_dir(tmp_path)
        catalog = full_catalog() + [make_mutant("m-extra", "port", "alpha")]
        report = run_kill_test(
            spec_dir=spec_dir,
            catalog=catalog,
            runner=runner_killing("m-alpha", "m-beta", "m-type", "m-holds"),  # 4/5 = 0.8
            root=tmp_path,
            warn=False,
        )
        assert report.kill_rate == pytest.approx(0.8)
        assert report.ok is True

    def test_just_below_the_floor_fails(self, tmp_path: Path) -> None:
        spec_dir = make_spec_dir(tmp_path)
        catalog = full_catalog() + [make_mutant(f"m-pad{i}", "port", "alpha") for i in range(6)]
        killed = ["m-alpha", "m-beta", "m-type", "m-holds", "m-pad0", "m-pad1", "m-pad2"]
        report = run_kill_test(
            spec_dir=spec_dir,
            catalog=catalog,
            runner=runner_killing(*killed),  # 7/10 = 0.7
            root=tmp_path,
            warn=False,
        )
        assert report.kill_rate == pytest.approx(0.7)
        assert report.ok is False

    def test_the_floor_is_read_from_the_manifest_not_hardcoded(self, tmp_path: Path) -> None:
        manifest = MANIFEST.replace("kill_rate_floor: 0.8", "kill_rate_floor: 0.4")
        spec_dir = make_spec_dir(tmp_path, manifest=manifest)
        report = run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog(),
            runner=runner_killing("m-alpha", "m-beta"),  # 0.5
            root=tmp_path,
            warn=False,
        )
        assert report.kill_rate_floor == pytest.approx(0.4)
        assert report.ok is True, "0.5 clears a negotiated floor of 0.4"

    def test_ok_is_false_for_every_non_pass_verdict(self, tmp_path: Path) -> None:
        """One conjunction; no second code path a later change could relax."""

        spec_dir = make_spec_dir(tmp_path)
        below = run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog(),
            runner=runner_killing("m-alpha"),
            root=tmp_path,
            warn=False,
        )
        incomplete = run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog()[:2],
            runner=kill_all,
            root=tmp_path,
            warn=False,
        )
        assert below.ok is False and incomplete.ok is False
        assert {below.verdict, incomplete.verdict} == {
            VERDICT_BELOW_FLOOR,
            VERDICT_INCOMPLETE_CATALOG,
        }


class TestNothingWaivesTheFloor:
    def test_suppression_shaped_keys_are_reported_and_never_honored(self) -> None:
        raw = {
            "waiver": "the owner said it was fine",
            "mutants": [
                {
                    "id": "m1",
                    "boundary_kind": "port",
                    "boundary_ref": "alpha",
                    "path": "src.py",
                    "find": "GOOD",
                    "replace": "BAD",
                    "description": "d",
                    "refine_variable": "v",
                    "refine_action": "A",
                    "expected_to_survive": True,
                    "justification": "known limitation",
                }
            ],
        }
        mutants, suppressions = parse_mutants(raw)
        assert len(mutants) == 1
        assert "waiver" in suppressions
        assert "mutants[0].expected_to_survive" in suppressions
        assert "mutants[0].justification" in suppressions
        # And none of them became behavior:
        assert not hasattr(mutants[0], "expected_to_survive")

    def test_a_recorded_justification_does_not_change_the_verdict(self, tmp_path: Path) -> None:
        """The inverse test: byte-identical verdicts with and without a waiver."""

        spec_dir = make_spec_dir(tmp_path)
        plain = run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog(),
            runner=runner_killing("m-alpha"),
            root=tmp_path,
            warn=False,
        )
        justified = run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog(),
            runner=runner_killing("m-alpha"),
            root=tmp_path,
            suppressions=["mutants[1].waiver", "mutants[2].expected_to_survive"],
            warn=False,
        )
        assert plain.verdict == justified.verdict == VERDICT_BELOW_FLOOR
        assert plain.kill_rate == justified.kill_rate
        assert plain.exit_code == justified.exit_code
        assert justified.ignored_suppression_keys  # reported...
        assert justified.ok is False  # ...and not honored

    def test_the_cli_exposes_no_flag_that_waives_the_floor(self) -> None:
        """A gate with an escape hatch is not a gate. Assert the hatch is absent.

        Introspects the registered argparse options rather than grepping the
        help text -- the module docstring names the flags it refuses to have,
        and matching prose would pass or fail for the wrong reason.
        """

        import argparse

        from scripts.run_kill_test import add_arguments

        parser = argparse.ArgumentParser()
        add_arguments(parser)
        registered = {
            option for action in parser._actions for option in action.option_strings
        }
        forbidden = {
            "--allow-below-floor",
            "--accept-survivors",
            "--accept-survivor",
            "--allow-survivors",
            "--waive",
            "--waiver",
            "--force",
            "--skip-kill-test",
            "--no-gate",
            "--allow-over-budget",
            "--expected-to-survive",
        }
        assert registered & forbidden == set(), (
            f"escape hatches registered on the kill-test CLI: {sorted(registered & forbidden)}"
        )

    def test_no_argument_can_turn_a_below_floor_verdict_into_a_pass(self) -> None:
        """Stronger than an allowlist: no argument participates in ``ok``.

        ``KillTestReport.ok`` is computed from the verdict alone, so there is
        no argument, environment variable, or manifest key a future change
        could route into it without deleting this test.
        """

        import inspect

        from scripts.kill_test import KillTestReport

        source = inspect.getsource(KillTestReport.ok.fget)
        assert source.count("return") == 1
        assert "VERDICT_PASS" in source
        for smell in ("if ", "or ", "and ", "getattr", "os.environ", "allow", "override"):
            assert smell not in source.split("return")[-1], (
                f"KillTestReport.ok grew a conditional ({smell!r}); the gate must stay "
                f"a single unconditional comparison"
            )


# ---------------------------------------------------------------------------
# A survivor is a pointer, not a statistic
# ---------------------------------------------------------------------------


class TestASurvivorPointsAtWhatToRefine:
    def test_survivor_names_the_variable_and_action_to_refine(self, tmp_path: Path) -> None:
        spec_dir = make_spec_dir(tmp_path)
        catalog = [
            make_mutant("m-alpha", "port", "alpha"),
            make_mutant("m-beta", "port", "beta", variable="corpus_gate", action="AnalyzeCorpus"),
            make_mutant("m-type", "invariant", "TypeInvariant"),
            make_mutant("m-holds", "invariant", "SomethingHolds"),
        ]
        report = run_kill_test(
            spec_dir=spec_dir,
            catalog=catalog,
            runner=runner_killing("m-alpha", "m-type", "m-holds"),
            root=tmp_path,
            warn=False,
        )
        pointers = report.refinement_pointers(catalog)
        assert len(pointers) == 1
        pointer = pointers[0]
        assert pointer["mutant_id"] == "m-beta"
        assert pointer["refine_variable"] == "corpus_gate"
        assert pointer["refine_action"] == "AnalyzeCorpus"
        assert pointer["boundary_kind"] == "port"
        assert pointer["boundary_ref"] == "beta"
        assert "corpus_gate" in pointer["message"]
        assert "AnalyzeCorpus" in pointer["message"]
        assert "too abstract" in pointer["message"]

    def test_a_catalog_entry_without_a_refinement_pointer_is_rejected(self) -> None:
        """A mutant that cannot say what to refine is useless when it survives."""

        for omitted in ("refine_variable", "refine_action", "boundary_ref"):
            entry = {
                "id": "m1",
                "boundary_kind": "port",
                "boundary_ref": "alpha",
                "path": "src.py",
                "find": "GOOD",
                "replace": "BAD",
                "description": "d",
                "refine_variable": "v",
                "refine_action": "A",
            }
            del entry[omitted]
            with pytest.raises(KillTestCatalogError, match=omitted):
                parse_mutants({"mutants": [entry]})

    def test_every_survivor_appears_in_the_json_evidence(self, tmp_path: Path) -> None:
        spec_dir = make_spec_dir(tmp_path)
        catalog = full_catalog()
        report = run_kill_test(
            spec_dir=spec_dir,
            catalog=catalog,
            runner=runner_killing("m-alpha"),
            root=tmp_path,
            warn=False,
        )
        out = tmp_path / "results" / "kill-test.json"
        report.write(out, catalog)
        payload = json.loads(out.read_text(encoding="utf-8"))
        assert payload["verdict"] == VERDICT_BELOW_FLOOR
        assert payload["ok"] is False
        assert len(payload["kill_matrix"]) == 4
        assert {row["mutant_id"] for row in payload["kill_matrix"] if not row["killed"]} == {
            "m-beta",
            "m-type",
            "m-holds",
        }
        assert len(payload["surviving_mutants"]) == 3
        for survivor in payload["surviving_mutants"]:
            assert survivor["refine_variable"]
            assert survivor["refine_action"]

    def test_evidence_is_written_even_when_the_verdict_is_bad(self, tmp_path: Path) -> None:
        """A report that only appears when the news is good is not evidence."""

        spec_dir = make_spec_dir(tmp_path)
        report = run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog(),
            runner=runner_killing(),
            root=tmp_path,
            warn=False,
        )
        out = tmp_path / "deep" / "nested" / "kill-test.json"
        report.write(out, full_catalog())
        assert out.is_file()
        assert json.loads(out.read_text(encoding="utf-8"))["kill_rate"] == 0.0


# ---------------------------------------------------------------------------
# Seeding is safe and honest
# ---------------------------------------------------------------------------


class TestSeedingIsSafe:
    def test_seeding_applies_then_restores_the_file(self, tmp_path: Path) -> None:
        source = tmp_path / "src.py"
        source.write_text("value = 'GOOD'\n", encoding="utf-8")
        mutant = make_mutant("m", "port", "alpha")
        with seeded(mutant, tmp_path):
            assert source.read_text(encoding="utf-8") == "value = 'BAD'\n"
        assert source.read_text(encoding="utf-8") == "value = 'GOOD'\n"

    def test_the_file_is_restored_even_when_the_run_raises(self, tmp_path: Path) -> None:
        """A kill test that can corrupt the tree is worse than the bug it hunts."""

        source = tmp_path / "src.py"
        source.write_text("value = 'GOOD'\n", encoding="utf-8")
        with pytest.raises(RuntimeError):
            with seeded(make_mutant("m", "port", "alpha"), tmp_path):
                raise RuntimeError("corpus blew up")
        assert source.read_text(encoding="utf-8") == "value = 'GOOD'\n"

    def test_a_stale_mutant_is_refused_not_counted_as_killed(self, tmp_path: Path) -> None:
        """A fault that no longer applies is not a killed fault."""

        source = tmp_path / "src.py"
        source.write_text("value = 'REFACTORED'\n", encoding="utf-8")
        with pytest.raises(KillTestCatalogError, match="stale"):
            with seeded(make_mutant("m", "port", "alpha"), tmp_path):
                pass

    def test_an_empty_catalog_is_refused(self) -> None:
        with pytest.raises(KillTestCatalogError, match="not a passing kill"):
            parse_mutants({"mutants": []})

    def test_duplicate_mutant_ids_are_refused(self) -> None:
        entry = {
            "id": "dup",
            "boundary_kind": "port",
            "boundary_ref": "alpha",
            "path": "src.py",
            "find": "GOOD",
            "replace": "BAD",
            "description": "d",
            "refine_variable": "v",
            "refine_action": "A",
        }
        with pytest.raises(KillTestCatalogError, match="duplicate"):
            parse_mutants({"mutants": [entry, dict(entry)]})


# ---------------------------------------------------------------------------
# The abstraction validator
# ---------------------------------------------------------------------------


class TestKillRatePreservingAbstraction:
    @staticmethod
    def report(rate: float, killed: list[str], survived: list[str]) -> dict:
        return {
            "kill_rate": rate,
            "kill_matrix": [{"mutant_id": m, "killed": True} for m in killed]
            + [{"mutant_id": m, "killed": False} for m in survived],
        }

    def test_a_holding_kill_rate_licenses_the_abstraction(self) -> None:
        before = self.report(1.0, ["a", "b"], [])
        after = self.report(1.0, ["a", "b"], [])
        legitimate, message = compare_reports(before, after)
        assert legitimate is True
        assert "legitimate" in message

    def test_a_rising_kill_rate_licenses_the_abstraction(self) -> None:
        before = self.report(0.5, ["a"], ["b"])
        after = self.report(1.0, ["a", "b"], [])
        legitimate, _ = compare_reports(before, after)
        assert legitimate is True

    def test_a_dropping_kill_rate_refuses_the_abstraction(self) -> None:
        """This is what tells a re-representation from a disguised deletion."""

        before = self.report(1.0, ["a", "b"], [])
        after = self.report(0.5, ["a"], ["b"])
        legitimate, message = compare_reports(before, after)
        assert legitimate is False
        assert "ABSTRACTION REFUSED" in message
        assert "b" in message

    def test_a_swap_that_holds_the_rate_but_loses_a_boundary_is_refused(self) -> None:
        """The rate is an aggregate; a lost boundary is still a lost boundary."""

        before = self.report(0.5, ["a"], ["b"])
        after = self.report(0.5, ["b"], ["a"])
        legitimate, message = compare_reports(before, after)
        assert legitimate is False
        assert "a" in message

    def test_a_baseline_regression_shows_up_as_its_own_verdict(self, tmp_path: Path) -> None:
        spec_dir = make_spec_dir(tmp_path)
        report = run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog(),
            runner=kill_all,
            root=tmp_path,
            baseline={"kill_rate": 1.0},
            warn=False,
        )
        assert report.verdict == VERDICT_PASS  # 1.0 is not below 1.0

        regressed = run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog(),
            runner=runner_killing("m-alpha", "m-beta", "m-type"),  # 0.75
            root=tmp_path,
            baseline={"kill_rate": 1.0},
            warn=False,
        )
        assert regressed.verdict == VERDICT_REGRESSED
        assert regressed.ok is False
        assert regressed.exit_code == EXIT_BELOW_FLOOR


# ---------------------------------------------------------------------------
# The live catalog for THIS repository
# ---------------------------------------------------------------------------


class TestThisRepositorysCatalogCoversItsOwnBoundaries:
    """These run against the real specs/current, so they fail the moment a
    port or invariant is added without a matching mutant."""

    spec_dir = REPO_ROOT / "specs" / "current"

    def test_the_real_catalog_covers_every_real_boundary(self) -> None:
        catalog, _ = load_catalog(self.spec_dir / "kill_mutants.toml")
        missing = missing_boundaries(catalog, required_boundaries(self.spec_dir))
        assert missing == [], f"declared boundaries with no seeded fault: {missing}"

    def test_the_real_catalog_has_one_mutant_per_port_and_per_invariant(self) -> None:
        catalog, _ = load_catalog(self.spec_dir / "kill_mutants.toml")
        required = required_boundaries(self.spec_dir)
        # MF-023: 19 -> 20. The Internal/External split added ExternalInvariant
        # (channel well-formedness), which External.cfg checks in addition to
        # the 14 inherited ones. The count moved because the MODEL gained a
        # real property, and the catalog was extended to match rather than the
        # obligation being trimmed to fit.
        assert len(required) == 20, "5 declared ports + 15 invariants (14 inherited + ExternalInvariant)"
        assert len(catalog) >= len(required)

    def test_the_real_catalog_declares_no_suppressions(self) -> None:
        _, suppressions = load_catalog(self.spec_dir / "kill_mutants.toml")
        assert suppressions == []

    def test_every_real_mutant_pattern_still_applies_exactly_once(self) -> None:
        """Guards against a mutant going stale as production code moves."""

        catalog, _ = load_catalog(self.spec_dir / "kill_mutants.toml")
        stale = []
        for mutant in catalog:
            target = REPO_ROOT / mutant.path
            if not target.is_file():
                stale.append((mutant.id, "missing file", mutant.path))
                continue
            count = target.read_text(encoding="utf-8").count(mutant.find)
            if count != 1:
                stale.append((mutant.id, f"pattern occurs {count} times", mutant.path))
        assert stale == [], f"stale mutants: {stale}"

    def test_every_real_mutant_names_a_variable_that_exists_in_the_model(self) -> None:
        """MF-023: the model is now the DECOMPOSED views, so a mutant's
        refine_variable must name a variable of Internal or of External.

        The union is the right check rather than either view alone: a mutant
        points at the variable whose representation is too abstract, and after
        the split those variables are distributed across two views. Requiring
        both views to be read also means a mutant naming a variable that was
        deleted from BOTH still fails, which is the property this test exists
        for.
        """
        catalog, _ = load_catalog(self.spec_dir / "kill_mutants.toml")
        variables: set[str] = set()
        for module, terminator in (("Internal.tla", "InternalVars =="),
                                   ("External.tla", "ExternalVars ==")):
            tla = (self.spec_dir / module).read_text(encoding="utf-8")
            block = tla.split("VARIABLES", 1)[1].split(terminator, 1)[0]
            variables |= {
                line.strip().rstrip(",") for line in block.splitlines() if line.strip()
            }
        for mutant in catalog:
            assert mutant.refine_variable in variables, (
                f"{mutant.id} points at variable {mutant.refine_variable!r}, "
                f"which is declared in neither Internal.tla nor External.tla"
            )

    def test_seeding_every_real_mutant_leaves_the_tree_byte_identical(self) -> None:
        catalog, _ = load_catalog(self.spec_dir / "kill_mutants.toml")
        for mutant in catalog:
            target = REPO_ROOT / mutant.path
            before = target.read_bytes()
            with seeded(mutant, REPO_ROOT):
                assert target.read_bytes() != before, f"{mutant.id} changed nothing"
            assert target.read_bytes() == before, f"{mutant.id} did not restore {mutant.path}"

    def test_every_real_python_mutant_still_parses(self) -> None:
        """Mutants must fail BEHAVIORALLY, not with a SyntaxError.

        A mutant that breaks the parse is killed by every case trivially and
        proves nothing about the representation.
        """

        import ast

        catalog, _ = load_catalog(self.spec_dir / "kill_mutants.toml")
        for mutant in catalog:
            if not mutant.path.endswith(".py"):
                continue
            target = REPO_ROOT / mutant.path
            with seeded(mutant, REPO_ROOT):
                ast.parse(target.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# CLI surface
# ---------------------------------------------------------------------------


class TestCliSurface:
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/run_kill_test.py", *args],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )

    def test_list_boundaries_reports_full_coverage_for_this_repo(self) -> None:
        result = self.run_cli("--target", "specs/current", "--list-boundaries")
        assert result.returncode == EXIT_PASS, result.stderr
        assert "NO MUTANT" not in result.stdout
        # MF-023: 19 -> 20. The decomposition added ExternalInvariant, the
        # catalog went incomplete the moment it did, and the resolution was to
        # SEED the fault rather than to drop the invariant or waive the
        # boundary. See the note in specs/current/kill_mutants.toml.
        assert "20/20 declared boundaries carry a seeded fault." in result.stdout

    def test_a_missing_corpus_command_is_refused_not_defaulted(self) -> None:
        """Without a corpus there is nothing to kill mutants with, so
        reporting a rate would be fabricating one."""

        result = self.run_cli("--target", "specs/current")
        assert result.returncode == EXIT_USAGE
        assert "--corpus-command is required" in result.stderr

    def test_a_missing_catalog_is_refused(self, tmp_path: Path) -> None:
        result = self.run_cli("--target", "specs/current", "--catalog", str(tmp_path / "nope.toml"))
        assert result.returncode == EXIT_USAGE
        assert "no mutant catalog" in result.stderr

    def test_compare_mode_refuses_a_dropped_kill_rate(self, tmp_path: Path) -> None:
        before = tmp_path / "before.json"
        after = tmp_path / "after.json"
        before.write_text(
            json.dumps({"kill_rate": 1.0, "kill_matrix": [{"mutant_id": "a", "killed": True}]})
        )
        after.write_text(
            json.dumps({"kill_rate": 0.0, "kill_matrix": [{"mutant_id": "a", "killed": False}]})
        )
        result = self.run_cli("--compare", str(before), str(after))
        assert result.returncode == 1
        assert "ABSTRACTION REFUSED" in result.stdout


# ---------------------------------------------------------------------------
# The control run
# ---------------------------------------------------------------------------


class TestTheControlRun:
    """The experiment needs a control.

    "Killed" means "the corpus run failed", so a corpus that already fails on
    correct code kills every mutant trivially and scores a perfect, meaningless
    1.0. This is not hypothetical -- the first real run of the worked
    distributed_history kill test scored 7/7 exactly this way, every "kill"
    being one unrelated pre-existing effect-oracle failure.
    """

    def test_a_red_control_refuses_rather_than_scoring(self, tmp_path: Path) -> None:
        spec_dir = make_spec_dir(tmp_path)
        report = run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog(),
            runner=runner_killing("m-alpha", "m-beta", "m-type", "m-holds", control_green=False),
            root=tmp_path,
            warn=False,
        )
        assert report.verdict == VERDICT_NO_CONTROL
        assert report.ok is False
        assert report.exit_code == EXIT_USAGE

    def test_a_red_control_computes_no_kill_rate(self, tmp_path: Path) -> None:
        """Not 1.0. That number would have been maximally flattering and
        completely uninformative."""

        spec_dir = make_spec_dir(tmp_path)
        report = run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog(),
            runner=runner_killing("m-alpha", "m-beta", "m-type", "m-holds", control_green=False),
            root=tmp_path,
            warn=False,
        )
        assert report.kill_rate is None

    def test_a_red_control_seeds_no_mutants_at_all(self, tmp_path: Path) -> None:
        spec_dir = make_spec_dir(tmp_path)
        seen: list[str] = []

        def runner(mutant: Mutant | None) -> tuple[bool, list[str], str]:
            if mutant is None:
                return True, [], "control failed"
            seen.append(mutant.id)
            return True, [], ""

        run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog(),
            runner=runner,
            root=tmp_path,
            warn=False,
        )
        assert seen == []

    def test_the_control_dominates_a_below_floor_verdict(self, tmp_path: Path) -> None:
        """Different remedy, so a different verdict: fix the corpus, then
        measure. Nothing has been learned about the representation."""

        spec_dir = make_spec_dir(tmp_path)
        report = run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog(),
            runner=runner_killing(control_green=False),
            root=tmp_path,
            warn=False,
        )
        assert report.verdict == VERDICT_NO_CONTROL
        assert "CONTROL FAILED" in report.summary()

    def test_the_control_result_is_recorded_in_the_evidence(self, tmp_path: Path) -> None:
        spec_dir = make_spec_dir(tmp_path)
        report = run_kill_test(
            spec_dir=spec_dir,
            catalog=full_catalog(),
            runner=kill_all,
            root=tmp_path,
            warn=False,
        )
        payload = report.to_dict(full_catalog())
        assert payload["control_green"] is True

    def test_there_is_no_flag_that_skips_the_control(self) -> None:
        import argparse

        from scripts.run_kill_test import add_arguments

        parser = argparse.ArgumentParser()
        add_arguments(parser)
        registered = {
            option for action in parser._actions for option in action.option_strings
        }
        assert not (registered & {"--skip-control", "--no-control", "--assume-green"})


# ---------------------------------------------------------------------------
# Per-component scoping
# ---------------------------------------------------------------------------


class TestPerComponentScoping:
    """A repository with two models has two kill tests, not one blended one.

    Scoping must narrow only the coverage OBLIGATION -- never what is measured.
    """

    def two_model_dir(self, tmp_path: Path) -> Path:
        spec_dir = make_spec_dir(tmp_path, cfg="SPECIFICATION S\nINVARIANT InternalOne\n")
        (spec_dir / "External.cfg").write_text(
            "SPECIFICATION S\nINVARIANT ExternalOne\n", encoding="utf-8"
        )
        (spec_dir / "MC.cfg").unlink()
        (spec_dir / "Internal.cfg").write_text(
            "SPECIFICATION S\nINVARIANT InternalOne\n", encoding="utf-8"
        )
        return spec_dir

    def test_the_strict_default_requires_every_config(self, tmp_path: Path) -> None:
        spec_dir = self.two_model_dir(tmp_path)
        refs = {ref for kind, ref in required_boundaries(spec_dir) if kind == "invariant"}
        assert refs == {"InternalOne", "ExternalOne"}

    def test_scoping_narrows_the_obligation(self, tmp_path: Path) -> None:
        spec_dir = self.two_model_dir(tmp_path)
        refs = {
            ref
            for kind, ref in required_boundaries(spec_dir, ["Internal.cfg"])
            if kind == "invariant"
        }
        assert refs == {"InternalOne"}

    def test_scoping_does_not_reduce_what_is_measured(self, tmp_path: Path) -> None:
        """Every mutant still runs, so an out-of-scope survivor still reports."""

        spec_dir = self.two_model_dir(tmp_path)
        catalog = [
            make_mutant("m-alpha", "port", "alpha"),
            make_mutant("m-beta", "port", "beta"),
            make_mutant("m-internal", "invariant", "InternalOne"),
            make_mutant("m-external", "invariant", "ExternalOne"),
        ]
        report = run_kill_test(
            spec_dir=spec_dir,
            catalog=catalog,
            runner=runner_killing("m-alpha", "m-beta", "m-internal"),
            root=tmp_path,
            cfg_names=["Internal.cfg"],
            warn=False,
        )
        assert report.total == 4, "all four mutants ran despite the narrowed obligation"
        assert {o.mutant_id for o in report.survivors} == {"m-external"}

    def test_scoping_to_a_nonexistent_config_is_refused(self, tmp_path: Path) -> None:
        spec_dir = self.two_model_dir(tmp_path)
        with pytest.raises(KillTestCatalogError, match="no such model config"):
            required_boundaries(spec_dir, ["Nope.cfg"])

    def test_the_inline_invariant_form_is_parsed(self, tmp_path: Path) -> None:
        """`INVARIANT Foo` and the `INVARIANTS` block must both work.

        Missing one would silently shrink the required set and hand back a
        kill test that looked complete while covering nothing.
        """

        spec_dir = self.two_model_dir(tmp_path)
        assert declared_invariants(spec_dir / "Internal.cfg") == ["InternalOne"]
