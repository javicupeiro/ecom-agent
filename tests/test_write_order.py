from ecom_agent.db.orders import OrdersDB
from ecom_agent.orchestrator import Ctx
from ecom_agent.permissions import AllowList, AlwaysAllow
from ecom_agent.tools.registry import default_registry


def test_write_blocked_without_permission(tmp_path) -> None:
    ctx = Ctx(db=OrdersDB(tmp_path / "o.db"))
    res = default_registry.dispatch("write_order", {"order_id": "ORD-999999"}, ctx, AllowList([]))
    assert res.is_error


def test_write_creates_with_permission(tmp_path) -> None:
    db = OrdersDB(tmp_path / "o.db")
    ctx = Ctx(db=db)
    res = default_registry.dispatch(
        "write_order",
        {"order_id": "ORD-777777", "customer_name": "Ana", "customer_surname": "Ruiz",
         "product": "SaborMix Essential", "address": "Calle 1", "purchase_date": "2026-06-05"},
        ctx, AlwaysAllow())
    assert not res.is_error and db.get("ORD-777777") is not None


def test_invalid_id_rejected(tmp_path) -> None:
    ctx = Ctx(db=OrdersDB(tmp_path / "o.db"))
    res = default_registry.dispatch("write_order", {"order_id": "bad"}, ctx, AlwaysAllow())
    assert res.is_error