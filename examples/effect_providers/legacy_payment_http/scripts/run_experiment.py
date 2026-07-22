#!/usr/bin/env python3
"""Run the preregistered 32-iteration HTTP effect-provider experiment."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib
from importlib.util import find_spec
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
from time import perf_counter
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
REPO_ROOT = PROJECT_ROOT.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SPEC_DIR = PROJECT_ROOT / "specs" / "program_model"
CASES_DIR = PROJECT_ROOT / "generated" / "spec-unit" / "payment_http_internal_cases"
MAPPING = SPEC_DIR / "case_adapters.toml"
PREREGISTRATION = PROJECT_ROOT.parent / "PREREGISTRATION.yaml"
PREREGISTRATION_SHA256 = "970ade21dcf9e460a60cdb1e70396b5b5507c460983e7001cb1bceff5fe9390b"
PREREGISTRATION_COMMIT = "141e63b"
ROOT_SEED = 20260721
ITERATIONS = list(range(32))
INTERNAL_ACTIONS = {
    "AuthorizeApproved",
    "AuthorizeDeclined",
    "AuthorizeBadRequest",
    "AuthorizeTransientThenApproved",
    "AuthorizeTimeoutThenDuplicateApproved",
    "AuthorizeExhaustedUnavailable",
    "AuthorizeMalformedResponse",
}
MUTANTS = [
    {"id": "PH-01", "expected_detector": "provider_local_assertion", "patch": "prepare GET instead of POST"},
    {"id": "PH-02", "expected_detector": "provider_local_assertion", "patch": "send to /v1/paymentz instead of /v1/payments"},
    {"id": "PH-03", "expected_detector": "provider_local_assertion", "patch": "serialize amount as JSON string instead of integer"},
    {"id": "PH-04", "expected_detector": "provider_local_assertion", "patch": "omit Idempotency-Key header"},
    {"id": "PH-05", "expected_detector": "provider_local_assertion", "patch": "regenerate Idempotency-Key on every retry"},
    {"id": "PH-06", "expected_detector": "provider_local_assertion", "patch": "omit connect/read timeout from Session.send"},
    {"id": "PH-07", "expected_detector": "provider_local_assertion", "patch": "perform no retry after timeout or unavailable response"},
    {"id": "PH-08", "expected_detector": "provider_local_assertion", "patch": "retry terminal decline or bad request"},
    {"id": "PH-09", "expected_detector": "provider_local_assertion", "patch": "perform one retry beyond configured maximum"},
    {"id": "PH-10", "expected_detector": "provider_local_assertion", "patch": "stop one attempt before retry budget is exhausted"},
    {"id": "PH-11", "expected_detector": "tla_output", "patch": "normalize declined bad-request or malformed as approved"},
    {"id": "PH-12", "expected_detector": "tla_output", "patch": "truncate approved authorization reference"},
]
DETECTOR_PRIORITY = [
    "tla_output",
    "tla_projected_state",
    "provider_local_assertion",
    "shared_journal",
    "passive_bypass_detector",
    "cleanup_detector",
]
SOURCE_FILES = {
    "application": PROJECT_ROOT / "legacy_payment_http_app" / "application.py",
    "provider": PROJECT_ROOT / "payment_effects" / "provider.py",
    "adapter": PROJECT_ROOT / "payment_effects" / "adapters.py",
    "baseline": PROJECT_ROOT / "payment_effects" / "baseline.py",
    "probes": PROJECT_ROOT / "payment_effects" / "probes.py",
    "scorer": PROJECT_ROOT / "scripts" / "run_experiment.py",
}
CONTROL_CANONICAL_FIELDS = (
    "green",
    "returncode",
    "executed_points",
    "expected_points",
    "action_outcome_coverage",
    "complete_unique_case_iteration_coverage",
    "representative_coverage",
    "canonical_transcript_digest",
    "leaked_patches",
    "outbound_socket_attempts",
    "provider_state_clean",
    "infra_errors",
)
MUTATION_CANONICAL_FIELDS = (
    "mutant_id",
    "patch",
    "expected_detector",
    "verdict",
    "triggered_detectors",
    "primary_detector",
    "expected_detector_matched",
    "first_discovery_root_seed",
    "first_discovery_iteration",
    "first_discovery_case",
    "discovery_failure_signature",
    "replay_failure_signature",
    "replay_returncode",
    "replay_digest",
    "replay_transcript_matches_first_discovery",
    "replay_structured_failure_matches_first_discovery",
    "replay_matches_first_discovery",
    "returncode",
    "diagnostic_count_retained",
    "executed_points",
    "execution_mode",
    "complete_through_first_discovery_iteration",
    "full_survivor_campaign",
    "collect_continue_supported",
    "replay_row_count",
    "leaked_patches",
    "outbound_socket_attempts",
    "provider_state_clean",
    "replay_cleanup_clean",
    "replay_outbound_socket_attempts",
    "replay_provider_state_clean",
    "infra_errors",
)


def _dependency_import_root(package: str) -> Path:
    """Return the environment import root needed by a recorded replay command.

    The shared runner records ``Path(sys.executable).resolve()``. A virtualenv
    interpreter is a symlink, so the recorded command may use the base Python
    without the virtualenv's site-packages. Keeping the dependency root explicit
    makes that command self-contained and verbatim-replayable.
    """

    spec = find_spec(package)
    if spec is None or spec.origin is None:
        raise RuntimeError(f"required experiment dependency is unavailable: {package}")
    return Path(spec.origin).resolve().parent.parent


REQUESTS_IMPORT_ROOT = _dependency_import_root("requests")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compare-to", type=Path)
    parser.add_argument("--skip-regenerate", action="store_true")
    parser.add_argument("--tlc2", default="tlc2")
    args = parser.parse_args()
    _assert_preregistration()
    if not args.skip_regenerate:
        _checked_run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "regenerate.py"),
                "--tlc2",
                args.tlc2,
            ],
            timeout=120,
        )
    cases = _load_cases()
    _assert_generated_contract(cases)
    framework_audit = _framework_audit()
    if not framework_audit["clean"]:
        raise SystemExit(
            "ERROR: forbidden framework rescue surface differs from preregistration: "
            + json.dumps(framework_audit, sort_keys=True)
        )
    source_provenance = _source_provenance()

    raw_dir = PROJECT_ROOT / "evidence" / "raw" / args.label
    raw_dir.mkdir(parents=True, exist_ok=False)
    started = perf_counter()
    control = _run_control(cases, raw_dir)
    if not control["green"]:
        raise SystemExit("ERROR: unmutated generated/effectful control is red; mutants were not scored")

    mutations = [_run_mutant(spec, raw_dir, cases) for spec in MUTANTS]
    baseline = _run_baseline()
    probes = _run_probes(cases, raw_dir)
    source_provenance_after = _source_provenance()
    sources_unchanged = source_provenance_after == source_provenance
    tlc = json.loads((PROJECT_ROOT / "evidence" / "tlc-generation.json").read_text())
    tlc["views"]["internal"]["executed_cases"] = control["executed_points"]
    mutation_verdict_digest = _digest(
        [[row["mutant_id"], row["verdict"], row["primary_detector"]] for row in mutations]
    )
    canonical_evidence_digest = _digest(
        _canonical_evidence(
            control=control,
            mutations=mutations,
            baseline=baseline,
            probes=probes,
            source_provenance=source_provenance,
        )
    )
    result = {
        "schema_version": 2,
        "project": "legacy_payment_http",
        "label": args.label,
        "preregistration_sha256": PREREGISTRATION_SHA256,
        "campaign": {
            "root_seed": ROOT_SEED,
            "iteration_indices": ITERATIONS,
            "generated_cases": len(cases),
            "executed_points": control["executed_points"],
            "all_seven_outcomes_executed": set(control["action_outcome_coverage"]) == INTERNAL_ACTIONS,
        },
        "tlc": tlc,
        "control": control,
        "mutations": mutations,
        "mutation_score": {
            "killed": sum(row["verdict"] == "killed" for row in mutations),
            "total": len(mutations),
            "score": sum(row["verdict"] == "killed" for row in mutations) / len(mutations),
            "expected_detector_matches": sum(row["expected_detector_matched"] for row in mutations),
        },
        "hand_written_baseline": baseline,
        "capability_probes": probes,
        "source_provenance": source_provenance,
        "campaign_integrity": {
            "sources_unchanged": sources_unchanged,
            "source_provenance_after": source_provenance_after,
        },
        "cost": _cost_report(framework_audit),
        "divergence": {
            "mutation_verdict_digest": mutation_verdict_digest,
            "canonical_evidence_digest_per_repetition": canonical_evidence_digest,
            "transcript_digest_per_repetition": control["canonical_transcript_digest"],
            "leaked_paths": [],
            "leaked_patches": control["leaked_patches"],
            "outbound_socket_attempts": probes["outbound_socket_successes"],
            "provider_state_after_run": "clean" if control["provider_state_clean"] else "leaked",
            "semantic_provider_decisions_not_in_case": [
                "transient HTTP status 502/503/504",
                "ConnectTimeout versus ReadTimeout",
                "response JSON whitespace/key order",
                "response header casing",
                "malformed response bytes",
                "opaque authorization reference bytes",
            ],
            "duplicated_concretization_or_projection": [
                "provider creates concrete authorization reference; adapter classifies exact match back to TLA opaque"
            ],
        },
        "framework_files_changed": framework_audit["files_changed"],
        "framework_audit": framework_audit,
        "campaign_limitations": {
            "mutation_execution": "early_stop_after_first_killing_iteration",
            "collect_continue_supported": False,
            "finding": (
                "The V0 effect runner exits after the first failing iteration. "
                "A killed mutant therefore proves one complete 56-case discovery "
                "iteration plus exact replay, while a survivor must complete 56x32."
            ),
            "recommendation": (
                "Add a collect/continue mutation mode so all deterministic iterations "
                "can be measured after first discovery without 32 wrapper invocations."
            ),
            "replay_environment": (
                "The shared runner resolves a virtualenv interpreter symlink when it "
                "records replay commands. This project therefore supplies its active "
                "requests site-packages directory as an explicit import root."
            ),
            "replay_environment_recommendation": (
                "Record the environment interpreter path without resolving its symlink, "
                "or otherwise preserve the originating environment in replay commands."
            ),
        },
        "wall_seconds": perf_counter() - started,
        "stop_go": _stop_go(
            control,
            mutations,
            probes,
            framework_audit,
            sources_unchanged=sources_unchanged,
        ),
    }
    if args.compare_to is not None:
        prior = json.loads(args.compare_to.read_text(encoding="utf-8"))
        comparison = {
            "prior": str(args.compare_to),
            "canonical_evidence_digest_equal": prior["divergence"][
                "canonical_evidence_digest_per_repetition"
            ]
            == canonical_evidence_digest,
            "transcript_digest_equal": prior["divergence"]["transcript_digest_per_repetition"]
            == control["canonical_transcript_digest"],
        }
        result["repetition_comparison"] = comparison
        result["stop_go"]["checks"].update(
            {
                "repetition_canonical_evidence_digest_equal": comparison[
                    "canonical_evidence_digest_equal"
                ],
                "repetition_transcript_digest_equal": comparison[
                    "transcript_digest_equal"
                ],
            }
        )
        if not all(result["stop_go"]["checks"].values()):
            result["stop_go"]["verdict"] = "no_go"
    output = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "control_points": control["executed_points"],
        "mutation_score": result["mutation_score"],
        "baseline_score": {"killed": baseline["killed"], "total": baseline["total"]},
        "stop_go": result["stop_go"],
    }, indent=2, sort_keys=True))
    return 0 if result["stop_go"]["verdict"] == "go" else 1


def _run_control(cases: list[Any], raw_dir: Path) -> dict[str, Any]:
    transcript = raw_dir / "control.jsonl"
    completed, command = _runner_command(transcript=transcript, work_dir=raw_dir / "control-work")
    rows = _read_rows(transcript)
    expected_points = len(cases) * len(ITERATIONS)
    expected_identities = {
        (str(case.name), iteration)
        for case in cases
        for iteration in ITERATIONS
    }
    actual_identities = {
        (str(row.get("case")), int(row.get("iteration", -1)))
        for row in rows
    }
    coverage = {
        action: sum(row["action"] == action for row in rows)
        for action in sorted(INTERNAL_ACTIONS)
    }
    leaked = sorted({item for row in rows for item in row["leaked_patches"]})
    outbound_attempts = sum(len(row.get("outbound_socket_attempts", [])) for row in rows)
    provider_state_clean = bool(rows) and all(
        row.get("provider_state_after_run") == "clean" for row in rows
    )
    elapsed = [float(row["elapsed_ms"]) for row in rows]
    canonical_digest = _digest(
        sorted([row["case"], row["iteration"], row["transcript_digest"]] for row in rows)
    )
    representative_coverage = {
        field: sorted({row["representative"][field] for row in rows})
        for field in ("transient_status", "timeout_type", "header_name", "layout")
    }
    control_log = raw_dir / "control-run.log"
    control_log.write_text(
        "$ " + shlex.join(command) + "\n" + completed.stdout + completed.stderr,
        encoding="utf-8",
    )
    compressed_log = _compress_optional(control_log)
    compressed = _compress_optional(transcript)
    complete_identity_coverage = actual_identities == expected_identities
    all_actions = set(coverage) == INTERNAL_ACTIONS and all(coverage.values())
    infra_errors: list[str] = []
    if not transcript.exists() and compressed is None:
        infra_errors.append("control transcript missing")
    if len(rows) != expected_points:
        infra_errors.append(f"expected {expected_points} transcript rows, got {len(rows)}")
    if not complete_identity_coverage:
        infra_errors.append("unique (case, iteration) coverage is incomplete or duplicated")
    return {
        "green": (
            completed.returncode == 0
            and not infra_errors
            and all_actions
            and not leaked
            and outbound_attempts == 0
            and provider_state_clean
        ),
        "returncode": completed.returncode,
        "executed_points": len(rows),
        "expected_points": expected_points,
        "action_outcome_coverage": coverage,
        "complete_unique_case_iteration_coverage": complete_identity_coverage,
        "representative_coverage": representative_coverage,
        "runtime_ms": _statistics(elapsed),
        "canonical_transcript_digest": canonical_digest,
        "raw_transcript": None if compressed is None else str(compressed.relative_to(PROJECT_ROOT)),
        "raw_diagnostic_log": (
            None if compressed_log is None else str(compressed_log.relative_to(PROJECT_ROOT))
        ),
        "leaked_patches": leaked,
        "outbound_socket_attempts": outbound_attempts,
        "provider_state_clean": provider_state_clean,
        "infra_errors": infra_errors,
        "command": shlex.join(command),
    }


def _run_mutant(
    spec: dict[str, str],
    raw_dir: Path,
    cases: list[Any],
) -> dict[str, Any]:
    mutant = spec["id"]
    transcript = raw_dir / f"{mutant}.jsonl"
    completed, command = _runner_command(
        transcript=transcript,
        work_dir=raw_dir / f"{mutant}-work",
        mutant=mutant,
    )
    output = completed.stdout + completed.stderr
    diagnostics = _failure_diagnostics(output)
    rows = _read_rows(transcript)
    case_names = {str(case.name) for case in cases}
    expected_points = len(cases) * len(ITERATIONS)
    identities = {
        (str(row.get("case")), int(row.get("iteration", -1))) for row in rows
    }
    full_survivor_campaign = (
        len(rows) == expected_points
        and identities
        == {(case_name, iteration) for case_name in case_names for iteration in ITERATIONS}
    )
    leaked = sorted({item for row in rows for item in row.get("leaked_patches", [])})
    outbound_attempts = sum(len(row.get("outbound_socket_attempts", [])) for row in rows)
    provider_state_clean = bool(rows) and all(
        row.get("provider_state_after_run") == "clean" for row in rows
    )
    detectors = _detectors(diagnostics, rows)
    first = diagnostics[0] if diagnostics else {}
    first_case = str(first.get("case", ""))
    first_iteration = int(first.get("iteration", -1))
    complete_through_first_discovery_iteration = (
        completed.returncode != 0
        and first_iteration >= 0
        and len(rows) == len(cases) * (first_iteration + 1)
        and identities
        == {
            (case_name, iteration)
            for case_name in case_names
            for iteration in range(first_iteration + 1)
        }
    )
    first_row = next(
        (
            row
            for row in rows
            if row["case"] == first_case and row["iteration"] == first_iteration
        ),
        None,
    )
    replay_command = str(first.get("replay", ""))
    replay_digest = ""
    replay_matches = False
    replay_transcript_matches = False
    replay_failure_matches = False
    replay_cleanup_clean = False
    replay_outbound_attempts = 0
    replay_provider_state_clean = False
    replay_row_count = 0
    replay_returncode: int | None = None
    replay_failure_signature: dict[str, Any] | None = None
    discovery_failure_signature = _failure_signature(first, rows)
    replay_log_compressed: Path | None = None
    if replay_command:
        replay_transcript = raw_dir / f"{mutant}-replay.jsonl"
        env = _runner_env(replay_transcript, mutant)
        replay = subprocess.run(
            shlex.split(replay_command),
            cwd=PROJECT_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=120,
        )
        replay_rows = _read_rows(replay_transcript)
        replay_diagnostics = _failure_diagnostics(replay.stdout + replay.stderr)
        replay_returncode = replay.returncode
        replay_failure_signature = _failure_signature(
            replay_diagnostics[0] if replay_diagnostics else {}, replay_rows
        )
        replay_failure_matches = (
            discovery_failure_signature is not None
            and replay_failure_signature == discovery_failure_signature
        )
        replay_row_count = len(replay_rows)
        if len(replay_rows) == 1:
            replay_digest = str(replay_rows[0]["transcript_digest"])
            replay_transcript_matches = (
                first_row is not None
                and replay_digest == first_row["transcript_digest"]
                and replay_rows[0]["case"] == first_case
                and replay_rows[0]["iteration"] == first_iteration
            )
            replay_cleanup_clean = all(
                not row.get("leaked_patches") for row in replay_rows
            )
            replay_outbound_attempts = sum(
                len(row.get("outbound_socket_attempts", [])) for row in replay_rows
            )
            replay_provider_state_clean = all(
                row.get("provider_state_after_run") == "clean" for row in replay_rows
            )
        replay_log = raw_dir / f"{mutant}-replay.log"
        replay_log.write_text(
            "$ " + replay_command + "\n" + replay.stdout + replay.stderr,
            encoding="utf-8",
        )
        replay_log_compressed = _compress_optional(replay_log)
        _compress_optional(replay_transcript)
        replay_matches = _replay_is_exact(
            returncode=replay.returncode,
            transcript_matches=replay_transcript_matches,
            discovery_failure_signature=discovery_failure_signature,
            replay_failure_signature=replay_failure_signature,
        )
    run_log = raw_dir / f"{mutant}-run.log"
    run_log.write_text(
        "$ " + shlex.join(command) + "\n" + output,
        encoding="utf-8",
    )
    run_log_compressed = _compress_optional(run_log)
    compressed = _compress_optional(transcript)
    expected_matched = spec["expected_detector"] in detectors
    infra_errors: list[str] = []
    if compressed is None:
        infra_errors.append("mutant transcript missing")
    if completed.returncode != 0 and not diagnostics:
        infra_errors.append("structured EFFECT_FUZZ_FAILURE diagnostic missing")
    if completed.returncode != 0 and not complete_through_first_discovery_iteration:
        infra_errors.append(
            "killed mutant did not complete every 56-case iteration through first discovery"
        )
    if completed.returncode == 0 and not full_survivor_campaign:
        infra_errors.append(
            f"surviving mutant did not complete all {expected_points} unique case/iteration points"
        )
    if leaked or outbound_attempts or not provider_state_clean:
        infra_errors.append("mutant provider cleanup/socket isolation failed")
    if completed.returncode != 0 and (
        not replay_cleanup_clean
        or replay_outbound_attempts
        or not replay_provider_state_clean
    ):
        infra_errors.append("replay provider cleanup/socket isolation failed")
    if completed.returncode != 0 and replay_row_count != 1:
        infra_errors.append(
            f"exact replay must emit one transcript row, observed {replay_row_count}"
        )
    if completed.returncode != 0 and replay_returncode == 0:
        infra_errors.append("exact replay unexpectedly returned zero")
    if completed.returncode != 0 and replay_failure_signature is None:
        infra_errors.append("exact replay structured failure diagnostic missing")
    if completed.returncode != 0 and not replay_failure_matches:
        infra_errors.append("exact replay structured failure differs from first discovery")
    killed = (
        completed.returncode != 0
        and expected_matched
        and replay_matches
        and not infra_errors
    )
    primary = next((name for name in DETECTOR_PRIORITY if name in detectors), None)
    return {
        "mutant_id": mutant,
        "patch": spec["patch"],
        "expected_detector": spec["expected_detector"],
        "verdict": (
            "killed"
            if killed
            else "survived"
            if completed.returncode == 0 and full_survivor_campaign and not infra_errors
            else "invalid_or_misattributed"
        ),
        "triggered_detectors": detectors,
        "primary_detector": primary,
        "expected_detector_matched": expected_matched,
        "first_discovery_root_seed": first.get("root_seed"),
        "first_discovery_iteration": first.get("iteration"),
        "first_discovery_case": first.get("case"),
        "replay_command": replay_command,
        "replay_digest": replay_digest,
        "discovery_failure_signature": discovery_failure_signature,
        "replay_failure_signature": replay_failure_signature,
        "replay_returncode": replay_returncode,
        "replay_transcript_matches_first_discovery": replay_transcript_matches,
        "replay_structured_failure_matches_first_discovery": replay_failure_matches,
        "replay_matches_first_discovery": replay_matches,
        "returncode": completed.returncode,
        "raw_transcript": None if compressed is None else str(compressed.relative_to(PROJECT_ROOT)),
        "raw_diagnostic_log": (
            None if run_log_compressed is None else str(run_log_compressed.relative_to(PROJECT_ROOT))
        ),
        "raw_replay_diagnostic_log": (
            None
            if replay_log_compressed is None
            else str(replay_log_compressed.relative_to(PROJECT_ROOT))
        ),
        "diagnostic_count_retained": len(diagnostics),
        "executed_points": len(rows),
        "execution_mode": (
            "early_stop_after_first_killing_iteration"
            if completed.returncode != 0
            else "full_survivor_campaign"
        ),
        "complete_through_first_discovery_iteration": complete_through_first_discovery_iteration,
        "full_survivor_campaign": full_survivor_campaign,
        "collect_continue_supported": False,
        "replay_row_count": replay_row_count,
        "leaked_patches": leaked,
        "outbound_socket_attempts": outbound_attempts,
        "provider_state_clean": provider_state_clean,
        "replay_cleanup_clean": replay_cleanup_clean,
        "replay_outbound_socket_attempts": replay_outbound_attempts,
        "replay_provider_state_clean": replay_provider_state_clean,
        "infra_errors": infra_errors,
    }


def _runner_command(
    *,
    transcript: Path,
    work_dir: Path,
    mutant: str | None = None,
) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_generated_case_adapters.py"),
        str(CASES_DIR),
        "--mapping",
        str(MAPPING),
        "--spec-dir",
        str(SPEC_DIR),
        "--import-root",
        str(PROJECT_ROOT),
        "--import-root",
        str(REQUESTS_IMPORT_ROOT),
        "--batch",
        "--fuzz-runs",
        str(len(ITERATIONS)),
        "--seed",
        str(ROOT_SEED),
        "--work-dir",
        str(work_dir),
    ]
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=_runner_env(transcript, mutant),
        text=True,
        capture_output=True,
        check=False,
        timeout=120,
    )
    return completed, command


def _runner_env(transcript: Path, mutant: str | None) -> dict[str, str]:
    env = os.environ.copy()
    env["LEGACY_PAYMENT_TRANSCRIPT"] = str(transcript)
    if mutant is None:
        env.pop("LEGACY_PAYMENT_MUTANT", None)
    else:
        env["LEGACY_PAYMENT_MUTANT"] = mutant
    return env


def _run_baseline() -> dict[str, Any]:
    from payment_effects.baseline import run_hand_baseline

    return run_hand_baseline([spec["id"] for spec in MUTANTS])


def _run_probes(cases: list[Any], raw_dir: Path) -> dict[str, Any]:
    from payment_effects.probes import run_capability_probes

    case = next(case for case in cases if case.input.action == "AuthorizeApproved")
    transcript = raw_dir / "capability-probes.jsonl"
    result = run_capability_probes(case, str(transcript))
    compressed = _compress_optional(transcript)
    result["raw_transcript"] = None if compressed is None else str(compressed.relative_to(PROJECT_ROOT))
    return result


def _detectors(diagnostics: list[dict[str, Any]], rows: list[dict[str, Any]]) -> list[str]:
    found = {name for row in rows for name in row.get("detectors", [])}
    for diagnostic in diagnostics:
        phase = diagnostic.get("phase")
        error = str(diagnostic.get("error", ""))
        if "DETECTOR[provider_local_assertion]" in error:
            found.add("provider_local_assertion")
        if "DETECTOR[cleanup_detector]" in error:
            found.add("cleanup_detector")
        if phase == "output_assert":
            found.add("tla_output")
        if phase == "projected_assert" or "after-state mismatch" in error:
            found.add("tla_projected_state")
    return [name for name in DETECTOR_PRIORITY if name in found]


def _failure_diagnostics(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    marker = "EFFECT_FUZZ_FAILURE "
    for line in text.splitlines():
        if marker not in line:
            continue
        try:
            rows.append(json.loads(line.split(marker, 1)[1]))
        except json.JSONDecodeError:
            continue
    return rows


def _failure_signature(
    diagnostic: dict[str, Any], rows: list[dict[str, Any]]
) -> dict[str, Any] | None:
    if not diagnostic:
        return None
    detectors = _detectors([diagnostic], rows)
    normalized_error = " ".join(str(diagnostic.get("error", "")).split())
    return {
        "case": str(diagnostic.get("case", "")),
        "iteration": int(diagnostic.get("iteration", -1)),
        "phase": str(diagnostic.get("phase", "")),
        "error_type": str(diagnostic.get("error_type", "")),
        "detector": next((name for name in DETECTOR_PRIORITY if name in detectors), None),
        "normalized_error": normalized_error,
    }


def _replay_is_exact(
    *,
    returncode: int,
    transcript_matches: bool,
    discovery_failure_signature: dict[str, Any] | None,
    replay_failure_signature: dict[str, Any] | None,
) -> bool:
    return (
        returncode != 0
        and transcript_matches
        and discovery_failure_signature is not None
        and replay_failure_signature == discovery_failure_signature
    )


def _assert_preregistration() -> None:
    actual = hashlib.sha256(PREREGISTRATION.read_bytes()).hexdigest()
    if actual != PREREGISTRATION_SHA256:
        raise SystemExit(
            f"ERROR: immutable preregistration changed: {actual} != {PREREGISTRATION_SHA256}"
        )


def _assert_generated_contract(cases: list[Any]) -> None:
    actions = {str(case.input.action) for case in cases}
    if actions != INTERNAL_ACTIONS:
        raise SystemExit(
            f"ERROR: generated semantic action drift: {sorted(actions)} != {sorted(INTERNAL_ACTIONS)}"
        )
    if any(case.input.action not in case.labels for case in cases):
        raise SystemExit("ERROR: generated cases lost their semantic action label")
    if len(cases) != 56:
        raise SystemExit(f"ERROR: expected 56 complete generated cases, got {len(cases)}")
    generation = json.loads((PROJECT_ROOT / "evidence" / "tlc-generation.json").read_text())
    for name, expected in generation["model_digests"].items():
        actual = hashlib.sha256((SPEC_DIR / name).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"ERROR: generated corpus provenance is stale for {name}")


def _load_cases() -> list[Any]:
    sys.path.insert(0, str(CASES_DIR.parent))
    module = importlib.import_module(CASES_DIR.name)
    return list(module.CASES)


def _read_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _compress_optional(path: Path) -> Path | None:
    if not path.is_file():
        return None
    destination = path.with_suffix(path.suffix + ".gz")
    with path.open("rb") as source, gzip.open(destination, "wb", compresslevel=9) as target:
        while chunk := source.read(1024 * 1024):
            target.write(chunk)
    path.unlink()
    return destination


def _statistics(values: list[float]) -> dict[str, float | int]:
    if not values:
        return {
            "count": 0,
            "minimum": 0.0,
            "p50": 0.0,
            "p95": 0.0,
            "maximum": 0.0,
            "total": 0.0,
        }
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "minimum": ordered[0],
        "p50": _percentile(ordered, 0.50),
        "p95": _percentile(ordered, 0.95),
        "maximum": ordered[-1],
        "total": sum(ordered),
    }


def _percentile(values: list[float], quantile: float) -> float:
    index = max(0, min(len(values) - 1, int((len(values) - 1) * quantile)))
    return values[index]


def _digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _source_provenance() -> dict[str, dict[str, str]]:
    return {
        name: {
            "path": str(path.relative_to(PROJECT_ROOT)),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for name, path in SOURCE_FILES.items()
    }


def _canonical_evidence(
    *,
    control: dict[str, Any],
    mutations: list[dict[str, Any]],
    baseline: dict[str, Any],
    probes: dict[str, Any],
    source_provenance: dict[str, dict[str, str]],
) -> dict[str, Any]:
    """Return the complete deterministic evidence compared across repetitions.

    Runtime timings, filesystem paths, and shell commands are deliberately
    excluded. Semantic control coverage, every mutation/discovery/replay gate,
    the separate baseline, probes, and exact scorer inputs are included.
    """

    canonical_probes = {
        key: value
        for key, value in probes.items()
        if key != "raw_transcript"
    }
    return {
        "control": {key: control[key] for key in CONTROL_CANONICAL_FIELDS},
        "mutations": [
            {key: mutation[key] for key in MUTATION_CANONICAL_FIELDS}
            for mutation in mutations
        ],
        "hand_written_baseline": baseline,
        "capability_probes": canonical_probes,
        "source_provenance": source_provenance,
    }


def _checked_run(command: list[str], *, timeout: int) -> None:
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    if completed.returncode != 0:
        sys.stderr.write(completed.stdout + completed.stderr)
        raise SystemExit(completed.returncode)


def _loc(paths: list[Path]) -> int:
    return sum(len(path.read_text(encoding="utf-8").splitlines()) for path in paths if path.is_file())


def _cost_report(framework_audit: dict[str, Any]) -> dict[str, Any]:
    groups = {
        "application": list((PROJECT_ROOT / "legacy_payment_http_app").glob("*.py")),
        "interface": [
            SPEC_DIR / "spec_manifest.yaml",
            SPEC_DIR / "generated" / "payment_http_contract" / "ports.py",
        ],
        "provider": [PROJECT_ROOT / "payment_effects" / "provider.py"],
        "adapter": [
            PROJECT_ROOT / "payment_effects" / "adapters.py",
            PROJECT_ROOT / "payment_effects" / "external.py",
        ],
        "projection_or_oracle": [
            SPEC_DIR / "tlc_projection.py",
            PROJECT_ROOT / "payment_effects" / "baseline.py",
        ],
        "model": list(SPEC_DIR.glob("*.tla")) + list(SPEC_DIR.glob("*.cfg")),
        "experiment": list((PROJECT_ROOT / "scripts").glob("*.py")) + list((PROJECT_ROOT / "tests").glob("*.py")),
    }
    authoring = PROJECT_ROOT / "evidence" / "authoring.json"
    authoring_data = json.loads(authoring.read_text()) if authoring.exists() else {}
    retrieval = PROJECT_ROOT / "evidence" / "retrieval.json"
    retrieval_data = json.loads(retrieval.read_text()) if retrieval.exists() else {}
    result: dict[str, Any] = {
        "authoring_wall_minutes": authoring_data.get("authoring_wall_minutes"),
        "authoring_edit_run_iterations": authoring_data.get("authoring_edit_run_iterations"),
        "framework_files_changed": framework_audit["files_changed"],
        "retrieval_files_read": retrieval_data.get("retrieval_files_read"),
        "retrieval_lines_read": retrieval_data.get("retrieval_lines_read"),
        "retrieval_files_changed": retrieval_data.get("retrieval_files_changed"),
        "retrieval_lines_changed": retrieval_data.get("retrieval_lines_changed"),
    }
    for name, paths in groups.items():
        result[f"{name}_files"] = len([path for path in paths if path.is_file()])
        result[f"{name}_loc"] = _loc(paths)
    return result


def _stop_go(
    control: dict[str, Any],
    mutations: list[dict[str, Any]],
    probes: dict[str, Any],
    framework_audit: dict[str, Any],
    *,
    sources_unchanged: bool,
) -> dict[str, Any]:
    checks = {
        "control_32_iterations_green": control["green"],
        "all_seven_outcomes": set(control["action_outcome_coverage"]) == INTERNAL_ACTIONS,
        "all_12_mutants_killed": all(row["verdict"] == "killed" for row in mutations),
        "all_expected_detectors": all(row["expected_detector_matched"] for row in mutations),
        "all_replays_nonzero_structured_exact": all(
            row["replay_returncode"] != 0
            and row["replay_transcript_matches_first_discovery"]
            and row["replay_structured_failure_matches_first_discovery"]
            and row["replay_matches_first_discovery"]
            for row in mutations
        ),
        "patches_clean": control["provider_state_clean"] and probes["patches_clean_after_probes"],
        "mutant_and_replay_isolation_clean": all(
            row["provider_state_clean"]
            and row["replay_provider_state_clean"]
            and not row["leaked_patches"]
            and row["outbound_socket_attempts"] == 0
            and row["replay_cleanup_clean"]
            and row["replay_outbound_socket_attempts"] == 0
            for row in mutations
        ),
        "no_outbound_socket_succeeded": probes["outbound_socket_successes"] == 0,
        "framework_files_changed_zero": framework_audit["clean"]
        and framework_audit["files_changed"] == 0,
        "scored_sources_unchanged": sources_unchanged,
    }
    return {
        "verdict": "go" if all(checks.values()) else "no_go",
        "checks": checks,
        "compatibility_only": probes["compatibility_only"],
    }


def _framework_audit() -> dict[str, Any]:
    forbidden = [
        "spec_double_compiler",
        "scripts/run_generated_case_adapters.py",
        "scripts/generate_cases_from_tlc_dump.py",
        "scripts/generate_python.py",
        "scripts/tla_spec_dev.py",
        "scripts/scaffold_spec.py",
        "scripts/onboard_program_model.py",
        "templates",
        "tests",
    ]
    commands = [
        ["git", "diff", "--name-only", PREREGISTRATION_COMMIT, "--", *forbidden],
        ["git", "ls-files", "--others", "--exclude-standard", "--", *forbidden],
    ]
    changed: set[str] = set()
    command_rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
        names = [line for line in completed.stdout.splitlines() if line]
        changed.update(names)
        command_rows.append(
            {
                "command": shlex.join(command),
                "returncode": completed.returncode,
                "paths": names,
                "stderr": completed.stderr.strip(),
            }
        )
        if completed.returncode != 0:
            errors.append(f"audit command failed: {shlex.join(command)}")
    return {
        "base_commit": PREREGISTRATION_COMMIT,
        "forbidden_surfaces": forbidden,
        "changed_paths": sorted(changed),
        "files_changed": len(changed),
        "commands": command_rows,
        "errors": errors,
        "clean": not changed and not errors,
    }
if __name__ == "__main__":
    raise SystemExit(main())
