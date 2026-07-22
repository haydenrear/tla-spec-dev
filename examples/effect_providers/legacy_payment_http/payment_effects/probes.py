"""Unscored compatibility probes for paths outside Session.send."""

from __future__ import annotations

import socket
from typing import Any
from urllib.request import urlopen

from spec_double_compiler.effects import derive_effect_seed
from spec_double_compiler.runtime import EffectProviderContext

from .provider import OutboundSocketAttempt, payment_http_provider, patches_are_clean


def run_capability_probes(case: Any, transcript_path: str) -> dict[str, Any]:
    import os

    prior = os.environ.get("LEGACY_PAYMENT_TRANSCRIPT")
    os.environ["LEGACY_PAYMENT_TRANSCRIPT"] = transcript_path
    context = EffectProviderContext(
        port_name="PaymentHttpPort",
        action=str(case.input.action),
        case=case,
        work_dir=__import__("pathlib").Path(transcript_path).parent / "probe-work",
        iteration=0,
        root_seed=20260721,
        derived_seed=derive_effect_seed(
            20260721, str(case.name), 0, "PaymentHttpPort"
        ),
    )
    alternate: dict[str, Any] = {}
    raw: dict[str, Any] = {}
    try:
        scope = payment_http_provider.bind(context)
        with scope:
            try:
                urlopen("http://127.0.0.1:9/probe", timeout=0.1)
                alternate["outbound_succeeded"] = True
            except OutboundSocketAttempt as exc:
                alternate.update(
                    outbound_succeeded=False,
                    socket_guard_blocked=True,
                    error=str(exc),
                )
            try:
                sock = socket.socket()
                try:
                    sock.connect(("127.0.0.1", 9))
                    raw["outbound_succeeded"] = True
                finally:
                    sock.close()
            except OutboundSocketAttempt as exc:
                raw.update(
                    outbound_succeeded=False,
                    socket_guard_blocked=True,
                    error=str(exc),
                )
            alternate["session_send_calls"] = len(scope.requests)
            raw["session_send_calls"] = len(scope.requests)
            scope.mark_capability_probe_complete()
    finally:
        if prior is None:
            os.environ.pop("LEGACY_PAYMENT_TRANSCRIPT", None)
        else:
            os.environ["LEGACY_PAYMENT_TRANSCRIPT"] = prior
    return {
        "alternate_http_client": {
            **alternate,
            "bypasses_session_send": alternate.get("session_send_calls") == 0,
        },
        "raw_socket": {
            **raw,
            "bypasses_session_send": raw.get("session_send_calls") == 0,
        },
        "compatibility_only": True,
        "patches_clean_after_probes": patches_are_clean(),
        "outbound_socket_successes": sum(
            bool(item.get("outbound_succeeded")) for item in (alternate, raw)
        ),
    }
