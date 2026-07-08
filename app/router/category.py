from flask_smorest import Blueprint
from sqlalchemy.exc import IntegrityError

from app.decorator import role_required
from app.schemas.category_schema import(
    CategoryBaseSchema,
    CategoryResponseSchema,
    CategoryUpdateSchema
)
from app.db.session import get_db
from app.db.model import Category

category_bp = Blueprint(
    "categories",
    __name__,
    url_prefix="/category"
)


@category_bp.route("/", methods=["POST"])
@category_bp.doc(
    summary="Створити категорію",
    description="""
    Створює нову категорію товарів.

    Функція доступна лише адміністратору.
    """,
    tags=["Categories"]
)
@category_bp.arguments(CategoryBaseSchema)
@category_bp.response(201, CategoryResponseSchema)
@category_bp.alt_response(
    409,
    description="Категорія з такою назвою вже існує."
)
@category_bp.alt_response(
    500,
    description="Виникла помилка сервера"
)
@role_required("admin")
def create_category(data):
    db = get_db()
    try:
        category = Category(
            name=data["name"],
            description=data["description"]
        )
        db.add(category)
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        return {"message": "Категорія з такою назвою вже існує."}, 409

    except Exception:
        db.rollback()
        return {"message": "Виникла помилка сервера"}, 500

    return category, 201


@category_bp.route("/", methods=["GET"])
@category_bp.doc(
    summary="Отримати каталог категорій",
    description="Повертає список усіх категорій",
    tags=["Categories"]
)
@category_bp.response(200, CategoryResponseSchema(many=True))
def get_categories():
    db = get_db()
    categories = db.query(Category).all()
    return categories


@category_bp.route("/<int:category_id>", methods=["PATCH"])
@category_bp.doc(
    summary="Оновити категорію",
    description="""
    Оновлює категорію за ID.
    
    Функція доступна лише адміністратору.
    Повертає збережені зміни. 
    """,
    tags=["Categories"]
)
@category_bp.arguments(CategoryUpdateSchema)
@category_bp.response(200, CategoryResponseSchema)
@category_bp.alt_response(
    409,
    description="Категорія з такою назвою вже існує."
)
@category_bp.alt_response(
    500,
    description="Виникла помилка сервера"
)
@category_bp.alt_response(
    404,
    description="Категорію не знайдено"
)
@role_required("admin")
def update_category(data, category_id):
    db = get_db()
    category = db.query(Category).filter_by(
        id=category_id
    ).first()

    if category is None:
        return {"message": "Категорію не знайдено"}, 404

    try:
        for key, value in data.items():
            setattr(category, key, value)
        db.commit()
        db.refresh(category)

    except IntegrityError:
        db.rollback()
        return {"message": "Категорія з такою назвою вже існує."}, 400

    except Exception:
        db.rollback()
        return {"message": "Виникла помилка сервера"}, 500

    return category


@category_bp.route("/<int:category_id>", methods=["DELETE"])
@category_bp.doc(
    summary="Видалити категорію",
    description="""
    Видаляє категорію за ID.

    Функція доступна лише адміністратору. 
    """,
    tags=["Categories"]
)
@category_bp.response(204)
@category_bp.alt_response(
    500,
    description="Виникла помилка сервера"
)
@category_bp.alt_response(
    404,
    description="Категорію не знайдено"
)
@category_bp.alt_response(
    400,
    description="Неможливо видалити категорію, оскільки вона містить товари."
)
@role_required("admin")
def delete_category(category_id):
    db = get_db()
    category = db.query(Category).filter_by(
        id=category_id
    ).first()

    if category is None:
        return {"message": "Категорію не знайдено"}, 404

    if category.products:
        return {
            "message": "Неможливо видалити категорію, оскільки вона містить товари."
        }, 400

    try:
        db.delete(category)
        db.commit()

    except Exception:
        db.rollback()
        return {"message": "Виникла помилка"}, 500

    return "", 204
