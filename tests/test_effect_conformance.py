"""MF-013: effect conformance harness.

The load-bearing tests here are the two the 2026-07-18 degeneracy audit
demanded:

* :class:`TestUndeclaredEffectFails` -- an undeclared observed effect FAILS.
  Recording the gap is not an alternative to failing on it.
* :class:`TestNothingSuppressesAGap` -- the INVERSE test. A recorded
  justification, annotation, or manifest entry does NOT prevent the failure.
  There is deliberately no test that suppression works, because suppression no
  longer exists. These tests are the regression guard against reintroducing it.

See ``references/architecture_tractability.md`` "No Degenerate Escapes" and
``references/modular_fuzzing.md`` oracle 3.
"""

from __future__ import annotations

import copy
import inspect
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from effect_conformance import (  # noqa: E402
    SUPPRESSION_KEYS,
    VERDICT_CLEAN,
    VERDICT_DEAD_SURFACE,
    VERDICT_GAPS,
    VERDICT_UNOBSERVABLE,
    EffectConformanceReport,
    EffectDeclarationError,
    EffectRecorder,
    EffectSandbox,
    ObservedEffect,
    UnobservableTarget,
    assess_target_observability,
    diff_effects,
    load_effect_declarations,
)


def declarations(**ports):
    """Build an effects block with one action, ``Act``, owning every port.

    Deep-copied so that a test which annotates a port (several below do, to
    prove the annotation changes nothing) cannot leak that mutation into the
    next test through the shared ``WRITE_PORT`` literal.
    """
    return copy.deepcopy(
        {
            "effects": {
                "components": {"C": {"ports": ports}},
                "actions": {"Act": list(ports)},
            }
        }
    )


WRITE_PORT = {"type": "filesystem.write", "target": "**/workspace/**"}


class TestDeclarationSchema:
    def test_parses_ports_and_actions(self):
        decls = load_effect_declarations(declarations(workspace=WRITE_PORT))
        assert decls.all_qualified() == ["C.workspace"]
        assert [d.port for d in decls.declared_for_action("Act")] == ["workspace"]

    def test_absent_block_is_empty_not_an_error(self):
        assert load_effect_declarations(None).ports == {}

    def test_port_without_type_is_rejected(self):
        with pytest.raises(EffectDeclarationError, match="declares no type"):
            load_effect_declarations(declarations(workspace={"target": "**"}))

    def test_port_without_target_is_rejected(self):
        with pytest.raises(EffectDeclarationError, match="declares no target"):
            load_effect_declarations(declarations(workspace={"type": "filesystem.write"}))

    def test_unobservable_type_is_rejected(self):
        """A port whose type the sandbox cannot observe is unverifiable."""
        with pytest.raises(EffectDeclarationError, match="unobservable type"):
            load_effect_declarations(declarations(p={"type": "telepathy", "target": "*"}))

    def test_action_naming_unknown_port_is_rejected(self):
        block = declarations(workspace=WRITE_PORT)
        block["effects"]["actions"]["Act"] = ["nope"]
        with pytest.raises(EffectDeclarationError, match="unknown port"):
            load_effect_declarations(block)


