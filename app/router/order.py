from flask_smorest import Blueprint
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import get_db
from app.schemas.order_schemas import (
    OrderCreateSchema,
    OrderResponsesSchema,
    OrderStatusUpdateSchema
)
from app.db.model import (
    Order,
    Product,
    OrderItem,
    User
)
from app.db.model_enum import ProductStatus, OrderStatus
from app.number_order import generate_order_number
from app.schemas.message_schema import MessageSchema
from app.decorator import role_required
from app.schemas.search_schemas import SearchSchema
from app.constants import allowed_transitions

order_bp = Blueprint(
    "orders",
    __name__,
    url_prefix="/order"
)


@order_bp.route("/", methods=["POST"])
@order_bp.doc(
    summary="Оформлення замовлення",
    description="""
    Оформлює замовлення.

    Доступно лише для авторизованих користувачів.

    Перевіряє наявність товарів і їх доступну кількість на складі, 
    розраховує загальну вартість замовлення, 
    оновлює залишки та статус товарів при необхідності.
    Повертає інформацію про створене замовлення.
    """,
    tags=["Orders"]
)
@order_bp.arguments(OrderCreateSchema)
@order_bp.response(201, OrderResponsesSchema)
@order_bp.alt_response(
    400,
    description="Некоректні дані замовлення"
)
@order_bp.alt_response(
    404,
    description="Товар не знайдено"
)
@order_bp.alt_response(
    500,
    description="Внутрішня помилка сервера"
)
@jwt_required()
def create_order(data):
    db = get_db()
    user_id = get_jwt_identity()
    order = Order(
        number=generate_order_number(),
        customer_first_name=data["customer_first_name"],
        customer_last_name=data["customer_last_name"],
        customer_phone=data["customer_phone"],
        delivery_method=data["delivery_method"],
        user_id=user_id
    )

    total_price = Decimal("0")

    for item in data["items"]:
        product = db.scalar(
            select(Product)
            .where(Product.id == item["product_id"])
            .with_for_update()
        )

        if product is None:
            return (
                {"message": f"Продукт з id={item['product_id']} не знайдено"},
                404
            )

        if product.quantity < item["quantity"]:
            return {
                "message": f"Недостатньо товару '{product.name}' на складі. "
                           f"Доступна кількість товару {product.quantity}"
            }, 400

        order_item = OrderItem(
            product_id=product.id,
            quantity=item["quantity"],
            price=product.price
        )
        order.items.append(order_item)
        total_price += product.price * item["quantity"]

        product.quantity -= item["quantity"]

        if product.quantity == 0:
            product.status = ProductStatus.OUT_OF_STOCK

    order.total_price = total_price

    try:
        db.add(order)
        db.commit()
        db.refresh(order)

    except SQLAlchemyError:
        db.rollback()
        return {"message": "Помилка при створенні замовлення"}, 500
    except Exception:
        db.rollback()
        raise

    return order


