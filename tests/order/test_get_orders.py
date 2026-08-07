from sqlalchemy import select
from decimal import Decimal
from datetime import datetime

from app.db.model import (
    Product,
    User,
    Category,
    Order,
    OrderItem
)


def test_get_orders_admin(
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

    response = test_client.get(
        "/order/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    response_json = response.get_json()
    orders = db.scalars(select(Order)).all()

    expected = sorted(
        (
            order.id,
            order.number,
            order.status.value,
            order.total_price,
            order.created_at,
        )
        for order in orders
    )

    actual = sorted(
        (
            item["id"],
            item["number"],
            item["status"],
            Decimal(item["total_price"]),
            datetime.fromisoformat(item["created_at"]),
        )
        for item in response_json
    )

    assert response.status_code == 200
    assert expected == actual


def test_get_orders_user(
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

    login_data = login_response.get_json()
    token = login_data["access_token"]

    response = test_client.get(
        "/order/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    response_json = response.get_json()

    user = db.scalar(
        select(User).where(User.username == "testclient1")
    )
    orders = db.scalars(
        select(Order).where(Order.user_id == user.id)
    ).all()

    print(type(response_json))
    print(response_json)

    expected = sorted(
        (
            order.id,
            order.number,
            order.status.value,
            order.total_price,
            order.created_at,
        )
        for order in orders
    )

    actual = sorted(
        (
            item["id"],
            item["number"],
            item["status"],
            Decimal(item["total_price"]),
            datetime.fromisoformat(item["created_at"]),
        )
        for item in response_json
    )

    assert response.status_code == 200
    assert expected == actual
