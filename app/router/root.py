from flask import redirect
from app.router.home import home_bp


@home_bp.route("/")
def root():
    return redirect("/api/swagger-ui")
