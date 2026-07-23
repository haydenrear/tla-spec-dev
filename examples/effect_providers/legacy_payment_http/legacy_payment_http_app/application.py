"""A deliberately legacy-shaped payment client with module-owned requests.

The application owns request preparation, a ``requests.Session``, retries, and
response normalization.  The experiment provider patches exactly
``requests.Session.send``; no transport is injected into this module.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from typing import Any

import requests


DEFAULT_BASE_URL = "https://payments.example.test"
REQUEST_TIMEOUT = (0.25, 0.75)
TRANSIENT_STATUSES = frozenset({502, 503, 504})


@dataclass(frozen=True)
class PaymentResult:
    decision: str
    reason: str
    authorization_reference: str
    attempts: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _mutant() -> str:
    return os.environ.get("LEGACY_PAYMENT_MUTANT", "CONTROL")


def authorize_payment(
    *,
    payment_id: str,
    amount: int,
    idempotency_key: str,
    base_url: str = DEFAULT_BASE_URL,
    max_attempts: int = 3,
) -> PaymentResult:
    """Authorize once, retrying only modeled transient transport outcomes."""

    mutant = _mutant()
    method = "GET" if mutant == "PH-01" else "POST"
    path = "/v1/paymentz" if mutant == "PH-02" else "/v1/payments"
    payload_amount: int | str = str(amount) if mutant == "PH-03" else amount
    attempt_limit = max_attempts
    if mutant == "PH-09":
        attempt_limit += 1
    elif mutant == "PH-10":
        attempt_limit -= 1

    session = requests.Session()
    session.trust_env = False
    for attempt in range(1, attempt_limit + 1):
        headers: dict[str, str] = {"Accept": "application/json"}
        if mutant != "PH-04":
            key = (
                f"{idempotency_key}-retry-{attempt}"
                if mutant == "PH-05" and attempt > 1
                else idempotency_key
            )
            headers["Idempotency-Key"] = key
        request = requests.Request(
            method=method,
            url=base_url.rstrip("/") + path,
            headers=headers,
            json={"payment_id": payment_id, "amount": payload_amount},
        )
        prepared = session.prepare_request(request)
        try:
            if mutant == "PH-06":
                response = session.send(prepared)
            else:
                response = session.send(prepared, timeout=REQUEST_TIMEOUT)
        except (requests.ConnectTimeout, requests.ReadTimeout):
            if mutant == "PH-07" or attempt == attempt_limit:
                return PaymentResult("unavailable", "transport_exhausted", "", attempt)
            continue

        if response.status_code in TRANSIENT_STATUSES:
            if mutant == "PH-07" or attempt == attempt_limit:
                return PaymentResult("unavailable", "transport_exhausted", "", attempt)
            continue

        result = _normalize_terminal_response(response, attempt)
        if mutant == "PH-08" and response.status_code in {400, 402} and attempt < attempt_limit:
            continue
        if mutant == "PH-11" and result.decision in {"declined", "bad_request", "malformed_response"}:
            return PaymentResult("approved", "", "mutant-approved", attempt)
        if mutant == "PH-12" and result.decision == "approved":
            return PaymentResult(
                result.decision,
                result.reason,
                result.authorization_reference[:-1],
                result.attempts,
            )
        return result

    return PaymentResult("unavailable", "transport_exhausted", "", attempt_limit)


def _normalize_terminal_response(response: requests.Response, attempts: int) -> PaymentResult:
    try:
        document = response.json()
    except (requests.JSONDecodeError, json.JSONDecodeError, ValueError):
        return PaymentResult("malformed_response", "invalid_json", "", attempts)
    if not isinstance(document, dict):
        return PaymentResult("malformed_response", "invalid_json", "", attempts)

    status = document.get("status")
    if response.status_code in {200, 201, 409} and status == "approved":
        reference = document.get("authorization_reference")
        if not isinstance(reference, str) or not reference:
            return PaymentResult("malformed_response", "invalid_json", "", attempts)
        return PaymentResult("approved", "", reference, attempts)
    if response.status_code == 402 and status == "declined":
        return PaymentResult("declined", str(document.get("reason", "declined")), "", attempts)
    if response.status_code == 400:
        return PaymentResult("bad_request", str(document.get("reason", "invalid_request")), "", attempts)
    return PaymentResult("malformed_response", "unexpected_response", "", attempts)
