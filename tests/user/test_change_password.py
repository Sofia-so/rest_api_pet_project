def test_change_password_success(test_client, init_database):
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

    response = test_client.patch(
        "/user/me/password",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "current_password": "strong_password",
            "new_password": "new_password",
            "confirm_password": "new_password"
        }
    )
    assert response.status_code == 200
    assert response.get_json()["message"] == "Пароль успішно змінено."

    old_login = test_client.post(
        "/user/login",
        json={
            "username": "testclient2",
            "password": "strong_password"
        }
    )

    assert old_login.status_code == 401

    new_login = test_client.post(
        "/user/login",
        json={
            "username": "testclient2",
            "password": "new_password"
        }
    )
    assert new_login.status_code == 200


def test_change_password_wrong_current_password(
        test_client,
        init_database
):
    register_response = test_client.post(
        "/user/register",
        json={
            "first_name": "test_user",
            "last_name": "test_user",
            "username": "testclient_in_func_pas_change",
            "email": "test_client111@email.com",
            "password": "password",
            "confirm_password": "password"
        }
    )
    assert register_response.status_code == 201

    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testclient_in_func_pas_change",
            "password": "password"
        }
    )
    assert login_response.status_code == 200

    login_data = login_response.get_json()
    assert "access_token" in login_data
    token = login_data["access_token"]

    response = test_client.patch(
        "/user/me/password",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "current_password": "strong_password",
            "new_password": "new_password",
            "confirm_password": "new_password"
        }
    )
    assert response.status_code == 401


def test_change_password_passwords_d_not_match(
        test_client,
        init_database
    ):
    register_response = test_client.post(
        "/user/register",
        json={
            "first_name": "test_user",
            "last_name": "test_user",
            "username": "testclient_in_func_pas_change2",
            "email": "test_client1112@email.com",
            "password": "password",
            "confirm_password": "password"
        }
    )
    assert register_response.status_code == 201

    login_response = test_client.post(
        "/user/login",
        json={
            "username": "testclient_in_func_pas_change2",
            "password": "password"
        }
    )
    assert login_response.status_code == 200

    login_data = login_response.get_json()
    assert "access_token" in login_data
    token = login_data["access_token"]
    response = test_client.patch(
        "/user/me/password",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "current_password": "password",
            "new_password": "new_password",
            "confirm_password": "new_passworder"
        }
    )
    response_data = response.get_json()
    assert response.status_code == 422
    assert (response_data["errors"]["json"]["confirm_password"]
            == "Паролі не співпадають.")