class TestSandboxObservation:
    def test_records_filesystem_write(self, tmp_path):
        sandbox = EffectSandbox(root=tmp_path / "sb")
        with sandbox, sandbox.observe(action="Act", case="c1"):
            (sandbox.root / "out.txt").write_text("hi", encoding="utf-8")
        effects = sandbox.recorder.for_case("c1")
        assert any(e.type == "filesystem.write" and e.target.endswith("out.txt") for e in effects)

    def test_records_write_via_builtin_open(self, tmp_path):
        sandbox = EffectSandbox(root=tmp_path / "sb")
        with sandbox, sandbox.observe(action="Act", case="c1"):
            with open(sandbox.root / "viaopen.txt", "w", encoding="utf-8") as handle:
                handle.write("x")
        assert any(e.target.endswith("viaopen.txt") for e in sandbox.recorder.for_case("c1"))

    def test_read_is_not_an_effect(self, tmp_path):
        target = tmp_path / "readme.txt"
        target.write_text("data", encoding="utf-8")
        sandbox = EffectSandbox(root=tmp_path / "sb")
        with sandbox, sandbox.observe(action="Act", case="c1"):
            target.read_text(encoding="utf-8")
        assert sandbox.recorder.for_case("c1") == []

    def test_records_delete(self, tmp_path):
        victim = tmp_path / "gone.txt"
        victim.write_text("x", encoding="utf-8")
        sandbox = EffectSandbox(root=tmp_path / "sb")
        with sandbox, sandbox.observe(action="Act", case="c1"):
            victim.unlink()
        assert any(e.type == "filesystem.delete" for e in sandbox.recorder.for_case("c1"))

    def test_records_process_spawn(self, tmp_path):
        sandbox = EffectSandbox(root=tmp_path / "sb")
        with sandbox, sandbox.observe(action="Act", case="c1"):
            subprocess.run([sys.executable, "-c", "pass"], check=True)
        assert any(e.type == "process.spawn" for e in sandbox.recorder.for_case("c1"))

    def test_escaping_the_sandbox_root_is_still_observed(self, tmp_path):
        """Containment is not concealment: a write outside the root is recorded."""
        outside = tmp_path / "outside.txt"
        sandbox = EffectSandbox(root=tmp_path / "sb")
        with sandbox, sandbox.observe(action="Act", case="c1"):
            outside.write_text("escaped", encoding="utf-8")
        assert any(e.target.endswith("outside.txt") for e in sandbox.recorder.for_case("c1"))

    def test_fake_transport_records_without_network(self, tmp_path):
        sandbox = EffectSandbox(root=tmp_path / "sb")
        with sandbox, sandbox.observe(action="Act", case="c1"):
            sandbox.transport("orders").send("https://example.invalid/orders", {"id": 1})
        assert any(e.type == "network.http" for e in sandbox.recorder.for_case("c1"))

    def test_patches_are_removed_on_exit(self, tmp_path):
        import builtins

        original = builtins.open
        sandbox = EffectSandbox(root=tmp_path / "sb")
        with sandbox:
            assert builtins.open is not original
        assert builtins.open is original

    def test_patches_are_removed_even_when_body_raises(self, tmp_path):
        import builtins

        original = builtins.open
        sandbox = EffectSandbox(root=tmp_path / "sb")
        with pytest.raises(RuntimeError):
            with sandbox:
                raise RuntimeError("adapter blew up")
        assert builtins.open is original


