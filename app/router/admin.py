from flask_smorest import Blueprint
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

from app.schemas.user_schemas import (
    UserBaseSchema,
    UserResponseSchema
)
from app.db.session import get_db
from app.db.model import User
from app.decorator import role_required

worker_bp = Blueprint(
    "worker",
    __name__,
    url_prefix="/admin"
)


@worker_bp.route("/register", methods=["POST"])
@worker_bp.doc(
    summary="Реєстрація працівника",
    description="""
    Реєстрація нового співробітника.
    
    Ця функція доступна лише адміністратору.
    - перевіряє унікальність email та ім'я користувача;
    - хешує пароль перед збереженням;
    - повертає інформацію про створеного користувача.
    """,
    tags=["Workers"]
)
@worker_bp.arguments(UserBaseSchema)
@worker_bp.response(201, UserResponseSchema)
@role_required("admin")
def register_employee(data):
    db = get_db()
    try:
        new_worker = User(
            first_name=data["first_name"],
            last_name=data["last_name"],
            username=data["username"],
            email=data["email"],
            password=generate_password_hash(data["password"]),
            role="employee"
        )
        db.add(new_worker)
        db.commit()

    except IntegrityError:
        db.rollback()
        return {"message": "Користувач з таким ім'ям або email вже існує."}, 400

    except Exception:
        return {"message": "Не вдалося виконати запит."}, 500

    return new_worker



@worker_bp.route("/", methods=["GET"])
@worker_bp.doc(
    summary="Отримати список усіх співробітників",
    description="Надає список усіх співробітників",
    tags=["Workers"]
)
@worker_bp.response(200, UserResponseSchema(many=True))
@role_required("admin")
def get_employees():
    db = get_db()
    employees = db.query(User).filter_by(
        role="employee"
    ).all()
    return employees


@worker_bp.route("/<int:employee_id>", methods=["DELETE"])
@worker_bp.doc(
    summary="Видалити співробітника",
    description="""
    Видаляє співробітника за його ID.
    
    Функція доступна лише адміністратору.
    """,
    tags=["Workers"]
)
@worker_bp.response(204)
@role_required("admin")
def delete_employee(employee_id):
    db = get_db()

    employee = db.query(User).filter_by(
        id=employee_id,
        role="employee"
    ).first()

    if employee is None:
        return {"message": "Користувача не знайдено"}, 404

    try:
        db.delete(employee)
        db.commit()
    except Exception:
        db.rollback()
        return {"message": "Не вдалося виконати запит."}, 500

    return "", 204
