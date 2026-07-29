from sqlalchemy import select

from app.db.model import User


def test_update_user_success(test_client, init_database):
    db = init_database
    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testclient2",
            "password": "strong_password"
        }
    )
    assert login_response.status_code == 200

    login_data = login_response.get_json()
    assert "access_token" in login_data
    token = login_data["access_token"]
    user = db.scalar(
        select(User).where(User.username == "testclient2")
    )

    assert user is not None

    response = test_client.patch(
        f"/user/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "first_name": "update_name",
            "last_name": "update_name"
        }
    )
    updated_user = db.scalar(
        select(User).where(User.username == "testclient2")
    )
    response_data = response.get_json()
    assert response.status_code == 200
    assert response_data["first_name"] == "update_name"
    assert response_data["last_name"] == "update_name"
    assert updated_user.first_name == "update_name"
    assert updated_user.last_name == "update_name"


def test_update_not_found_user(
        test_client,
        init_database
):
    db = init_database
    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testclient2",
            "password": "strong_password"
        }
    )

    assert login_response.status_code == 200

    login_data = login_response.get_json()
    token = login_data["access_token"]
    user = db.scalar(
        select(User).where(User.username == "testclient2")
    )
    assert user is not None

    db.delete(user)
    db.commit()

    response = test_client.patch(
        f"/user/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "first_name": "update_name",
            "last_name": "update_name"
        }
    )
    assert response.status_code == 401


def test_update_user_duplicate_username(
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

    response = test_client.patch(
        f"/user/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "username": "testclient1"
        }
    )
    assert response.status_code == 409


def test_update_user_duplicate_email(
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

    response = test_client.patch(
        f"/user/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "email": "testclient1@email.com"
        }
    )
    assert response.status_code == 409