class TestUndeclaredEffectFails:
    """THE core rule. An undeclared observed effect FAILS the run."""

    def test_declared_effect_is_clean(self):
        decls = load_effect_declarations(declarations(workspace=WRITE_PORT))
        report = diff_effects(
            decls,
            [ObservedEffect(type="filesystem.write", target="/tmp/workspace/a.txt", action="Act", case="c1")],
            cases=["c1"],
        )
        assert report.ok
        assert report.verdict == VERDICT_CLEAN
        assert report.gaps == []

    def test_undeclared_effect_is_recorded_AND_fails(self):
        decls = load_effect_declarations(declarations(workspace=WRITE_PORT))
        report = diff_effects(
            decls,
            [
                ObservedEffect(type="filesystem.write", target="/tmp/workspace/a.txt", action="Act", case="c1"),
                # /etc/passwd is outside every declared target pattern.
                ObservedEffect(type="filesystem.write", target="/etc/passwd", action="Act", case="c1"),
            ],
            cases=["c1"],
        )
        # Recorded...
        assert len(report.gaps) == 1
        assert "/etc/passwd" in report.gaps[0].describe()
        # ...AND failing. Recording is not an alternative to failing.
        assert report.ok is False
        assert report.verdict == VERDICT_GAPS

    def test_effect_of_wrong_type_on_a_declared_target_is_a_gap(self):
        """The port is typed: a delete does not ride in on a write declaration."""
        decls = load_effect_declarations(declarations(workspace=WRITE_PORT))
        report = diff_effects(
            decls,
            [ObservedEffect(type="filesystem.delete", target="/tmp/workspace/a.txt", action="Act", case="c1")],
            cases=["c1"],
        )
        assert report.ok is False
        assert report.verdict == VERDICT_GAPS

    def test_effect_from_an_action_that_declares_no_port_is_a_gap(self):
        """Ports are per action, so a port declared for Act does not cover Other."""
        decls = load_effect_declarations(declarations(workspace=WRITE_PORT))
        report = diff_effects(
            decls,
            [ObservedEffect(type="filesystem.write", target="/tmp/workspace/a.txt", action="Other", case="c1")],
            cases=["c1"],
        )
        assert report.ok is False
        assert report.verdict == VERDICT_GAPS

    def test_end_to_end_sandbox_to_gap(self, tmp_path):
        """Observation and diff joined: an undisclosed write becomes a failure."""
        decls = load_effect_declarations(declarations(workspace=WRITE_PORT))
        sandbox = EffectSandbox(root=tmp_path / "workspace")
        with sandbox, sandbox.observe(action="Act", case="c1"):
            (sandbox.root / "declared.txt").write_text("ok", encoding="utf-8")
            (tmp_path / "undisclosed.txt").write_text("surprise", encoding="utf-8")
        report = diff_effects(decls, sandbox.recorder.effects, cases=["c1"])
        assert report.ok is False
        assert any("undisclosed.txt" in gap.describe() for gap in report.gaps)


class TestNothingSuppressesAGap:
    """The INVERSE test: the regression guard against the withdrawn escape.

    Out-of-contract justifications were withdrawn on 2026-07-18. These tests
    assert that every shape the old escape could take -- a manifest
    justification table, a per-port annotation, a per-action waiver -- leaves
    the failure exactly where it was. There is intentionally no test asserting
    that suppression works.
    """

    def _report_with(self, block_mutator):
        block = declarations(workspace=WRITE_PORT)
        block_mutator(block)
        decls = load_effect_declarations(block)
        return diff_effects(
            decls,
            [ObservedEffect(type="filesystem.write", target="/etc/passwd", action="Act", case="c1")],
            cases=["c1"],
        )

    def test_baseline_gap_fails(self):
        report = self._report_with(lambda block: None)
        assert report.ok is False and len(report.gaps) == 1

    def test_manifest_level_justification_table_does_not_suppress(self):
        report = self._report_with(
            lambda block: block["effects"].update(
                {
                    "justifications": [
                        {"target": "/etc/passwd", "reason": "legacy audit log, accepted by review"}
                    ]
                }
            )
        )
        assert report.ok is False, "a manifest justification table must not suppress the gap"
        assert len(report.gaps) == 1
        assert "effects.justifications" in report.ignored_suppression_keys

    def test_port_level_annotation_does_not_suppress(self):
        report = self._report_with(
            lambda block: block["effects"]["components"]["C"]["ports"]["workspace"].update(
                {"out_of_contract": True, "justification": "known deviation, documented in ADR-7"}
            )
        )
        assert report.ok is False, "a port annotation must not suppress the gap"
        assert len(report.gaps) == 1

    def test_action_level_waiver_does_not_suppress(self):
        report = self._report_with(
            lambda block: block["effects"].update({"waiver": {"Act": ["/etc/passwd"]}})
        )
        assert report.ok is False, "an action waiver must not suppress the gap"
        assert len(report.gaps) == 1

    def test_allow_undeclared_flag_in_manifest_does_not_suppress(self):
        report = self._report_with(lambda block: block["effects"].update({"allow_undeclared": True}))
        assert report.ok is False, "an allow_undeclared entry must not suppress the gap"
        assert len(report.gaps) == 1

    def test_suppression_attempts_are_reported_not_silently_dropped(self):
        """A silently ignored waiver would let an author believe it worked."""
        report = self._report_with(
            lambda block: block["effects"].update({"justification": "because"})
        )
        assert report.ignored_suppression_keys == ["effects.justification"]
        assert "IGNORED SUPPRESSION ATTEMPT" in report.render()
        assert report.ok is False

    def test_verdict_is_identical_with_and_without_a_justification(self):
        without = self._report_with(lambda block: None)
        with_just = self._report_with(
            lambda block: block["effects"].update({"justification": "accepted risk"})
        )
        assert without.verdict == with_just.verdict == VERDICT_GAPS
        assert without.ok == with_just.ok is False


