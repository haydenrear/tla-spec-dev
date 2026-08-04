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
    BOUNDARY_EFFECT_TYPES,
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
    OutOfProcessObservation,
    UnobservableTarget,
    WorkingTreeObserver,
    SKIP_DECLINED,
    SKIP_ERROR,
    SKIP_NOT_RUNNABLE,
    SKIP_UNBOUND,
    SkippedCase,
    adapter_skip_reason,
    assess_target_observability,
    corpus_import_roots,
    diff_effects,
    ensure_import_roots,
    execute_corpus,
    load_effect_declarations,
    reset_case_work_dir,
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


# ---------------------------------------------------------------------------
# MF-033: make the effect oracle OBSERVE out-of-process work.
#
# MF-028 measured that every adapter in this repository shells out, so the
# in-process sandbox saw only the spawn and the verdict was `unobservable`
# forever. WorkingTreeObserver reaches across the boundary via a snapshot diff.
# These tests pin two things at once: (a) the child's filesystem effects are now
# genuinely observed and diffed against ports; (b) MF-027 polarity SURVIVES --
# an unwatched axis, and a spawn with no out-of-process evidence at all, still
# refuse. The observation is positive evidence, never a downgrade flag.
# ---------------------------------------------------------------------------


class TestWorkingTreeObserverSeesOutOfProcessWrites:
    """The observer recovers a CHILD process's real filesystem effects."""

    def test_child_subprocess_write_is_observed_out_of_process(self, tmp_path):
        """The exact blindness MF-028 recorded, now seen.

        `test_a_child_that_writes_is_proof_the_boundary_is_real` proves the
        in-process sandbox cannot see this write. Here the WorkingTreeObserver,
        watching the same root, does.
        """
        watched = tmp_path / "workspace"
        watched.mkdir()
        target = watched / "written-by-child.txt"
        recorder = EffectRecorder()
        with WorkingTreeObserver(watched, recorder, action="Act", case="c1"):
            subprocess.run(
                [sys.executable, "-c", f"open({str(target)!r}, 'w').write('x')"], check=True
            )
        assert target.exists(), "the child really wrote out-of-process"
        writes = [e for e in recorder.effects if e.type == "filesystem.write"]
        assert any(str(target) in e.target for e in writes), (
            "the observer recovered the child's write across the process boundary"
        )
        assert all("out-of-process" in e.detail for e in writes)

    def test_child_delete_is_observed_as_filesystem_delete(self, tmp_path):
        watched = tmp_path / "workspace"
        watched.mkdir()
        victim = watched / "doomed.txt"
        victim.write_text("here")
        recorder = EffectRecorder()
        with WorkingTreeObserver(watched, recorder, action="Act", case="c1"):
            subprocess.run([sys.executable, "-c", f"import os; os.remove({str(victim)!r})"], check=True)
        assert not victim.exists()
        deletes = [e for e in recorder.effects if e.type == "filesystem.delete"]
        assert any(str(victim) in e.target for e in deletes)

    def test_observer_records_its_coverage_as_positive_evidence(self, tmp_path):
        watched = tmp_path / "workspace"
        watched.mkdir()
        recorder = EffectRecorder()
        with WorkingTreeObserver(watched, recorder, action="Act", case="c1"):
            (watched / "a.txt").write_text("x")
        assert len(recorder.out_of_process) == 1
        obs = recorder.out_of_process[0]
        assert obs.covered_types == frozenset({"filesystem.write", "filesystem.delete"})
        assert obs.case == "c1" and obs.observed_count >= 1

    def test_unchanged_tree_records_zero_effects_but_still_a_coverage_record(self, tmp_path):
        watched = tmp_path / "workspace"
        watched.mkdir()
        (watched / "pre-existing.txt").write_text("untouched")
        recorder = EffectRecorder()
        with WorkingTreeObserver(watched, recorder, action="Act", case="c1"):
            pass
        assert recorder.effects == []
        assert recorder.out_of_process[0].observed_count == 0


