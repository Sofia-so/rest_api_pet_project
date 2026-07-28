import pytest
import os
from alembic import command
from alembic.config import Config
from werkzeug.security import generate_password_hash

from app.db.session import get_db
from app.db.model import(
    User,
    Category,
    Product
)
from app.db.model_enum import (
    ProductStatus
)


@pytest.fixture(scope="module")
def app():
    os.environ["CONFIG_TYPE"] = "app.config.TestingConfig"
    print("CONFIG_TYPE:", os.getenv("CONFIG_TYPE"))

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    from app import create_app

    app = create_app()
    print("DB:", app.config["SQLALCHEMY_DATABASE_URI"])

    with app.app_context():
        yield app

    command.downgrade(alembic_cfg, "base")
    os.environ.pop("CONFIG_TYPE", None)


@pytest.fixture(scope="module")
def test_client(app):
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client


@pytest.fixture(scope="module")
def init_database(app):
    db = get_db()
    print(db.query(User).all())

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
        test_employee
    ])
    db.commit()
    db.refresh(test_admin)
    db.refresh(test_user1)
    db.refresh(test_user2)
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
