from sqlalchemy import select

from app.db.model import User


def test_register_employee_success(
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
        "/admin/register",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "first_name": "employee",
            "last_name": "employee",
            "username": "test_employee1",
            "email": "test_testemployee@email.com",
            "password": "password",
            "confirm_password": "password"
        }
    )
    employee = db.scalar(
        select(User).where(User.username == "test_employee1")
    )
    response_json = response.get_json()
    assert response.status_code == 201
    assert response_json["username"] == "test_employee1"
    assert response_json["email"] == "test_testemployee@email.com"
    assert employee is not None
    assert employee.first_name == "employee"
    assert employee.last_name == "employee"
    assert employee.email == "test_testemployee@email.com"


def test_register_employee_failed_login(
        test_client,
        init_database
):
    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testad1min",
            "password": "strong_password"
        }
    )
    assert login_response.status_code == 401
