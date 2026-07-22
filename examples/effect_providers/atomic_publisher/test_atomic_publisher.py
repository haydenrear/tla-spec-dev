#!/usr/bin/env python3
from __future__ import annotations

import importlib
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[2]
SPEC_DIR = PROJECT_ROOT / "specs" / "program_model"
GENERATED_DIR = SPEC_DIR / "generated"
INTERNAL_PARENT = GENERATED_DIR / "cases" / "spec-unit"
EXTERNAL_PARENT = GENERATED_DIR / "cases" / "testgraph"
for root in (GENERATED_DIR, INTERNAL_PARENT, EXTERNAL_PARENT, PROJECT_ROOT, REPO_ROOT):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


class AtomicPublisherExperimentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.previous_mutant = os.environ.pop("ATOMIC_PUBLISHER_MUTANT", None)

    def tearDown(self) -> None:
        if self.previous_mutant is not None:
            os.environ["ATOMIC_PUBLISHER_MUTANT"] = self.previous_mutant
        else:
            os.environ.pop("ATOMIC_PUBLISHER_MUTANT", None)

    def test_generated_internal_cases_preserve_seven_actions_and_outcomes(self) -> None:
        cases = importlib.import_module("atomic_internal_cases.cases").CASES
        pairs = {(case.input.action, case.after["outcome"]) for case in cases}
        self.assertEqual(len(cases), 7)
        self.assertEqual(len({case.input.action for case in cases}), 7)
        self.assertEqual(len(pairs), 7)
        for case in cases:
            self.assertEqual(case.before["scenario"], case.after["outcome"])

    def test_generated_filesystem_port_accepts_project_binding(self) -> None:
        from atomic_publisher_contract.ports import FilesystemPort
        from atomic_internal_cases.cases import CASES
        from application import AtomicPublisher, PublishRequest
        from providers import AtomicFilesystemBinding
        from spec_double_compiler.effects import derive_effect_seed
        from spec_double_compiler.runtime import EffectProviderContext

        case = CASES[0]
        with tempfile.TemporaryDirectory(prefix="atomic-binding-test-") as raw_root:
            context = EffectProviderContext(
                port_name="FilesystemPort",
                action=case.input.action,
                case=case,
                work_dir=Path(raw_root),
                iteration=3,
                root_seed=20260721,
                derived_seed=derive_effect_seed(20260721, case.name, 3, "FilesystemPort"),
            )
            binding = AtomicFilesystemBinding(context)
            with binding as entered:
                self.assertIsInstance(entered, FilesystemPort)
                representative = entered.representative
                output = AtomicPublisher(entered).publish(
                    PublishRequest(
                        final_path=representative["final_path"],
                        stage_path=representative["stage_path"],
                        record_id=representative["record_id"],
                        payload=representative["new_payload"],
                        expected_revision=0,
                    )
                )
                self.assertEqual(output, case.output)
            self.assertFalse(list(Path(raw_root).rglob("provider-root")))

    def test_real_temporary_filesystem_conformance_covers_every_outcome(self) -> None:
        from conformance import run_real_filesystem_conformance

        evidence = run_real_filesystem_conformance()
        self.assertEqual(evidence["verdict"], "green")
        self.assertEqual(len(evidence["outcomes"]), 7)
        self.assertTrue(all(row["matched"] for row in evidence["outcomes"]))
        self.assertTrue(all(not row["actual_stage_exists"] for row in evidence["outcomes"]))

    def test_replace_failure_removes_stage_before_harness_teardown(self) -> None:
        from application import AtomicPublisher
        from conformance import RealFilesystem

        with tempfile.TemporaryDirectory(prefix="atomic-stage-cleanup-test-") as raw_root:
            filesystem = RealFilesystem(Path(raw_root), "replace_failure")
            output = AtomicPublisher(filesystem).publish(filesystem.request())
            self.assertEqual(output["status"], "replace_error")
            self.assertFalse(Path(filesystem.stage_path).exists())
            self.assertEqual(filesystem.events[-1], "delete_stage")

    def test_external_cli_cases_match_output_and_projected_state(self) -> None:
        from atomic_external_cases.cases import CASES
        from external_adapter import AtomicPublisherCliAdapter, AtomicPublisherCliProjector
        from spec_double_compiler.runtime import AdapterCaseContext, ProjectedStateAssertionContext

        for case in CASES:
            with self.subTest(action=case.input.action), tempfile.TemporaryDirectory(
                prefix="atomic-external-test-"
            ) as raw_root:
                work_dir = Path(raw_root)
                result = AtomicPublisherCliAdapter().run(case, work_dir=work_dir)
                self.assertEqual(result.output, case.output)
                context = ProjectedStateAssertionContext(
                    kind="atomic-publisher-cli",
                    case=case,
                    work_dir=work_dir,
                    mapping=None,
                    shared={},
                    result=result,
                )
                self.assertEqual(AtomicPublisherCliProjector().observe(context), case.after)

    def test_fixed_catalog_smoke_kills_all_mutants_and_replays_exactly(self) -> None:
        with tempfile.TemporaryDirectory(prefix="atomic-evidence-test-") as raw_root:
            evidence_path = Path(raw_root) / "evidence.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "run_experiment.py"),
                    "--skip-regenerate",
                    "--repetitions",
                    "1",
                    "--run-label",
                    "focused-test",
                    "--evidence",
                    str(evidence_path),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=60,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            self.assertEqual(evidence["decision"]["verdict"], "go")
            mutants = evidence["repetitions"][0]["mutants"]
            self.assertEqual(sum(row["verdict"] == "killed" for row in mutants), 12)
            self.assertTrue(all(row["replay_exact"] for row in mutants))
            self.assertTrue(all(row["replay_returncode"] != 0 for row in mutants))
            self.assertTrue(all(row["replay_failure_exact"] for row in mutants))
            self.assertTrue(all(row["replay_provider_exit_clean"] for row in mutants))
            self.assertTrue(all(row["replay_transcript_exact"] for row in mutants))
            self.assertEqual(evidence["cleanup_isolation"]["verdict"], "green")
            for relative, digest in evidence["source_provenance"].items():
                self.assertEqual(
                    hashlib.sha256((PROJECT_ROOT / relative).read_bytes()).hexdigest(),
                    digest,
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