class TestOutOfProcessObservationFeedsTheDiff:
    """Observed child effects are diffed against ports like any other."""

    def test_observed_child_write_can_match_a_declared_port(self):
        """A child write inside a declared target exercises the port.

        This is the mechanism by which a shelling-out adapter stops leaving all
        its ports dead: the child's writes are now real observations.
        """
        decls = load_effect_declarations(declarations(workspace=WRITE_PORT))
        report = diff_effects(
            decls,
            [
                ObservedEffect(
                    type="filesystem.write", target="/tmp/workspace/child-wrote.txt",
                    action="Act", case="c1", detail="out-of-process:working-tree-diff",
                ),
            ],
            cases=["c1"],
        )
        assert report.dead_surface == [], "the port was exercised by the observed child write"
        assert report.gaps == []

    def test_observed_child_write_outside_a_port_is_a_gap(self):
        """The oracle's whole point: an undeclared child effect is a gap.

        Out-of-process observation makes a real advisory SIGNAL possible -- here
        a gap the sandbox alone could never have seen.
        """
        decls = load_effect_declarations(declarations(workspace=WRITE_PORT))
        report = diff_effects(
            decls,
            [
                ObservedEffect(
                    type="filesystem.write", target="/etc/passwd",
                    action="Act", case="c1", detail="out-of-process:working-tree-diff",
                ),
            ],
            cases=["c1"],
            out_of_process=[
                OutOfProcessObservation(
                    case="c1", action="Act", observer="working-tree-diff",
                    covered_types=frozenset({"filesystem.write", "filesystem.delete"}),
                ),
            ],
        )
        assert len(report.gaps) == 1


