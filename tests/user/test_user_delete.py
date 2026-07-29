from sqlalchemy import select

from app.db.model import User


def test_delete_user_success(
        test_client,
        init_database
):
    db = init_database
    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testclient3",
            "password": "strong_password"
        }
    )
    assert login_response.status_code == 200

    login_data = login_response.get_json()
    assert "access_token" in login_data

    token = login_data["access_token"]
    user = db.scalar(
        select(User).where(User.username == "testclient3")
    )
    assert user is not None

    response = test_client.delete(
        "/user/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 204


def test_delete_user_with_order(
        test_client,
        init_database
):
    db = init_database
    register_response = test_client.post(
        "/user/register",
        json={
            "first_name": "test_user",
            "last_name": "test_user",
            "username": "test_user_in_func",
            "email": "testuser_in_func@email.com",
            "password": "password",
            "confirm_password": "password"
        }
    )
    assert register_response.status_code == 201

    login_response = test_client.post(
        "/user/login",
        json={
            "username": "test_user_in_func",
            "password": "password"
        }
    )
    assert login_response.status_code == 200

    login_data = login_response.get_json()
    token = login_data["access_token"]
    order_response = test_client.post(
        "/order/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "customer_first_name": "customer_first_name",
            "customer_last_name": "customer_last_name",
            "customer_phone": "+380501234567",
            "delivery_method": "courier",
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1
                }
            ]
        }
    )
    assert order_response.status_code == 201

    response = test_client.delete(
        "/user/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 409

    user = db.scalar(
        select(User).where(User.username == "test_user_in_func")
    )
    assert user is not None