class TestDeadModelSurface:
    """A declared port no case exercises is removed or exercised -- not explained."""

    def test_never_observed_port_is_dead_surface_and_fails(self):
        decls = load_effect_declarations(declarations(workspace=WRITE_PORT))
        report = diff_effects(decls, [], cases=["c1"])
        assert report.ok is False
        assert report.verdict == VERDICT_DEAD_SURFACE
        assert [d.port.qualified for d in report.dead_surface] == ["C.workspace"]

    def test_exercising_the_port_resolves_dead_surface(self):
        decls = load_effect_declarations(declarations(workspace=WRITE_PORT))
        report = diff_effects(
            decls,
            [ObservedEffect(type="filesystem.write", target="/tmp/workspace/a.txt", action="Act", case="c1")],
            cases=["c1"],
        )
        assert report.dead_surface == []
        assert report.ok

    def test_removing_the_port_resolves_dead_surface(self):
        report = diff_effects(load_effect_declarations(declarations()), [], cases=["c1"])
        assert report.dead_surface == []
        assert report.ok

    def test_prose_does_not_resolve_dead_surface(self):
        block = declarations(workspace=WRITE_PORT)
        block["effects"]["components"]["C"]["ports"]["workspace"]["justification"] = (
            "unobserved because the corpus does not yet reach this branch"
        )
        report = diff_effects(load_effect_declarations(block), [], cases=["c1"])
        assert report.ok is False, "prose must not resolve dead model surface"
        assert len(report.dead_surface) == 1


class TestSuppressionScanIsScopedToTheEffectsBlock:
    """MF-011's per-variable ``justification:`` table is a different mechanism.

    It records why each VARIABLE earns its place (invariants / effects /
    kill_tests) and is legitimate. Only suppression keys inside the ``effects``
    block are reported. Conflating the two would flag every manifest in the
    repository and train readers to ignore the warning.
    """

    def test_mf011_variable_justification_table_is_not_flagged(self):
        manifest = declarations(workspace=WRITE_PORT)
        manifest["justification"] = {
            "setup_phase": {"invariants": ["TypeInvariant"], "effects": [], "kill_tests": []}
        }
        assert load_effect_declarations(manifest).ignored_suppression_keys == []

    def test_suppression_inside_the_effects_block_is_flagged(self):
        manifest = declarations(workspace=WRITE_PORT)
        manifest["effects"]["justification"] = "waived"
        assert load_effect_declarations(manifest).ignored_suppression_keys == ["effects.justification"]


