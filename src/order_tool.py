"""Customer-safe order lookup."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ORDERS_PATH = Path(__file__).resolve().parent.parent / "data" / "orders.json"
with ORDERS_PATH.open(encoding="utf-8") as orders_file:
    _ORDERS = {item.get("order_id", "").upper(): item for item in json.load(orders_file)["orders"]}

_ORDER_ID = re.compile(r"^ORD-\d+$")


def lookup_order(order_id: str) -> dict[str, Any] | None:
    normalized = str(order_id).strip().upper()
    if not _ORDER_ID.fullmatch(normalized) or normalized not in _ORDERS:
        return None
    order = _ORDERS[normalized]
    result: dict[str, Any] = {
        "order_id": normalized,
        "status": order.get("status"),
        "items": [{key: item[key] for key in ("name", "quantity", "final_sale") if key in item} for item in order.get("items", [])],
        "created_at": order.get("placed_at"),
    }
    if order.get("status") not in {"cancelled", "returned"} and order.get("shipped_at"):
        result["shipped_at"] = order["shipped_at"]
    if order.get("status") not in {"cancelled", "returned"}:
        for field in ("carrier", "tracking_number", "estimated_delivery", "customer_safe_message"):
            if order.get(field) is not None:
                result[field] = order[field]
    return result