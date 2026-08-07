def test_get_categories(
        test_client,
        init_database
):
    response = test_client.get(
        "/category/"
    )
    category1 = {
        "name": "test_category1",
        "description": "test category"
    }
    category2 = {
        "name": "test_category2",
        "description": "test category"
    }
    response_json = response.get_json()
    assert response.status_code == 200
    assert any(
        item["name"] == category1["name"] for item in response_json
    )
    assert any(
        item["name"] == category2["name"] for item in response_json
    )
    assert any(
        item["description"] == category1["description"] for item in response_json
    )
    assert any(
        item["description"] == category2["description"] for item in response_json
    )


def test_get_wrong_category(
        test_client,
        init_database
):
    response = test_client.get(
        "/category/"
    )
    category = {
        "name": "test_category16666",
        "description": "test category"
    }
    response_json = response.get_json()
    assert response.status_code == 200
    assert all(item["name"] != category["name"] for item in response_json)
