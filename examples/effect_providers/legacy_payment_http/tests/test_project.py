from __future__ import annotations

import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[2]
CASES_PARENT = PROJECT_ROOT / "generated" / "spec-unit"
CONTRACT_PARENT = PROJECT_ROOT / "specs" / "program_model" / "generated"
for root in (PROJECT_ROOT, REPO_ROOT, CASES_PARENT, CONTRACT_PARENT):
    sys.path.insert(0, str(root))

from payment_effects.adapters import PaymentHttpCaseAdapter  # noqa: E402
from payment_effects.external import PaymentHttpExternalAdapter  # noqa: E402
from payment_effects.provider import patches_are_clean, payment_http_provider  # noqa: E402
from legacy_payment_http_app import authorize_payment  # noqa: E402
from scripts.run_experiment import (  # noqa: E402
    CONTROL_CANONICAL_FIELDS,
    INTERNAL_ACTIONS,
    MUTATION_CANONICAL_FIELDS,
    SOURCE_FILES,
    _canonical_evidence,
    _compress_optional,
    _digest,
    _replay_is_exact,
    _source_provenance,
    _statistics,
)
from spec_double_compiler.effects import derive_effect_seed  # noqa: E402
from spec_double_compiler.runtime import EffectProviderContext  # noqa: E402


class LegacyPaymentHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = list(importlib.import_module("payment_http_internal_cases").CASES)

    def test_generated_action_and_label_gate(self) -> None:
        self.assertEqual({case.input.action for case in self.cases}, INTERNAL_ACTIONS)
        self.assertEqual(len(self.cases), 56)
        self.assertTrue(all(case.input.action in case.labels for case in self.cases))
        coverage = {
            action: sum(case.input.action == action for case in self.cases)
            for action in INTERNAL_ACTIONS
        }
        self.assertEqual(set(coverage.values()), {8})

    def test_generated_payment_http_port_protocol_shape_is_available(self) -> None:
        from payment_http_contract.ports import PaymentHttpPort

        self.assertTrue(getattr(PaymentHttpPort, "_is_protocol", False))
        self.assertTrue(getattr(PaymentHttpPort, "_is_runtime_protocol", False))

    def test_ph05_preserves_initial_key_and_rotates_only_retry(self) -> None:
        keys: list[str | None] = []

        def send(
            _session: requests.Session,
            prepared: requests.PreparedRequest,
            **_kwargs: object,
        ) -> requests.Response:
            keys.append(prepared.headers.get("Idempotency-Key"))
            response = requests.Response()
            response.request = prepared
            response.url = str(prepared.url)
            if len(keys) == 1:
                response.status_code = 503
                document = {"status": "retry"}
            else:
                response.status_code = 200
                document = {
                    "status": "approved",
                    "authorization_reference": "auth-test",
                }
            response._content = json.dumps(document).encode("utf-8")
            response.headers["Content-Type"] = "application/json"
            return response

        with patch.dict(os.environ, {"LEGACY_PAYMENT_MUTANT": "PH-05"}):
            with patch.object(requests.Session, "send", new=send):
                result = authorize_payment(
                    payment_id="pay-test",
                    amount=17,
                    idempotency_key="idem-test",
                )
        self.assertEqual(result.decision, "approved")
        self.assertEqual(keys, ["idem-test", "idem-test-retry-2"])

    def test_replay_acceptance_requires_nonzero_and_same_structured_failure(self) -> None:
        signature = {
            "case": "case-1",
            "iteration": 0,
            "phase": "run",
            "error_type": "ProviderLocalAssertion",
            "detector": "provider_local_assertion",
            "normalized_error": "stable",
        }
        self.assertTrue(
            _replay_is_exact(
                returncode=1,
                transcript_matches=True,
                discovery_failure_signature=signature,
                replay_failure_signature=dict(signature),
            )
        )
        self.assertFalse(
            _replay_is_exact(
                returncode=0,
                transcript_matches=True,
                discovery_failure_signature=signature,
                replay_failure_signature=dict(signature),
            )
        )
        changed = {**signature, "phase": "output_assert"}
        self.assertFalse(
            _replay_is_exact(
                returncode=1,
                transcript_matches=True,
                discovery_failure_signature=signature,
                replay_failure_signature=changed,
            )
        )

    def test_canonical_digest_changes_on_mutation_replay_or_probe_drift(self) -> None:
        control = {field: None for field in CONTROL_CANONICAL_FIELDS}
        mutation = {field: None for field in MUTATION_CANONICAL_FIELDS}
        mutation.update(
            mutant_id="PH-01",
            verdict="killed",
            replay_returncode=1,
            replay_failure_signature={"phase": "run"},
        )
        probes = {"outbound_socket_successes": 0, "raw_transcript": "ignored"}
        source = {"scorer": {"path": "scorer.py", "sha256": "abc"}}

        def evidence_digest(
            mutation_row: dict[str, object], probe_row: dict[str, object]
        ) -> str:
            return _digest(
                _canonical_evidence(
                    control=control,
                    mutations=[mutation_row],
                    baseline={"killed": 1, "total": 1},
                    probes=probe_row,
                    source_provenance=source,
                )
            )

        original = evidence_digest(mutation, probes)
        for field, value in (
            ("verdict", "survived"),
            ("replay_returncode", 0),
            ("replay_failure_signature", {"phase": "output_assert"}),
        ):
            changed = copy.deepcopy(mutation)
            changed[field] = value
            with self.subTest(field=field):
                self.assertNotEqual(original, evidence_digest(changed, probes))
        changed_probes = {**probes, "outbound_socket_successes": 1}
        self.assertNotEqual(original, evidence_digest(mutation, changed_probes))

    def test_source_provenance_covers_all_scored_sources(self) -> None:
        provenance = _source_provenance()
        self.assertEqual(set(provenance), set(SOURCE_FILES))
        self.assertTrue(
            {"application", "provider", "adapter", "scorer"}.issubset(provenance)
        )
        for name, path in SOURCE_FILES.items():
            with self.subTest(name=name):
                self.assertEqual(
                    provenance[name]["sha256"], hashlib.sha256(path.read_bytes()).hexdigest()
                )

    def test_same_seed_replays_exact_concrete_transcript(self) -> None:
        case = next(case for case in self.cases if case.input.action == "AuthorizeApproved")
        digests: list[str] = []
        with TemporaryDirectory(prefix="legacy-payment-test-") as temporary:
            root = Path(temporary)
            transcript = root / "transcript.jsonl"
            prior = os.environ.get("LEGACY_PAYMENT_TRANSCRIPT")
            os.environ["LEGACY_PAYMENT_TRANSCRIPT"] = str(transcript)
            try:
                for run in range(2):
                    context = EffectProviderContext(
                        port_name="PaymentHttpPort",
                        action=case.input.action,
                        case=case,
                        work_dir=root / f"work-{run}",
                        iteration=7,
                        root_seed=20260721,
                        derived_seed=derive_effect_seed(
                            20260721, case.name, 7, "PaymentHttpPort"
                        ),
                    )
                    adapter = PaymentHttpCaseAdapter()
                    with payment_http_provider.bind(context):
                        adapter.setup(SimpleNamespace(effects={"PaymentHttpPort": None}))
                        result = adapter.run(case)
                        self.assertEqual(result.output, case.output)
                rows = [json.loads(line) for line in transcript.read_text().splitlines()]
                digests = [row["transcript_digest"] for row in rows]
            finally:
                if prior is None:
                    os.environ.pop("LEGACY_PAYMENT_TRANSCRIPT", None)
                else:
                    os.environ["LEGACY_PAYMENT_TRANSCRIPT"] = prior
        self.assertEqual(len(set(digests)), 1)
        self.assertTrue(patches_are_clean())

    def test_external_loopback_adapter_drives_real_http_process(self) -> None:
        cases_parent = PROJECT_ROOT / "generated" / "testgraph"
        sys.path.insert(0, str(cases_parent))
        external_cases = list(
            importlib.import_module("payment_http_external_cases").CASES
        )
        case = next(case for case in external_cases if case.input.action == "SubmitApproved")
        result = PaymentHttpExternalAdapter().run(case)
        self.assertEqual(result.output, case.output)
        self.assertEqual(result.after, case.after)

    def test_missing_transcript_helpers_are_structured_and_non_throwing(self) -> None:
        with TemporaryDirectory(prefix="legacy-payment-missing-") as temporary:
            missing = Path(temporary) / "missing.jsonl"
            self.assertIsNone(_compress_optional(missing))
        self.assertEqual(_statistics([])["count"], 0)


if __name__ == "__main__":
    unittest.main()
