from sqlalchemy import select

from app.db.model import User, Category


def test_create_category_success(
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

    response = test_client.post(
        "/category/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "test_category5328",
            "description": ""
        }
    )
    category = db.scalar(
        select(Category).where(Category.name == "test_category5328")
    )
    response_json = response.get_json()
    assert response.status_code == 201
    assert category is not None
    assert category.name == "test_category5328"
    assert response_json["name"] == "test_category5328"
    assert response_json["description"] == ""


def test_create_category_duplicate_name(
        test_client,
        init_database
):
    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testadmin",
            "password": "strong_password"
        }
    )
    assert login_response.status_code == 200

    login_data = login_response.get_json()
    assert "access_token" in login_data

    token = login_data["access_token"]

    response = test_client.post(
        "/category/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "test_category1",
            "description": ""
        }
    )
    assert response.status_code == 409


def test_create_category_without_auth(
        test_client,
        init_database
):
    response = test_client.post(
        "/category/",
        json={
            "name": "test_category1",
            "description": ""
        }
    )
    assert response.status_code == 401
