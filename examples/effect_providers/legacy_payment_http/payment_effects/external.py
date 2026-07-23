"""Out-of-process External adapter using a real loopback HTTP server."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
from threading import Thread
from typing import Any

from spec_double_compiler.runtime import CaseRunResult


class PaymentHttpExternalAdapter:
    def run(self, case: Any, work_dir: Path | None = None) -> CaseRunResult:
        del work_dir
        params = dict(case.input.params)
        outcome = str(params["outcome"])
        script = _script_for(outcome)
        handler = _handler_for(script)
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        project_root = Path(__file__).resolve().parents[1]
        env = os.environ.copy()
        env.pop("LEGACY_PAYMENT_MUTANT", None)
        try:
            command = [
                sys.executable,
                "-m",
                "legacy_payment_http_app",
                "--payment-id",
                str(params["payment_id"]),
                "--amount",
                str(params["amount"]),
                "--idempotency-key",
                str(params["idempotency_key"]),
                "--base-url",
                f"http://127.0.0.1:{server.server_port}",
            ]
            completed = subprocess.run(
                command,
                cwd=project_root,
                env=env,
                text=True,
                capture_output=True,
                check=False,
                timeout=15,
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
        if completed.returncode != 0:
            raise AssertionError(completed.stderr)
        result = json.loads(completed.stdout)
        result["authorization_reference"] = (
            "opaque" if result.get("authorization_reference") else "none"
        )
        observed_after = {
            "completed": True,
            "outcome": outcome,
            "decision": result["decision"],
            "reason": result["reason"],
            "referenceClass": result["authorization_reference"],
            "attempts": result["attempts"],
        }
        return CaseRunResult(output=result, after=observed_after)


def _script_for(outcome: str) -> list[tuple[int, bytes]]:
    approved = _json_bytes(
        {"status": "approved", "authorization_reference": "external-auth-ref"}
    )
    if outcome == "approved":
        return [(200, approved)]
    if outcome == "declined":
        return [(402, _json_bytes({"status": "declined", "reason": "insufficient_funds"}))]
    if outcome == "bad_request":
        return [(400, _json_bytes({"status": "bad_request", "reason": "invalid_request"}))]
    if outcome == "transient_then_approved":
        return [(503, _json_bytes({"status": "retry"})), (200, approved)]
    if outcome == "timeout_then_duplicate_approved":
        duplicate = _json_bytes(
            {
                "status": "approved",
                "authorization_reference": "external-auth-ref",
                "duplicate": True,
            }
        )
        return [(504, _json_bytes({"status": "retry"})), (409, duplicate)]
    if outcome == "exhausted_unavailable":
        retry = _json_bytes({"status": "retry"})
        return [(502, retry), (503, retry), (504, retry)]
    return [(200, b"{")]


def _handler_for(script: list[tuple[int, bytes]]) -> type[BaseHTTPRequestHandler]:
    responses = list(script)

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            self.rfile.read(length)
            status, body = responses.pop(0) if responses else script[-1]
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, _format: str, *_args: Any) -> None:
            return None

    return Handler


def _json_bytes(value: dict[str, Any]) -> bytes:
    return json.dumps(value, separators=(",", ":")).encode("utf-8")

