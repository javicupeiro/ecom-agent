from ecom_agent.db.orders import OrdersDB


def test_seeded_order_is_readable(tmp_path) -> None:
    db = OrdersDB(tmp_path / "orders.db")
    order = db.get("ORD-100200")
    assert order is not None and order["status"] == "shipped"
    assert db.get("ORD-000000") is None