class TestPolaritySurvivesOutOfProcessObservation:
    """MF-027 polarity must not weaken when we make more things observable.

    The whole risk of this ticket: in teaching the oracle to see child writes,
    do not let it start passing runtimes it still cannot see. Every test here
    asserts a refusal SURVIVES.
    """

    def _spawn_report(self, out_of_process=()):
        decls = load_effect_declarations(
            declarations(proc={"type": "process.spawn", "target": "*"})
        )
        return diff_effects(
            decls,
            [ObservedEffect(type="process.spawn", target="java -jar x.jar", action="Act", case="c1")],
            cases=["c1"],
            out_of_process=list(out_of_process),
        )

    def test_spawn_with_no_out_of_process_evidence_is_still_unobservable(self):
        """The MF-027 default is untouched: no evidence => full refusal."""
        report = self._spawn_report()
        assert report.verdict == VERDICT_UNOBSERVABLE and report.ok is False
        assert report.unobservable[0].kind == "process-boundary"
        assert "invisible to this run" in report.unobservable[0].reason

    def test_filesystem_only_coverage_still_leaves_network_unobservable(self):
        """The load-bearing test: observing the filesystem does NOT certify the network.

        A working-tree diff covers filesystem.write/delete. The child could still
        open a socket the diff cannot see, so the verdict STAYS unobservable and
        the residual is named precisely.
        """
        report = self._spawn_report(
            out_of_process=[
                OutOfProcessObservation(
                    case="c1", action="Act", observer="working-tree-diff",
                    covered_types=frozenset({"filesystem.write", "filesystem.delete"}),
                )
            ]
        )
        assert report.verdict == VERDICT_UNOBSERVABLE and report.ok is False
        reason = report.unobservable[0].reason
        assert "filesystem.write" in reason, "names what WAS observed"
        assert "network.connect" in reason and "network.http" in reason, "names the residual"

    def test_only_total_coverage_of_every_axis_discharges_the_boundary(self):
        """Symmetric control: a spawn is fully accounted for ONLY when every axis is proven.

        This is the structural boundary of the rule -- and a filesystem-only
        observer never reaches it, which is exactly why this repo stays
        unobservable. The rule discharges on positive coverage of ALL axes, not
        on a flag.
        """
        report = self._spawn_report(
            out_of_process=[
                OutOfProcessObservation(
                    case="c1", action="Act", observer="omniscient",
                    covered_types=frozenset(BOUNDARY_EFFECT_TYPES),
                )
            ]
        )
        assert report.unobservable == [], "every axis proven => nothing left to refuse"
        assert report.verdict == VERDICT_CLEAN

    def test_coverage_for_a_different_case_does_not_discharge_this_spawn(self):
        """Evidence is scoped: a diff of case c2 says nothing about c1's child."""
        report = self._spawn_report(
            out_of_process=[
                OutOfProcessObservation(
                    case="c2", action="Other", observer="working-tree-diff",
                    covered_types=frozenset(BOUNDARY_EFFECT_TYPES),
                )
            ]
        )
        assert report.verdict == VERDICT_UNOBSERVABLE and report.ok is False

    def test_out_of_process_is_evidence_not_a_flag(self):
        """diff_effects grows an evidence parameter, never a suppression one.

        The forbidden names from TestNothingDowngrades stay forbidden; the new
        parameter carries OBSERVATIONS, and empty observations discharge nothing.
        """
        import inspect

        params = set(inspect.signature(diff_effects).parameters)
        assert "out_of_process" in params
        for forbidden in ("allow_unobservable", "ignore_unobservable", "assume_observable", "skip_observability"):
            assert forbidden not in params
        # Empty evidence is not a downgrade: the spawn is as unobservable as ever.
        assert self._spawn_report(out_of_process=[]).verdict == VERDICT_UNOBSERVABLE

    def test_a_runtime_refusal_is_not_touched_by_filesystem_coverage(self):
        """A JVM adapter is refused at the RUNTIME edge; observing files nearby
        does not make its own in-JVM work observable."""
        decls = load_effect_declarations(declarations(workspace=WRITE_PORT))
        sandbox = EffectSandbox(root=Path(tempfile.mkdtemp()) / "sb")
        sandbox.require_observable("com.example:JvmAdapter", resolved=object(), runtime="jvm")
        report = diff_effects(
            decls,
            [ObservedEffect(type="filesystem.write", target="/tmp/workspace/a", action="Act", case="c1")],
            cases=["c1"],
            unobservable=sandbox.recorder.unobservable,
            out_of_process=[
                OutOfProcessObservation(
                    case="c1", action="Act", observer="working-tree-diff",
                    covered_types=frozenset(BOUNDARY_EFFECT_TYPES),
                )
            ],
        )
        assert report.verdict == VERDICT_UNOBSERVABLE and report.ok is False

    def test_end_to_end_real_spawn_with_observer_sees_the_write_but_still_refuses(self, tmp_path):
        """The full MF-033 story in one test.

        A real child writes a file; the WorkingTreeObserver recovers the write
        out-of-process and it matches a declared port (so the port is no longer
        dead). But the child could have opened a socket the diff cannot see, so
        the run STILL refuses -- verdict unobservable, residual named. Observed
        more; certified nothing unseen.
        """
        watched = tmp_path / "specs"
        watched.mkdir()
        child_file = watched / "program_model.tla"
        decls = load_effect_declarations(
            declarations(
                spec_tree={"type": "filesystem.write", "target": "**/specs/**"},
                proc={"type": "process.spawn", "target": "*"},
            )
        )
        recorder = EffectRecorder()
        with EffectSandbox(root=tmp_path / "sb", recorder=recorder) as sandbox:
            with sandbox.observe(action="Act", case="c1"):
                with WorkingTreeObserver(watched, recorder, action="Act", case="c1"):
                    subprocess.run(
                        [sys.executable, "-c", f"open({str(child_file)!r}, 'w').write('MODULE')"],
                        check=True,
                    )
        report = diff_effects(
            decls,
            recorder.effects,
            cases=["c1"],
            unobservable=recorder.unobservable,
            out_of_process=recorder.out_of_process,
        )
        # The child's write was observed out-of-process and matched spec_tree.
        assert any(
            e.type == "filesystem.write" and str(child_file) in e.target for e in report.observed
        )
        spec_tree_dead = any(d.port.port == "spec_tree" for d in report.dead_surface)
        assert not spec_tree_dead, "the observed child write exercised the declared port"
        # ...and yet the run still refuses, because the spawn's network axis is unseen.
        assert report.verdict == VERDICT_UNOBSERVABLE and report.ok is False
        assert any(f.kind == "process-boundary" for f in report.unobservable)

    def test_evidence_json_surfaces_the_out_of_process_observation(self, tmp_path):
        report = self._spawn_report(
            out_of_process=[
                OutOfProcessObservation(
                    case="c1", action="Act", observer="working-tree-diff",
                    covered_types=frozenset({"filesystem.write", "filesystem.delete"}),
                    observed_count=3,
                )
            ]
        )
        payload = json.loads(report.write(tmp_path / "e.json").read_text(encoding="utf-8"))
        assert payload["out_of_process_observations"][0]["observer"] == "working-tree-diff"
        assert payload["out_of_process_observations"][0]["observed_count"] == 3
        assert payload["verdict"] == VERDICT_UNOBSERVABLE


