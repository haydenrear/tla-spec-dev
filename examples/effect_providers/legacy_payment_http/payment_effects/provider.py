"""Deterministic, self-installing ``requests.Session.send`` effect provider."""

from __future__ import annotations

from contextlib import ExitStack
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import random
import socket
from time import perf_counter
from typing import Any
from unittest.mock import patch
from urllib.parse import urlsplit

import requests

from spec_double_compiler.runtime import EffectProviderContext


ORIGINAL_SESSION_SEND = requests.Session.send
ORIGINAL_SOCKET_CONNECT = socket.socket.connect
ORIGINAL_CREATE_CONNECTION = socket.create_connection
_ACTIVE: PaymentHttpScope | None = None


ACTION_OUTCOMES = {
    "AuthorizeApproved": "approved",
    "AuthorizeDeclined": "declined",
    "AuthorizeBadRequest": "bad_request",
    "AuthorizeTransientThenApproved": "transient_then_approved",
    "AuthorizeTimeoutThenDuplicateApproved": "timeout_then_duplicate_approved",
    "AuthorizeExhaustedUnavailable": "exhausted_unavailable",
    "AuthorizeMalformedResponse": "malformed_response",
}


class ProviderLocalAssertion(AssertionError):
    detector = "provider_local_assertion"

    def __init__(self, message: str) -> None:
        super().__init__(f"DETECTOR[provider_local_assertion] {message}")


class OutboundSocketAttempt(RuntimeError):
    detector = "passive_bypass_detector"


def active_scope() -> "PaymentHttpScope":
    if _ACTIVE is None:
        raise RuntimeError("PaymentHttpPort provider is not active")
    return _ACTIVE


class PaymentHttpProvider:
    def bind(self, context: EffectProviderContext) -> "PaymentHttpScope":
        return PaymentHttpScope(context)


payment_http_provider = PaymentHttpProvider()


