from sqlalchemy import select

from app.db.model import Category


def test_delete_category_with_products(
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

    category = db.scalar(
        select(Category).where(Category.name == "test_category2")
    )
    assert category is not None

    category_id = category.id
    login_data = login_response.get_json()
    token = login_data["access_token"]
    response = test_client.delete(
        f"/category/{category_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    category = db.get(Category, category_id)
    assert response.status_code == 400
    assert category is not None


def test_delete_category_success(
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
            "name": "test_category444",
            "description": ""
        }
    )
    assert response.status_code == 201
    category = db.scalar(
        select(Category).where(Category.name == "test_category444")
    )
    category_id = category.id
    assert category is not None

    delete_response = test_client.delete(
        f"/category/{category_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    updated_category = db.get(Category, category_id)
    assert delete_response.status_code == 204
    assert updated_category is None
