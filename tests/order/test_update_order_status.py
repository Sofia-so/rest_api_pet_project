from sqlalchemy import select

from app.db.model import Order
from app.db.model_enum import OrderStatus


def test_update_order_status_success(
        test_client,
        init_db_orders
):
    db = init_db_orders
    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testadmin",
            "password": "strong_password"
        }
    )
    assert login_response.status_code == 200

    login_data = login_response.get_json()
    token = login_data["access_token"]

    order = db.scalar(
        select(Order).where(Order.number == "ORD-001")
    )

    assert order is not None
    assert order.status == OrderStatus.PENDING

    order_id = order.id

    response = test_client.patch(
        f"/order/{order_id}/status",
        headers = {
            "Authorization": f"Bearer {token}"
        },
        json={
            "status": "processing"
        }
    )

    assert response.status_code == 200

    updated_order = db.scalar(
        select(Order).where(Order.number == "ORD-001")
    )

    assert updated_order.status == OrderStatus.PROCESSING


def test_update_order_status_incorrect_status_change(
        test_client,
        init_db_orders
):
    db = init_db_orders

    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testadmin",
            "password": "strong_password"
        }
    )
    assert login_response.status_code == 200

    login_data = login_response.get_json()
    token = login_data["access_token"]

    order = db.scalar(
        select(Order).where(Order.number == "ORD-002")
    )

    assert order is not None
    assert order.status == OrderStatus.SHIPPED

    order_id = order.id

    response1 = test_client.patch(
        f"/order/{order_id}/status",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "status": "shipped"
        }
    )
    data1_json = response1.get_json()

    assert response1.status_code == 400
    assert data1_json["message"] == "Замовлення вже має цей статус."

    db.refresh(order)
    assert order.status == OrderStatus.SHIPPED

    response2 = test_client.patch(
        f"/order/{order_id}/status",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "status": "processing"
        }
    )
    data2_json = response2.get_json()

    assert response2.status_code == 409
    assert "Не можна змінити статус з " in data2_json["message"]
