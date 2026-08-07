from sqlalchemy import select

from app.db.model import Order
from app.db.model_enum import OrderStatus


def test_cancel_order_success(
        test_client,
        init_db_orders
):
    db = init_db_orders
    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testclient1",
            "password": "strong_password"
        }
    )
    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]
    order = db.scalar(
        select(Order).where(Order.number == "ORD-001")
    )
    order_id = order.id
    response = test_client.patch(
        f"/order/{order_id}/cancel",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    updated_order = db.get(Order, order.id)
    assert response.status_code == 200
    assert updated_order.status == OrderStatus.CANCELLED

    response2 = test_client.patch(
        f"/order/{order_id}/cancel",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response2.status_code == 400


def test_cancel_order_not_own(
        test_client,
        init_db_orders
):
    db = init_db_orders

    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testclient765",
            "password": "password"
        }
    )
    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]
    order = db.scalar(
        select(Order).where(Order.number == "ORD-002")
    )
    order_id = order.id
    response = test_client.patch(
        f"/order/{order_id}/cancel",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 403


def test_cancel_shipped_order(
        test_client,
        init_db_orders
):
    db = init_db_orders

    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testclient1",
            "password": "strong_password"
        }
    )
    assert login_response.status_code == 200
    token = login_response.get_json()["access_token"]
    order = db.scalar(
        select(Order).where(Order.number == "ORD-002")
    )
    order_id = order.id
    response = test_client.patch(
        f"/order/{order_id}/cancel",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 409
    