# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml", "testgraphsdk"]
#
# [tool.uv.sources]
# testgraphsdk = { path = "../sdk/python", editable = true }
# ///
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import yaml
from testgraphsdk import NodeResult, NodeSpec, node, procs


SPEC = (
    NodeSpec("effect.providers.examples")
    .kind("assertion")
    .tags("effect-providers", "generated-cases", "mutation", "external")
    .timeout("240s")
    .side_effects("filesystem:writes", "process:spawn", "network:loopback")
)

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "examples" / "effect_providers"
AGGREGATE = EXAMPLES / "RESULTS.json"
ATOMIC = EXAMPLES / "atomic_publisher"
HTTP = EXAMPLES / "legacy_payment_http"
REMINDER = EXAMPLES / "reminder_worker"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def relative_digests_match(root: Path, expected: dict[str, str]) -> bool:
    return all(
        (root / relative).is_file()
        and hashlib.sha256((root / relative).read_bytes()).hexdigest() == digest
        for relative, digest in expected.items()
    )


def source_hashes_match(project: Path, provenance: dict[str, Any]) -> bool:
    if provenance and all(isinstance(value, str) for value in provenance.values()):
        return all(
            (project / relative).is_file()
            and hashlib.sha256((project / relative).read_bytes()).hexdigest() == digest
            for relative, digest in provenance.items()
        )
    return all(
        (project / str(value["path"])).is_file()
        and hashlib.sha256(
            (project / str(value["path"])).read_bytes()
        ).hexdigest()
        == str(value["sha256"])
        for value in provenance.values()
    )


def log_text(ctx: Any, record: Any) -> str:
    if not record.log_path:
        return ""
    return (ctx.report_dir / record.log_path).read_text(encoding="utf-8")


