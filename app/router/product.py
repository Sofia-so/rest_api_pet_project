from flask_smorest import Blueprint
from sqlalchemy.exc import IntegrityError

from app.decorator import role_required
from app.db.session import get_db
from app.schemas.product_schemas import (
    ProductBaseSchema,
    ProductResponseSchema,
    ProductUpdateSchema
)
from app.db.model import Product, Category

product_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/product"
)


@product_bp.route("/", methods=["POST"])
@product_bp.doc(
    summary="Створення товару",
    description="""
    Створює товар.
    
    Доступна тільки користувачам із ролями "admin" або "employee".
    У разі існування товару з такою назвою повертає повідомлення про помилку.
    Повертає товар. 
    """,
    tags=["Products"]
)
@product_bp.arguments(ProductBaseSchema)
@product_bp.response(201, ProductResponseSchema)
@product_bp.alt_response(
    409,
    description="Товар із такою назвою вже існує."
)
@product_bp.alt_response(
    500,
    description="Виникла помилка сервера."
)
@role_required("admin", "employee")
def create_product(data):
    db = get_db()
    try:
        product = Product(
            name=data["name"],
            description=data["description"],
            status=data["status"],
            price=data["price"],
            quantity=data["quantity"],
            category_id=data["category_id"]
        )
        db.add(product)
        db.commit()
        db.refresh(product)

    except IntegrityError:
        db.rollback()
        return {"message": "Товар із такою назвою вже існує."}, 400

    except Exception:
        db.rollback()
        return {"message": "Виникла помилка сервера."}, 500

    return product


@product_bp.route("/", methods=["GET"])
@product_bp.doc(
    summary="Отримати список товарів",
    description="Повертає список усіх товарів.",
    tags=["Products"]
)
@product_bp.response(200, ProductResponseSchema(many=True))
def get_products():
    db = get_db()
    products = db.query(Product).all()
    return products


@product_bp.route("/<int:product_id>", methods=["PATCH"])
@product_bp.doc(
    summary="Оновлює товар",
    description="""
    Оновлює товар за ID.
    
    Функція доступна лише користувачам з ролями "admin", "employee".
    Повертає товар зі збереженими змінами.
    """,
    tags=["Products"]
)
@product_bp.arguments(ProductUpdateSchema)
@product_bp.response(200, ProductResponseSchema)
@product_bp.alt_response(
    409,
    description="Товар із такою назвою вже існує."
)
@product_bp.alt_response(
    404,
    description="Категорію не знайдено."
)
@product_bp.alt_response(
    500,
    description="Виникла помилка сервера."
)
@role_required("admin", "employee")
def update_product(data, product_id):
    db = get_db()
    product = db.query(Product).filter_by(
        id=product_id
    ).first()
    if product is None:
        return {"message": "Товар не знайдено"}, 404

    if "category_id" in data:
        category = db.get(Category, data["category_id"])
        if category is None:
            return {"message": "Категорію не знайдено"}, 404

    try:
        for key, value in data.items():
            setattr(product, key, value)
        db.commit()
        db.refresh(product)

    except IntegrityError:
        db.rollback()
        return {"message": "Товар із такою назвою вже існує."}, 409

    except Exception:
        db.rollback()
        return {"message": "Виникла помилка сервера"}, 500

    return product


@product_bp.route("/<int:product_id>", methods=["DELETE"])
@product_bp.doc(
    summary="Видаляє товар",
    description="""
    Видаляє товар за його ID.

    Функція доступна лише користувачам з ролями "admin" або "employee".
    """,
    tags=["Products"]
)
@product_bp.response(204)
@product_bp.alt_response(
    404,
    description="Товар не знайдено"
)
@product_bp.alt_response(
    500,
    description="Виникла помилка сервера."
)
@role_required("admin", "employee")
def delete_product(product_id):
    db = get_db()
    product = db.get(Product, product_id)
    if product is None:
        return {"message": "Товар не знайдено"}, 404
    try:
        db.delete(product)
        db.commit()
    except Exception:
        db.rollback()
        return {"message": "Виникла помилка"}, 500

    return "", 204
