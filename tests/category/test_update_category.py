from sqlalchemy import select

from app.db.model import User, Category


def test_update_category_success(
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

    category = db.scalar(
        select(Category).where(Category.name == "test_category2")
    )
    assert category is not None
    category_id = category.id

    response = test_client.patch(
        f"/category/{category_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "description": "test category"
        }
    )
    update_category = db.scalar(
        select(Category).where(Category.name == "test_category2")
    )
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["description"] == "test category"
    assert update_category.description == "test category"


def test_update_category_not_found(
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

    login_data = login_response.get_json()
    token = login_data["access_token"]

    response = test_client.post(
        "/category/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "test_category111",
            "description": ""
        }
    )

    assert response.status_code == 201

    category = db.scalar(
        select(Category).where(Category.name == "test_category111")
    )
    assert category is not None

    db.delete(category)
    db.commit()

    category_id = category.id

    update_response = test_client.patch(
        f"/category/{category_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "description": "test category"
        }
    )
    assert update_response.status_code == 404