# ---------------------------------------------------------------------------
# HP-04. Three defects found by RUNNING the oracle against this repository's own
# model for the first time in the project's history -- not by reading it, which
# four MF-026 audit rounds had already done.
# ---------------------------------------------------------------------------


class TestSkippedCasesAreReportedNotFatal:
    """RC-02-DF-03. The run does not die on an adapter it cannot drive."""

    def test_an_apply_only_adapter_is_skipped_with_a_reason(self):
        class ApplyOnly:
            def apply(self):  # no run(case, work_dir): nothing can drive it
                return {}

        skip = adapter_skip_reason(ApplyOnly(), object())
        assert skip is not None
        kind, reason = skip
        assert kind == SKIP_NOT_RUNNABLE
        assert "apply()" in reason and "run(case, work_dir)" in reason

    def test_an_adapter_that_declines_the_case_is_a_different_skip(self):
        """"cannot be driven at all" and "declined this input" are not the same fact."""

        class Picky:
            def can_run(self, case):
                return False, "wrong phase"

            def run(self, case, work_dir=None):  # pragma: no cover - never called
                raise AssertionError("must not run")

        skip = adapter_skip_reason(Picky(), object())
        assert skip == (SKIP_DECLINED, "wrong phase")

    def test_a_runnable_adapter_is_not_skipped(self):
        class Fine:
            def run(self, case, work_dir=None):
                return None

        assert adapter_skip_reason(Fine(), object()) is None

    def test_a_skip_does_not_change_the_verdict(self):
        """The epic's no_new_gates_rule: a skip is a report, never a refusal."""
        decls = load_effect_declarations(declarations(workspace=WRITE_PORT))
        report = diff_effects(
            decls,
            [ObservedEffect(type="filesystem.write", target="/a/workspace/f", action="Act", case="c1")],
            cases=["c1"],
            skipped=[
                SkippedCase(case="c2", action="Other", adapter="m:A", reason="apply()-only", kind=SKIP_NOT_RUNNABLE)
            ],
            executed_actions=["Act"],
        )
        assert report.verdict == VERDICT_CLEAN
        assert report.ok is True
        # ...and yet it is impossible to read the report without seeing it.
        assert "1 skipped case(s)" in report.summary()
        assert "SKIPPED CASES" in report.render()
        assert "apply()-only" in report.render()

    def test_action_reach_is_answered_by_the_run(self):
        report = diff_effects(
            load_effect_declarations(declarations(workspace=WRITE_PORT)),
            [],
            cases=["c1"],
            skipped=[SkippedCase(case="c2", action="Skipped", adapter="m:A", reason="apply()-only")],
            offered_actions=["Act", "Skipped"],
            executed_actions=["Act"],
        )
        reach = report.action_reach()
        assert "1 of 2 action(s) in this corpus DRIVEN" in reach
        assert "Skipped: Skipped" in reach
        payload = report.to_dict()["action_reach"]
        assert payload["executed"] == ["Act"] and payload["skipped"] == ["Skipped"]

    def test_a_port_whose_every_action_was_skipped_is_not_called_dead(self):
        """An absence of evidence is not evidence of absence.

        Nine of seventeen adapters in this repository's own model are
        apply()-only, so before this annotation the oracle's dead-port list
        mixed proven dead surface with ports nothing had been in a position to
        exercise. On the shipped model that was 7 of the 9 reported dead ports.
        """
        block = declarations(evidence=WRITE_PORT, other=dict(WRITE_PORT))
        block["effects"]["actions"] = {"Act": ["other"], "Skipped": ["evidence"]}
        decls = load_effect_declarations(block)
        report = diff_effects(
            decls,
            [],
            cases=["c1"],
            skipped=[SkippedCase(case="c2", action="Skipped", adapter="m:A", reason="apply()-only")],
            executed_actions=["Act"],
        )
        by_port = {dead.port.port: dead for dead in report.dead_surface}
        assert by_port["evidence"].blocked_by == ("Skipped",)
        assert "UNEXERCISED PORT (NOT proven dead)" in by_port["evidence"].describe()
        # `other`'s action DID run and still did not exercise it: that is real
        # dead surface and softening it would be the same mistake inverted.
        assert by_port["other"].blocked_by == ()
        assert "DEAD MODEL SURFACE" in by_port["other"].describe()
        # The verdict is untouched either way.
        assert report.verdict == VERDICT_DEAD_SURFACE and report.ok is False


