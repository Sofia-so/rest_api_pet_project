from sqlalchemy import select
from decimal import Decimal

from app.db.model import Product


def test_search_product(
        test_client,
        init_database
):
    db = init_database
    response = test_client.get(
        "/product/search",
        query_string={
            "query": "prod"
        }
    )
    products = db.scalars(
        select(Product).where(Product.name.ilike(f"%prod%")).
               limit(10)
    ).all()
    expected = sorted(
        (product.id, product.name, product.price, product.quantity)
        for product in products
    )
    actual = sorted(
        (item["id"], item["name"], Decimal(item["price"]), item["quantity"])
        for item in response.get_json()
    )

    assert response.status_code == 200
    assert expected == actual
