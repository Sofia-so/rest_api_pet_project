from sqlalchemy import select
from werkzeug.security import check_password_hash

from app.db.model import User


def test_register_success(
        test_client,
        init_database
):
    db = init_database
    response = test_client.post(
        "/user/register",
        json={
            "first_name": "test_user",
            "last_name": "test_user",
            "username": "test_user",
            "email": "testuser@email.com",
            "password": "password",
            "confirm_password": "password"
        }
    )

    user = db.scalar(
        select(User).where(User.username == "test_user")
    )
    response_json = response.get_json()

    assert response.status_code == 201
    assert user is not None
    assert user.email == "testuser@email.com"
    assert response_json["username"] == "test_user"
    assert response_json["email"] == "testuser@email.com"
    assert check_password_hash(
        user.password,
        "password"
    )


def test_register_duplicate_username(
        test_client,
        init_database
):
    response = test_client.post(
        "/user/register",
        json={
            "first_name": "test_user2",
            "last_name": "test_user2",
            "username": "testclient1",
            "email": "test_client1@email.com",
            "password": "password",
            "confirm_password": "password"
        }
    )
    response_json = response.get_json()
    print(response_json)
    assert response.status_code == 409


def test_register_duplicate_email(
            test_client,
            init_database
    ):

    response = test_client.post(
        "/user/register",
        json={
            "first_name": "test_user",
            "last_name": "test_user",
            "username": "test_client",
            "email": "testclient1@email.com",
            "password": "password",
            "confirm_password": "password"
        }
    )

    response_json = response.get_json()
    print(response_json)
    assert response.status_code == 409


def test_register_passwords_d_not_match(
        test_client,
        init_database
):
    response = test_client.post(
        "/user/register",
        json={
            "first_name": "test_user",
            "last_name": "test_user",
            "username": "test_user_test2",
            "email": "testuser44@email.com",
            "password": "password",
            "confirm_password": "password44"
        }
    )
    response_json = response.get_json()
    assert response.status_code == 422
    assert (response_json["errors"]["json"]["confirm_password"]
            == "Паролі не співпадають.")
