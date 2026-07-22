from __future__ import annotations

import json
import inspect
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from typing import get_type_hints


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "generated"))

import run_experiment


class ReminderWorkerExperimentTests(unittest.TestCase):
    def test_provider_bindings_match_every_generated_protocol_signature(self) -> None:
        from reminder_contract.ports import ClockPort, NotifierPort, OutboxPort, QueuePort
        from providers import ClockBinding, NotifierBinding, OutboxBinding, QueueBinding

        for protocol, binding in (
            (ClockPort, ClockBinding),
            (QueuePort, QueueBinding),
            (OutboxPort, OutboxBinding),
            (NotifierPort, NotifierBinding),
        ):
            for method_name, expected in protocol.__dict__.items():
                if method_name.startswith("_") or not inspect.isfunction(expected):
                    continue
                with self.subTest(port=protocol.__name__, method=method_name):
                    actual = getattr(binding, method_name)
                    expected_parameters = list(inspect.signature(expected).parameters.values())[1:]
                    actual_parameters = list(inspect.signature(actual).parameters.values())[1:]
                    self.assertEqual(
                        [(parameter.name, parameter.kind) for parameter in actual_parameters],
                        [(parameter.name, parameter.kind) for parameter in expected_parameters],
                    )
                    self.assertEqual(get_type_hints(actual), get_type_hints(expected))

    def test_generated_contract_is_typed_and_fallback_reproducible(self) -> None:
        from reminder_contract.ports import ClockPort, NotifierPort, QueuePort
        from reminder_contract.types import QueueMutation, ReadClock, SendMessage

        signatures = {
            "clock.now": (inspect.signature(ClockPort.now), ReadClock, int),
            "queue.acknowledge": (
                inspect.signature(QueuePort.acknowledge),
                QueueMutation,
                None,
            ),
            "notifier.send": (
                inspect.signature(NotifierPort.send),
                SendMessage,
                str,
            ),
        }
        for label, (signature, command_type, result_type) in signatures.items():
            with self.subTest(signature=label):
                self.assertEqual(list(signature.parameters), ["self", "command"])
                self.assertIs(signature.parameters["command"].annotation, command_type)
                self.assertIs(signature.return_annotation, result_type)

        committed = ROOT / "generated" / "reminder_contract"

        def source_tree(path: Path) -> dict[str, bytes]:
            return {
                source.name: source.read_bytes()
                for source in sorted(path.iterdir())
                if source.is_file()
            }

        with tempfile.TemporaryDirectory(prefix="reminder-contract-repro-") as temporary:
            temporary_root = Path(temporary)
            for label, python_args in (
                ("active-environment", []),
                ("stdlib-fallback", ["-S"]),
            ):
                output = temporary_root / label
                completed = subprocess.run(
                    [
                        sys.executable,
                        *python_args,
                        str(REPO_ROOT / "scripts" / "generate_python.py"),
                        str(ROOT / "specs" / "program_model" / "spec_manifest.yaml"),
                        "--out",
                        str(output),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    timeout=30,
                )
                self.assertEqual(
                    completed.returncode,
                    0,
                    completed.stdout + completed.stderr,
                )
                self.assertEqual(
                    source_tree(output / "reminder_contract"),
                    source_tree(committed),
                    f"generated contract drifted under {label}",
                )

    def test_preregistration_and_generated_action_coverage_are_fixed(self) -> None:
        run_experiment.validate_preregistration()
        cases = run_experiment.generated_cases()
        self.assertEqual(
            [case.input.action for case in cases],
            list(run_experiment.EXPECTED_ACTIONS),
        )
        self.assertEqual(len(cases), 7)

    def test_one_iteration_runs_through_actual_effect_runner_and_cleans_up(self) -> None:
        with tempfile.TemporaryDirectory(prefix="reminder-test-") as temporary:
            root = Path(temporary)
            trace = root / "trace.jsonl"
            cleanup = root / "cleanup.jsonl"
            environment = os.environ.copy()
            environment["REMINDER_TRACE_LOG"] = str(trace)
            environment["REMINDER_CLEANUP_LOG"] = str(cleanup)
            environment.pop("REMINDER_MUTANT", None)
            completed = subprocess.run(
                run_experiment.runner_command(fuzz_runs=1),
                cwd=ROOT,
                env=environment,
                text=True,
                capture_output=True,
                timeout=30,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            traces = run_experiment.read_jsonl(trace)
            cleanups = run_experiment.read_jsonl(cleanup)
            self.assertEqual(len(traces), 7)
            self.assertEqual(len(cleanups), 7)
            self.assertTrue(all(row["registry_empty"] for row in cleanups))
            self.assertGreater(
                len({row["bundle"]["concretization_seed"] for row in traces}),
                1,
            )

    def test_hand_written_baseline_is_separate_and_has_green_control(self) -> None:
        with tempfile.TemporaryDirectory(prefix="reminder-baseline-") as temporary:
            baseline = run_experiment.run_baseline(Path(temporary))
        self.assertTrue(baseline["control_green"])
        self.assertEqual(baseline["total"], 12)
        from providers import active_point_count

        self.assertEqual(active_point_count(), 0)

    def test_external_cases_cross_the_process_boundary(self) -> None:
        sys.path.insert(0, str(ROOT / "generated" / "cases" / "testgraph"))
        from external_adapter import ReminderProcessAdapter
        from reminder_external_cases.cases import CASES

        adapter = ReminderProcessAdapter()
        with tempfile.TemporaryDirectory(prefix="reminder-process-") as temporary:
            root = Path(temporary)
            for case in CASES:
                point = root / case.name
                point.mkdir()
                result = adapter.run(case, point)
                self.assertEqual(result.output, case.output)
                self.assertEqual(result.after, case.after)

    def test_bypass_probe_restores_socket_patch(self) -> None:
        original = socket.socket.connect
        probes = run_experiment.capability_probes()
        self.assertIs(socket.socket.connect, original)
        self.assertFalse(probes["direct_network_bypass"]["outbound_socket_succeeded"])
        self.assertTrue(probes["direct_network_bypass"]["passive_attempt_detected"])
        self.assertFalse(probes["direct_clock_bypass"]["provider_intercepted"])


if __name__ == "__main__":
    unittest.main()
