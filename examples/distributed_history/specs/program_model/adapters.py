from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from ecommerce_backend.domain import EcommerceStore

# G-12: the block the scaffold emits, and this file did not carry.
#
# `scaffold_spec.py` substitutes `SKILL_ROOT_BOOTSTRAP` into every `adapters.py`
# it writes, because without it `from spec_double_compiler.runtime import ...`
# resolves under NO interpreter absent a hand-set `PYTHONPATH`. This file is the
# one `references/testgraph_adapters.md` calls "the concrete reference
# implementation" and `scaffold_spec.py` itself names as the worked example --
# and it had none of it.
#
# `G-10`'s shape exactly: the scaffold is right and the reference teaches
# otherwise. Round 2's `T3` established that agents learn the flag set by
# reading this example rather than from the tool; they learn adapter shape here
# too, and what they were learning could not be imported. Found by the round-002
# ticket agent, which hit it in its own scaffolded project.
#
# INSERTED PROGRAMMATICALLY from `scaffold_spec.SKILL_ROOT_BOOTSTRAP`, not
# retyped, and `tests/test_reference_adapters_carry_the_bootstrap.py` asserts
# the two stay byte-identical -- a second copy of a resolution order is a second
# thing to forget (`E-14`).
import os
import sys


def _spec_double_compiler_root() -> Path | None:
    """Where the spec-double-compiler skill is, in decreasing authority.

    `Path.home()` is deliberately LAST: a project home
    (`<repo>/.skill-manager`) or a worktree home
    (`<worktree>/.skill-manager`) must win over the operator's global
    `~/.skill-manager`, or this module reads a different build of the skill
    than the checkout was resolved against.

    Returns None only when no candidate holds the package; an inherited
    PYTHONPATH is then the last thing left to answer.
    """
    # THE ENCLOSING CHECKOUT FIRST, ahead of every home including an explicit
    # one. This block is copied into `adapters.py` files that live INSIDE the
    # spec-double-compiler repository as well as into downstream projects, and
    # in the former the package is a sibling of the checkout root. Without this
    # candidate the reference example imported the INSTALLED skill instead of
    # the checkout under review -- `sys.path.insert(0, home)` outranking the
    # repository whose tests were running -- which is the hazard the docstring
    # above warns about, produced by the code below it.
    #
    # Costs a downstream project nothing: no ancestor of a scaffolded project
    # holds a `spec_double_compiler` package, so this loop finds nothing and
    # resolution proceeds exactly as before. Found by the blind review of `#318`,
    # which also showed the reference example failing to import at all on any
    # checkout that does not happen to sit under the operator's home.
    for parent in Path(__file__).resolve().parents:
        if (parent / "spec_double_compiler").is_dir():
            return parent

    explicit = os.environ.get("SPEC_DOUBLE_COMPILER_HOME")
    if explicit:
        root = Path(explicit).expanduser()
        if not (root / "spec_double_compiler").is_dir():
            raise ModuleNotFoundError(
                f"SPEC_DOUBLE_COMPILER_HOME={explicit} holds no spec_double_compiler "
                "package. Point it at <home>/skills/spec-double-compiler, or unset it."
            )
        return root

    homes = []
    bound = os.environ.get("SKILL_MANAGER_HOME")
    if bound:
        homes.append(Path(bound).expanduser())
    # Nearest enclosing checkout home, so a project or worktree home is still
    # found from a bare shell that exported nothing.
    homes.extend(parent / ".skill-manager" for parent in Path(__file__).resolve().parents)
    homes.append(Path.home() / ".skill-manager")

    for home in homes:
        root = home / "skills" / "spec-double-compiler"
        if (root / "spec_double_compiler").is_dir():
            return root
    return None


def _ensure_spec_double_compiler() -> None:
    """Resolve BEFORE importing, not only after the import fails.

    Deciding this inside `except ModuleNotFoundError` would make the whole
    resolution order conditional on nothing else having already answered, so
    an inherited PYTHONPATH — or a CLI wrapper pinned to another home — would
    silently outrank both the explicit override and the bound home.
    """
    root = _spec_double_compiler_root()
    if root is not None:
        sys.path.insert(0, str(root))
    import spec_double_compiler  # noqa: F401


_ensure_spec_double_compiler()

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
        result = store.project_order(params["order"])
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
