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
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    db = get_db()
    user = db.get(User, user_id)

    if not user:
        return {"message": "Користувача не знайдено"}, 404

    return user


@user_bp.route("/update", methods=["PATCH"])
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
@jwt_required()
def update_user(data):
    user_id = get_jwt_identity()
    db = get_db()
    user = db.query(User).filter_by(
        id=user_id
    ).first()

    if not user:
        return {"message": "Користувача не знайдено"}, 404

    try:
        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)

        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()
        return {
            "message": "Користувач з таким ім'ям або email вже існує."
        }, 400
    return user


@user_bp.route("/delete", methods=["DELETE"])
@user_bp.doc(
    summary="Видалення акаунту користувача",
    description="""
    Видаляє поточного авторизованого користувача.
    """,
    tags=["Users"]
)
@user_bp.response(204)
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


@user_bp.route("/change-password", methods=["POST"])
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
