from sqlalchemy import select

from app.db.model import User


def test_get_employees_success(
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

    response = test_client.get(
        "/admin/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    response_json = response.get_json()
    employee = {
        "first_name": "test_employee",
        "last_name": "test_employee",
        "username": "testemployee",
        "email": "testemployee@email.com"
    }
    assert response.status_code == 200
    assert response_json[0]["first_name"] == employee["first_name"]
    assert response_json[0]["last_name"] == employee["last_name"]
    assert response_json[0]["username"] == employee["username"]
    assert response_json[0]["email"] == employee["email"]


def test_get_employees_with_role_user(
        test_client,
        init_database
):
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

    response = test_client.get(
        "/admin/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 403
