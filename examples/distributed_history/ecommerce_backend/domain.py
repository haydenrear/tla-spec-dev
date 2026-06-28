from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EMPTY_STATE = {
    "accounts": [],
    "carts": {},
    "orders": {},
    "outbox": [],
    "projections": {},
}


@dataclass(frozen=True)
class OperationResult:
    status: int
    body: dict[str, Any]


class EcommerceStore:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = str(db_path or ":memory:")
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def close(self) -> None:
        self._conn.close()

    def _init_schema(self) -> None:
        with self._conn:
            self._conn.execute("create table if not exists accounts (account_id text primary key)")
            self._conn.execute(
                "create table if not exists cart_items (account_id text not null, sku text not null, qty integer not null)"
            )
            self._conn.execute(
                "create table if not exists orders (order_id text primary key, account_id text not null, items_json text not null, status text not null)"
            )
            self._conn.execute(
                "create table if not exists outbox (order_id text primary key, event_name text not null)"
            )
            self._conn.execute(
                "create table if not exists projections (order_id text primary key, visible_status text not null)"
            )

    def reset(self) -> None:
        with self._conn:
            for table in ("accounts", "cart_items", "orders", "outbox", "projections"):
                self._conn.execute(f"delete from {table}")

    def load_state(self, state: dict[str, Any]) -> None:
        self.reset()
        with self._conn:
            for account_id in state.get("accounts", []):
                self._conn.execute("insert into accounts(account_id) values (?)", (account_id,))
            for account_id, items in state.get("carts", {}).items():
                for sku in items:
                    self._conn.execute(
                        "insert into cart_items(account_id, sku, qty) values (?, ?, 1)",
                        (account_id, sku),
                    )
            for order_id, order in state.get("orders", {}).items():
                self._conn.execute(
                    "insert into orders(order_id, account_id, items_json, status) values (?, ?, ?, ?)",
                    (
                        order_id,
                        order["account"],
                        json.dumps(list(order.get("items", [])), sort_keys=True),
                        order.get("status", "accepted"),
                    ),
                )
            for event in state.get("outbox", []):
                self._conn.execute(
                    "insert into outbox(order_id, event_name) values (?, ?)",
                    (event["order_id"], event.get("event", "OrderAccepted")),
                )
            for order_id, visible_status in state.get("projections", {}).items():
                self._conn.execute(
                    "insert into projections(order_id, visible_status) values (?, ?)",
                    (order_id, visible_status),
                )

    def create_account(self, account_id: str) -> OperationResult:
        with self._conn:
            self._conn.execute("insert or ignore into accounts(account_id) values (?)", (account_id,))
        return OperationResult(201, {"account": account_id})

    def add_cart_item(self, account_id: str, sku: str) -> OperationResult:
        if not self._account_exists(account_id):
            return OperationResult(404, {"error": "account_not_found"})
        if sku in self._cart_items(account_id):
            return OperationResult(202, {"account": account_id, "sku": sku})
        with self._conn:
            self._conn.execute(
                "insert into cart_items(account_id, sku, qty) values (?, ?, 1)",
                (account_id, sku),
            )
        return OperationResult(202, {"account": account_id, "sku": sku})

    def checkout(self, account_id: str, order_id: str) -> OperationResult:
        if not self._account_exists(account_id):
            return OperationResult(404, {"error": "account_not_found"})
        existing = self._conn.execute("select order_id from orders where order_id = ?", (order_id,)).fetchone()
        if existing is not None:
            return OperationResult(200, {"order": order_id, "idempotent": True})

        items = self._cart_items(account_id)
        if not items:
            return OperationResult(409, {"error": "empty_cart"})
        with self._conn:
            self._conn.execute(
                "insert into orders(order_id, account_id, items_json, status) values (?, ?, ?, ?)",
                (order_id, account_id, json.dumps(items, sort_keys=True), "accepted"),
            )
            self._conn.execute(
                "insert into outbox(order_id, event_name) values (?, ?)",
                (order_id, "OrderAccepted"),
            )
        return OperationResult(202, {"order": order_id, "status": "accepted"})

    def process_outbox(self, limit: int = 100) -> OperationResult:
        rows = self._conn.execute(
            "select order_id, event_name from outbox order by order_id limit ?",
            (limit,),
        ).fetchall()
        with self._conn:
            for row in rows:
                self._conn.execute(
                    "insert or replace into projections(order_id, visible_status) values (?, ?)",
                    (row["order_id"], "ready_to_ship"),
                )
                self._conn.execute("delete from outbox where order_id = ?", (row["order_id"],))
        return OperationResult(200, {"processed": len(rows)})

    def project_order(self, order_id: str) -> OperationResult:
        row = self._conn.execute(
            "select order_id, event_name from outbox where order_id = ?",
            (order_id,),
        ).fetchone()
        if row is None:
            return OperationResult(200, {"processed": 0})
        with self._conn:
            self._conn.execute(
                "insert or replace into projections(order_id, visible_status) values (?, ?)",
                (row["order_id"], "ready_to_ship"),
            )
            self._conn.execute("delete from outbox where order_id = ?", (row["order_id"],))
        return OperationResult(200, {"processed": 1})

    def snapshot(self) -> dict[str, Any]:
        accounts = [
            row["account_id"]
            for row in self._conn.execute("select account_id from accounts order by account_id").fetchall()
        ]
        carts: dict[str, list[str]] = {}
        for row in self._conn.execute(
            "select account_id, sku from cart_items order by account_id, sku"
        ).fetchall():
            carts.setdefault(row["account_id"], []).append(row["sku"])
        orders: dict[str, dict[str, Any]] = {}
        for row in self._conn.execute(
            "select order_id, account_id, items_json, status from orders order by order_id"
        ).fetchall():
            orders[row["order_id"]] = {
                "account": row["account_id"],
                "items": json.loads(row["items_json"]),
                "status": row["status"],
            }
        outbox = [
            {"order_id": row["order_id"], "event": row["event_name"]}
            for row in self._conn.execute("select order_id, event_name from outbox order by order_id").fetchall()
        ]
        projections = {
            row["order_id"]: row["visible_status"]
            for row in self._conn.execute(
                "select order_id, visible_status from projections order by order_id"
            ).fetchall()
        }
        return {
            "accounts": accounts,
            "carts": carts,
            "orders": orders,
            "outbox": outbox,
            "projections": projections,
        }

    def _account_exists(self, account_id: str) -> bool:
        return self._conn.execute("select 1 from accounts where account_id = ?", (account_id,)).fetchone() is not None

    def _cart_items(self, account_id: str) -> list[str]:
        return [
            row["sku"]
            for row in self._conn.execute(
                "select sku from cart_items where account_id = ? order by sku",
                (account_id,),
            ).fetchall()
        ]
