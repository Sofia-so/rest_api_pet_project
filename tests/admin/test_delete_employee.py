from sqlalchemy import select

from app.db.model import User


def test_delete_employee_success(
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
            "username": "test_employee11",
            "email": "test_test11employee@email.com",
            "password": "password",
            "confirm_password": "password"
        }
    )
    employee = db.scalar(
        select(User).where(User.username == "test_employee11")
    )
    employee_id = employee.id
    assert response.status_code == 201

    delete_response = test_client.delete(
        f"/admin/{employee_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert delete_response.status_code == 204
    updated_employee = db.scalar(
        select(User).where(User.username == "test_employee11")
    )
    assert updated_employee is None


def test_delete_employee_wrong_id(
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

    delete_response = test_client.delete(
        "/admin/999999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert delete_response.status_code == 404