@order_bp.route("/<int:order_id>/cancel", methods=["PATCH"])
@order_bp.doc(
    summary="Скасування замовлення",
    description="""
    Скасовує замовлення.

    Доступно авторизованим користувачам.
    Користувач із роллю "client" може скасувати лише власне замовлення.
    Користувачі з ролями "admin" та "employee" можуть скасувати будь-яке замовлення.

    Повертає товари на склад, змінює статус замовлення на "CANCELLED" 
    та повертає повідомлення про успішне скасування.
    """,
    tags=["Orders"]
)
@order_bp.response(200, MessageSchema)
@order_bp.alt_response(
    404,
    description="Замовлення або користувача не знайдено"
)
@order_bp.alt_response(
    400,
    description="Замовлення вже скасовано."
)
@order_bp.alt_response(
    403,
    description="Ви можете скасувати лише власні замовлення."
)
@order_bp.alt_response(
    409,
    description="Замовлення не можна скасувати через його поточний статус"
)
@order_bp.alt_response(
    500,
    description="Внутрішня помилка сервера"
)
@jwt_required()
def cancel_order(order_id):
    db = get_db()
    order = db.get(Order, order_id)
    current_user_id = get_jwt_identity()
    user = db.get(User, current_user_id)

    if order is None:
        return {"message": "Замовлення не знайдено"}, 404

    if user is None:
        return {"message": "Користувача не знайдено"}, 404

    if user.role == "client":
        if order.user_id != user.id:
            return {
                "message": "Ви можете скасувати лише власні замовлення."
            }, 403

    if order.status == OrderStatus.CANCELLED:
        return {
            "message": "Замовлення вже скасовано."
        }, 400

    if order.status == OrderStatus.SHIPPED:
        return {
            "message": "Замовлення не можна скасувати, оскільки його вже відправлено."
        }, 409

    for item in order.items:
        product = db.get(Product, item.product_id)
        product.quantity += item.quantity

        if product.quantity > 0:
            product.status = ProductStatus.AVAILABLE

    try:
        order.status = OrderStatus.CANCELLED
        db.commit()
        db.refresh(order)
    except SQLAlchemyError:
        db.rollback()
        return {"message": "Внутрішня помилка сервера"}, 500
    except Exception:
        db.rollback()
        raise
    return {"message": "Замовлення скасовано"}, 200


@order_bp.route("/", methods=["GET"])
@order_bp.doc(
    summary="Список замовлень",
    description="""
    Повертає список усіх замовлень.

    Доступно лише користувачам з ролями "admin" та "employee".
    """,
    tags=["Orders"]
)
@order_bp.response(200, OrderResponsesSchema(many=True))
@role_required("admin", "employee")
def get_orders():
    db = get_db()
    orders = db.query(Order).all()
    return orders


@order_bp.route("/search", methods=["GET"])
@order_bp.doc(
    summary="Пошук замовлення",
    description="""
    Повертає список замовлень, номер яких містить введений пошуковий рядок.

    Доступно лише користувачам з ролями "admin" та "employee".
    """,
    tags=["Orders"]
)
@order_bp.arguments(SearchSchema, location="query")
@order_bp.response(200, OrderResponsesSchema(many=True))
@role_required("admin", "employee")
def search_order(args):
    db = get_db()
    orders = db.scalars(
        select(Order).where(
            Order.number.ilike(f"%{args['query']}%")).limit(10)
    ).all()
    return orders


@order_bp.route("/<int:order_id>/status", methods=["PATCH"])
@order_bp.doc(
    summary="Змінити статус замовлення",
    description="""
    Змінює статус замовлення

    Доступно лише користувачам з ролями "admin" та "employee".
    Перевіряє допустимість переходу між статусами.
    """,
    tags=["Orders"]
)
@order_bp.arguments(OrderStatusUpdateSchema)
@order_bp.response(200, OrderResponsesSchema)
@order_bp.alt_response(
    404,
    description="Замовлення не знайдено"
)
@order_bp.alt_response(
    400,
    description="Некоректна зміна статусу"
)
@order_bp.alt_response(
    409,
    description="Недопустимий перехід між статусами"
)
@order_bp.alt_response(
    500,
    description="Внутрішня помилка сервера"
)
@role_required("admin", "employee")
def update_order_status(data, order_id):
    db = get_db()
    order = db.get(Order, order_id)

    if order is None:
        return {
            "message": "Замовлення не знайдено"
        }, 404

    new_status = data["status"]

    if order.status == data["status"]:
        return {
            "message": "Замовлення вже має цей статус."
        }, 400

    if new_status not in allowed_transitions[order.status]:
        return {
            "message": (
                f"Не можна змінити статус з "
                f"'{order.status.value}' на '{new_status.value}'."
            )
        }, 409

    order.status = new_status

    try:
        db.commit()
        db.refresh(order)
    except SQLAlchemyError:
        db.rollback()
        return {"message": "Внутрішня помилка сервера"}, 500
    except Exception:
        db.rollback()
        raise
    return order
