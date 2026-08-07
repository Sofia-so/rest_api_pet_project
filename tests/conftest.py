import pytest
import os
from alembic import command
from alembic.config import Config
from werkzeug.security import generate_password_hash
from decimal import Decimal
from sqlalchemy import select

from app.db.session import get_db
from app.db.model import(
    User,
    Category,
    Product,
    Order,
    OrderItem
)
from app.db.model_enum import (
    ProductStatus,
    OrderStatus,
    DeliveryMethod
)


@pytest.fixture(scope="session")
def app():
    os.environ["CONFIG_TYPE"] = "app.config.TestingConfig"
    print("CONFIG_TYPE:", os.getenv("CONFIG_TYPE"))

    from app import create_app

    app = create_app()
    print("DB:", app.config["SQLALCHEMY_DATABASE_URI"])

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    with app.app_context():
        yield app

    command.downgrade(alembic_cfg, "base")
    os.environ.pop("CONFIG_TYPE", None)


@pytest.fixture(scope="function")
def test_client(app):
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client


@pytest.fixture(scope="module")
def init_database(app):
    db = get_db()

    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(Product).delete()
    db.query(Category).delete()
    db.query(User).delete()
    db.commit()

    password = "strong_password"
    test_admin = User(
        first_name="test_admin",
        last_name="test_admin",
        username="testadmin",
        email="testadmin@email.com",
        password=generate_password_hash(password),
        role="admin"
    )

    test_user1 = User(
        first_name="test_client",
        last_name="test_client",
        username="testclient1",
        email="testclient1@email.com",
        password=generate_password_hash(password),
        role="client"
    )
    test_user2 = User(
        first_name="test_client",
        last_name="test_client",
        username="testclient2",
        email="testclient2@email.com",
        password=generate_password_hash(password),
        role="client"
    )
    test_user3 = User(
        first_name="test_client",
        last_name="test_client",
        username="testclient3",
        email="testclient3@email.com",
        password=generate_password_hash(password),
        role="client"
    )
    test_employee = User(
        first_name="test_employee",
        last_name="test_employee",
        username="testemployee",
        email="testemployee@email.com",
        password=generate_password_hash(password),
        role="employee"
    )

    db.add_all([
        test_admin,
        test_user1,
        test_user2,
        test_user3,
        test_employee
    ])
    db.commit()
    db.refresh(test_admin)
    db.refresh(test_user1)
    db.refresh(test_user2)
    db.refresh(test_user3)
    db.refresh(test_employee)

    category1 = Category(
        name="test_category1",
        description="test category"
    )

    category2 = Category(
        name="test_category2",
        description="test category"
    )

    db.add_all([category1, category2])
    db.commit()
    db.refresh(category1)
    db.refresh(category2)

    product1 = Product(
        name="test_product1",
        description="test product",
        price=223.60,
        status=ProductStatus.AVAILABLE,
        quantity=43,
        category_id=category1.id
    )

    product2 = Product(
        name="test_product2",
        description="test product",
        price=2323.60,
        status=ProductStatus.AVAILABLE,
        quantity=2,
        category_id=category2.id
    )

    db.add_all([product1, product2])
    db.commit()
    db.refresh(product1)
    db.refresh(product2)

    yield db
    db.close()


@pytest.fixture(scope="module")
def init_db_orders(init_database):
    db = init_database
    user = db.scalar(
        select(User).where(User.username == "testclient1")
    )
    category = db.scalar(
        select(Category).where(Category.id == Category.name == "test_category1")
    )    
    product = Product(
        name="test_product_test",
        description="test product",
        price=2323.60,
        status=ProductStatus.AVAILABLE,
        quantity=23,
        category=category
    )
    order1 = Order(
        number="ORD-001",
        customer_first_name="Ivan",
        customer_last_name="Ivanov",
        customer_phone="+380000000000",
        delivery_method=DeliveryMethod.PICKUP,
        status=OrderStatus.PENDING,
        total_price=Decimal("2323.60") * 2,
        user_id=user.id
    )
    order1.items.extend([
        OrderItem(
            product=product,
            quantity=2,
            price=product.price
        ),
        OrderItem(
            product=product,
            quantity=2,
            price=product.price
        )
    ])

    order2 = Order(
        number="ORD-002",
        customer_first_name="Ivan",
        customer_last_name="Ivanov",
        customer_phone="+380000000000",
        delivery_method=DeliveryMethod.PICKUP,
        status=OrderStatus.SHIPPED,
        total_price=Decimal("2323.60") * 3,
        user_id=user.id
    )
    order2.items.extend([
        OrderItem(
            product=product,
            quantity=3,
            price=product.price
        ),
        OrderItem(
            product=product,
            quantity=3,
            price=product.price
        )
    ])

    db.add_all([order1, order2])
    db.commit()

    password = "password"
    user = User(
        first_name="test_client",
        last_name="test_client",
        username="testclient765",
        email="testclient6t2@email.com",
        password=generate_password_hash(password),
        role="client"
    )

    db.add(user)
    db.commit()

    yield db
    db.close()
