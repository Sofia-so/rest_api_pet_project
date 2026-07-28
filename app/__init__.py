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
from app.db.md_engine import init_engine
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    config_type = os.getenv(
        "CONFIG_TYPE",
        default="app.config.Config"
    )
    app.config.from_object(config_type)
    init_engine(app.config["SQLALCHEMY_DATABASE_URI"])

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
