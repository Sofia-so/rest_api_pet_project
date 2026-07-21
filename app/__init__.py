from flask import Flask
from flask_smorest import Api
from app.authen.jwt_manager import jwt
from app.db.session import close_db
from app.router import (
    auth,
    user,
    root,
    home
)
import os
from dotenv import load_dotenv


def create_app():
    app = Flask(__name__)

    load_dotenv()

    app.config.update(
        API_TITLE="API",
        API_VERSION="v1",
        OPENAPI_VERSION="3.0.3",
        OPENAPI_URL_PREFIX="/api",
        OPENAPI_JSON_PATH="openapi.json",
        OPENAPI_SWAGGER_UI_PATH="/swagger-ui",
        OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
        PROPAGATE_EXCEPTIONS=True,
    )
    app.config["SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    app.config["API_SPEC_OPTIONS"] = {
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        },
        "security": [{"BearerAuth": []}]
    }

    jwt.init_app(app)

    api = Api(app)

    from app.router.home import home_bp
    from app.router.user import user_bp
    from app.router.admin import worker_bp
    from app.router.category import category_bp
    from app.router.product import product_bp
    from app.router.order import order_bp

    api.register_blueprint(home_bp)
    api.register_blueprint(user_bp)
    api.register_blueprint(worker_bp)
    api.register_blueprint(category_bp)
    api.register_blueprint(product_bp)
    api.register_blueprint(order_bp)
    app.teardown_appcontext(close_db)

    return app
