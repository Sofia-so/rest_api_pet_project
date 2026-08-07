from sqlalchemy import select
from decimal import Decimal

from app.db.model import Product


def test_get_products(
        test_client,
        init_database
):
    db = init_database
    response = test_client.get(
        "/product/"
    )
    products = db.scalars(
        select(Product)
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
