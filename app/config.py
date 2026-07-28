import os


class Config:
    TESTING = False

    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")

    API_TITLE = "API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/api"
    OPENAPI_JSON_PATH = "openapi.json"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    PROPAGATE_EXCEPTIONS = True


class TestingConfig(Config):
    TESTING = True

    SECRET_KEY = os.getenv("TEST_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URI")
