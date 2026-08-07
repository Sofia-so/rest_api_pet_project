from sqlalchemy import select
from decimal import Decimal

from app.db.model import (
    Product,
    User,
    Category,
    Order,
    OrderItem
)
from app.db.model_enum import ProductStatus

def test_create_order_success(
        test_client,
        init_database
):
    db = init_database
    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testadmin",
            "password": "strong_password"
        }
    )
    assert login_response.status_code == 200

    admin = db.scalar(
        select(User).where(User.username == "testadmin")
    )
    assert admin is not None

    login_data = login_response.get_json()
    assert "access_token" in login_data

    token = login_data["access_token"]

    category_response = test_client.post(
        "/category/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "test_category88",
            "description": ""
        }
    )
    assert category_response.status_code == 201

    category = db.scalar(
        select(Category).where(Category.name == "test_category88")
    )
    assert category is not None

    product_response = test_client.post(
        "/product/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "test_product42",
            "description": "test product",
            "status": "available",
            "price": 565.90,
            "quantity": 6,
            "category_id": category.id
        }
    )
    assert product_response.status_code == 201

    product = db.scalar(
        select(Product).where(Product.name == "test_product42")
    )

    assert product is not None

    response = test_client.post(
        "/order/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "customer_first_name": "customer_first_name",
            "customer_last_name": "customer_last_name",
            "customer_phone": "+380000000000",
            "delivery_method": "pickup",
            "items": [
                {
                    "product_id": product.id,
                    "quantity": 6
                },
                {
                    "product_id": product.id,
                    "quantity": 3
                }
            ]
        }
    )
    assert response.status_code == 201

    response_json = response.get_json()
    order_id = response_json["id"]
    order = db.get(Order, order_id)
    order_items = db.scalars(
        select(OrderItem).where(OrderItem.order_id == order.id)
    ).all()
    total_price = (6 * product.price) + (3 * Decimal("223.60"))
    updated_product = db.get(Product, product.id)
    expected = sorted(
        (item.product_id, item.quantity, item.price)
        for item in order_items
    )

    actual = sorted(
        (
            item["product_id"],
            item["quantity"],
            Decimal(item["price"])
        )
        for item in response_json["items"]
    )

    assert order is not None
    assert response_json["number"] == order.number
    assert response_json["status"] == "pending"
    assert Decimal(response_json["total_price"]) == total_price
    assert updated_product.status == ProductStatus.OUT_OF_STOCK
    assert expected == actual


def test_create_order_insufficient_quantity_of_product(
        test_client,
        init_database
):
    db = init_database
    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testclient1",
            "password": "strong_password"
        }
    )
    assert login_response.status_code == 200

    login_json = login_response.get_json()
    token = login_json["access_token"]

    product = db.scalar(
        select(Product).where(Product.name == "test_product1")
    )

    response = test_client.post(
        "/order/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "customer_first_name": "customer_first_name",
            "customer_last_name": "customer_last_name",
            "customer_phone": "+380000000000",
            "delivery_method": "pickup",
            "items": [
                {
                    "product_id": product.id,
                    "quantity": product.quantity + 1
                }
            ]
        }
    )
    assert response.status_code == 400
