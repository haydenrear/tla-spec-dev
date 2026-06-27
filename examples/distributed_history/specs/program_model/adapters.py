from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from ecommerce_backend.domain import EcommerceStore
from spec_double_compiler.runtime import CaseRunResult


def _state(value: Any) -> dict[str, Any]:
    return json.loads(json.dumps(value, sort_keys=True))


class _InternalAdapter:
    def setup_all(self, context: Any) -> None:
        context.shared["setup_all_called"] = True

    def teardown_all(self, context: Any) -> None:
        context.shared["teardown_all_called"] = True

    def run(self, case: Any, work_dir: Path | None = None) -> CaseRunResult:
        store = EcommerceStore()
        try:
            store.load_state(case.before)
            output = self.apply(store, case.input.params)
            return CaseRunResult(output=output, after=store.snapshot())
        finally:
            store.close()

    def apply(self, store: EcommerceStore, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class CreateAccountInternalAdapter(_InternalAdapter):
    def apply(self, store: EcommerceStore, params: dict[str, Any]) -> dict[str, Any]:
        result = store.create_account(params["account"])
        return {"status": result.status, "body": result.body}


class AddCartItemInternalAdapter(_InternalAdapter):
    def apply(self, store: EcommerceStore, params: dict[str, Any]) -> dict[str, Any]:
        result = store.add_cart_item(params["account"], params["sku"])
        return {"status": result.status, "body": result.body}


class CheckoutInternalAdapter(_InternalAdapter):
    def apply(self, store: EcommerceStore, params: dict[str, Any]) -> dict[str, Any]:
        result = store.checkout(params["account"], params["order"])
        return {"status": result.status, "body": result.body}


class ProjectOrderInternalAdapter(_InternalAdapter):
    def apply(self, store: EcommerceStore, params: dict[str, Any]) -> dict[str, Any]:
        result = store.process_outbox()
        return {"status": result.status, "body": result.body}


class _HttpAdapter:
    def setup_all(self, context: Any) -> None:
        base_url = os.environ.get("ECOMMERCE_BASE_URL", "http://127.0.0.1:18080")
        context.shared["base_url"] = base_url.rstrip("/")
        self._wait_for_health(context.shared["base_url"])
        self._post(context.shared["base_url"], "/debug/traffic/reset", {})
        self._post(context.shared["base_url"], "/debug/reset", {})

    def teardown_all(self, context: Any) -> None:
        base_url = context.shared.get("base_url") or os.environ.get("ECOMMERCE_BASE_URL", "http://127.0.0.1:18080")
        try:
            self._post(base_url.rstrip("/"), "/debug/reset", {})
        except Exception:
            return

    def setup(self, context: Any) -> None:
        base_url = context.shared["base_url"]
        self._post(base_url, "/debug/reset", {})
        self._post(base_url, "/debug/load", {"state": context.case.before})

    def teardown(self, context: Any) -> None:
        self._post(context.shared["base_url"], "/debug/reset", {})

    def run(self, case: Any, work_dir: Path | None = None) -> CaseRunResult:
        base_url = os.environ.get("ECOMMERCE_BASE_URL", "http://127.0.0.1:18080").rstrip("/")
        result = self.apply(base_url, case.input.params)
        return CaseRunResult(output=result)

    def apply(self, base_url: str, params: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def _wait_for_health(self, base_url: str) -> None:
        deadline = time.time() + 20
        last_error: BaseException | None = None
        while time.time() < deadline:
            try:
                self._get(base_url, "/health")
                return
            except Exception as exc:
                last_error = exc
                time.sleep(0.2)
        raise RuntimeError(f"service did not become healthy at {base_url}: {last_error}")

    def _get(self, base_url: str, path: str) -> dict[str, Any]:
        with urllib.request.urlopen(base_url + path, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def _post(self, base_url: str, path: str, body: dict[str, Any]) -> dict[str, Any]:
        payload = json.dumps(body, sort_keys=True).encode("utf-8")
        request = urllib.request.Request(
            base_url + path,
            data=payload,
            headers={"content-type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return {
                    "status": response.status,
                    "body": json.loads(response.read().decode("utf-8")),
                }
        except urllib.error.HTTPError as exc:
            return {
                "status": exc.code,
                "body": json.loads(exc.read().decode("utf-8")),
            }


class CreateAccountHttpAdapter(_HttpAdapter):
    def apply(self, base_url: str, params: dict[str, Any]) -> dict[str, Any]:
        return self._post(base_url, "/accounts", {"account": params["account"]})


class AddCartItemHttpAdapter(_HttpAdapter):
    def apply(self, base_url: str, params: dict[str, Any]) -> dict[str, Any]:
        return self._post(base_url, "/cart/items", {"account": params["account"], "sku": params["sku"]})


class CheckoutHttpAdapter(_HttpAdapter):
    def apply(self, base_url: str, params: dict[str, Any]) -> dict[str, Any]:
        return self._post(base_url, "/checkout", {"account": params["account"], "order": params["order"]})


class RunFulfillmentWorkerHttpAdapter(_HttpAdapter):
    def apply(self, base_url: str, params: dict[str, Any]) -> dict[str, Any]:
        return self._post(base_url, "/worker/drain", {"limit": params.get("limit", 100)})


class ExpectedClusterProjection:
    def expected_state(self, context: Any) -> dict[str, Any]:
        return _visible_projection(context.case.after)


class ClusterStateProjector:
    def observe(self, context: Any) -> dict[str, Any]:
        base_url = context.shared.get("base_url") or os.environ.get("ECOMMERCE_BASE_URL", "http://127.0.0.1:18080")
        with urllib.request.urlopen(base_url.rstrip("/") + "/debug/state", timeout=5) as response:
            return _visible_projection(json.loads(response.read().decode("utf-8")))


class ProjectedStateAssertion:
    def assert_state(self, context: Any) -> None:
        expected = _state(context.expected)
        actual = _state(context.actual)
        artifact = context.work_dir / "program-state.json"
        payload = {
            "case": context.case.name,
            "action": context.case.input.action,
            "params": dict(context.case.input.params),
            "expected_program_state": expected,
            "actual_projected_program_state": actual,
            "adapter_result": _case_result_payload(context.result),
            "matched": actual == expected,
        }
        artifact.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if actual != expected:
            raise AssertionError(f"projected cluster state mismatch for {context.case.name}; wrote {artifact}")


def _visible_projection(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "accounts": list(state.get("accounts", [])),
        "carts": dict(state.get("carts", {})),
        "orders": dict(state.get("orders", {})),
        "outbox": list(state.get("outbox", [])),
        "projections": dict(state.get("projections", {})),
    }


def _case_result_payload(result: CaseRunResult | None) -> dict[str, Any] | None:
    if result is None:
        return None
    return {
        "output": result.output,
        "after": result.after,
        "semantic_output": result.semantic_output,
    }
