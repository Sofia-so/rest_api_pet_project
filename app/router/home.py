from flask_smorest import Blueprint
from flask import redirect
from app.schemas.message_schema import MessageSchema

home_bp = Blueprint(
    "home",
    __name__,
    url_prefix="/",
    description="home page"
)


@home_bp.route("/home_page")
@home_bp.doc(
    summary="вітає користувача на головній сторінці",
    description="головна сторінка",
    tags=["Головна сторінка"]
)
@home_bp.response(200, MessageSchema)
def home_page():
    return {"message": "Вітаємо на головній сторінці!"}, redirect("/docs")
