def test_search_order(
        test_client,
        init_db_orders
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
    token = login_data["access_token"]

    response = test_client.get(
        "/order/search",
        headers={
            "Authorization": f"Bearer {token}"
        },
        query_string={
            "query": "001"
        }
    )

    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json[0]["customer_first_name"] == "Ivan"
    assert response_json[0]["customer_last_name"] == "Ivanov"
    assert response_json[0]["customer_phone"] == "+380000000000"
    assert len(response_json) == 1

    response2 = test_client.get(
        "/order/search",
        headers={
            "Authorization": f"Bearer {token}"
        },
        query_string={
            "query": "00"
        }
    )

    response2_json = response2.get_json()
    assert response2.status_code == 200
    assert len(response2_json) == 2

    response3 = test_client.get(
        "/order/search",
        headers={
            "Authorization": f"Bearer {token}"
        },
        query_string={
            "query": "00RTY"
        }
    )

    response3_json = response3.get_json()
    assert response3.status_code == 200
    assert len(response3_json) == 0


def test_search_order_with_role_client(
        test_client,
        init_db_orders
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
    token = login_data["access_token"]

    response = test_client.get(
        "/order/search",
        headers={
            "Authorization": f"Bearer {token}"
        },
        query_string={
            "query": "001"
        }
    )

    assert response.status_code == 403