class TestImportRootsForAScaffoldedProject:
    """RC-02-DF-02. The oracle could not read a project the CLI itself creates."""

    def test_the_target_spec_dir_leads_the_import_roots(self, tmp_path):
        spec_dir = tmp_path / "specs" / "current"
        spec_dir.mkdir(parents=True)
        roots = corpus_import_roots(spec_dir)
        assert roots[0] == spec_dir.resolve()
        # The toolchain root carries spec_double_compiler, which every
        # scaffolded adapters.py imports.
        assert (Path(__file__).resolve().parents[1]) in roots

    def test_ensure_import_roots_puts_them_in_front(self, tmp_path):
        first = tmp_path / "one"
        second = tmp_path / "two"
        first.mkdir()
        second.mkdir()
        saved = list(sys.path)
        try:
            added = ensure_import_roots([first, second])
            assert set(added) == {str(first), str(second)}
            assert sys.path[0] == str(first), "the spec dir must win over anything already importable"
        finally:
            sys.path[:] = saved

    def test_the_scaffolded_convention_imports_with_no_pythonpath(self, tmp_path):
        """The exact shape of `case_adapters.toml`: a bare module path."""
        spec_dir = tmp_path / "specs" / "current"
        spec_dir.mkdir(parents=True)
        (spec_dir / "hp04_production_adapters.py").write_text(
            "class Adapter:\n    def run(self, case, work_dir=None):\n        return None\n",
            encoding="utf-8",
        )
        saved = list(sys.path)
        try:
            ensure_import_roots(corpus_import_roots(spec_dir))
            from spec_double_compiler.runtime import load_object

            assert load_object("hp04_production_adapters:Adapter") is not None
        finally:
            sys.path[:] = saved
            sys.modules.pop("hp04_production_adapters", None)


class TestTheWorkDirIsResetPerCase:
    """MF026-R4-F-01. 20 / 15 / 14 gaps over an identical corpus and tree."""

    def test_a_stale_case_dir_is_emptied(self, tmp_path):
        work = tmp_path / "work"
        stale = work / "case_1"
        stale.mkdir(parents=True)
        (stale / "target-repo").mkdir()
        (stale / "target-repo" / "manifest.yaml").write_text("from a previous run", encoding="utf-8")

        fresh = reset_case_work_dir(work, "case_1")

        assert fresh.exists() and list(fresh.iterdir()) == []

    def test_sibling_case_dirs_and_the_parent_survive(self, tmp_path):
        """Only the directory this case is about to use is emptied."""
        work = tmp_path / "work"
        (work / "case_1").mkdir(parents=True)
        (work / "case_2").mkdir(parents=True)
        keep = work / "case_2" / "keep.txt"
        keep.write_text("x", encoding="utf-8")
        (work / "notes.txt").write_text("caller's own file", encoding="utf-8")

        reset_case_work_dir(work, "case_1")

        assert keep.exists()
        assert (work / "notes.txt").exists()

    def test_the_report_states_whether_the_scratch_was_reset(self):
        report = diff_effects(
            load_effect_declarations(declarations(workspace=WRITE_PORT)),
            [ObservedEffect(type="filesystem.write", target="/a/workspace/f", action="Act", case="c1")],
            cases=["c1"],
            executed_actions=["Act"],
            work_dir="/tmp/w",
            work_dir_reset=True,
        )
        assert "each case started from an EMPTY directory" in report.render()
        assert report.to_dict()["determinism"]["work_dir_reset_per_case"] is True


