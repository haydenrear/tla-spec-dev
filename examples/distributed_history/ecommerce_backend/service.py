from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
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


class EcommerceHandler(BaseHTTPRequestHandler):
    store: EcommerceStore

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/health":
            _write_json(self, 200, {"ok": True})
            return
        if path == "/debug/state":
            _write_json(self, 200, self.store.snapshot())
            return
        _write_json(self, 404, {"error": "not_found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        body = _read_json(self)
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


def make_server() -> ThreadingHTTPServer:
    port = int(os.environ.get("ECOMMERCE_PORT", "18080"))
    db_path = os.environ.get("ECOMMERCE_DB", "/tmp/ecommerce-example.db")
    EcommerceHandler.store = EcommerceStore(db_path)
    return ThreadingHTTPServer(("0.0.0.0", port), EcommerceHandler)


def main() -> int:
    server = make_server()
    try:
        server.serve_forever()
    finally:
        server.server_close()
        EcommerceHandler.store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
