from __future__ import annotations

from typing import Any

from legacy_payment_http_app import authorize_payment
from spec_double_compiler.runtime import CaseRunResult

from .provider import active_scope


class PaymentHttpCaseAdapter:
    """Run the production call while the provider owns Session.send."""

    def setup(self, context: Any) -> None:
        if context.effects.get("PaymentHttpPort", object()) is not None:
            raise AssertionError("self-installed PaymentHttpPort must bind None")

    def run(self, case: Any, work_dir: Any = None) -> CaseRunResult:
        del work_dir
        params = dict(case.input.params)
        scope = active_scope()
        result = authorize_payment(
            payment_id=str(params["payment_id"]),
            amount=int(params["amount"]),
            idempotency_key=str(params["idempotency_key"]),
        )
        scope.record_application_result(result)
        scope.assert_complete()
        normalized = result.as_dict()
        normalized["authorization_reference"] = scope.normalized_reference(
            result.authorization_reference
        )
        observed_after = {
            "completed": True,
            "outcome": str(params["outcome"]),
            "decision": normalized["decision"],
            "reason": normalized["reason"],
            "referenceClass": normalized["authorization_reference"],
            "attempts": normalized["attempts"],
        }
        return CaseRunResult(output=normalized, after=observed_after)