class TestExecuteCorpusEndToEnd:
    """All three defects at once, on a project shaped like a scaffolded one."""

    @staticmethod
    def _project(tmp_path):
        spec_dir = tmp_path / "specs" / "current"
        (spec_dir / "cases_pkg").mkdir(parents=True)
        # `case_adapters.toml` names adapters as BARE module paths -- the
        # convention `tla-spec-dev scaffold` writes. Nothing here adjusts
        # sys.path; that is the point of the test.
        (spec_dir / "case_adapters.toml").write_text(
            '[adapters.Writes]\nadapter = "hp04_adapters:WritesAdapter"\n'
            '[adapters.ApplyOnly]\nadapter = "hp04_adapters:ApplyOnlyAdapter"\n',
            encoding="utf-8",
        )
        (spec_dir / "hp04_adapters.py").write_text(
            "from pathlib import Path\n"
            "\n"
            "\n"
            "class WritesAdapter:\n"
            "    def run(self, case, work_dir=None):\n"
            "        # Exactly the shape that made the oracle non-reproducible:\n"
            "        # an adapter materializing its own before-state writes on a\n"
            "        # cold run and finds the file already there on a warm one.\n"
            "        target = Path(work_dir) / 'target-repo' / 'manifest.yaml'\n"
            "        target.parent.mkdir(parents=True, exist_ok=True)\n"
            "        if not target.exists():\n"
            "            target.write_text('scaffolded', encoding='utf-8')\n"
            "        return None\n"
            "\n"
            "\n"
            "class ApplyOnlyAdapter:\n"
            "    def apply(self):\n"
            "        return {}\n",
            encoding="utf-8",
        )
        (spec_dir / "cases_pkg" / "__init__.py").write_text(
            "from .cases import CASES\n\n__all__ = ['CASES']\n", encoding="utf-8"
        )
        (spec_dir / "cases_pkg" / "cases.py").write_text(
            "from dataclasses import dataclass, field\n"
            "\n"
            "\n"
            "@dataclass(frozen=True)\n"
            "class Case:\n"
            "    name: str\n"
            "    labels: frozenset\n"
            "    view: str = 'internal'\n"
            "\n"
            "\n"
            "CASES = [\n"
            "    Case(name='case_1', labels=frozenset({'Writes'})),\n"
            "    Case(name='case_2', labels=frozenset({'ApplyOnly'})),\n"
            "    Case(name='case_3', labels=frozenset({'Unbound'})),\n"
            "]\n",
            encoding="utf-8",
        )
        return spec_dir

    def _run(self, spec_dir, work_dir):
        recorder = EffectRecorder()
        execution = execute_corpus(
            spec_dir=spec_dir,
            cases_dirs=[spec_dir / "cases_pkg"],
            mapping_path=spec_dir / "case_adapters.toml",
            work_dir=work_dir,
            recorder=recorder,
        )
        block = declarations(spec_tree={"type": "filesystem.write", "target": "**/target-repo/**"})
        block["effects"]["actions"] = {"Writes": ["spec_tree"]}
        return diff_effects(
            load_effect_declarations(block),
            recorder.effects,
            cases=execution.cases,
            unobservable=recorder.unobservable,
            skipped=recorder.skipped,
            offered_actions=execution.offered_actions,
            executed_actions=execution.executed_actions,
            work_dir=str(work_dir),
            work_dir_reset=True,
        )

    def test_runs_a_scaffolded_project_and_reports_what_it_could_not_run(self, tmp_path):
        spec_dir = self._project(tmp_path)
        saved = list(sys.path)
        try:
            report = self._run(spec_dir, tmp_path / "work")
        finally:
            sys.path[:] = saved
            for name in ("hp04_adapters", "cases_pkg", "cases_pkg.cases"):
                sys.modules.pop(name, None)

        # RC-02-DF-02: it imported `hp04_adapters` with no caller help.
        assert report.cases == ["case_1"]
        # RC-02-DF-03: the apply()-only adapter did not abort the run, and the
        # unbound action is named rather than passed over in silence.
        kinds = {skip.action: skip.kind for skip in report.skipped}
        assert kinds == {"ApplyOnly": SKIP_NOT_RUNNABLE, "Unbound": SKIP_UNBOUND}
        assert "1 of 3 action(s) in this corpus DRIVEN" in report.action_reach()

    def test_two_runs_over_an_identical_corpus_are_identical(self, tmp_path):
        """MF026-R4-F-01, the whole ticket in one assertion.

        The measured defect was 20 / 15 / 14 gaps across three runs of an
        identical corpus on an identical tree -- a 43% spread on the number any
        claim would rest on. The comparison here is the WHOLE report, not just
        the count, because two runs that agree on a total while disagreeing on
        which effects produced it are still not reproducible.
        """
        spec_dir = self._project(tmp_path)
        work = tmp_path / "work"
        saved = list(sys.path)
        try:
            first = self._run(spec_dir, work).to_dict()
            second = self._run(spec_dir, work).to_dict()
            third = self._run(spec_dir, work).to_dict()
        finally:
            sys.path[:] = saved
            for name in ("hp04_adapters", "cases_pkg", "cases_pkg.cases"):
                sys.modules.pop(name, None)

        assert first == second == third
        # Stable on a NONZERO gap count. Agreeing on zero would be a weaker
        # claim: the defect was a gap that appeared on the cold run and vanished
        # on the warm one, so the count has to be reproducible while it is a
        # number somebody would cite.
        assert len(first["gaps"]) == 1
        # The warm runs really did re-execute the write -- this is not agreement
        # by way of both runs observing nothing.
        assert first["observed_effects"], "the adapter's write must be observed on every run"
        assert any(
            effect["target"].endswith("manifest.yaml") for effect in first["observed_effects"]
        ), "the write that used to appear only on a cold run must appear on every run"


