"""Separate ordinary hand-written unit baseline; no generated cases or fuzz."""

from __future__ import annotations

from contextlib import contextmanager
import json
import os
from typing import Any, Iterator
from unittest.mock import patch

import requests

from legacy_payment_http_app import authorize_payment


BASELINE_SCENARIOS = {
    "approved": {
        "script": [(200, {"status": "approved", "authorization_reference": "baseline-ref"})],
        "expected": {
            "decision": "approved",
            "reason": "",
            "authorization_reference": "baseline-ref",
            "attempts": 1,
        },
    },
    "declined": {
        "script": [(402, {"status": "declined", "reason": "insufficient_funds"})],
        "expected": {
            "decision": "declined",
            "reason": "insufficient_funds",
            "authorization_reference": "",
            "attempts": 1,
        },
    },
    "transient_then_approved": {
        "script": [
            (503, {"status": "retry"}),
            (200, {"status": "approved", "authorization_reference": "baseline-ref"}),
        ],
        "expected": {
            "decision": "approved",
            "reason": "",
            "authorization_reference": "baseline-ref",
            "attempts": 2,
        },
    },
    "exhausted_unavailable": {
        "script": [
            (502, {"status": "retry"}),
            (503, {"status": "retry"}),
            (504, {"status": "retry"}),
        ],
        "expected": {
            "decision": "unavailable",
            "reason": "transport_exhausted",
            "authorization_reference": "",
            "attempts": 3,
        },
    },
}


def run_hand_baseline(mutants: list[str]) -> dict[str, Any]:
    original = os.environ.get("LEGACY_PAYMENT_MUTANT")
    results: list[dict[str, Any]] = []
    try:
        for mutant in ["CONTROL", *mutants]:
            if mutant == "CONTROL":
                os.environ.pop("LEGACY_PAYMENT_MUTANT", None)
            else:
                os.environ["LEGACY_PAYMENT_MUTANT"] = mutant
            failure: str | None = None
            failed_scenario: str | None = None
            for name, scenario in BASELINE_SCENARIOS.items():
                try:
                    _run_scenario(name, scenario)
                except Exception as exc:
                    failure = f"{type(exc).__name__}: {exc}"
                    failed_scenario = name
                    break
            results.append(
                {
                    "mutant_id": mutant,
                    "verdict": "green" if failure is None else "killed",
                    "first_failure_scenario": failed_scenario,
                    "error": failure,
                }
            )
    finally:
        if original is None:
            os.environ.pop("LEGACY_PAYMENT_MUTANT", None)
        else:
            os.environ["LEGACY_PAYMENT_MUTANT"] = original
    control = results[0]
    if control["verdict"] != "green":
        raise AssertionError(f"hand-written baseline control is red: {control}")
    killed = sum(row["verdict"] == "killed" for row in results[1:])
    return {
        "scenarios": list(BASELINE_SCENARIOS),
        "results": results,
        "killed": killed,
        "total": len(mutants),
        "score": killed / len(mutants),
    }


def _run_scenario(name: str, scenario: dict[str, Any]) -> None:
    script = list(scenario["script"])
    calls: list[dict[str, Any]] = []
    with _fake_session_send(script, calls):
        result = authorize_payment(
            payment_id="baseline-pay",
            amount=73,
            idempotency_key="baseline-idempotency",
        )
    expected = dict(scenario["expected"])
    assert result.as_dict() == expected, (
        f"{name} result mismatch: {result.as_dict()!r} != {expected!r}"
    )
    assert len(calls) == expected["attempts"], (
        f"{name} expected {expected['attempts']} attempts, observed {len(calls)}"
    )


@contextmanager
def _fake_session_send(
    script: list[tuple[int, dict[str, Any]]],
    calls: list[dict[str, Any]],
) -> Iterator[None]:
    def send(
        _session: requests.Session,
        prepared: requests.PreparedRequest,
        **kwargs: Any,
    ) -> requests.Response:
        body = json.loads(
            prepared.body.decode("utf-8")
            if isinstance(prepared.body, bytes)
            else str(prepared.body)
        )
        record = {
            "method": prepared.method,
            "url": prepared.url,
            "body": body,
            "key": prepared.headers.get("Idempotency-Key"),
            "timeout": kwargs.get("timeout"),
        }
        calls.append(record)
        assert record["method"] == "POST"
        assert str(record["url"]).endswith("/v1/payments")
        assert record["body"] == {"payment_id": "baseline-pay", "amount": 73}
        assert record["key"] == "baseline-idempotency"
        assert record["timeout"] == (0.25, 0.75)
        if not script:
            raise AssertionError("application exceeded hand-written response script")
        status, document = script.pop(0)
        response = requests.Response()
        response.status_code = status
        response.request = prepared
        response.url = str(prepared.url)
        response._content = json.dumps(document).encode("utf-8")
        response.headers["Content-Type"] = "application/json"
        return response

    with patch.object(requests.Session, "send", new=send):
        yield

