from app.db.model import User
from app.db.session import get_db
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt
)
from sqlalchemy.exc import IntegrityError
from app.router.user import user_bp
from app.schemas.user_schemas import (
    UserBaseSchema,
    UserResponseSchema,
    UserLoginSchema
)
from app.schemas.token_schema import TokenSchema
from app.schemas.message_schema import MessageSchema

from app.authen.jwt_blocklist import BLACKLIST


@user_bp.route("/register", methods=["POST"])
@user_bp.doc(
    summary="Реєстрація користувача",
    description="""
    Створює нового користувача.

    - перевіряє унікальність email та ім'я користувача;
    - хешує пароль перед збереженням;
    - повертає інформацію про створеного користувача.
    """,
    tags=["Auth"]
)
@user_bp.arguments(UserBaseSchema)
@user_bp.response(201, UserResponseSchema)
def register(data):
    db = get_db()

    try:
        new_user = User(
            first_name=data["first_name"],
            last_name=data["last_name"],
            username=data["username"],
            email=data["email"],
            password=generate_password_hash(data["password"]),
            role="client"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        return {
            "message": "Користувач з таким ім'ям або email вже існує."
        }, 400
    return new_user, 201


@user_bp.route("/login", methods=["POST"])
@user_bp.doc(
    summary="Авторизація користувача",
    description="""
    Перевіряє ім'я користувача та пароль.

    Якщо дані правильні, повертає JWT-токен,
    який використовується для доступу до захищених ендпоінтів.
    """,
    tags=["Auth"]
)
@user_bp.arguments(UserLoginSchema)
@user_bp.response(200, TokenSchema)
def login(data):
    db = get_db()
    user = (
    db.query(User)
      .filter_by(username=data["username"])
      .first()
    )
    if user is None:
        return {"message": "Невірний логін або пароль"}, 401

    if not check_password_hash(
        user.password, data["password"]
    ):
        return {"message": "Невірний логін або пароль"}, 401
    access_token = create_access_token(identity=str(user.id))
    return {"access_token": access_token}, 200


@user_bp.route("/logout", methods=["POST"])
@user_bp.doc(
    summary="Вихід користувача",
    description="""
    Деактивує поточний JWT-токен.
    Після виходу цей токен більше не може використовуватися
    для доступу до захищених ендпоінтів.
    """,
    tags=["Auth"]
)
@user_bp.response(200, MessageSchema)
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    BLACKLIST.add(jti)

    return {"message": "Токен деактивовано"}, 200
