def test_login(
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

    login_data = login_response.get_json()

    assert "access_token" in login_data

    token = login_data["access_token"]

    response = test_client.get(
        "/user/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["username"] == "testclient1"


def test_login_wrong_username(
        test_client,
        init_database
):
    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testcliiient1",
            "password": "strong_password"
        }
    )

    assert login_response.status_code == 401


def test_login_wrong_password(
        test_client,
        init_database
):
    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testclient1",
            "password": "strong_passwo55rd"
        }
    )

    assert login_response.status_code == 401


def test_get_current_user_without_token(test_client):

    response = test_client.get(
        "/user/me"
    )

    assert response.status_code == 401
