from app.db.model import User
from app.db.session import get_db
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)
from sqlalchemy.exc import IntegrityError
from flask_smorest import Blueprint
from app.schemas.user_schemas import (
    UserResponseSchema,
    UserUpdateSchema
)
from app.schemas.change_password_schema import ChangePasswordSchema
from app.schemas.message_schema import MessageSchema


user_bp = Blueprint(
    "user",
    __name__,
    url_prefix="/user"
)


@user_bp.route("/me", methods=["GET"])
@user_bp.doc(
    summary="Отримання профілю користувача",
    description="Повертає дані поточного авторизованого користувача.",
    tags=["Users"]
)
@user_bp.response(200, UserResponseSchema)
@user_bp.alt_response(
    404,
    description="Користувача не знайдено"
)
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    db = get_db()
    user = db.get(User, user_id)

    if not user:
        return {"message": "Користувача не знайдено"}, 404

    return user


@user_bp.route("/me", methods=["PATCH"])
@user_bp.doc(
    summary="Оновлення користувача",
    description="""
    Оновлює дані поточного авторизованого користувача.

    - перевіряє унікальність email та ім'я користувача;
    - повертає оновлені дані користувача.
    """,
    tags=["Users"]
)
@user_bp.arguments(UserUpdateSchema)
@user_bp.response(200, UserResponseSchema)
@user_bp.alt_response(
    404,
    description="Користувача не знайдено"
)
@user_bp.alt_response(
    409,
    description="Користувач з таким ім'ям або email вже існує."
)
@jwt_required()
def update_user(data):
    user_id = get_jwt_identity()
    db = get_db()
    user = db.query(User).filter_by(
        id=user_id
    ).first()

    if user is None:
        return {"message": "Користувача не знайдено"}, 404

    try:
        for key, value in data.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()
        return {
            "message": "Користувач з таким ім'ям або email вже існує."
        }, 409
    return user


@user_bp.route("/me", methods=["DELETE"])
@user_bp.doc(
    summary="Видалення акаунту користувача",
    description="""
    Видаляє поточного авторизованого користувача.
    """,
    tags=["Users"]
)
@user_bp.response(204)
@user_bp.alt_response(
    404,
    description="Користувача не знайдено"
)
@user_bp.alt_response(
    500,
    description="Не вдалося виконати запит."
)
@jwt_required()
def delete_user():
    user_id = get_jwt_identity()
    db = get_db()
    user = db.get(User, user_id)

    if not user:
        return {"message": "Користувача не знайдено"}, 404

    try:
        db.delete(user)
        db.commit()
    except Exception:
        db.rollback()
        return {"message": "Не вдалося виконати запит."}, 500
    return "", 204


@user_bp.route("/me/password", methods=["PATCH"])
@user_bp.doc(
    summary="Зміна пароля",
    description="""
    Змінює пароль поточного авторизованого користувача.

    - перевіряє поточний пароль;
    - перевіряє підтвердження нового пароля;
    - зберігає новий пароль у хешованому вигляді.
    """,
    tags=["Users"]
)
@user_bp.arguments(ChangePasswordSchema)
@user_bp.response(200, MessageSchema)
@user_bp.alt_response(
    404,
    description="Користувача не знайдено"
)
@user_bp.alt_response(
    500,
    description="Не вдалося змінити пароль."
)
@user_bp.alt_response(
    401,
    description="Поточний пароль невірний."
)
@jwt_required()
def change_password(data):
    db = get_db()
    user_id = get_jwt_identity()
    user = db.get(User, user_id)

    if not user:
        return {"message": "Користувача не знайдено."}, 404

    if not check_password_hash(
        user.password,
        data["current_password"]
    ):
        return {"message": "Поточний пароль невірний."}, 401

    try:
        user.password = generate_password_hash(data["new_password"])
        db.commit()
    except Exception:
        db.rollback()
        return {"message": "Не вдалося змінити пароль."}, 500

    return {"message": "Пароль успішно змінено."}
