from sqlalchemy import select

from app.db.model import Category


def test_search_category(
        test_client,
        init_database
):
    db = init_database
    response = test_client.get(
        "/category/search",
        query_string={
            "query": "catg"
        }
    )
    categories = db.scalars(
        select(Category).where(Category.name.ilike(f"%catg%"))
        .limit(10)
    ).all()
    response_json = response.get_json()
    expected_names = sorted(category.name for category in categories)
    actual_names = sorted(item["name"] for item in response_json)

    assert response.status_code == 200
    assert actual_names == expected_names