@node(SPEC)
def main(ctx):
    # Test Graph describes every source in a copied probe project even when a
    # graph does not select this node. Keep repository-only imports in the
    # execution path so description stays portable.
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from extract_spec_manifest import parse_simple_yaml

    aggregate = load(AGGREGATE)
    atomic = load(ATOMIC / "evidence" / "atomic-publisher-raw.json")
    reminder_1 = load(
        REMINDER / "evidence" / "runs" / "reviewed-parser-parity-1" / "results.json"
    )
    reminder_2 = load(
        REMINDER / "evidence" / "runs" / "reviewed-parser-parity-2" / "results.json"
    )
    http_1 = load(HTTP / "evidence" / "reviewed-local-repetition-1.json")
    http_2 = load(HTTP / "evidence" / "reviewed-local-repetition-2.json")

    preregistration = EXAMPLES / "PREREGISTRATION.yaml"
    preregistration_digest = hashlib.sha256(preregistration.read_bytes()).hexdigest()
    result = NodeResult.pass_(SPEC.id)
    result.assertion(
        "immutable preregistration digest matches aggregate",
        preregistration_digest == aggregate["preregistration"]["sha256"],
    )

    reminder_manifest_text = (
        REMINDER / "specs" / "program_model" / "spec_manifest.yaml"
    ).read_text(encoding="utf-8")
    fallback_manifest = parse_simple_yaml(reminder_manifest_text)
    pyyaml_manifest = yaml.safe_load(reminder_manifest_text)
    contract_keys = (
        "module",
        "package",
        "types",
        "state",
        "commands",
        "results",
        "events",
        "ports",
        "fake",
        "invariant_templates",
        "example_traces",
        "adapters",
        "invariants",
        "finite_model",
        "generators",
    )
    fallback_contract = {key: fallback_manifest.get(key) for key in contract_keys}
    pyyaml_contract = {key: pyyaml_manifest.get(key) for key in contract_keys}
    reminder_methods = fallback_manifest["ports"]
    none_result_methods = (
        reminder_methods["QueuePort"]["methods"]["acknowledge"],
        reminder_methods["QueuePort"]["methods"]["release"],
        reminder_methods["QueuePort"]["methods"]["dead_letter"],
        reminder_methods["OutboxPort"]["methods"]["stage"],
        reminder_methods["OutboxPort"]["methods"]["mark_sent"],
    )
    result.assertion(
        "reminder contract sections have exact PyYAML/fallback semantic parity",
        fallback_contract == pyyaml_contract
        and all(method["result"] is None for method in none_result_methods),
    )

    atomic_repetitions = atomic["repetitions"]
    result.assertion("atomic decision is go", atomic["decision"]["verdict"] == "go")
    result.assertion(
        "atomic controls cover 112 points twice",
        [len(row["control"]["points"]) for row in atomic_repetitions] == [112, 112],
    )
    result.assertion(
        "atomic kills repeat and first-discovery replays are exact",
        all(
            len(row["mutants"]) == 12
            and all(mutant["verdict"] == "killed" for mutant in row["mutants"])
            for row in atomic_repetitions
        )
        and all(
            mutant["replay_returncode"] != 0
            and mutant["replay_exact"]
            and mutant["replay_failure_exact"]
            and mutant["replay_transcript_exact"]
            for mutant in atomic_repetitions[0]["mutants"]
        )
        and all(
            mutant["replay_exact"] is None
            for mutant in atomic_repetitions[1]["mutants"]
        )
        and atomic_repetitions[0]["verdict_digest"]
        == atomic_repetitions[1]["verdict_digest"]
        and atomic_repetitions[0]["transcript_digest"]
        == atomic_repetitions[1]["transcript_digest"],
    )
    result.assertion(
        "atomic source provenance is current",
        source_hashes_match(ATOMIC, atomic["source_provenance"]),
    )
    result.assertion(
        "atomic model and generated-corpus provenance is current",
        relative_digests_match(
            ATOMIC / "specs" / "program_model",
            atomic["generated_provenance"]["model_digests"],
        ),
    )
    result.assertion(
        "atomic cleanup and framework audit are green",
        atomic["cleanup_isolation"]["verdict"] == "green"
        and atomic["framework_files_changed"] == 0,
    )

    result.assertion(
        "reminder accepted repetitions are go and deterministic",
        reminder_1["decision"] == "go"
        and reminder_2["decision"] == "go"
        and reminder_1["canonical_verdict_digest"]
        == reminder_2["canonical_verdict_digest"],
    )
    result.assertion(
        "reminder controls, mutants, replays, and cleanup are complete",
        all(
            row["control_valid"]
            and row["control"]["executed_points"] == 175
            and row["effectful_mutation"]["killed"] == 12
            and row["campaign_integrity"]["replays_exact"]
            and row["campaign_integrity"]["cleanup_exact"]
            and row["campaign_integrity"]["framework_audit_zero"]
            for row in (reminder_1, reminder_2)
        ),
    )
    result.assertion(
        "reminder source provenance is current",
        source_hashes_match(REMINDER, reminder_2["source_provenance"]),
    )
    reminder_spec = REMINDER / "specs" / "program_model"
    reminder_cases = (
        REMINDER
        / "generated"
        / "cases"
        / "spec-unit"
        / "reminder_internal_cases"
    )
    result.assertion(
        "reminder model and generated-corpus provenance is current",
        reminder_2["generated_cases"]["source_model_sha256"]
        == canonical_digest(
            {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in (
                    reminder_spec / "Internal.tla",
                    reminder_spec / "Internal.cfg",
                )
            }
        )
        and reminder_2["generated_cases"]["package_sha256"]
        == canonical_digest(
            {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(reminder_cases.glob("*.py"))
            }
        ),
    )

    result.assertion(
        "HTTP accepted repetitions are go and full evidence is deterministic",
        http_1["stop_go"]["verdict"] == "go"
        and http_2["stop_go"]["verdict"] == "go"
        and http_2["repetition_comparison"]["canonical_evidence_digest_equal"]
        and http_2["repetition_comparison"]["transcript_digest_equal"],
    )
    result.assertion(
        "HTTP controls, mutants, structured replay, and isolation are complete",
        all(
            row["control"]["executed_points"] == 1792
            and row["mutation_score"]["killed"] == 12
            and row["stop_go"]["checks"]["all_replays_nonzero_structured_exact"]
            and row["stop_go"]["checks"]["mutant_and_replay_isolation_clean"]
            and row["stop_go"]["checks"]["framework_files_changed_zero"]
            for row in (http_1, http_2)
        ),
    )
    result.assertion(
        "HTTP source provenance is current",
        source_hashes_match(HTTP, http_2["source_provenance"]),
    )
    result.assertion(
        "HTTP model and generated-corpus provenance is current",
        relative_digests_match(
            HTTP / "specs" / "program_model",
            http_2["tlc"]["model_digests"],
        )
        and (HTTP / http_2["tlc"]["generated_port"]["path"]).is_file()
        and hashlib.sha256(
            (HTTP / http_2["tlc"]["generated_port"]["path"]).read_bytes()
        ).hexdigest()
        == http_2["tlc"]["generated_port"]["sha256"],
    )

    overall = aggregate["overall"]
    result.assertion(
        "aggregate reconciles all fixed catalogs",
        overall["effectful_mutation"] == {"killed": 36, "score": 1.0, "total": 36}
        and overall["expected_detector_attribution"]
        == {
            "passive_bypass_detector": 1,
            "provider_owned_assertion_or_shared_journal": 20,
            "tla_derived_case_oracle": 15,
            "total": 36,
        },
    )
    result.assertion(
        "aggregate labels baseline comparison descriptive",
        overall["separate_hand_written_baselines"]["comparison_is_descriptive_not_pooled"],
    )

    commands = [
        (
            "atomic-tests",
            [sys.executable, str(ATOMIC / "test_atomic_publisher.py")],
            ATOMIC,
            None,
        ),
        (
            "reminder-tests",
            [sys.executable, str(REMINDER / "test_reminder_worker.py")],
            REMINDER,
            None,
        ),
    ]
    for label, argv, cwd, environment in commands:
        record = procs.run(ctx, label, argv, cwd=cwd, env=environment)
        result.process(record).assertion(f"{label} passed", record.exit_code == 0)

    http_environment = {
        **os.environ,
        "UV_CACHE_DIR": str(ctx.report_dir / "uv-cache"),
    }
    http_tests = procs.run(
        ctx,
        "http-tests",
        [
            "uv",
            "run",
            "--project",
            str(HTTP),
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            str(HTTP / "tests"),
            "-v",
        ],
        cwd=REPO_ROOT,
        env=http_environment,
    )
    result.process(http_tests).assertion("HTTP unit/loopback tests passed", http_tests.exit_code == 0)

    http_external = procs.run(
        ctx,
        "http-external-56",
        [
            "uv",
            "run",
            "--project",
            str(HTTP),
            "python",
            str(REPO_ROOT / "scripts" / "run_generated_case_adapters.py"),
            str(HTTP / "generated" / "testgraph" / "payment_http_external_cases"),
            "--mapping",
            str(HTTP / "specs" / "program_model" / "testgraph_bindings.yml"),
            "--spec-dir",
            str(HTTP / "specs" / "program_model"),
            "--import-root",
            str(HTTP),
            "--view",
            "external",
            "--batch",
        ],
        cwd=REPO_ROOT,
        env=http_environment,
    )
    result.process(http_external).assertion(
        "all 56 HTTP external cases passed",
        http_external.exit_code == 0
        and "executed 56 cases in batch" in log_text(ctx, http_external),
    )

    return (
        result.metric("effectfulMutantsKilled", 36)
        .metric("effectfulMutantsTotal", 36)
        .metric("controlPointsPerAcceptedRepetition", 112 + 1792 + 175)
        .metric("externalCasesValidated", 7 + 56 + 7)
        .artifact("aggregate-results", str(AGGREGATE))
        .artifact(
            "atomic-evidence",
            str(ATOMIC / "evidence" / "atomic-publisher-raw.json"),
        )
        .artifact(
            "http-evidence",
            str(HTTP / "evidence" / "reviewed-local-repetition-2.json"),
        )
        .artifact(
            "reminder-evidence",
            str(
                REMINDER
                / "evidence"
                / "runs"
                / "reviewed-parser-parity-2"
                / "results.json"
            ),
        )
    )


if __name__ == "__main__":
    main()
