from __future__ import annotations

import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
import urllib.error
import urllib.request
from urllib.parse import urlparse

from .domain import EcommerceStore


def _read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("content-length", "0"))
    if length == 0:
        return {}
    return json.loads(handler.rfile.read(length).decode("utf-8"))


def _write_json(handler: BaseHTTPRequestHandler, status: int, body: dict[str, Any]) -> None:
    payload = json.dumps(body, sort_keys=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("content-type", "application/json")
    handler.send_header("content-length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


def _request_json(method: str, base_url: str, path: str, body: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body, sort_keys=True).encode("utf-8")
        headers["content-type"] = "application/json"
    request = urllib.request.Request(base_url.rstrip("/") + path, data=data, headers=headers, method=method)
    deadline = time.time() + 10
    while True:
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8"))
        except (OSError, TimeoutError, urllib.error.URLError):
            if time.time() >= deadline:
                raise
            time.sleep(0.2)


def _forward(handler: BaseHTTPRequestHandler, base_url: str, path: str, body: dict[str, Any]) -> None:
    status, response_body = _request_json("POST", base_url, path, body)
    _write_json(handler, status, response_body)


class EcommerceHandler(BaseHTTPRequestHandler):
    store: EcommerceStore
    role: str = "monolith"
    queue_events: list[dict[str, Any]] = []

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            _write_json(self, 200, {"ok": True, "role": self.role})
            return
        if path == "/debug/state" and self.role in {"monolith", "database"}:
            _write_json(self, 200, self.store.snapshot())
            return
        if path == "/debug/state" and self.role == "queue":
            _write_json(self, 200, {"transport_queue": list(self.queue_events)})
            return
        if path == "/debug/state" and self.role == "gateway":
            status, state = _request_json("GET", _database_url(), "/debug/state")
            if status != 200:
                _write_json(self, status, state)
                return
            queue_status, queue_state = _request_json("GET", _queue_url(), "/debug/state")
            if queue_status == 200:
                state["transport_queue"] = queue_state.get("transport_queue", [])
            _write_json(self, 200, state)
            return
        _write_json(self, 404, {"error": "not_found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        body = _read_json(self)
        if self.role == "monolith":
            self._post_monolith(path, body)
            return
        if self.role == "database":
            self._post_database(path, body)
            return
        if self.role == "queue":
            self._post_queue(path, body)
            return
        if self.role == "account":
            self._post_account(path, body)
            return
        if self.role == "cart":
            self._post_cart(path, body)
            return
        if self.role == "checkout":
            self._post_checkout(path, body)
            return
        if self.role == "worker":
            self._post_worker(path, body)
            return
        if self.role == "gateway":
            self._post_gateway(path, body)
            return
        _write_json(self, 404, {"error": "unknown_role", "role": self.role})

    def _post_monolith(self, path: str, body: dict[str, Any]) -> None:
        if path == "/accounts":
            result = self.store.create_account(body["account"])
            _write_json(self, result.status, result.body)
            return
        if path == "/cart/items":
            result = self.store.add_cart_item(body["account"], body["sku"])
            _write_json(self, result.status, result.body)
            return
        if path == "/checkout":
            result = self.store.checkout(body["account"], body["order"])
            _write_json(self, result.status, result.body)
            return
        if path == "/worker/drain":
            result = self.store.process_outbox(int(body.get("limit", 100)))
            _write_json(self, result.status, result.body)
            return
        if path == "/debug/reset":
            self.store.reset()
            _write_json(self, 200, {"ok": True})
            return
        if path == "/debug/load":
            self.store.load_state(body.get("state", body))
            _write_json(self, 200, {"ok": True})
            return
        _write_json(self, 404, {"error": "not_found"})

    def _post_database(self, path: str, body: dict[str, Any]) -> None:
        self._post_monolith(path, body)

    def _post_queue(self, path: str, body: dict[str, Any]) -> None:
        if path == "/queue/enqueue":
            event = {"order_id": body["order_id"], "event": body.get("event", "OrderAccepted")}
            self.queue_events.append(event)
            _write_json(self, 202, {"queued": 1, "event": event})
            return
        if path == "/queue/drain":
            limit = int(body.get("limit", 100))
            events = self.queue_events[:limit]
            del self.queue_events[:limit]
            _write_json(self, 200, {"processed": len(events), "events": events})
            return
        if path == "/debug/reset":
            self.queue_events.clear()
            _write_json(self, 200, {"ok": True})
            return
        if path == "/debug/load":
            state = body.get("state", body)
            self.queue_events[:] = list(state.get("outbox", []))
            _write_json(self, 200, {"ok": True})
            return
        _write_json(self, 404, {"error": "not_found"})

    def _post_account(self, path: str, body: dict[str, Any]) -> None:
        if path == "/accounts":
            _forward(self, _database_url(), "/accounts", body)
            return
        _write_json(self, 404, {"error": "not_found"})

    def _post_cart(self, path: str, body: dict[str, Any]) -> None:
        if path == "/cart/items":
            _forward(self, _database_url(), "/cart/items", body)
            return
        _write_json(self, 404, {"error": "not_found"})

    def _post_checkout(self, path: str, body: dict[str, Any]) -> None:
        if path == "/checkout":
            status, response_body = _request_json("POST", _database_url(), "/checkout", body)
            if status == 202:
                _request_json(
                    "POST",
                    _queue_url(),
                    "/queue/enqueue",
                    {"order_id": body["order"], "event": "OrderAccepted"},
                )
            _write_json(self, status, response_body)
            return
        _write_json(self, 404, {"error": "not_found"})

    def _post_worker(self, path: str, body: dict[str, Any]) -> None:
        if path == "/worker/drain":
            status, response_body = _request_json("POST", _queue_url(), "/queue/drain", body)
            if status != 200:
                _write_json(self, status, response_body)
                return
            processed = 0
            for _event in response_body.get("events", []):
                db_status, db_body = _request_json("POST", _database_url(), "/worker/drain", {"limit": 1})
                if db_status != 200:
                    _write_json(self, db_status, db_body)
                    return
                processed += int(db_body.get("processed", 0))
            _write_json(self, 200, {"processed": processed})
            return
        _write_json(self, 404, {"error": "not_found"})

    def _post_gateway(self, path: str, body: dict[str, Any]) -> None:
        if path == "/accounts":
            _forward(self, _account_url(), "/accounts", body)
            return
        if path == "/cart/items":
            _forward(self, _cart_url(), "/cart/items", body)
            return
        if path == "/checkout":
            _forward(self, _checkout_url(), "/checkout", body)
            return
        if path == "/worker/drain":
            _forward(self, _worker_url(), "/worker/drain", body)
            return
        if path == "/debug/reset":
            _request_json("POST", _database_url(), "/debug/reset", {})
            _request_json("POST", _queue_url(), "/debug/reset", {})
            _write_json(self, 200, {"ok": True})
            return
        if path == "/debug/load":
            state = body.get("state", body)
            _request_json("POST", _database_url(), "/debug/load", {"state": state})
            _request_json("POST", _queue_url(), "/debug/load", {"state": state})
            _write_json(self, 200, {"ok": True})
            return
        _write_json(self, 404, {"error": "not_found"})


def make_server() -> ThreadingHTTPServer:
    port = int(os.environ.get("ECOMMERCE_PORT", "18080"))
    db_path = os.environ.get("ECOMMERCE_DB", "/tmp/ecommerce-example.db")
    EcommerceHandler.role = os.environ.get("ECOMMERCE_ROLE", "monolith")
    if EcommerceHandler.role in {"monolith", "database"}:
        EcommerceHandler.store = EcommerceStore(db_path)
    return ThreadingHTTPServer(("0.0.0.0", port), EcommerceHandler)


def main() -> int:
    server = make_server()
    try:
        server.serve_forever()
    finally:
        server.server_close()
        store = getattr(EcommerceHandler, "store", None)
        if store is not None:
            store.close()
    return 0


def _database_url() -> str:
    return os.environ.get("ECOMMERCE_DATABASE_URL", "http://database-service")


def _queue_url() -> str:
    return os.environ.get("ECOMMERCE_QUEUE_URL", "http://queue-service")


def _account_url() -> str:
    return os.environ.get("ECOMMERCE_ACCOUNT_URL", "http://account-service")


def _cart_url() -> str:
    return os.environ.get("ECOMMERCE_CART_URL", "http://cart-service")


def _checkout_url() -> str:
    return os.environ.get("ECOMMERCE_CHECKOUT_URL", "http://checkout-service")


def _worker_url() -> str:
    return os.environ.get("ECOMMERCE_WORKER_URL", "http://worker-service")


if __name__ == "__main__":
    raise SystemExit(main())
