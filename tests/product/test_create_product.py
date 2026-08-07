from sqlalchemy import select

from app.db.model import (
    Product,
    User,
    Category
)
from app.db.model_enum import ProductStatus


def test_create_product_success(
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
    assert "access_token" in login_json

    token = login_json["access_token"]
    employee = db.scalar(
        select(User).where(User.username == "testemployee")
    )
    assert employee is not None

    category = db.scalar(
        select(Category).where(Category.name == "test_category1")
    )

    response = test_client.post(
        "/product/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "test_product4562",
            "description": "test product",
            "status": "available",
            "price": 5789,
            "quantity": 43,
            "category_id": category.id
        }
    )
    response_json = response.get_json()
    product = db.scalar(
        select(Product).where(Product.name == "test_product4562")
    )
    assert response.status_code == 201
    assert response_json["name"] == "test_product4562"
    assert response_json["quantity"] == 43
    assert product is not None
    assert product.status == ProductStatus.AVAILABLE
    assert product.price == 5789.00


def test_create_product_duplicate_name(
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

    category = db.scalar(
        select(Category).where(Category.name == "test_category1")
    )

    response = test_client.post(
        "/product/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "test_product1",
            "description": "test product",
            "status": "available",
            "price": 5789,
            "quantity": 43,
            "category_id": category.id
        }
    )
    assert response.status_code == 400


def test_create_product_with_role_user(
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

    login_data = login_response.get_json()

    assert "access_token" in login_data

    token = login_data["access_token"]
    category = db.scalar(
        select(Category).where(Category.name == "test_category1")
    )

    response = test_client.post(
        "/product/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "test_product777",
            "description": "test product",
            "status": "available",
            "price": 5789,
            "quantity": 43,
            "category_id": category.id
        }
    )
    assert response.status_code == 403
