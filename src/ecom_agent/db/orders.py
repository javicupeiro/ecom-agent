"""SQLite-backed orders table. Reads and writes are exposed through SEPARATE tools
so write permission can be withheld. This module is just the data layer.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    order_id         TEXT PRIMARY KEY,
    customer_name    TEXT NOT NULL,
    customer_surname TEXT NOT NULL,
    product          TEXT NOT NULL,
    address          TEXT NOT NULL,
    purchase_date    TEXT NOT NULL,
    ship_date        TEXT,
    status           TEXT NOT NULL DEFAULT 'processing'
);
"""

COLUMNS = [
    "order_id", "customer_name", "customer_surname", "product",
    "address", "purchase_date", "ship_date", "status",
]

SEED = [
    ("ORD-100200", "Almudena", "Garcia", "SaborMix ProConnect",
     "Calle Quevedo 3, Madrid", "2026-05-20", "2026-05-22", "shipped"),
    ("ORD-555000", "Vicente", "Roig", "SaborMix Essential",
     "Av. del puerto 109, Valencia", "2026-06-01", None, "processing"),
]


class OrdersDB:
    """Persist and query order records."""

    def __init__(self, path: str | Path = "./.data/orders.db") -> None:
        """Create the database file and initialize the schema if needed."""

        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _conn(self) -> sqlite3.Connection:
        """Open a row-mapped SQLite connection."""

        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        """Create the schema and seed sample data on first run."""

        with self._conn() as conn:
            conn.executescript(SCHEMA)
            if conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0:
                conn.executemany(f"INSERT INTO orders VALUES ({','.join('?' * 8)})", SEED)

    # --- reads ---
    def get(self, order_id: str) -> dict[str, Any] | None:
        """Return one order by id, or None if it does not exist."""

        with self._conn() as conn:
            row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
            return dict(row) if row else None

    def find_by_surname(self, surname: str) -> list[dict[str, Any]]:
        """Return all orders that match a customer surname."""

        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM orders WHERE lower(customer_surname) = lower(?)", (surname,)
            ).fetchall()
            return [dict(r) for r in rows]

    # --- write ---
    def upsert(self, order: dict[str, Any]) -> str:
        """Insert a new order or merge fields into an existing one."""

        existing = self.get(order["order_id"])
        with self._conn() as conn:
            if existing:
                merged = {**existing, **{k: v for k, v in order.items() if v is not None}}
                conn.execute(
                    "UPDATE orders SET customer_name=?, customer_surname=?, product=?, "
                    "address=?, purchase_date=?, ship_date=?, status=? WHERE order_id=?",
                    (merged["customer_name"], merged["customer_surname"], merged["product"],
                     merged["address"], merged["purchase_date"], merged["ship_date"],
                     merged["status"], merged["order_id"]),
                )
                return "updated"
            cols = [c for c in COLUMNS if c in order]
            conn.execute(
                f"INSERT INTO orders ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                tuple(order[c] for c in cols),
            )
            return "created"