class PaymentHttpScope:
    def __init__(self, context: EffectProviderContext) -> None:
        self.context = context
        self.outcome = ACTION_OUTCOMES[context.action]
        self.params = dict(context.case.input.params)
        self.expected_output = dict(context.case.output)
        self.expected_attempts = int(self.expected_output["attempts"])
        rng = random.Random(context.derived_seed)
        self.transient_status = rng.choice([502, 503, 504])
        self.timeout_type = rng.choice([requests.ConnectTimeout, requests.ReadTimeout])
        self.malformed_bytes = rng.choice(
            [b"{", b"not-json", b"[1,", b'"unterminated']
        )
        self.header_name = rng.choice(
            ["X-Request-Id", "x-request-id", "X-ReQuEsT-Id"]
        )
        self.layout = rng.choice(["compact", "spaced", "indented", "reversed"])
        self.authorization_reference = f"auth-\u0394-{rng.getrandbits(80):020x}"
        self.requests: list[dict[str, Any]] = []
        self.responses: list[dict[str, Any]] = []
        self.detectors: list[str] = []
        self.application_result: dict[str, Any] | None = None
        self.outbound_socket_attempts: list[str] = []
        self._stack: ExitStack | None = None
        self._started = 0.0
        self._asserted_complete = False

    def __enter__(self) -> None:
        global _ACTIVE
        if _ACTIVE is not None:
            raise RuntimeError("PaymentHttpPort provider scopes may not overlap")
        self._started = perf_counter()
        stack = ExitStack()
        stack.__enter__()
        self._stack = stack
        _ACTIVE = self
        try:
            scope = self

            def patched_send(
                session: requests.Session,
                request: requests.PreparedRequest,
                **kwargs: Any,
            ) -> requests.Response:
                return scope._send(session, request, **kwargs)

            def patched_socket_connect(sock: socket.socket, address: Any) -> None:
                scope._socket_connect(sock, address)

            def patched_create_connection(address: Any, *args: Any, **kwargs: Any) -> None:
                scope._create_connection(address, *args, **kwargs)

            stack.enter_context(patch.object(requests.Session, "send", new=patched_send))
            stack.enter_context(patch.object(socket.socket, "connect", new=patched_socket_connect))
            stack.enter_context(patch.object(socket, "create_connection", new=patched_create_connection))
        except BaseException:
            _ACTIVE = None
            stack.__exit__(*__import__("sys").exc_info())
            self._stack = None
            raise
        return None

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool:
        global _ACTIVE
        assertion_error: BaseException | None = None
        if exc is None and not self._asserted_complete:
            try:
                self.assert_complete()
            except BaseException as caught:
                assertion_error = caught
        stack, self._stack = self._stack, None
        try:
            if stack is not None:
                stack.__exit__(exc_type, exc, traceback)
        finally:
            _ACTIVE = None
            elapsed_ms = (perf_counter() - self._started) * 1000.0
            leaked = self._patch_leaks()
            if leaked:
                self.detectors.append("cleanup_detector")
                if assertion_error is None and exc is None:
                    assertion_error = AssertionError(
                        "DETECTOR[cleanup_detector] leaked patches: " + ", ".join(leaked)
                    )
            self._write_transcript(elapsed_ms=elapsed_ms, leaked_patches=leaked, incoming=exc)
        if assertion_error is not None:
            raise assertion_error
        return False

    def record_application_result(self, result: Any) -> None:
        self.application_result = asdict(result)

    def assert_complete(self) -> None:
        actual = len(self.requests)
        if actual != self.expected_attempts:
            self._fail(
                f"expected {self.expected_attempts} Session.send calls for {self.outcome}, observed {actual}"
            )
        self._asserted_complete = True

    def mark_capability_probe_complete(self) -> None:
        """Declare that an unscored bypass probe intentionally made no semantic send."""

        self._asserted_complete = True

    def normalized_reference(self, concrete: str) -> str:
        if not concrete:
            return "none"
        if concrete == self.authorization_reference:
            return "opaque"
        return "invalid"

    def _send(self, _session: requests.Session, request: requests.PreparedRequest, **kwargs: Any) -> requests.Response:
        attempt = len(self.requests) + 1
        record = self._request_record(request, kwargs)
        self.requests.append(record)
        if attempt > self.expected_attempts:
            self._fail(
                f"unexpected Session.send attempt {attempt}; modeled maximum is {self.expected_attempts}"
            )
        self._assert_request(record, attempt)

        if self.outcome == "transient_then_approved" and attempt == 1:
            return self._response(request, self.transient_status, {"status": "retry"})
        if self.outcome == "timeout_then_duplicate_approved" and attempt == 1:
            error = self.timeout_type(f"scripted {self.timeout_type.__name__}", request=request)
            self.responses.append({"exception": self.timeout_type.__name__})
            raise error
        if self.outcome == "exhausted_unavailable":
            if (self.context.derived_seed + attempt) % 2:
                return self._response(request, self.transient_status, {"status": "retry"})
            error = self.timeout_type(f"scripted {self.timeout_type.__name__}", request=request)
            self.responses.append({"exception": self.timeout_type.__name__})
            raise error
        if self.outcome == "declined":
            return self._response(
                request,
                402,
                {"status": "declined", "reason": "insufficient_funds"},
            )
        if self.outcome == "bad_request":
            return self._response(
                request,
                400,
                {"status": "bad_request", "reason": "invalid_request"},
            )
        if self.outcome == "malformed_response":
            return self._response(request, 200, None, raw=self.malformed_bytes)
        status = 409 if self.outcome == "timeout_then_duplicate_approved" else 200
        return self._response(
            request,
            status,
            {
                "status": "approved",
                "authorization_reference": self.authorization_reference,
                "duplicate": status == 409,
            },
        )

    def _request_record(
        self,
        request: requests.PreparedRequest,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        body = request.body
        if isinstance(body, bytes):
            body_text = body.decode("utf-8", errors="replace")
        else:
            body_text = "" if body is None else str(body)
        try:
            parsed_body: Any = json.loads(body_text)
        except ValueError:
            parsed_body = {"__invalid_json__": body_text}
        return {
            "method": request.method,
            "url": request.url,
            "path": urlsplit(str(request.url)).path,
            "body": parsed_body,
            "idempotency_key": request.headers.get("Idempotency-Key"),
            "content_type": request.headers.get("Content-Type"),
            "timeout_present": "timeout" in kwargs,
            "timeout": _plain(kwargs.get("timeout")),
        }

    def _assert_request(self, record: dict[str, Any], attempt: int) -> None:
        if record["method"] != "POST":
            self._fail(f"attempt {attempt} method {record['method']!r} is not POST")
        if record["path"] != "/v1/payments":
            self._fail(f"attempt {attempt} path {record['path']!r} is not /v1/payments")
        expected_body = {
            "payment_id": self.params["payment_id"],
            "amount": self.params["amount"],
        }
        if record["body"] != expected_body:
            self._fail(
                f"attempt {attempt} JSON body {record['body']!r} does not match {expected_body!r}"
            )
        if record["idempotency_key"] != self.params["idempotency_key"]:
            self._fail(
                f"attempt {attempt} Idempotency-Key {record['idempotency_key']!r} "
                f"does not match {self.params['idempotency_key']!r}"
            )
        if not record["timeout_present"] or record["timeout"] != [0.25, 0.75]:
            self._fail(
                f"attempt {attempt} timeout must be [0.25, 0.75], observed {record['timeout']!r}"
            )

    def _response(
        self,
        request: requests.PreparedRequest,
        status: int,
        document: dict[str, Any] | None,
        *,
        raw: bytes | None = None,
    ) -> requests.Response:
        response = requests.Response()
        response.status_code = status
        response.request = request
        response.url = str(request.url)
        response.headers[self.header_name] = f"req-{self.context.iteration}"
        response.headers["Content-Type"] = "application/json"
        if raw is not None:
            body = raw
        else:
            body = self._render_json(document or {})
        response._content = body
        response.encoding = "utf-8"
        self.responses.append(
            {
                "status": status,
                "header_name": self.header_name,
                "layout": self.layout,
                "body_sha256": hashlib.sha256(body).hexdigest(),
            }
        )
        return response

    def _render_json(self, document: dict[str, Any]) -> bytes:
        rendered = dict(document)
        if self.layout == "reversed":
            rendered = dict(reversed(list(rendered.items())))
        if self.layout == "compact":
            text = json.dumps(rendered, ensure_ascii=False, separators=(",", ":"))
        elif self.layout == "indented":
            text = json.dumps(rendered, ensure_ascii=False, indent=2)
        else:
            text = json.dumps(rendered, ensure_ascii=False)
        return text.encode("utf-8")

    def _socket_connect(self, _socket: socket.socket, address: Any) -> None:
        self.outbound_socket_attempts.append(repr(address))
        raise OutboundSocketAttempt(f"blocked socket.connect to {address!r}")

    def _create_connection(self, address: Any, *args: Any, **kwargs: Any) -> None:
        self.outbound_socket_attempts.append(repr(address))
        raise OutboundSocketAttempt(f"blocked socket.create_connection to {address!r}")

    def _fail(self, message: str) -> None:
        self.detectors.append("provider_local_assertion")
        raise ProviderLocalAssertion(message)

    def _patch_leaks(self) -> list[str]:
        leaks: list[str] = []
        if requests.Session.send is not ORIGINAL_SESSION_SEND:
            leaks.append("requests.Session.send")
        if socket.socket.connect is not ORIGINAL_SOCKET_CONNECT:
            leaks.append("socket.socket.connect")
        if socket.create_connection is not ORIGINAL_CREATE_CONNECTION:
            leaks.append("socket.create_connection")
        return leaks

    def _write_transcript(
        self,
        *,
        elapsed_ms: float,
        leaked_patches: list[str],
        incoming: BaseException | None,
    ) -> None:
        payload: dict[str, Any] = {
            "case": str(self.context.case.name),
            "action": self.context.action,
            "outcome": self.outcome,
            "iteration": self.context.iteration,
            "root_seed": self.context.root_seed,
            "derived_seed": self.context.derived_seed,
            "seed_version": self.context.seed_version,
            "representative": {
                "transient_status": self.transient_status,
                "timeout_type": self.timeout_type.__name__,
                "malformed_sha256": hashlib.sha256(self.malformed_bytes).hexdigest(),
                "header_name": self.header_name,
                "layout": self.layout,
                "authorization_reference": self.authorization_reference,
            },
            "requests": self.requests,
            "responses": self.responses,
            "application_result": self.application_result,
            "detectors": sorted(set(self.detectors)),
            "incoming_error": None if incoming is None else f"{type(incoming).__name__}: {incoming}",
            "outbound_socket_attempts": list(self.outbound_socket_attempts),
            "leaked_patches": leaked_patches,
            "provider_state_after_run": (
                "clean" if _ACTIVE is None and not leaked_patches else "leaked"
            ),
        }
        canonical = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        payload["transcript_digest"] = hashlib.sha256(canonical).hexdigest()
        payload["elapsed_ms"] = elapsed_ms
        destination = os.environ.get("LEGACY_PAYMENT_TRANSCRIPT")
        if destination:
            path = Path(destination)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def patches_are_clean() -> bool:
    return (
        _ACTIVE is None
        and requests.Session.send is ORIGINAL_SESSION_SEND
        and socket.socket.connect is ORIGINAL_SOCKET_CONNECT
        and socket.create_connection is ORIGINAL_CREATE_CONNECTION
    )


def _plain(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _plain(inner) for key, inner in value.items()}
    return value