class TestPathOpenIsObserved:
    """HP-04: `path.open("a")` used to cross the boundary unobserved.

    Found by running the oracle over HP-01's A/B reference rather than by
    reading the sandbox. The reference appends its durable ledger with
    `self._ledger_path.open("a")`; the sandbox patched `builtins.open`,
    `Path.write_text` and `Path.write_bytes` but not `Path.open`, so the
    idiomatic append was silent while the equivalent `open(path, "a")` was
    recorded. The oracle then "killed" the ordering NEGATIVE CONTROL, whose
    mutation swaps that append for a `Path.write_text` -- it detected a change
    of API, not a change of behavior.
    """

    def test_append_through_path_open_is_recorded(self, tmp_path):
        sandbox = EffectSandbox(root=tmp_path / "sb")
        target = tmp_path / "ledger.txt"
        with sandbox, sandbox.observe(action="Act", case="c1"):
            with target.open("a", encoding="utf-8") as handle:
                handle.write("COMMIT t1 1\n")
        assert any(
            effect.type == "filesystem.write" and effect.target.endswith("ledger.txt")
            for effect in sandbox.recorder.for_case("c1")
        )

    def test_reading_through_path_open_is_not_a_write(self, tmp_path):
        target = tmp_path / "ledger.txt"
        target.write_text("x", encoding="utf-8")
        sandbox = EffectSandbox(root=tmp_path / "sb")
        with sandbox, sandbox.observe(action="Act", case="c1"):
            with target.open("r", encoding="utf-8") as handle:
                handle.read()
        assert sandbox.recorder.for_case("c1") == []

    def test_the_two_idioms_produce_the_same_crossing(self, tmp_path):
        """The point of the fix: observation must not depend on which was used."""
        def crossings(write) -> set[tuple[str, str]]:
            sandbox = EffectSandbox(root=tmp_path / "sb")
            with sandbox, sandbox.observe(action="Act", case="c"):
                write(tmp_path / "ledger.txt")
            return {(e.type, e.target) for e in sandbox.recorder.for_case("c")}

        via_path = crossings(lambda p: p.open("a", encoding="utf-8").close())
        via_builtin = crossings(lambda p: open(p, "a", encoding="utf-8").close())
        assert via_path == via_builtin


