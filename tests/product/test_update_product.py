from sqlalchemy import select

from app.db.model import (
    Product,
    User
)
from app.db.model_enum import ProductStatus


def test_update_product_success(
        test_client,
        init_database
):
    db = init_database

    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testemployee",
            "password": "strong_password"
        }
    )
    assert login_response.status_code == 200

    login_json = login_response.get_json()
    token = login_json["access_token"]
    employee = db.scalar(
        select(User).where(User.username == "testemployee")
    )
    assert employee is not None

    product = db.scalar(
    select(Product).where(Product.name == "test_product2")
    )
    assert product is not None
    product_id = product.id

    response = test_client.patch(
        f"/product/{product_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "status": "out_of_stock",
            "price": 5789,
            "quantity": 0
        }
    )

    updated_product = db.scalar(
    select(Product).where(Product.name == "test_product2")
    )
    assert response.status_code == 200
    assert updated_product.status == ProductStatus.OUT_OF_STOCK
    assert updated_product.quantity == 0


def test_update_product_wrong_token(
        test_client,
        init_database
):
    db = init_database

    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testemployee",
            "password": "strong_password"
        }
    )
    assert login_response.status_code == 200

    product = db.scalar(
    select(Product).where(Product.name == "test_product2")
    )
    assert product is not None
    product_id = product.id

    response = test_client.patch(
        f"/product/{product_id}",
        headers={
            "Authorization": f"Bearer TR33344445g"
        },
        json={
            "status": "out_of_stock",
            "price": 5789,
            "quantity": 0
        }
    )

    assert response.status_code == 422
