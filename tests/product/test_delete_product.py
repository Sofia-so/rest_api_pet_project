from sqlalchemy import select

from app.db.model import (
    Product,
    User,
    Category
)


def test_delete_product_success(
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

    login_json = login_response.get_json()
    token = login_json["access_token"]
    admin = db.scalar(
        select(User).where(User.username == "testadmin")
    )
    assert admin is not None

    product = db.scalar(
        select(Product).where(Product.name == "test_product2")
    )
    assert product is not None
    product_id = product.id

    response = test_client.delete(
        f"/product/{product_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    deleted_product = db.get(Product, product_id)

    assert response.status_code == 204
    assert deleted_product is None


def test_delete_product_in_order(
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

    category = db.scalar(
        select(Category).where(Category.name == "test_category1")
    )
    assert category is not None

    create_response = test_client.post(
        "/product/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "test_product674",
            "description": "test product",
            "status": "available",
            "price": 5789,
            "quantity": 43,
            "category_id": category.id
        }
    )

    assert create_response.status_code == 201
    product = db.scalar(
        select(Product).where(Product.name == "test_product674")
    )
    product_id = product.id
    assert product is not None

    order_response = test_client.post(
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
                    "product_id": product_id,
                    "quantity": 2
                }
            ]
        }
    )

    assert order_response.status_code == 201

    response = test_client.delete(
        f"/product/{product_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 409