class TestAnAdapterThatRaisesIsCollectedNotFatal:
    """HP-04: one bad case used to hide every case after it.

    Distinguished from a SKIP on purpose. A skip means the adapter said it could
    not take the case and enters no verdict; an error means it said it could,
    then blew up, and the run FAILS -- which it already did before HP-04, by
    dying with a traceback and writing no report at all. Collecting it is a
    better report of the same failure, not a relaxed one.
    """

    def test_the_error_fails_the_run_and_names_the_case(self):
        report = diff_effects(
            load_effect_declarations(declarations(workspace=WRITE_PORT)),
            [ObservedEffect(type="filesystem.write", target="/a/workspace/f", action="Act", case="c1")],
            cases=["c1"],
            skipped=[
                SkippedCase(
                    case="c2",
                    action="Act",
                    adapter="m:A",
                    reason="NotImplementedError: load the TLA `before` state",
                    kind=SKIP_ERROR,
                )
            ],
            executed_actions=["Act"],
        )
        assert report.verdict == "adapter_error"
        assert report.ok is False
        assert [skip.case for skip in report.errored] == ["c2"]
        assert "ADAPTER ERRORS" in report.render()
        assert "RAISED on at least one case and are measured by nothing" in report.action_reach()
        assert report.to_dict()["adapter_errors"][0]["case"] == "c2"

    def test_a_declared_incapacity_is_still_only_a_report(self):
        """The two must not collapse into each other."""
        report = diff_effects(
            load_effect_declarations(declarations(workspace=WRITE_PORT)),
            [ObservedEffect(type="filesystem.write", target="/a/workspace/f", action="Act", case="c1")],
            cases=["c1"],
            skipped=[SkippedCase(case="c2", action="Other", adapter="m:A", reason="apply()-only")],
            executed_actions=["Act"],
        )
        assert report.errored == []
        assert report.ok is True

    def test_later_cases_still_run_after_one_raises(self, tmp_path):
        recorder = EffectRecorder()
        spec_dir = tmp_path / "specs" / "current"
        (spec_dir / "cases_pkg").mkdir(parents=True)
        (spec_dir / "case_adapters.toml").write_text(
            '[adapters.Boom]\nadapter = "hp04_boom:BoomAdapter"\n'
            '[adapters.Fine]\nadapter = "hp04_boom:FineAdapter"\n',
            encoding="utf-8",
        )
        (spec_dir / "hp04_boom.py").write_text(
            "from pathlib import Path\n\n\n"
            "class BoomAdapter:\n"
            "    def run(self, case, work_dir=None):\n"
            "        raise NotImplementedError('implement me')\n\n\n"
            "class FineAdapter:\n"
            "    def run(self, case, work_dir=None):\n"
            "        (Path(work_dir) / 'out.txt').write_text('x', encoding='utf-8')\n",
            encoding="utf-8",
        )
        (spec_dir / "cases_pkg" / "__init__.py").write_text(
            "from .cases import CASES\n\n__all__ = ['CASES']\n", encoding="utf-8"
        )
        (spec_dir / "cases_pkg" / "cases.py").write_text(
            "from dataclasses import dataclass\n\n\n"
            "@dataclass(frozen=True)\n"
            "class Case:\n"
            "    name: str\n"
            "    labels: frozenset\n\n\n"
            "CASES = [\n"
            "    Case(name='c1', labels=frozenset({'Boom'})),\n"
            "    Case(name='c2', labels=frozenset({'Fine'})),\n"
            "]\n",
            encoding="utf-8",
        )
        saved = list(sys.path)
        try:
            execution = execute_corpus(
                spec_dir=spec_dir,
                cases_dirs=[spec_dir / "cases_pkg"],
                mapping_path=spec_dir / "case_adapters.toml",
                work_dir=tmp_path / "work",
                recorder=recorder,
            )
        finally:
            sys.path[:] = saved
            for name in ("hp04_boom", "cases_pkg", "cases_pkg.cases"):
                sys.modules.pop(name, None)

        assert [skip.kind for skip in recorder.skipped] == [SKIP_ERROR]
        # The case AFTER the raise ran, and its effect was observed.
        assert execution.cases == ["c1", "c2"]
        assert any(effect.case == "c2" for effect in recorder.effects)