class TestShippedManifestDeclarations:
    """The declarations this ticket ships must actually parse and be valid.

    Reads the PROMOTED manifest at ``specs/current``, not the ticket-local
    copy: ticket directories are consumed by promotion, so a test pinned to
    ``specs/tickets/MF-013`` passes before close and fails after it.
    """

    def test_promoted_manifest_effects_block_is_well_formed(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
        from extract_spec_manifest import load_manifest

        path = Path(__file__).resolve().parents[1] / "specs" / "current" / "spec_manifest.yaml"
        if not path.is_file():
            pytest.skip("no promoted spec_manifest.yaml")
        decls = load_effect_declarations(load_manifest(path))
        assert decls.ports, "shipped manifest declares no effect ports"
        assert decls.ignored_suppression_keys == [], "shipped manifest must carry no suppression keys"
        for action, ports in decls.action_ports.items():
            for port in ports:
                assert port in decls.ports, f"{action} names undeclared port {port}"


class TestReportEvidence:
    def test_report_is_writable_as_ticket_evidence(self, tmp_path):
        decls = load_effect_declarations(declarations(workspace=WRITE_PORT))
        report = diff_effects(
            decls,
            [ObservedEffect(type="filesystem.write", target="/etc/passwd", action="Act", case="c1")],
            cases=["c1"],
        )
        path = report.write(tmp_path / "nested" / "effect_conformance.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["verdict"] == VERDICT_GAPS
        assert payload["ok"] is False
        assert payload["gaps"][0]["target"] == "/etc/passwd"
        assert "withdrawn" in payload["suppression_policy"]

    def test_clean_report_is_also_written(self, tmp_path):
        decls = load_effect_declarations(declarations(workspace=WRITE_PORT))
        report = diff_effects(
            decls,
            [ObservedEffect(type="filesystem.write", target="/tmp/workspace/a.txt", action="Act", case="c1")],
            cases=["c1"],
        )
        payload = json.loads(report.write(tmp_path / "clean.json").read_text(encoding="utf-8"))
        assert payload["ok"] is True and payload["verdict"] == VERDICT_CLEAN


# ---------------------------------------------------------------------------
# MF-027: the oracle must refuse targets it cannot observe.
#
# MF-013 shipped correct behavior with a silent boundary: the sandbox patches
# the in-process CPython runtime, so a JVM adapter and a subprocess-delegating
# adapter were both invisible, both produced an empty observation set, and an
# empty observation set read as a clean report. These tests pin the refusal.
# ---------------------------------------------------------------------------


class TestObservabilityAssessment:
    """Observability is granted on evidence, never assumed."""

    def test_resolved_python_object_is_observable(self):
        assessment = assess_target_observability("pkg.mod:Adapter", resolved=object())
        assert assessment.observable is True
        assert assessment.finding() is None

    def test_unresolved_target_is_not_observable(self):
        """No live object => no evidence => refusal. This is the polarity."""
        assessment = assess_target_observability("pkg.mod:Adapter", resolved=None)
        assert assessment.observable is False
        assert "no evidence" in assessment.reason

    def test_declared_non_python_runtime_is_not_observable(self):
        assessment = assess_target_observability(
            "pkg.mod:Adapter", resolved=object(), runtime="jvm"
        )
        assert assessment.observable is False
        assert "jvm" in assessment.reason

    def test_jvm_adapter_reference_is_not_observable(self):
        assessment = assess_target_observability(
            "com.hayden.testgraphsdk:Node", resolved=object(), kind="java"
        )
        assert assessment.observable is False

    def test_jbang_node_is_not_observable(self):
        assessment = assess_target_observability(
            "jbang test_graph/nodes/Verify.java", resolved=object()
        )
        assert assessment.observable is False

    def test_command_string_is_not_a_python_reference(self):
        assessment = assess_target_observability(
            "/usr/bin/env python3 run.py", resolved=object()
        )
        assert assessment.observable is False

    def test_unrecognised_runtime_defaults_to_refusal_not_to_clean(self):
        """The default for something nobody enumerated must be refusal.

        A default of "observable" is what made the original defect silent: any
        runtime the author did not think to list reported green.
        """
        assessment = assess_target_observability(
            "some-target", resolved=None, runtime="brand-new-runtime-9000"
        )
        assert assessment.observable is False


class TestUnobservableTargetFails:
    """An unobservable target FAILS. It never returns a clean report."""

    def _report_for(self, **kwargs):
        decls = load_effect_declarations(declarations(workspace=WRITE_PORT))
        sandbox = EffectSandbox(root=Path(tempfile.mkdtemp()) / "sb")
        sandbox.require_observable("com.example:JvmAdapter", **kwargs)
        return diff_effects(
            decls,
            [ObservedEffect(type="filesystem.write", target="/tmp/workspace/a", action="Act", case="c1")],
            cases=["c1"],
            unobservable=sandbox.recorder.unobservable,
        )

    def test_jvm_target_fails_rather_than_reporting_clean(self):
        """The headline case: a Java adapter in a separate JVM.

        Note the observed effect in the fixture MATCHES the declared port, so
        under MF-013 this exact input produced verdict=clean, ok=True. That is
        the false green MF-027 removes.
        """
        report = self._report_for(resolved=object(), runtime="jvm")
        assert report.ok is False
        assert report.verdict == VERDICT_UNOBSERVABLE
        assert report.gaps == [] and report.dead_surface == []
        assert len(report.unobservable) == 1

    def test_failure_names_why(self):
        report = self._report_for(resolved=object(), runtime="jvm")
        message = report.unobservable[0].describe()
        assert "com.example:JvmAdapter" in message
        assert "jvm" in message
        assert "TARGET NOT OBSERVABLE" in message

    def test_unobservable_outranks_a_clean_diff_in_the_rendered_report(self):
        rendered = self._report_for(resolved=object(), runtime="jvm").render()
        assert "REFUSED" in rendered
        assert "certifies NOTHING" in rendered
        assert "unobservable" in rendered

    def test_unobservable_outranks_gaps_and_dead_surface(self):
        """Precedence: absence of evidence is not a measurement of gaps."""
        decls = load_effect_declarations(declarations(workspace=WRITE_PORT))
        report = diff_effects(
            decls,
            [ObservedEffect(type="filesystem.write", target="/etc/passwd", action="Act", case="c1")],
            cases=["c1"],
            unobservable=[UnobservableTarget(target="x", reason="r")],
        )
        assert report.gaps, "the gap is still recorded"
        assert report.verdict == VERDICT_UNOBSERVABLE
        assert report.ok is False

    def test_evidence_json_records_the_refusal_and_the_scope(self, tmp_path):
        report = self._report_for(resolved=object(), runtime="jvm")
        payload = json.loads(report.write(tmp_path / "e.json").read_text(encoding="utf-8"))
        assert payload["ok"] is False
        assert payload["verdict"] == VERDICT_UNOBSERVABLE
        assert payload["unobservable_targets"][0]["kind"] == "runtime"
        assert "in-process CPython only" in payload["observable_scope"]


class TestSubprocessBoundaryIsAnExplicitFinding:
    """A spawn is a boundary, not a fully-accounted-for effect."""

    def _spawn_report(self, declare_the_port: bool):
        ports = {"workspace": WRITE_PORT}
        if declare_the_port:
            ports["proc"] = {"type": "process.spawn", "target": "*java*"}
        decls = load_effect_declarations(declarations(**ports))
        return diff_effects(
            decls,
            [
                ObservedEffect(type="filesystem.write", target="/tmp/workspace/a", action="Act", case="c1"),
                ObservedEffect(type="process.spawn", target="java -jar tla2tools.jar", action="Act", case="c1"),
            ],
            cases=["c1"],
        )

    def test_spawn_surfaces_as_an_unobservable_finding_naming_the_process(self):
        report = self._spawn_report(declare_the_port=True)
        assert report.unobservable, "the spawn must not be silent"
        finding = report.unobservable[0]
        assert "java -jar tla2tools.jar" in finding.describe()
        assert finding.kind == "process-boundary"

    def test_declaring_a_spawn_port_does_not_silence_the_boundary(self):
        """Declaring "I spawn java" does not say what java then wrote.

        This is the subtle half. The declared port makes the spawn itself
        non-gap, and under MF-013 that was the end of it -- verdict clean.
        The child's own effects were never observed and never mentioned.
        """
        declared = self._spawn_report(declare_the_port=True)
        assert declared.gaps == [], "the spawn matches its declared port"
        assert declared.ok is False, "but the run still refuses"
        assert declared.verdict == VERDICT_UNOBSERVABLE

    def test_undeclared_spawn_is_both_a_gap_and_a_boundary_finding(self):
        report = self._spawn_report(declare_the_port=False)
        assert len(report.gaps) == 1
        assert len(report.unobservable) == 1

    def test_end_to_end_real_spawn_through_the_sandbox(self, tmp_path):
        """Drive a real subprocess through the real patches."""
        decls = load_effect_declarations(
            declarations(proc={"type": "process.spawn", "target": "*"})
        )
        sandbox = EffectSandbox(root=tmp_path / "sb")
        with sandbox, sandbox.observe(action="Act", case="c1"):
            subprocess.run([sys.executable, "-c", "pass"], check=True)
        report = diff_effects(
            decls,
            sandbox.recorder.effects,
            cases=["c1"],
            unobservable=sandbox.recorder.unobservable,
        )
        assert report.verdict == VERDICT_UNOBSERVABLE
        assert report.ok is False
        assert any(sys.executable in f.target for f in report.unobservable)

    def test_a_child_that_writes_is_proof_the_boundary_is_real(self, tmp_path):
        """The child writes a file; the sandbox never sees the write.

        This is the concrete harm: the write below is a real filesystem
        effect that no declared port authorised, and the oracle cannot see
        it. The boundary finding is the honest report of that blindness.
        """
        victim = tmp_path / "written-by-child.txt"
        decls = load_effect_declarations(
            declarations(proc={"type": "process.spawn", "target": "*"})
        )
        sandbox = EffectSandbox(root=tmp_path / "sb")
        with sandbox, sandbox.observe(action="Act", case="c1"):
            subprocess.run(
                [sys.executable, "-c", f"open({str(victim)!r},'w').write('x')"], check=True
            )
        assert victim.exists(), "the child really did write"
        writes = [e for e in sandbox.recorder.effects if e.type == "filesystem.write"]
        assert all(str(victim) not in e.target for e in writes), (
            "the sandbox cannot see the child's write -- that is the gap being declared"
        )
        report = diff_effects(
            decls, sandbox.recorder.effects, cases=["c1"],
            unobservable=sandbox.recorder.unobservable,
        )
        assert report.ok is False and report.verdict == VERDICT_UNOBSERVABLE


class TestNothingDowngradesAnUnobservableVerdict:
    """The regression guard, built exactly as MF-013 built its inverse test.

    Every test asserts the NEGATIVE: that some plausible opt-out does NOT turn
    an unobservable verdict into a pass. There is deliberately no test that an
    opt-out works, because no opt-out exists. The "helpful" instinct here is
    to let a user whose runtime the sandbox cannot support declare their way
    out of a check; that opt-out is the silence this ticket removed.
    """

    def _report_with(self, block_mutator=lambda block: None, **assess):
        block = declarations(workspace=WRITE_PORT)
        block_mutator(block)
        decls = load_effect_declarations(block)
        sandbox = EffectSandbox(root=Path(tempfile.mkdtemp()) / "sb")
        sandbox.require_observable(
            "com.example:JvmAdapter", **{"resolved": object(), "runtime": "jvm", **assess}
        )
        return diff_effects(
            decls,
            [ObservedEffect(type="filesystem.write", target="/tmp/workspace/a", action="Act", case="c1")],
            cases=["c1"],
            unobservable=sandbox.recorder.unobservable,
        )

    def test_baseline_is_a_failure(self):
        report = self._report_with()
        assert report.ok is False and report.verdict == VERDICT_UNOBSERVABLE

    def test_manifest_level_observable_claim_does_not_downgrade(self):
        report = self._report_with(
            lambda block: block["effects"].update({"observable": True})
        )
        assert report.ok is False
        assert "effects.observable" in report.ignored_suppression_keys

    def test_assume_observable_does_not_downgrade(self):
        report = self._report_with(
            lambda block: block["effects"].update({"assume_observable": ["com.example:JvmAdapter"]})
        )
        assert report.ok is False
        assert "effects.assume_observable" in report.ignored_suppression_keys

    def test_port_level_skip_observability_does_not_downgrade(self):
        report = self._report_with(
            lambda block: block["effects"]["components"]["C"]["ports"]["workspace"].update(
                {"skip_observability": True}
            )
        )
        assert report.ok is False

    def test_trusted_runtime_entry_does_not_downgrade(self):
        report = self._report_with(
            lambda block: block["effects"].update({"trusted_runtime": "jvm"})
        )
        assert report.ok is False

    def test_allow_unobservable_flag_does_not_downgrade(self):
        report = self._report_with(
            lambda block: block["effects"].update({"allow_unobservable": True})
        )
        assert report.ok is False

    def test_justification_prose_does_not_downgrade(self):
        report = self._report_with(
            lambda block: block["effects"].update(
                {"justification": "JVM adapters are audited manually every release"}
            )
        )
        assert report.ok is False

    def test_declaring_the_runtime_as_python_does_not_beat_the_reference_shape(self):
        """Lying in the manifest does not create observability."""
        sandbox = EffectSandbox(root=Path(tempfile.mkdtemp()) / "sb")
        sandbox.require_observable(
            "jbang nodes/Verify.java", resolved=object(), runtime="python"
        )
        assert sandbox.recorder.unobservable, "the reference shape still refuses"

    def test_verdict_is_identical_with_and_without_every_suppression_key(self):
        plain = self._report_with()
        loaded = self._report_with(
            lambda block: block["effects"].update(
                {key: True for key in sorted(SUPPRESSION_KEYS)}
            )
        )
        assert plain.verdict == loaded.verdict == VERDICT_UNOBSERVABLE
        assert plain.ok is loaded.ok is False
        assert len(plain.unobservable) == len(loaded.unobservable)

    def test_no_diff_effects_keyword_can_clear_the_finding(self):
        """The API offers no suppression parameter."""
        import inspect

        params = set(inspect.signature(diff_effects).parameters)
        for forbidden in (
            "allow_unobservable",
            "ignore_unobservable",
            "assume_observable",
            "skip_observability",
            "strict",
        ):
            assert forbidden not in params, f"diff_effects must not accept {forbidden}"

    def test_recorder_offers_no_way_to_withdraw_a_refusal(self):
        recorder = EffectRecorder()
        recorder.record_unobservable(UnobservableTarget(target="t", reason="r"))
        for forbidden in ("clear_unobservable", "waive", "waive_unobservable", "suppress"):
            assert not hasattr(recorder, forbidden), f"EffectRecorder must not expose {forbidden}"
        assert len(recorder.unobservable) == 1

    def test_ok_reads_only_the_finding_lists(self):
        """No configuration is consulted by the gate -- structurally."""
        # Strip comments: the prose in this property explains what it refuses
        # to consult, and naming a thing is not consulting it.
        code = "\n".join(
            line.split("#", 1)[0]
            for line in inspect.getsource(EffectConformanceReport.ok.fget).splitlines()
        )
        assert "self.unobservable" in code
        for forbidden in ("config", "flag", "os.environ", "getattr(", "manifest", "if "):
            assert forbidden not in code, f"ok must not consult {forbidden}"

    def test_environment_variables_do_not_downgrade(self, monkeypatch):
        for name in (
            "EFFECT_CONFORMANCE_ALLOW_UNOBSERVABLE",
            "SPEC_DOUBLE_SKIP_OBSERVABILITY",
            "TLA_SPEC_DEV_ASSUME_OBSERVABLE",
        ):
            monkeypatch.setenv(name, "1")
        report = self._report_with()
        assert report.ok is False and report.verdict == VERDICT_UNOBSERVABLE

    def test_cli_exposes_no_downgrade_flag(self):
        """The reporting command must not grow an opt-out flag."""
        source = (
            Path(__file__).resolve().parents[1] / "scripts" / "effect_conformance_report.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "--allow-unobservable",
            "--skip-observability",
            "--assume-observable",
            "--no-observability",
            "--ignore-unobservable",
        ):
            assert forbidden not in source, f"CLI must not offer {forbidden}"
